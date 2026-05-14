"""MIT License

Copyright (c) 2023 - present Encore Development

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

import discord
from discord.ext import commands

from ..config import Config

class HelpDropdown(discord.ui.Select):
    def __init__(self, categories: list[str]) -> None:
        self.view: HelpView

        super().__init__(
            placeholder="Browse a category...",
            min_values=1, max_values=1,
            options=[
                discord.SelectOption(emoji="🌟", label="News", description="What's new with Yeetify."),
                discord.SelectOption(emoji="📖", label="Tutorial", description="Get started in seconds."),
            ] + [
                discord.SelectOption(emoji=emoji, label=category, description=desc)
                for category, emoji, desc in zip(
                    categories,
                    ["🎵", "🎚️", "💿", "⚙️", "📡", "⏱️", "📋"],
                    [
                        "Core playback commands.",
                        "Audio filters & effects.",
                        "Playlist management.",
                        "Server configuration.",
                        "Event listeners.",
                        "Background tasks.",
                        "More commands.",
                    ]
                )
            ],
            custom_id="select"
        )
    
    async def callback(self, interaction: discord.Interaction) -> None:
        embed = self.view.build_embed(self.values[0])
        await interaction.response.edit_message(embed=embed)

class HelpView(discord.ui.View):
    def __init__(self, bot: commands.Bot, author: discord.Member) -> None:
        super().__init__(timeout=60)

        self.author: discord.Member = author
        self.bot: commands.Bot = bot
        self.response: discord.Message = None
        self.categories: list[str] = [ name.capitalize() for name, cog in bot.cogs.items() if len([c for c in cog.walk_commands()]) ]

        self.add_item(discord.ui.Button(label='Website', emoji='🌎', url='https://Encore.xyz'))
        self.add_item(discord.ui.Button(label='Document', emoji=':support:915152950471581696', url='https://docs.Encore.xyz'))
        self.add_item(discord.ui.Button(label='Github', emoji=':github:1098265017268322406', url='https://github.com/ChocoMeow/Encore'))
        self.add_item(discord.ui.Button(label='Donate', emoji=':patreon:913397909024800878', url='https://www.patreon.com/Encore'))
        self.add_item(HelpDropdown(self.categories))

    async def on_timeout(self) -> None:
        for child in self.children:
            if child.custom_id == "select":
                child.disabled = True
        try:
            await self.response.edit(view=self)
        except:
            pass

    async def interaction_check(self, interaction: discord.Interaction) -> None:
        return interaction.user == self.author

    def build_embed(self, category: str) -> discord.Embed:
        category = category.lower()

        CATEGORY_META = {
            "basic":    ("🎵", 0xFF00E2, "Core playback commands available to everyone."),
            "effect":   ("🎚️", 0xFF00E2, "Audio filters & effects. DJ role required."),
            "playlist": ("💿", 0xFF00E2, "Manage your personal playlists."),
            "settings": ("⚙️", 0xFF00E2, "Server configuration. Admin only."),
            "listeners":("📡", 0xFF00E2, "Internal event listeners."),
            "task":     ("⏱️", 0xFF00E2, "Background tasks."),
        }

        if category == "news":
            embed = discord.Embed(color=0xFF00E2)
            embed.set_author(name="Yeetify  ·  Help Center", icon_url=self.bot.user.display_avatar.url)
            embed.title = "Welcome to Yeetify"
            embed.description = (
                "> A powerful, modern music bot built for your server.\n\n"
                "**Features**\n"
                "` ⚡ ` High quality music — YouTube, Spotify, SoundCloud\n"
                "` 🎚️ ` Audio effects — nightcore, 8D, vaporwave & more\n"
                "` 💿 ` Personal playlists with sharing & permissions\n"
                "` 🔁 ` Loop, shuffle, autoplay & full queue control\n"
                "` 🎤 ` Live lyrics display\n"
                "` 🌐 ` Multi-language support\n\n"
                "**Quick Start**\n"
                "` 1 ` Join a voice channel\n"
                "` 2 ` Run `/play` with a song name or link\n"
                "` 3 ` Control playback with the buttons below the player"
            )
            embed.set_footer(text=f"Yeetify  ·  {len(self.categories)} categories  ·  Select one below")
            return embed

        if category == "tutorial":
            embed = discord.Embed(color=0xFF00E2)
            embed.set_author(name="Yeetify  ·  Tutorial", icon_url=self.bot.user.display_avatar.url)
            embed.title = "How to use Yeetify"
            embed.description = (
                "> Follow these steps to get started.\n\n"
                "` 1 ` Join a voice channel\n"
                "` 2 ` Run `/play <song name or URL>`\n"
                "` 3 ` Use the player buttons to pause, skip, loop\n"
                "` 4 ` Save songs with `/playlist create` & `/playlist add`\n"
                "` 5 ` Apply audio effects with `/nightcore`, `/8d`, etc.\n"
                "` 6 ` Configure the bot with `/settings`"
            )
            embed.set_footer(text="Yeetify  ·  Use / to run commands")
            return embed

        # Category command list embed
        emoji, color, subtitle = CATEGORY_META.get(category, ("📋", 0xFF00E2, f"{category.capitalize()} commands."))
        embed = discord.Embed(color=color)
        embed.set_author(name=f"Yeetify  ·  {category.capitalize()} Commands", icon_url=self.bot.user.display_avatar.url)
        embed.title = f"{emoji}  {category.capitalize()}"
        embed.description = f"> {subtitle}\n\n"

        try:
            cog = [c for _, c in self.bot.cogs.items() if _.lower() == category][0]
            commands = [cmd for cmd in cog.walk_commands() if cmd.qualified_name != cog.qualified_name]
            embed.description += "\n".join(
                f"`/{cmd.qualified_name}`  {cmd.callback.__doc__ or cmd.description or 'No description'}"
                for cmd in commands
            )
        except IndexError:
            embed.description += "*No commands found in this category.*"

        embed.set_footer(text="Yeetify  ·  Use / to run commands")
        return embed