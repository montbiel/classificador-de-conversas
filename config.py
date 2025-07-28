#!/usr/bin/env python3
"""
Configurações do sistema de classificação de conversas
"""

import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações do Banco de Dados
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+asyncpg://postgres:12345678@127.0.0.1:5432/redfine_core')

# Configurações da OpenAI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'sua_chave_api_aqui')
OPENAI_MODEL = "gpt-4o-mini"
OPENAI_MAX_TOKENS = 150
OPENAI_TEMPERATURE = 0.3
OPENAI_TIMEOUT = 30

# Configurações do Sistema
BATCH_SIZE = 10
DELAY_BETWEEN_REQUESTS = 1.0
MAX_MESSAGES_PER_USER = 25
RETRY_ATTEMPTS = 3
RETRY_DELAY = 5

# Configurações de Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = 'logs/classifier.log'
LOG_MAX_SIZE = '10MB'
LOG_BACKUP_COUNT = 5

# Configurações das Colunas do Banco (adaptadas ao schema real)
CHAT_HISTORY_USER_ID_COLUMN = 'customer_id'  # Coluna real no banco
CHAT_HISTORY_TIMESTAMP_COLUMN = 'message_date'  # Coluna real no banco
CHAT_HISTORY_MESSAGE_COLUMN = 'message'  # Coluna real no banco

# Tags de Classificação Organizadas (sem redundâncias)
CLASSIFICATION_TAGS = [
    # Dúvidas (consolidadas)
    "Dúvidas sobre meio de pagamento",  # inclui boleto, PIX, cartão, parcelamento
    "Dúvidas sobre preço/valor",
    "Dúvidas sobre desconto",
    "Dúvidas sobre curso",  # inclui acesso, conteúdo, duração, horários
    "Dúvidas sobre certificado",
    "Dúvidas sobre matrícula",
    "Dúvidas sobre cancelamento/reembolso",
    "Dúvidas sobre suporte técnico",
    
    # Problemas Financeiros (consolidadas)
    "Problemas financeiros: sem dinheiro",
    "Problemas financeiros: dificuldade financeira",
    "Problemas financeiros: não pode pagar agora",
    "Problemas financeiros: problemas com parcelamento",
    "Problemas financeiros: outros",
    
    # Problemas Técnicos (consolidadas)
    "Problema: site não abre",
    "Problema: link não funciona",
    "Problema: erro no pagamento",  # inclui emissão de boleto
    "Problema: erro no cadastro",
    "Problema: erro no login",
    "Problema: erro no acesso ao curso",
    "Problema: conteúdo não carrega",  # inclui vídeo, material, certificado
    "Problema: área do aluno não funciona",
    "Problema: app não funciona",
    "Problema: sistema lento",
    "Problema: página travou",
    
    # Insatisfação (consolidadas)
    "Não gostou: conteúdo/metodologia",  # inclui conteúdo, metodologia, professor, material
    "Não gostou: plataforma/atendimento",  # inclui plataforma, atendimento, qualidade
    "Não gostou: preço/duração",  # inclui preço, duração
    
    # Insegurança (consolidadas)
    "Insegurança: não se sente preparado",  # inclui falta de experiência
    "Insegurança: medo/desconfiança",  # inclui medo de errar, não confia na empresa, medo de ser enganado
    "Insegurança: dúvidas sobre qualidade/valor",  # inclui dúvidas sobre qualidade, não sabe se vale a pena
    
    # Atendimento (consolidadas)
    "Atendimento: não respondeu/demorou",  # inclui não respondeu, demorou para responder
    "Atendimento: resposta insatisfatória",  # inclui resposta ruim, não resolveu problema
    "Atendimento: não foi atendido",  # inclui transferiu várias vezes
    
    # Outros
    "Outros"
]

