from telethon import TelegramClient, events
from telethon.sessions import StringSession
import os
import asyncio
from config import config
from handlers import send_alert

class TelegramMonitor:
    def __init__(self):
        self.session_string = os.getenv('SESSION_STRING')
        if not self.session_string:
            raise ValueError("❌ SESSION_STRING não configurada!")
        
        self.client = TelegramClient(
            StringSession(self.session_string),
            config.API_ID,
            config.API_HASH
        )
        
    async def start(self):
        print("🚀 Iniciando monitor do Telegram...")
        
        # Conexão direta sem interação
        await self.client.connect()
        
        if not await self.client.is_user_authorized():
            print("❌ Falha na autenticação. Recriando sessão...")
            await self.recreate_session()
            return
        
        # Sucesso!
        me = await self.client.get_me()
        print(f"✅ Conectado como: {me.first_name}")
        print(f"📡 Canais: {len(config.CHANNELS)} | Palavras: {len(config.KEYWORDS)}")
        
        # Registrar handler
        self.client.add_event_handler(
            self.handle_new_message,
            events.NewMessage(chats=config.CHANNELS)
        )
        
        print("🎯 Monitoramento ativo!")
        await self.client.run_until_disconnected()
    
    async def recreate_session(self):
        """Tenta recriar a sessão se a atual estiver inválida"""
        print("🔄 Tentando recriar sessão...")
        try:
            # Isso vai falar mas vai nos dar mais informações
            await self.client.start(phone=config.PHONE_NUMBER)
        except Exception as e:
            print(f"❌ Erro detalhado: {e}")
            print("💡 Dica: Gere uma NOVA session string")
    
    async def handle_new_message(self, event):
        if not event.message.text:
            return
            
        text = event.message.text.lower()
        for keyword in config.KEYWORDS:
            if keyword in text:
                channel = await self.get_channel_name(event.message.chat_id)
                print(f"🔔 {keyword} em {channel}")
                
                alert_data = {
                    'channel': channel,
                    'message': event.message.text,
                    'keyword': keyword,
                    'message_id': event.message.id,
                    'date': event.message.date.isoformat()
                }
                
                try:
                    await send_alert(alert_data)
                    print("✅ Alerta enviado!")
                except Exception as e:
                    print(f"❌ Erro no alerta: {e}")
                break
    
    async def get_channel_name(self, chat_id):
        try:
            entity = await self.client.get_entity(chat_id)
            return entity.title or entity.username or f'Canal_{chat_id}'
        except:
            return f'Canal_{chat_id}'
