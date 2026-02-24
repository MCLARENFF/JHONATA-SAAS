import os
import telebot
import PyPDF2
import io
from google import genai

# 🛡️ CONFIGURAÇÃO DE ELITE
TELEGRAM_TOKEN = "8621777070:AAGzYDzxaAD49OW0mAtkkPBc1AJ-T-ce4LY"
GEMINI_KEY = "AIzaSyBT0srDBnrJuh3tV6RyrEuY9IhdjdqORD4"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = genai.Client(api_key=GEMINI_KEY)

print("🚀 SOBERANO CLOUD ATIVO - AGUARDANDO COMANDOS NO TELEGRAM...")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "⚖️ *Bem-vindo ao Soberano Auditor AI*\n\n"
        "Sou sua Inteligência Artificial especializada em auditoria jurídica de contratos.\n\n"
        "👉 *Como usar:* Envie-me um arquivo **PDF** de um contrato e eu farei uma análise de risco em segundos."
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(content_types=['document'])
def handle_docs(message):
    if message.document.mime_type == 'application/pdf':
        msg_processando = bot.reply_to(message, "🚨 *Dissecando contrato... Por favor, aguarde.*", parse_mode='Markdown')
        
        try:
            # 1. Baixa o arquivo da nuvem do Telegram
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            
            # 2. Extrai o texto do PDF
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(downloaded_file))
            texto = ""
            for page in range(min(len(pdf_reader.pages), 3)): # Analisa as primeiras 3 páginas (o essencial)
                texto += pdf_reader.pages[page].extract_text()
            
            # 3. Consulta o Oráculo Gemini 2.5 Flash
            prompt = (
                "Você é a Auditora Soberano Lab. Analise este contrato para um cliente leigo. "
                "1. Responda 'STATUS: 🔴 ALTO RISCO' ou 'STATUS: 🟢 BAIXO RISCO' na primeira linha. "
                "2. Liste 3 pontos de atenção ou possíveis golpes de forma curta e grossa. "
                "Aqui está o texto: " + texto[:4000]
            )
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            # 4. Entrega o Veredito
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=msg_processando.message_id,
                text=f"⚖️ *RESULTADO DA AUDITORIA*\n\n{response.text}",
                parse_mode='Markdown'
            )
            
        except Exception as e:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=msg_processando.message_id,
                text=f"⚠️ *Erro no processamento:* {str(e)}"
            )
    else:
        bot.reply_to(message, "❌ Por favor, envie apenas arquivos no formato **PDF**.")

bot.infinity_polling()