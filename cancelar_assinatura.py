import discord
from discord.ext import commands
import sqlite3


class CancelarAssinatura(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='cancelar_assinatura', aliases=['cancelar', 'encerrar'])
    async def cancelar_assinatura(self, ctx):
        """
        Cancela a assinatura ativa do usuário.
        """

        if ctx.author.id not in self.bot.sessoes_ativas:
            await ctx.send("❌ Você precisa fazer login primeiro! Use `!login`")
            return

        usuario = self.bot.sessoes_ativas[ctx.author.id]


        try:
            conn = sqlite3.connect('usuarios.db')
            cursor = conn.cursor()

            # Verifica se há uma assinatura ativa
            cursor.execute("""
                SELECT id, plano_id FROM assinaturas
                WHERE usuario_id = ? AND status = 'ativa'
                ORDER BY data_inicio DESC
                LIMIT 1
            """, (usuario['id'],))
            assinatura = cursor.fetchone()

            if not assinatura:
                conn.close()
                await ctx.send("ℹ️ Você não possui nenhuma assinatura ativa para cancelar.")
                return

            assinatura_id, plano_id = assinatura

            # Cancela (atualiza o status)
            cursor.execute("""
                UPDATE assinaturas
                SET status = 'cancelada', data_fim = datetime('now')
                WHERE id = ?
            """, (assinatura_id,))

            conn.commit()
            conn.close()

            await ctx.send("❌ Sua assinatura foi **cancelada com sucesso**. Esperamos vê-lo novamente em breve! 💔")

        except Exception as e:
            await ctx.send(f"⚠️ Erro ao cancelar assinatura: {e}")
            print(f"Erro no comando !cancelar_assinatura: {e}")


# Função para registrar o Cog no bot
async def setup(bot):
    await bot.add_cog(CancelarAssinatura(bot))
