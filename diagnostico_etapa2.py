#!/usr/bin/env python3
"""
Diagnóstico da ETAPA 2 - Problemas na criação das tabelas
"""

import os
from dotenv import load_dotenv

def diagnostico_etapa2():
    print("=" * 60)
    print("🔍 DIAGNÓSTICO - ETAPA 2")
    print("=" * 60)
    
    # 1. Verificar arquivo .env
    print("1️⃣ VERIFICANDO ARQUIVO .ENV:")
    if os.path.exists('.env'):
        print("   ✅ Arquivo .env existe")
        load_dotenv()
        db_url = os.getenv('DATABASE_URL')
        if db_url:
            print(f"   ✅ DATABASE_URL encontrada: {db_url[:50]}...")
        else:
            print("   ❌ DATABASE_URL não encontrada")
    else:
        print("   ❌ Arquivo .env não existe")
    
    print()
    
    # 2. Verificar script SQL
    print("2️⃣ VERIFICANDO SCRIPT SQL:")
    if os.path.exists('etapa2_setup_database.sql'):
        print("   ✅ Script SQL existe")
        with open('etapa2_setup_database.sql', 'r') as f:
            content = f.read()
            if 'CREATE TABLE' in content:
                print("   ✅ Script contém comandos CREATE TABLE")
            else:
                print("   ❌ Script não contém comandos CREATE TABLE")
    else:
        print("   ❌ Script SQL não existe")
    
    print()
    
    # 3. Possíveis problemas
    print("3️⃣ POSSÍVEIS PROBLEMAS:")
    print("   🔴 PostgreSQL não está rodando")
    print("   🔴 Banco 'redfine_core' não existe")
    print("   🔴 Credenciais incorretas (usuário/senha)")
    print("   🔴 Permissões insuficientes para criar tabelas")
    print("   🔴 Erro de sintaxe no script SQL")
    print("   🔴 Cliente PostgreSQL não conectou corretamente")
    
    print()
    
    # 4. Soluções
    print("4️⃣ SOLUÇÕES:")
    print("   ✅ Verifique se o PostgreSQL está rodando")
    print("   ✅ Verifique se o banco 'redfine_core' existe")
    print("   ✅ Teste as credenciais no pgAdmin/DBeaver")
    print("   ✅ Execute o script SQL linha por linha")
    print("   ✅ Verifique se há mensagens de erro")
    
    print()
    
    # 5. Comandos SQL individuais
    print("5️⃣ COMANDOS SQL PARA TESTAR:")
    print("   -- Teste 1: Verificar conexão")
    print("   SELECT version();")
    print()
    print("   -- Teste 2: Verificar se o banco existe")
    print("   SELECT current_database();")
    print()
    print("   -- Teste 3: Criar tabela chat_history")
    print("   CREATE TABLE IF NOT EXISTS chat_history (")
    print("       id SERIAL PRIMARY KEY,")
    print("       user_id INTEGER NOT NULL,")
    print("       message TEXT NOT NULL,")
    print("       timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,")
    print("       message_type VARCHAR(50) DEFAULT 'text'")
    print("   );")
    
    print("=" * 60)

if __name__ == "__main__":
    diagnostico_etapa2() 