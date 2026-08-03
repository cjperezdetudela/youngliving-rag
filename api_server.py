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
_pipeline = None
_gemini_generator = None

def get_pipeline():
    global _pipeline
    if _pipeline is None:
        _pipeline = YoungLivingRAGPipeline(base_dir)
    return _pipeline

def get_generator():
    global _gemini_generator
    if _gemini_generator is None:
        preferred_model = os.environ.get("GEMINI_MODEL", "gemini-flash-latest")
        _gemini_generator = GeminiAdvisorGenerator(preferred_model=preferred_model)
    return _gemini_generator


def extract_matched_products(docs):
    products = []
    seen = set()
    pipeline_obj = get_pipeline()
    if pipeline_obj.loader.vademecum_df.empty:
        return products

    for doc in docs:
        title = doc.get("title", "")
        content = doc.get("content", "")

        for _, row in pipeline_obj.loader.vademecum_df.iterrows():
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
    pipeline_obj = get_pipeline()
    generator_obj = get_generator()

    pipeline_output = pipeline_obj.execute(query, top_k=3)

    # 2. Generate response using Gemini LLM (with contextual RAG & conversation history)
    response_payload = generator_obj.generate(pipeline_output, history=history)

    # 3. Attach matched structured product cards for interactive UI
    docs = pipeline_output.get("documents", [])
    response_payload["products"] = extract_matched_products(docs)

    return jsonify(response_payload)


@app.route('/api/catalog', methods=['GET'])
def get_catalog():
    pipeline_obj = get_pipeline()
    items = []
    if not pipeline_obj.loader.vademecum_df.empty:
        for _, row in pipeline_obj.loader.vademecum_df.iterrows():
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
    if not pipeline_obj.loader.blog_posts_df.empty:
        for _, row in pipeline_obj.loader.blog_posts_df.iterrows():
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

    if not pipeline_obj.loader.essenciales_posts_df.empty:
        for _, row in pipeline_obj.loader.essenciales_posts_df.iterrows():
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
    gen_obj = get_generator()
    return jsonify({
        "status": "online",
        "version": "Asesor de Bienestar 1.0",
        "gemini_active": gen_obj.client is not None,
        "model_primary": gen_obj.preferred_model
    })


if __name__ == '__main__':
    port = int(os.environ.get("FLASK_PORT", 5000))
    print(f"[YoungLiving] Iniciando servidor API Flask RAG v0.4 con integracion Gemini en puerto {port}...")
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
