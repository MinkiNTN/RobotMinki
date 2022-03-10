import discord
from discord.ext import commands, pages
from config_helper import ConfigHelper
import xmltodict
import requests
import re
from datetime import datetime
import random

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
            images = images + result['posts']['post']
            pid += 1
        return images
    else:
        result = xmltodict.parse(req.content)
        return result['posts']['post']

def get_embed(image):
    embed = discord.Embed(title = f"Image ID: {image['@id']}", type= 'rich')
    embed.set_author(name = 'Safebooru')
    embed.set_footer(text = f"Posted on: {datetime.strptime(image['@created_at'], '%a %b %d %H:%M:%S %z %Y')}")
    embed.description = f"{image['@tags']}"
    embed.set_image(url = image['@sample_url'])
    embed.url = image['@file_url']
    return embed

def get_paginator(images):
    embeds = []
    for image in images:
        embeds.append(get_embed(image))
    return pages.Paginator(pages=embeds, loop_pages=True)

class Safebooru(commands.Cog, name='Safebooru', description='Fetching images from Safebooru'):
    config = ConfigHelper.load_config()

    NisekoiCharacter = [
        'Ichijou Raku',
        'Kanakura Yui',
        'Kirisaki Chitoge',
        'Maiko Shuu',
        'Miyamoto Ruri',
        'Onodera Haru',
        'Onodera Kosaki',
        'Tachibana Marika',
        'Tsugumi Seishirou',
    ]

    def __init__(self, bot):
        self.bot = bot

    async def get_nisekoi_character(self,ctx: discord.AutocompleteContext):
        """Returns a list of Nisekoi characters that begin with the characters entered so far."""
        return [character for character in self.NisekoiCharacter if character.startswith(ctx.value.lower())]

    @commands.slash_command(name="safebooru", description="Fetch images from Safebooru", guild_ids=config['guild_ids'])
    async def safebooru(self, 
            ctx: discord.ApplicationContext,
            tags: discord.Option(str, "Enter your tags (characters will take priority).", required = False, default = ''), 
            nisekoi_character: discord.Option(str, "Choose your favorite Nisekoi character.", required = False, autocomplete=get_nisekoi_character),
            randomise: discord.Option(bool, "Randomise the results?", default="True")
        ):
        if nisekoi_character != None: # A character is selected
            await ctx.respond(f"Fetching images of {nisekoi_character}")
            tags = nisekoi_character.lower().replace(' ', '_') # Set tag to character's name
        elif tags == '': # No tags => Get recent
            await ctx.respond('Fetching 100 most recent uploads')
        else: # Fetch based on tag
            await ctx.respond('Searching for images with tags: {}'.format(tags))

        images = get_images(tags=tags)
        if randomise:
            images = random.sample(images, len(images))

        paginator = get_paginator(images)
        if paginator != None:
            await paginator.respond(ctx.interaction, ephemeral=False)
        else:
            await ctx.followup.send(f"Error fetching images, please try again later.")
    
def setup(bot):
    bot.add_cog(Safebooru(bot))