# Script para remover planos duplicados do banco

import sqlite3

def limpar_planos_duplicados():
    """Remove planos duplicados, mantendo apenas um de cada"""
    try:
        conn = sqlite3.connect('usuarios.db')
        cursor = conn.cursor()
        
        # Mostra quantos planos existem
        cursor.execute("SELECT COUNT(*) FROM planos")
        total_antes = cursor.fetchone()[0]
        print(f"📊 Total de planos ANTES: {total_antes}")
        
        # Mostra os planos atuais
        cursor.execute("SELECT id, nome, preco FROM planos")
        planos_atuais = cursor.fetchall()
        
        print("\n📋 Planos atuais:")
        for plano in planos_atuais:
            print(f"   ID {plano[0]}: {plano[1]} - R$ {plano[2]:.2f}")
        
        # Mantém apenas o primeiro de cada tipo
        # (os IDs menores - que foram criados primeiro)
        cursor.execute("""
            DELETE FROM planos 
            WHERE id NOT IN (
                SELECT MIN(id) 
                FROM planos 
                GROUP BY nome
            )
        """)
        
        conn.commit()
        
        # Mostra resultado
        cursor.execute("SELECT COUNT(*) FROM planos")
        total_depois = cursor.fetchone()[0]
        
        print(f"\n✅ Planos duplicados removidos!")
        print(f"📊 Total de planos DEPOIS: {total_depois}")
        print(f"🗑️  Removidos: {total_antes - total_depois} planos")
        
        # Mostra planos restantes
        cursor.execute("SELECT id, nome, preco FROM planos")
        planos_finais = cursor.fetchall()
        
        print("\n📋 Planos finais:")
        for plano in planos_finais:
            print(f"   ID {plano[0]}: {plano[1]} - R$ {plano[2]:.2f}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("LIMPEZA DE PLANOS DUPLICADOS")
    print("=" * 60 + "\n")
    
    limpar_planos_duplicados()
    
    print("\n" + "=" * 60)