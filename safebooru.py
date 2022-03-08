import discord
from discord.ext import commands
from config_helper import ConfigHelper
import xmltodict
import requests

class Safebooru(commands.Cog, name='Safebooru', description='Fetching images from Safebooru'):
    config = ConfigHelper.load_config()
    base_url = 'https://safebooru.org/index.php?page=dapi&s=post&q=index'
    req_header = {
        "Cache-Control": "no-cache",
        "Pragma": "no-cache"
    }
    image_index = 0
    images = []

    def __init__(self, bot):
        self.bot = bot

    def get_images(self, tags):
        formatted_tags = tags.replace(' ', '%20')
        url = self.base_url + f'&tags={formatted_tags}'
        req = requests.get(url, headers=self.req_header)
        result = xmltodict.parse(req.content)
        return result['posts']['post']

    def get_embed(self):
        embed = discord.Embed(title = f"Image ID: {self.images[self.image_index]['@id']}, {self.image_index}/{len(self.images)}", type= 'rich')
        embed.set_image(url=self.images[self.image_index]['@sample_url'])
        return embed

    @commands.slash_command(name="safebooru", description="Fetch images from Safebooru", guild_ids=config['guild_ids'])
    async def safebooru(self, ctx, tags):
        self.images = self.get_images(tags)
        await ctx.respond('Searching for images with tags: {}'.format(tags))
        msg = await ctx.send(embed = self.get_embed())
        await msg.add_reaction('⬅️')
        await msg.add_reaction('➡️')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        await self.handle_emoji_reaction(payload)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        await self.handle_emoji_reaction(payload)

    async def handle_emoji_reaction(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if payload.user_id != self.config['bot_id'] and message.author.bot:
            if payload.emoji == discord.PartialEmoji.from_str('➡️'):
                self.image_index += 1
                await message.edit(embed = self.get_embed())
            elif payload.emoji == discord.PartialEmoji.from_str('⬅️'):
                self.image_index -= 1
                await message.edit(embed = self.get_embed())

def setup(bot):
    bot.add_cog(Safebooru(bot))