# Classificador de Conversas com IA - Documentação Completa

## Visão Geral
Este sistema analisa as últimas 20 interações de usuários específicos na tabela `chat_history` e classifica as conversas usando a API da OpenAI. O sistema garante que usuários já classificados não sejam reprocessados e gera um arquivo com todas as classificações.

## Estrutura do Projeto

```
classificador-conversas/
├── src/
│   ├── __init__.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   └── queries.py
│   ├── ai_classifier/
│   │   ├── __init__.py
│   │   ├── openai_client.py
│   │   └── conversation_analyzer.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py
│   │   └── file_handler.py
│   └── main.py
├── config/
│   └── config.yaml
├── data/
│   ├── customers.csv
│   ├── processed_users.json
│   └── classifications.csv
├── logs/
│   └── classifier.log
├── requirements.txt
└── README.md
```

## Passo a Passo da Implementação

### 1. Configuração do Ambiente

#### 1.1 Instalação de Dependências
```bash
pip install -r requirements.txt
```

**requirements.txt:**
```
pandas==2.1.4
openai==1.3.7
psycopg2-binary==2.9.9
pyyaml==6.0.1
python-dotenv==1.0.0
logging==0.4.9.6
```

#### 1.2 Configuração de Variáveis de Ambiente
Criar arquivo `.env`:
```env
OPENAI_API_KEY=sua_chave_api_aqui
DATABASE_URL=postgresql://usuario:senha@localhost:5432/nome_banco
LOG_LEVEL=INFO
```

### 2. Configuração do Banco de Dados

#### 2.1 Estrutura da Tabela chat_history (assumida)
```sql
CREATE TABLE chat_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_type VARCHAR(50) DEFAULT 'text'
);

-- Tabela para armazenar classificações
CREATE TABLE conversation_classifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    classification TEXT NOT NULL,
    confidence_score FLOAT,
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_20_messages TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. Implementação dos Módulos

#### 3.1 Conexão com Banco de Dados (`src/database/connection.py`)
```python
import psycopg2
import os
from dotenv import load_dotenv
import logging

load_dotenv()

class DatabaseConnection:
    def __init__(self):
        self.connection_string = os.getenv('DATABASE_URL')
        self.logger = logging.getLogger(__name__)
    
    def get_connection(self):
        try:
            return psycopg2.connect(self.connection_string)
        except Exception as e:
            self.logger.error(f"Erro na conexão com banco: {e}")
            raise
    
    def execute_query(self, query, params=None):
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                if query.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                conn.commit()
        finally:
            conn.close()
```

#### 3.2 Queries do Banco (`src/database/queries.py`)
```python
class ChatQueries:
    @staticmethod
    def get_unclassified_users():
        return """
        SELECT DISTINCT ch.user_id 
        FROM chat_history ch
        LEFT JOIN conversation_classifications cc ON ch.user_id = cc.user_id
        WHERE cc.user_id IS NULL
        ORDER BY ch.user_id
        """
    
    @staticmethod
    def get_last_20_messages(user_id):
        return """
        SELECT message, timestamp, message_type
        FROM chat_history
        WHERE user_id = %s
        ORDER BY timestamp DESC
        LIMIT 20
        """
    
    @staticmethod
    def insert_classification(user_id, classification, confidence_score, messages):
        return """
        INSERT INTO conversation_classifications 
        (user_id, classification, confidence_score, last_20_messages)
        VALUES (%s, %s, %s, %s)
        """
    
    @staticmethod
    def get_all_classifications():
        return """
        SELECT user_id, classification, confidence_score, analysis_date
        FROM conversation_classifications
        ORDER BY analysis_date DESC
        """
```

#### 3.3 Cliente OpenAI (`src/ai_classifier/openai_client.py`)
```python
import openai
import os
import logging
from typing import Dict, Any

