import os
import json
import re
import unicodedata
import pandas as pd
from typing import List, Dict, Any, Tuple

def normalize_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    return text.lower().strip()

class DataSourceLoader:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.data_dir = os.path.join(base_dir, 'data')
        
        self.manifest_path = self._resolve_file('Manifiesto_integracion_Vademecum_v0.2.json')
        self.router_config_path = self._resolve_file('Router_YoungLiving_v0.4.json')
        self.prompt_patch_path = self._resolve_file('Parche_prompt_router_YoungLiving_v0.3.txt')
        
        self.vademecum_path = self._resolve_file('Vademecum_YL_v0.5_Completo_ES_CA.xlsx') if os.path.exists(self._resolve_file('Vademecum_YL_v0.5_Completo_ES_CA.xlsx')) else self._resolve_file('Vademecum_YL_v0.4_Completo_ES_CA.xlsx')
        self.corpus_path = self._resolve_file('Conocimientos_YoungLiving_RAG_v0.5.jsonl') if os.path.exists(self._resolve_file('Conocimientos_YoungLiving_RAG_v0.5.jsonl')) else self._resolve_file('Conocimientos_YoungLiving_RAG_v0.4.jsonl')
        self.catalog_path = self._resolve_file('bbdd_youngliving_catalogo_v0.5.csv') if os.path.exists(self._resolve_file('bbdd_youngliving_catalogo_v0.5.csv')) else self._resolve_file('bbdd_youngliving_catalogo_v0.4.csv')
        self.blog_chunks_path = self._resolve_file('youngliving_chunks_rag.jsonl')
        self.blog_posts_path = self._resolve_file('youngliving_posts_full.csv')
        self.essenciales_chunks_path = self._resolve_file('essenciales_chunks_rag.jsonl')
        self.essenciales_posts_path = self._resolve_file('essenciales_posts_full.csv')
        
        self.manifest = self._load_json(self.manifest_path)
        self.router_config = self._load_json(self.router_config_path)
        self.prompt_rules = self._load_text(self.prompt_patch_path)
        
        self.vademecum_df = self._load_excel(self.vademecum_path)
        self.corpus_data = self._load_jsonl(self.corpus_path)
        self.catalog_df = self._load_csv(self.catalog_path)
        self.blog_chunks = self._load_jsonl(self.blog_chunks_path)
        self.blog_posts_df = self._load_csv(self.blog_posts_path)
        self.essenciales_chunks = self._load_jsonl(self.essenciales_chunks_path)
        self.essenciales_posts_df = self._load_csv(self.essenciales_posts_path)

    def _resolve_file(self, filename: str) -> str:
        """Prioriza buscar el archivo en la carpeta 'data/' y cae en la raíz si no se encuentra."""
        data_path = os.path.join(self.data_dir, filename)
        if os.path.exists(data_path):
            return data_path
        
        root_path = os.path.join(self.base_dir, filename)
        if os.path.exists(root_path):
            return root_path
            
        scraper_path = os.path.join(self.base_dir, '..', 'youngliving_browser_scraper_pack', filename)
        if os.path.exists(scraper_path):
            return scraper_path
            
        return root_path

    def _load_json(self, path: str) -> Dict[str, Any]:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _load_text(self, path: str) -> str:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""

    def _load_jsonl(self, path: str) -> List[Dict[str, Any]]:
        data = []
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data.append(json.loads(line.strip()))
        return data

    def _load_excel(self, path: str) -> pd.DataFrame:
        if os.path.exists(path):
            return pd.read_excel(path)
        return pd.DataFrame()

    def _load_csv(self, path: str) -> pd.DataFrame:
        if os.path.exists(path):
            return pd.read_csv(path)
        return pd.DataFrame()


