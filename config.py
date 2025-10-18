import os

class Config:
    # Essas variáveis serão configuradas no Railway
    API_ID = int(os.getenv('API_ID', '12345678'))
    API_HASH = os.getenv('API_HASH', 'abc123def456')
    PHONE_NUMBER = os.getenv('PHONE_NUMBER', '+5511999999999')
    BOT_TOKEN = os.getenv('BOT_TOKEN', 'seu_bot_token')
    USER_ID = int(os.getenv('USER_ID', '123456789'))
    
    # Palavras-chave para monitorar
    KEYWORDS = [keyword.strip().lower() for keyword in os.getenv('KEYWORDS', 'oferta,promoção,desconto').split(',')]
    
    # Canais para monitorar - ADICIONE AQUI OS @username DOS CANAIS
    CHANNELS = [
        '@canal_ofertas1',
        '@canal_ofertas2',
        '@promocoes_brasil'
        # Adicione mais canais aqui
    ]

config = Config()
