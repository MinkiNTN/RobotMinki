import discord
from discord.ext import commands, pages
from config_helper import ConfigHelper
import xmltodict
import requests
import re

base_url = 'https://safebooru.org/index.php?page=dapi&s=post&q=index'

def get_images(tags):
    """Get images based on the tags from Safebooru API.
    If no tags is passed, fetch the most recent list (hard cap at 100)"""
    images = []
    pid = 0
    formatted_tags = tags.replace(' ', '%20')
    url = base_url + f'&tags={formatted_tags}'
    req = requests.get(url)
    count = int(re.search(r'count=\"(.*?)\"', req.text).group(1))
    if tags != '':
        while len(images) != count:
            if len(images) >= 100:
                url_with_id = url + f'&pid={pid}'
                req = requests.get(url_with_id)
            result = xmltodict.parse(req.content)
            image_list = result['posts']['post']
            for image in image_list:
                images.append(image)
            pid += 1
        return images
    else:
        result = xmltodict.parse(req.content)
        return result['posts']['post']

def get_embed(image):
    embed = discord.Embed(title = f"Image ID: {image['@id']}", type= 'rich')
    embed.set_author(name = 'Safebooru')
    embed.set_footer(text = f"{image['@file_url']}")
    embed.description = f"{image['@tags']}"
    embed.set_image(url = image['@sample_url'])
    return embed

def get_paginator(images):
    embeds = []
    for image in images:
        embeds.append(get_embed(image))
    return pages.Paginator(pages=embeds, loop_pages=True)

class CharacterButton(discord.ui.Button):
    images = []
    image_index = 0
    def __init__(self, character_name: str):
        super().__init__(
            label=character_name,
            style=discord.enums.ButtonStyle.primary,
            custom_id=character_name.lower().replace(' ', '_')
        )

    async def callback(self, interaction: discord.Interaction):
        paginator = get_paginator(get_images(self.custom_id))
        if paginator != None:
            await paginator.respond(interaction, ephemeral=False)

class Safebooru(commands.Cog, name='Safebooru', description='Fetching images from Safebooru'):
    config = ConfigHelper.load_config()
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

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="safebooru", description="Fetch images from Safebooru", guild_ids=config['guild_ids'])
    async def safebooru(self, ctx, tags: discord.Option(str, "Enter your tags", required = False, default = '')):
        paginator = get_paginator(get_images(tags))
        if paginator != None:
            if tags == '':
                await ctx.respond('Fetching 100 most recent uploads')
            else:
                await ctx.respond('Searching for images with tags: {}'.format(tags))
            await paginator.respond(ctx.interaction, ephemeral=False)
        else:
            await ctx.respond('Error fetching images. Please try again later.')

    def create_nisekoi_view(self):
        view = discord.ui.View(timeout = None)

        for character in self.NisekoiCharacter:
            view.add_item(CharacterButton(character))
        return view

    @commands.slash_command(name="safebooru-nisekoi", description="Fetch Nisekoi character images from Safebooru", guild_ids=config['guild_ids'])
    async def safebooru_nisekoi(self, ctx):
        await ctx.respond("Choose your character", view = self.create_nisekoi_view())

    @commands.Cog.listener()
    async def on_ready(self):
        """This method is called every time the bot restarts.
        If a view was already created before (with the same custom IDs for buttons)
        it will be loaded and the bot will start watching for button clicks again.
        """
        self.bot.add_view(self.create_nisekoi_view())
    
def setup(bot):
    bot.add_cog(Safebooru(bot))