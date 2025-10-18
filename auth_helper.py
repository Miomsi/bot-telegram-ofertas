import os
from telethon import TelegramClient
from telethon.sessions import StringSession

async def generate_session_string():
    """Gera string de sessão para usar no Railway"""
    API_ID = int(os.getenv('API_ID'))
    API_HASH = os.getenv('API_HASH')
    
    client = TelegramClient(StringSession(), API_ID, API_HASH)
    await client.start(phone=os.getenv('PHONE_NUMBER'))
    
    print("=" * 50)
    print("SESSION_STRING gerada com sucesso!")
    print("ADICIONE esta variável no Railway:")
    print("=" * 50)
    print(client.session.save())
    print("=" * 50)
    
    await client.disconnect()

if __name__ == "__main__":
    import asyncio
    asyncio.run(generate_session_string())
