import discord
from discord.ext import commands
import sqlite3
import asyncio
from pagamentos import iniciar_pagamento  


class Planos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='planos')
    async def planos(self, ctx):

        if ctx.author.id not in self.bot.sessoes_ativas:
            await ctx.send("❌ Você precisa fazer login primeiro! Use `!login`.")
            return

        usuario = self.bot.sessoes_ativas[ctx.author.id]

        try:
            conn = sqlite3.connect('usuarios.db')
            cursor = conn.cursor()

            cursor.execute("SELECT id, nome, descricao, preco, duracao_dias FROM planos")
            planos = cursor.fetchall()
            conn.close()

            if not planos:
                await ctx.send("⚠️ Nenhum plano disponível no momento.")
                return

            # Mostra os planos
            msg = "💎 **PLANOS DISPONÍVEIS** 💎\n\n"
            for i, (pid, nome, desc, preco, dias) in enumerate(planos, 1):
                msg += f"**{i}. {nome}** — R${preco:.2f} / {dias} dias\n📜 {desc}\n\n"
            msg += "Digite o número do plano que deseja assinar (ou digite `cancelar`):"

            await ctx.send(msg)

            # espera resposta
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            r = await self.bot.wait_for("message", check=check, timeout=60)
            escolha = r.content.strip().lower()

            # Permitir cancelar
            if escolha == "cancelar":
                await ctx.send("❌ Operação cancelada pelo usuário.")
                return

            # Verifica se é um número válido
            if not escolha.isdigit() or not (1 <= int(escolha) <= len(planos)):
                await ctx.send("❌ Opção inválida. Digite um número válido ou 'cancelar'.")
                return

            plano = planos[int(escolha) - 1]
            plano_id, nome_plano, desc, preco, dias = plano


            # 1️⃣ CHAMA O PAGAMENTO ANTES DE REGISTRAR ASSINATURA
            pago = await iniciar_pagamento(
                self.bot,
                ctx,
                usuario,
                nome_plano,
                preco
            )

            if not pago:
                await ctx.send("❌ Pagamento não concluído. Assinatura cancelada.")
                return

            # 2️⃣ REGISTRA ASSINATURA APÓS PAGAMENTO APROVADO
            conn = sqlite3.connect('usuarios.db')
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE assinaturas
                SET status = 'cancelada'
                WHERE usuario_id = ? AND status = 'ativa'
            """, (usuario["id"],))

            cursor.execute("""
                INSERT INTO assinaturas (usuario_id, plano_id, data_inicio, data_fim, status)
                VALUES (?, ?, datetime('now'), datetime('now', ? || ' days'), 'ativa')
            """, (usuario['id'], plano_id, dias))

            conn.commit()
            conn.close()

            await ctx.send(
                f"🎉 **Assinatura confirmada!**\n\n"
                f"📦 Plano: {nome_plano}\n"
                f"💰 Valor: R${preco:.2f}\n"
                f"📅 Duração: {dias} dias"
            )

        except asyncio.TimeoutError:
            await ctx.send("⏰ Tempo esgotado.")
        except Exception as e:
            await ctx.send(f"⚠️ Erro: {e}")
            print(e)


async def setup(bot):
    await bot.add_cog(Planos(bot))
