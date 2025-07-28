#!/usr/bin/env python3
"""
Teste do classificador baseado em tags
"""

import asyncio
from tag_based_classifier import TagBasedClassifier

async def test_tag_classifier():
    # Testar classificador com IA
    classifier_ai = TagBasedClassifier(use_ai=True)
    
    # Testar classificador apenas com palavras-chave
    classifier_keywords = TagBasedClassifier(use_ai=False)
    
    # Casos de teste específicos
    test_cases = [
        {
            "name": "Problemas financeiros: sem dinheiro",
            "messages": [
                {"message": "Olá, não tenho dinheiro para pagar o curso", "timestamp": "2024-01-15 10:00:00", "role": "user"},
                {"message": "Estou sem grana no momento", "timestamp": "2024-01-15 10:01:00", "role": "user"}
            ]
        },
        {
            "name": "Dúvidas sobre boleto",
            "messages": [
                {"message": "Como faço para gerar o boleto?", "timestamp": "2024-01-15 10:00:00", "role": "user"},
                {"message": "O boleto não chegou no meu email", "timestamp": "2024-01-15 10:01:00", "role": "user"}
            ]
        },
        {
            "name": "Problema: site não abre",
            "messages": [
                {"message": "O site não está abrindo", "timestamp": "2024-01-15 10:00:00", "role": "user"},
                {"message": "Não consigo acessar a página", "timestamp": "2024-01-15 10:01:00", "role": "user"}
            ]
        },
        {
            "name": "Não gostou: conteúdo do curso",
            "messages": [
                {"message": "Não gostei do conteúdo do curso", "timestamp": "2024-01-15 10:00:00", "role": "user"},
                {"message": "O material não é bom", "timestamp": "2024-01-15 10:01:00", "role": "user"}
            ]
        },
        {
            "name": "Insegurança: não se sente preparado",
            "messages": [
                {"message": "Não me sinto preparado para trabalhar", "timestamp": "2024-01-15 10:00:00", "role": "user"},
                {"message": "Não tenho confiança", "timestamp": "2024-01-15 10:01:00", "role": "user"}
            ]
        },
        {
            "name": "Atendimento: não respondeu dúvida",
            "messages": [
                {"message": "Minha dúvida não foi respondida", "timestamp": "2024-01-15 10:00:00", "role": "user"},
                {"message": "Não recebi resposta sobre minha pergunta", "timestamp": "2024-01-15 10:01:00", "role": "user"}
            ]
        }
    ]
    
    print("🧪 TESTE DO CLASSIFICADOR BASEADO EM TAGS")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Teste {i}: {test_case['name']}")
        print(f"   Mensagens: {[msg['message'] for msg in test_case['messages']]}")
        
        # Testar com palavras-chave
        result_keywords = await classifier_keywords.classify_conversation(test_case['messages'])
        print(f"   🔍 Palavras-chave: {result_keywords['classification']} (confiança: {result_keywords['confidence']:.2f})")
        print(f"      Contexto: {result_keywords['context']}")
        
        # Testar com IA (se disponível)
        if classifier_ai.ai_available:
            result_ai = await classifier_ai.classify_conversation(test_case['messages'])
            print(f"   🤖 IA: {result_ai['classification']} (confiança: {result_ai['confidence']:.2f})")
            print(f"      Contexto: {result_ai['context']}")
        else:
            print("   🤖 IA: Não disponível")
    
    print("\n" + "=" * 50)
    print("✅ Teste concluído!")

if __name__ == "__main__":
    asyncio.run(test_tag_classifier()) 