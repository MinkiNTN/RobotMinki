import discord
from discord.ext import commands
from config_helper import ConfigHelper
import shared
import fandom

class NisekoiLookup(commands.Cog, name='Nisekoi lookup tool', description='Fetching Nisekoi related stuff from Fandom Wiki'):
    config = ConfigHelper.load_config()

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        fandom.set_wiki("Nisekoi")
    
    nisekoi_lookup = discord.SlashCommandGroup('nisekoi-lookup', 'Fetching Nisekoi related stuff from Fandom Wiki', guild_ids=config['guild_ids'])

    @nisekoi_lookup.command(name='character', description='Get a character wiki page')
    async def character(self, 
            ctx: discord.ApplicationContext,
            name: discord.Option(str, "Choose your favorite Nisekoi character.", required = True, autocomplete=shared.get_nisekoi_character)):
        page = fandom.page(name)
        await ctx.respond('[Testing] Page summary: {}'.format(page.summary))

def setup(bot):
    bot.add_cog(NisekoiLookup(bot))