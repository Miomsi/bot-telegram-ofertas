from telethon import TelegramClient, events
from telethon.sessions import StringSession
import os
from config import config
from handlers import send_alert

class TelegramMonitor:
    def __init__(self):
        # Usar sessão string para autenticação no Railway
        session_string = os.getenv('SESSION_STRING')
        if not session_string:
            raise ValueError("❌ SESSION_STRING não configurada!")
            
        print("🔐 Configurando cliente com sessão...")
        self.client = TelegramClient(
            StringSession(session_string),
            config.API_ID,
            config.API_HASH
        )
        
    async def start(self):
        print("🔄 Iniciando conexão...")
        
        # Importante: não passar phone number quando usar session string
        await self.client.start()
        
        print("✅ Monitor autenticado com sucesso!")
        print(f"📡 Monitorando {len(config.CHANNELS)} canais")
        print(f"🔍 Palavras-chave: {', '.join(config.KEYWORDS)}")
        
        # Verificar se está conectado
        if await self.client.is_user_authorized():
            me = await self.client.get_me()
            print(f"👤 Conectado como: {me.first_name}")
        else:
            print("❌ Não autorizado - verifique a SESSION_STRING")
            return
        
        # Lista os canais que está monitorando
        print("📋 Canais monitorados:")
        for channel in config.CHANNELS:
            print(f"   👁️  {channel}")
        
        # Configurar handler de mensagens
        self.client.add_event_handler(
            self.handle_new_message,
            events.NewMessage(chats=config.CHANNELS)
        )
        
        print("🚀 Monitoramento ativo! Aguardando mensagens...")
        await self.client.run_until_disconnected()
    
    async def handle_new_message(self, event):
        message = event.message
        if not message.text:
            return
            
        message_text = message.text.lower()
        channel_name = await self.get_channel_name(message.chat_id)
        
        print(f"📨 Nova mensagem de {channel_name}")
        
        for keyword in config.KEYWORDS:
            if keyword in message_text:
                print(f"🔔 Palavra-chave '{keyword}' detectada!")
                await self.process_alert(message, keyword, channel_name)
                break
    
    async def process_alert(self, message, keyword: str, channel_name: str):
        try:
            alert_data = {
                'channel': channel_name,
                'message': message.text,
                'keyword': keyword,
                'message_id': message.id,
                'date': message.date.isoformat()
            }
            
            await send_alert(alert_data)
            print(f"✅ Alerta enviado para o Telegram!")
            
        except Exception as e:
            print(f"❌ Erro ao processar alerta: {e}")
    
    async def get_channel_name(self, chat_id):
        try:
            entity = await self.client.get_entity(chat_id)
            return getattr(entity, 'title', f'Canal_{chat_id}') or getattr(entity, 'username', f'Canal_{chat_id}')
        except:
            return f'Canal_{chat_id}'
