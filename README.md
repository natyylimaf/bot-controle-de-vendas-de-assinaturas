<div align="center">

# 🎬 Bot de Controle de Vendas de Assinaturas

**Sistema de gestão de assinaturas de streaming de filmes, direto no Discord.**

![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![discord.py](https://img.shields.io/badge/discord.py-2.3.2-5865F2?style=for-the-badge&logo=discord&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
</div>

---

## 📖 Sobre o projeto

Projeto desenvolvido para a disciplina de **Engenharia de Software** do curso de **Análise e Desenvolvimento de Sistemas**. Trata-se de um bot de Discord que permite cadastrar usuários, contratar planos de streaming de filmes, simular pagamentos e acompanhar o ciclo de vida das assinaturas (ativa, expirada ou cancelada), com notificações automáticas.

> ⚠️ **Aviso:** o sistema de pagamento é **simulado** e não processa transações reais.

## ✨ Funcionalidades

### 👤 Gestão de usuários
- Cadastro com nome, e-mail e senha
- Validação de formato de e-mail e de senha (mínimo de 6 caracteres)
- Senha criptografada com **SHA-256**
- Verificação de e-mail duplicado
- Login/logout com sessões ativas no Discord
- Visualização de perfil e data de cadastro
- Exclusão permanente de conta, com confirmação

### 🎞️ Planos de assinatura

| Plano | Descrição | Preço | Duração |
|-------|-----------|-------|---------|
| **Básico** | Catálogo de filmes clássicos em qualidade SD | R$ 19,90 | 30 dias |
| **Premium** | Catálogo completo em qualidade HD | R$ 39,90 | 30 dias |
| **VIP** | Catálogo completo em 4K + lançamentos exclusivos | R$ 59,90 | 30 dias |

### 💳 Pagamentos (simulado)
- Pagamento simulado via cartão de teste, com o fluxo feito por mensagem privada (DM)
- Cartão de teste aprovado: `4242 4242 4242 4242` | recusado: `4000 0000 0000 0002`
- A assinatura só é criada após a aprovação do pagamento

### 📋 Gestão de assinaturas
- Consulta da assinatura atual: plano, datas de início e término, status e dias restantes
- Histórico completo (ativas, expiradas e canceladas)
- Cancelamento e mudança de plano (upgrade/downgrade)

### 🔔 Notificações
- Alerta automático por DM quando a assinatura expira (1 dia antes e no dia)
- Mensagens de confirmação de pagamento, cancelamento e mudança de plano

## 🤖 Comandos

O prefixo do bot é `!`.

| Comando | O que faz |
|---------|-----------|
| `!ajuda` | Lista os comandos disponíveis |
| `!cadastro` | Cria uma nova conta |
| `!login` / `!logout` | Entra e sai da conta |
| `!perfil` | Mostra seus dados e a data de cadastro |
| `!planos` | Lista os planos e permite contratar |
| `!minha_assinatura` | Mostra a assinatura atual |
| `!mudar_plano` | Faz upgrade ou downgrade de plano |
| `!cancelar_assinatura` | Cancela a assinatura ativa |
| `!historico` | Mostra o histórico de assinaturas |
| `!estatisticas` | Mostra estatísticas da sua conta |
| `!excluir_conta` | Exclui a conta permanentemente |

## 🏗️ Arquitetura

- **Linguagem:** Python 3.13+
- **Bot:** discord.py 2.3.2, organizado em *cogs* (um módulo por comando)
- **Banco de dados:** SQLite (`usuarios.db`, criado automaticamente na primeira execução)
- **Criptografia:** `hashlib` (SHA-256)

```
bot-controle-de-vendas-de-assinaturas/
├── main.py                    # Inicializa o bot e carrega todos os módulos (cogs)
├── database.py                # Acesso ao SQLite e criação das tabelas
├── auth.py                    # Autenticação: cadastro, login e hash de senha (SHA-256)
├── sessoes.py                 # Controle das sessões ativas dos usuários
│
├── ajuda.py                   # Comando !ajuda
├── cadastro.py                # Comando !cadastro
├── login.py                   # Comando !login
├── logout.py                  # Comando !logout
├── perfil.py                  # Comando !perfil
├── excluir_conta.py           # Comando !excluir_conta
│
├── planos.py                  # Comando !planos (listagem e contratação)
├── pagamentos.py              # Pagamento simulado via cartão (fluxo na DM)
├── minha_assinatura.py        # Comando !minha_assinatura
├── mudar_plano.py             # Comando !mudar_plano
├── cancelar_assinatura.py     # Comando !cancelar_assinatura
├── historico.py               # Comandos !historico e !estatisticas
├── verificar_assinaturas.py   # Tarefa automática (a cada 1h): expiração e notificações
├── limpar_planos.py           # Script utilitário: remove planos duplicados do banco
│
├── requirements.txt           # Dependências do projeto
├── .env.example               # Modelo do arquivo de configuração (token)
├── .gitignore                 # Arquivos ignorados pelo Git
└── README.md
```

> Arquivos locais, que não vão para o GitHub: `.env` (token real), `usuarios.db` (banco, criado automaticamente), `.venv/`, `__pycache__/` e `.vscode/`.

## 🔧 Criando o bot no Discord

### 1. Criar o aplicativo e pegar o token
1. Acesse o [Portal do Desenvolvedor do Discord](https://discord.com/developers/applications) e faça login.
2. Clique em **Novo aplicativo**, dê um nome (ex.: *Bot de Assinaturas*) e confirme.
3. No menu lateral, abra **Bot**.
4. Clique em **Redefinir token** (ou *Reset Token*), confirme e **copie o token**. Ele só aparece uma vez. Guarde-o para o arquivo `.env` e **nunca publique esse token**.
5. Ainda em **Bot**, role até **Intents de Gateway Privilegiadas** e ative as três opções, principalmente **Intent de Conteúdo de Mensagem**. Clique em **Salvar alterações**.

### 2. Criar um servidor de teste
No Discord, clique no **+** da barra lateral → **Criar o meu** → **Para mim e meus amigos** e dê um nome ao servidor.

### 3. Adicionar o bot ao servidor
1. No portal, vá em **OAuth2** → **Gerador de URL**.
2. Em **Escopos**, marque `bot`.
3. Em **Permissões do bot**, marque: *Enviar mensagens*, *Ler histórico de mensagens*, *Incorporar links*, *Adicionar reações* e *Gerenciar mensagens*.
4. Copie a **URL gerada** no final da página, abra no navegador, escolha o servidor de teste e clique em **Autorizar**.

O bot aparecerá na lista de membros do servidor (offline, até você executá-lo).

## 🚀 Como executar

**Pré-requisitos:** Python 3.13+ e um bot criado e adicionado ao seu servidor (veja a seção acima).

```bash
# 1. Clone o repositório
git clone https://github.com/natyylimaf/bot-controle-de-vendas-de-assinaturas.git
cd bot-controle-de-vendas-de-assinaturas

# 2. Crie e ative o ambiente virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/macOS

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure o token
copy .env.example .env        # Windows (use "cp" no Linux/macOS)
# edite o .env e coloque o token do seu bot em DISCORD_TOKEN

# 5. Execute
python main.py
```

Quando aparecer `✅ Bot conectado como ...`, o bot está online. Vá ao servidor e digite `!ajuda`.

Para **desligar**, volte ao terminal e pressione `Ctrl + C`: o bot fica offline.

## 👥 Equipe

- Davi Pitangui
- Gabryel Modesto
- Kaynan Barbosa
- Murilo Caldeira
- Nathália Lima


## 📄 Licença

Projeto acadêmico, desenvolvido apenas para fins educacionais.
