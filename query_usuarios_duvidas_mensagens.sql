-- =====================================================
-- QUERY: USUÁRIOS COM DÚVIDAS + MENSAGENS REAIS
-- =====================================================

-- QUERY PRINCIPAL: Com as 20 últimas mensagens reais
SELECT 
    c.user_id,
    c.wa_id,
    cust.profile_name as nome_cliente,
    cust.from_number as telefone_cliente,
    c.classificacao as tag_principal,
    c.classificacao_especifica as tag_especifica,
    c.confianca,
    c.data_classificacao,
    STRING_AGG(
        CONCAT(
            CASE 
                WHEN ch.message_type = 'USR' THEN '👤 Cliente: '
                WHEN ch.message_type = 'AIO' THEN '🤖 IA: '
                ELSE '❓ Outro: '
            END,
            ch.message
        ), 
        E'\n' ORDER BY ch.message_date DESC
    ) as mensagens_analisadas
FROM classificacoes c
LEFT JOIN customers cust ON c.user_id = cust.id::text
LEFT JOIN LATERAL (
    SELECT 
        ch2.message,
        ch2.message_type,
        ch2.message_date
    FROM chat_history ch2
    WHERE ch2.customer_id = c.user_id::integer
        AND ch2.message_type IN ('USR', 'AIO')
    ORDER BY ch2.message_date DESC
    LIMIT 20
) ch ON true
WHERE c.classificacao LIKE '%Dúvidas%'
    AND c.classificacao != 'Erro na classificação'
GROUP BY c.user_id, c.wa_id, cust.profile_name, cust.from_number, 
         c.classificacao, c.classificacao_especifica, c.confianca, c.data_classificacao
ORDER BY c.data_classificacao DESC;

-- QUERY ALTERNATIVA: Versão mais simples sem agregação
SELECT 
    c.user_id,
    c.wa_id,
    cust.profile_name as nome_cliente,
    cust.from_number as telefone_cliente,
    c.classificacao as tag_principal,
    c.classificacao_especifica as tag_especifica,
    c.confianca,
    c.data_classificacao,
    ch.message_type,
    ch.message,
    ch.message_date
FROM classificacoes c
LEFT JOIN customers cust ON c.user_id = cust.id::text
LEFT JOIN chat_history ch ON ch.customer_id = c.user_id::integer
    AND ch.message_type IN ('USR', 'AIO')
WHERE c.classificacao LIKE '%Dúvidas%'
    AND c.classificacao != 'Erro na classificação'
    AND ch.message_date >= (
        SELECT MAX(ch2.message_date) - INTERVAL '7 days'
        FROM chat_history ch2 
        WHERE ch2.customer_id = c.user_id::integer
    )
ORDER BY c.data_classificacao DESC, ch.message_date DESC;

-- QUERY COM EXATAMENTE 25 ÚLTIMAS MENSAGENS POR USUÁRIO
WITH ranked_messages AS (
    SELECT 
        ch.customer_id,
        ch.message,
        ch.message_type,
        ch.message_date,
        ROW_NUMBER() OVER (
            PARTITION BY ch.customer_id 
            ORDER BY ch.message_date DESC
        ) as rn
    FROM chat_history ch
    WHERE ch.message_type IN ('USR', 'AIR')
)
SELECT 
    c.user_id,
    c.wa_id,
    cust.profile_name as nome_cliente,
    cust.from_number as telefone_cliente,
    c.classificacao as tag_principal,
    c.classificacao_especifica as tag_especifica,
    c.confianca,
    c.data_classificacao,
    rm.message_type,
    rm.message,
    rm.message_date
FROM classificacoes c
LEFT JOIN customers cust ON c.user_id = cust.id::text
LEFT JOIN ranked_messages rm ON rm.customer_id = c.user_id::integer
WHERE c.classificacao LIKE '%Dúvidas%'
    AND c.classificacao != 'Erro na classificação'
    AND rm.rn <= 25
ORDER BY c.data_classificacao DESC, rm.message_date ASC;

