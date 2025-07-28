#!/usr/bin/env python3
"""
Classificador baseado em tags específicas
"""

import re
import time
import logging
from typing import Dict, Any, List, Tuple
from config import CLASSIFICATION_TAGS, TAG_KEYWORDS, CLASSIFICATION_PROMPT, OPENAI_API_KEY, OPENAI_MODEL

class TagBasedClassifier:
    def __init__(self, use_ai=True):
        self.use_ai = use_ai
        self.logger = logging.getLogger(__name__)
        
        if use_ai and OPENAI_API_KEY and OPENAI_API_KEY != 'sua_chave_api_aqui':
            try:
                import openai
                self.client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
                self.ai_available = True
            except Exception as e:
                self.logger.warning(f"IA não disponível: {e}")
                self.ai_available = False
        else:
            self.ai_available = False
    
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
    
    async def generate_improvement_suggestions(self, messages: List[Dict[str, Any]], classification: str) -> str:
        """Gera sugestões livres e específicas usando IA para melhorar o prompt"""
        if not messages:
            return "Nenhuma mensagem para análise"
        
        try:
            # Formatar mensagens para análise
            formatted_messages = self.format_messages_for_analysis(messages)
            
            # Prompt específico para gerar sugestões de melhoria
            improvement_prompt = f"""
Você é um especialista em análise de atendimento ao cliente. Analise a conversa abaixo e forneça até 5 sugestões específicas e acionáveis para melhorar o prompt de uma IA de atendimento.

CONTEXTO:
- Classificação da conversa: {classification}
- Total de mensagens: {len(messages)}
- Mensagens do cliente: {len([m for m in messages if m.get('role') == 'USR'])}
- Mensagens da IA: {len([m for m in messages if m.get('role') == 'AIR'])}

CONVERSA:
{formatted_messages}

INSTRUÇÕES:
1. Analise como a IA poderia ter melhorado o atendimento
2. Foque em sugestões específicas que podem ser implementadas no prompt da IA
3. Considere: clareza, completude, proatividade, personalização, resolução
4. Seja específico sobre o que deveria ser incluído ou melhorado
5. Limite a 5 sugestões mais importantes
6. Use formato de tópicos com "•" no início

FORMATO DE RESPOSTA:
• [Sugestão específica e acionável]

Se a conversa estiver bem conduzida, responda apenas: "Conversa bem conduzida - manter padrão atual"
"""
            
            # Fazer chamada para OpenAI
            response = await self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Você é um especialista em análise de atendimento ao cliente e melhoria de prompts de IA."},
                    {"role": "user", "content": improvement_prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            # Processar resposta
            content = response.choices[0].message.content.strip()
            
            # Log para debug
            self.logger.info(f"Sugestões de melhoria geradas: {content}")
            
            return content
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar sugestões de melhoria: {e}")
            return "Erro ao gerar sugestões de melhoria"
    
    def classify_by_keywords(self, messages: List[Dict[str, Any]]) -> Tuple[str, float, str]:
        """Classifica usando palavras-chave"""
        if not messages:
            return "Outros", 0.0, "Nenhuma mensagem encontrada"
        
        # Juntar todas as mensagens em um texto
        all_text = " ".join([msg["message"].lower() for msg in messages])
        
        # Contar ocorrências de cada tag
        tag_scores = {}
        
        for tag, keywords in TAG_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                # Buscar palavra-chave no texto
                if keyword.lower() in all_text:
                    score += 1
            
            if score > 0:
                tag_scores[tag] = score
        
        # Se encontrou alguma tag, retornar a com maior score
        if tag_scores:
            best_tag = max(tag_scores, key=tag_scores.get)
            confidence = min(tag_scores[best_tag] / 3.0, 0.9)  # Normalizar confiança
            context = f"Encontradas {tag_scores[best_tag]} palavras-chave relacionadas a '{best_tag}'"
            return best_tag, confidence, context
        
        # Se não encontrou nenhuma tag específica
        return "Outros", 0.5, "Nenhuma palavra-chave específica encontrada"
    
    async def classify_with_ai(self, messages: List[Dict[str, Any]]) -> Tuple[str, float, str]:
        """Classifica usando IA"""
        try:
            # Formatar mensagens
            formatted_messages = self.format_messages_for_analysis(messages)
            
            if not formatted_messages.strip():
                return "Outros", 0.0, "Nenhuma mensagem encontrada para análise"
            
            # Preparar prompt
            tags_text = "\n".join([f"- {tag}" for tag in CLASSIFICATION_TAGS])
            prompt = CLASSIFICATION_PROMPT.format(tags_text, formatted_messages)
            
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
            
            # Processar resposta
            content = response.choices[0].message.content.strip()
            
            # Log para debug
            self.logger.info(f"Resposta da IA: {content}")
            
            # Separar classificação, contexto e classificação específica
            if "|" in content:
                parts = content.split("|")
                if len(parts) >= 3:
                    classification = parts[0].strip().lstrip("- ").strip()  # Remove hífen e espaços
                    context = parts[1].strip()
                    classificacao_especifica = parts[2].strip()
                elif len(parts) == 2:
                    classification = parts[0].strip().lstrip("- ").strip()
                    context = parts[1].strip()
                    classificacao_especifica = context  # Usar contexto como específica
                else:
                    classification = parts[0].strip().lstrip("- ").strip()
                    context = "Classificação automática"
                    classificacao_especifica = "Detalhes não fornecidos"
            else:
                # Se não tem pipe, tentar extrair a classificação da resposta
                classification = content.lstrip("- ").strip()
                context = "Classificação automática"
                classificacao_especifica = "Detalhes não fornecidos"
                
                # Tentar encontrar uma tag válida na resposta
                for tag in CLASSIFICATION_TAGS:
                    if tag.lower() in content.lower():
                        classification = tag
                        context = f"Tag encontrada na resposta: {content}"
                        classificacao_especifica = "Classificação extraída da resposta"
                        break
            
            # Verificar se a classificação é uma tag válida (comparação mais flexível)
            classification_clean = classification.strip()
            tag_found = False
            
            for tag in CLASSIFICATION_TAGS:
                if tag.lower() == classification_clean.lower():
                    classification = tag  # Usar a tag exata do sistema
                    tag_found = True
                    break
            
            if not tag_found:
                # Tentar encontrar correspondência parcial
                for tag in CLASSIFICATION_TAGS:
                    if classification_clean.lower() in tag.lower() or tag.lower() in classification_clean.lower():
                        classification = tag
                        context = f"Tag '{classification_clean}' mapeada para '{tag}'"
                        tag_found = True
                        break
            
            if not tag_found:
                classification = "Outros"
                context = f"Tag '{classification_clean}' não reconhecida, classificada como 'Outros'"
                classificacao_especifica = "Tag não reconhecida pelo sistema"
            
            return classification, 0.9, context, classificacao_especifica
            
        except Exception as e:
            self.logger.error(f"Erro na classificação com IA: {e}")
            return "Outros", 0.0, f"Erro na classificação: {str(e)}"
    
    async def classify_conversation(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Classifica uma conversa usando tags"""
        try:
            start_time = time.time()
            
            # Tentar classificação com IA primeiro (se disponível)
            if self.use_ai and self.ai_available:
                try:
                    result = await self.classify_with_ai(messages)
                    if len(result) == 4:
                        classification, confidence, context, classificacao_especifica = result
                    else:
                        classification, confidence, context = result
                        classificacao_especifica = context
                    tokens_used = 200  # Estimativa
                except Exception as e:
                    self.logger.warning(f"Falha na IA, usando palavras-chave: {e}")
                    classification, confidence, context = self.classify_by_keywords(messages)
                    classificacao_especifica = context
                    tokens_used = 0
            else:
                # Usar classificação por palavras-chave
                classification, confidence, context = self.classify_by_keywords(messages)
                classificacao_especifica = context
                tokens_used = 0
            
            # Calcular tempo de processamento
            processing_time = int((time.time() - start_time) * 1000)
            
            # Gerar sugestões de melhoria
            sugestao_melhoria = await self.generate_improvement_suggestions(messages, classification)
            
            return {
                "classification": classification,
                "confidence": confidence,
                "context": context,
                "classificacao_especifica": classificacao_especifica,
                "sugestao_melhoria": sugestao_melhoria,
                "tokens_used": tokens_used,
                "processing_time": processing_time
            }
            
        except Exception as e:
            self.logger.error(f"Erro na classificação: {e}")
            return {
                "classification": "Outros",
                "confidence": 0.0,
                "context": f"Erro: {str(e)}",
                "tokens_used": 0,
                "processing_time": 0
            } 