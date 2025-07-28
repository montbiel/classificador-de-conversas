#!/usr/bin/env python3
"""
Monitor de Progresso - ETAPA 2
"""

import os
import time
from datetime import datetime

def check_etapa2_progress():
    """Verifica o progresso da ETAPA 2"""
    
    print("=" * 60)
    print("📊 MONITOR DE PROGRESSO - ETAPA 2")
    print("=" * 60)
    print(f"⏰ Hora: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    # Verificar arquivos criados
    files_to_check = [
        ("etapa2_setup_database.sql", "Script SQL para criar tabelas"),
        ("test_database_connection.py", "Teste de conexão com banco"),
        ("quick_db_test.py", "Teste rápido de conectividade"),
        (".env", "Variáveis de ambiente"),
        ("config/config.yaml", "Configurações do sistema")
    ]
    
    print("📁 ARQUIVOS CRIADOS:")
    for filename, description in files_to_check:
        if os.path.exists(filename):
            print(f"  ✅ {filename} - {description}")
        else:
            print(f"  ❌ {filename} - {description}")
    
    print()
    print("🔧 PRÓXIMOS PASSOS:")
    print("  1. Execute o script SQL no seu cliente PostgreSQL")
    print("  2. Verifique se as tabelas foram criadas")
    print("  3. Teste a conexão com o banco")
    
    print()
    print("📋 CHECKLIST DA ETAPA 2:")
    print("  [ ] Tabela chat_history criada")
    print("  [ ] Tabela conversation_classifications criada")
    print("  [ ] Índices criados")
    print("  [ ] Conexão com banco funcionando")
    print("  [ ] Dados de teste inseridos (opcional)")
    
    print()
    print("💡 DICAS:")
    print("  • Use pgAdmin, DBeaver ou outro cliente PostgreSQL")
    print("  • Conecte ao banco 'redfine_core'")
    print("  • Execute o arquivo 'etapa2_setup_database.sql'")
    print("  • Verifique se não há erros na execução")
    
    print("=" * 60)

def test_connection_simple():
    """Teste simples de conexão"""
    print("\n🔍 TESTE SIMPLES DE CONEXÃO:")
    
    try:
        import psycopg2
        from dotenv import load_dotenv
        
        load_dotenv()
        db_url = os.getenv('DATABASE_URL')
        
        if not db_url:
            print("  ❌ DATABASE_URL não encontrada")
            return False
        
        # Converter URL
        if 'asyncpg' in db_url:
            db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
        
        print(f"  📡 Tentando conectar...")
        
        # Timeout de 5 segundos
        conn = psycopg2.connect(db_url, connect_timeout=5)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        print(f"  ✅ Conexão OK! Resultado: {result}")
        return True
        
    except Exception as e:
        print(f"  ❌ Erro: {str(e)[:100]}...")
        return False

if __name__ == "__main__":
    check_etapa2_progress()
    
    # Perguntar se quer testar conexão
    print("\n🤔 Deseja testar a conexão com o banco? (s/n): ", end="")
    try:
        response = input().lower()
        if response in ['s', 'sim', 'y', 'yes']:
            test_connection_simple()
    except:
        pass
    
    print("\n📝 Para continuar, execute: python monitor_etapa2.py") 