#!/usr/bin/env python3
"""
Script para diagnosticar a estrutura da tabela chat_history existente
"""

import asyncio
import asyncpg
import sys
from typing import Optional

# Configuração do banco
DATABASE_URL = "postgresql+asyncpg://postgres:12345678@127.0.0.1:5432/redfine_core"

async def testar_conexao():
    """Testa a conexão com o banco de dados"""
    try:
        # Extrair parâmetros da URL
        url_parts = DATABASE_URL.replace("postgresql+asyncpg://", "").split("@")
        auth_part = url_parts[0].split(":")
        host_port_db = url_parts[1].split("/")
        host_port = host_port_db[0].split(":")
        
        user = auth_part[0]
        password = auth_part[1]
        host = host_port[0]
        port = int(host_port[1])
        database = host_port_db[1]
        
        print(f"🔄 Testando conexão com o banco...")
        print(f"   Host: {host}")
        print(f"   Porta: {port}")
        print(f"   Database: {database}")
        print(f"   Usuário: {user}")
        
        conn = await asyncpg.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )
        
        print("✅ Conexão estabelecida com sucesso!")
        return conn
        
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return None

async def verificar_tabela_chat_history(conn):
    """Verifica se a tabela chat_history existe e sua estrutura"""
    try:
        print("\n🔍 Verificando tabela chat_history...")
        
        # Verificar se a tabela existe
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'chat_history'
            );
        """)
        
        if not table_exists:
            print("❌ Tabela chat_history não encontrada!")
            return False
        
        print("✅ Tabela chat_history encontrada!")
        
        # Obter estrutura da tabela
        columns = await conn.fetch("""
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'chat_history'
            ORDER BY ordinal_position;
        """)
        
        print("\n📋 Estrutura da tabela chat_history:")
        print("-" * 60)
        print(f"{'Coluna':<20} {'Tipo':<15} {'Null':<8} {'Default'}")
        print("-" * 60)
        
        for col in columns:
            nullable = "YES" if col['is_nullable'] == 'YES' else "NO"
            default = str(col['column_default']) if col['column_default'] else "NULL"
            print(f"{col['column_name']:<20} {col['data_type']:<15} {nullable:<8} {default}")
        
        # Verificar se temos as colunas necessárias
        colunas_necessarias = ['id', 'user_id', 'message', 'timestamp', 'role']
        colunas_existentes = [col['column_name'] for col in columns]
        
        print(f"\n🔍 Verificando colunas necessárias:")
        for coluna in colunas_necessarias:
            if coluna in colunas_existentes:
                print(f"✅ {coluna}")
            else:
                print(f"❌ {coluna} - FALTANDO")
        
        # Contar registros
        count = await conn.fetchval("SELECT COUNT(*) FROM chat_history")
        print(f"\n📊 Total de registros na tabela: {count:,}")
        
        # Verificar se há dados de exemplo
        if count > 0:
            print("\n📝 Exemplo de dados:")
            sample = await conn.fetch("SELECT * FROM chat_history LIMIT 3")
            for i, row in enumerate(sample, 1):
                print(f"  Registro {i}: {dict(row)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar tabela: {e}")
        return False

async def verificar_tabela_classificacoes(conn):
    """Verifica se a tabela classificacoes existe"""
    try:
        print("\n🔍 Verificando tabela classificacoes...")
        
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'classificacoes'
            );
        """)
        
        if table_exists:
            print("✅ Tabela classificacoes encontrada!")
            
            # Verificar estrutura
            columns = await conn.fetch("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'classificacoes'
                ORDER BY ordinal_position;
            """)
            
            print("📋 Estrutura da tabela classificacoes:")
            for col in columns:
                nullable = "YES" if col['is_nullable'] == 'YES' else "NO"
                print(f"  - {col['column_name']} ({col['data_type']}, Null: {nullable})")
            
            # Contar registros
            count = await conn.fetchval("SELECT COUNT(*) FROM classificacoes")
            print(f"📊 Total de classificações: {count:,}")
            
        else:
            print("❌ Tabela classificacoes não encontrada!")
            
        return table_exists
        
    except Exception as e:
        print(f"❌ Erro ao verificar tabela classificacoes: {e}")
        return False

async def main():
    """Função principal"""
    print("🔧 DIAGNÓSTICO DA ESTRUTURA DO BANCO DE DADOS")
    print("=" * 50)
    
    # Testar conexão
    conn = await testar_conexao()
    if not conn:
        print("\n❌ Não foi possível conectar ao banco. Verifique:")
        print("   - Se o PostgreSQL está rodando")
        print("   - Se as credenciais estão corretas")
        print("   - Se o banco 'redfine_core' existe")
        return
    
    try:
        # Verificar tabela chat_history
        chat_history_ok = await verificar_tabela_chat_history(conn)
        
        # Verificar tabela classificacoes
        classificacoes_ok = await verificar_tabela_classificacoes(conn)
        
        print("\n" + "=" * 50)
        print("📋 RESUMO DO DIAGNÓSTICO")
        print("=" * 50)
        
        if chat_history_ok:
            print("✅ Tabela chat_history: OK")
        else:
            print("❌ Tabela chat_history: PROBLEMAS")
            
        if classificacoes_ok:
            print("✅ Tabela classificacoes: OK")
        else:
            print("❌ Tabela classificacoes: NÃO EXISTE")
        
        print("\n🎯 PRÓXIMOS PASSOS:")
        if chat_history_ok and classificacoes_ok:
            print("   - Ambos os componentes estão prontos!")
            print("   - Pode prosseguir para a ETAPA 3")
        elif chat_history_ok and not classificacoes_ok:
            print("   - Criar apenas a tabela classificacoes")
            print("   - Executar: python criar_tabela_classificacoes.py")
        else:
            print("   - Verificar e corrigir a estrutura das tabelas")
            print("   - Executar: python corrigir_tabelas.py")
            
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(main()) 