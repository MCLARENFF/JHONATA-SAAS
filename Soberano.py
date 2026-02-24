import os
import threading
from flask import Flask
import telebot
import PyPDF2
import io
from google import genai

# 🌐 1. CORAÇÃO HÍBRIDO (Para o Render ficar ativo)
app = Flask(__name__)

@app.route('/')
def home():
    return "Soberano Lab: Sistema Ativo e Protegido. 🟢"

def run_flask():
    # O Render injeta automaticamente a porta necessária
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

# 🛡️ 2. BUSCA DAS CHAVES SEGURAS (Configuradas no Render)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = genai.Client(api_key=GEMINI_KEY)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "⚖️ *Soberano Auditor Online!*\nEnvie o PDF para análise.", parse_mode='Markdown')

@bot.message_handler(content_types=['document'])
def handle_docs(message):
    if message.document.mime_type == 'application/pdf':
        msg = bot.reply_to(message, "🚨 *Analisando contrato...*")
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(downloaded_file))
            
            # Extrai texto das primeiras páginas
            texto = ""
            for i in range(min(len(pdf_reader.pages), 3)):
                texto += pdf_reader.pages[i].extract_text()
            
            texto = texto[:4000] # Limite para processamento rápido
            
            res = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"Auditora Jurídica: Analise este contrato. Diga 'STATUS: 🔴 ALTO RISCO' ou 'STATUS: 🟢 BAIXO RISCO' e dê 3 motivos curtos: {texto}"
            )
            bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=f"⚖️ *VEREDITO:*\n\n{res.text}", parse_mode='Markdown')
        except Exception as e:
            bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=f"⚠️ Erro no processamento: {e}")

# 🚀 3. DISPARO DO SISTEMA
if __name__ == "__main__":
    # Inicia o servidor web em uma linha separada (Thread)
    threading.Thread(target=run_flask, daemon=True).start()
    print("🚀 SOBERANO CLOUD V29 ONLINE!")
    # Inicia o bot do Telegram
    bot.infinity_polling()
