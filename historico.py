import discord
from discord.ext import commands
import sqlite3
from datetime import datetime
from sessoes import sessoes_ativas


class HistoricoSistema:
    """
    Sistema para gerenciar e visualizar histórico de assinaturas
    Mostra todas as assinaturas do usuário (ativas, canceladas, expiradas)
    """
    
    def __init__(self, db_path='usuarios.db'):
        """
        Inicializa o sistema de histórico
        
        Args:
            db_path: caminho do arquivo do banco de dados
        """
        self.db_path = db_path
    
    def get_historico(self, usuario_id):
        """
        Busca todas as assinaturas de um usuário no banco de dados
        
        Args:
            usuario_id (int): ID do usuário
            
        Returns:
            list: Lista de dicionários com dados das assinaturas
                  Retorna lista vazia se não houver assinaturas
        """
        try:
            # Conecta com o banco
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Busca todas assinaturas do usuário
            # JOIN com tabela planos para pegar informações completas
            cursor.execute("""
                SELECT 
                    a.id,
                    p.nome,
                    p.descricao,
                    p.preco,
                    a.data_inicio,
                    a.data_fim,
                    a.status
                FROM assinaturas a
                INNER JOIN planos p ON a.plano_id = p.id
                WHERE a.usuario_id = ?
                ORDER BY a.data_inicio DESC
            """, (usuario_id,))
            
            resultados = cursor.fetchall()
            conn.close()
            
            # Transforma os resultados em lista de dicionários
            # Isso facilita trabalhar com os dados depois
            historico = []
            for row in resultados:
                historico.append({
                    'id': row[0],
                    'plano_nome': row[1],
                    'plano_descricao': row[2],
                    'preco': row[3],
                    'data_inicio': row[4],
                    'data_fim': row[5],
                    'status': row[6]
                })
            
            return historico
            
        except sqlite3.Error as e:
            print(f"❌ Erro ao buscar histórico: {e}")
            return []
    
    def formatar_historico_embed(self, historico, usuario_nome):
        """
        Formata o histórico como um Embed bonito do Discord
        
        Args:
            historico (list): Lista de assinaturas
            usuario_nome (str): Nome do usuário
            
        Returns:
            discord.Embed: Embed formatado para enviar no Discord
        """
        # Se não houver histórico
        if not historico:
            embed = discord.Embed(
                title="📭 Histórico Vazio",
                description="Você ainda não possui nenhuma assinatura.\n\nUse `!planos` para ver os planos disponíveis!",
                color=discord.Color.light_gray()
            )
            return embed
        
        # Cria o embed principal
        embed = discord.Embed(
            title=f"📜 Histórico de Assinaturas - {usuario_nome}",
            description=f"Total de assinaturas: **{len(historico)}**",
            color=discord.Color.blue()
        )
        
        # Adiciona cada assinatura como um campo
        for i, assinatura in enumerate(historico, 1):
            # Define ícone baseado no status
            if assinatura['status'] == 'ativa':
                icone = "✅"
                cor_status = "**ATIVA**"
            elif assinatura['status'] == 'expirada':
                icone = "⏰"
                cor_status = "EXPIRADA"
            else:  # cancelada
                icone = "❌"
                cor_status = "CANCELADA"
            
            # Formata as datas
            try:
                data_inicio = datetime.strptime(assinatura['data_inicio'], '%Y-%m-%d %H:%M:%S')
                data_fim = datetime.strptime(assinatura['data_fim'], '%Y-%m-%d %H:%M:%S')
                
                inicio_formatado = data_inicio.strftime('%d/%m/%Y')
                fim_formatado = data_fim.strftime('%d/%m/%Y')
            except:
                inicio_formatado = assinatura['data_inicio']
                fim_formatado = assinatura['data_fim']
            
            # Monta o texto do campo
            valor = (
                f"{icone} **Status:** {cor_status}\n"
                f"💰 **Valor:** R$ {assinatura['preco']:.2f}\n"
                f"📅 **Início:** {inicio_formatado}\n"
                f"📅 **Término:** {fim_formatado}\n"
            )
            
            # Adiciona o campo no embed
            embed.add_field(
                name=f"{i}. {assinatura['plano_nome']}",
                value=valor,
                inline=False
            )
        
        # Rodapé com informações úteis
        embed.set_footer(text="Use !minha_assinatura para ver sua assinatura ativa atual")
        
        return embed
    
    def contar_assinaturas_por_status(self, usuario_id):
        """
        Conta quantas assinaturas o usuário tem por status
        
        Args:
            usuario_id (int): ID do usuário
            
        Returns:
            dict: Dicionário com contagem por status
                  Exemplo: {'ativa': 1, 'cancelada': 2, 'expirada': 1, 'total': 4}
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Conta assinaturas agrupadas por status
            cursor.execute("""
                SELECT status, COUNT(*) 
                FROM assinaturas 
                WHERE usuario_id = ?
                GROUP BY status
            """, (usuario_id,))
            
            resultados = cursor.fetchall()
            conn.close()
            
            # Organiza a contagem
            contagem = {
                'ativa': 0,
                'cancelada': 0,
                'expirada': 0,
                'total': 0
            }
            
            for status, qtd in resultados:
                contagem[status] = qtd
                contagem['total'] += qtd
            
            return contagem
            
        except sqlite3.Error as e:
            print(f"❌ Erro ao contar assinaturas: {e}")
            return {'ativa': 0, 'cancelada': 0, 'expirada': 0, 'total': 0}


# ========================================
# COG: Histórico
# ========================================
class Historico(commands.Cog):
    """Cog para gerenciar histórico de assinaturas"""
    
    def __init__(self, bot):
        self.bot = bot
        self.historico_sistema = HistoricoSistema()
        
    
    @commands.command(name='historico', aliases=['history', 'minhas_assinaturas'])
    async def historico(self, ctx):
        """
        Mostra o histórico completo de assinaturas do usuário
        Exibe todas assinaturas: ativas, canceladas e expiradas
        
        Como usar: !historico
        """
        # Verifica se o usuário está logado
        if ctx.author.id not in self.bot.sessoes_ativas:
            await ctx.send("❌ Você precisa fazer login primeiro! Use `!login`")
            return
        
        # Pega dados do usuário logado
        usuario = self.bot.sessoes_ativas[ctx.author.id]
        
        # Envia mensagem de carregamento
        msg_loading = await ctx.send("⏳ Buscando seu histórico de assinaturas...")
        
        try:
            # Busca o histórico no banco
            historico_lista = self.historico_sistema.get_historico(usuario['id'])
            
            # Formata como embed bonito
            embed = self.historico_sistema.formatar_historico_embed(
                historico_lista, 
                usuario['nome']
            )
            
            # Atualiza a mensagem com o embed
            await msg_loading.edit(content=None, embed=embed)
            
            # Se houver assinaturas, mostra estatísticas
            if historico_lista:
                contagem = self.historico_sistema.contar_assinaturas_por_status(usuario['id'])
                
                stats_msg = (
                    f"📊 **Estatísticas de {usuario['nome']}:**\n"
                    f"✅ Ativas: {contagem['ativa']}\n"
                    f"❌ Canceladas: {contagem['cancelada']}\n"
                    f"⏰ Expiradas: {contagem['expirada']}\n"
                    f"📦 Total: {contagem['total']}"
                )
                
                await ctx.send(stats_msg)
        
        except Exception as e:
            await msg_loading.edit(content=f"⚠️ Erro ao buscar histórico: {e}")
            print(f"Erro no comando !historico: {e}")
    
    @commands.command(name='estatisticas', aliases=['stats', 'minhas_stats'])
    async def estatisticas(self, ctx):
        """
        Mostra estatísticas detalhadas das assinaturas do usuário
        
        Como usar: !estatisticas
        """
        # Verifica se está logado
        if ctx.author.id not in self.bot.sessoes_ativas:
            await ctx.send("❌ Você precisa fazer login primeiro! Use `!login`")
            return
        
        usuario = self.bot.sessoes_ativas[ctx.author.id]
        
        try:
            # Busca contagem
            contagem = self.historico_sistema.contar_assinaturas_por_status(usuario['id'])
            
            # Busca histórico completo para calcular gastos
            historico_lista = self.historico_sistema.get_historico(usuario['id'])
            
            # Calcula total gasto
            total_gasto = sum(assinatura['preco'] for assinatura in historico_lista)
            
            # Cria embed de estatísticas
            embed = discord.Embed(
                title=f"📊 Estatísticas - {usuario['nome']}",
                color=discord.Color.gold()
            )
            
            embed.add_field(
                name="📦 Total de Assinaturas",
                value=f"**{contagem['total']}** assinaturas",
                inline=True
            )
            
            embed.add_field(
                name="💰 Total Gasto",
                value=f"R$ **{total_gasto:.2f}**",
                inline=True
            )
            
            embed.add_field(
                name="📈 Média por Assinatura",
                value=f"R$ **{total_gasto / contagem['total']:.2f}**" if contagem['total'] > 0 else "R$ 0.00",
                inline=True
            )
            
            embed.add_field(
                name="✅ Ativas",
                value=f"**{contagem['ativa']}**",
                inline=True
            )
            
            embed.add_field(
                name="❌ Canceladas",
                value=f"**{contagem['cancelada']}**",
                inline=True
            )
            
            embed.add_field(
                name="⏰ Expiradas",
                value=f"**{contagem['expirada']}**",
                inline=True
            )
            
            embed.set_footer(text="Use !historico para ver detalhes completos")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"⚠️ Erro ao buscar estatísticas: {e}")
            print(f"Erro no comando !estatisticas: {e}")


async def setup(bot):
    """
    Função de 'entrada' obrigatória para carregar a Cog.
    Adiciona a classe Historico ao bot.
    """
    await bot.add_cog(Historico(bot))
