"""MIT License

Copyright (c) 2023 - present Encore

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
import os
import logging
import voicelink

from discord.ext import commands
from typing import Optional

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

logger: logging.Logger = logging.getLogger("yeetify")

if not os.path.exists(os.path.join(ROOT_DIR, "settings.json")):
    raise Exception("Settings file not set!")

def open_json(path: str) -> dict:
    try:
        with open(os.path.join(ROOT_DIR, path), encoding="utf8") as json_file:
            return json.load(json_file)
    except:
        return {}

def update_json(path: str, new_data: dict) -> None:
    data = open_json(path)
    if not data:
        data = new_data
    else:
        data.update(new_data)

    with open(os.path.join(ROOT_DIR, path), "w") as json_file:
        json.dump(data, json_file, indent=4)

def get_aliases(command: str) -> list:
    """Return the list of aliases for a command from settings.json."""
    settings = open_json("settings.json")
    return settings.get("aliases", {}).get(command, [])

def cooldown_check(ctx: commands.Context) -> Optional[commands.Cooldown]:
    """Dynamic cooldown that reads per-command rates from settings.json."""
    settings = open_json("settings.json")
    cooldowns: dict = settings.get("cooldowns", {})

    # Build the lookup key: try "group subcommand" then just the command name
    if ctx.command is None:
        return None

    invoked = ctx.command.qualified_name  # e.g. "playlist view"
    rate, per = None, None

    if invoked in cooldowns:
        rate, per = cooldowns[invoked]
    else:
        # Fallback to the root command name
        root = ctx.command.name
        if root in cooldowns:
            rate, per = cooldowns[root]

    if rate is not None and per is not None:
        return commands.Cooldown(rate, per)
    return None