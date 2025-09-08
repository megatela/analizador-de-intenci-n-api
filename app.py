# Nombre del archivo: app.py (Versión 2 - Más Robusta)
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from collections import Counter
import re
from urllib.parse import urlparse

app = Flask(__name__)
CORS(app)

def analyze_url_logic(url, soup, text_content):
    # ... (Esta parte es idéntica a la anterior) ...
    words = re.findall(r'\b\w{4,15}\b', text_content.lower())
    stop_words = set(['para', 'como', 'sobre', 'desde', 'hasta', 'este', 'esta', 'estos', 'estas', 'pero', 'porque', 'con', 'que', 'del', 'los', 'las', 'más', 'ser', 'por', 'son'])
    meaningful_words = [word for word in words if word not in stop_words]
    most_common_words = [word for word, count in Counter(meaningful_words).most_common(15)]
    central_theme = " ".join(most_common_words[:3]) if most_common_words else "No determinado"
    keywords = ", ".join(most_common_words)
    main_keyword = most_common_words[0] if most_common_words else ""
    text_lower = text_content.lower()
    intent = "Informativa"
    if any(k in text_lower for k in ['comprar', 'precio', 'oferta', 'tienda', 'carrito', 'descuento']): intent = "Transaccional"
    elif any(k in text_lower for k in ['mejor', 'comparativa', 'review', 'opiniones', 'top 5', 'alternativas']): intent = "Comercial"
    elif any(k in text_lower for k in ['contacto', 'acerca de', 'login', 'iniciar sesión']): intent = "Navegacional"
    word_count = len(text_content.split())
    completeness = "Completo y profundo" if word_count > 1200 else "Aceptable" if word_count > 600 else "Contenido breve"
    meta_title = soup.find('title').get_text(strip=True) if soup.find('title') else "No encontrado"
    meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
    meta_desc = meta_desc_tag['content'] if meta_desc_tag and meta_desc_tag.get('content') else "No encontrada"
    parsed_url = urlparse(url)
    url_friendliness = "Sí, corta y clara" if len(parsed_url.path) < 80 and not parsed_url.query else "Larga o con parámetros, se puede mejorar"
    h1_tag = soup.find('h1')
    h1 = h1_tag.get_text(strip=True) if h1_tag else "No encontrado"
    h2s = [h.get_text(strip=True) for h in soup.find_all('h2')]
    keyword_in_h1 = "Sí" if main_keyword and h1 and main_keyword in h1.lower() else "No"
    images = soup.find_all('img')
    images_with_alt = sum(1 for img in images if img.get('alt', '').strip())
    image_optimization = f"{images_with_alt} de {len(images)} imágenes tienen texto Alt." if images else "No se encontraron imágenes."
    structured_data = "Sí, se detectó JSON-LD" if soup.find('script', type='application/ld+json') else "No se encontraron datos estructurados (JSON-LD)"
    return {
        "central_theme": central_theme, "keywords": keywords, "intent": intent, "completeness": f"{completeness} ({word_count} palabras)",
        "meta_title": meta_title, "meta_description": meta_desc, "url_friendliness": url_friendliness, "h1": h1,
        "keyword_in_h1": f"{keyword_in_h1} (Palabra clave: '{main_keyword}')", "h2s": ", ".join(h2s) if h2s else 'Ninguno',
        "image_optimization": image_optimization, "structured_data": structured_data,
        "core_web_vitals": "Requiere API de PageSpeed para datos reales (LCP, FID, CLS)."
    }

@app.route('/analyze', methods=['GET'])
def analyze():
    try:
        url_to_analyze = request.args.get('url')
        if not url_to_analyze: return jsonify({"error": "No se proporcionó una URL."}), 400
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        # === CAMBIO IMPORTANTE: AUMENTAMOS EL TIEMPO DE ESPERA ===
        response = requests.get(url_to_analyze, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        for script_or_style in soup(["script", "style"]): script_or_style.decompose()
        text_content = soup.get_text(separator=' ', strip=True)
        analysis_results = analyze_url_logic(url_to_analyze, soup, text_content)
        return jsonify(analysis_results)
    except Exception as e:
        # Ahora este error nos dará más detalles
        return jsonify({"error": f"Ha ocurrido un error interno al analizar la URL: {str(e)}"}), 500
