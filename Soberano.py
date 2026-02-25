import os
import io
from flask import Flask, request, render_template_string
import PyPDF2
from google import genai

# 🌐 INICIALIZAÇÃO DA PLATAFORMA WEB
app = Flask(__name__)
GEMINI_KEY = os.environ.get("GEMINI_KEY")
client = genai.Client(api_key=GEMINI_KEY)

# 🎨 DESIGN DA PÁGINA (Interface do Usuário Integrada)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Soberano AI - Auditoria Jurídica</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0d0d0d; color: #ffffff; text-align: center; padding: 50px 20px; margin: 0; }
        .container { max-width: 650px; margin: auto; background: #1a1a1a; padding: 40px; border-radius: 15px; box-shadow: 0 0 20px rgba(0, 255, 170, 0.2); border: 1px solid #333; }
        h1 { color: #00ffaa; font-size: 2.5em; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 2px;}
        p.subtitle { color: #888; font-size: 1.1em; margin-bottom: 30px; }
        .upload-area { border: 2px dashed #00ffaa; padding: 30px; border-radius: 10px; background: #111; margin-bottom: 20px; }
        input[type=file] { color: #fff; }
        button { background-color: #00ffaa; color: #000; border: none; padding: 15px 30px; font-size: 18px; cursor: pointer; border-radius: 8px; font-weight: bold; transition: 0.3s; width: 100%; text-transform: uppercase;}
        button:hover { background-color: #00cc88; box-shadow: 0 0 15px rgba(0,255,170,0.5); }
        .result { margin-top: 40px; text-align: left; background: #222; padding: 25px; border-radius: 10px; white-space: pre-wrap; border-left: 5px solid #00ffaa; line-height: 1.6;}
        .footer { margin-top: 30px; color: #555; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏛️ SOBERANO AI</h1>
        <p class="subtitle">Motor de Triagem Jurídica de Contratos v1.0</p>
        
        <div class="upload-area">
            <form method="post" enctype="multipart/form-data">
                <input type="file" name="file" accept=".pdf" required>
                <br><br>
                <button type="submit">⚡ Iniciar Auditoria</button>
            </form>
        </div>

        {% if result %}
        <div class="result">
            <h3 style="color: #00ffaa; margin-top:0;">⚖️ VEREDITO DA IA:</h3>
            {{ result }}
        </div>
        {% endif %}
    </div>
    <div class="footer">Desenvolvido por Jhonata - Soberano Lab &copy; 2026</div>
</body>
</html>
"""

# 🧠 ROTA PRINCIPAL (Processamento do PDF)
@app.route('/', methods=['GET', 'POST'])
def home():
    veredicto = None
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template_string(HTML_TEMPLATE, result="⚠️ Erro: Nenhum arquivo enviado.")
        
        file = request.files['file']
        if file.filename == '':
            return render_template_string(HTML_TEMPLATE, result="⚠️ Erro: Arquivo vazio.")
        
        if file and file.filename.endswith('.pdf'):
            try:
                # Extração
                pdf_reader = PyPDF2.PdfReader(file)
                texto = ""
                for i in range(min(len(pdf_reader.pages), 3)): # Lê as 3 primeiras páginas
                    texto += pdf_reader.pages[i].extract_text()
                
                texto = texto[:4000] # Limite de segurança
                
                # Inteligência
                res = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=f"Você é a Soberano AI, uma Auditora Jurídica. Analise este contrato de forma clara. 1. Inicie com 'STATUS: 🔴 ALTO RISCO' ou 'STATUS: 🟢 BAIXO RISCO'. 2. Liste 3 pontos de atenção ou possíveis golpes. Texto: {texto}"
                )
                veredicto = res.text
            except Exception as e:
                veredicto = f"⚠️ Erro no motor de processamento: {str(e)}"
        else:
            veredicto = "⚠️ Por favor, envie um arquivo com extensão .PDF válido."
            
    return render_template_string(HTML_TEMPLATE, result=veredicto)

# 🚀 INICIALIZAÇÃO DO SERVIDOR WEB
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
