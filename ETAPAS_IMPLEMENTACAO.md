# Etapas de Implementação - Classificador de Conversas com IA

## Visão Geral das Etapas

Este documento organiza a implementação do classificador de conversas em etapas práticas e sequenciais, considerando que:
- A tabela `chat_history` já existe no banco `redfine_core`
- O arquivo `customers.csv` já está disponível
- Precisamos criar apenas a tabela `classificacoes`
- O sistema deve processar as 20 últimas mensagens de cada usuário

---

## 📋 ETAPA 1: Configuração do Ambiente e Instalação

### 1.1 Verificação da Estrutura Atual
```bash
# Verificar se estamos no diretório correto
pwd
# Deve mostrar: /c/Users/andro/OneDrive/Documentos/Classificador das conversas

# Verificar arquivos existentes
ls -la
# Deve mostrar: customers.csv, venv/, etc.
```

### 1.2 Ativação do Ambiente Virtual
```bash
# Ativar ambiente virtual (Windows PowerShell)
.\venv\Scripts\Activate.ps1
# Deve mostrar: (venv) PS C:\Users\andro\OneDrive\Documentos\Classificador das conversas
```

### 1.3 Instalação das Dependências Necessárias
```bash
# Instalar dependências para o novo sistema
pip install asyncpg openai python-dotenv pandas
```

### 1.4 Configuração de Variáveis de Ambiente
```bash
# Criar arquivo .env (se não existir)
echo "OPENAI_API_KEY=sua_chave_api_aqui" > .env
```

**Resultado da Etapa 1:** ✅ **CONCLUÍDA COM SUCESSO!**

### ✅ Checklist da Etapa 1 - CONCLUÍDA:

- [x] **1.1 Verificação da Estrutura Atual** ✅
  - [x] Diretório do projeto confirmado
  - [x] Arquivo `customers.csv` presente
  - [x] Ambiente virtual existente

- [x] **1.2 Ativação do Ambiente Virtual** ✅
  - [x] Ambiente virtual ativado com sucesso
  - [x] Prompt mostra `(venv)`

- [x] **1.3 Instalação das Dependências** ✅
  - [x] `asyncpg` instalado
  - [x] `openai` instalado
  - [x] `python-dotenv` instalado
  - [x] `pandas` instalado

- [x] **1.4 Configuração de Variáveis de Ambiente** ✅
  - [x] Arquivo `.env` criado
  - [x] `OPENAI_API_KEY` configurado

**🎉 ETAPA 1 COMPLETAMENTE FINALIZADA!**

---

## 🗄️ ETAPA 2: Diagnóstico e Criação da Tabela Classificações

### 2.1 Diagnóstico da Estrutura Atual do Banco
```bash
# Executar diagnóstico para verificar estrutura atual
python diagnosticar_tabela_existente.py
```

**Resultado esperado:**
- ✅ Tabela `chat_history` encontrada
- ❌ Tabela `classificacoes` não encontrada
- 📊 Total de registros na tabela chat_history: X
- 📋 Estrutura da tabela chat_history mostrada

### 2.2 Criação da Tabela Classificações
```bash
# Criar apenas a tabela classificacoes
python criar_tabela_classificacoes.py
```

**Resultado esperado:**
- ✅ Tabela classificacoes criada com sucesso
- ✅ Índices criados para otimização
- ✅ Teste de inserção realizado com sucesso
- 🎯 PRÓXIMO PASSO: ETAPA 3

### 2.3 Verificação da Estrutura Final
```sql
-- Conectar ao PostgreSQL e verificar:
-- Verificar se a tabela classificacoes foi criada
\dt classificacoes

-- Verificar estrutura da tabela
\d classificacoes

-- Verificar se existem dados na tabela chat_history
SELECT COUNT(*) as total_mensagens FROM chat_history;
SELECT COUNT(DISTINCT user_id) as usuarios_unicos FROM chat_history;

-- Verificar se os IDs do customers.csv existem na chat_history
SELECT COUNT(*) as clientes_com_mensagens 
FROM chat_history 
WHERE user_id IN (SELECT id FROM customers);
```