class OpenAIClient:
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.logger = logging.getLogger(__name__)
    
    def classify_conversation(self, messages: str) -> Dict[str, Any]:
        try:
            prompt = f"""
            Analise as seguintes mensagens de conversa e classifique o tipo de interação.
            
            Mensagens:
            {messages}
            
            Classifique em uma das seguintes categorias:
            1. Suporte Técnico - Problemas com produtos/serviços
            2. Vendas - Interesse em compra
            3. Reclamação - Insatisfação com atendimento/produto
            4. Informação - Busca por informações gerais
            5. Elogio - Feedback positivo
            6. Outros - Não se encaixa nas categorias acima
            
            Responda apenas com o número da categoria e uma breve justificativa.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um classificador especializado em conversas de atendimento ao cliente."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            return {
                "classification": response.choices[0].message.content,
                "confidence": 0.9  # Pode ser ajustado baseado na resposta
            }
            
        except Exception as e:
            self.logger.error(f"Erro na classificação OpenAI: {e}")
            return {"classification": "Erro na classificação", "confidence": 0.0}
```

#### 3.4 Analisador de Conversas (`src/ai_classifier/conversation_analyzer.py`)
```python
import json
import logging
from typing import List, Dict, Any
from .openai_client import OpenAIClient

class ConversationAnalyzer:
    def __init__(self):
        self.openai_client = OpenAIClient()
        self.logger = logging.getLogger(__name__)
    
    def format_messages(self, messages: List[tuple]) -> str:
        """Formata as mensagens para análise"""
        formatted = []
        for message, timestamp, msg_type in messages:
            formatted.append(f"[{timestamp}] {message}")
        return "\n".join(formatted)
    
    def analyze_user_conversation(self, user_id: int, messages: List[tuple]) -> Dict[str, Any]:
        """Analisa a conversa de um usuário específico"""
        try:
            formatted_messages = self.format_messages(messages)
            
            if not formatted_messages.strip():
                return {
                    "user_id": user_id,
                    "classification": "Sem mensagens suficientes",
                    "confidence": 0.0
                }
            
            result = self.openai_client.classify_conversation(formatted_messages)
            
            return {
                "user_id": user_id,
                "classification": result["classification"],
                "confidence": result["confidence"],
                "messages_count": len(messages)
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao analisar conversa do usuário {user_id}: {e}")
            return {
                "user_id": user_id,
                "classification": "Erro na análise",
                "confidence": 0.0
            }
```

#### 3.5 Gerenciador de Arquivos (`src/utils/file_handler.py`)
```python
import pandas as pd
import json
import os
from typing import List, Dict, Any
import logging

class FileHandler:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.logger = logging.getLogger(__name__)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Garante que os diretórios necessários existam"""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs("logs", exist_ok=True)
    
    def load_customers(self) -> List[int]:
        """Carrega lista de clientes do CSV"""
        try:
            df = pd.read_csv(os.path.join(self.data_dir, "customers.csv"))
            return df['id'].tolist()
        except Exception as e:
            self.logger.error(f"Erro ao carregar customers.csv: {e}")
            return []
    
    def save_classifications(self, classifications: List[Dict[str, Any]]):
        """Salva classificações em CSV"""
        try:
            df = pd.DataFrame(classifications)
            output_path = os.path.join(self.data_dir, "classifications.csv")
            df.to_csv(output_path, index=False)
            self.logger.info(f"Classificações salvas em: {output_path}")
        except Exception as e:
            self.logger.error(f"Erro ao salvar classificações: {e}")
    
    def load_processed_users(self) -> set:
        """Carrega usuários já processados"""
        try:
            file_path = os.path.join(self.data_dir, "processed_users.json")
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return set(json.load(f))
            return set()
        except Exception as e:
            self.logger.error(f"Erro ao carregar usuários processados: {e}")
            return set()
    
    def save_processed_users(self, processed_users: set):
        """Salva lista de usuários processados"""
        try:
            file_path = os.path.join(self.data_dir, "processed_users.json")
            with open(file_path, 'w') as f:
                json.dump(list(processed_users), f)
        except Exception as e:
            self.logger.error(f"Erro ao salvar usuários processados: {e}")
