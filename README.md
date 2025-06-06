# AI Plays JackBox

Bringing the dead internet theory to life.

## Installation

```pip install ai-plays-jackbox```

## Usage

```shell
# Run with the Web UI (preferred experience)
ai-plays-jackbox-ui

# Or via CLI
ai-plays-jackbox --chat-model-name ollama --room-code abcd
```

## Supported Games

- JackBox Party Pack 7
  - Quiplash 3

## Setup for Chat Models

### Ollama

- Ollama should be installed and running
  - Pull a model to use with the library: `ollama pull <model>` e.g. `ollama pull llama3.2`
  - See [Ollama.com](https://ollama.com/search) for more information on the models available.

### OpenAI

- `OPENAI_API_KEY` needs to be popluated in your environment variables.

### Gemini

- To use the Google Cloud API:
  - Set `GOOGLE_GEMINI_DEVELOPER_API_KEY` to your developer API key
- To use the Google Cloud API:
  - Set `GOOGLE_GENAI_USE_VERTEXAI` to `1`
  - Set `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` for your GCP Project using Vertex AI
  - Credentials will be provided via [ADC](https://cloud.google.com/docs/authentication/provide-credentials-adc)
    - ADC searches for credentials in the following locations:
      - `GOOGLE_APPLICATION_CREDENTIALS` environment variable
      - A credential file created by using the gcloud auth application-default login command
      - The attached service account, returned by the metadata server

## Dev Prerequisites

- Python 3.11+
- [Poetry](https://python-poetry.org/) v2.0+

### Setup

- `poetry install`
- `ai-plays-jackbox-ui`

### Linting

- `poetry run lint`
