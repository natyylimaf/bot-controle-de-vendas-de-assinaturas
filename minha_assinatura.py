import discord
from discord.ext import commands
import sqlite3


class MinhaAssinatura(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='minha_assinatura', aliases=['assinatura', 'plano_atual'])
    async def minha_assinatura(self, ctx):
        """
        Mostra o plano atual do usuário logado.
        """

        if ctx.author.id not in self.bot.sessoes_ativas:
            await ctx.send("❌ Você precisa fazer login primeiro! Use `!login`")
            return

        usuario = self.bot.sessoes_ativas[ctx.author.id]

        try:
            conn = sqlite3.connect('usuarios.db')
            cursor = conn.cursor()

            # Busca a assinatura ativa do usuário
            cursor.execute("""
                SELECT a.id, p.nome, p.preco, p.duracao_dias, a.data_inicio, a.data_fim, a.status
                FROM assinaturas a
                JOIN planos p ON a.plano_id = p.id
                WHERE a.usuario_id = ? AND a.status = 'ativa'
                ORDER BY a.data_inicio DESC
                LIMIT 1
            """, (usuario['id'],))
            assinatura = cursor.fetchone()
            conn.close()

            if assinatura:
                id_assin, nome_plano, preco, dias, inicio, fim, status = assinatura
                await ctx.send(f"""
💼 **SUA ASSINATURA ATUAL**

📦 **Plano:** {nome_plano}
💰 **Valor:** R${preco:.2f}
📅 **Início:** {inicio}
📅 **Término:** {fim}
⚙️ **Status:** {status}

🎉 Obrigado por ser nosso assinante!
                """)
            else:
                await ctx.send("ℹ️ Você não possui nenhuma assinatura ativa. Use `!planos` para escolher um plano.")

        except Exception as e:
            await ctx.send(f"⚠️ Erro ao buscar assinatura: {e}")
            print(f"Erro no comando !minha_assinatura: {e}")


# Função que registra o Cog no bot
async def setup(bot):
    await bot.add_cog(MinhaAssinatura(bot))
