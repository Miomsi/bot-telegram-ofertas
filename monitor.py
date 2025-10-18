from telethon import TelegramClient, events
from config import config
from handlers import send_alert

class TelegramMonitor:
    def __init__(self):
        self.client = TelegramClient(
            'monitor_session',
            config.API_ID,
            config.API_HASH
        )
        
    async def start(self):
        await self.client.start(phone=config.PHONE_NUMBER)
        print("✅ Monitor iniciado com sucesso!")
        print(f"📡 Monitorando {len(config.CHANNELS)} canais")
        print(f"🔍 Palavras-chave: {', '.join(config.KEYWORDS)}")
        
        self.client.add_event_handler(
            self.handle_new_message,
            events.NewMessage(chats=config.CHANNELS)
        )
        
        await self.client.run_until_disconnected()
    
    async def handle_new_message(self, event):
        message = event.message
        if not message.text:
            return
            
        message_text = message.text.lower()
        
        for keyword in config.KEYWORDS:
            if keyword in message_text:
                print(f"🔔 Palavra-chave detectada: {keyword}")
                await self.process_alert(message, keyword)
                break
    
    async def process_alert(self, message, keyword: str):
        try:
            alert_data = {
                'channel': await self.get_channel_name(message.chat_id),
                'message': message.text,
                'keyword': keyword,
                'message_id': message.id,
                'date': message.date.isoformat()
            }
            
            await send_alert(alert_data)
            
        except Exception as e:
            print(f"❌ Erro ao processar alerta: {e}")
    
    async def get_channel_name(self, chat_id):
        try:
            entity = await self.client.get_entity(chat_id)
            return getattr(entity, 'title', f'Canal_{chat_id}') or getattr(entity, 'username', f'Canal_{chat_id}')
        except:
            return f'Canal_{chat_id}'