# Palavras-chave para cada tag (consolidadas)
TAG_KEYWORDS = {
    # Problemas Financeiros
    "Problemas financeiros: sem dinheiro": [
        "sem dinheiro", "não tenho dinheiro", "sem grana", "não tenho grana", "sem dinheiro para",
        "não tenho dinheiro para", "sem dinheiro para pagar", "não tenho dinheiro para pagar"
    ],
    "Problemas financeiros: dificuldade financeira": [
        "dificuldade financeira", "problema financeiro", "sem recursos", "sem condições econômicas",
        "dificuldades financeiras", "problemas financeiros", "sem condições financeiras"
    ],
    "Problemas financeiros: não pode pagar agora": [
        "não posso pagar agora", "não tenho dinheiro agora", "sem dinheiro agora", "não posso pagar neste momento",
        "sem condições agora", "não tenho condições agora", "não posso pagar neste momento", "não posso pagar por enquanto"
    ],
    "Problemas financeiros: problemas com parcelamento": [
        "problema com parcelamento", "não consigo parcelar", "não aceita parcelamento", "dificuldade para parcelar"
    ],
    "Problemas financeiros: outros": [
        "problema financeiro", "questão financeira", "dificuldade de pagamento", "outro motivo financeiro"
    ],
    
    # Dúvidas (consolidadas)
    "Dúvidas sobre meio de pagamento": [
        "meio de pagamento", "formas de pagamento", "como pagar", "como fazer o pagamento",
        "opções de pagamento", "métodos de pagamento", "qual forma de pagar", "boleto", "pix", 
        "cartão de crédito", "cartão", "parcelamento", "parcelas", "como gerar boleto", 
        "onde está o boleto", "link do boleto", "como fazer pix", "chave pix", "qr code pix"
    ],
    "Dúvidas sobre preço/valor": [
        "quanto custa", "qual o valor", "qual o preço", "valor do curso", "preço do curso",
        "quanto é", "custo", "valor total", "preço total"
    ],
    "Dúvidas sobre desconto": [
        "desconto", "promoção", "oferta", "código de desconto", "cupom", "desconto especial",
        "preço promocional", "oferta especial"
    ],
    "Dúvidas sobre curso": [
        "acesso ao curso", "conteúdo do curso", "duração do curso", "horários", "como acessar o curso",
        "o que tem no curso", "quanto tempo dura", "quando são as aulas", "material do curso"
    ],
    "Dúvidas sobre certificado": [
        "certificado", "como gerar certificado", "onde está o certificado", "certificado não gera",
        "link do certificado", "certificado de conclusão"
    ],
    "Dúvidas sobre matrícula": [
        "matrícula", "como fazer matrícula", "processo de matrícula", "inscrição", "cadastro"
    ],
    "Dúvidas sobre cancelamento/reembolso": [
        "reembolso", "devolução", "cancelamento", "cancelar", "como cancelar", "quero cancelar", "desistir"
    ],
    "Dúvidas sobre suporte técnico": [
        "suporte", "suporte técnico", "ajuda técnica", "problema técnico", "assistência"
    ],
    
    # Problemas Técnicos (consolidadas)
    "Problema: site não abre": [
        "site não abre", "site não carrega", "site não funciona", "página não abre",
        "não consegue acessar o site", "site fora do ar", "site travou", "não consigo acessar a página",
        "página não carrega", "site não está abrindo"
    ],
    "Problema: link não funciona": [
        "link não funciona", "link quebrado", "link não abre", "link não carrega",
        "link não está funcionando", "link inválido"
    ],
    "Problema: erro no pagamento": [
        "erro no pagamento", "pagamento não foi processado", "erro ao pagar",
        "pagamento falhou", "erro na transação", "pagamento não foi aprovado",
        "não conseguiu emitir boleto", "boleto não foi gerado", "erro ao gerar boleto",
        "não consegue gerar boleto", "problema para emitir boleto"
    ],
    "Problema: erro no login": [
        "erro no login", "não consegue fazer login", "login não funciona",
        "senha incorreta", "usuário não encontrado", "erro de acesso"
    ],
    "Problema: erro no acesso ao curso": [
        "não consegue acessar o curso", "erro no acesso ao curso", "curso não carrega",
        "não consegue entrar no curso", "erro ao acessar material"
    ],
    "Problema: conteúdo não carrega": [
        "vídeo não carrega", "vídeo não funciona", "vídeo não abre", "erro no vídeo", "vídeo travou", "vídeo não reproduz",
        "material não baixa", "não consegue baixar", "download não funciona", "erro ao baixar material", "arquivo não baixa",
        "certificado não gera", "certificado não carrega", "certificado não baixa"
    ],
    
    # Insatisfação (consolidadas)
    "Não gostou: conteúdo/metodologia": [
        "não gostei do conteúdo", "não gostou do conteúdo", "conteúdo ruim", "conteúdo não é bom", "conteúdo não agradou",
        "não gostei da metodologia", "não gostou da metodologia", "metodologia ruim", "metodologia não funciona",
        "não gostei do professor", "não gostou do professor", "professor ruim", "professor não explica bem",
        "não gostei do material", "não gostou do material", "material ruim", "material não é bom"
    ],
    "Não gostou: plataforma/atendimento": [
        "não gostei da plataforma", "não gostou da plataforma", "plataforma ruim", "plataforma não funciona bem",
        "não gostei do site", "não gostou do site", "não gostei do atendimento", "não gostou do atendimento",
        "atendimento ruim", "atendimento não é bom", "não gostei do suporte", "não gostou do suporte",
        "qualidade ruim", "qualidade não é boa"
    ],
    "Não gostou: preço/duração": [
        "não gostei do preço", "não gostou do preço", "preço ruim", "preço caro", "preço alto",
        "não gostei da duração", "não gostou da duração", "duração ruim", "duração longa", "duração curta"
    ],
    
    # Insegurança (consolidadas)
    "Insegurança: não se sente preparado": [
        "não me sinto preparado", "não me sinto preparada", "não me sinto capaz",
        "não tenho confiança", "não me sinto seguro", "não me sinto segura", "falta de experiência"
    ],
    "Insegurança: medo/desconfiança": [
        "tenho medo de errar", "medo de cometer erros", "tenho medo de falhar", "não quero errar", "tenho receio de errar",
        "não confio na empresa", "não confio na instituição", "não tenho confiança na empresa",
        "tenho dúvidas sobre a empresa", "não sei se a empresa é boa", "medo de ser enganado"
    ],
    "Insegurança: dúvidas sobre qualidade/valor": [
        "dúvidas sobre qualidade", "não sei se vale a pena", "qualidade não é boa", "não sei se é bom"
    ],
    
    # Atendimento (consolidadas)
    "Atendimento: não respondeu/demorou": [
        "não respondeu minha dúvida", "minha dúvida não foi respondida", "não responderam minha pergunta",
        "não recebi resposta", "não obtive resposta", "não foi respondido",
        "demorou para responder", "demorou muito para responder", "demora no atendimento",
        "atendimento demorado", "resposta demorou", "demorou para me atender"
    ],
    "Atendimento: resposta insatisfatória": [
        "resposta não foi satisfatória", "não ficou satisfeito com a resposta",
        "resposta não resolveu", "não gostou da resposta", "resposta insatisfatória",
        "não resolveu problema", "problema não foi resolvido"
    ],
    "Atendimento: não foi atendido": [
        "não foi atendido", "transferiu várias vezes", "não conseguiu falar com ninguém"
    ]
}

