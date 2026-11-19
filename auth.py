import sqlite3
import hashlib

class AuthSystem:
    # Construtor da classe
    def __init__(self, db_path='usuarios.db'):
        """
        Sistema de Autenticação de Usuários

        Esta classe cuida de toda a parte de LOGIN do sistema.
        Ela verifica se o usuário existe e se a senha está correta

        """
        self.db_path = db_path  # Guarda o caminho do banco

    def _hash_senha(self, senha):
        return hashlib.sha256(senha.encode()).hexdigest()
    
    def validar_email(self, email):
        if '@' not in email:
            return False

        # Separa o email pelo @
        # Exemplo: "joao@email.com" vira ["joao", "email.com"]   
        partes = email.split('@')

        # partes[0] = "joao" (antes do @)
        # partes[1] = "email.com" (depois do @)

        # Verifica se tem um ponto (.) na parte depois do @
        if '.' not in partes[1]:
            return False
        
        # Se passou por todas as verificaç~oes, o email é válido!
        return True
    
    def validar_senha(self, senha):
        # Verifica o tamanho da senha
        if len(senha) < 6:
            return False, "Senha deve ter no mínimo 6 caracteres"
        
        # Se passou por todas as verificações, a senha é válida!
        return True, "Senha válida"
    
    def login(self, email, senha):
        try:
            # 1. Conecta com o banco de dados
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 2. Criptografa a senha que o usuário digitou
            # (para comprar com a senha criptografada do banco)
            senha_hash = self._hash_senha(senha)

            # 3. Busca no banco um usuário com esse email E senha
            cursor.execute("""
                SELECT id, nome, email, data_cadastro
                FROM usuarios
                WHERE email = ? AND senha = ?
            """, (email, senha_hash))

            # 4. Pega o resultado da busca
            resultado = cursor.fetchone()

            # 5. Fecha a conexão com o banco
            conn.close()

            # 6. Verifica se encontrou algum usuário
            if resultado:
                # Encontrou! Retorna os dados do usuário
                # (mas SEM retornar a senha, por segurança!) 
                return {
                    'id': resultado[0],
                    'nome': resultado[1],
                    'email': resultado[2],
                    'data_cadastro': resultado[3]
                }
            else:
                # Não encontrou: email ou senha incorretos
                return None

        except sqlite3.Error as e:
            # Se der algum erro no banco de dados, mostra a mensagem
            print(f"\u274C Erro ao fazer login: {e}")
            return None
        

    def cadastrar_usuario_teste(self, nome, email, senha):
        """
        Função AUXILIAR só para testes!
        Cadastra um usuário no banco de dados.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Criptografa a senha antes de salvar
            senha_hash = self._hash_senha(senha)
            
            # Insere o usuário no banco
            cursor.execute("""
                INSERT INTO usuarios (nome, email, senha)
                VALUES (?, ?, ?)
            """, (nome, email, senha_hash))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Usuário '{nome}' cadastrado com sucesso!")
            return True
            
        except sqlite3.IntegrityError:
            # Erro quando o email já existe
            print(f"❌ E-mail '{email}' já está cadastrado!")
            return False
        except sqlite3.Error as e:
            print(f"❌ Erro ao cadastrar: {e}")
            return False
        
    def verificar_email_existe(self, email):
        """
        Verifica se um e-mail já está cadastrado no sistema
        
        Útil para:
        - Evitar cadastros duplicados
        - Validar antes de criar nova conta
        
        Args:
            email (str): E-mail a verificar
            
        Returns:
            bool: True se o email já existe, False caso contrário
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Busca se existe algum usuário com esse email
            cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
            resultado = cursor.fetchone()
            conn.close()
            
            # Se encontrou algo, o email existe
            return resultado is not None
            
        except sqlite3.Error as e:
            print(f"❌ Erro ao verificar e-mail: {e}")
            return False

    def cadastrar_usuario(self, nome, email, senha):
        """
        Cadastra um novo usuário no banco de dados (usado pelo BOT)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Verifica se o e-mail já está cadastrado
            cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
            if cursor.fetchone():
                conn.close()
                return False, "❌ Este e-mail já está cadastrado."

            # Criptografa a senha antes de salvar
            senha_hash = self._hash_senha(senha)

            # Insere o novo usuário
            cursor.execute("""
                INSERT INTO usuarios (nome, email, senha)
                VALUES (?, ?, ?)
            """, (nome, email, senha_hash))
            conn.commit()
            conn.close()

            return True, "✅ Usuário cadastrado com sucesso!"

        except sqlite3.Error as e:
            return False, f"❌ Erro ao cadastrar: {e}"
        

    def excluir_conta(self, usuario_id, senha):
        """
        Exclui permanentemente a conta de um usuário, após verificar a senha.
        Retorna True se deu certo, False se a senha estiver incorreta.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Busca a senha atual do usuário
            cursor.execute("SELECT senha FROM usuarios WHERE id = ?", (usuario_id,))
            row = cursor.fetchone()

            if not row:
                conn.close()
                return False

            senha_hash_salva = row[0]
            senha_hash_tentativa = hashlib.sha256(senha.encode()).hexdigest()

            # Verifica se a senha confere
            if senha_hash_salva != senha_hash_tentativa:
                conn.close()
                return False

            # Exclui assinaturas vinculadas
            cursor.execute("DELETE FROM assinaturas WHERE usuario_id = ?", (usuario_id,))
            # Exclui o usuário
            cursor.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"Erro ao excluir conta: {e}")
            return False