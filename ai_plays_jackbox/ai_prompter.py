from loguru import logger
from ollama import generate


def get_ai_response(prompt: str, model: str = "gemma2", num_predict: int = 0) -> str:
    prompt_options = {}
    if num_predict > 0:
        prompt_options = {"num_predict": num_predict}
    generation_response = generate(model=model, prompt=prompt, options=prompt_options)
    response = generation_response.response.strip().replace("\n", " ")
    logger.info(response)
    return response
