import discord
from discord.ext import commands
from auth import AuthSystem  # Importa a classe de autenticação
from sessoes import sessoes_ativas

class Login(commands.Cog):
    """
    Módulo responsável pelo comando !login
    """
    def __init__(self, bot):
        self.bot = bot
        self.auth = AuthSystem()  # Cria instância do sistema de autenticação

    @commands.command(name='login')
    async def login(self, ctx):
        # Verifica se já está logado
        if ctx.author.id in self.bot.sessoes_ativas:
            usuario = self.bot.sessoes_ativas[ctx.author.id]
            await ctx.send(f"ℹ️ {ctx.author.mention}, você já está logado como **{usuario['nome']}**!")
            return

        # Pede as credenciais
        await ctx.send(f"🔐 {ctx.author.mention}, me envie suas credenciais no formato:\n"
                       "`email | senha`\n\nExemplo: `maria@email.com | senha123`")

        # Função para verificar se a próxima mensagem é do mesmo usuário
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            # Aguarda a resposta do usuário (timeout de 60 segundos)
            msg = await self.bot.wait_for('message', check=check, timeout=60.0)

            # IMPORTANTE: Deleta a mensagem com a senha por segurança!
            await msg.delete()

            # Separa o email e senha
            dados = msg.content.split('|')

            if len(dados) != 2:
                await ctx.send("❌ Formato inválido! Use: `email | senha`")
                return

            email = dados[0].strip()
            senha = dados[1].strip()

            # Valida o email
            if not self.auth.validar_email(email):
                await ctx.send("❌ E-mail inválido!")
                return

            # Tenta fazer login
            usuario = self.auth.login(email, senha)

            if usuario:
                # Login bem-sucedido → guarda sessão
                self.bot.sessoes_ativas[ctx.author.id] = usuario

                await ctx.send(f"""
✅ **Login realizado com sucesso!**

👤 **Nome:** {usuario['nome']}
📧 **E-mail:** {usuario['email']}
📅 **Membro desde:** {usuario['data_cadastro']}

🎉 Bem-vindo(a) de volta!
                """)
            else:
                await ctx.send("❌ E-mail ou senha incorretos! Tente novamente com `!login`")

        except Exception as e:
            await ctx.send(f"⏰ Tempo esgotado ou erro! Tente novamente com `!login`\nErro: {e}")


# Função de setup obrigatória para Cogs
async def setup(bot):
    await bot.add_cog(Login(bot))
