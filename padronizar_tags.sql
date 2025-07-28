-- =====================================================
-- PADRONIZAÇÃO DE TAGS - VERSÃO ESSENCIAL
-- =====================================================

-- ATUALIZAÇÃO 1: Padronizar tags de problemas financeiros
UPDATE classificacoes 
SET classificacao_especifica = 'sem recursos financeiros'
WHERE classificacao_especifica IN (
    'sem dinheiro agora', 'sem dinheiro', 'sem recursos', 'sem condições'
);

-- ATUALIZAÇÃO 2: Padronizar tags de desemprego
UPDATE classificacoes 
SET classificacao_especifica = 'sem emprego'
WHERE classificacao_especifica IN (
    'desempregado', 'desempregada', 'sem renda'
);

-- ATUALIZAÇÃO 3: Padronizar tags de formas de pagamento
UPDATE classificacoes 
SET classificacao_especifica = 'formas de pagamento'
WHERE classificacao_especifica IN (
    'opções', 'opções disponíveis', 'formas disponíveis', 'opções de pagamento'
);

-- ATUALIZAÇÃO 4: Padronizar tags de erros de geração
UPDATE classificacoes 
SET classificacao_especifica = 'erro de geração'
WHERE classificacao_especifica IN (
    'não gera', 'não gerou', 'não conseguiu gerar'
);

-- ATUALIZAÇÃO 5: Padronizar tags de erros de acesso
UPDATE classificacoes 
SET classificacao_especifica = 'erro de acesso'
WHERE classificacao_especifica IN (
    'não abre', 'não conseguiu abrir', 'não conseguiu acessar', 'dificuldades de acesso'
);

-- ATUALIZAÇÃO 6: Padronizar tags de preço/valor
UPDATE classificacoes 
SET classificacao_especifica = 'consulta de preço'
WHERE classificacao_especifica IN (
    'quanto custa', 'preços populares', 'valor alto'
);

-- ATUALIZAÇÃO 7: Padronizar tags de parcelamento
UPDATE classificacoes 
SET classificacao_especifica = 'parcelamento'
WHERE classificacao_especifica IN (
    'parcelamento disponível', 'opções de parcelamento'
);

-- ATUALIZAÇÃO 8: Padronizar tags de certificado
UPDATE classificacoes 
SET classificacao_especifica = 'não consegue gerar certificado'
WHERE classificacao_especifica IN (
    'não gera', 'não gerou', 'certificado não gera'
);

-- ATUALIZAÇÃO 9: Padronizar tags de boleto
UPDATE classificacoes 
SET classificacao_especifica = 'problema boleto'
WHERE classificacao_especifica IN (
    'não conseguiu gerar', 'problema com boleto', 'erro no boleto'
);

-- ATUALIZAÇÃO 10: Padronizar tags de conteúdo do curso
UPDATE classificacoes 
SET classificacao_especifica = 'dúvida conteúdo'
WHERE classificacao_especifica IN (
    'conteúdo curso', 'não entendeu', 'material complementar'
);

-- ATUALIZAÇÃO 11: Padronizar tags de acesso ao curso
UPDATE classificacoes 
SET classificacao_especifica = 'problema acesso'
WHERE classificacao_especifica IN (
    'acesso curso', 'não conseguiu acessar', 'dificuldades de acesso'
);

-- ATUALIZAÇÃO 12: Padronizar tags de "Outros" - APENAS ESSENCIAIS
UPDATE classificacoes 
SET classificacao_especifica = 'OPTOUT'
WHERE classificacao_especifica IN (
    'cancelar envios', 'cancelamento de mensagens', 'cancelar participação', 'cancelou inscrição'
);

UPDATE classificacoes 
SET classificacao_especifica = 'sem interesse'
WHERE classificacao_especifica IN (
    'sem interesse', 'não vai participar', 'não quer mais', 'não quer pagar'
);

UPDATE classificacoes 
SET classificacao_especifica = 'problema técnico'
WHERE classificacao_especifica IN (
    'Tag não reconhecida pelo sistema', 'problema', 'erro', 'erro no sistema'
);

-- ATUALIZAÇÃO 13: Padronizar tags de insegurança
UPDATE classificacoes 
SET classificacao_especifica = 'falta de confiança'
WHERE classificacao_especifica IN (
    'medo de errar', 'muito medo', 'medo de não conseguir', 'medo de dirigir'
);

UPDATE classificacoes 
SET classificacao_especifica = 'dúvidas sobre capacidade'
WHERE classificacao_especifica IN (
    'dúvidas sobre qualidade', 'dúvidas sobre depressão', 'dúvidas sobre capacidade'
);

-- ATUALIZAÇÃO 14: Padronizar tags de atendimento
UPDATE classificacoes 
SET classificacao_especifica = 'insatisfação atendimento'
WHERE classificacao_especifica IN (
    'insatisfeito', 'problema não resolvido', 'não resolveu'
);

-- VERIFICAÇÃO: Mostrar resultado da padronização
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
ORDER BY quantidade DESC
LIMIT 20; 