# AI Plays JackBox

Bringing the dead internet theory to life.

## Supported Games

- JackBox Party Pack 7
  - Quiplash 3

## Prerequisites

- Python 3.11+
- [Poetry](https://python-poetry.org/)

### Ollama

- Ollama should be installed and running
  - Pull a model to use with the library: `ollama pull <model>` e.g. `ollama pull llama3.2`
  - See [Ollama.com](https://ollama.com/search) for more information on the models available.

### OpenAI

- `OPENAI_API_KEY` needs to be popluated in your environment variables.

## Setup

- `poetry install`
- `poetry run ui`

## Linting

- `poetry run lint`
