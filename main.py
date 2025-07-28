#!/usr/bin/env python3
"""
Programa principal do classificador de conversas
"""

import asyncio
import logging
import time
from typing import List, Dict, Any
from database import DatabaseManager
from tag_based_classifier import TagBasedClassifier
from config import BATCH_SIZE, DELAY_BETWEEN_REQUESTS

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('classificador.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class ConversationClassifier:
    def __init__(self):
        self.db = DatabaseManager()
        self.ai = TagBasedClassifier(use_ai=True)
    
    async def process_user(self, user_id: str) -> Dict[str, Any]:
        """Processa um usuário específico"""
        logger.info(f"Processando usuário: {user_id}")
        
        try:
            # Verificar se o usuário já foi classificado (verificação adicional de segurança)
            conn = await self.db.get_connection()
            count = await conn.fetchval(
                "SELECT COUNT(*) FROM classificacoes WHERE user_id = $1",
                user_id
            )
            await conn.close()
            
            if count > 0:
                logger.info(f"Usuário {user_id} já foi classificado anteriormente, pulando...")
                return {
                    "user_id": user_id,
                    "status": "ja_classificado",
                    "classification": "Já processado anteriormente"
                }
            
            # Obter mensagens do usuário
            messages = await self.db.get_last_25_messages(user_id)
            
            if not messages:
                logger.warning(f"Usuário {user_id} não possui mensagens")
                return {
                    "user_id": user_id,
                    "status": "sem_mensagens",
                    "classification": "Sem dados para análise"
                }
            
            # Classificar conversa
            result = await self.ai.classify_conversation(messages)
            
            # Buscar wa_id do usuário
            wa_id = await self.db.get_wa_id_by_customer_id(user_id)
            # Salvar no banco
            await self.db.save_classification(
                user_id=user_id,
                classification=result["classification"],
                confidence=result["confidence"],
                context=result["context"],
                tokens_used=result["tokens_used"],
                processing_time=result["processing_time"],
                wa_id=wa_id,
                classificacao_especifica=result.get("classificacao_especifica", ""),
                sugestao_melhoria=result.get("sugestao_melhoria", "")
            )
            
            logger.info(f"Usuário {user_id} classificado como: {result['classification']}")
            
            return {
                "user_id": user_id,
                "status": "concluido",
                "classification": result["classification"],
                "confidence": result["confidence"]
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar usuário {user_id}: {e}")
            return {
                "user_id": user_id,
                "status": "erro",
                "error": str(e)
            }
    
    async def run(self):
        """Executa o classificador"""
        logger.info("🚀 Iniciando classificador de conversas")
        
        try:
            # Obter usuários não classificados
            unclassified_users = await self.db.get_unclassified_users()
            logger.info(f"📊 Encontrados {len(unclassified_users)} usuários para classificar")
            
            if not unclassified_users:
                logger.info("✅ Todos os usuários já foram classificados!")
                return
            
            # Processar usuários em lotes
            processed_count = 0
            skipped_count = 0
            for i, user_id in enumerate(unclassified_users):
                try:
                    result = await self.process_user(user_id)
                    
                    # Contar apenas usuários realmente processados
                    if result["status"] == "concluido":
                        processed_count += 1
                    elif result["status"] == "ja_classificado":
                        skipped_count += 1
                    
                    # Log de progresso
                    if (i + 1) % BATCH_SIZE == 0:
                        logger.info(f"📈 Processados {i + 1}/{len(unclassified_users)} usuários (novos: {processed_count}, pulados: {skipped_count})")
                    
                    # Delay para evitar rate limiting
                    if i < len(unclassified_users) - 1:  # Não delay no último
                        await asyncio.sleep(DELAY_BETWEEN_REQUESTS)
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao processar usuário {user_id}: {e}")
                    continue
            
            logger.info(f"🎉 Processamento concluído! {processed_count} usuários processados, {skipped_count} usuários pulados (já classificados)")
            
        except Exception as e:
            logger.error(f"❌ Erro geral no processamento: {e}")

async def main():
    """Função principal"""
    classifier = ConversationClassifier()
    await classifier.run()

if __name__ == "__main__":
    asyncio.run(main()) 