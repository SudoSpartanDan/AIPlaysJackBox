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

```shell
# Run with the Web UI (preferred experience)
ai-plays-jackbox-ui

# Or via CLI
ai-plays-jackbox --chat-model-name ollama --room-code abcd
```

## Supported Games

| Party Pack            | Game                   |
| --------------------- | ---------------------- |
| JackBox Party Pack 7  | Quiplash 3             |

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
