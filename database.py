import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_path='usuarios.db'):  # Construtor da classe
        self.db_path = db_path  # Guarda o caminho do banco
        self.criar_tabelas()  # Chama a função que cria as tabelas

    def criar_tabelas(self):
        try:
            # Conecta com o banco de dados (cria o arquivo .db se não existir)
            conn = sqlite3.connect(self.db_path)

            # Cursor é como um "ponteiro" que executa comandos no banco
            cursor = conn.cursor()

            # === TABELA DE USUÁRIOS ===
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    senha TEXT NOT NULL,
                    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # === TABELA DE PLANOS ===
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS planos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    descricao TEXT,
                    preco REAL NOT NULL,
                    duracao_dias INTEGER NOT NULL      
                )
            """)

            # === TABELA DE ASSINATURAS ===
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS assinaturas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER NOT NULL,
                    plano_id INTEGER NOT NULL,
                    data_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data_fim TIMESTAMP,
                    status TEXT DEFAULT 'ativa',
                    FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
                    FOREIGN KEY (plano_id) REFERENCES planos (id)                          
                )
            """)

            # Salva as mudanças no banco
            conn.commit()

            # Fecha a conexão
            conn.close()

            print("\u2705 Banco de dados configurado com sucesso!")
        
        except sqlite3.Error as e:
            # Se der algum erro, mostra a mensagem
            print(f"\u274C Erro ao criar tabelas: {e}")

    def inserir_planos_padrao(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Lista com os 3 planos
            planos = [
                ('Básico', 'Acesso a conteúdo básico', 19.90, 30),
                ('Premium', 'Acesso completo + HD', 39.90, 30),
                ('VIP', 'Acesso completo + 4K + downloads', 59.90, 30)
            ]

            # Verifica se já existem planos antes de inserir
            cursor.execute("SELECT COUNT(*) FROM planos")
            total_planos = cursor.fetchone()[0]

            if total_planos == 0:
                # Só insere se não houver nenhum plano
                cursor.executemany("""
                    INSERT INTO planos (nome, descricao, preco, duracao_dias)
                    VALUES (?, ?, ?, ?)
                """, planos)
                print("✅ Planos padrão inseridos!")
            else:
                print(f"ℹ️  Já existem {total_planos} planos no banco. Nada foi inserido.")

            conn.commit()
            conn.close()

            print("\u2705 Planos padrão inseridos!")

        except sqlite3.Error as e:
            print(f"\u274C Erro ao inserir planos: {e}")

# === EXECUTAR QUANDO RODARMOS ESTE ARQUIVO DIRETAMENTE ===
if __name__ == "__main__":
    # Cria o banco e as tabelas
    db = Database()

    # Insere os planos padrão
    db.inserir_planos_padrao()

    print("\n\U0001F389 Banco de dados pronto para uso!")