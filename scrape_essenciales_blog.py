import urllib.request
import json
import re
import os
import html
import pandas as pd

def clean_html(raw_html):
    if not raw_html:
        return ""
    # Unescape HTML entities
    text = html.unescape(raw_html)
    # Remove script and style tags
    text = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', text, flags=re.DOTALL | re.IGNORECASE)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def chunk_text(text, title, url, post_id, category, tags, chunk_size=350):
    words = text.split()
    if not words:
        return []
    
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk_words = words[i:i + chunk_size + 50] # Slight overlap
        chunk_str = " ".join(chunk_words)
        chunks.append({
            "chunk_id": f"essenciales_{post_id}_c{len(chunks)+1}",
            "post_id": str(post_id),
            "source": "Essenciales Blog",
            "title": title,
            "url": url,
            "category": category,
            "tags": tags,
            "word_count": len(chunk_words),
            "text": chunk_str
        })
    return chunks

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, 'data')

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    # Fetch Categories mapping
    categories_map = {}
    try:
        req_cat = urllib.request.Request("https://www.essenciales.com/blog/wp-json/wp/v2/categories?per_page=100", headers=headers)
        cats_data = json.loads(urllib.request.urlopen(req_cat).read().decode('utf-8'))
        for c in cats_data:
            categories_map[c['id']] = c['name']
    except Exception as e:
        print("Warning loading categories:", e)

    posts_all = []
    all_chunks = []

    page = 1
    while True:
        url = f"https://www.essenciales.com/blog/wp-json/wp/v2/posts?per_page=100&page={page}"
        print(f"Descargando página {page} de Essenciales Blog...")
        try:
            req = urllib.request.Request(url, headers=headers)
            resp = urllib.request.urlopen(req)
            data = json.loads(resp.read().decode('utf-8'))
            if not data:
                break
            
            for p in data:
                post_id = p.get('id')
                title = clean_html(p.get('title', {}).get('rendered', ''))
                link = p.get('link', '')
                date = p.get('date', '')
                raw_content = p.get('content', {}).get('rendered', '')
                full_text = clean_html(raw_content)
                excerpt = clean_html(p.get('excerpt', {}).get('rendered', ''))
                
                cat_ids = p.get('categories', [])
                cat_names = [categories_map.get(cid, "Aromaterapia") for cid in cat_ids]
                category_str = ", ".join(cat_names) if cat_names else "Aromaterapia"
                
                word_count = len(full_text.split())
                char_count = len(full_text)

                posts_all.append({
                    "id": f"essenciales_{post_id}",
                    "title": title,
                    "url": link,
                    "canonical_url": link,
                    "date": date,
                    "category": category_str,
                    "tags": "essenciales, aromaterapia, aceites",
                    "word_count": word_count,
                    "char_count": char_count,
                    "extraction_quality": "HIGH",
                    "description": excerpt[:300],
                    "full_text": full_text
                })

                # Generate RAG Chunks
                chunks = chunk_text(full_text, title, link, post_id, category_str, ["essenciales", "blog"])
                all_chunks.extend(chunks)

            page += 1
        except Exception as e:
            print(f"Fin de paginación o error en página {page}: {e}")
            break

    print(f"\nTotal artículos extraídos de Essenciales Blog: {len(posts_all)}")
    print(f"Total chunks RAG generados: {len(all_chunks)}")

    # Save to CSV and JSONL in both root and data/
    df_posts = pd.DataFrame(posts_all)

    for folder in [base_dir, data_dir]:
        csv_path = os.path.join(folder, 'essenciales_posts_full.csv')
        jsonl_path = os.path.join(folder, 'essenciales_posts_full.jsonl')
        chunks_path = os.path.join(folder, 'essenciales_chunks_rag.jsonl')

        df_posts.to_csv(csv_path, index=False, encoding='utf-8-sig')
        
        with open(jsonl_path, 'w', encoding='utf-8') as f:
            for p in posts_all:
                f.write(json.dumps(p, ensure_ascii=False) + '\n')

        with open(chunks_path, 'w', encoding='utf-8') as f:
            for c in all_chunks:
                f.write(json.dumps(c, ensure_ascii=False) + '\n')

        print(f" Guardados en {folder}: {csv_path}, {jsonl_path}, {chunks_path}")

if __name__ == '__main__':
    main()
