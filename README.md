<div align="center">
  <h1>🎧 Yeetify</h1>
  <p>A self-hosted Discord music bot built for reliability, low-latency playback, and full queue control — powered by Lavalink and discord.py.</p>

  ![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python)
  ![discord.py](https://img.shields.io/badge/discord.py-2.4.0-5865F2?style=flat-square&logo=discord)
  ![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
  ![Version](https://img.shields.io/badge/Version-v2.7.3-FF00E2?style=flat-square)
</div>

---

## Overview

Yeetify is a feature-complete Discord music bot with support for multiple streaming platforms, audio DSP effects, personal playlist management, and a fully customizable player controller. It runs on a Lavalink audio backend, exposing both prefix and slash command interfaces with per-guild localization.

Built on top of [Vocard](https://github.com/ChocoMeow/Vocard) by chocomeow, with significant modifications and customizations by **Encore**.

---

## Features

- **Multi-platform playback** — YouTube, YouTube Music, Spotify, SoundCloud, Apple Music, Twitch, Bandcamp, Vimeo, Reddit, TikTok
- **Full queue control** — add, remove, move, swap, shuffle, clear, export and import queues as `.txt` files
- **Audio effects** — nightcore, 8D, vaporwave, and more via Lavalink filters
- **Personal playlists** — per-user playlist system backed by MongoDB, with configurable limits
- **Live lyrics** — fetches and displays synced lyrics via lrclib
- **Customizable controller** — fully configurable embed layout, buttons, and color scheme via `settings.json`
- **Slash + prefix commands** — hybrid command support with autocomplete
- **Per-guild localization** — multi-language support with a custom translation layer
- **Voice status templates** — dynamic voice channel status updates while playing
- **IPC client** — optional dashboard integration via WebSocket IPC
- **Docker support** — containerized deployment out of the box

---

## Requirements

| Dependency | Version |
|---|---|
| [Python](https://www.python.org/downloads/) | 3.11+ |
| [Lavalink Server](https://github.com/lavalink-devs/Lavalink) | 4.0.0+ |
| [MongoDB](https://www.mongodb.com/) | Any recent version |
| Java | 17+ (for Lavalink) |

---

## Installation

**1. Clone the repository**
```bash
git clone https://github.com/yourusername/yeetify.git
cd yeetify
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Configure the bot**

Copy and edit `settings.json` with your credentials:
```json
{
  "token": "YOUR_BOT_TOKEN",
  "client_id": "YOUR_CLIENT_ID",
  "mongodb_url": "YOUR_MONGODB_URI",
  "mongodb_name": "YOUR_DB_NAME",
  "nodes": {
    "DEFAULT": {
      "host": "your-lavalink-host",
      "port": 443,
      "password": "your-lavalink-password",
      "secure": true
    }
  }
}
```

**4. Start a Lavalink node**

Download the latest Lavalink `.jar` from the [releases page](https://github.com/lavalink-devs/Lavalink/releases) and run:
```bash
java -jar Lavalink.jar
```

**5. Run the bot**
```bash
python main.py
```

---

## Docker

```bash
docker build -t yeetify .
docker run -d --name yeetify yeetify
```

---

## Configuration

All bot behavior is controlled through `settings.json`. Key sections:

| Key | Description |
|---|---|
| `prefix` | Command prefix for message commands |
| `embed_color` | Global embed accent color (hex) |
| `default_controller` | Player embed layout, buttons, and templates |
| `sources_settings` | Per-platform emoji and color overrides |
| `playlist_settings` | Max playlists and tracks per user |
| `cooldowns` | Per-command rate limits |
| `aliases` | Command aliases |
| `ipc_client` | Dashboard IPC connection settings |

---

## Project Structure

```
yeetify/
├── cogs/               # Command modules (basic, effect, playlist, settings, etc.)
├── voicelink/          # Core audio engine, player, queue, views, utils
│   └── views/          # Discord UI components (controller, help, queue, etc.)
├── langs/              # Localization files
├── logs/               # Rotating log output
├── main.py             # Bot entrypoint
├── function.py         # Shared utilities and JSON helpers
├── settings.json       # Bot configuration
├── requirements.txt    # Python dependencies
└── Dockerfile
```

---

## Commands

Use `/help` in Discord to browse all commands by category. Key commands:

| Command | Description |
|---|---|
| `/play <query>` | Search and queue a song or playlist |
| `/search <query>` | Pick from search results interactively |
| `/queue` | View the current queue |
| `/nowplaying` | Show what's currently playing |
| `/skip` | Skip to the next track |
| `/loop <mode>` | Set loop mode (track / queue / off) |
| `/shuffle` | Shuffle the queue |
| `/lyrics` | Show lyrics for the current track |
| `/playlist` | Manage personal playlists |
| `/settings` | Configure bot behavior for your server |

---

## Credits

Yeetify is a fork of [Vocard](https://github.com/ChocoMeow/Vocard) by **chocomeow**.
Modified, maintained, and extended by **Encore**.

---

## License

This project is licensed under the [MIT License](LICENSE).
