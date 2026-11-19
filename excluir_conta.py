import discord
from discord.ext import commands
import asyncio
import sqlite3

from sessoes import sessoes_ativas
from auth import AuthSystem

auth = AuthSystem()

class ExcluirConta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='excluir_conta')
    async def excluir_conta(self, ctx):
        """
        Permite ao usuário excluir permanentemente sua conta.
        Requer confirmação de senha.
        """

        # 1. Verifica se está logado
        if ctx.author.id not in self.bot.sessoes_ativas:
            await ctx.send("❌ Você precisa fazer login primeiro! Use `!login`")
            return

        usuario = self.bot.sessoes_ativas[ctx.author.id]

        # 2. Pede confirmação (senha)
        await ctx.send(f"""
⚠️ **ATENÇÃO, {ctx.author.mention}!** ⚠️

Esta ação é **PERMANENTE** e **IRREVERSÍVEL**.
Todos os seus dados, incluindo perfil e assinaturas, serão **excluídos para sempre**.

Para confirmar a exclusão da sua conta (`{usuario['email']}`), por favor, digite sua **SENHA**:
        """)

        # 3. Aguarda a senha
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=60.0)
            senha = msg.content.strip()

            # 4. Deleta a mensagem com a senha por segurança
            try:
                await msg.delete()
            except discord.Forbidden:
                await ctx.send("ℹ️ *Não tenho permissão para deletar sua mensagem de senha, mas ela será processada.*")

            # 5. Tenta excluir a conta usando o AuthSystem
            sucesso = auth.excluir_conta(usuario['id'], senha)

            if sucesso:
                # 6. Se deu certo, desloga o usuário
                del self.bot.sessoes_ativas[ctx.author.id]
                await ctx.send(f"✅ **Conta excluída com sucesso.**\nSentiremos sua falta, {usuario['nome']}. Adeus.")
            else:
                await ctx.send("❌ **Senha incorreta!** A exclusão da conta foi cancelada.")

        except asyncio.TimeoutError:
            await ctx.send("⏰ Tempo esgotado! A exclusão da conta foi cancelada.")
        except Exception as e:
            await ctx.send(f"⚠️ Erro inesperado durante a exclusão: {e}")
            print(f"Erro no !excluir_conta: {e}")


async def setup(bot):
    await bot.add_cog(ExcluirConta(bot))