-- QUERY FINAL: Mensagens agrupadas por usuário (RECOMENDADA) - 25 ÚLTIMAS MENSAGENS
WITH ranked_messages AS (
    SELECT 
        ch.customer_id,
        ch.message,
        ch.message_type,
        ch.message_date,
        ROW_NUMBER() OVER (
            PARTITION BY ch.customer_id 
            ORDER BY ch.message_date DESC
        ) as rn
    FROM chat_history ch
    WHERE ch.message_type IN ('USR', 'AIR')
),
user_messages AS (
    SELECT 
        rm.customer_id,
        STRING_AGG(
            CONCAT(
                CASE 
                    WHEN rm.message_type = 'USR' THEN '👤 Cliente: '
                    WHEN rm.message_type = 'AIR' THEN '🤖 IA: '
                    ELSE '❓ Outro: '
                END,
                rm.message
            ), 
            E'\n' ORDER BY rm.message_date ASC
        ) as mensagens_analisadas,
        MAX(rm.message_date) as ultima_interacao
    FROM ranked_messages rm
    WHERE rm.rn <= 25
    GROUP BY rm.customer_id
)
SELECT 
    c.user_id,
    c.wa_id,
    cust.profile_name as nome_cliente,
    cust.from_number as telefone_cliente,
    c.classificacao as tag_principal,
    c.classificacao_especifica as tag_especifica,
    c.confianca,
    c.data_classificacao,
    c.sugestao_melhoria,
    um.mensagens_analisadas
FROM classificacoes c
LEFT JOIN customers cust ON c.user_id = cust.id::text
LEFT JOIN user_messages um ON um.customer_id = c.user_id::integer
WHERE c.classificacao LIKE '%Dúvidas%'
    AND c.classificacao != 'Erro na classificação'
ORDER BY um.ultima_interacao DESC;

-- =====================================================
-- QUERY: QUANTIDADE TOTAL DE TAGS POR CATEGORIA
-- =====================================================

-- QUERY PRINCIPAL: Contagem de todas as classificações principais
SELECT 
    c.classificacao as categoria_principal,
    COUNT(*) as quantidade_total,
    ROUND(
        (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM classificacoes WHERE classificacao != 'Erro na classificação')), 
        2
    ) as percentual
FROM classificacoes c
WHERE c.classificacao != 'Erro na classificação'
GROUP BY c.classificacao
ORDER BY quantidade_total DESC;

-- QUERY DETALHADA: Contagem de classificações específicas
SELECT 
    c.classificacao as categoria_principal,
    c.classificacao_especifica as categoria_especifica,
    COUNT(*) as quantidade,
    ROUND(
        (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM classificacoes WHERE classificacao != 'Erro na classificação')), 
        2
    ) as percentual_total,
    ROUND(
        (COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY c.classificacao)), 
        2
    ) as percentual_categoria
FROM classificacoes c
WHERE c.classificacao != 'Erro na classificação'
    AND c.classificacao_especifica IS NOT NULL
    AND c.classificacao_especifica != ''
GROUP BY c.classificacao, c.classificacao_especifica
ORDER BY c.classificacao, quantidade DESC;

-- QUERY RESUMIDA: Apenas categorias principais com totais
SELECT 
    CASE 
        WHEN c.classificacao LIKE '%Dúvidas%' THEN 'Dúvidas Gerais'
        WHEN c.classificacao LIKE '%Problemas%' THEN 'Problemas'
        WHEN c.classificacao LIKE '%Outros%' THEN 'Outros'
        ELSE c.classificacao
    END as categoria_agrupada,
    COUNT(*) as quantidade_total,
    ROUND(
        (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM classificacoes WHERE classificacao != 'Erro na classificação')), 
        2
    ) as percentual
FROM classificacoes c
WHERE c.classificacao != 'Erro na classificação'
GROUP BY 
    CASE 
        WHEN c.classificacao LIKE '%Dúvidas%' THEN 'Dúvidas Gerais'
        WHEN c.classificacao LIKE '%Problemas%' THEN 'Problemas'
        WHEN c.classificacao LIKE '%Outros%' THEN 'Outros'
        ELSE c.classificacao
    END
ORDER BY quantidade_total DESC;

-- =====================================================
-- QUERY: APENAS DÚVIDAS - CATEGORIA PRINCIPAL
-- =====================================================

-- QUERY PRINCIPAL: Apenas dúvidas com categoria principal
SELECT 
    c.classificacao as categoria_principal,
    COUNT(*) as quantidade_total,
    ROUND(
        (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM classificacoes WHERE classificacao LIKE '%Dúvidas%')), 
        2
    ) as percentual_dentro_duvidas
FROM classificacoes c
WHERE c.classificacao LIKE '%Dúvidas%'
    AND c.classificacao != 'Erro na classificação'
