import discord
from discord.ext import commands
import sqlite3
import asyncio
from pagamentos import iniciar_pagamento

class MudarPlano(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='mudar_plano')
    async def mudar_plano(self, ctx):
        """
        Permite ao usuário visualizar seu plano atual e trocar por outro.
        """

        # 1. Verifica login
        if ctx.author.id not in self.bot.sessoes_ativas:
            await ctx.send("❌ Você precisa fazer login primeiro! Use `!login`.")
            return

        usuario = self.bot.sessoes_ativas[ctx.author.id]

        try:
            conn = sqlite3.connect('usuarios.db')
            cursor = conn.cursor()

            # 2. Busca qual o plano ATUAL do usuário (se tiver)
            cursor.execute("""
                SELECT p.nome 
                FROM assinaturas a
                JOIN planos p ON a.plano_id = p.id
                WHERE a.usuario_id = ? AND a.status = 'ativa'
            """, (usuario['id'],))
            
            plano_atual = cursor.fetchone()
            nome_plano_atual = plano_atual[0] if plano_atual else "Nenhum"

            # 3. Busca todos os planos disponíveis para troca
            cursor.execute("SELECT id, nome, descricao, preco, duracao_dias FROM planos")
            planos_disponiveis = cursor.fetchall()
            
            if not planos_disponiveis:
                await ctx.send("⚠️ Não há planos cadastrados no sistema.")
                conn.close()
                return

            # Monta a mensagem visual
            msg = f"🔄 **MUDANÇA DE PLANO** 🔄\n"
            msg += f"👤 Usuário: {usuario['email']}\n"
            msg += f"📊 Plano Atual: **{nome_plano_atual}**\n\n"
            msg += "Escolha o novo plano:\n"

            for i, (pid, nome, desc, preco, dias) in enumerate(planos_disponiveis, 1):
                msg += f"**{i}. {nome}** — R${preco:.2f} ({dias} dias)\n"

            msg += "\nDigite o número do novo plano (ou `cancelar`):"

            await ctx.send(msg)

            # 4. Aguarda escolha do usuário
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            try:
                resposta = await self.bot.wait_for('message', check=check, timeout=60.0)
                escolha = resposta.content.strip().lower()

                if escolha == 'cancelar':
                    await ctx.send("❌ Operação cancelada.")
                    conn.close()
                    return

                if not escolha.isdigit() or not (1 <= int(escolha) <= len(planos_disponiveis)):
                    await ctx.send("❌ Opção inválida.")
                    conn.close()
                    return

                # Pega os dados do plano escolhido
                plano_selecionado = planos_disponiveis[int(escolha) - 1]
                novo_plano_id, novo_nome, novo_desc, novo_preco, novo_dias = plano_selecionado

                # Verifica se o usuário escolheu o mesmo plano que já tem
                if novo_nome == nome_plano_atual:
                    await ctx.send(f"⚠️ Você já possui o plano **{novo_nome}** ativo!")
                    conn.close()
                    return

                # Fecha conexão temporariamente para aguardar pagamento (evita travar banco)
                conn.close() 

                # 5. Processo de Pagamento (Igual ao planos.py)
                pago = await iniciar_pagamento(
                    self.bot,
                    ctx,
                    usuario,
                    novo_nome,
                    novo_preco
                )

                if not pago:
                    await ctx.send("❌ Pagamento não concluído. A mudança de plano foi cancelada.")
                    return

                # 6. Atualiza o Banco de Dados (Reabre conexão)
                conn = sqlite3.connect('usuarios.db')
                cursor = conn.cursor()

                # A) Cancela a assinatura antiga (se existir)
                cursor.execute("""
                    UPDATE assinaturas
                    SET status = 'cancelada'
                    WHERE usuario_id = ? AND status = 'ativa'
                """, (usuario['id'],))

                # B) Insere a nova assinatura
                cursor.execute("""
                    INSERT INTO assinaturas (usuario_id, plano_id, data_inicio, data_fim, status)
                    VALUES (?, ?, datetime('now'), datetime('now', ? || ' days'), 'ativa')
                """, (usuario['id'], novo_plano_id, novo_dias))

                conn.commit()
                conn.close()

                await ctx.send(f"✅ **Sucesso!** Seu plano foi alterado para **{novo_nome}**.")

            except asyncio.TimeoutError:
                await ctx.send("⏱️ Tempo esgotado.")
                conn.close()

        except Exception as e:
            await ctx.send(f"❌ Erro ao processar mudança: {e}")
            print(f"Erro em mudar_plano: {e}")

async def setup(bot):
    await bot.add_cog(MudarPlano(bot))