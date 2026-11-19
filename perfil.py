import discord
from discord.ext import commands

class Perfil(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='perfil')
    async def perfil(self, ctx):
        """
        Mostra informações do usuário logado
        """
        if ctx.author.id not in self.bot.sessoes_ativas:
            await ctx.send("❌ Você precisa fazer login primeiro! Use `!login`")
            return

        usuario = self.bot.sessoes_ativas[ctx.author.id]

        await ctx.send(f"""
👤 **SEU PERFIL**

**Nome:** {usuario['nome']}
**E-mail:** {usuario['email']}
**Cadastro:** {usuario['data_cadastro']}
**ID:** {usuario['id']}
        """)


# Função para registrar o comando no bot
async def setup(bot):
    await bot.add_cog(Perfil(bot))
