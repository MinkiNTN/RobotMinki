import discord
from discord.ext import commands
from discord.commands import Option
import logging
from config_helper import ConfigHelper

# Logger setup
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler) 
# End logger setup

intents = discord.Intents.default()
intents.messages = True

bot = commands.Bot(
    command_prefix="$",
    description="A description",
    intents=intents,
)
guild_ids = []

extensions = ['dad_mode']

# Config related stuff
config = ConfigHelper.load_config()
token = config['bot_token']
for id in config['guild_ids']:
    guild_ids.append(id)
    
# Bot related stuff
@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="the world burn. $ prefix"))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    # Ping Pong~
    if message.content == "Ping":
        await message.channel.send('Pong')
    # Eris classic #1: k den
    if message.content == "k den":
        await message.channel.send('k den')
    # Eris classic #2: smooches
    if ConfigHelper.id_is_in_whitelist(message.author.id, config['smooches_whitelist']) and message.content == "smooches":
        await message.channel.send(embed=smooches())
    # Eris classic #3: wahhhh
    if ConfigHelper.id_is_in_whitelist(message.author.id, config['wahhhh_whitelist']) and message.content == 'wahhhh':
        await message.channel.send(embed=wahhhh())
    # Nothing matches, boo~
    await bot.process_commands(message)

@bot.command()
async def test(ctx):
    await ctx.send("Test command~ Beep boop.") 

@bot.slash_command(name="greet", description="Greetings~!", guild_ids=guild_ids)
async def greet(ctx, name: str = None):
    name = name or ctx.author.name
    await ctx.respond(f"Hello {name}!")

def smooches():
    embed = discord.Embed(title = "Anon U-Turn!", type= 'rich')
    embed.set_image(url="https://i.imgur.com/PfzW3oz.gif")
    return embed

def wahhhh():
    embed = discord.Embed(title = "Wahhhh~ (RIP Eris)", type= 'rich')
    embed.set_image(url="https://i.imgur.com/f1ctVoD.gif")
    return embed

# Shutdown function
@bot.command(name='shutdown')
@commands.is_owner()
async def shutdown(ctx):
    await ctx.send("Bot is now shutting down.")
    bot.clear()
    await bot.close()

# Cog reload funtion
async def get_extensions(ctx: discord.AutocompleteContext):
    """Returns a list of extensions that begin with the characters entered so far."""
    return [extension for extension in extensions if extension.startswith(ctx.value.lower())]

@bot.slash_command(name="reload", description="Reload the specified extension", guild_ids=guild_ids)
async def reload(
        ctx: discord.ApplicationContext,
        extension: Option(str, "Enter in the extension name.", autocomplete=get_extensions)
    ):
    try:
        bot.reload_extension(f"{extension}")
        embed = discord.Embed(title='Reload Successfully', description=f'{extension} successfully reloaded.', color=0x00FF00)
    except discord.ExtensionNotLoaded:
        embed = discord.Embed(title='Reload Failed', description=f'{extension} does not exist, or has not been loaded.', color=0xFF0000)
    await ctx.respond(embed=embed)

# Load the extensions
for extension in extensions:
    bot.load_extension(f'{extension}')
# Let's do it
bot.run(token)