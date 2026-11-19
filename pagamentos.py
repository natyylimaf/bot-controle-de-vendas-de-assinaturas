import asyncio
import discord

async def iniciar_pagamento(bot, ctx, usuario, nome_plano, preco):

    print("BOT ESTÁ ESPERANDO NA DM...")

    try:
        await ctx.author.send(
            f"💳 Você escolheu assinar o plano **{nome_plano}** por **R${preco:.2f}**.\n"
            "Vamos simular o pagamento!\n\n"
            "⚠️ **Use apenas cartões de teste!**\n"
            "Exemplo válido: `4242 4242 4242 4242`\n"
            "Exemplo recusado: `4000 0000 0000 0002`"
        )
    except:
        await ctx.send("❌ Não consegui enviar DM para você! Ative suas mensagens privadas.")
        return False

    # CHECK UNIVERSAL PARA DM
    def check_dm(m):
        return (
            m.author.id == ctx.author.id
            and isinstance(m.channel, (discord.DMChannel, discord.PartialMessageable))
        )

    # 1️⃣ Número do cartão
    await ctx.author.send("📇 Digite o **número do cartão**:")

    try:
        msg_card = await bot.wait_for('message', check=check_dm, timeout=120)
        print("BOT RECEBEU ALGUMA COISA:", msg_card)
        card_number = msg_card.content.strip()
    except Exception as e:
        print("ERRO AO LER CARTÃO:", e)
        await ctx.author.send("⏰ Tempo esgotado. Tente novamente.")
        return False

    # 2️⃣ Nome no cartão
    await ctx.author.send("✍️ Digite o **nome no cartão**:")

    try:
        msg_name = await bot.wait_for('message', check=check_dm, timeout=120)
        nome_cartao = msg_name.content.strip()
    except:
        await ctx.author.send("⏰ Tempo esgotado. Tente novamente.")
        return False

    # PROCESSANDO
    await ctx.author.send("⏳ Processando pagamento...")
    await asyncio.sleep(2)

    # SIMULA RECUSA
    if card_number.replace(" ", "").endswith("0002"):
        await ctx.author.send("❌ **Pagamento recusado** (simulação: cartão inválido).")
        return False

    # SUCESSO
    await ctx.author.send(
        f"✅ Pagamento aprovado!\n"
        f"💰 Valor: R$ {preco:.2f}\n"
        f"📦 Plano: {nome_plano}"
    )

    return True
