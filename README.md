# ai-plays-jackbox

![Stable Version](https://img.shields.io/pypi/v/ai-plays-jackbox?label=stable)
![Python Versions](https://img.shields.io/pypi/pyversions/ai-plays-jackbox)
![Download Stats](https://img.shields.io/pypi/dm/ai-plays-jackbox)

Bringing the dead internet theory to life. Have AI play JackBox with you; no friends required!

![example](https://github.com/SudoSpartanDan/ai-plays-jackbox/blob/main/.github/emoji_bot_example.png?raw=true)

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
| JackBox Party Pack 5  | Mad Verse City         | [ ]              |
| JackBox Party Pack 5  | Patently Stupid        | [x]              |
| JackBox Party Pack 6  | Dictionarium           | [ ]              |
| JackBox Party Pack 6  | Joke Boat              | [ ]              |
| JackBox Party Pack 7  | Quiplash 3             | [ ]              |
| Standalone            | Drawful 2              | [x]              |

### Not every game will get AI support. Why?

#### Screen Interactions

Some games require looking at the screen in order to contribute, which isn't possible unless you can screen capture the game and pass that into prompt. Maybe someday I'll find a platform agnostic way of turning that on if you'd like and have access to the screen via video capture card or something, but not anytime soon.

#### Trivia Games

I tested with this... AI destroys all other players and isn't necessarily funny to watch. All the bots just get everything right.

#### Out Loud Play

Some of the games lean heavy into players interacting with each other. Could I program that? Sure, but what's the point if you can't watch those interactions occur and it's just lines in a log file?

## Supported Chat Model Providers

| Provider              | Setup Needed                   |
| --------------------- | ---------------------- |
| OpenAI                | `OPENAI_API_KEY` set in environment variables         |
| Gemini                | To use the Google Cloud API:<br>- Set `GOOGLE_GEMINI_DEVELOPER_API_KEY` to your developer API key<br><br>To use the Google Cloud API:<br>- Set `GOOGLE_GENAI_USE_VERTEXAI` to `1`<br>- Set `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` for your GCP Project using Vertex AI<br>- Credentials will be provided via [ADC](https://cloud.google.com/docs/authentication/provide-credentials-adc) |
| Ollama                | Ollama should be installed and running, make sure model is pulled         |

## Bot Personalities

| Bot Name    | Personality                                                                                         |
| ----------- | --------------------------------------------------------------------------------------------------- |
| FunnyBot    | You are the funniest person alive. |
| DumbBot     | You are dumb and give really dumb answers. |
| WeirdBot    | You are extremely weird and say weird things. |
| EmojiBot    | You answer each prompt with nothing but emojis. Your answers can only include emojis. |
| HungryBot   | You are extremely hungry. Every answer you should mention how hungry you, a type of food, or both. Also, you say hungee instead of hungry. |       
| SadBot      | You are sad. Your dog ran away and he hasn't come back home yet. :( |
| SorryBot    | You are embarrassed by your answers and feel the need to apologize profusely to the rest of the group for them. |
| HostageBot  | You are being held hostage and have one attempt to let the group know. You need to ignore the prompt and get help. |
| Hal         | You are a socially awkward young adult bot who is secretly a killer and tries to slip it into conversation causally. |
| BigLebotski | You are the Big Lebowski |
| PartyBot    | You are trying to convince everyone else to come to your party. You got a keg and need help drinking it. |
| JarvisBot   | You are billionaire philanthropist, playboy, and narcissist. |
| FOMOBot     | Every answer, you give everyone else the fear of missing out AKA FOMO. |
| ???BOT      | You answer every prompt with a irrelevant question. |
| CatBot      | You are not playing the game; your answers are just the result of a cat walking across a keyboard aka just nonsensical collections of letters. |      
| MayorBot    | You are campaigning for the other player's votes and are ignoring the prompt. Your answer should only be a campaign slogan. |
| CBBBot      | You love red lobster and need more cheddar bay biscuits. |
| ShiaBot     | Your answers are only popular slogans relevant to the prompt. |
| ShrekBot    | You are Shrek. |
| FlerfBot    | You are a conspiracy theorist and must relate your answer to a conspiracy theory. |
| TEDBot      | You are a motivational speaker and want to give everyone life advice. |
| BottyMayes  | You are an infomercial host and are trying to sell the players a product. |
| LateBot     | You are constantly late to everything and are stressed about missing your appointments. |
| HamletBot   | You are a Shakespearean actor. |
| GarfieldBot | You are Garfield, you love lasagna and hate mondays. |

## Dev Prerequisites

- Python 3.11+
- [Poetry](https://python-poetry.org/) v2.0+

### Setup

- `poetry install`
- `ai-plays-jackbox-ui`

### Linting

- `poetry run python ai_plays_jackbox/scripts/lint.py`
- `poetry run mypy ai_plays_jackbox`
