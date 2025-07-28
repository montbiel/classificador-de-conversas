#!/usr/bin/env python3
"""
Teste rápido de conexão com timeout
"""

import os
import psycopg2
import socket
from dotenv import load_dotenv

def test_connection():
    print("🔍 Teste rápido de conectividade...")
    
    # Carregar variáveis de ambiente
    load_dotenv()
    db_url = os.getenv('DATABASE_URL')
    
    if not db_url:
        print("❌ DATABASE_URL não encontrada no .env")
        return False
    
    print(f"📡 URL do banco: {db_url}")
    
    # Teste 1: Verificar se o host está acessível
    try:
        print("🔗 Testando conectividade com 127.0.0.1:5432...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # 5 segundos de timeout
        result = sock.connect_ex(('127.0.0.1', 5432))
        sock.close()
        
        if result == 0:
            print("✅ Host 127.0.0.1:5432 está acessível")
        else:
            print("❌ Host 127.0.0.1:5432 não está acessível")
            print("   Verifique se o PostgreSQL está rodando")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste de conectividade: {e}")
        return False
    
    # Teste 2: Tentar conexão com timeout
    try:
        print("🔐 Tentando conexão com o banco...")
        
        # Converter URL asyncpg para psycopg2
        if 'asyncpg' in db_url:
            db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
        
        # Conectar com timeout
        conn = psycopg2.connect(db_url, connect_timeout=10)
        print("✅ Conexão estabelecida com sucesso!")
        
        # Teste rápido
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print(f"✅ Query de teste: {result}")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Erro operacional: {e}")
        print("\n🔧 Possíveis causas:")
        print("1. PostgreSQL não está rodando")
        print("2. Banco 'redfine_core' não existe")
        print("3. Credenciais incorretas")
        print("4. Firewall bloqueando conexão")
        return False
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("TESTE RÁPIDO DE CONEXÃO")
    print("=" * 50)
    
    success = test_connection()
    
    if success:
        print("\n🎉 Banco de dados acessível!")
        print("   Execute o script SQL: etapa2_setup_database.sql")
    else:
        print("\n❌ Problemas de conectividade detectados")
    
    print("=" * 50) 