import os
import threading
from flask import Flask
import telebot
import PyPDF2
import io
from google import genai

# 🌐 1. CORAÇÃO HÍBRIDO (Para o Render parar de carregar infinitamente)
app = Flask(__name__)
@app.route('/')
def home():
    return "Soberano Lab: Sistema Ativo e Protegido. 🟢"

def run_flask():
    # O Render injeta automaticamente a porta necessária
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

# 🛡️ 2. BUSCA DAS CHAVES SEGURAS (Não expostas no código)
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
            texto = pdf_reader.pages[0].extract_text()[:3000]
            
            res = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"Auditora Jurídica: Analise este contrato. Diga 'STATUS: 🔴 ALTO RISCO' ou 'STATUS: 🟢 BAIXO RISCO' e dê 3 motivos curtos: {texto}"
            )
            bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=f"⚖️ *VEREDITO:*\n\n{res.text}", parse_mode='Markdown')
        except Exception as e:
            bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=f"⚠️ Erro: {e}")

# 🚀 3. DISPARO DO SISTEMA
if __name__ == "__main__":
    # Inicia o site em paralelo para o Render ficar feliz
    threading.Thread(target=run_flask).start()
    print("🚀 SOBERANO CLOUD V28 ONLINE!")
    bot.infinity_polling()
