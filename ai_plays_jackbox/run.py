from ai_plays_jackbox.room import JackBoxRoom


def run():
    room_code = _get_room_code()
    room = JackBoxRoom()
    room.play(room_code)


def _get_room_code() -> str:
    while True:
        room_code = input("Please enter the room code: ")
        if len(room_code) != 4 or not room_code.isalpha():
            print("Invalid room code; please try again")
        else:
            return room_code