GROUP BY c.classificacao
ORDER BY quantidade_total DESC;

-- QUERY DETALHADA: Dúvidas com informações dos usuários
SELECT 
    c.user_id,
    c.wa_id,
    cust.profile_name as nome_cliente,
    cust.from_number as telefone_cliente,
    c.classificacao as categoria_principal,
    c.confianca,
    c.data_classificacao,
    c.sugestao_melhoria
FROM classificacoes c
LEFT JOIN customers cust ON c.user_id = cust.id::text
WHERE c.classificacao LIKE '%Dúvidas%'
    AND c.classificacao != 'Erro na classificação'
ORDER BY c.data_classificacao DESC;

-- QUERY RESUMO: Total de dúvidas vs total geral
SELECT 
    'Total de Dúvidas' as tipo,
    COUNT(*) as quantidade,
    ROUND(
        (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM classificacoes WHERE classificacao != 'Erro na classificação')), 
        2
    ) as percentual_do_total
FROM classificacoes c
WHERE c.classificacao LIKE '%Dúvidas%'
    AND c.classificacao != 'Erro na classificação'

UNION ALL

SELECT 
    'Total Geral (sem dúvidas)' as tipo,
    COUNT(*) as quantidade,
    ROUND(
        (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM classificacoes WHERE classificacao != 'Erro na classificação')), 
        2
    ) as percentual_do_total
FROM classificacoes c
WHERE c.classificacao NOT LIKE '%Dúvidas%'
    AND c.classificacao != 'Erro na classificação'

ORDER BY quantidade DESC;

-- =====================================================
-- QUERY GENÉRICA: CATEGORIA ESPECÍFICA + MENSAGENS + SUGESTÕES
-- =====================================================

-- QUERY GENÉRICA: Substitua XXXX pela categoria desejada (ex: 'Dúvidas', 'Problemas', 'Outros')
-- Exemplo de uso: 
-- - Para dúvidas: WHERE c.classificacao LIKE '%Dúvidas%'
-- - Para problemas: WHERE c.classificacao LIKE '%Problemas%'
-- - Para outros: WHERE c.classificacao LIKE '%Outros%'
-- - Para categoria específica: WHERE c.classificacao = 'Dúvidas sobre preço/valor'

WITH ranked_messages AS (
    SELECT 
        ch.customer_id,
        ch.message,
        ch.message_type,
        ch.message_date,
        ROW_NUMBER() OVER (
            PARTITION BY ch.customer_id 
            ORDER BY ch.message_date DESC
        ) as rn
    FROM chat_history ch
    WHERE ch.message_type IN ('USR', 'AIO')
),
user_messages AS (
    SELECT 
        rm.customer_id,
        STRING_AGG(
            CONCAT(
                CASE 
                    WHEN rm.message_type = 'USR' THEN '👤 Cliente: '
                    WHEN rm.message_type = 'AIO' THEN '🤖 IA: '
                    ELSE '❓ Outro: '
                END,
                rm.message
            ), 
            E'\n' ORDER BY rm.message_date ASC
        ) as mensagens_analisadas,
        MAX(rm.message_date) as ultima_interacao
    FROM ranked_messages rm
    WHERE rm.rn <= 25
    GROUP BY rm.customer_id
)
SELECT 
    c.user_id,
    c.wa_id,
    cust.profile_name as nome_cliente,
    cust.from_number as telefone_cliente,
    c.classificacao as categoria_principal,
    c.classificacao_especifica as categoria_especifica,
    c.confianca,
    c.data_classificacao,
    c.sugestao_melhoria,
    um.mensagens_analisadas
FROM classificacoes c
LEFT JOIN customers cust ON c.user_id = cust.id::text
LEFT JOIN user_messages um ON um.customer_id = c.user_id::integer
WHERE c.classificacao LIKE '%XXXX%'  -- SUBSTITUA XXXX pela categoria desejada
    AND c.classificacao != 'Erro na classificação'
ORDER BY c.data_classificacao DESC;

-- =====================================================
-- QUERY GENÉRICA SIMPLIFICADA (ALTERNATIVA)
-- =====================================================

