#!/usr/bin/env python3
"""
Script para testar conexão com o banco de dados redfine_core
ETAPA 2 - Configuração do Banco de Dados
"""

import os
import psycopg2
from dotenv import load_dotenv

def test_database_connection():
    """Testa a conexão com o banco de dados"""
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Obter URL do banco
    db_url = os.getenv('DATABASE_URL')
    if db_url and 'asyncpg' in db_url:
        # Converter URL asyncpg para psycopg2
        db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
    
    print(f"🔗 Testando conexão com: {db_url}")
    
    try:
        # Tentar conectar
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Teste 1: Verificar versão
        cursor.execute("SELECT version();")
        version_result = cursor.fetchone()
        if version_result:
            print(f"✅ Conexão estabelecida!")
            print(f"📊 Versão do PostgreSQL: {version_result[0]}")
        else:
            print("⚠️ Não foi possível obter a versão do PostgreSQL")
        
        # Teste 2: Verificar se as tabelas existem
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('chat_history', 'conversation_classifications')
        """)
        existing_tables = [row[0] for row in cursor.fetchall()]
        print(f"📋 Tabelas existentes: {existing_tables}")
        
        # Teste 3: Verificar dados na chat_history
        cursor.execute("SELECT COUNT(*) FROM chat_history")
        message_result = cursor.fetchone()
        message_count = message_result[0] if message_result else 0
        print(f"💬 Total de mensagens na chat_history: {message_count}")
        
        if message_count > 0:
            cursor.execute("SELECT COUNT(DISTINCT customer_id) FROM chat_history")
            user_result = cursor.fetchone()
            user_count = user_result[0] if user_result else 0
            print(f"👥 Usuários únicos com mensagens: {user_count}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Teste de conexão concluído com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        print("\n🔧 Possíveis soluções:")
        print("1. Verifique se o PostgreSQL está rodando")
        print("2. Verifique se o banco 'redfine_core' existe")
        print("3. Verifique as credenciais no arquivo .env")
        print("4. Verifique se o psycopg2-binary está instalado")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("ETAPA 2: Teste de Conexão com Banco de Dados")
    print("=" * 60)
    
    success = test_database_connection()
    
    if success:
        print("\n✅ Próximo passo: Execute o script SQL 'etapa2_setup_database.sql'")
        print("   no seu cliente PostgreSQL (pgAdmin, DBeaver, etc.)")
    else:
        print("\n❌ Corrija os problemas de conexão antes de continuar")
    
    print("=" * 60) 