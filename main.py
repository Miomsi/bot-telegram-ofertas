import asyncio
import logging
from monitor import TelegramMonitor

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def main():
    print("🚀 Iniciando Sistema de Monitoramento do Telegram")
    print("📝 Configurando monitor...")
    
    monitor = TelegramMonitor()
    
    try:
        await monitor.start()
    except KeyboardInterrupt:
        print("⏹️ Monitor interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
    finally:
        await monitor.client.disconnect()
        print("🔴 Monitor finalizado")

if __name__ == "__main__":
    asyncio.run(main())
