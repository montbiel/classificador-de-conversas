#!/usr/bin/env python3
"""
Script de teste para verificar se a lógica está pulando usuários já classificados
"""

import asyncio
import logging
from database import DatabaseManager
from main import ConversationClassifier

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def test_skip_logic():
    """Testa se a lógica está pulando usuários já classificados"""
    logger.info("🧪 Iniciando teste de verificação de pulo de usuários já classificados")
    
    db = DatabaseManager()
    classifier = ConversationClassifier()
    
    try:
        # 1. Verificar usuários não classificados inicialmente
        logger.info("📊 Verificando usuários não classificados...")
        unclassified_initial = await db.get_unclassified_users()
        logger.info(f"Usuários não classificados inicialmente: {len(unclassified_initial)}")
        
        if not unclassified_initial:
            logger.warning("❌ Nenhum usuário não classificado encontrado para teste")
            return
        
        # 2. Pegar alguns usuários para teste
        test_users = unclassified_initial[:3]  # Testar com 3 usuários
        logger.info(f"🔍 Usuários selecionados para teste: {test_users}")
        
        # 3. Processar o primeiro usuário normalmente
        logger.info("🔄 Processando primeiro usuário...")
        result1 = await classifier.process_user(test_users[0])
        logger.info(f"Resultado do primeiro usuário: {result1['status']}")
        
        # 4. Tentar processar o mesmo usuário novamente
        logger.info("🔄 Tentando processar o mesmo usuário novamente...")
        result2 = await classifier.process_user(test_users[0])
        logger.info(f"Resultado da segunda tentativa: {result2['status']}")
        
        # 5. Verificar se foi pulado
        if result2['status'] == 'ja_classificado':
            logger.info("✅ SUCESSO: Usuário foi pulado corretamente!")
        else:
            logger.error("❌ FALHA: Usuário não foi pulado!")
        
        # 6. Verificar usuários não classificados após o teste
        logger.info("📊 Verificando usuários não classificados após teste...")
        unclassified_after = await db.get_unclassified_users()
        logger.info(f"Usuários não classificados após teste: {len(unclassified_after)}")
        
        # 7. Verificar se o usuário testado foi removido da lista
        if test_users[0] not in unclassified_after:
            logger.info("✅ SUCESSO: Usuário foi removido da lista de não classificados!")
        else:
            logger.error("❌ FALHA: Usuário ainda está na lista de não classificados!")
        
        # 8. Testar com múltiplos usuários
        logger.info("🔄 Testando processamento em lote...")
        processed_count = 0
        skipped_count = 0
        
        for user_id in test_users:
            result = await classifier.process_user(user_id)
            if result['status'] == 'concluido':
                processed_count += 1
            elif result['status'] == 'ja_classificado':
                skipped_count += 1
            logger.info(f"Usuário {user_id}: {result['status']}")
        
        logger.info(f"📈 Resultado do teste em lote: {processed_count} processados, {skipped_count} pulados")
        
        # 9. Verificação final
        final_unclassified = await db.get_unclassified_users()
        logger.info(f"📊 Usuários não classificados finais: {len(final_unclassified)}")
        
        # Verificar se os usuários de teste foram removidos
        test_users_remaining = [u for u in test_users if u in final_unclassified]
        if not test_users_remaining:
            logger.info("✅ SUCESSO: Todos os usuários de teste foram processados/removidos!")
        else:
            logger.warning(f"⚠️ Usuários de teste ainda não classificados: {test_users_remaining}")
        
        logger.info("🎉 Teste concluído!")
        
    except Exception as e:
        logger.error(f"❌ Erro durante o teste: {e}")

async def test_database_consistency():
    """Testa a consistência do banco de dados"""
    logger.info("🔍 Testando consistência do banco de dados...")
    
    db = DatabaseManager()
    
    try:
        # Verificar se a tabela classificacoes existe
        conn = await db.get_connection()
        
        # Verificar estrutura da tabela
        columns = await conn.fetch("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'classificacoes'
            ORDER BY ordinal_position
        """)
        
        logger.info("📋 Estrutura da tabela classificacoes:")
        for col in columns:
            logger.info(f"  - {col['column_name']}: {col['data_type']}")
        
        # Verificar índices
        indexes = await conn.fetch("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE tablename = 'classificacoes'
        """)
        
        logger.info("🔗 Índices da tabela classificacoes:")
        for idx in indexes:
            logger.info(f"  - {idx['indexname']}")
        
        # Contar registros
        total_count = await conn.fetchval("SELECT COUNT(*) FROM classificacoes")
        logger.info(f"📊 Total de classificações no banco: {total_count}")
        
        await conn.close()
        
    except Exception as e:
        logger.error(f"❌ Erro ao verificar banco: {e}")

async def main():
    """Função principal do teste"""
    logger.info("🚀 Iniciando testes de verificação...")
    
    await test_database_consistency()
    await test_skip_logic()

if __name__ == "__main__":
    asyncio.run(main()) 