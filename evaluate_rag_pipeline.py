import os
import json
import pandas as pd
from datetime import datetime
from rag_retrieval_reranker import YoungLivingRAGPipeline, normalize_text

def run_evaluation():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pipeline = YoungLivingRAGPipeline(base_dir)
    
    test_battery_path = os.path.join(base_dir, 'Bateria_pruebas_YoungLiving_v0.4.jsonl')
    with open(test_battery_path, 'r', encoding='utf-8') as f:
        test_cases = [json.loads(line.strip()) for line in f if line.strip()]
        
    results = []
    correct_intents = 0
    correct_sources = 0
    top1_source_matches = 0
    safety_interceptions = 0
    
    for case in test_cases:
        test_id = case['id']
        query = case['query']
        expected_intent = case['expected_intent']
        expected_source = case['expected_source']
        category = case['category']
        lang = case['language']
        
        pipeline_output = pipeline.execute(query, top_k=3)
        route_info = pipeline_output['route_info']
        docs = pipeline_output['documents']
        
        classified_intent = route_info['intent']
        assigned_source = route_info['primary_source']
        confidence = route_info['confidence']
        
        is_intent_pass = (classified_intent == expected_intent)
        is_source_pass = (assigned_source == expected_source) or (os.path.basename(assigned_source) == os.path.basename(expected_source))
        
        if is_intent_pass:
            correct_intents += 1
        if is_source_pass:
            correct_sources += 1
            
        top1_doc_source = docs[0]['source'] if docs else "N/A"
        blog_sources = ["youngliving_posts_full.csv", "youngliving_chunks_rag.jsonl"]
        top1_match = (
            (top1_doc_source == expected_source) or 
            (os.path.basename(top1_doc_source) == os.path.basename(expected_source)) or
            (os.path.basename(top1_doc_source) in blog_sources and os.path.basename(expected_source) in blog_sources)
        )
        if top1_match:
            top1_source_matches += 1
            
        if classified_intent == "SAFETY_FALLBACK":
            safety_interceptions += 1
            
        results.append({
            "ID_Prueba": test_id,
            "Consulta_Usuario": query,
            "Idioma": lang,
            "Categoria": category,
            "Intencion_Esperada": expected_intent,
            "Intencion_Clasificada": classified_intent,
            "Fuente_Esperada": expected_source,
            "Fuente_Asignada_Router": assigned_source,
            "Top1_Fuente_Reranker": top1_doc_source,
            "Confianza_Score": confidence,
            "Resultado_Intencion": "PASS" if is_intent_pass else "FAIL",
            "Resultado_Fuente_Router": "PASS" if is_source_pass else "FAIL",
            "Resultado_Reranker_Top1": "PASS" if top1_match else "FAIL",
            "Trazabilidad_Razonamiento": route_info['reasoning'],
            "Top1_Documento_Titulo": docs[0]['title'] if docs else "Sin resultados",
            "Top1_Rerank_Score": docs[0].get('rerank_score', 0.0) if docs else 0.0
        })

    total_cases = len(test_cases)
    intent_accuracy = (correct_intents / total_cases) * 100
    source_accuracy = (correct_sources / total_cases) * 100
    reranker_accuracy = (top1_source_matches / total_cases) * 100
    
    print("=" * 75)
    print("EVALUACIÓN DEL PIPELINE DE RAG RERANKING / RETRIEVAL - YOUNGLIVING v0.4")
    print("=" * 75)
    print(f"Total de Casos Evaluados:            {total_cases}")
    print(f"Precisión de Intención (Router):     {intent_accuracy:.2f}% ({correct_intents}/{total_cases})")
    print(f"Precisión de Fuente Primaria:       {source_accuracy:.2f}% ({correct_sources}/{total_cases})")
    print(f"Precisión Reranker Top-1 Match:      {reranker_accuracy:.2f}% ({top1_source_matches}/{total_cases})")
    print(f"Intercepciones de Seguridad (Safety):{safety_interceptions}")
    print("=" * 75)
    
    df_results = pd.DataFrame(results)
    
    summary_data = [
        {"Métrica": "Versión del Pipeline RAG", "Valor": "v0.4 - Catálogo Completo (Prioritized Reranker)"},
        {"Métrica": "Total de Pruebas Evaluadas", "Valor": total_cases},
        {"Métrica": "Precisión de Intención (Router)", "Valor": f"{intent_accuracy:.2f}%"},
        {"Métrica": "Precisión de Asignación de Fuente", "Valor": f"{source_accuracy:.2f}%"},
        {"Métrica": "Precisión Reranker Top-1", "Valor": f"{reranker_accuracy:.2f}%"},
        {"Métrica": "Intercepciones de Seguridad (SAFETY_FALLBACK)", "Valor": safety_interceptions},
        {"Métrica": "Fecha y Hora de Ejecución", "Valor": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    ]
    df_summary = pd.DataFrame(summary_data)
    
    excel_path = os.path.join(base_dir, 'Validacion_funcional_YoungLiving_v0.4_Full_pruebas.xlsx')
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df_summary.to_excel(writer, sheet_name='Resumen_Ejecucion', index=False)
        df_results.to_excel(writer, sheet_name='Trazas_Full_Pruebas', index=False)
        
    json_path = os.path.join(base_dir, 'Validacion_funcional_YoungLiving_v0.4_Full_pruebas.json')
    report_json = {
        "summary": summary_data,
        "traces": results
    }
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(report_json, f, ensure_ascii=False, indent=2)
        
    print(f"Reporte Excel guardado en: {excel_path}")
    print(f"Reporte JSON guardado en:  {json_path}")

if __name__ == "__main__":
    run_evaluation()