# Prompt para Classificação com Tags Consolidadas
CLASSIFICATION_PROMPT = """
Analise a seguinte conversa de atendimento ao cliente e classifique-a usando uma das tags consolidadas abaixo:

Tags disponíveis:
{}

Conversa para análise:
{}

IMPORTANTE: Use a tag MAIS APROPRIADA que se aplica ao contexto da conversa.

Responda com TRÊS partes separadas por pipe (|):
1. A tag consolidada
2. Uma justificativa abrangente e clara da classificação
3. A CLASSIFICAÇÃO ESPECÍFICA, que deve ser clara e informativa sobre o que aconteceu na conversa:

EXEMPLOS DE CLASSIFICAÇÃO ESPECÍFICA:

DÚVIDAS:
- "Dúvidas sobre meio de pagamento" → classificacao_especifica: "Perguntou sobre formas de pagamento", "Perguntou sobre boleto", "Perguntou sobre PIX", "Perguntou sobre cartão", "Perguntou sobre parcelamento"
- "Dúvidas sobre preço/valor" → classificacao_especifica: "Perguntou quanto custa", "Perguntou sobre o valor", "Perguntou sobre o preço"
- "Dúvidas sobre desconto" → classificacao_especifica: "Perguntou sobre desconto", "Perguntou sobre promoção", "Perguntou sobre cupom"
- "Dúvidas sobre curso" → classificacao_especifica: "Perguntou sobre acesso ao curso", "Perguntou sobre conteúdo do curso", "Perguntou sobre duração do curso", "Perguntou sobre horários"
- "Dúvidas sobre certificado" → classificacao_especifica: "Perguntou sobre certificado", "Solicitou link do certificado", "Perguntou como gerar certificado"
- "Dúvidas sobre matrícula" → classificacao_especifica: "Perguntou sobre matrícula", "Perguntou sobre inscrição", "Perguntou sobre cadastro"
- "Dúvidas sobre cancelamento/reembolso" → classificacao_especifica: "Perguntou sobre cancelamento", "Perguntou sobre reembolso", "Quer cancelar o curso"
- "Dúvidas sobre suporte técnico" → classificacao_especifica: "Perguntou sobre suporte", "Perguntou sobre ajuda técnica"

PROBLEMAS FINANCEIROS:
- "Problemas financeiros: sem dinheiro" → classificacao_especifica: "Está desempregado", "Sem renda", "Sem dinheiro para pagar", "Endividado"
- "Problemas financeiros: dificuldade financeira" → classificacao_especifica: "Dificuldade financeira", "Sem condições econômicas", "Problemas financeiros"
- "Problemas financeiros: não pode pagar agora" → classificacao_especifica: "Não pode pagar agora", "Momento difícil", "Sem dinheiro no momento"
- "Problemas financeiros: problemas com parcelamento" → classificacao_especifica: "Problema com parcelamento", "Não aceita parcelamento", "Limite excedido"
- "Problemas financeiros: outros" → classificacao_especifica: "Outro problema financeiro", "Questão financeira específica"

PROBLEMAS TÉCNICOS:
- "Problema: site não abre" → classificacao_especifica: "Site fora do ar", "Site não carrega", "Página não abre"
- "Problema: link não funciona" → classificacao_especifica: "Link quebrado", "Link não funciona", "Link inválido"
- "Problema: erro no pagamento" → classificacao_especifica: "Erro no pagamento", "Pagamento falhou", "Boleto não foi gerado"
- "Problema: erro no cadastro" → classificacao_especifica: "Erro no cadastro", "Problema para se cadastrar"
- "Problema: erro no login" → classificacao_especifica: "Erro no login", "Não consegue fazer login", "Senha incorreta"
- "Problema: erro no acesso ao curso" → classificacao_especifica: "Não consegue acessar o curso", "Erro no acesso ao curso"
- "Problema: conteúdo não carrega" → classificacao_especifica: "Vídeo não carrega", "Material não baixa", "Certificado não gera", "Ebook não baixa"
- "Problema: área do aluno não funciona" → classificacao_especifica: "Área do aluno não funciona", "Portal do aluno com problema"
- "Problema: app não funciona" → classificacao_especifica: "App não funciona", "Aplicativo com problema"
- "Problema: sistema lento" → classificacao_especifica: "Sistema lento", "Plataforma lenta"
- "Problema: página travou" → classificacao_especifica: "Página travou", "Site travou"

INSATISFAÇÃO:
- "Não gostou: conteúdo/metodologia" → classificacao_especifica: "Não gostou do conteúdo", "Não gostou da metodologia", "Não gostou do professor", "Não gostou do material"
- "Não gostou: plataforma/atendimento" → classificacao_especifica: "Não gostou da plataforma", "Não gostou do atendimento", "Não gostou da qualidade"
- "Não gostou: preço/duração" → classificacao_especifica: "Não gostou do preço", "Não gostou da duração", "Preço caro", "Duração inadequada"

INSEGURANÇA:
- "Insegurança: não se sente preparado" → classificacao_especifica: "Não se sente preparado", "Falta de experiência", "Não se sente capaz"
- "Insegurança: medo/desconfiança" → classificacao_especifica: "Medo de errar", "Não confia na empresa", "Medo de ser enganado"
- "Insegurança: dúvidas sobre qualidade/valor" → classificacao_especifica: "Dúvidas sobre qualidade", "Não sabe se vale a pena"

ATENDIMENTO:
- "Atendimento: não respondeu/demorou" → classificacao_especifica: "Não respondeu dúvida", "Demorou para responder", "Sem resposta"
- "Atendimento: resposta insatisfatória" → classificacao_especifica: "Resposta insatisfatória", "Não resolveu problema", "Problema não resolvido"
- "Atendimento: não foi atendido" → classificacao_especifica: "Não foi atendido", "Transferiu várias vezes"

OUTROS:
- "Outros" → classificacao_especifica: "Apenas conversou", "Informações gerais", "Agradecimento", "Cumprimento", "Sem problema específico"

REGRAS IMPORTANTES:
- A classificação específica deve ser CLARA e INFORMATIVA
- Deve deixar óbvio o que aconteceu na conversa
- EVITE redundância com a tag principal
- Use linguagem simples e direta
- Foque no que aconteceu especificamente
- Seja abrangente na justificativa, mas específico na classificação

Exemplo de resposta:
- Outros|Cliente conversou sobre assuntos diversos sem problema específico|apenas conversou
- Problemas financeiros: sem dinheiro|Cliente relatou estar desempregado e sem condições de pagar|está desempregado
- Dúvidas sobre certificado|Cliente perguntou sobre como obter o certificado do curso|perguntou sobre certificado
- Problemas técnicos: conteúdo não carrega|Cliente não consegue baixar o Ebook do curso|Ebook não baixa
- Não gostou: conteúdo/metodologia|Cliente expressou insatisfação com a qualidade do conteúdo|não gostou do conteúdo
- Insegurança: não se sente preparado|Cliente demonstrou falta de confiança em suas capacidades|não se sente preparado
- Atendimento: não respondeu/demorou|Cliente não obteve resposta para sua dúvida|não respondeu dúvida
""" 