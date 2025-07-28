#!/usr/bin/env python3
"""
Script para criar apenas a tabela classificacoes
Assume que a tabela chat_history já existe
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

async def verificar_tabela_classificacoes(conn):
    """Verifica se a tabela classificacoes já existe"""
    try:
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'classificacoes'
            );
        """)
        
        if table_exists:
            print("✅ Tabela classificacoes já existe!")
            return True
        else:
            print("❌ Tabela classificacoes não encontrada. Será criada.")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar tabela: {e}")
        return False

async def criar_tabela_classificacoes(conn):
    """Cria a tabela classificacoes"""
    try:
        print("\n🔨 Criando tabela classificacoes...")
        
        # SQL para criar a tabela classificacoes
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS classificacoes (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(255) NOT NULL,
            classificacao TEXT NOT NULL,
            confianca DECIMAL(5,4),
            contexto TEXT,
            data_classificacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            modelo_utilizado VARCHAR(100) DEFAULT 'gpt-4o-mini',
            tokens_utilizados INTEGER,
            tempo_processamento_ms INTEGER,
            status VARCHAR(50) DEFAULT 'concluido',
            observacoes TEXT
        );
        """
        
        await conn.execute(create_table_sql)
        print("✅ Tabela classificacoes criada com sucesso!")
        
        # Criar índices para melhor performance
        print("\n🔨 Criando índices...")
        
        indices_sql = [
            "CREATE INDEX IF NOT EXISTS idx_classificacoes_user_id ON classificacoes(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_classificacoes_data ON classificacoes(data_classificacao);",
            "CREATE INDEX IF NOT EXISTS idx_classificacoes_status ON classificacoes(status);"
        ]
        
        for idx_sql in indices_sql:
            await conn.execute(idx_sql)
        
        print("✅ Índices criados com sucesso!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar tabela: {e}")
        return False

async def testar_insercao(conn):
    """Testa inserção de dados na tabela classificacoes"""
    try:
        print("\n🧪 Testando inserção de dados...")
        
        # Inserir um registro de teste
        test_sql = """
        INSERT INTO classificacoes (
            user_id, 
            classificacao, 
            confianca, 
            contexto, 
            modelo_utilizado,
            tokens_utilizados,
            tempo_processamento_ms,
            status
        ) VALUES (
            'test_user_123',
            'Teste de classificação',
            0.95,
            'Contexto de teste para verificar funcionamento',
            'gpt-4o-mini',
            150,
            2500,
            'concluido'
        );
        """
        
        await conn.execute(test_sql)
        print("✅ Inserção de teste realizada com sucesso!")
        
        # Verificar se o registro foi inserido
        count = await conn.fetchval("SELECT COUNT(*) FROM classificacoes WHERE user_id = 'test_user_123'")
        print(f"✅ Registro de teste encontrado: {count} registro(s)")
        
        # Limpar registro de teste
        await conn.execute("DELETE FROM classificacoes WHERE user_id = 'test_user_123'")
        print("✅ Registro de teste removido")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de inserção: {e}")
        return False

async def main():
    """Função principal"""
    print("🔧 CRIAÇÃO DA TABELA CLASSIFICAÇÕES")
    print("=" * 50)
    
    # Testar conexão
    conn = await testar_conexao()
    if not conn:
        print("\n❌ Não foi possível conectar ao banco.")
        return
    
    try:
        # Verificar se a tabela já existe
        tabela_existe = await verificar_tabela_classificacoes(conn)
        
        if tabela_existe:
            print("\n✅ A tabela classificacoes já existe e está pronta para uso!")
            print("🎯 Pode prosseguir para a ETAPA 3")
            return
        
        # Criar a tabela
        sucesso_criacao = await criar_tabela_classificacoes(conn)
        if not sucesso_criacao:
            print("\n❌ Falha na criação da tabela.")
            return
        
        # Testar inserção
        sucesso_teste = await testar_insercao(conn)
        if not sucesso_teste:
            print("\n❌ Falha no teste de inserção.")
            return
        
        print("\n" + "=" * 50)
        print("🎉 ETAPA 2 CONCLUÍDA COM SUCESSO!")
        print("=" * 50)
        print("✅ Tabela classificacoes criada e testada")
        print("✅ Índices criados para otimização")
        print("✅ Teste de inserção realizado com sucesso")
        print("\n🎯 PRÓXIMO PASSO: ETAPA 3 - Implementação dos módulos Python")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(main()) 