**Resultado da Etapa 2:** Tabela `classificacoes` criada e pronta para uso.

---

## 🔧 ETAPA 3: Implementação do Sistema de Classificação

### 3.1 Arquivo de Configuração (`config.py`)
```python
# Arquivo já criado com:
# - Configuração do banco de dados
# - Configuração da OpenAI
# - Prompts para classificação
# - Configurações do sistema
```

### 3.2 Módulo de Conexão com Banco (`database.py`)
```python
#!/usr/bin/env python3
"""
Módulo de conexão com banco de dados
"""

import asyncio
import asyncpg
import logging
from typing import List, Dict, Any, Optional
from config import DATABASE_URL

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
            return df['id'].astype(str).tolist()
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
    
    async def get_last_20_messages(self, user_id: str) -> List[Dict[str, Any]]:
        """Obtém as últimas 20 mensagens de um usuário"""
        try:
            conn = await self.get_connection()
            
            messages = await conn.fetch("""
                SELECT message, timestamp, role
                FROM chat_history
                WHERE user_id = $1
                ORDER BY timestamp DESC
                LIMIT 20
            """, user_id)
            
            await conn.close()
            
            return [
                {
                    "message": msg["message"],
                    "timestamp": msg["timestamp"],
                    "role": msg["role"]
                }
                for msg in messages
            ]
            
        except Exception as e:
            self.logger.error(f"Erro ao obter mensagens do usuário {user_id}: {e}")
            return []
    
    async def save_classification(self, user_id: str, classification: str, 
                                confidence: float, context: str, 
                                tokens_used: int, processing_time: int):
        """Salva classificação no banco"""
        try:
            conn = await self.get_connection()
            
            await conn.execute("""
                INSERT INTO classificacoes (
                    user_id, classificacao, confianca, contexto,
                    tokens_utilizados, tempo_processamento_ms, status
                ) VALUES ($1, $2, $3, $4, $5, $6, 'concluido')
            """, user_id, classification, confidence, context, 
                 tokens_used, processing_time)
            
            await conn.close()
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar classificação: {e}")
            raise
```

### 3.3 Módulo de Classificação com IA (`ai_classifier.py`)
```python
#!/usr/bin/env python3
"""
Módulo de classificação usando OpenAI
"""

import asyncio
import time
import logging
from typing import Dict, Any, List
import openai
from config import OPENAI_API_KEY, OPENAI_MODEL, CLASSIFICATION_PROMPT

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
            timestamp = msg["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
            role = msg.get("role", "user")
            message = msg["message"]
            formatted.append(f"[{timestamp}] {role}: {message}")
        
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
            prompt = CLASSIFICATION_PROMPT.format(messages=formatted_messages)
            
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
```

### 3.4 Programa Principal (`main.py`)
```python
#!/usr/bin/env python3
"""
Programa principal do classificador de conversas
"""

import asyncio
import logging
import time
from typing import List, Dict, Any
from database import DatabaseManager
from ai_classifier import AIClassifier
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
        self.ai = AIClassifier()
    
    async def process_user(self, user_id: str) -> Dict[str, Any]:
        """Processa um usuário específico"""
        logger.info(f"Processando usuário: {user_id}")
        
        try:
            # Obter mensagens do usuário
            messages = await self.db.get_last_20_messages(user_id)
            
            if not messages:
                logger.warning(f"Usuário {user_id} não possui mensagens")
                return {
                    "user_id": user_id,
                    "status": "sem_mensagens",
                    "classification": "Sem dados para análise"
                }
            
            # Classificar conversa
            result = await self.ai.classify_conversation(messages)
            
            # Salvar no banco
            await self.db.save_classification(
                user_id=user_id,
                classification=result["classification"],
                confidence=result["confidence"],
                context=result["context"],
                tokens_used=result["tokens_used"],
                processing_time=result["processing_time"]
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
            for i, user_id in enumerate(unclassified_users):
                try:
                    result = await self.process_user(user_id)
                    processed_count += 1
                    
                    # Log de progresso
                    if (i + 1) % BATCH_SIZE == 0:
                        logger.info(f"📈 Processados {i + 1}/{len(unclassified_users)} usuários")
                    
                    # Delay para evitar rate limiting
                    if i < len(unclassified_users) - 1:  # Não delay no último
                        await asyncio.sleep(DELAY_BETWEEN_REQUESTS)
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao processar usuário {user_id}: {e}")
                    continue
            
            logger.info(f"🎉 Processamento concluído! {processed_count} usuários processados")
            
        except Exception as e:
            logger.error(f"❌ Erro geral no processamento: {e}")

async def main():
    """Função principal"""
    classifier = ConversationClassifier()
    await classifier.run()

if __name__ == "__main__":
    asyncio.run(main())
```

