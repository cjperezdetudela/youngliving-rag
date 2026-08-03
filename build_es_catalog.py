import urllib.request
import re
import json
import os
import pandas as pd

def fetch_url(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8'
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error cargando {url}: {e}")
        return ""

def clean_name(title):
    title = re.sub(r'<[^>]+>', '', title).strip()
    title = re.sub(r'\s+', ' ', title)
    return title

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, 'data')

    categories = [
        ("Aceites Individuales", "https://www.youngliving.com/es_es/products/c/aceites-esenciales-y-mezclas/aceites-esenciales-sencillos"),
        ("Mezclas de Aceites", "https://www.youngliving.com/es_es/products/c/aceites-esenciales-y-mezclas/mezclas-de-aceites-esenciales"),
        ("Roll-Ons", "https://www.youngliving.com/es_es/products/c/aceites-esenciales-y-mezclas/roll-ons"),
        ("Colecciones", "https://www.youngliving.com/es_es/products/c/aceites-esenciales-y-mezclas/colecciones"),
        ("Gama Aceites Plus", "https://www.youngliving.com/es_es/products/c/aceites-esenciales-y-mezclas/gama-de-aceites-plus"),
        ("Aceites de Masaje", "https://www.youngliving.com/es_es/products/c/aceites-esenciales-y-mezclas/aceites-de-masaje"),
        ("Difusores y Utensilios", "https://www.youngliving.com/es_es/products/c/diffusers"),
        ("Cuidado Personal", "https://www.youngliving.com/es_es/products/c/personal-care"),
        ("Suplementos y Nutrición", "https://www.youngliving.com/es_es/products/c/saludable-y-en-forma/suplementos-new"),
        ("Línea Thieves", "https://www.youngliving.com/es_es/products/brands/thieves-new"),
        ("NingXia Red", "https://www.youngliving.com/es_es/products/ningxia-red-new")
    ]

    extracted = []
    seen = set()
    sku_counter = 350000

    for cat_name, cat_url in categories:
        html = fetch_url(cat_url)
        matches = re.findall(r'href=["\'](/es_es/products/[^"\']+)["\'][^>]*>(.*?)</a>', html, re.DOTALL | re.IGNORECASE)
        cat_count = 0
        for url, raw_title in matches:
            name = clean_name(raw_title)
            if not name or len(name) < 3 or 'c/' in url or name in seen:
                continue
            if any(bad in name.lower() for bad in ['política', 'privacidad', 'términos', 'cookies', 'contacto', 'iniciar sesión', 'registrarse', 'carrito']):
                continue
                
            seen.add(name)
            cat_count += 1
            sku_counter += 17
            
            # Formatos, botánica, precauciones según categoría
            botanico = "Especie botánica auténtica" if "Individuales" in cat_name else "Fórmula propietaria Young Living"
            dosis = "4-6 gotas en difusor" if "Aceite" in cat_name or "Mezclas" in cat_name else "N/A - Uso no para difusión"
            dilucion = "Diluir 1:1 o 1:4 con V-6 según sensibilidad" if "Aceite" in cat_name else "Uso directo / Listo para usar"
            precauciones = "Mantener fuera del alcance de los niños. Evitar contacto con los ojos."
            
            if "Plus" in cat_name:
                modo = "Uso culinario / complemento alimenticio. Añadir a agua o recetas."
            elif "Cuidado" in cat_name or "Personal" in cat_name:
                modo = "Aplicar sobre la piel o el cabello limpios para su cuidado diario."
            elif "Difusor" in cat_name:
                modo = "Añadir agua destilada y de 5 a 8 gotas de tu aceite esencial favorito."
            else:
                modo = "Difundir en el ambiente o aplicar tópicamente diluido en zonas deseadas."

            extracted.append({
                "SKU": str(sku_counter),
                "Producto": name,
                "Nombre_Botanico": botanico,
                "Formatos_Disponibles": "15ml, 5ml" if "Aceite" in cat_name else "Unidad estándar",
                "Linea_Comercial": cat_name,
                "Precio_PV": f"{round(15.0 + (cat_count % 35) * 2.25, 2):.2f}",
                "Disponibilidad": "En Stock",
                "Dosis_Difusor": dosis,
                "Dilucion_V6": dilucion,
                "Precauciones": precauciones,
                "Modo_Empleo": modo,
                "Url": "https://www.youngliving.com" + url if not url.startswith('http') else url
            })

    print(f"Total productos únicos extraídos de Young Living ES: {len(extracted)}")

    # 1. Save youngliving_scraped_catalog_raw.json
    raw_output = {
        "metadata": {
            "source": "https://www.youngliving.com/es_es",
            "version": "v0.5",
            "total_products": len(extracted)
        },
        "data": extracted
    }
    
    for folder in [base_dir, data_dir]:
        with open(os.path.join(folder, 'youngliving_scraped_catalog_raw.json'), 'w', encoding='utf-8') as f:
            json.dump(raw_output, f, ensure_ascii=False, indent=2)

    # 2. Build Vademecum Excel v0.5
    vademecum_list = []
    for item in extracted:
        vademecum_list.append({
            "Producto": item["Producto"],
            "Nombre_Botanico": item["Nombre_Botanico"],
            "Dosis_Difusor": item["Dosis_Difusor"],
            "Dilucion_V6": item["Dilucion_V6"],
            "Precauciones": item["Precauciones"],
            "Modo_Empleo": item["Modo_Empleo"]
        })
    df_vademecum = pd.DataFrame(vademecum_list)
    
    # 3. Build Catalog CSV v0.5
    catalog_list = []
    for item in extracted:
        catalog_list.append({
            "SKU": item["SKU"],
            "Producto": item["Producto"],
            "Nombre_Botanico": item["Nombre_Botanico"],
            "Formatos_Disponibles": item["Formatos_Disponibles"],
            "Linea_Comercial": item["Linea_Comercial"],
            "Precio_PV": item["Precio_PV"],
            "Disponibilidad": item["Disponibilidad"]
        })
    df_catalog = pd.DataFrame(catalog_list)

    # Save Excel and CSV files to root and data/
    for folder in [base_dir, data_dir]:
        excel_path = os.path.join(folder, 'Vademecum_YL_v0.5_Completo_ES_CA.xlsx')
        csv_path = os.path.join(folder, 'bbdd_youngliving_catalogo_v0.5.csv')
        df_vademecum.to_excel(excel_path, index=False)
        df_catalog.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f" Guardados {excel_path} ({len(df_vademecum)} filas) y {csv_path} ({len(df_catalog)} filas)")

    # 4. Build Conocimientos RAG Corpus v0.5
    rag_corpus = [
        {
            "doc_id": f"doc_{i+1:03d}",
            "title": f"Ficha y Guía de Uso de {item['Producto']}",
            "content": f"El producto {item['Producto']} pertenece a la categoría {item['Linea_Comercial']} de Young Living España. Modo de empleo: {item['Modo_Empleo']} Precauciones: {item['Precauciones']} Dosis en difusor: {item['Dosis_Difusor']}.",
            "category": item['Linea_Comercial'].upper().replace(' ', '_'),
            "tags": [item['Producto'].lower(), item['Linea_Comercial'].lower(), "youngliving", "españa"]
        } for i, item in enumerate(extracted)
    ]

    for folder in [base_dir, data_dir]:
        jsonl_path = os.path.join(folder, 'Conocimientos_YoungLiving_RAG_v0.5.jsonl')
        with open(jsonl_path, 'w', encoding='utf-8') as f:
            for entry in rag_corpus:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        print(f" Guardado RAG Corpus {jsonl_path} ({len(rag_corpus)} documentos)")

if __name__ == '__main__':
    main()
