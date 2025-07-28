#!/usr/bin/env python3
"""
Teste das configurações do sistema
"""

try:
    from config import DATABASE_URL, OPENAI_API_KEY, CLASSIFICATION_CATEGORIES
    print("✅ Configurações carregadas com sucesso!")
    print(f"📊 DATABASE_URL: {DATABASE_URL[:50]}...")
    print(f"🔑 OPENAI_API_KEY: {OPENAI_API_KEY[:10] if OPENAI_API_KEY else 'Não configurado'}...")
    print(f"📋 Categorias: {len(CLASSIFICATION_CATEGORIES)} categorias definidas")
    
    # Testar importação dos módulos principais
    from database import DatabaseManager
    from ai_classifier import AIClassifier
    print("✅ Módulos principais importados com sucesso!")
    
except Exception as e:
    print(f"❌ Erro ao carregar configurações: {e}") 