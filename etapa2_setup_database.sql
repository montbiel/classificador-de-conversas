-- =====================================================
-- ETAPA 2: Configuração do Banco de Dados
-- Banco: redfine_core
-- =====================================================

-- 1. Verificar versão do PostgreSQL
SELECT version();

-- 2. Criar tabela de histórico de chat (se não existir)
CREATE TABLE IF NOT EXISTS chat_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_type VARCHAR(50) DEFAULT 'text'
);

-- 3. Criar tabela para armazenar classificações
CREATE TABLE IF NOT EXISTS conversation_classifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    classification TEXT NOT NULL,
    confidence_score FLOAT,
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_20_messages TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Criar índices para otimização
CREATE INDEX IF NOT EXISTS idx_chat_history_user_id ON chat_history(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_timestamp ON chat_history(timestamp);
CREATE INDEX IF NOT EXISTS idx_classifications_user_id ON conversation_classifications(user_id);

-- 5. Verificar se as tabelas foram criadas corretamente
\dt chat_history
\dt conversation_classifications

-- 6. Verificar estrutura da tabela chat_history
\d chat_history

-- 7. Verificar se existem dados na tabela chat_history
SELECT COUNT(*) as total_mensagens FROM chat_history;
SELECT COUNT(DISTINCT user_id) as usuarios_unicos FROM chat_history;

-- 8. Verificar se os IDs do customers.csv existem na chat_history
-- (Execute apenas se a tabela customers existir no banco)
-- SELECT COUNT(*) as clientes_com_mensagens 
-- FROM chat_history 
-- WHERE user_id IN (SELECT id FROM customers);

-- 9. Inserir dados de teste (OPCIONAL - descomente se quiser testar)
-- INSERT INTO chat_history (user_id, message, timestamp) VALUES
-- (2295, 'Olá, preciso de ajuda com meu login', '2024-01-15 10:00:00'),
-- (2295, 'Não consigo acessar minha conta', '2024-01-15 10:01:00'),
-- (3112, 'Gostaria de informações sobre o plano premium', '2024-01-15 11:00:00'),
-- (3112, 'Qual o valor mensal?', '2024-01-15 11:01:00');

-- 10. Verificar dados de teste (se inseridos)
-- SELECT COUNT(*) as total_mensagens FROM chat_history;
-- SELECT DISTINCT user_id FROM chat_history LIMIT 10;

-- =====================================================
-- FIM DA ETAPA 2
-- ===================================================== 