import asyncio
import logging
import os
from monitor import TelegramMonitor

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def check_environment():
    """Verifica se todas as variáveis de ambiente estão configuradas"""
    required_vars = ['API_ID', 'API_HASH', 'PHONE_NUMBER', 'BOT_TOKEN', 'USER_ID', 'SESSION_STRING']
    missing = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"❌ Variáveis faltando: {', '.join(missing)}")
        return False
    
    print("✅ Todas as variáveis de ambiente estão configuradas")
    return True

async def main():
    print("🚀 Iniciando Sistema de Monitoramento do Telegram")
    print("🔍 Verificando configuração...")
    
    # Verificar variáveis de ambiente
    if not check_environment():
        print("❌ Configure as variáveis faltando no Railway e reinicie")
        return
    
    print("📝 Iniciando monitor...")
    
    try:
        monitor = TelegramMonitor()
        await monitor.start()
    except KeyboardInterrupt:
        print("⏹️ Monitor interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("🔴 Monitor finalizado")

if __name__ == "__main__":
    asyncio.run(main())
