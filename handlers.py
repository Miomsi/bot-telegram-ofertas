from telegram import Bot
from telegram.constants import ParseMode
from config import config

class AlertHandler:
    def __init__(self):
        self.bot = Bot(token=config.BOT_TOKEN)
    
    async def send_alert(self, alert_data: dict):
        try:
            message = f"""
🚨 <b>ALERTA DE PALAVRA-CHAVE</b> 🚨

<b>Canal:</b> {alert_data['channel']}
<b>Palavra-chave:</b> #{alert_data['keyword'].replace(' ', '_')}
<b>Data:</b> {alert_data['date']}

<b>Mensagem:</b>
{alert_data['message'][:500]}...
            """.strip()
            
            await self.bot.send_message(
                chat_id=config.USER_ID,
                text=message,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )
            print(f"✅ Alerta enviado para {config.USER_ID}")
            
        except Exception as e:
            print(f"❌ Erro ao enviar alerta: {e}")

alert_handler = AlertHandler()

async def send_alert(alert_data: dict):
    await alert_handler.send_alert(alert_data)
