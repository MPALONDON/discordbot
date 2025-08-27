# Discord Bot

A Discord bot built with Python that can moderate servers, play music, run polls, and more. This project demonstrates use of **discord.py**, **SQLAlchemy**, and external libraries like **yt_dlp**.

---

## Features

### Moderation
- Kick and ban members (requires permission)  
- Assign roles

### Fun Commands
- Roll a dice: `!roll`  
- Polls: `!poll "Question" option1 option2 ...`

### Music
- Join/leave voice channels: `!join`, `!leave`  
- Play music from YouTube: `!play <url>`  
- Pause, resume, stop: `!pause`, `!resume`, `!stop`

### Utility
- Show list of available commands: `!commands`  
- Welcome new members automatically

---

## Installation

1. Clone this repository:

```bash
git clone https://github.com/yourusername/discord-bot.git
cd discord-bot
```

2. Create a virtual environment

```bash
python -m venv .venv
# Linux / Mac
source .venv/bin/activate
# Windows
.venv\Scripts\activate
```

3. install dependencies:
```requirements
pip install -r requirements.txt
 ```

4. Get your bot token:

- Go to the [Discord Developer Portal](https://discord.com/developers/applications)
- Create a new application
- Add a bot to the application
- Give Privileged Gateway Intents
- Copy the bot token 
- Paste it in `config.json`:

```json
{
  "DISCORD_TOKEN": "your-bot-token-here"
}
```

### Make sure you have FFmpeg installed if you want music playback!

