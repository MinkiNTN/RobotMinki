import discord

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

async def get_nisekoi_character(ctx: discord.AutocompleteContext):
    """Returns a list of Nisekoi characters that begin with the characters entered so far."""
    return [character for character in NisekoiCharacter if character.startswith(ctx.value.lower())]
