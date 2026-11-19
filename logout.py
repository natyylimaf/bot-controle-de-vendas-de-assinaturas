import discord
from discord.ext import commands
from sessoes import sessoes_ativas

class Logout(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ========================================
    # COMANDO: !logout
    # ========================================
    @commands.command(name='logout')
    async def logout(self, ctx):
        """Desloga o usuário do sistema"""
        if ctx.author.id not in self.bot.sessoes_ativas:
            await ctx.send(f"ℹ️ {ctx.author.mention}, você não está logado!")
            return

        # Remove o usuário da sessão ativa
        self.bot.sessoes_ativas.pop(ctx.author.id)
        await ctx.send(f"✅ {ctx.author.mention}, você foi deslogado com sucesso!")

# 🔧 Função obrigatória para registrar o módulo no bot
async def setup(bot):
    await bot.add_cog(Logout(bot))
