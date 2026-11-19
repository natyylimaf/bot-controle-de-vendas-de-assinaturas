import discord
from discord.ext import commands, tasks
import sqlite3
from datetime import datetime


class VerificarAssinaturas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.avisados = set()      # evita avisos repetidos
        self.verificar.start()   # inicia a task automática

    def cog_unload(self):
        self.verificar.cancel()  # caso a cog seja recarregada

    @tasks.loop(hours=1)  # roda automaticamente a cada 1 hora
    async def verificar(self):
        try:
            conn = sqlite3.connect("usuarios.db")
            cursor = conn.cursor()

            cursor.execute("""
                SELECT usuario_id, data_fim
                FROM assinaturas
                WHERE status = 'ativa'
            """)
            assinaturas = cursor.fetchall()
            conn.close()

            agora = datetime.now()

            for usuario_id, data_fim in assinaturas:
                expira = datetime.strptime(data_fim, "%Y-%m-%d %H:%M:%S")
                dias_faltando = (expira - agora).days

                # descobre o id do Discord de quem está logado com esse usuário
                discord_id = next(
                    (d for d, u in self.bot.sessoes_ativas.items() if u["id"] == usuario_id),
                    None
                )
                user = self.bot.get_user(discord_id) if discord_id else None

                if not user or dias_faltando not in (0, 1):
                    continue

                chave = (usuario_id, data_fim, dias_faltando)
                if chave in self.avisados:
                    continue

                if dias_faltando == 1:
                    texto = "⚠️ *Aviso importante!*\nSeu plano expira **amanhã**!\nUse `!planos` para renovar."
                else:
                    texto = "🔔 Seu plano expira **hoje**!\nUse `!planos` para renovar quando quiser."

                try:
                    await user.send(texto)
                    self.avisados.add(chave)
                except discord.Forbidden:
                    pass

        except Exception as e:
            print("Erro ao verificar assinaturas:", e)

    @verificar.before_loop
    async def before_verificar(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(VerificarAssinaturas(bot))
