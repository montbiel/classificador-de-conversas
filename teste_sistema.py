#!/usr/bin/env python3
"""
Script de teste do sistema de classificação
"""

import asyncio
import logging
from database import DatabaseManager
from tag_based_classifier import TagBasedClassifier

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_database_connection():
    """Testa conexão com banco de dados"""
    print("🔍 Testando conexão com banco de dados...")
    
    try:
        db = DatabaseManager()
        conn = await db.get_connection()
        print("✅ Conexão com banco estabelecida!")
        
        # Testar leitura de clientes do CSV
        customers = await db.get_customers_from_csv()
        print(f"✅ Clientes carregados do CSV: {len(customers)}")
        print(f"   Primeiros 5 clientes: {customers[:5]}")
        
        # Testar busca de usuários não classificados
        unclassified = await db.get_unclassified_users()
        print(f"✅ Usuários não classificados: {len(unclassified)}")
        
        # Testar busca de mensagens de um usuário
        if customers:
            test_user = customers[0]
            messages = await db.get_last_25_messages(test_user)
            print(f"✅ Mensagens do usuário {test_user}: {len(messages)}")
            if messages:
                print(f"   Primeira mensagem: {messages[0]['message'][:50]}...")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão com banco: {e}")
        return False

async def test_ai_classifier():
    """Testa o classificador de IA"""
    print("\n🤖 Testando classificador de IA...")
    
    try:
        ai = TagBasedClassifier(use_ai=True)
        
        # Mensagens de teste
        test_messages = [
            {
                "message": "Olá, preciso de ajuda com meu login",
                "timestamp": "2024-01-15 10:00:00",
                "role": "USR"
            },
            {
                "message": "Não consigo acessar minha conta",
                "timestamp": "2024-01-15 10:01:00", 
                "role": "USR"
            }
        ]
        
        result = await ai.classify_conversation(test_messages)
        print(f"✅ Classificação realizada: {result['classification']}")
        print(f"   Confiança: {result['confidence']}")
        print(f"   Contexto: {result['context']}")
        print(f"   Tokens usados: {result['tokens_used']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no classificador de IA: {e}")
        return False

async def test_full_system():
    """Testa o sistema completo com um usuário real"""
    print("\n🚀 Testando sistema completo...")
    
    try:
        db = DatabaseManager()
        ai = TagBasedClassifier(use_ai=True)
        
        # Obter um usuário não classificado
        unclassified = await db.get_unclassified_users()
        
        if not unclassified:
            print("✅ Todos os usuários já foram classificados!")
            return True
        
        # Testar com o primeiro usuário
        test_user = unclassified[0]
        print(f"🧪 Testando com usuário: {test_user}")
        
        # Obter mensagens
        messages = await db.get_last_25_messages(test_user)
        print(f"   Mensagens encontradas: {len(messages)}")
        
        if not messages:
            print("   ⚠️ Usuário não possui mensagens")
            return True
        
        # Classificar
        result = await ai.classify_conversation(messages)
        print(f"   Classificação: {result['classification']}")
        
        # Salvar no banco
        await db.save_classification(
            user_id=test_user,
            classification=result["classification"],
            confidence=result["confidence"],
            context=result["context"],
            tokens_used=result["tokens_used"],
            processing_time=result["processing_time"]
        )
        print(f"   ✅ Classificação salva no banco!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no sistema completo: {e}")
        return False

async def main():
    """Função principal de teste"""
    print("🧪 TESTE DO SISTEMA DE CLASSIFICAÇÃO")
    print("=" * 50)
    
    # Testar conexão com banco
    db_ok = await test_database_connection()
    
    # Testar classificador de IA
    ai_ok = await test_ai_classifier()
    
    # Testar sistema completo
    system_ok = await test_full_system()
    
    print("\n" + "=" * 50)
    print("📋 RESUMO DOS TESTES")
    print("=" * 50)
    
    if db_ok:
        print("✅ Conexão com banco: OK")
    else:
        print("❌ Conexão com banco: FALHOU")
    
    if ai_ok:
        print("✅ Classificador de IA: OK")
    else:
        print("❌ Classificador de IA: FALHOU")
    
    if system_ok:
        print("✅ Sistema completo: OK")
    else:
        print("❌ Sistema completo: FALHOU")
    
    if db_ok and ai_ok and system_ok:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("🎯 O sistema está pronto para uso!")
    else:
        print("\n⚠️ Alguns testes falharam. Verifique os erros acima.")

if __name__ == "__main__":
    asyncio.run(main()) 