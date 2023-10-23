# Cog Stuff
from discord.ext import commands

# AA Contexts
from django.conf import settings
from aadiscordbot.cogs.utils.decorators import is_admin
from .tasks import post_all_leader_boards

import logging

logger = logging.getLogger(__name__)


class FatLeaders(commands.Cog):
    """
    Fat LEADERS!
    """
    def __init__(self, bot):
        self.bot = bot


    @commands.slash_command(name='gib_corp_leaderboards', guild_ids=[int(settings.DISCORD_GUILD_ID)])
    async def me(self, ctx, alternate:bool = False):
        """
        Spit out the fat Leaderboard
        """
        try:
            await ctx.defer(ephemeral=True)
            
            if is_admin(ctx.author.id):
                alt = alternate and ctx.author.id == 318309023478972417
                post_all_leader_boards.delay(current_month=True, channel_id=ctx.channel.id, fun=alt)
            await ctx.respond("Requested! Standby!", ephemeral=True)
        except commands.MissingPermissions as e:
            return await ctx.respond(e.missing_permissions[0], ephemeral=True)


def setup(bot):
    bot.add_cog(FatLeaders(bot))
