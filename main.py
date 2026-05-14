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

import discord
import sys
import os
import aiohttp
import update
import logging
import function as func

from discord.ext import commands
from logging.handlers import TimedRotatingFileHandler
from voicelink import Config, LangHandler, MongoDBHandler, IPCClient, VoicelinkException, NodeException
from voicelink.utils import dispatch_message

class Translator(discord.app_commands.Translator):
    MISSING_TRANSLATOR: dict[str, list[str]] = {}

    async def load(self):
        func.logger.info("Loaded Translator")
        
    async def unload(self):
        func.logger.info("Unload Translator")
        
    async def translate(
        self,
        string: discord.app_commands.locale_str,
        locale: discord.Locale,
        context: discord.app_commands.TranslationContext
    ) -> str | None:
        locale_key = str(locale).upper()
        local_translations = LangHandler._local_langs.get(locale_key)
        if not local_translations:
            return None

        translated_text = local_translations.get(string.message)
        if translated_text is not None:
            return translated_text

        missing = self.MISSING_TRANSLATOR.setdefault(locale_key, [])
        if string.message not in missing:
            missing.append(string.message)

        return None

class Yeetify(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ipc_client: IPCClient



    async def setup_hook(self) -> None:
        # Connecting to MongoDB
        await MongoDBHandler.init(bot_config.mongodb_url, bot_config.mongodb_name)

        # Set translator
        await self.tree.set_translator(Translator())

        # Loading all the module in `cogs` folder
        for module in os.listdir(func.ROOT_DIR + '/cogs'):
            if module.endswith('.py'):
                try:
                    await self.load_extension(f"cogs.{module[:-3]}")
                    func.logger.info(f"Loaded {module[:-3]}")
                except Exception as e:
                    func.logger.error(f"Something went wrong while loading {module[:-3]} cog.", exc_info=e)

        # IPC setup
        self.ipc_client: IPCClient = IPCClient(self, **bot_config.ipc_client)
        if bot_config.ipc_client.get("enable", False):
            try:
                await self.ipc_client.connect()
            except Exception as e:
                func.logger.error(f"Cannot connected to dashboard! - Reason: {e}")

        # THEN sync after all cogs and commands are registered
        try:
            synced = await self.tree.sync()
            func.logger.info(f"Auto-registered {len(synced)} slash commands globally.")
        except Exception as e:
            func.logger.error(f"Failed to sync slash commands: {e}")

        # Update version tracking
        if not bot_config.version or bot_config.version != update.__version__:
            func.update_json("settings.json", new_data={"version": update.__version__})
            
            for locale_key, values in self.tree.translator.MISSING_TRANSLATOR.items():
                func.logger.warning(f'Missing translation for "{", ".join(values)}" in "{locale_key}"')
            self.tree.translator.MISSING_TRANSLATOR.clear()

    async def on_ready(self):
        func.logger.info("------------------")
        func.logger.info(f"Logging As: {self.user}")
        func.logger.info(f"Bot ID: {self.user.id}")
        func.logger.info(f"Slash Commands: {len(self.tree.get_commands())}")
        func.logger.info("------------------")
        func.logger.info(f"Yeetify Version: {update.__version__}")
        func.logger.info(f"Discord Version: {discord.__version__}")
        func.logger.info(f"Python Version: {sys.version}")
        func.logger.info("------------------")
        func.logger.info("Yeetify — main source on Vocard by chocomeow — https://github.com/ChocoMeow/Vocard")

        bot_config.client_id = self.user.id
        LangHandler._local_langs.clear()

    async def on_app_command_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError) -> None:
        error_msg = getattr(error, 'original', error)

        if isinstance(error_msg, (aiohttp.client_exceptions.ClientOSError, discord.errors.NotFound)):
            return

        elif isinstance(error_msg, discord.app_commands.CommandOnCooldown):
            pass

        elif isinstance(error_msg, discord.app_commands.MissingPermissions):
            pass

        elif not issubclass(error_msg.__class__, (VoicelinkException, NodeException)):
            error_msg = await Lang_handler.get_lang(interaction.guild.id, "common.errors.unknown")
            func.logger.error(f"An unexpected app command error occurred in {interaction.command.name} on {interaction.guild.name}({interaction.guild.id}).", exc_info=error)

        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(error_msg, ephemeral=True)
            else:
                await interaction.followup.send(error_msg, ephemeral=True)
        except:
            pass