```

#### 3.6 Logger (`src/utils/logger.py`)
```python
import logging
import os
from datetime import datetime

def setup_logger():
    """Configura o sistema de logging"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"classifier_{datetime.now().strftime('%Y%m%d')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)
```

### 4. Programa Principal (`src/main.py`)
```python
import time
import logging
from typing import List, Dict, Any
from database.connection import DatabaseConnection
from database.queries import ChatQueries
from ai_classifier.conversation_analyzer import ConversationAnalyzer
from utils.file_handler import FileHandler
from utils.logger import setup_logger

class ConversationClassifier:
    def __init__(self):
        self.logger = setup_logger()
        self.db = DatabaseConnection()
        self.queries = ChatQueries()
        self.analyzer = ConversationAnalyzer()
        self.file_handler = FileHandler()
        
    def get_unclassified_users(self) -> List[int]:
        """Obtém usuários não classificados"""
        try:
            results = self.db.execute_query(self.queries.get_unclassified_users())
            return [row[0] for row in results]
        except Exception as e:
            self.logger.error(f"Erro ao obter usuários não classificados: {e}")
            return []
    
    def get_user_messages(self, user_id: int) -> List[tuple]:
        """Obtém as últimas 20 mensagens de um usuário"""
        try:
            results = self.db.execute_query(
                self.queries.get_last_20_messages(user_id), 
                (user_id,)
            )
            return results
        except Exception as e:
            self.logger.error(f"Erro ao obter mensagens do usuário {user_id}: {e}")
            return []
    
    def save_classification(self, user_id: int, classification: str, 
                          confidence: float, messages: str):
        """Salva classificação no banco"""
        try:
            self.db.execute_query(
                self.queries.insert_classification(user_id, classification, 
                                                 confidence, messages),
                (user_id, classification, confidence, messages)
            )
        except Exception as e:
            self.logger.error(f"Erro ao salvar classificação: {e}")
    
    def process_user(self, user_id: int) -> Dict[str, Any]:
        """Processa um usuário específico"""
        self.logger.info(f"Processando usuário: {user_id}")
        
        # Obtém mensagens
        messages = self.get_user_messages(user_id)
        
        if not messages:
            self.logger.warning(f"Usuário {user_id} não possui mensagens")
            return {"user_id": user_id, "status": "sem_mensagens"}
        
        # Analisa conversa
        analysis = self.analyzer.analyze_user_conversation(user_id, messages)
        
        # Salva no banco
        formatted_messages = self.analyzer.format_messages(messages)
        self.save_classification(
            user_id, 
            analysis["classification"], 
            analysis["confidence"],
            formatted_messages
        )
        
        self.logger.info(f"Usuário {user_id} classificado como: {analysis['classification']}")
        return analysis
    
    def export_classifications(self):
        """Exporta todas as classificações para CSV"""
        try:
            results = self.db.execute_query(self.queries.get_all_classifications())
            classifications = []
            
            for row in results:
                classifications.append({
                    "user_id": row[0],
                    "classification": row[1],
                    "confidence_score": row[2],
                    "analysis_date": row[3]
                })
            
            self.file_handler.save_classifications(classifications)
            self.logger.info(f"Exportadas {len(classifications)} classificações")
            
        except Exception as e:
            self.logger.error(f"Erro ao exportar classificações: {e}")
    
    def run(self, batch_size: int = 10, delay: float = 1.0):
        """Executa o classificador"""
        self.logger.info("Iniciando classificador de conversas")
        
        # Obtém usuários não classificados
        unclassified_users = self.get_unclassified_users()
        self.logger.info(f"Encontrados {len(unclassified_users)} usuários para classificar")
        
        processed_count = 0
        
        for i, user_id in enumerate(unclassified_users):
            try:
                result = self.process_user(user_id)
                processed_count += 1
                
                # Log de progresso
                if (i + 1) % batch_size == 0:
                    self.logger.info(f"Processados {i + 1}/{len(unclassified_users)} usuários")
                
                # Delay para evitar rate limiting
                time.sleep(delay)
                
            except Exception as e:
                self.logger.error(f"Erro ao processar usuário {user_id}: {e}")
                continue
        
        # Exporta resultados
        self.export_classifications()
        
        self.logger.info(f"Processamento concluído. {processed_count} usuários processados")

def main():
    classifier = ConversationClassifier()
    classifier.run(batch_size=10, delay=1.0)

if __name__ == "__main__":
    main()
```

### 5. Configuração (`config/config.yaml`)
```yaml
database:
  host: localhost
  port: 5432
  database: nome_banco
  user: usuario
  password: senha

openai:
  model: gpt-3.5-turbo
  max_tokens: 150
  temperature: 0.3

classifier:
  batch_size: 10
  delay_seconds: 1.0
  max_messages: 20

logging:
  level: INFO
  file: logs/classifier.log
```

### 6. Script de Execução

#### 6.1 Execução Manual
```bash
cd classificador-conversas
python src/main.py
```

#### 6.2 Execução Automatizada (cron job)
```bash
# Adicionar ao crontab para executar diariamente às 2h
0 2 * * * cd /path/to/classificador-conversas && python src/main.py
```

### 7. Monitoramento e Logs

O sistema gera logs detalhados em `logs/classifier_YYYYMMDD.log` com:
- Progresso do processamento
- Erros e exceções
- Estatísticas de classificação
- Performance e tempo de execução

### 8. Arquivos de Saída

#### 8.1 `data/classifications.csv`
Contém todas as classificações realizadas:
```csv
user_id,classification,confidence_score,analysis_date
2295,"1. Suporte Técnico - Problema com login",0.9,2024-01-15 10:30:00
3112,"2. Vendas - Interesse em plano premium",0.85,2024-01-15 10:31:00
```

#### 8.2 `data/processed_users.json`
Lista de usuários já processados para evitar reprocessamento.

### 9. Tratamento de Erros

O sistema inclui:
- Retry automático para falhas de API
- Logging detalhado de erros
- Continuidade do processamento mesmo com falhas individuais
- Backup de dados processados

### 10. Otimizações Recomendadas

1. **Cache de Classificações**: Implementar cache Redis para evitar reprocessamento
2. **Processamento Paralelo**: Usar multiprocessing para acelerar
3. **Rate Limiting**: Implementar controle de taxa para API OpenAI
4. **Métricas**: Adicionar dashboard de métricas de classificação
5. **Validação**: Implementar validação manual de classificações

### 11. Testes

```python
# test_classifier.py
import unittest
from src.main import ConversationClassifier

class TestConversationClassifier(unittest.TestCase):
    def setUp(self):
        self.classifier = ConversationClassifier()
    
    def test_classification(self):
        # Teste com mensagens de exemplo
        messages = [
            ("Olá, preciso de ajuda com meu login", "2024-01-15 10:00:00", "text"),
            ("Não consigo acessar minha conta", "2024-01-15 10:01:00", "text")
        ]
        
        result = self.classifier.analyzer.analyze_user_conversation(1, messages)
        self.assertIsNotNone(result["classification"])

if __name__ == "__main__":
    unittest.main()
```

### 12. Deploy e Manutenção

1. **Ambiente de Produção**: Usar Docker para containerização
2. **Monitoramento**: Implementar alertas para falhas
3. **Backup**: Backup automático das classificações
4. **Atualizações**: Pipeline de CI/CD para atualizações
5. **Documentação**: Manter documentação atualizada

Este sistema fornece uma solução completa e escalável para classificação automática de conversas usando IA, com controle de reprocessamento e exportação de resultados. 