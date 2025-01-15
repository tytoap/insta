from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import os
import re
import requests

app = Flask(__name__)
CORS(app)

# Diretório para salvar os vídeos
DOWNLOADS_DIR = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOADS_DIR, exist_ok=True)


@app.route("/")
def index():
    return render_template("index.html")
def extract_shortcode(url):
    """Extrai o shortcode da URL do Instagram."""
    match = re.search(r'/reel/([^/]+)/', url)
    if match:
        return match.group(1)
    return None
    

@app.route('/download1', methods=['POST'])
def download1():
    data = request.get_json()
    url = data.get("url")
    
    if not url:
        return jsonify({"error": "URL inválida"}), 400
    
    shortcode = extract_shortcode(url)
    if not shortcode:
        return jsonify({"error": "Shortcode não encontrado na URL"}), 400

    # Construa a URL esperada pela biblioteca
    api_url = f"https://www.instagram.com/p/{shortcode}/?__a=1&__d=dis"
    
    # Simulação de processamento (substitua com sua lógica real)
    return jsonify({"message": "Processamento simulado para URL", "api_url": api_url})


@app.route("/download", methods=["POST"])
def download_video():
    try:
        # Obter a URL enviada pelo cliente
        data = request.get_json()
        if not data or "url" not in data:
            return jsonify({"error": "URL não fornecida"}), 400

        instagram_url = data["url"]
        ######################
        # Extrair o shortcode da URL

        shortcode = extract_shortcode(instagram_url)
        if not shortcode:
            return jsonify({"error": "Shortcode não encontrado na URL"}), 400

        # Construa a URL esperada pela biblioteca
        api_url = f"https://www.instagram.com/p/{shortcode}/?__a=1&__d=dis"
        
     
       # Requisição à API do Instagram
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(api_url, headers=headers)

        if response.status_code != 200:
            return jsonify({"error": "Não foi possível acessar os dados do vídeo"}), 500

        # Processar a resposta JSON
        data = response.json()
        video_url = data["graphql"]["shortcode_media"]["video_url"]

        # Baixar o vídeo
        video_response = requests.get(video_url, stream=True)
        video_filename = os.path.join(DOWNLOADS_DIR, f"video_{shortcode}.mp4")

        with open(video_filename, "wb") as f:
            for chunk in video_response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

        return jsonify({"message": "Download concluído", "path": f"/download/{shortcode}"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ping', methods=['POST'])
def ping():
    data = request.get_json()
    if data and data.get("message") == "ping":
        return jsonify({"response": "pong"}), 200
    return jsonify({"error": "Invalid message"}), 400


@app.route("/download/<shortcode>")
def serve_video(shortcode):
    video_path = os.path.join(DOWNLOADS_DIR, f"video_{shortcode}.mp4")
    if not os.path.exists(video_path):
        return jsonify({"error": "Vídeo não encontrado"}), 404
    return send_file(video_path, as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