class IntentRouterEngine:
    def __init__(self, router_config: Dict[str, Any], prompt_rules: str):
        self.router_config = router_config
        self.prompt_rules = prompt_rules
        self.intents = router_config.get('intents', {})
        self.synonyms = router_config.get('query_preprocessing', {}).get('synonym_mapping', {})
        
        self.safety_keywords = [
            "embarazo", "embarazada", "lactancia", "bebe", "bebes", "recien nacido",
            "ingerir", "tomar por boca", "contacto ocular"
        ]

    def classify(self, query: str) -> Dict[str, Any]:
        query_norm = normalize_text(query)
        
        # 1. Strict Safety Check for high-risk topics
        if any(re.search(rf'\b{re.escape(skw)}\b', query_norm) for skw in self.safety_keywords):
            return {
                "intent": "SAFETY_FALLBACK",
                "confidence": 0.98,
                "primary_source": self.intents.get("SAFETY_FALLBACK", {}).get("primary_data_source", "Parche_prompt_router_YoungLiving_v0.3.txt"),
                "retrieval_strategy": "rule_based_fallback",
                "reasoning": "Regla de seguridad activada por presencia de términos médicos/riesgo."
            }
            
        # 2. Intent Scoring
        scores = {}
        for intent_key, cfg in self.intents.items():
            if intent_key == "SAFETY_FALLBACK":
                continue
            score = 0.0
            keywords = cfg.get('keywords', [])
            for kw in keywords:
                kw_norm = normalize_text(kw)
                if kw_norm in query_norm:
                    score += 2.0
                    
            # Check synonyms
            for main_term, syn_list in self.synonyms.items():
                all_syns = [main_term] + syn_list
                if any(normalize_text(s) in query_norm for s in all_syns):
                    kw_list_norm = [normalize_text(k) for k in keywords]
                    if any(normalize_text(main_term) in k for k in kw_list_norm):
                        score += 0.5
            scores[intent_key] = score

        sorted_intents = sorted(scores.items(), key=lambda x: (x[1], -self.intents[x[0]].get('priority', 99)), reverse=True)
        top_intent, top_score = sorted_intents[0]
        
        if top_score > 0:
            confidence = min(0.70 + (top_score * 0.08), 0.98)
            classified = top_intent
        else:
            classified = 'GENERAL_QUERY'
            confidence = 0.50

        intent_info = self.intents.get(classified, {})
        return {
            "intent": classified,
            "confidence": round(confidence, 2),
            "primary_source": intent_info.get("primary_data_source", "Conocimientos_YoungLiving_RAG_v0.5.jsonl"),
            "retrieval_strategy": intent_info.get("retrieval_strategy", "multi_source_search"),
            "reasoning": f"Coincidencia de consulta general (Score: {top_score:.1f})."
        }