class CommandCheck(discord.app_commands.CommandTree):
    async def interaction_check(self, interaction: discord.Interaction, /) -> bool:
        if interaction.type == discord.InteractionType.application_command:
            if not interaction.guild:
                await interaction.response.send_message("This command can only be used in guilds!")
                return False

            channel_perm = interaction.channel.permissions_for(interaction.guild.me)
            if not channel_perm.read_messages or not channel_perm.send_messages:
                await interaction.response.send_message("I don't have permission to read or send messages in this channel.", ephemeral=True)
                return False
            
        return True



# Loading settings and logger
bot_config = Config(func.open_json("settings.json"))
Lang_handler = LangHandler.init()

LOG_SETTINGS = bot_config.logging
if (LOG_FILE := LOG_SETTINGS.get("file", {})).get("enable", True):
    log_path = os.path.abspath(LOG_FILE.get("path", "./logs"))
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    file_handler = TimedRotatingFileHandler(filename=f'{log_path}/yeetify.log', encoding="utf-8", backupCount=LOG_SETTINGS.get("max_history", 30), when="d")
    file_handler.namer = lambda name: name.replace(".log", "") + ".log"
    file_handler.setFormatter(logging.Formatter('{asctime} [{levelname:<8}] {name}: {message}', '%Y-%m-%d %H:%M:%S', style='{'))
    logging.getLogger().addHandler(file_handler)

for log_name, log_level in LOG_SETTINGS.get("level", {}).items():
    _logger = logging.getLogger(log_name)
    _logger.setLevel(log_level)

# Setup the bot object
intents = discord.Intents.default()
intents.message_content = False
intents.members = bot_config.ipc_client.get("enable", False)
intents.voice_states = True
intents.presences = False

bot = Yeetify(
    command_prefix="!",
    help_command=None,
    tree_cls=CommandCheck,
    chunk_guilds_at_startup=False,
    activity=discord.Activity(type=discord.ActivityType.listening, name="Encore Development 🎵"),
    case_insensitive=True,
    intents=intents
)

@bot.command()
@commands.is_owner()
async def sync(ctx):
    try:
        synced = await bot.tree.sync()
        func.logger.info(f"Manual global sync: {len(synced)} commands")
        await ctx.send(f"✅ Synced `{len(synced)}` slash commands globally.")
    except Exception as e:
        await ctx.send(f"❌ Sync failed: `{e}`")

@bot.command()
@commands.is_owner()
async def syncguild(ctx):
    try:
        synced = await bot.tree.sync(guild=ctx.guild)
        func.logger.info(f"Manual guild sync: {len(synced)} commands to {ctx.guild.name}")
        await ctx.send(f"✅ Synced `{len(synced)}` slash commands to **{ctx.guild.name}** instantly.")
    except Exception as e:
        await ctx.send(f"❌ Guild sync failed: `{e}`")

def print_banner():
    C = "\033[96m"   # cyan
    D = "\033[90m"   # dark gray
    W = "\033[97m"   # white
    R = "\033[0m"    # reset

    art = [
        r" ███████╗███╗   ██╗ ██████╗ ██████╗ ██████╗ ███████╗",
        r" ██╔════╝████╗  ██║██╔════╝██╔═══██╗██╔══██╗██╔════╝",
        r" █████╗  ██╔██╗ ██║██║     ██║   ██║██████╔╝█████╗  ",
        r" ██╔══╝  ██║╚██╗██║██║     ██║   ██║██╔══██╗██╔══╝  ",
        r" ███████╗██║ ╚████║╚██████╗╚██████╔╝██║  ██║███████╗",
        r" ╚══════╝╚═╝  ╚═══╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝",
    ]

    width = 56
    print()
    print(f"  {D}{'_' * width}{R}")
    print(f"  {D}|{R}")
    for line in art:
        print(f"  {D}|{R}  {C}{line}{R}")
    print(f"  {D}|{R}")
    print(f"  {D}|{'_' * (width - 1)}{R}")
    print(f"  {D}|{R}  {D}version  -{R}  {W}{update.__version__}{R}")
    print(f"  {D}|{R}  {D}prefix   -{R}  {W}{bot_config.bot_prefix or '/'}{R}")
    print(f"  {D}|{R}  {D}author   -{R}  {W}Encore{R}")
    print(f"  {D}|{R}  {D}modified -{R}  {W}Encore Development{R}")
    print(f"  {D}|{R}  {D}source   -{R}  {W}github.com/ChocoMeow/Vocard{R}")
    print(f"  {D}|{'_' * (width - 1)}{R}")
    print()

if __name__ == "__main__":
    update.check_version(with_msg=True)
    print_banner()
    bot.run(bot_config.token, root_logger=True)
