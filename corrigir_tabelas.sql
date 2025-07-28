-- =====================================================
-- CORREÇÃO - CRIAÇÃO DE TABELAS
-- Execute cada comando separadamente
-- =====================================================

-- PASSO 1: Verificar se as tabelas existem
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('chat_history', 'conversation_classifications');

-- PASSO 2: Se as tabelas existirem, vamos removê-las primeiro
DROP TABLE IF EXISTS conversation_classifications CASCADE;
DROP TABLE IF EXISTS chat_history CASCADE;

-- PASSO 3: Criar tabela chat_history do zero
CREATE TABLE chat_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_type VARCHAR(50) DEFAULT 'text'
);

-- PASSO 4: Verificar se chat_history foi criada
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name = 'chat_history';

-- PASSO 5: Verificar estrutura da tabela chat_history
\d chat_history

-- PASSO 6: Criar tabela conversation_classifications
CREATE TABLE conversation_classifications (
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

-- PASSO 8: Verificar estrutura da tabela conversation_classifications
\d conversation_classifications

-- PASSO 9: Criar índices (agora que as tabelas existem)
CREATE INDEX idx_chat_history_user_id ON chat_history(user_id);
CREATE INDEX idx_chat_history_timestamp ON chat_history(timestamp);
CREATE INDEX idx_classifications_user_id ON conversation_classifications(user_id);

-- PASSO 10: Teste final - inserir dados de teste
INSERT INTO chat_history (user_id, message) VALUES (999, 'Teste de conexão');
SELECT * FROM chat_history WHERE user_id = 999;
DELETE FROM chat_history WHERE user_id = 999;

-- PASSO 11: Verificação final
SELECT 
    table_name,
    column_name,
    data_type
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND table_name IN ('chat_history', 'conversation_classifications')
ORDER BY table_name, ordinal_position;

-- =====================================================
-- FIM DA CORREÇÃO
-- ===================================================== 