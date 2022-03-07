from operator import index
import discord
from discord.ext import commands
from config_helper import ConfigHelper
import xmltodict
from requests import request

base_url = 'https://safebooru.org/index.php?page=dapi&s=post&q=index'

req = request('GET', 'https://safebooru.org/index.php?page=dapi&s=post&q=index')
result = xmltodict.parse(req.content)
items = result['posts']['post']

class Safebooru(commands.Cog, name='Safebooru', description='Fetching images from Safebooru'):
    config = ConfigHelper.load_config()
    image_index = 0

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="safebooru", description="Fetch images from Safebooru", guild_ids=config['guild_ids'])
    async def safebooru(self, ctx):
        await ctx.respond(embed = self.get_embed())

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        self.image_index += 1 
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        await message.edit(embed = self.get_embed())

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        self.image_index += 1 
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        await message.edit(embed = self.get_embed())

    def get_embed(self):
        embed = discord.Embed(title = f"Image ID: {items[self.image_index]['@id']}", type= 'rich')
        embed.set_image(url=items[self.image_index]['@preview_url'])
        return embed

def setup(bot):
    bot.add_cog(Safebooru(bot))
