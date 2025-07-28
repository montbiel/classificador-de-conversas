#!/usr/bin/env python3
"""
Módulo de classificação usando OpenAI
"""

import asyncio
import time
import logging
from typing import Dict, Any, List
import openai
from config import OPENAI_API_KEY, OPENAI_MODEL, CLASSIFICATION_PROMPT, CLASSIFICATION_CATEGORIES

class AIClassifier:
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.logger = logging.getLogger(__name__)
    
    def format_messages_for_analysis(self, messages: List[Dict[str, Any]]) -> str:
        """Formata mensagens para análise"""
        if not messages:
            return "Nenhuma mensagem encontrada."
        
        formatted = []
        for msg in messages:
            # Tratar timestamp que pode ser string ou datetime
            timestamp = msg["timestamp"]
            if hasattr(timestamp, 'strftime'):
                timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            else:
                timestamp_str = str(timestamp)
            
            role = msg.get("role", "user")
            message = msg["message"]
            formatted.append(f"[{timestamp_str}] {role}: {message}")
        
        return "\n".join(formatted)
    
    async def classify_conversation(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Classifica uma conversa usando OpenAI"""
        try:
            start_time = time.time()
            
            # Formatar mensagens
            formatted_messages = self.format_messages_for_analysis(messages)
            
            if not formatted_messages.strip():
                return {
                    "classification": "Sem mensagens suficientes",
                    "confidence": 0.0,
                    "context": "Nenhuma mensagem encontrada para análise",
                    "tokens_used": 0,
                    "processing_time": 0
                }
            
            # Preparar prompt
            categories_text = "\n".join(CLASSIFICATION_CATEGORIES)
            prompt = CLASSIFICATION_PROMPT.format(categories_text, formatted_messages)
            
            # Fazer chamada para OpenAI
            response = await self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Você é um classificador especializado em conversas de atendimento ao cliente."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            # Calcular tempo de processamento
            processing_time = int((time.time() - start_time) * 1000)
            
            # Processar resposta
            content = response.choices[0].message.content.strip()
            tokens_used = response.usage.total_tokens
            
            # Separar classificação e contexto
            if "|" in content:
                classification, context = content.split("|", 1)
                classification = classification.strip()
                context = context.strip()
            else:
                classification = content
                context = "Classificação automática"
            
            return {
                "classification": classification,
                "confidence": 0.9,  # Confiança padrão
                "context": context,
                "tokens_used": tokens_used,
                "processing_time": processing_time
            }
            
        except Exception as e:
            self.logger.error(f"Erro na classificação: {e}")
            return {
                "classification": "Erro na classificação",
                "confidence": 0.0,
                "context": f"Erro: {str(e)}",
                "tokens_used": 0,
                "processing_time": 0
            } 