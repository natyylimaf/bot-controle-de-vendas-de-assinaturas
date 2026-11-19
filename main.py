import os
import discord
from dotenv import load_dotenv
import asyncio
from discord.ext import commands
from sessoes import sessoes_ativas

load_dotenv()  # lê o token do arquivo .env

# Configuração do bot
# intents = permissões que o bot precisa
intents = discord.Intents.all()
intents.message_content = True  # Permissão para ler mensagens

# Cria o bot com prefixo ! (ex: !login, !cadastro)
bot = commands.Bot(command_prefix='!', intents=intents)

# cria apenas UMA instância global
sessoes_ativas = {}
bot.sessoes_ativas = sessoes_ativas

# ========================================
# EVENTO: Quando o bot conectar
# ========================================]
@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user}')
    print(f'🤖 Bot pronto para usar!')


# ========================================
# INICIAR O BOT
# ========================================
async def main():
    # Isso permite que a Cog (extensão) 'historico' acesse a variável via self.bot.sessoes_ativas
    bot.sessoes_ativas = sessoes_ativas
    
    # Carrega as extensões e cogs
    await bot.load_extension("ajuda")
    await bot.load_extension("planos")
    await bot.load_extension("cadastro")
    await bot.load_extension("login")
    await bot.load_extension("perfil")
    await bot.load_extension("minha_assinatura")
    await bot.load_extension("mudar_plano") 
    await bot.load_extension("cancelar_assinatura")
    await bot.load_extension("verificar_assinaturas")
    await bot.load_extension("historico")
    await bot.load_extension("excluir_conta") 
    await bot.load_extension("logout") 

    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        raise SystemExit("Defina DISCORD_TOKEN no arquivo .env")

    print("🚀 Iniciando o bot...")
    await bot.start(TOKEN)  # usar .start() em vez de .run() dentro de função async

# executa o bot de forma assíncrona
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Bot desligado.")

