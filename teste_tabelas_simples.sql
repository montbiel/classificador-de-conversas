-- =====================================================
-- TESTE SIMPLIFICADO - CRIAÇÃO DE TABELAS
-- Execute cada comando separadamente
-- =====================================================

-- PASSO 1: Verificar conexão
SELECT version();

-- PASSO 2: Verificar banco atual
SELECT current_database();

-- PASSO 3: Verificar se as tabelas já existem
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('chat_history', 'conversation_classifications');

-- PASSO 4: Criar tabela chat_history (execute apenas se não existir)
CREATE TABLE IF NOT EXISTS chat_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_type VARCHAR(50) DEFAULT 'text'
);

-- PASSO 5: Verificar se chat_history foi criada
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name = 'chat_history';

-- PASSO 6: Criar tabela conversation_classifications (execute apenas se não existir)
CREATE TABLE IF NOT EXISTS conversation_classifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    classification TEXT NOT NULL,
    confidence_score FLOAT,
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_20_messages TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- PASSO 7: Verificar se conversation_classifications foi criada
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name = 'conversation_classifications';

-- PASSO 8: Criar índices (execute apenas se as tabelas existirem)
CREATE INDEX IF NOT EXISTS idx_chat_history_user_id ON chat_history(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_timestamp ON chat_history(timestamp);
CREATE INDEX IF NOT EXISTS idx_classifications_user_id ON conversation_classifications(user_id);

-- PASSO 9: Verificar estrutura das tabelas
\d chat_history
\d conversation_classifications

-- PASSO 10: Teste final - inserir e consultar dados
INSERT INTO chat_history (user_id, message) VALUES (999, 'Teste de conexão');
SELECT * FROM chat_history WHERE user_id = 999;
DELETE FROM chat_history WHERE user_id = 999;

-- =====================================================
-- FIM DO TESTE
-- ===================================================== 