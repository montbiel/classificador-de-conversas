#!/usr/bin/env python3
"""
Módulo de conexão com banco de dados
"""

import asyncio
import asyncpg
import logging
from typing import List, Dict, Any, Optional
from config import DATABASE_URL, CHAT_HISTORY_USER_ID_COLUMN, CHAT_HISTORY_TIMESTAMP_COLUMN, CHAT_HISTORY_MESSAGE_COLUMN

class DatabaseManager:
    def __init__(self):
        self.database_url = DATABASE_URL
        self.logger = logging.getLogger(__name__)
    
    async def get_connection(self):
        """Obtém conexão com o banco"""
        try:
            # Extrair parâmetros da URL
            url_parts = self.database_url.replace("postgresql+asyncpg://", "").split("@")
            auth_part = url_parts[0].split(":")
            host_port_db = url_parts[1].split("/")
            host_port = host_port_db[0].split(":")
            
            user = auth_part[0]
            password = auth_part[1]
            host = host_port[0]
            port = int(host_port[1])
            database = host_port_db[1]
            
            conn = await asyncpg.connect(
                user=user,
                password=password,
                host=host,
                port=port,
                database=database
            )
            return conn
            
        except Exception as e:
            self.logger.error(f"Erro na conexão: {e}")
            raise
    
    async def get_customers_from_csv(self) -> List[str]:
        """Obtém lista de clientes do arquivo CSV"""
        try:
            import pandas as pd
            df = pd.read_csv("customers.csv")
            return df['customer_id'].astype(str).tolist()
        except Exception as e:
            self.logger.error(f"Erro ao ler customers.csv: {e}")
            return []
    
    async def get_unclassified_users(self) -> List[str]:
        """Obtém usuários que não foram classificados ainda"""
        try:
            conn = await self.get_connection()
            
            # Obter clientes do CSV
            customers = await self.get_customers_from_csv()
            
            # Verificar quais já foram classificados
            unclassified = []
            for customer_id in customers:
                count = await conn.fetchval(
                    "SELECT COUNT(*) FROM classificacoes WHERE user_id = $1",
                    customer_id
                )
                if count == 0:
                    unclassified.append(customer_id)
            
            await conn.close()
            return unclassified
            
        except Exception as e:
            self.logger.error(f"Erro ao obter usuários não classificados: {e}")
            return []
    
    async def get_last_25_messages(self, user_id: str) -> List[Dict[str, Any]]:
        """Obtém as últimas 25 mensagens de um usuário"""
        try:
            conn = await self.get_connection()
            
            # Converter user_id para integer se possível
            try:
                user_id_int = int(user_id)
                param = user_id_int
            except ValueError:
                param = user_id
            
            messages = await conn.fetch(f"""
                SELECT {CHAT_HISTORY_MESSAGE_COLUMN}, {CHAT_HISTORY_TIMESTAMP_COLUMN}, message_type
                FROM chat_history
                WHERE {CHAT_HISTORY_USER_ID_COLUMN} = $1
                AND message_type IN ('USR', 'AIR')
                ORDER BY {CHAT_HISTORY_TIMESTAMP_COLUMN} DESC
                LIMIT 25
            """, param)
            
            await conn.close()
            
            return [
                {
                    "message": msg[CHAT_HISTORY_MESSAGE_COLUMN],
                    "timestamp": msg[CHAT_HISTORY_TIMESTAMP_COLUMN],
                    "role": msg["message_type"]
                }
                for msg in messages
            ]
            
        except Exception as e:
            self.logger.error(f"Erro ao obter mensagens do usuário {user_id}: {e}")
            return []
    
    async def save_classification(self, user_id: str, classification: str, 
                                confidence: float, context: str, 
                                tokens_used: int, processing_time: int, wa_id: str = None,
                                classificacao_especifica: str = None, sugestao_melhoria: str = None):
        """Salva classificação no banco"""
        try:
            conn = await self.get_connection()
            
            await conn.execute("""
                INSERT INTO classificacoes (
                    user_id, classificacao, confianca, contexto,
                    tokens_utilizados, tempo_processamento_ms, status, wa_id, classificacao_especifica, sugestao_melhoria
                ) VALUES ($1, $2, $3, $4, $5, $6, 'concluido', $7, $8, $9)
            """, user_id, classification, confidence, context, 
                 tokens_used, processing_time, wa_id, classificacao_especifica, sugestao_melhoria)
            
            await conn.close()
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar classificação: {e}")
            raise 

    async def get_wa_id_by_customer_id(self, customer_id: str) -> str:
        """Busca o wa_id na tabela customers pelo customer_id"""
        try:
            conn = await self.get_connection()
            wa_id = await conn.fetchval("SELECT wa_id FROM customers WHERE id = $1", int(customer_id))
            await conn.close()
            return wa_id
        except Exception as e:
            self.logger.error(f"Erro ao buscar wa_id para o customer_id {customer_id}: {e}")
            return None 