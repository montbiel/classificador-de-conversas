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

# Tags de Classificação Específicas
CLASSIFICATION_TAGS = [
    # Problemas Financeiros Específicos (unificados e organizados)
    "Problemas financeiros: sem dinheiro",  # ausência total de dinheiro
    "Problemas financeiros: dificuldade financeira",  # dificuldades financeiras em geral
    "Problemas financeiros: não pode pagar agora",  # impossibilidade momentânea
    "Problemas financeiros: problemas com parcelamento",  # dificuldade em parcelar
    "Problemas financeiros: outros",  # casos financeiros não previstos acima
    
    # Dúvidas Específicas
    "Dúvidas sobre meio de pagamento",
    "Dúvidas sobre boleto",
    "Dúvidas sobre cartão de crédito",
    "Dúvidas sobre PIX",
    "Dúvidas sobre parcelamento",
    "Dúvidas sobre preço/valor",
    "Dúvidas sobre desconto",
    "Dúvidas sobre reembolso",
    "Dúvidas sobre cancelamento",
    "Dúvidas sobre matrícula",
    "Dúvidas sobre acesso ao curso",
    "Dúvidas sobre certificado",
    "Dúvidas sobre conteúdo do curso",
    "Dúvidas sobre duração do curso",
    "Dúvidas sobre horários",
    "Dúvidas sobre suporte técnico",
    
    # Problemas com Plataforma
    "Problema: site não abre",
    "Problema: link não funciona",
    "Problema: não conseguiu emitir boleto",
    "Problema: erro no pagamento",
    "Problema: erro no cadastro",
    "Problema: erro no login",
    "Problema: erro no acesso ao curso",
    "Problema: vídeo não carrega",
    "Problema: material não baixa",
    "Problema: certificado não gera",
    "Problema: área do aluno não funciona",
    "Problema: app não funciona",
    "Problema: sistema lento",
    "Problema: página travou",
    
    # Insatisfação Específica
    "Não gostou: conteúdo do curso",
    "Não gostou: metodologia",
    "Não gostou: professor",
    "Não gostou: material didático",
    "Não gostou: plataforma",
    "Não gostou: atendimento",
    "Não gostou: qualidade do curso",
    "Não gostou: duração do curso",
    "Não gostou: preço do curso",
    
    # Insegurança Específica
    "Insegurança: não se sente preparado",
    "Insegurança: medo de errar",
    "Insegurança: falta de experiência",
    "Insegurança: não confia na empresa",
    "Insegurança: medo de ser enganado",
    "Insegurança: dúvidas sobre qualidade",
    "Insegurança: não sabe se vale a pena",
    
    # Atendimento
    "Atendimento: não respondeu dúvida",
    "Atendimento: demorou para responder",
    "Atendimento: resposta insatisfatória",
    "Atendimento: não foi atendido",
    "Atendimento: transferiu várias vezes",
    "Atendimento: não resolveu problema",
    
    # Outros
    "Outros"
]

