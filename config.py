import os

class Config:
    # Telethon
    API_ID = int(os.getenv('API_ID', '29971858'))
    API_HASH = os.getenv('API_HASH', 'e123a63fbaee45f82e518a55Bde4cecb')
    PHONE_NUMBER = os.getenv('PHONE_NUMBER', '+5591983718772')
    
    # Bot
    BOT_TOKEN = os.getenv('BOT_TOKEN', '7639172116:AMM7XvC_1hpVdN9WxcjBrqi1RciHYoofA')
    USER_ID = int(os.getenv('USER_ID', '123456789'))
    
    # Monitoramento
    KEYWORDS = [keyword.strip().lower() for keyword in os.getenv('KEYWORDS', '5070,4070').split(',')]
    
    # ⚠️ CANAIS PARA MONITORAR - ADICIONE SEUS LINKS AQUI ⚠️
    CHANNELS = [
        'https://t.me/terabyteshopoficial',  # TERABYTE - JÁ ADICIONADO

        # ⬇️⬇️⬇️ ADICIONE MAIS CANAIS AQUI ⬇️⬇️⬇️
        # 'https://t.me/nomedocanal',
        # 'https://t.me/outrocanal',
    ]

config = Config()