**Resultado da Etapa 3:** Sistema completo implementado e pronto para execução.

---

## 🧪 ETAPA 4: Testes e Execução

### 4.1 Teste de Conexão com Banco
```bash
# Testar se a conexão está funcionando
python -c "
import asyncio
from database import DatabaseManager

async def test():
    db = DatabaseManager()
    try:
        conn = await db.get_connection()
        print('✅ Conexão com banco OK!')
        await conn.close()
    except Exception as e:
        print(f'❌ Erro na conexão: {e}')

asyncio.run(test())
"
```

### 4.2 Teste do Sistema de IA
```bash
# Testar se a API da OpenAI está configurada
python -c "
import asyncio
from ai_classifier import AIClassifier

async def test():
    ai = AIClassifier()
    test_messages = [
        {'message': 'Olá, preciso de ajuda com meu login', 'timestamp': '2024-01-15 10:00:00', 'role': 'user'},
        {'message': 'Não consigo acessar minha conta', 'timestamp': '2024-01-15 10:01:00', 'role': 'user'}
    ]
    result = await ai.classify_conversation(test_messages)
    print(f'Classificação: {result}')

asyncio.run(test())
"
```

### 4.3 Execução Completa do Sistema
```bash
# Executar o classificador completo
python main.py
```

**Resultado esperado:**
```
🚀 Iniciando classificador de conversas
📊 Encontrados X usuários para classificar
Processando usuário: 12345
Usuário 12345 classificado como: 1|Usuário fez várias perguntas sobre funcionalidades
📈 Processados 5/50 usuários
...
🎉 Processamento concluído! 50 usuários processados
```

---

## 📊 ETAPA 5: Verificação de Resultados

### 5.1 Verificação no Banco de Dados
```sql
-- Conectar ao banco redfine_core
psql -h 127.0.0.1 -p 5432 -U postgres -d redfine_core

-- Verificar classificações criadas
SELECT COUNT(*) as total_classificacoes FROM classificacoes;

-- Verificar distribuição das classificações
SELECT classificacao, COUNT(*) as quantidade 
FROM classificacoes 
GROUP BY classificacao 
ORDER BY quantidade DESC;

-- Verificar usuários processados
SELECT user_id, classificacao, confianca, data_classificacao
FROM classificacoes
ORDER BY data_classificacao DESC
LIMIT 10;
```

### 5.2 Verificação de Logs
```bash
# Verificar logs gerados
tail -f classificador.log
```

### 5.3 Exportação de Resultados
```python
# Script para exportar resultados para CSV
import asyncio
import pandas as pd
from database import DatabaseManager

async def export_results():
    db = DatabaseManager()
    conn = await db.get_connection()
    
    # Buscar todas as classificações
    results = await conn.fetch("""
        SELECT user_id, classificacao, confianca, contexto, 
               data_classificacao, tokens_utilizados, tempo_processamento_ms
        FROM classificacoes
        ORDER BY data_classificacao DESC
    """)
    
    # Converter para DataFrame
    df = pd.DataFrame(results, columns=[
        'user_id', 'classificacao', 'confianca', 'contexto',
        'data_classificacao', 'tokens_utilizados', 'tempo_processamento_ms'
    ])
    
    # Salvar em CSV
    df.to_csv('classificacoes_completas.csv', index=False)
    print(f"✅ Exportadas {len(df)} classificações para classificacoes_completas.csv")
    
    await conn.close()

asyncio.run(export_results())
```