# Palavras-chave específicas para cada tag (problemas financeiros unificados)
TAG_KEYWORDS = {
    # Problemas Financeiros Específicos
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
    
    # Dúvidas Específicas
    "Dúvidas sobre meio de pagamento": [
        "meio de pagamento", "formas de pagamento", "como pagar", "como fazer o pagamento",
        "opções de pagamento", "métodos de pagamento", "qual forma de pagar"
    ],
    "Dúvidas sobre boleto": [
        "boleto", "como gerar boleto", "onde está o boleto", "boleto não chegou", "boleto não foi enviado",
        "link do boleto", "boleto bancário", "como pagar o boleto"
    ],
    "Dúvidas sobre cartão de crédito": [
        "cartão de crédito", "cartão", "parcelamento", "parcelas", "quantas parcelas",
        "limite do cartão", "cartão não passou", "erro no cartão"
    ],
    "Dúvidas sobre PIX": [
        "pix", "pix não funcionou", "como fazer pix", "chave pix", "qr code pix",
        "pix não foi confirmado", "pix não chegou"
    ],
    "Dúvidas sobre preço/valor": [
        "quanto custa", "qual o valor", "qual o preço", "valor do curso", "preço do curso",
        "quanto é", "custo", "valor total", "preço total"
    ],
    "Dúvidas sobre desconto": [
        "desconto", "promoção", "oferta", "código de desconto", "cupom", "desconto especial",
        "preço promocional", "oferta especial"
    ],
    
    # Problemas com Plataforma
    "Problema: site não abre": [
        "site não abre", "site não carrega", "site não funciona", "página não abre",
        "não consegue acessar o site", "site fora do ar", "site travou", "não consigo acessar a página",
        "página não carrega", "site não está abrindo"
    ],
    "Problema: link não funciona": [
        "link não funciona", "link quebrado", "link não abre", "link não carrega",
        "link não está funcionando", "link inválido"
    ],
    "Problema: não conseguiu emitir boleto": [
        "não conseguiu emitir boleto", "boleto não foi gerado", "erro ao gerar boleto",
        "não consegue gerar boleto", "problema para emitir boleto"
    ],
    "Problema: erro no pagamento": [
        "erro no pagamento", "pagamento não foi processado", "erro ao pagar",
        "pagamento falhou", "erro na transação", "pagamento não foi aprovado"
    ],
    "Problema: erro no login": [
        "erro no login", "não consegue fazer login", "login não funciona",
        "senha incorreta", "usuário não encontrado", "erro de acesso"
    ],
    "Problema: erro no acesso ao curso": [
        "não consegue acessar o curso", "erro no acesso ao curso", "curso não carrega",
        "não consegue entrar no curso", "erro ao acessar material"
    ],
    "Problema: vídeo não carrega": [
        "vídeo não carrega", "vídeo não funciona", "vídeo não abre",
        "erro no vídeo", "vídeo travou", "vídeo não reproduz"
    ],
    "Problema: material não baixa": [
        "material não baixa", "não consegue baixar", "download não funciona",
        "erro ao baixar material", "arquivo não baixa"
    ],
    
    # Insatisfação Específica
    "Não gostou: conteúdo do curso": [
        "não gostei do conteúdo", "não gostou do conteúdo", "conteúdo ruim",
        "conteúdo não é bom", "conteúdo não agradou", "conteúdo não atendeu"
    ],
    "Não gostou: metodologia": [
        "não gostei da metodologia", "não gostou da metodologia", "metodologia ruim",
        "metodologia não funciona", "não gostei da didática", "não gostou da didática"
    ],
    "Não gostou: professor": [
        "não gostei do professor", "não gostou do professor", "professor ruim",
        "professor não explica bem", "professor não é bom"
    ],
    "Não gostou: plataforma": [
        "não gostei da plataforma", "não gostou da plataforma", "plataforma ruim",
        "plataforma não funciona bem", "não gostei do site", "não gostou do site"
    ],
    "Não gostou: atendimento": [
        "não gostei do atendimento", "não gostou do atendimento", "atendimento ruim",
        "atendimento não é bom", "não gostei do suporte", "não gostou do suporte"
    ],
    
    # Insegurança Específica
    "Insegurança: não se sente preparado": [
        "não me sinto preparado", "não me sinto preparada", "não me sinto capaz",
        "não tenho confiança", "não me sinto seguro", "não me sinto segura"
    ],
    "Insegurança: medo de errar": [
        "tenho medo de errar", "medo de cometer erros", "tenho medo de falhar",
        "não quero errar", "tenho receio de errar"
    ],
    "Insegurança: não confia na empresa": [
        "não confio na empresa", "não confio na instituição", "não tenho confiança na empresa",
        "tenho dúvidas sobre a empresa", "não sei se a empresa é boa"
    ],
    
    # Atendimento
    "Atendimento: não respondeu dúvida": [
        "não respondeu minha dúvida", "minha dúvida não foi respondida", "não responderam minha pergunta",
        "não recebi resposta", "não obtive resposta", "não foi respondido"
    ],
    "Atendimento: demorou para responder": [
        "demorou para responder", "demorou muito para responder", "demora no atendimento",
        "atendimento demorado", "resposta demorou", "demorou para me atender"
    ],
    "Atendimento: resposta insatisfatória": [
        "resposta não foi satisfatória", "não ficou satisfeito com a resposta",
        "resposta não resolveu", "não gostou da resposta", "resposta insatisfatória"
    ]
}

