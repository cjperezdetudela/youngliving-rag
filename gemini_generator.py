import os
import re
import html
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


def sanitize_text(text: str) -> str:
    if not text:
        return ""
    # Clean HTML entities
    text = html.unescape(text)
    text = re.sub(r'&#x[0-9a-fA-F]+;', '', text)
    text = re.sub(r'&\w+;', '', text)
    text = text.replace("&quot;", '"').replace("&amp;", '&').replace("&lt;", '<').replace("&gt;", '>')
    
    # Remove markdown line separators '---' or '***'
    text = re.sub(r'^\s*[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)
    
    # Replace markdown headings #### and ### with plain text
    text = re.sub(r'^\s*#{1,6}\s*(.*?)$', r'\1', text, flags=re.MULTILINE)
    
    # Remove ALL asterisks '*' completely from text
    text = text.replace('*', '')

    # Clean up double blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def ensure_closing_question(text: str) -> str:
    text = sanitize_text(text)
    closing = "¿Te puedo ayudar en algo más?"
    
    # Remove existing trailing questions if redundant
    regex_trailing_question = r'(\n+)?(¿.*?\?|\?)\s*$'
    text_clean = re.sub(regex_trailing_question, '', text, flags=re.IGNORECASE).strip()
    
    return f"{text_clean}\n\n{closing}"


class GeminiAdvisorGenerator:
    """
    Módulo de generación de respuestas dinámicas con personalidad humana,
    interlocución activa, respuestas aisladas directas a aclaraciones, sin repetirse
    y sin símbolos '---', '####' ni asteriscos '*'.
    """

    DEFAULT_MODELS = ["gemini-flash-latest", "gemini-flash-lite-latest", "gemini-2.0-flash", "gemini-2.5-flash"]

    def __init__(self, api_key: str = None, preferred_model: str = "gemini-flash-latest"):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        self.preferred_model = preferred_model
        self.client = None

        if GENAI_AVAILABLE and self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
                print(f"[GeminiAdvisorGenerator] Cliente Gemini inicializado correctamente (Modelo primario: {self.preferred_model}).")
            except Exception as e:
                print(f"[GeminiAdvisorGenerator] Error al inicializar cliente Gemini: {e}")
                self.client = None
        else:
            if not GENAI_AVAILABLE:
                print("[GeminiAdvisorGenerator] 'google-genai' no está instalado.")
            if not self.api_key:
                print("[GeminiAdvisorGenerator] No se encontró GEMINI_API_KEY o GOOGLE_API_KEY. Modo Fallback Estructurado Humano activo.")

    def _build_system_instruction(self, route_info: Dict[str, Any], is_safety: bool) -> str:
        instruction = (
            "Eres un Asesor Humano, Empático, Cercano y Experto en Aceites Esenciales, Aromaterapia y Cuidado de la Salud de Young Living y Essenciales.\n"
            "Tu objetivo es comunicarte como una persona cercana, transparente, rigurosa y conversacional.\n\n"
            "REGLAS OBLIGATORIAS DE INTERLOCUCIÓN Y ESTILO:\n"
            "1. RESPUESTA DIRECTA A ACLARACIONES (SIN REPETIRSE): Si el usuario realiza una pregunta concreta de aclaración o sobre un aceite específico (por ejemplo: usar aceite de limón antes de dormir en la cara), responde DIRECTAMENTE a esa duda puntual aislada de forma natural, sin repetir la plantilla previa ni volver a volcar largas listas genéricas.\n"
            "2. SÍMBOLOS STRICTAMENTE PROHIBIDOS: No utilices NUNCA el separador '---', encabezados con '#' ni ASTERISCOS '*'. Está prohibido usar asteriscos para negritas o cursivas. Usa texto plano sin asteriscos, saltos de línea y listas con viñetas limpias usando únicamente '•'.\n"
            "3. FRANQUEZA TOTAL Y SINCERIDAD: Sé transparente respecto al alcance de los aceites esenciales (los aceites son complementos cosméticos/botánicos pero no sustituyen un tratamiento médico prescrito).\n"
            "4. RECETAS DE APLICACIÓN CONCRETAS: Cuando se soliciten recetas, incluye proporciones de dilución en aceite vegetal (V-6, Jojoba), modo de aplicación y advertencias (ej. fotosensibilidad).\n"
            "5. NO USAR CARTELES O BANNERS ROBÓTICOS DE SEGURIDAD.\n"
            "6. CIERRE OBLIGATORIO: Finaliza tu respuesta SIEMPRE con la pregunta de cierre exacta: '¿Te puedo ayudar en algo más?'\n"
        )
        return instruction

    def generate(self, pipeline_output: Dict[str, Any], history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        query = pipeline_output.get("query", "")
        route_info = pipeline_output.get("route_info", {})
        docs = pipeline_output.get("documents", [])
        retrieved_context = pipeline_output.get("retrieved_context", "")
        intent = route_info.get("intent", "")
        is_safety = (intent == "SAFETY_FALLBACK")

        citations = []
        for doc in docs:
            src = doc.get("source")
            if src and src not in citations:
                citations.append(src)

        # Si tenemos cliente de Gemini activo con API Key
        if self.client:
            sys_instruction = self._build_system_instruction(route_info, is_safety)
            
            history_context = ""
            if history:
                history_context = "HISTORIAL PREVIO DE LA CONVERSACIÓN:\n"
                for h in history[-4:]:
                    role = "Usuario" if h.get("role") == "user" else "Asesor"
                    history_context += f"{role}: {h.get('text', '')}\n"
                history_context += "\n"

            prompt = (
                f"{history_context}"
                f"NUEVA CONSULTA CONCRETA DEL USUARIO: {query}\n\n"
                f"CONTEXTO RECUPERADO DE LA BASE DE DATOS:\n{retrieved_context}\n\n"
                "Responde directamente a la nueva consulta aislada sin repetir explicaciones anteriores. "
                "Sin usar asteriscos '*', guiones '---' ni almohadillas '#' y finalizando SIEMPRE con '¿Te puedo ayudar en algo más?'."
            )

            for model_name in [self.preferred_model] + [m for m in self.DEFAULT_MODELS if m != self.preferred_model]:
                try:
                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=sys_instruction,
                            temperature=0.3,
                            max_output_tokens=900,
                        )
                    )
                    if response and response.text:
                        final_text = ensure_closing_question(response.text)
                        return {
                            "role": "assistant",
                            "text": final_text,
                            "citations": citations,
                            "isSafetyFallback": False,
                            "modelUsed": model_name,
                            "status": "success"
                        }
                except Exception as err:
                    print(f"[GeminiAdvisorGenerator] Error al generar con modelo {model_name}: {err}")
                    continue

        # Fallback Conversacional Estructurado Humano
        return self._generate_fallback_response(query, route_info, docs, citations, is_safety, history)

    def _generate_fallback_response(self, query: str, route_info: Dict[str, Any], docs: List[Dict[str, Any]], citations: List[str], is_safety: bool, history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        query_lower = query.lower()

        # Aclaración específica sobre Aceite de Limón en el rostro antes de dormir / sebo
        if "limon" in query_lower or "limón" in query_lower:
            text = (
                "¡Perfecto! Respecto a tu duda concreta sobre usar el aceite esencial de Limón en el rostro antes de dormir para regular el sebo:\n\n"
                "1. ¿Se puede aplicar por la noche?\n"
                "Sí, la noche es precisamente el único momento adecuado para aplicarlo en el rostro. El aceite esencial de Limón es fotosensible. Si se aplicase durante el día, la radiación solar o la luz UV reaccionarían con la piel causando manchas oscuras o irritación. Aplicarlo antes de ir a dormir evita el riesgo fotosensible.\n\n"
                "2. Precauciones y Receta Nocturna de Aplicación:\n"
                "• Nunca aplicarlo puro: La piel del rostro es fina y el aceite de limón puro es muy ácido y astringente.\n"
                "• Receta Nocturna Seborreguladora: Diluye 1 sola gota de Aceite Esencial de Limón en 5 ml (una cucharadita) de Aceite Vegetal de Jojoba o V-6. El aceite vegetal de jojoba equilibra la grasa cutánea por afinidad lipídica sin taponar los poros.\n"
                "• Frecuencia: Aplícalo 2 noches por semana sobre el rostro limpio. Si notas sensibilidad o sequedad, suspende su uso o alterna con la Lavanda."
            )

        # 1. Piel grasa / cuidado facial general
        elif any(term in query_lower for term in ["piel grasa", "grasa", "rostro", "sebo", "acne", "poros", "limpieza facial"]):
            text = (
                "¡Perfecto! Déjame ver qué puedo hacer por ti y consultar en nuestra base de datos las mejores opciones para el cuidado y equilibrio de la piel grasa del rostro.\n\n"
                "Explicación Dermatológica sobre la Piel Grasa\n"
                "La piel grasa se produce por una hiperactividad de las glándulas sebáceas que generan un exceso de sebo en la dermis facial. Un error muy común es utilizar limpiadores agresivos o alcohol que resecan la piel, provocando un efecto rebote donde las glándulas producen aún más sebo para protegerse. Los aceites esenciales seborreguladores y astringentes naturales ayudan a equilibrar la producción grasa sin alterar la barrera protectora cutánea.\n\n"
                "Franqueza sobre nuestras opciones\n"
                "Sinceramente, los aceites esenciales son complementos cosméticos purificantes excepcionales pero no constituyen un fármaco dermatológico. En nuestra base de datos de Young Living y Essenciales disponemos de opciones botánicas probadas de gran eficacia para el rostro:\n\n"
                "Opciones Recomendadas y Recetas de Aplicación Facial\n\n"
                "Opción 1: Aceite Esencial de Árbol de Té (Melaleuca alternifolia)\n"
                "• ¿Por qué ayuda?: Posee intensas propiedades antisépticas, limpiadoras y seborreguladoras que purifican los poros sin obstruirlos.\n"
                "• Receta Serum Matificante: Mezcla 1 gota de Árbol de Té con 5 ml de Aceite Vegetal de Jojoba o V-6. Aplica 2 o 3 gotas de la mezcla sobre el rostro limpio por la noche mediante suaves toques.\n\n"
                "Opción 2: Aceite Esencial de Lavanda (Lavandula angustifolia)\n"
                "• ¿Por qué ayuda?: Es un potente regenerador y calmante cutáneo que reduce el enrojecimiento y equilibra la hidratación de la piel grasa o mixta.\n"
                "• Receta Tónico Facial: Añade 2 gotas de Lavanda a 50 ml de agua destilada o agua de rosas en un pulverizador. Agita y aplica por la mañana antes de tu crema ligera habitual.\n\n"
                "Opción 3: Aceite Esencial de Geranio o Limón\n"
                "• ¿Por qué ayuda?: Tienen acción astringente suave que tonifica y matifica el exceso de brillo tónico en la zona T.\n"
                "• Modo de Empleo: Diluir siempre 1 gota en aceite portador neutro y evitar la exposición solar inmediata en el caso del Limón."
            )

        # 2. Verrugas
        elif "verruga" in query_lower or "verrugas" in query_lower:
            text = (
                "¡Perfecto! Déjame ver qué puedo hacer por ti y revisar detalladamente toda nuestra base de datos de aromaterapia y vademécum.\n\n"
                "Explicación de Salud sobre las Verrugas\n"
                "Las verrugas son pequeñas protuberancias benignas en la capa superficial de la piel causadas habitualmente por la proliferación celular inducida por el Virus del Papiloma Humano (VPH). Requieren un manejo cuidadoso para no irritar la piel sana circundante ni provocar marcas.\n\n"
                "Franqueza sobre nuestra base de datos\n"
                "Sinceramente, debo ser totalmente honesto contigo: no dispongo en nuestro vademécum ni catálogo comercial de un medicamento o tratamiento médico certificado para eliminar verrugas de forma directa. Ningún aceite esencial debe considerarse un fármaco cauterizante médico ni un sustituto de una intervención dermatológica.\n\n"
                "Opciones Botánicas y Recetas Tradicionales de Cuidado Cutáneo\n\n"
                "Opción 1: Aceite Esencial de Orégano (Origanum vulgare)\n"
                "• ¿Por qué ayuda?: Rico en carvacrol y timol, fenoles naturales con intensa acción purificante y cauterizante vegetal.\n"
                "• Receta y Modo de Empleo: Mezcla 1 gota de aceite esencial de Orégano con 4 o 5 gotas de Complejo de Aceites Vegetales V-6. Con ayuda de un bastoncillo de algodón limpia el punto exacto de la verruga 1 vez al día, evitando estrictamente tocar la piel sana alrededor.\n\n"
                "Opción 2: Aceite Esencial de Árbol de Té (Melaleuca alternifolia)\n"
                "• ¿Por qué ayuda?: Reconocido por sus propiedades limpiadoras y regeneradoras cutáneas de amplio espectro.\n"
                "• Receta y Modo de Empleo: Aplica 1 gota de Árbol de Té diluida 1:1 en V-6 directamente sobre la zona antes de acostarte y cubre con una pequeña tirita transpirable."
            )

        # 3. Consultas generales con documentos RAG encontrados
        elif docs:
            clean_title = sanitize_text(docs[0].get('title', 'Información de la Base de Datos'))
            clean_title = re.sub(r'\s*\d+\.\d+\s*PV.*$', '', clean_title)
            clean_content = sanitize_text(docs[0].get('content', ''))

            text = (
                f"¡Perfecto! Déjame ver qué puedo hacer por ti. He consultado nuestra base de datos e información relevante para tu consulta:\n\n"
                f"{clean_title}\n\n"
                f"{clean_content}\n\n"
            )
            if len(docs) > 1:
                text += "Otras opciones y referencias encontradas en el catálogo y blogs:\n"
                for d in docs[1:3]:
                    t_title = sanitize_text(d.get('title', ''))
                    t_title = re.sub(r'\s*\d+\.\d+\s*PV.*$', '', t_title)
                    text += f"• {t_title}: {sanitize_text(d.get('content', ''))[:140]}...\n"

        # 4. Fallback general
        else:
            text = (
                "¡Hola! Déjame ver qué puedo hacer por ti...\n\n"
                "Sinceramente, he buscado en todas nuestras fichas del Vademécum, catálogo y artículos de blog y no he encontrado información directa sobre esa consulta específica."
            )

        final_text = ensure_closing_question(text)

        return {
            "role": "assistant",
            "text": final_text,
            "citations": citations,
            "isSafetyFallback": False,
            "modelUsed": "rag-human-conversational-fallback",
            "status": "fallback"
        }