---

## 🔄 ETAPA 6: Automação e Monitoramento

### 6.1 Script de Execução Automatizada
```bash
# Criar script de execução (Windows)
echo '@echo off
cd /d "C:\Users\andro\OneDrive\Documentos\Classificador das conversas"
call venv\Scripts\activate.bat
python main.py
pause' > executar_classificador.bat
```

### 6.2 Monitoramento de Progresso
```python
# Script para verificar progresso
import asyncio
from database import DatabaseManager

async def check_progress():
    db = DatabaseManager()
    
    # Total de clientes no CSV
    customers = await db.get_customers_from_csv()
    total_customers = len(customers)
    
    # Total de classificações
    conn = await db.get_connection()
    total_classifications = await conn.fetchval("SELECT COUNT(*) FROM classificacoes")
    await conn.close()
    
    # Progresso
    progress = (total_classifications / total_customers) * 100
    
    print(f"📊 PROGRESSO DO CLASSIFICADOR")
    print(f"Total de clientes: {total_customers}")
    print(f"Classificações realizadas: {total_classifications}")
    print(f"Progresso: {progress:.1f}%")
    
    if progress < 100:
        remaining = total_customers - total_classifications
        print(f"Restam: {remaining} clientes para classificar")
    else:
        print("✅ Todos os clientes foram classificados!")

asyncio.run(check_progress())
```

---

## ✅ Checklist de Conclusão

- [x] **ETAPA 1: Configuração do Ambiente** ✅
  - [x] Ambiente virtual ativado
  - [x] Dependências instaladas
  - [x] Variáveis de ambiente configuradas

- [x] **ETAPA 2: Diagnóstico e Criação da Tabela** ✅
  - [x] Diagnóstico executado
  - [x] Tabela classificacoes criada
  - [x] Estrutura verificada

- [x] **ETAPA 3: Implementação do Sistema** ✅
  - [x] Módulos criados
  - [x] Sistema de IA configurado
  - [x] Programa principal implementado

- [x] **ETAPA 4: Testes e Execução** ✅
  - [x] Testes de conexão realizados
  - [x] Sistema executado com sucesso
  - [x] Resultados verificados

- [x] **ETAPA 5: Verificação de Resultados** ✅
  - [x] Classificações verificadas no banco
  - [x] Logs analisados
  - [x] Resultados exportados

- [x] **ETAPA 6: Automação e Monitoramento** ✅
  - [x] Scripts de automação criados
  - [x] Monitoramento configurado

---

## 🚨 Troubleshooting

### Problemas Comuns:

1. **Erro de conexão com banco**: 
   - Verificar se o PostgreSQL está rodando
   - Verificar credenciais no DATABASE_URL
   - Testar conexão manualmente

2. **Erro da API OpenAI**: 
   - Verificar OPENAI_API_KEY no arquivo .env
   - Verificar limites de uso da API
   - Testar com uma chamada simples

3. **Arquivo customers.csv não encontrado**: 
   - Verificar se o arquivo está no diretório raiz
   - Verificar se tem a coluna 'id'

4. **Tabela chat_history não encontrada**: 
   - Verificar se a tabela existe no banco redfine_core
   - Verificar se tem as colunas: id, user_id, message, timestamp, role

### Comandos de Debug:
```bash
# Verificar variáveis de ambiente
python -c "from config import DATABASE_URL, OPENAI_API_KEY; print('DATABASE_URL:', DATABASE_URL); print('OPENAI_API_KEY:', OPENAI_API_KEY[:10] + '...' if OPENAI_API_KEY else 'Não configurado')"

# Testar conexão com banco
python diagnosticar_tabela_existente.py

# Verificar clientes no CSV
python -c "import pandas as pd; df = pd.read_csv('customers.csv'); print('Total clientes:', len(df)); print('Primeiros 5:', df['id'].head().tolist())"

# Verificar logs
tail -n 50 classificador.log
```

Este documento fornece um guia passo a passo atualizado e simplificado para implementar o classificador de conversas, considerando a estrutura atual do projeto. 