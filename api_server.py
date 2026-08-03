import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from rag_retrieval_reranker import YoungLivingRAGPipeline
from gemini_generator import GeminiAdvisorGenerator

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

base_dir = os.path.dirname(os.path.abspath(__file__))
pipeline = YoungLivingRAGPipeline(base_dir)

# Initialize Gemini Generator
preferred_model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
gemini_generator = GeminiAdvisorGenerator(preferred_model=preferred_model)


def extract_matched_products(docs):
    products = []
    seen = set()
    if pipeline.loader.vademecum_df.empty:
        return products

    for doc in docs:
        title = doc.get("title", "")
        content = doc.get("content", "")

        for _, row in pipeline.loader.vademecum_df.iterrows():
            prod_name = str(row.get('Producto', ''))
            clean_name = prod_name.split('(')[0].strip()

            if (clean_name.lower() in title.lower() or clean_name.lower() in content.lower()) and prod_name not in seen:
                seen.add(prod_name)
                products.append({
                    "producto": prod_name,
                    "nombreBotanico": str(row.get('Nombre_Botanico', '')),
                    "dosisDifusor": str(row.get('Dosis_Difusor', '')),
                    "dilucionV6": str(row.get('Dilucion_V6', '')),
                    "precauciones": str(row.get('Precauciones', '')),
                    "modoEmpleo": str(row.get('Modo_Empleo', ''))
                })
    return products


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json or {}
    query = data.get('query', '').strip()
    history = data.get('history', [])

    if not query:
        return jsonify({"error": "No query provided"}), 400

    # 1. Execute RAG Retrieval & Reranking Pipeline
    pipeline_output = pipeline.execute(query, top_k=3)

    # 2. Generate response using Gemini LLM (with contextual RAG & conversation history)
    response_payload = gemini_generator.generate(pipeline_output, history=history)

    # 3. Attach matched structured product cards for interactive UI
    docs = pipeline_output.get("documents", [])
    response_payload["products"] = extract_matched_products(docs)

    return jsonify(response_payload)


@app.route('/api/catalog', methods=['GET'])
def get_catalog():
    items = []
    if not pipeline.loader.vademecum_df.empty:
        for _, row in pipeline.loader.vademecum_df.iterrows():
            items.append({
                "type": "PRODUCT",
                "producto": str(row.get('Producto', '')),
                "nombreBotanico": str(row.get('Nombre_Botanico', '')),
                "dosisDifusor": str(row.get('Dosis_Difusor', '')),
                "dilucionV6": str(row.get('Dilucion_V6', '')),
                "precauciones": str(row.get('Precauciones', '')),
                "modoEmpleo": str(row.get('Modo_Empleo', ''))
            })

    articles = []
    if not pipeline.loader.blog_posts_df.empty:
        for _, row in pipeline.loader.blog_posts_df.iterrows():
            articles.append({
                "type": "ARTICLE",
                "source": "Young Living Blog",
                "id": str(row.get('id', '')),
                "title": str(row.get('title', '')),
                "category": str(row.get('category', '')),
                "date": str(row.get('date', '')),
                "url": str(row.get('url', '')),
                "tags": str(row.get('tags', '')),
                "description": str(row.get('description', '')),
                "fullText": str(row.get('full_text', ''))
            })

    if not pipeline.loader.essenciales_posts_df.empty:
        for _, row in pipeline.loader.essenciales_posts_df.iterrows():
            articles.append({
                "type": "ARTICLE",
                "source": "Essenciales Blog",
                "id": str(row.get('id', '')),
                "title": str(row.get('title', '')),
                "category": str(row.get('category', '')),
                "date": str(row.get('date', '')),
                "url": str(row.get('url', '')),
                "tags": str(row.get('tags', '')),
                "description": str(row.get('description', '')),
                "fullText": str(row.get('full_text', ''))
            })

    return jsonify({
        "totalProducts": len(items),
        "totalArticles": len(articles),
        "totalReferences": len(items) + len(articles),
        "products": items,
        "articles": articles
    })


@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        "status": "online",
        "version": "Asesor de Bienestar 1.0",
        "gemini_active": gemini_generator.client is not None,
        "model_primary": gemini_generator.preferred_model
    })


if __name__ == '__main__':
    port = int(os.environ.get("FLASK_PORT", 5000))
    print(f"[YoungLiving] Iniciando servidor API Flask RAG v0.4 con integracion Gemini en puerto {port}...")
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
