import json
import threading
import traceback
from abc import ABC, abstractmethod
from typing import Optional, Union
from urllib import parse
from uuid import uuid4

import cv2
import html2text
import numpy as np
from loguru import logger
from pydantic import BaseModel, Field, field_validator
from websocket import WebSocketApp

from ai_plays_jackbox.constants import ECAST_HOST
from ai_plays_jackbox.llm.chat_model import ChatModel
from ai_plays_jackbox.llm.ollama_model import OllamaModel


class JackBoxBotBase(ABC):
    _is_disconnected: bool = False
    _ws: Optional[WebSocketApp] = None
    _ws_thread: Optional[threading.Thread] = None
    _message_sequence: int = 0
    _player_guid: str
    _name: str
    _personality: str
    _chat_model: ChatModel

    def __init__(
        self,
        name: str = "FunnyBot",
        personality: str = "You are the funniest bot ever.",
        chat_model: Optional[ChatModel] = None,
    ):
        self._name = name
        self._personality = personality
        self._player_guid = str(uuid4())
        if chat_model is None:
            chat_model = OllamaModel()
        self._chat_model = chat_model

    def connect(self, room_code: str) -> None:
        self._room_code = room_code
        bootstrap_payload = {
            "role": "player",
            "name": self._name,
            "userId": self._player_guid,
            "format": "json",
            "password": "",
        }
        self._ws = WebSocketApp(
            f"wss://{ECAST_HOST}/api/v2/rooms/{room_code}/play?{parse.urlencode(bootstrap_payload)}",
            subprotocols=["ecast-v0"],
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )
        self._ws.on_open = self._on_open

        self._ws_thread = threading.Thread(name=self._name, target=self._ws.run_forever, daemon=True)
        self._ws_thread.start()

    def disconnect(self) -> None:
        if self._ws:
            self._ws.close()
        if self._ws_thread and self._ws_thread.is_alive():
            self._ws_thread.join()

    def is_disconnected(self) -> bool:
        return self._is_disconnected

    @property
    @abstractmethod
    def _player_operation_key(self) -> str:
        return f"player:{self._player_id}"

    @abstractmethod
    def _is_player_operation_key(self, operation_key: str) -> bool:
        return operation_key == self._player_operation_key

    @property
    @abstractmethod
    def _room_operation_key(self) -> str:
        return "room"

    @abstractmethod
    def _is_room_operation_key(self, operation_key: str) -> bool:
        return operation_key == self._room_operation_key

    def _on_open(self, ws) -> None:
        logger.info(f"WebSocket connection opened for {self._name}")

    def _on_error(self, ws, error) -> None:
        logger.error(f"Error for {self._name}: {error}")
        if isinstance(error, Exception):
            traceback.print_exc()
        else:
            print(error)

    def _on_close(self, ws, close_status_code, close_msg) -> None:
        if close_status_code != 1000 and close_status_code is not None:
            logger.warning(f"Trying to reconnect {self._name}")
            self.connect(self._room_code)
        else:
            self._is_disconnected = True
            logger.info(f"WebSocket closed for {self._name}")

    def _on_message(self, wsapp, message) -> None:
        server_message = ServerMessage.model_validate_json(message)

        if server_message.opcode == "client/welcome":
            self._player_id = server_message.result["id"]
            self._handle_welcome(server_message.result)

        operation: Optional[Union[ObjectOperation, TextOperation]] = None
        if server_message.opcode == "object":
            operation = ObjectOperation(**server_message.result)
        elif server_message.opcode == "text":
            operation = TextOperation(**server_message.result)

        if operation is not None:
            if self._is_player_operation_key(operation.key):
                self._handle_player_operation(operation.json_data)
            if self._is_room_operation_key(operation.key):
                self._handle_room_operation(operation.json_data)

    @abstractmethod
    def _handle_welcome(self, data: dict) -> None:
        pass

    @abstractmethod
    def _handle_player_operation(self, data: dict) -> None:
        pass

    @abstractmethod
    def _handle_room_operation(self, data: dict) -> None:
        pass

    def _send_ws(self, opcode: str, params: dict) -> None:
        self._message_sequence += 1
        message = {"seq": self._message_sequence, "opcode": opcode, "params": params}
        if self._ws is not None:
            self._ws.send(json.dumps(message))
        else:
            raise Exception("Websocket connection has not been initialized")

    def _client_send(self, request: dict) -> None:
        params = {"from": self._player_id, "to": 1, "body": request}
        self._send_ws("client/send", params)

    def _object_update(self, key: str, val: dict) -> None:
        params = {"key": key, "val": val}
        self._send_ws("object/update", params)

    def _text_update(self, key: str, val: str) -> None:
        params = {"key": key, "val": val}
        self._send_ws("text/update", params)

    def _html_to_text(self, html: str) -> str:
        return html2text.html2text(html)

    def _image_bytes_to_polylines(self, image_bytes: bytes, canvas_height: int, canvas_width: int) -> list[str]:
        # Let's edge trace the outputted image to contours
        image_array = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(image_array, flags=1)
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray_image, threshold1=100, threshold2=200)
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Figure out scaling factor
        height, width = gray_image.shape
        scale_x = canvas_width / width
        scale_y = canvas_height / height
        scale_factor = min(scale_x, scale_y)

        # generate the polylines from the contours
        polylines = []
        for contour in contours:
            if len(contour) > 1:  # Only include contours with 2 or more points
                polyline = [f"{int(point[0][0] * scale_factor)},{int(point[0][1] * scale_factor)}" for point in contour]  # type: ignore
                polylines.append("|".join(polyline))

        return polylines

    def __del__(self):
        self.disconnect()


##### Web Socket Classes #####
class ServerMessage(BaseModel):
    seq: int = Field(alias="pc")
    opcode: str
    result: dict


class TextOperation(BaseModel):
    from_field: int = Field(alias="from")
    key: str
    json_data: dict = Field(default={})
    value: str = Field(alias="val")
    version: int

    @field_validator("json_data")  # type: ignore
    def set_json_data(cls, value, values: dict):
        return json.loads(values.get("value", ""))


class ObjectOperation(BaseModel):
    from_field: int = Field(alias="from")
    key: str
    json_data: dict = Field(alias="val")
    value: str = Field(default="")
    version: int

    @field_validator("value")  # type: ignore
    def set_value(cls, value, values: dict):
        return json.dumps(values.get("json_data"))
