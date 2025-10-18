import asyncio
import logging
from monitor import TelegramMonitor

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    print("🚀 Iniciando Sistema de Monitoramento do Telegram")
    
    try:
        monitor = TelegramMonitor()
        await monitor.start()
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
