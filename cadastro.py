import discord
import asyncio
from discord.ext import commands
from auth import AuthSystem

class Cadastro(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.auth = AuthSystem()

    @commands.command(name='cadastro', aliases=['registrar', 'register'])
    async def cadastro(self, ctx):
        """Sistema de cadastro de novos usuários"""

        # Verifica se já está logado
        if ctx.author.id in self.bot.sessoes_ativas:
            await ctx.send(f"ℹ️ {ctx.author.mention}, você já está logado! Use `!logout` primeiro se quiser criar outra conta.")
            return

        await ctx.send(f"📬 {ctx.author.mention}, te enviei uma mensagem privada! Verifique sua DM.")

        try:
            # Cria canal de DM
            dm = await ctx.author.create_dm()

            # ===== PASSO 1: NOME =====
            await dm.send("""
╔═══════════════════════════════╗
║  📝 CADASTRO - PASSO 1/3     ║
╚═══════════════════════════════╝

Por favor, digite seu **nome completo**:

Exemplo: João Silva
            """)

            def check_dm(m):
                return m.author == ctx.author and isinstance(m.channel, discord.DMChannel)

            msg_nome = await self.bot.wait_for('message', check=check_dm, timeout=120.0)
            nome = msg_nome.content.strip()

            if len(nome) < 3:
                await dm.send("❌ Nome muito curto! Tente novamente com `!cadastro`.")
                return

            if len(nome) > 100:
                await dm.send("❌ Nome muito longo! Máximo de 100 caracteres.\n\nTente novamente com `!cadastro`.")
                return

            # ===== PASSO 2: EMAIL =====
            await dm.send(f"""
╔═══════════════════════════════╗
║  📧 CADASTRO - PASSO 2/3     ║
╚═══════════════════════════════╝

Ótimo, **{nome}**!

Agora digite seu **e-mail**:

Exemplo: joao@email.com
            """)

            msg_email = await self.bot.wait_for('message', check=check_dm, timeout=120.0)
            email = msg_email.content.strip().lower()

            # Valida o email
            if not self.auth.validar_email(email):
                await dm.send("❌ E-mail inválido!\nExemplo válido: usuario@email.com")
                return

            # Verifica se o email já existe
            if self.auth.verificar_email_existe(email):
                await dm.send("❌ Este e-mail já está cadastrado! Use `!login` para entrar.")
                return

            # ===== PASSO 3: SENHA =====
            await dm.send("""
╔═══════════════════════════════╗
║  🔒 CADASTRO - PASSO 3/3     ║
╚═══════════════════════════════╝

Perfeito! Agora crie uma **senha segura** (mínimo 6 caracteres):
            """)

            msg_senha = await self.bot.wait_for('message', check=check_dm, timeout=120.0)
            senha = msg_senha.content.strip()

            valido, mensagem = self.auth.validar_senha(senha)
            if not valido:
                await dm.send(f"❌ {mensagem}\nTente novamente com `!cadastro`.")
                return

            await dm.send("🔄 Confirme sua senha:")
            msg_confirma = await self.bot.wait_for('message', check=check_dm, timeout=120.0)
            senha_confirma = msg_confirma.content.strip()

            if senha != senha_confirma:
                await dm.send("❌ As senhas não coincidem! Tente novamente com `!cadastro`.")
                return

            # ===== CADASTRAR =====
            sucesso, msg_result = self.auth.cadastrar_usuario(nome, email, senha)

            if sucesso:
                embed = discord.Embed(
                    title="🎉 Cadastro Concluído!",
                    description="Sua conta foi criada com sucesso!",
                    color=discord.Color.green()
                )
                embed.add_field(name="👤 Nome", value=nome, inline=False)
                embed.add_field(name="📧 E-mail", value=email, inline=False)
                embed.add_field(name="✅ Próximo Passo", value="Use `!login` para entrar no sistema!", inline=False)
                embed.set_footer(text="Bem-vindo ao sistema! 🚀")
                await dm.send(embed=embed)
                await ctx.send(f"🎉 {ctx.author.mention} se cadastrou com sucesso!")
            else:
                await dm.send(f"❌ Erro ao cadastrar: {msg_result}")

        except asyncio.TimeoutError:
            await ctx.send(f"⏰ {ctx.author.mention}, tempo esgotado! Use `!cadastro` novamente.")
        except discord.Forbidden:
            await ctx.send(f"❌ {ctx.author.mention}, ative as DMs para continuar o cadastro.")
        except Exception as e:
            await ctx.send(f"⚠️ Erro inesperado: {e}")
            print(f"Erro no cadastro: {e}")


# 🔧 Função obrigatória para registrar o módulo no bot
async def setup(bot):
    await bot.add_cog(Cadastro(bot))

