import random
import re
from discord.ext import commands
from config_helper import ConfigHelper

class DadMode(commands.Cog, name='Dad mode', description='Hello description, I am dad'):
    trigger_regex = r"^(I'm|I am)\W"
    emote_regex = r'\<(:(.*?):\d{18})\>'
    user_id_regex = r'\<(@!\d{18})\>'
    role_id_regex = r'\<(@&\d{18})\>'
    config = ConfigHelper.load_config()

    def __init__(self, bot):
        self.bot = bot

    def should_trigger(self, percent):
        return random.randrange(100) < percent

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        if re.search(self.trigger_regex, message.content, flags=re.IGNORECASE):
            if self.should_trigger(self.config['dad_mode_trigger_percentage']):
                split_string = re.split(self.trigger_regex, message.content, maxsplit=1, flags=re.IGNORECASE)
                result = re.sub(self.emote_regex, '<\g<2>>', split_string[2])
                userids = re.findall(self.user_id_regex, result)
                roleids = re.findall(self.role_id_regex, result)

                for id_string in userids:
                    id = int(''.join(filter(lambda i: i.isdigit(), id_string)))
                    user = await self.bot.get_or_fetch_user(id)
                    result = result.replace(id_string, user.name)

                for id in roleids:
                    id = int(''.join(filter(lambda i: i.isdigit(), id_string)))
                    role = message.channel.guild.get_role(id)
                    result = result.replace(id_string, role.name)
 
                result = result.replace('@everyone', '<everyone>') 
                # result = result.replace('@here', '<here>')
                await message.channel.send(f"Hello {result}, {split_string[1]} dad")

    @commands.slash_command(name="set-dad-mode-percentage", description="Set trigger percentage for dad mode. 100% if not specified", guild_ids=config['guild_ids'])
    async def set_dad_mode_percentage(self, ctx, percent: int = 100):
        self.config['dad_mode_trigger_percentage'] = percent
        ConfigHelper.save_config(self.config)
        await ctx.respond(f"Dad mode trigger percentage set to {percent}%")

def setup(bot):
    bot.add_cog(DadMode(bot))
