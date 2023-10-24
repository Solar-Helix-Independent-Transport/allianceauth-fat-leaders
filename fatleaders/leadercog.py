# Cog Stuff
from discord.ext import commands
import discord

# AA Contexts
from django.conf import settings
from aadiscordbot.cogs.utils.decorators import is_admin
from .tasks import post_all_corporate_leader_boards

import logging

logger = logging.getLogger(__name__)


class FatLeaders(commands.Cog):
    """
    Fat LEADERS!
    """
    def __init__(self, bot):
        self.bot = bot


    @commands.slash_command(name='gib_corp_leaderboards', guild_ids=[int(settings.DISCORD_GUILD_ID)])
    async def me(self, ctx,
                 bg:discord.Option(str, choices=["Light", "Dark", "crinkle_paper.jpg"]), 
                 font:discord.Option(str, choices=["OpenSans", "Brookeshappell", "ThedoctorIsIn", "GradeSkooler", "FakeBoyfriend"])):
        """
        Spit out the fat Leaderboard
        """
        try:
            await ctx.defer(ephemeral=True)
            
            if is_admin(ctx.author.id):
                
                post_all_corporate_leader_boards.delay(current_month=True, channel_id=ctx.channel.id, bg=bg, font=font)
            await ctx.respond("Requested! Standby!", ephemeral=True)
        except commands.MissingPermissions as e:
            return await ctx.respond(e.missing_permissions[0], ephemeral=True)


def setup(bot):
    bot.add_cog(FatLeaders(bot))