class MultiSourceRetriever:
    def __init__(self, loader: DataSourceLoader):
        self.loader = loader
        self.synonyms = loader.router_config.get('query_preprocessing', {}).get('synonym_mapping', {})

    def _expand_tokens(self, tokens: set) -> set:
        expanded = set(tokens)
        for main_term, syns in self.synonyms.items():
            main_norm = normalize_text(main_term)
            syns_norm = [normalize_text(s) for s in syns]
            if main_norm in tokens or any(s in tokens for s in syns_norm):
                expanded.add(main_norm)
                expanded.update(syns_norm)
        return expanded

    def search_all_sources(self, query: str, route_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        query_norm = normalize_text(query)
        raw_tokens = set(query_norm.split())
        query_tokens = self._expand_tokens(raw_tokens)
        candidates = []
        
        # Priority 1: Vademecum Structured Excel
        if not self.loader.vademecum_df.empty:
            for idx, row in self.loader.vademecum_df.iterrows():
                text_block = " ".join([str(val) for val in row.values if pd.notna(val)])
                text_norm = normalize_text(text_block)
                matches = sum(1 for tok in query_tokens if tok in text_norm and len(tok) > 2)
                sim_score = min(1.0, (matches / max(1, len(raw_tokens))) + 0.1) if matches > 0 else 0.0
                candidates.append({
                    "source": "data/Vademecum_YL_v0.4_Completo_ES_CA.xlsx",
                    "priority": 1,
                    "content_type": "STRUCTURED_GROUND_TRUTH",
                    "title": f"Ficha Técnica: {row.get('Producto', 'Producto YL')}",
                    "content": f"Producto: {row.get('Producto')}\nNombre Botánico: {row.get('Nombre_Botanico')}\nDosis Difusor: {row.get('Dosis_Difusor')}\nDilución V-6: {row.get('Dilucion_V6')}\nPrecauciones: {row.get('Precauciones')}\nModo Empleo: {row.get('Modo_Empleo')}",
                    "similarity_score": round(sim_score, 4)
                })
                    
        # Priority 2: RAG Conceptual Corpus JSONL
        for doc in self.loader.corpus_data:
            content_norm = normalize_text(doc.get('content', '') + ' ' + doc.get('title', '') + ' ' + ' '.join(doc.get('tags', [])))
            matches = sum(1 for tok in query_tokens if tok in content_norm and len(tok) > 2)
            sim_score = min(1.0, (matches / max(1, len(raw_tokens))) + 0.1) if matches > 0 else 0.0
            candidates.append({
                "source": "data/Conocimientos_YoungLiving_RAG_v0.4.jsonl",
                "priority": 2,
                "content_type": "COMBINED_RAG_CORPUS",
                "title": doc.get('title', 'Documento RAG'),
                "content": doc.get('content', ''),
                "similarity_score": round(sim_score, 4)
            })

        # Priority 8: Commercial Catalog CSV
        if not self.loader.catalog_df.empty:
            for idx, row in self.loader.catalog_df.iterrows():
                text_block = " ".join([str(val) for val in row.values if pd.notna(val)])
                text_norm = normalize_text(text_block)
                matches = sum(1 for tok in query_tokens if tok in text_norm and len(tok) > 2)
                sim_score = min(1.0, (matches / max(1, len(raw_tokens))) + 0.1) if matches > 0 else 0.0
                candidates.append({
                    "source": "data/bbdd_youngliving_catalogo_v0.4.csv",
                    "priority": 8,
                    "content_type": "COMMERCIAL_CATALOG",
                    "title": f"Catálogo SKU: {row.get('SKU', '')} - {row.get('Producto', '')}",
                    "content": f"Producto: {row.get('Producto')}\nSKU: {row.get('SKU')}\nFormatos: {row.get('Formatos_Disponibles')}\nPrecio PV: {row.get('Precio_PV')}\nDisponibilidad: {row.get('Disponibilidad')}",
                    "similarity_score": round(sim_score, 4)
                })

        # Priority 9: Scraped Young Living Blog Chunks JSONL
        for chunk in self.loader.blog_chunks:
            chunk_text = chunk.get('text', '') + ' ' + chunk.get('title', '') + ' ' + str(chunk.get('tags', ''))
            chunk_norm = normalize_text(chunk_text)
            matches = sum(1 for tok in query_tokens if tok in chunk_norm and len(tok) > 2)
            sim_score = min(1.0, (matches / max(1, len(raw_tokens))) + 0.1) if matches > 0 else 0.0
            candidates.append({
                "source": "data/youngliving_chunks_rag.jsonl",
                "priority": 9,
                "content_type": "BLOG_CONTENT",
                "title": chunk.get('title', 'Artículo de Blog YL'),
                "content": chunk.get('text', '')[:450],
                "similarity_score": round(sim_score, 4)
            })

        # Priority 9: Scraped Essenciales Blog Chunks JSONL
        for chunk in self.loader.essenciales_chunks:
            chunk_text = chunk.get('text', '') + ' ' + chunk.get('title', '') + ' ' + str(chunk.get('tags', ''))
            chunk_norm = normalize_text(chunk_text)
            matches = sum(1 for tok in query_tokens if tok in chunk_norm and len(tok) > 2)
            sim_score = min(1.0, (matches / max(1, len(raw_tokens))) + 0.1) if matches > 0 else 0.0
            candidates.append({
                "source": "data/essenciales_chunks_rag.jsonl",
                "priority": 9,
                "content_type": "BLOG_CONTENT",
                "title": chunk.get('title', 'Artículo Blog Essenciales'),
                "content": chunk.get('text', '')[:450],
                "similarity_score": round(sim_score, 4)
            })

        return candidates


class PrioritizedReranker:
    def __init__(self, loader: DataSourceLoader):
        self.loader = loader
        
        # Intent to allowed/expected content types mapping
        self.intent_source_map = {
            "VADEMECUM_STRUCT": ["STRUCTURED_GROUND_TRUTH", "Vademecum_YL_v0.4_Completo_ES_CA.xlsx"],
            "CORPUS_RAG": ["COMBINED_RAG_CORPUS", "Conocimientos_YoungLiving_RAG_v0.4.jsonl"],
            "CATALOG_SEARCH": ["COMMERCIAL_CATALOG", "bbdd_youngliving_catalogo_v0.4.csv"],
            "BLOG_POSTS": ["BLOG_CONTENT", "youngliving_posts_full.csv", "youngliving_chunks_rag.jsonl"],
            "SAFETY_FALLBACK": ["PROMPT_RULES_PATCH", "Parche_prompt_router_YoungLiving_v0.3.txt"]
        }

    def rerank(self, candidates: List[Dict[str, Any]], route_info: Dict[str, Any], top_k: int = 3) -> List[Dict[str, Any]]:
        target_intent = route_info.get("intent", "")
        primary_source = route_info.get("primary_source", "")
        
        if target_intent == "SAFETY_FALLBACK":
            return [{
                "source": "Parche_prompt_router_YoungLiving_v0.3.txt",
                "priority": 0,
                "content_type": "PROMPT_RULES_PATCH",
                "title": "Aviso y Regla de Seguridad Médica / Ingesta / Sensibilidad",
                "content": self.loader.prompt_rules,
                "rerank_score": 1.0,
                "rationale": "Intercepción prioritaria por regla de seguridad de salud."
            }]

        allowed_targets = self.intent_source_map.get(target_intent, [])

        for cand in candidates:
            sim_score = cand.get("similarity_score", 0.0)
            cand_source = cand.get("source", "")
            cand_type = cand.get("content_type", "")
            cand_priority = cand.get("priority", 10)
            
            cand_base = os.path.basename(cand_source)
            primary_base = os.path.basename(primary_source)
            
            is_matched_source = (
                (cand_source == primary_source) or 
                (cand_base == primary_base) or 
                (cand_type in allowed_targets) or 
                any(cand_base == os.path.basename(t) for t in allowed_targets)
            )
            intent_boost = 1.0 if is_matched_source else 0.0
            
            priority_score = max(0.1, (10 - cand_priority) / 10.0)
            
            final_score = (0.50 * intent_boost) + (0.35 * sim_score) + (0.15 * priority_score)
            cand["rerank_score"] = round(final_score, 4)
            cand["rationale"] = f"Intent Match: {intent_boost} | Similitud: {sim_score:.2f} | Prioridad P{cand_priority}: {priority_score:.2f}"

        sorted_candidates = sorted(candidates, key=lambda x: x.get("rerank_score", 0.0), reverse=True)
        return sorted_candidates[:top_k]


class RAGContextAssembler:
    @staticmethod
    def assemble_payload(query: str, route_info: Dict[str, Any], reranked_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        context_str = ""
        for i, doc in enumerate(reranked_docs, 1):
            context_str += f"\n--- [Documento #{i} | Fuente: {doc['source']} | Prioridad: P{doc.get('priority', 'N/A')}] ---\n"
            context_str += f"Título: {doc.get('title')}\n"
            context_str += f"Contenido:\n{doc.get('content')}\n"
            
        system_prompt = (
            "Eres el Asistente Experto en el Vademécum de Aceites Esenciales Young Living.\n"
            "Responde de forma precisa, amable y segura atendiendo a la intención clasificada y a los documentos recuperados.\n"
            f"Intención Detectada: {route_info['intent']} (Confianza: {route_info['confidence']})\n"
            f"Fuente Primaria Requerida: {route_info['primary_source']}\n"
        )
        
        return {
            "query": query,
            "route_info": route_info,
            "retrieved_context": context_str.strip(),
            "documents": reranked_docs,
            "system_prompt": system_prompt
        }


class YoungLivingRAGPipeline:
    def __init__(self, base_dir: str):
        self.loader = DataSourceLoader(base_dir)
        self.router = IntentRouterEngine(self.loader.router_config, self.loader.prompt_rules)
        self.retriever = MultiSourceRetriever(self.loader)
        self.reranker = PrioritizedReranker(self.loader)

    def execute(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        route_info = self.router.classify(query)
        candidates = self.retriever.search_all_sources(query, route_info)
        reranked_docs = self.reranker.rerank(candidates, route_info, top_k=top_k)
        payload = RAGContextAssembler.assemble_payload(query, route_info, reranked_docs)
        return payload

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pipeline = YoungLivingRAGPipeline(base_dir)
    sample_query = "¿Cuál es la dosis recomendada para difusor de lavanda y menta?"
    result = pipeline.execute(sample_query)
    print("=" * 70)
    print(f"QUERY: {result['query']}")
    print(f"INTENT: {result['route_info']['intent']} (Confianza: {result['route_info']['confidence']})")
    print(f"DOCUMENTOS RECUPERADOS: {len(result['documents'])}")
    for doc in result['documents']:
        print(f" -> [{doc['source']}] (Score: {doc['rerank_score']}) - {doc['title']}")
    print("=" * 70)
