from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
import json
import os
import logging
import re

# Configurações
logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CONFIG_FILE = "config.json"

def carregar_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"alertas": {}, "chat_id": None}

def salvar_config(config):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except:
        pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    config = carregar_config()
    config["chat_id"] = update.effective_chat.id
    salvar_config(config)
    
    keyboard = [
        [InlineKeyboardButton("➕ Criar Alerta", callback_data="criar_alerta")],
        [InlineKeyboardButton("📋 Meus Alertas", callback_data="listar_alertas")],
        [InlineKeyboardButton("❌ Remover Alerta", callback_data="remover_alerta")],
        [InlineKeyboardButton("ℹ️ Ajuda", callback_data="ajuda")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🔔 *AlertKey Bot*\n\n"
        "Monitore canais e receba alertas quando suas palavras-chave aparecerem!\n\n"
        "*Como usar:*\n"
        "1. Crie um alerta com palavras-chave\n"
        "2. Adicione os canais para monitorar\n"
        "3. Receba notificações em tempo real!",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    config = carregar_config()
    
    if query.data == "criar_alerta":
        await query.edit_message_text(
            "🔔 *Criar Novo Alerta*\n\n"
            "Digite um *nome* para este alerta:\n"
            "Ex: `Placas de Vídeo` ou `Ofertas PC`",
            parse_mode='Markdown'
        )
        context.user_data["etapa"] = "nome_alerta"
        
    elif query.data == "listar_alertas":
        await listar_alertas(query, config)
        
    elif query.data == "remover_alerta":
        await remover_alerta_menu(query, config)
        
    elif query.data == "ajuda":
        await ajuda(query)
        
    elif query.data.startswith("remover_alerta:"):
        nome_alerta = query.data.split(":")[1]
        if nome_alerta in config["alertas"]:
            del config["alertas"][nome_alerta]
            salvar_config(config)
            await query.edit_message_text(f"✅ Alerta *{nome_alerta}* removido!", parse_mode='Markdown')
        await start(update, context)
        
    elif query.data == "voltar":
        await start(update, context)

async def listar_alertas(query, config):
    if not config["alertas"]:
        await query.edit_message_text(
            "📋 *Meus Alertas*\n\n"
            "❌ Nenhum alerta configurado.\n\n"
            "Clique em *➕ Criar Alerta* para começar!",
            parse_mode='Markdown'
        )
        return
    
    mensagem = "📋 *Meus Alertas*\n\n"
    for nome, dados in config["alertas"].items():
        palavras = ", ".join(dados["palavras"])
        canais = ", ".join([c.split('/')[-1] for c in dados["canais"]])
        mensagem += f"🔔 *{nome}*\n"
        mensagem += f"   📝 *Palavras:* {palavras}\n"
        mensagem += f"   📢 *Canais:* {canais}\n\n"
    
    keyboard = [[InlineKeyboardButton("🔙 Voltar", callback_data="voltar")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(mensagem, reply_markup=reply_markup, parse_mode='Markdown')

async def remover_alerta_menu(query, config):
    if not config["alertas"]:
        await query.edit_message_text("❌ Nenhum alerta para remover!")
        return
    
    keyboard = []
    for nome in config["alertas"].keys():
        keyboard.append([InlineKeyboardButton(f"❌ {nome}", callback_data=f"remover_alerta:{nome}")])
    
    keyboard.append([InlineKeyboardButton("🔙 Voltar", callback_data="voltar")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🗑️ *Remover Alerta*\n\nSelecione o alerta para remover:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def ajuda(query):
    texto = (
        "ℹ️ *Como usar o AlertKey Bot*\n\n"
        "*1. Criar Alertas:*\n"
        "   - Clique em *➕ Criar Alerta*\n"
        "   - Digite um nome para o alerta\n"
        "   - Adicione palavras-chave (separadas por vírgula)\n"
        "   - Adicione links de canais\n\n"
        
        "*2. Formatos Aceitos:*\n"
        "   - *Canais:* `https://t.me/nome`, `@nome`, `t.me/nome`\n"
        "   - *Palavras:* `rtx 4070, placa de vídeo, promoção`\n\n"
        
        "*3. Receber Alertas:*\n"
        "   - Quando suas palavras aparecerem nos canais monitorados\n"
        "   - Você recebe notificação instantânea\n\n"
        
        "*Exemplo Completo:*\n"
        "```\n"
        "Nome: Placas NVIDIA\n"
        "Palavras: rtx 4070, rtx 4060, rtx 3080\n"
        "Canais: https://t.me/terabyteshopoficial\n"
        "```"
    )
    
    keyboard = [[InlineKeyboardButton("🔙 Voltar", callback_data="voltar")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(texto, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
        
    config = carregar_config()
    texto = update.message.text.strip()
    user_data = context.user_data
    
    if user_data.get("etapa") == "nome_alerta":
        user_data["nome_alerta"] = texto
        user_data["etapa"] = "palavras_alerta"
        
        await update.message.reply_text(
            "📝 Agora digite as *palavras-chave* (separadas por vírgula):\n"
            "Ex: `rtx 4070, placa de vídeo, promoção, nvidia`",
            parse_mode='Markdown'
        )
        
    elif user_data.get("etapa") == "palavras_alerta":
        palavras = [p.strip().lower() for p in texto.split(",") if p.strip()]
        user_data["palavras_alerta"] = palavras
        user_data["etapa"] = "canais_alerta"
        
        await update.message.reply_text(
            "📢 Agora adicione os *links dos canais* (um por mensagem):\n"
            "Ex: `https://t.me/terabyteshopoficial`\n\n"
            "Digite *`pronto`* quando terminar.",
            parse_mode='Markdown'
        )
        user_data["canais_alerta"] = []
        
    elif user_data.get("etapa") == "canais_alerta":
        if texto.lower() == "pronto":
            # Finalizar criação do alerta
            if not user_data["canais_alerta"]:
                await update.message.reply_text("❌ Adicione pelo menos um canal!")
                return
                
            config["alertas"][user_data["nome_alerta"]] = {
                "palavras": user_data["palavras_alerta"],
                "canais": user_data["canais_alerta"]
            }
            salvar_config(config)
            
            # Resumo do alerta criado
            canais = ", ".join([c.split('/')[-1] for c in user_data["canais_alerta"]])
            palavras = ", ".join(user_data["palavras_alerta"])
            
            await update.message.reply_text(
                f"✅ *Alerta criado com sucesso!*\n\n"
                f"🔔 *Nome:* {user_data['nome_alerta']}\n"
                f"📝 *Palavras:* {palavras}\n"
                f"📢 *Canais:* {canais}\n\n"
                f"⚡ Agora você receberá alertas quando estas palavras aparecerem nos canais!",
                parse_mode='Markdown'
            )
            
            user_data.clear()
            await start(update, context)
            
        else:
            # Adicionar canal à lista
            canal = texto.strip()
            user_data["canais_alerta"].append(canal)
            
            await update.message.reply_text(
                f"✅ Canal adicionado: `{canal}`\n\n"
                f"📋 *Canais adicionados:* {len(user_data['canais_alerta'])}\n"
                f"Digite o próximo canal ou *`pronto`* para finalizar.",
                parse_mode='Markdown'
            )

async def monitorar_canais(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message = update.message or update.channel_post
        if not message:
            return
            
        config = carregar_config()
        if not config["alertas"]:
            return
            
        chat_username = getattr(message.chat, 'username', '')
        if not chat_username:
            return
            
        canal_atual = f"https://t.me/{chat_username}"
        
        # Pega o texto da mensagem
        texto = ""
        if message.text:
            texto = message.text.lower()
        elif message.caption:
            texto = message.caption.lower()
        else:
            return
        
        # Verifica todos os alertas
        for nome_alerta, dados_alerta in config["alertas"].items():
            # Verifica se o canal atual está sendo monitorado neste alerta
            canal_monitorado = False
            for canal in dados_alerta["canais"]:
                if chat_username in canal or canal in canal_atual or canal in f"@{chat_username}":
                    canal_monitorado = True
                    break
                    
            if not canal_monitorado:
                continue
                
            # Verifica palavras-chave
            palavras_encontradas = []
            for palavra in dados_alerta["palavras"]:
                if palavra.lower() in texto:
                    palavras_encontradas.append(palavra)
            
            if palavras_encontradas and config.get("chat_id"):
                chat_title = message.chat.title or "Canal"
                
                mensagem_alerta = (
                    f"🚨 *ALERTA: {nome_alerta}* 🚨\n\n"
                    f"**📢 Canal:** {chat_title}\n"
                    f"**🔍 Palavras encontradas:** {', '.join(palavras_encontradas)}\n"
                    f"**📝 Conteúdo:** {texto[:200]}...\n\n"
                    f"🔗 [Ver Mensagem](https://t.me/{chat_username}/{message.message_id})"
                )
                
                await context.bot.send_message(
                    chat_id=config["chat_id"],
                    text=mensagem_alerta,
                    parse_mode='Markdown'
                )
                
                print(f"🔔 ALERTA: {nome_alerta} - {palavras_encontradas} em {chat_title}")
                
    except Exception as e:
        print(f"Erro monitoramento: {e}")
# --- Integração com Telethon (para ler canais) ---
from telethon import TelegramClient, events
import asyncio

# Usa as mesmas variáveis do bot
API_ID = int(os.getenv('TG_API_ID', 0))
API_HASH = os.getenv('TG_API_HASH', '')
SESSION_NAME = "monitor_session"

# Cria cliente Telethon
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

async def iniciar_monitoramento(application):
    @client.on(events.NewMessage())
    async def handler(event):
        try:
            config = carregar_config()
            if not config.get("alertas") or not config.get("chat_id"):
                return

            # Nome do canal
            chat = await event.get_chat()
            username = getattr(chat, 'username', None)
            if not username:
                return

            texto = event.message.message.lower() if event.message.message else ""
            if not texto:
                return

            canal_link = f"https://t.me/{username}"

            for nome_alerta, dados_alerta in config["alertas"].items():
                if not any(canal_link in c or f"@{username}" in c for c in dados_alerta["canais"]):
                    continue

                palavras = [p for p in dados_alerta["palavras"] if p.lower() in texto]
                if palavras:
                    mensagem_alerta = (
                        f"🚨 *ALERTA: {nome_alerta}* 🚨\n\n"
                        f"📢 Canal: {chat.title or username}\n"
                        f"🔍 Palavras: {', '.join(palavras)}\n"
                        f"📝 {texto[:200]}...\n"
                        f"🔗 [Ver Mensagem]({canal_link}/{event.message.id})"
                    )
                    await application.bot.send_message(
                        chat_id=config["chat_id"],
                        text=mensagem_alerta,
                        parse_mode='Markdown'
                    )
        except Exception as e:
            print(f"Erro Telethon: {e}")

    print("👀 Monitoramento de canais iniciado com Telethon...")
    await client.start()
    await client.run_until_disconnected()

def main():
    print("🤖 AlertKey Bot iniciado! 🔔")

    application = Application.builder().token(TOKEN).build()

    # Handlers do bot
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Inicia o Telethon junto com o bot
    loop = asyncio.get_event_loop()
    loop.create_task(iniciar_monitoramento(application))

    print("✅ Bot rodando! Envie /start no Telegram")
    application.run_polling()


