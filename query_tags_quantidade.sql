-- =====================================================
-- QUERIES PARA ANÁLISE DE TAGS E CLASSIFICAÇÕES
-- =====================================================

-- QUERY 1: Tags principais (classificações) e suas quantidades
SELECT 
    classificacao,
    COUNT(*) as quantidade,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM classificacoes), 2) as percentual
FROM classificacoes 
WHERE classificacao IS NOT NULL 
    AND classificacao != 'Erro na classificação'
GROUP BY classificacao 
ORDER BY quantidade DESC;

-- QUERY 2: Tags específicas e suas quantidades
SELECT 
    classificacao_especifica,
    COUNT(*) as quantidade,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM classificacoes WHERE classificacao_especifica IS NOT NULL), 2) as percentual
FROM classificacoes 
WHERE classificacao_especifica IS NOT NULL 
    AND classificacao_especifica != ''
GROUP BY classificacao_especifica 
ORDER BY quantidade DESC;

-- QUERY 3: Combinação de tags principais e específicas
SELECT 
    classificacao as tag_principal,
    classificacao_especifica as tag_especifica,
    COUNT(*) as quantidade
FROM classificacoes 
WHERE classificacao IS NOT NULL 
    AND classificacao != 'Erro na classificação'
    AND classificacao_especifica IS NOT NULL 
    AND classificacao_especifica != ''
GROUP BY classificacao, classificacao_especifica 
ORDER BY quantidade DESC;

-- QUERY 4: Resumo geral das classificações
SELECT 
    'Total de classificações' as tipo,
    COUNT(*) as quantidade
FROM classificacoes
UNION ALL
SELECT 
    'Classificações com sucesso' as tipo,
    COUNT(*) as quantidade
FROM classificacoes 
WHERE classificacao != 'Erro na classificação'
UNION ALL
SELECT 
    'Classificações com erro' as tipo,
    COUNT(*) as quantidade
FROM classificacoes 
WHERE classificacao = 'Erro na classificação'
UNION ALL
SELECT 
    'Com tags específicas' as tipo,
    COUNT(*) as quantidade
FROM classificacoes 
WHERE classificacao_especifica IS NOT NULL 
    AND classificacao_especifica != '';

-- QUERY 5: Top 10 tags específicas mais frequentes
SELECT 
    classificacao_especifica,
    COUNT(*) as quantidade,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM classificacoes WHERE classificacao_especifica IS NOT NULL), 2) as percentual
FROM classificacoes 
WHERE classificacao_especifica IS NOT NULL 
    AND classificacao_especifica != ''
GROUP BY classificacao_especifica 
ORDER BY quantidade DESC
LIMIT 10;

-- QUERY 6: Distribuição por confiança das classificações
SELECT 
    CASE 
        WHEN confianca >= 0.9 THEN 'Alta confiança (90-100%)'
        WHEN confianca >= 0.7 THEN 'Média-alta confiança (70-89%)'
        WHEN confianca >= 0.5 THEN 'Média confiança (50-69%)'
        WHEN confianca > 0 THEN 'Baixa confiança (1-49%)'
        ELSE 'Sem confiança (0%)'
    END as nivel_confianca,
    COUNT(*) as quantidade
FROM classificacoes 
WHERE classificacao != 'Erro na classificação'
GROUP BY 
    CASE 
        WHEN confianca >= 0.9 THEN 'Alta confiança (90-100%)'
        WHEN confianca >= 0.7 THEN 'Média-alta confiança (70-89%)'
        WHEN confianca >= 0.5 THEN 'Média confiança (50-69%)'
        WHEN confianca > 0 THEN 'Baixa confiança (1-49%)'
        ELSE 'Sem confiança (0%)'
    END
ORDER BY quantidade DESC; 