# Prompt para Classificação com Tags Específicas
CLASSIFICATION_PROMPT = """
Analise a seguinte conversa de atendimento ao cliente e classifique-a usando uma das tags específicas abaixo:

Tags disponíveis:
{}

Conversa para análise:
{}

IMPORTANTE: Use a tag MAIS ESPECÍFICA que se aplica ao contexto da conversa.

Responda com TRÊS partes separadas por pipe (|):
1. A tag específica
2. Uma breve justificativa da classificação
3. O MOTIVO COMPLEMENTAR, que adicione informações úteis SEM REPETIR a tag principal. Use apenas um termo curto e específico:

EXEMPLOS DE CLASSIFICAÇÃO ESPECÍFICA COMPLEMENTAR:

PROBLEMAS FINANCEIROS:
- "Problemas financeiros: sem dinheiro" → classificacao_especifica: "desempregado", "sem renda", "endividado"
- "Problemas financeiros: dificuldade financeira" → classificacao_especifica: "sem condições", "endividado", "dificuldade"
- "Problemas financeiros: não pode pagar agora" → classificacao_especifica: "momento difícil", "sem dinheiro agora", "não pode agora"
- "Problemas financeiros: problemas com parcelamento" → classificacao_especifica: "não aceita parcelamento", "limite excedido"

DÚVIDAS:
- "Dúvidas sobre meio de pagamento" → classificacao_especifica: "como pagar", "formas disponíveis", "opções"
- "Dúvidas sobre boleto" → classificacao_especifica: "não recebeu", "vencido", "problema"
- "Dúvidas sobre preço/valor" → classificacao_especifica: "quanto custa" (SEMPRE usar esta expressão)
- "Dúvidas sobre certificado" → classificacao_especifica: "solicitou link", "não gera", "problema"
- "Dúvidas sobre parcelamento" → classificacao_especifica: "parcelamento" (SEMPRE usar esta expressão)
- "Dúvidas sobre acesso ao curso" → classificacao_especifica: "acesso curso" (SEMPRE usar esta expressão)
- "Dúvidas sobre conteúdo do curso" → classificacao_especifica: "conteúdo curso" (SEMPRE usar esta expressão)

PROBLEMAS TÉCNICOS:
- "Problema: site não abre" → classificacao_especifica: "fora do ar", "não carrega", "erro"
- "Problema: certificado não gera" → classificacao_especifica: "erro", "não gera", "problema"
- "Problema: erro no pagamento" → classificacao_especifica: "falhou", "negado", "erro"

INSATISFAÇÃO:
- "Não gostou: conteúdo do curso" → classificacao_especifica: "ruim", "não gostou", "insatisfeito"
- "Não gostou: atendimento" → classificacao_especifica: "ruim", "não gostou", "insatisfeito"

ATENDIMENTO:
- "Atendimento: não respondeu dúvida" → classificacao_especifica: "sem resposta", "não respondeu", "ignorado"
- "Atendimento: não resolveu problema" → classificacao_especifica: "não resolveu", "problema não resolvido", "insatisfeito"

OUTROS:
- "Outros" → classificacao_especifica: "apenas conversou", "informações gerais", "sem problema específico"

REGRAS IMPORTANTES:
- NÃO repita palavras que já estão na tag principal
- A classificação específica deve COMPLEMENTAR, não repetir
- Use termos curtos e objetivos
- Foque no que aconteceu especificamente

Exemplo de resposta:
- Outros|Cliente conversou sobre assuntos diversos|apenas conversou
- Problemas financeiros: sem dinheiro|Cliente relatou está desempregado|desempregado
- Dúvidas sobre certificado|Cliente solicitou link para certificado|solicitou link
- Atendimento: não respondeu dúvida|Cliente não obteve resposta|sem resposta
""" 