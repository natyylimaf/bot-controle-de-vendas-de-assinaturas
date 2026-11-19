import discord
from discord.ext import commands

class Ajuda(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ajuda')
    async def ajuda(self, ctx):
        await ctx.send("""
🤖 **COMANDOS DISPONÍVEIS**

`!cadastro` - Fazer cadastro no sistema
`!login` - Fazer login no sistema
`!logout` - Sair da conta
`!perfil` - Ver suas informações
`!planos` - Ver planos disponíveis e escolher        
`!minha_assinatura` - Ver sua assinatura
`!mudar_plano` - Mudar seu plano de assinatura
`!cancelar_assinatura` - Cancela sua assinatura
`!historico` - Ver histórico completo de assinaturas
`!estatisticas` - Ver estatísticas e total gasto
`!excluir_conta` - Exclui permanentemente sua conta
`!ajuda` - Mostrar esta mensagem
        """)

# Função de setup ASSÍNCRONA
async def setup(bot):
    await bot.add_cog(Ajuda(bot))
