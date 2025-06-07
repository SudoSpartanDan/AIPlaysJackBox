# AI Plays JackBox

![Stable Version](https://img.shields.io/pypi/v/ai-plays-jackbox?label=stable)
![Python Versions](https://img.shields.io/pypi/pyversions/ai-plays-jackbox)
![Download Stats](https://img.shields.io/pypi/dm/ai-plays-jackbox)

Bringing the dead internet theory to life. Have AI play JackBox with you; no friends required!

![example](.github/emoji_bot_example.png)

## Installation

```shell
pip install ai-plays-jackbox
```

## Usage

### Web UI

```shell
ai-plays-jackbox-ui
```

### CLI

```shell
ai-plays-jackbox --chat-model-name openai --room-code abcd
```

```
usage: ai-plays-jackbox [-h] --room-code WXYZ --chat-model-provider {openai,gemini,ollama} [--chat-model-name CHAT_MODEL_NAME] [--num-of-bots 4] [--temperature 0.5] [--top-p 0.9]

options:
  -h, --help            show this help message and exit
  --room-code WXYZ      The JackBox room code
  --chat-model-provider {openai,gemini,ollama}
                        Choose which chat model platform to use
  --chat-model-name CHAT_MODEL_NAME
                        Choose which chat model to use (Will default to default for provider)
  --num-of-bots 4       How many bots to have play
  --temperature 0.5     Temperature for Gen AI
  --top-p 0.9           Top P for Gen AI
```

## Supported Games

> [!NOTE]
> Ollama Chat Model Provider does not support image generation

| Party Pack            | Game                   | Image Generation |
| --------------------- | ---------------------- | ---------------- |
| JackBox Party Pack 5  | Patently Stupid        | [x]              |
| JackBox Party Pack 7  | Quiplash 3             | [ ]              |
| Standalone            | Drawful 2              | [x]              |

## Supported Chat Model Providers

| Provider              | Setup Needed                   |
| --------------------- | ---------------------- |
| OpenAI                | `OPENAI_API_KEY` set in environment variables         |
| Gemini                | To use the Google Cloud API:<br>- Set `GOOGLE_GEMINI_DEVELOPER_API_KEY` to your developer API key<br><br>To use the Google Cloud API:<br>- Set `GOOGLE_GENAI_USE_VERTEXAI` to `1`<br>- Set `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` for your GCP Project using Vertex AI<br>- Credentials will be provided via [ADC](https://cloud.google.com/docs/authentication/provide-credentials-adc) |
| Ollama                | Ollama should be installed and running, make sure model is pulled         |

## Dev Prerequisites

- Python 3.11+
- [Poetry](https://python-poetry.org/) v2.0+

### Setup

- `poetry install`
- `ai-plays-jackbox-ui`

### Linting

- `poetry run python scripts/lint.py`
- `poetry run mypy ai_plays_jackbox`
