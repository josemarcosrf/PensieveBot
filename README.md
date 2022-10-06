# Pensieve Bot

This is a simple Telegram bot which takes voice clips and responds with the
transcription.
Meant to be my personal [pensieve](https://harrypotter.fandom.com/wiki/Pensieve)-bot.

The ASR model exploration can be found in this
[STT-exploratory gist](https://gist.github.com/jmrf/9d84e77fc180996198d8a93258904a9f)
and in particular this implementation is based on
[OpenAI's whisper model](https://github.com/openai/whisper)

The bot integration uses [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI)


## ToC

<!--ts-->
* [Pensieve Bot](#pensieve-bot)
   * [ToC](#toc)
   * [How To](#how-to)
      * [Install](#install)
      * [Run](#run)

<!-- Created by https://github.com/ekalinin/github-markdown-toc -->
<!-- Added by: ubuntu, at: Thu Sep 29 20:00:14 UTC 2022 -->

<!--te-->

## How To

### Install

> NOTE: It is recommended to create a virtual env with python 3.8+

```bash
pip install -r requirements.txt
```

### Run

First create a `.env` file with the following values:

```bash
VALID_SENDER_IDS="sender_id_1,sender_id_2,..."  # telegram user IDs to which the bot replies
BOT_TOKEN="your-bot-token"  # Telgram bot token (from BotFather)
```

The run with:
```bash
# Run the bot with the 'small' whisper model
python -m src.run -m small -v INFO
```
