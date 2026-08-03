import os
import json
import pandas as pd

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Load the scraped raw data (v0.4)
    scraped_file = os.path.join(base_dir, 'youngliving_scraped_catalog_raw.json')
    if not os.path.exists(scraped_file):
        print(f"Error: No se encuentra el archivo {scraped_file}")
        return
        
    with open(scraped_file, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
        
    oils_data = raw_data.get("data", [])
    print(f"Leídos {len(oils_data)} aceites del scraper.")
    
    # 2. Build Vademecum Data (Priority 1)
    vademecum_list = []
    for oil in oils_data:
        vademecum_list.append({
            "Producto": oil.get("Producto"),
            "Nombre_Botanico": oil.get("Nombre_Botanico"),
            "Dosis_Difusor": oil.get("Dosis_Difusor"),
            "Dilucion_V6": oil.get("Dilucion"),
            "Precauciones": oil.get("Precauciones"),
            "Modo_Empleo": oil.get("Modo_Empleo")
        })
        
    df_vademecum = pd.DataFrame(vademecum_list)
    vademecum_excel_path = os.path.join(base_dir, 'Vademecum_YL_v0.4_Completo_ES_CA.xlsx')
    df_vademecum.to_excel(vademecum_excel_path, index=False)
    print(f"Creado: {vademecum_excel_path} con {len(vademecum_list)} registros.")
    
    # 3. Build Catalog Data (Priority 8)
    catalog_list = []
    for oil in oils_data:
        catalog_list.append({
            "SKU": oil.get("SKU"),
            "Producto": oil.get("Producto"),
            "Nombre_Botanico": oil.get("Nombre_Botanico"),
            "Formatos_Disponibles": oil.get("Formatos"),
            "Linea_Comercial": oil.get("Linea"),
            "Precio_PV": oil.get("Precio_PV"),
            "Disponibilidad": "En Stock"
        })
        
    df_catalog = pd.DataFrame(catalog_list)
    catalog_csv_path = os.path.join(base_dir, 'bbdd_youngliving_catalogo_v0.4.csv')
    df_catalog.to_csv(catalog_csv_path, index=False, encoding='utf-8-sig')
    print(f"Creado: {catalog_csv_path} con {len(catalog_list)} registros.")
    
    # 4. Build Conocimientos RAG Corpus (Priority 2) - Upgraded to v0.4
    conocimientos_data = [
        {
            "doc_id": "doc_001",
            "title": "Propiedades Aromáticas y Beneficios Emocionales de Lavanda",
            "content": "El aceite esencial de Lavanda (Lavandula angustifolia / Espígol) es conocido mundialmente como el rey de los aceites esenciales. Ofrece una fragancia floral, dulce y equilibrante que promueve estados profundos de relajación, tranquilidad y bienestar emocional. Ayuda a calmar la mente en momentos de tensión y a preparar un ambiente propicio para el descanso nocturno.",
            "category": "ACEITES_INDIVIDUALES",
            "tags": ["lavanda", "espigol", "emocional", "relax", "sueño"]
        },
        {
            "doc_id": "doc_002",
            "title": "Origen Botánico y Terpenos del Incienso (Frankincense)",
            "content": "El aceite esencial de Incienso proviene de la resina del árbol Boswellia carterii. Rico en alfa-pineno y monoterpenos, su aroma amaderado, balsámico y profundo ha sido utilizado históricamente en prácticas espirituales para fomentar la introspección, la claridad mental y la elevación de la conciencia.",
            "category": "BOTANICA_CONCEPTUAL",
            "tags": ["incienso", "boswellia", "espiritualidad", "meditacion", "terpenos"]
        },
        {
            "doc_id": "doc_003",
            "title": "Energía y Vitalidad con Cítricos y Menta",
            "content": "La combinación de aceites cítricos como el Limón (Citrus limon) y la Menta (Mentha piperita) genera una atmósfera vigorizante y estimulante. El mentol presente en la menta estimula los sentidos, favoreciendo la concentración mental y disipando el cansancio intelectual.",
            "category": "PROPICIEDADES_AROMATICAS",
            "tags": ["menta", "limon", "energia", "concentracion", "bienestar"]
        },
        {
            "doc_id": "doc_004",
            "title": "Historia y Leyenda de la Mezcla Thieves",
            "content": "La famosa mezcla de aceites esenciales Thieves está inspirada en la leyenda de cuatro ladrones franceses del siglo XIV que elaboraron una combinación aromática de clavo, canela, limón, eucalipto y romero para protegerse mientras realizaban sus incursiones. Su aroma especiado es icónico en la línea de bienestar de Young Living.",
            "category": "HISTORIA_TRADICION",
            "tags": ["thieves", "ladrones", "historia", "mezcla", "especiado"]
        }
    ]
    
    conocimientos_jsonl_path = os.path.join(base_dir, 'Conocimientos_YoungLiving_RAG_v0.4.jsonl')
    with open(conocimientos_jsonl_path, 'w', encoding='utf-8') as f:
        for item in conocimientos_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    print(f"Creado: {conocimientos_jsonl_path}")

if __name__ == "__main__":
    main()
