import os
import threading
from flask import Flask
import telebot
import PyPDF2
import io
import time
from google import genai

# 🌐 1. CORAÇÃO HÍBRIDO
app = Flask(__name__)

@app.route('/')
def home():
    return "Soberano Lab: Sistema Ativo e Protegido. 🟢"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

# 🛡️ 2. BUSCA DAS CHAVES SEGURAS
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = genai.Client(api_key=GEMINI_KEY)

# 💎 MENSAGEM VIP DE BOAS-VINDAS (COM AMORTECEDOR)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    mensagem_vip = """
🏛️ *BEM-VINDO AO SOBERANO AI* 🏛️
_O seu Auditor Jurídico de Bolso._

Eu sou uma inteligência artificial treinada para ler, analisar e encontrar riscos ocultos em contratos.

*Como usar:*
1️⃣ Envie um documento em formato *PDF*.
2️⃣ Aguarde alguns segundos.
3️⃣ Receba o Veredito (🔴 Alto Risco ou 🟢 Baixo Risco) com 3 pontos de atenção.

🚨 *Aguardando o seu arquivo...*
"""
    try:
        bot.reply_to(message, mensagem_vip, parse_mode='Markdown')
    except Exception as e:
        print(f"⚠️ Erro ignorado ao enviar boas-vindas: {e}")

@bot.message_handler(content_types=['document'])
def handle_docs(message):
    if message.document.mime_type == 'application/pdf':
        try:
            msg = bot.reply_to(message, "🚨 *Analisando contrato...*")
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(downloaded_file))
            
            texto = ""
            for i in range(min(len(pdf_reader.pages), 3)):
                texto += pdf_reader.pages[i].extract_text()
            
            texto = texto[:4000]
            
            res = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"Auditora Jurídica: Analise este contrato. Diga 'STATUS: 🔴 ALTO RISCO' ou 'STATUS: 🟢 BAIXO RISCO' e dê 3 motivos curtos: {texto}"
            )
            bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=f"⚖️ *VEREDITO:*\n\n{res.text}", parse_mode='Markdown')
        except Exception as e:
            try:
                bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=f"⚠️ Erro no processamento: {e}")
            except:
                pass

# 🚀 3. DISPARO DO SISTEMA COM RECONEXÃO AUTOMÁTICA
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    print("🚀 SOBERANO CLOUD V31 BLINDADO ONLINE!")
    
    while True:
        try:
            # Configuração otimizada para evitar que o Render corte a conexão
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            print(f"⚠️ Queda de rede detectada. Reconectando em 5 segundos... Erro: {e}")
            time.sleep(5)
