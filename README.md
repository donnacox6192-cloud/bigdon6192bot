# BigDon6192Bot 🤖

A Telegram bot for math calculations and unit conversions.

## Features
- Basic math: `2+2`, `(5*3)/2`, `2^8`, `17%5`
- Unit conversion: `100 cm to m`, `5 kg to lb`, `30 c to f`
- Categories: length, weight, temperature, volume, time

## Deploy on Railway

1. Push this repo to GitHub.
2. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub**.
3. Select your repo.
4. Add environment variable `BOT_TOKEN` with your token from [@BotFather](https://t.me/BotFather).
5. Set service type to **Worker** (Railway auto-detects `Procfile`).
6. Deploy! 🚀

## Local Run

```bash
pip install -r requirements.txt
cp .env.example .env  # add your token
python bot.py
