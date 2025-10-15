from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
import json
import os
import logging

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not TOKEN:
    print("❌ Token não encontrado!")
    exit(1)

CONFIG_FILE = "config.json"

def carregar_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"produtos": [], "canais": [], "chat_id": None}

def salvar_config(config):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except:
        pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        config = carregar_config()
        config["chat_id"] = update.effective_chat.id
        salvar_config(config)
        
        keyboard = [
            [InlineKeyboardButton("➕ Adicionar Produto", callback_data="add_produto")],
            [InlineKeyboardButton("➕ Adicionar Canal", callback_data="add_canal")],
            [InlineKeyboardButton("🗑️ Remover Produto", callback_data="remover_produto_menu")],
            [InlineKeyboardButton("🗑️ Remover Canal", callback_data="remover_canal_menu")],
            [InlineKeyboardButton("📋 Ver Configuração", callback_data="ver_config")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🤖 **Bot Monitor de Ofertas**\n\n"
            "Configure os produtos e canais:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        print(f"Erro: {e}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        
        if query.data == "add_produto":
            await query.edit_message_text(
                "📝 Digite a palavra para monitorar:\nEx: `4070` ou `rtx 4070`",
                parse_mode='Markdown'
            )
            context.user_data["aguardando"] = "novo_produto"
            
        elif query.data == "add_canal":
            await query.edit_message_text(
                "📢 Digite o @username do canal:\nEx: `@terabyteshopoficial`\n\n⚠️ Só o @username, sem https://",
                parse_mode='Markdown'
            )
            context.user_data["aguardando"] = "novo_canal"
            
        elif query.data == "ver_config":
            await mostrar_configuracao(query)
            
        elif query.data == "remover_produto_menu":
            await remover_produto_menu(query)
            
        elif query.data == "remover_canal_menu":
            await remover_canal_menu(query)
            
        elif query.data.startswith("remover_produto:"):
            produto = query.data.split(":")[1]
            config = carregar_config()
            config["produtos"] = [p for p in config["produtos"] if p != produto]
            salvar_config(config)
            await query.edit_message_text(f"✅ Produto `{produto}` removido!", parse_mode='Markdown')
            
        elif query.data.startswith("remover_canal:"):
            canal = query.data.split(":")[1]
            config = carregar_config()
            config["canais"] = [c for c in config["canais"] if c != canal]
            salvar_config(config)
            await query.edit_message_text(f"✅ Canal `{canal}` removido!", parse_mode='Markdown')
            
    except Exception as e:
        print(f"Erro: {e}")

async def remover_produto_menu(query):
    config = carregar_config()
    
    if not config["produtos"]:
        await query.edit_message_text("❌ Nenhum produto para remover!")
        return
    
    keyboard = []
    for produto in config["produtos"]:
        keyboard.append([InlineKeyboardButton(f"❌ {produto}", callback_data=f"remover_produto:{produto}")])
    
    keyboard.append([InlineKeyboardButton("🔙 Voltar", callback_data="voltar")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🗑️ **Remover Produto**\n\nClique no produto para remover:",
        reply_markup=reply_markup
    )

async def remover_canal_menu(query):
    config = carregar_config()
    
    if not config["canais"]:
        await query.edit_message_text("❌ Nenhum canal para remover!")
        return
    
    keyboard = []
    for canal in config["canais"]:
        keyboard.append([InlineKeyboardButton(f"❌ {canal}", callback_data=f"remover_canal:{canal}")])
    
    keyboard.append([InlineKeyboardButton("🔙 Voltar", callback_data="voltar")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🗑️ **Remover Canal**\n\nClique no canal para remover:",
        reply_markup=reply_markup
    )

async def mostrar_configuracao(query):
    config = carregar_config()
    
    produtos = "\n".join([f"• {p}" for p in config["produtos"]]) if config["produtos"] else "❌ Nenhum"
    canais = "\n".join([f"• {c}" for c in config["canais"]]) if config["canais"] else "❌ Nenhum"
    
    keyboard = [
        [InlineKeyboardButton("➕ Adicionar Produto", callback_data="add_produto")],
        [InlineKeyboardButton("➕ Adicionar Canal", callback_data="add_canal")],
        [InlineKeyboardButton("🗑️ Remover Produto", callback_data="remover_produto_menu")],
        [InlineKeyboardButton("🗑️ Remover Canal", callback_data="remover_canal_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"⚙️ **Configuração Atual**\n\n🛒 **Produtos:**\n{produtos}\n\n📢 **Canais:**\n{canais}",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message and context.user_data.get("aguardando"):
            config = carregar_config()
            texto = update.message.text.strip()
            
            if context.user_data["aguardando"] == "novo_produto":
                if texto.lower() not in config["produtos"]:
                    config["produtos"].append(texto.lower())
                    salvar_config(config)
                    await update.message.reply_text(f"✅ `{texto}` adicionado!", parse_mode='Markdown')
                else:
                    await update.message.reply_text("⚠️ Já existe!")
                    
            elif context.user_data["aguardando"] == "novo_canal":
                # Remove qualquer 'https://t.me/' se o usuário colocar
                texto = texto.replace('https://t.me/', '').replace('t.me/', '')
                if not texto.startswith('@'):
                    texto = '@' + texto
                    
                if texto.lower() not in config["canais"]:
                    config["canais"].append(texto.lower())
                    salvar_config(config)
                    await update.message.reply_text(f"✅ `{texto}` adicionado!", parse_mode='Markdown')
                else:
                    await update.message.reply_text("⚠️ Já existe!")
            
            context.user_data["aguardando"] = None
            
    except Exception as e:
        print(f"Erro: {e}")

async def monitorar_ofertas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message = update.message or update.channel_post
        if not message:
            return
        
        config = carregar_config()
        chat_username = getattr(message.chat, 'username', '')
        
        canal_atual = f"@{chat_username}" if chat_username else ""
        if canal_atual and canal_atual.lower() in [c.lower() for c in config["canais"]]:
            
            texto = ""
            if message.text:
                texto = message.text.lower()
            elif message.caption:
                texto = message.caption.lower()
            else:
                return
            
            produtos_encontrados = []
            for produto in config["produtos"]:
                if produto in texto:
                    produtos_encontrados.append(produto)
            
            if produtos_encontrados and config.get("chat_id"):
                chat_title = message.chat.title or "Canal"
                
                mensagem_alerta = (
                    f"🚨 **OFERTA ENCONTRADA!** 🚨\n\n"
                    f"**📢 Canal:** {chat_title}\n"
                    f"**🛒 Produto:** {', '.join(produtos_encontrados)}\n"
                    f"**📝 Detalhes:** {texto[:200]}...\n\n"
                    f"🔗 [Ver Oferta](https://t.me/{chat_username}/{message.message_id})"
                )
                
                await context.bot.send_message(
                    chat_id=config["chat_id"],
                    text=mensagem_alerta,
                    parse_mode='Markdown'
                )
                
                print(f"🎯 OFERTA: {produtos_encontrados} em {chat_title}")
                
    except Exception as e:
        print(f"Erro monitoramento: {e}")

async def voltar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

def main():
    print("🤖 Bot iniciado na nuvem! 🌐")
    
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.TEXT | filters.CAPTION, monitorar_ofertas))
    
    print("✅ Bot rodando! Envie /start no Telegram")
    
    application.run_polling()

if __name__ == '__main__':
    main()
