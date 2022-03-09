import discord
from discord.ext import commands
from config_helper import ConfigHelper
import xmltodict
import requests

base_url = 'https://safebooru.org/index.php?page=dapi&s=post&q=index'
req_header = {
    "Cache-Control": "no-cache",
    "Pragma": "no-cache"
}

def get_images(tags):
    formatted_tags = tags.replace(' ', '%20')
    url = base_url + f'&tags={formatted_tags}'
    req = requests.get(url, headers=req_header)
    result = xmltodict.parse(req.content)
    return result['posts']['post']

def get_embed(images, image_index):
    embed = discord.Embed(title = f"Image ID: {images[image_index]['@id']}", type= 'rich')
    embed.set_author(name = 'Safebooru')
    embed.set_footer(text = f"URL: {images[image_index]['@file_url']}")
    embed.description = f"{images[image_index]['@tags']}"
    embed.set_image(url = images[image_index]['@sample_url'])
    return embed

async def add_reaction(msg):
    await msg.add_reaction('⬅️')
    await msg.add_reaction('➡️')

class Safebooru(commands.Cog, name='Safebooru', description='Fetching images from Safebooru'):
    config = ConfigHelper.load_config()
    image_index = 0
    images = []

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="safebooru", description="Fetch images from Safebooru", guild_ids=config['guild_ids'])
    async def safebooru(self, ctx, tags):
        self.images = get_images(tags)
        await ctx.respond('Searching for images with tags: {}'.format(tags))
        msg = await ctx.send(embed = get_embed(self.images, self.image_index))
        await add_reaction(msg)

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
                await message.edit(embed = get_embed(self.images, self.image_index))
            elif payload.emoji == discord.PartialEmoji.from_str('⬅️'):
                self.image_index -= 1
                await message.edit(embed = get_embed(self.images, self.image_index))

    @commands.slash_command(name="safebooru-nisekoi", description="Fetch Nisekoi character images from Safebooru", guild_ids=config['guild_ids'])
    async def safebooru_nisekoi(self, ctx):
        NisekoiCharacter = [
            'Ichijou Raku',
            'Kirisaki Chitoge',
            'Onodera Kosaki',
            'Miyamoto Ruri',
            'Tachibana Marika', 
            'Tsugumi Seishirou', 
            'Onodera Haru',
            'Maiko Shuu',
            'Kanakura Yui'
        ]

        view = discord.ui.View(timeout = None)

        for character in NisekoiCharacter:
            view.add_item(CharacterButton(character))
        
        await ctx.respond("Choose your character", view = view)

class CharacterButton(discord.ui.Button):
    images = []
    image_index = 0
    def __init__(self, character_name: str):
        super().__init__(
            label=character_name,
            style=discord.enums.ButtonStyle.primary,
        )

    async def callback(self, interaction: discord.Interaction):
        tags = self.label.lower().replace(' ', '_')
        self.images = get_images(tags)
        Safebooru.images = self.images
        await interaction.response.send_message('Searching Safebooru for images of {}'.format(self.label))
        msg = await interaction.followup.send(embed = get_embed(self.images, self.image_index))
        await add_reaction(msg)        
    
def setup(bot):
    bot.add_cog(Safebooru(bot))