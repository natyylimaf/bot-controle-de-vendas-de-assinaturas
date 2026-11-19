import discord
from discord.ext import commands, tasks
import sqlite3
from datetime import datetime


class VerificarAssinaturas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
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

                user = self.bot.get_user(usuario_id)

                if user:
                    if dias_faltando == 1:
                        try:
                            await user.send(
                                "⚠️ *Aviso importante!*\n"
                                "Seu plano expira **amanhã**!\n"
                                "Deseja renovar?"
                            )
                        except:
                            pass

                    if dias_faltando == 0:
                        try:
                            await user.send(
                                "🔔 Seu plano expira **hoje**!\n"
                                "Use `!planos` para renovar quando quiser."
                            )
                        except:
                            pass

        except Exception as e:
            print("Erro ao verificar assinaturas:", e)

    @verificar.before_loop
    async def before_verificar(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(VerificarAssinaturas(bot))
