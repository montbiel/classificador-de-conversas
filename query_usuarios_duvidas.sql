-- =====================================================
-- QUERY: USUÁRIOS COM TAGS DE DÚVIDA
-- =====================================================

-- QUERY PRINCIPAL: Buscar usuários com tags de dúvida
SELECT 
    c.user_id,
    c.wa_id,
    c.classificacao as tag_principal,
    c.classificacao_especifica as tag_especifica,
    c.confianca,
    c.data_classificacao,
    c.contexto as mensagens_analisadas
FROM classificacoes c
WHERE c.classificacao LIKE '%Dúvidas%'
    AND c.classificacao != 'Erro na classificação'
ORDER BY c.data_classificacao DESC;

-- QUERY ALTERNATIVA: Com contagem de mensagens analisadas
SELECT 
    c.user_id,
    c.wa_id,
    c.classificacao as tag_principal,
    c.classificacao_especifica as tag_especifica,
    c.confianca,
    c.data_classificacao,
    c.contexto as mensagens_analisadas,
    LENGTH(c.contexto) as tamanho_contexto,
    COUNT(*) OVER (PARTITION BY c.classificacao) as total_por_tag
FROM classificacoes c
WHERE c.classificacao LIKE '%Dúvidas%'
    AND c.classificacao != 'Erro na classificação'
ORDER BY c.data_classificacao DESC;

-- QUERY RESUMO: Contagem por tipo de dúvida
SELECT 
    c.classificacao as tag_principal,
    c.classificacao_especifica as tag_especifica,
    COUNT(*) as quantidade,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM classificacoes WHERE classificacao LIKE '%Dúvidas%'), 2) as percentual
FROM classificacoes c
WHERE c.classificacao LIKE '%Dúvidas%'
    AND c.classificacao != 'Erro na classificação'
GROUP BY c.classificacao, c.classificacao_especifica
ORDER BY quantidade DESC;

-- QUERY DETALHADA: Com informações do customer e mensagens reais
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