-- Versão mais simples que pode funcionar melhor em alguns casos
SELECT 
    c.user_id,
    c.wa_id,
    cust.profile_name as nome_cliente,
    cust.from_number as telefone_cliente,
    c.classificacao as categoria_principal,
    c.classificacao_especifica as categoria_especifica,
    c.confianca,
    c.data_classificacao,
    c.sugestao_melhoria,
    STRING_AGG(
        CONCAT(
            CASE 
                WHEN ch.message_type = 'USR' THEN '👤 Cliente: '
                WHEN ch.message_type = 'AIO' THEN '🤖 IA: '
                ELSE '❓ Outro: '
            END,
            ch.message
        ), 
        E'\n' ORDER BY ch.message_date DESC
    ) as mensagens_analisadas
FROM classificacoes c
LEFT JOIN customers cust ON c.user_id = cust.id::text
LEFT JOIN chat_history ch ON ch.customer_id = c.user_id::integer
    AND ch.message_type IN ('USR', 'AIO')
WHERE c.classificacao LIKE '%XXXX%'  -- SUBSTITUA XXXX pela categoria desejada
    AND c.classificacao != 'Erro na classificação'
GROUP BY c.user_id, c.wa_id, cust.profile_name, cust.from_number, 
         c.classificacao, c.classificacao_especifica, c.confianca, c.data_classificacao, c.sugestao_melhoria
ORDER BY c.data_classificacao DESC;

-- =====================================================
-- EXEMPLOS DE USO DA QUERY GENÉRICA
-- =====================================================

-- EXEMPLO 1: Para ver apenas dúvidas
-- WHERE c.classificacao LIKE '%Dúvidas%'

-- EXEMPLO 2: Para ver apenas problemas financeiros
-- WHERE c.classificacao LIKE '%Problemas financeiros%'

-- EXEMPLO 3: Para ver apenas "Outros"
-- WHERE c.classificacao LIKE '%Outros%'

-- EXEMPLO 4: Para ver uma categoria específica exata
-- WHERE c.classificacao = 'Dúvidas sobre preço/valor'

-- EXEMPLO 5: Para ver múltiplas categorias
-- WHERE c.classificacao IN ('Dúvidas sobre preço/valor', 'Problemas financeiros: dificuldade financeira')

-- =====================================================
-- QUERY DE DIAGNÓSTICO
-- =====================================================

-- Verificar se existem dados nas tabelas
SELECT 'classificacoes' as tabela, COUNT(*) as total_registros FROM classificacoes
UNION ALL
SELECT 'customers' as tabela, COUNT(*) as total_registros FROM customers
UNION ALL
SELECT 'chat_history' as tabela, COUNT(*) as total_registros FROM chat_history;

-- Verificar categorias disponíveis
SELECT DISTINCT classificacao, COUNT(*) as quantidade
FROM classificacoes 
WHERE classificacao != 'Erro na classificação'
GROUP BY classificacao
ORDER BY quantidade DESC;

-- Verificar tipos de mensagem disponíveis
SELECT DISTINCT message_type, COUNT(*) as quantidade
FROM chat_history
GROUP BY message_type
ORDER BY quantidade DESC;

-- =====================================================
-- QUERY MODIFICADA: USUÁRIOS COM DÚVIDAS SOBRE CERTIFICADO
-- =====================================================

-- Query original modificada para mostrar ID e wa_id dos usuários
SELECT 
    c.user_id,
    c.wa_id,
    c.classificacao as categoria_principal,
    c.classificacao_especifica as categoria_especifica,
    c.confianca,
    c.data_classificacao
FROM classificacoes c
WHERE c.classificacao LIKE '%Dúvidas sobre certificado%'
    AND c.classificacao_especifica IS NOT NULL
    AND c.classificacao_especifica != ''
ORDER BY c.data_classificacao DESC;

-- =====================================================
-- QUERY ALTERNATIVA: COM INFORMAÇÕES ADICIONAIS DO CLIENTE
-- =====================================================

-- Versão com dados do cliente incluídos
SELECT 
    c.user_id,
    c.wa_id,
    cust.profile_name as nome_cliente,
    cust.from_number as telefone_cliente,
    c.classificacao as categoria_principal,
    c.classificacao_especifica as categoria_especifica,
    c.confianca,
    c.data_classificacao,
    c.sugestao_melhoria
FROM classificacoes c
LEFT JOIN customers cust ON c.user_id = cust.id::text
WHERE c.classificacao LIKE '%Dúvidas sobre certificado%'
    AND c.classificacao_especifica IS NOT NULL
    AND c.classificacao_especifica != ''
ORDER BY c.data_classificacao DESC; 