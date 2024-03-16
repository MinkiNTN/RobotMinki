import discord
from discord.ext import commands
from config_helper import ConfigHelper

class ManageChannel(commands.Cog, name='Channel manager', description='Automatically hide/unhide channels'):
    config = ConfigHelper.load_config()
    config_key = 'is_channel_manager_enabled'

    def __init__(self, bot):
        self.bot = bot

    def should_trigger(self):
        return self.config[self.config_key]

    @commands.slash_command(name="channel-manage", description="Enable/Disable automatic channel hide feature.", guild_ids=config['guild_ids'])
    async def enable_channel_manage(self, ctx, enable: bool):
        if enable is not None:
            self.config[self.config_key] = enable
        else:
            ctx.respond(f"Please specify if you want to enable or disable the feature.")

        try:
            ConfigHelper.save_config(self.config)
            enableText = "enable" if enable else "disable"
            await ctx.respond(f"Channel manage feature is now {enableText}d.")
        except PermissionError:
            await ctx.respond(f"Failed to {enableText} channel manage feature. Error occured saving config file.")

    @commands.slash_command(name="channel-manage-test", description="Test command for development", guild_ids=config['guild_ids'])
    async def test(self, ctx, channel: discord.Option(discord.SlashCommandOptionType.channel)):
        print(channel.id)
        perms = channel.overwrites_for(ctx.guild.default_role)
        print(perms.view_channel)
        perms.view_channel = False

        try:
            await channel.set_permissions(ctx.guild.default_role, overwrite=perms)
            await ctx.respond(f"{perms.view_channel}")
        except discord.InvalidArgument as e:
            print(e)
            await ctx.respond(f"InvalidArgument")
        except discord.Forbidden:
            await ctx.respond(f"The bot does not have permission to modify this channel.")
        except discord.HTTPException as e:
            error_code = e.status
            await ctx.respond(f"HTTP Exception occurred with error code: {error_code}")

def setup(bot):
    bot.add_cog(ManageChannel(bot))
