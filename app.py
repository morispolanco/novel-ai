import streamlit as st
import requests
import json
import re
from tenacity import retry, stop_after_attempt, wait_fixed

# API configuration
api_url = "https://openrouter.ai/api/v1/chat/completions"
api_model = st.secrets.get("OPENROUTER_MODEL", "mistralai/devstral-small:free")
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}"
}

# Retry decorator for API calls
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def make_api_request(payload):
    response = requests.post(api_url, headers=headers, data=json.dumps(payload))
    response.raise_for_status()
    return response.json()

# Initialize session state
def initialize_session_state():
    defaults = {
        "novel_outline_data": None,
        "characters_data": None,
        "setting_details": None,
        "plot_twist_data": None,
        "chapters_data": None,
        "chapter_contents": {},
        "chapter_conflicts": {},
        "chapter_scene_descriptions": {},
        "chapter_dialogue_snippets": {},
        "chapter_sub_plot_ideas": {},
        "chapter_key_events": {},
        "error": None,
        "loading_states": {},
        "user_theme": "",
        "num_chapters": 25,
        "narrative_technique": None,
        "narrator_pov": None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Helper function to validate API response
def validate_api_response(result):
    if not (result.get("choices") and isinstance(result["choices"], list) and
            result["choices"][0].get("message") and
            result["choices"][0]["message"].get("content")):
        return None, "Respuesta de la API inválida o vacía."
    return result["choices"][0]["message"]["content"], None

# Helper function to clean and extract JSON from response
def clean_json_content(content):
    # Try to extract JSON from within ```json ... ``` blocks
    json_pattern = r'```json\s*([\s\S]*?)\s*```'
    match = re.search(json_pattern, content)
    if match:
        content = match.group(1).strip()
    
    # Remove any leading/trailing non-JSON text
    try:
        # Find the first { or [ and last } or ]
        start = content.find('{') if '{' in content else content.find('[')
        end = content.rfind('}') if '}' in content else content.rfind(']')
        if start != -1 and end != -1:
            content = content[start:end + 1]
        return content
    except:
        return content

# Helper function to ensure em-dash dialogue
def ensure_em_dash_dialogue(text):
    return text.replace('"', '—')

# Function to generate initial novel outline
def generate_initial_outline():
    st.session_state.loading_states["outline"] = True
    st.session_state.novel_outline_data = None
    st.session_state.error = None

    theme = st.session_state.user_theme.strip()
    if not theme:
        theme = "una novela histórica de aventuras ambientada en la Guerra de Independencia Española (1808-1814), con un protagonista que lucha contra la ocupación napoleónica, intrigas, resistencia popular, y una visión realista de la época."
    elif len(theme) > 500:
        st.session_state.error = "El tema de la novela es demasiado largo. Usa menos de 500 caracteres."
        st.session_state.loading_states["outline"] = False
        return
    else:
        theme = f"una novela histórica de aventuras ambientada en {theme}. La novela debe presentar un protagonista fuerte, intrigas, y una visión realista de la época."

    prompt = f"""
    Genera la síntesis, la descripción y la trama de {theme}. La respuesta debe ser un objeto JSON válido con las propiedades 'synthesis', 'description' y 'plot'. 
    Asegúrate de que la respuesta contenga SOLO el objeto JSON, sin texto adicional, explicaciones ni bloques de código (```). Ejemplo:
    {{"synthesis": "Una novela...", "description": "Ambientada en...", "plot": "La historia sigue..."}}.
    """
    payload = {"model": api_model, "messages": [{"role": "user", "content": prompt}]}

    try:
        with st.spinner("Creando el esquema inicial..."):
            progress_bar = st.progress(0)
            result = make_api_request(payload)
            progress_bar.progress(50)
            content, error = validate_api_response(result)
            if error:
                st.session_state.error = error
            else:
                cleaned_content = clean_json_content(content)
                try:
                    parsed_json = json.loads(cleaned_content)
                    st.session_state.novel_outline_data = parsed_json
                except json.JSONDecodeError as e:
                    st.session_state.error = f"El contenido recibido de la API no es un JSON válido: {str(e)}. Contenido: {cleaned_content}"
                    st.session_state.novel_outline_data = {"raw_content": content}  # Store raw content as fallback
            progress_bar.progress(100)
    except requests.exceptions.RequestException as err:
        st.session_state.error = f"Error al conectar con la API: {str(err)}. Revisa tu conexión."
    finally:
        st.session_state.loading_states["outline"] = False

# Function to generate main characters
def generate_characters():
    st.session_state.loading_states["characters"] = True
    st.session_state.characters_data = None
    st.session_state.error = None

    if not (st.session_state.novel_outline_data and st.session_state.narrative_technique and st.session_state.narrator_pov):
        st.session_state.error = "Genera primero el esquema inicial y selecciona la técnica narrativa y el punto de vista."
        st.session_state.loading_states["characters"] = False
        return

    characters_prompt = f"""
    Basándote en la siguiente información de la novela:
    Síntesis General: {st.session_state.novel_outline_data['synthesis']}
    Trama General: {st.session_state.novel_outline_data['plot']}
    Técnica Narrativa: {st.session_state.narrative_technique}
    Punto de Vista del Narrador: {st.session_state.narrator_pov}
    Genera 3-5 personajes principales para esta novela. Para cada personaje, proporciona su nombre, su rol en la historia (ej. 'protagonista', 'antagonista', 'aliado', 'interés amoroso'), y una breve descripción de su personalidad y su relevancia para la trama. 
    Responde con un array JSON válido que contenga objetos con las propiedades 'name', 'role' y 'description'. 
    Asegúrate de que la respuesta contenga SOLO el array JSON, sin texto adicional, explicaciones ni bloques de código (```). Ejemplo:
    [{{"name": "Juan", "role": "protagonista", "description": "Un joven valiente..."}}, {{"name": "Ana", "role": "aliado", "description": "Una estratega..."}}]
    """
    payload = {"model": api_model, "messages": [{"role": "user", "content": characters_prompt}]}

    try:
        with st.spinner("Generando personajes..."):
            progress_bar = st.progress(0)
            result = make_api_request(payload)
            progress_bar.progress(50)
            content, error = validate_api_response(result)
            if error:
                st.session_state.error = error
            else:
                cleaned_content = clean_json_content(content)
                try:
                    parsed_json = json.loads(cleaned_content)
                    st.session_state.characters_data = parsed_json
                except json.JSONDecodeError as e:
                    st.session_state.error = f"El contenido recibido de la API no es un JSON válido: {str(e)}. Contenido: {cleaned_content}"
                    st.session_state.characters_data = {"raw_content": content}  # Store raw content as fallback
            progress_bar.progress(100)
    except requests.exceptions.RequestException as err:
        st.session_state.error = f"Error al generar personajes: {str(err)}. Revisa tu conexión."
    finally:
        st.session_state.loading_states["characters"] = False

# Function to generate setting details
def generate_setting_details():
    st.session_state.loading_states["setting"] = True
    st.session_state.setting_details = None
    st.session_state.error = None

    if not (st.session_state.novel_outline_data and st.session_state.characters_data and
            st.session_state.narrative_technique and st.session_state.narrator_pov):
        st.session_state.error = "Genera primero el esquema inicial, los personajes y selecciona la técnica narrativa y el punto de vista."
        st.session_state.loading_states["setting"] = False
        return

    setting_prompt = f"""
    Basándote en el tema de la novela: '{st.session_state.user_theme.strip() or 'Guerra de Independencia Española'}',
    la descripción general de la novela: '{st.session_state.novel_outline_data['description']}',
    la técnica narrativa: {st.session_state.narrative_technique} y
    el punto de vista del narrador: {st.session_state.narrator_pov},
    genera una descripción detallada de la ambientación o un aspecto histórico/cultural clave de la novela.
    Incluye detalles sobre la atmósfera, la sociedad, la vida cotidiana, y elementos visuales relevantes. Aproximadamente 500-700 palabras.
    """
    payload = {"model": api_model, "messages": [{"role": "user", "content": setting_prompt}]}

    try:
        with st.spinner("Generando ambientación..."):
            progress_bar = st.progress(0)
            result = make_api_request(payload)
            progress_bar.progress(50)
            content, error = validate_api_response(result)
            if error:
                st.session_state.error = error
            else:
                st.session_state.setting_details = content
            progress_bar.progress(100)
    except requests.exceptions.RequestException as err:
        st.session_state.error = f"Error al generar ambientación: {str(err)}. Revisa tu conexión."
    finally:
        st.session_state.loading_states["setting"] = False

# Function to generate plot twist
def generate_plot_twist():
    st.session_state.loading_states["plot_twist"] = True
    st.session_state.plot_twist_data = None
    st.session_state.error = None

    if not (st.session_state.novel_outline_data and st.session_state.characters_data and
            st.session_state.setting_details and st.session_state.narrative_technique and
            st.session_state.narrator_pov):
        st.session_state.error = "Genera el esquema inicial, los personajes, la ambientación y selecciona la técnica narrativa y el punto de vista antes de generar giros argumentales."
        st.session_state.loading_states["plot_twist"] = False
        return

    plot_twist_prompt = f"""
    Basándote en la síntesis general: "{st.session_state.novel_outline_data['synthesis']}",
    la trama general: "{st.session_state.novel_outline_data['plot']}",
    los personajes: {', '.join([char['name'] for char in st.session_state.characters_data])},
    la ambientación: "{st.session_state.setting_details}",
    la técnica narrativa: {st.session_state.narrative_technique} y
    el punto de vista del narrador: {st.session_state.narrator_pov},
    sugiere 1-2 giros argumentales sorprendentes y significativos para la novela.
    Describe cómo podrían impactar la trama y los personajes. Aproximadamente 300-500 palabras.
    """
    payload = {"model": api_model, "messages": [{"role": "user", "content": plot_twist_prompt}]}

    try:
        with st.spinner("Generando giros argumentales..."):
            progress_bar = st.progress(0)
            result = make_api_request(payload)
            progress_bar.progress(50)
            content, error = validate_api_response(result)
            if error:
                st.session_state.error = error
            else:
                st.session_state.plot_twist_data = content
            progress_bar.progress(100)
    except requests.exceptions.RequestException as err:
        st.session_state.error = f"Error al generar giros argumentales: {str(err)}. Revisa tu conexión."
    finally:
        st.session_state.loading_states["plot_twist"] = False

# Function to generate table of contents
def generate_table_of_contents():
    st.session_state.loading_states["chapters"] = True
    st.session_state.chapters_data = None
    st.session_state.error = None

    if not (st.session_state.novel_outline_data and st.session_state.characters_data and
            st.session_state.setting_details and st.session_state.plot_twist_data and
            st.session_state.narrative_technique and st.session_state.narrator_pov):
        st.session_state.error = "Genera el esquema inicial, los personajes, la ambientación, los giros argumentales y selecciona la técnica narrativa y el punto de vista antes de generar la tabla de contenidos."
        st.session_state.loading_states["chapters"] = False
        return

    if not 9 <= st.session_state.num_chapters <= 30:
        st.session_state.error = "El número de capítulos debe estar entre 9 y 30."
        st.session_state.loading_states["chapters"] = False
        return

    chapters_prompt = f"""
    Basándote en la síntesis general: "{st.session_state.novel_outline_data['synthesis']}",
    la trama general: "{st.session_state.novel_outline_data['plot']}",
    la ambientación: "{st.session_state.setting_details}",
    los personajes principales: {', '.join([char['name'] for char in st.session_state.characters_data])},
    los giros argumentales: "{st.session_state.plot_twist_data}",
    la técnica narrativa: {st.session_state.narrative_technique} y
    el punto de vista del narrador: {st.session_state.narrator_pov},
    genera una tabla de contenidos para una novela de {st.session_state.num_chapters} capítulos.
    Cada capítulo debe tener un título y una breve descripción de su contenido, siguiendo el estilo de una novela histórica de aventuras.
    Responde con un array JSON válido que contenga objetos con las propiedades 'title' y 'description'.
    Asegúrate de que la respuesta contenga SOLO el array JSON, sin texto adicional, explicaciones ni bloques de código (```). Ejemplo:
    [{{"title": "El comienzo", "description": "El protagonista descubre..."}}, {{"title": "La traición", "description": "Un aliado revela..."}}]
    """
    payload = {"model": api_model, "messages": [{"role": "user", "content": chapters_prompt}]}

    try:
        with st.spinner("Generando tabla de contenidos..."):
            progress_bar = st.progress(0)
            result = make_api_request(payload)
            progress_bar.progress(50)
            content, error = validate_api_response(result)
            if error:
                st.session_state.error = error
            else:
                cleaned_content = clean_json_content(content)
                try:
                    parsed_json = json.loads(cleaned_content)
                    st.session_state.chapters_data = parsed_json
                except json.JSONDecodeError as e:
                    st.session_state.error = f"El contenido recibido de la API no es un JSON válido: {str(e)}. Contenido: {cleaned_content}"
                    st.session_state.chapters_data = {"raw_content": content}  # Store raw content as fallback
            progress_bar.progress(100)
    except requests.exceptions.RequestException as err:
        st.session_state.error = f"Error al generar tabla de contenidos: {str(err)}. Revisa tu conexión."
    finally:
        st.session_state.loading_states["chapters"] = False

# Function to generate chapter content
def generate_chapter_content(chapter, index):
    st.session_state.loading_states[f"chapter_content_{index}"] = True
    st.session_state.error = None

    if not (st.session_state.novel_outline_data and st.session_state.chapters_data and
            st.session_state.narrative_technique and st.session_state.narrator_pov):
        st.session_state.error = "Genera primero el esquema de la novela, la tabla de contenidos y selecciona la técnica narrativa y el punto de vista."
        st.session_state.loading_states[f"chapter_content_{index}"] = False
        return

    chapter_prompt = f"""
    Basándote en la siguiente información de la novela:
    Síntesis General: {st.session_state.novel_outline_data['synthesis']}
    Trama General: {st.session_state.novel_outline_data['plot']}
    Ambientación: {st.session_state.setting_details}
    Personajes Principales: {', '.join([f'{char['name']} ({char['role']})' for char in st.session_state.characters_data])}
    Giros Argumentales: {st.session_state.plot_twist_data or 'No especificados'}
    Técnica Narrativa: {st.session_state.narrative_technique}
    Punto de Vista del Narrador: {st.session_state.narrator_pov}
    Conflicto del Capítulo: {st.session_state.chapter_conflicts.get(index, 'No especificado')}
    Descripción de Escena del Capítulo: {st.session_state.chapter_scene_descriptions.get(index, 'No especificado')}
    Diálogo del Capítulo: {st.session_state.chapter_dialogue_snippets.get(index, 'No especificado')}
    Subtramas del Capítulo: {st.session_state.chapter_sub_plot_ideas.get(index, 'No especificadas')}
    Eventos Clave del Capítulo: {st.session_state.chapter_key_events.get(index, 'No especificados')}
    Escribe el contenido completo para el capítulo '{chapter['title']}' (Capítulo {index + 1}).
    El capítulo debe tener aproximadamente 1200 palabras y expandir la descripción: '{chapter['description']}'.
    Asegúrate de que el tono y estilo sean coherentes con una novela histórica de aventuras.
    Asegúrate de que los diálogos utilicen rayas (guion largo '—') en lugar de comillas.
    """
    payload = {"model": api_model, "messages": [{"role": "user", "content": chapter_prompt}]}

    try:
        with st.spinner(f"Generando contenido para el Capítulo {index + 1}..."):
            progress_bar = st.progress(0)
            result = make_api_request(payload)
            progress_bar.progress(50)
            content, error = validate_api_response(result)
            if error:
                st.session_state.error = f"No se pudo generar el contenido para el Capítulo {index + 1}: {error}"
            else:
                st.session_state.chapter_contents[index] = ensure_em_dash_dialogue(content)
            progress_bar.progress(100)
    except requests.exceptions.RequestException as err:
        st.session_state.error = f"Error al generar contenido para el Capítulo {index + 1}: {str(err)}. Revisa tu conexión."
    finally:
        st.session_state.loading_states[f"chapter_content_{index}"] = False

# Function to generate chapter conflict
def generate_chapter_conflict(chapter, index):
    st.session_state.loading_states[f"chapter_conflict_{index}"] = True
    st.session_state.error = None

    if not (st.session_state.novel_outline_data and st.session_state.chapters_data and
            st.session_state.narrative_technique and st.session_state.narrator_pov):
        st.session_state.error = "Genera primero el esquema de la novela, la tabla de contenidos y selecciona la técnica narrativa y el punto de vista."
        st.session_state.loading_states[f"chapter_conflict_{index}"] = False
        return

    conflict_prompt = f"""
    Basándote en la síntesis general de la novela: "{st.session_state.novel_outline_data['synthesis']}",
    la trama general: "{st.session_state.novel_outline_data['plot']}",
    la técnica narrativa: {st.session_state.narrative_technique} y
    el punto de vista del narrador: {st.session_state.narrator_pov},
    y específicamente en el capítulo '{chapter['title']}' (descripción: '{chapter['description']}'),
    sugiere un conflicto o un obstáculo significativo que podría surgir en este capítulo.
    Describe la naturaleza del conflicto, sus posibles implicaciones para el protagonista y la trama dentro de este capítulo, y cómo podría resolverse o evolucionar.
    Aproximadamente 300-500 palabras.
    """
    payload = {"model": api_model, "messages": [{"role": "user", "content": conflict_prompt}]}

    try:
        with st.spinner(f"Generando conflicto para el Capítulo {index + 1}..."):
            progress_bar = st.progress(0)
            result = make_api_request(payload)
            progress_bar.progress(50)
            content, error = validate_api_response(result)
            if error:
                st.session_state.error = f"No se pudo generar el conflicto para el Capítulo {index + 1}: {error}"
            else:
                st.session_state.chapter_conflicts[index] = content
            progress_bar.progress(100)
    except requests.exceptions.RequestException as err:
        st.session_state.error = f"Error al generar conflicto para el Capítulo {index + 1}: {str(err)}. Revisa tu conexión."
    finally:
        st.session_state.loading_states[f"chapter_conflict_{index}"] = False

# Function to generate chapter scene description
def generate_chapter_scene_description(chapter, index):
    st.session_state.loading_states[f"chapter_scene_{index}"] = True
    st.session_state.error = None

    if not (st.session_state.novel_outline_data and st.session_state.chapters_data and
            st.session_state.narrative_technique and st.session_state.narrator_pov):
        st.session_state.error = "Genera primero el esquema de la novela, la tabla de contenidos y selecciona la técnica narrativa y el punto de vista."
        st.session_state.loading_states[f"chapter_scene_{index}"] = False
        return

    scene_prompt = f"""
    Basándote en el tema de la novela: '{st.session_state.user_theme.strip() or 'Guerra de Independencia Española'}',
    la descripción general de la novela: '{st.session_state.novel_outline_data['description']}',
    la técnica narrativa: {st.session_state.narrative_technique} y
    el punto de vista del narrador: {st.session_state.narrator_pov},
    y específicamente en el capítulo '{chapter['title']}' (descripción: '{chapter['description']}'),
    genera una descripción detallada de una escena clave o un lugar significativo dentro de este capítulo.
    Enfócate en los detalles sensoriales (vista, sonido, olfato, tacto), la atmósfera, y cómo el entorno influye en los personajes en esta escena.
    Aproximadamente 500-700 palabras.
    """
    payload = {"model": api_model, "messages": [{"role": "user", "content": scene_prompt}]}

    try:
        with st.spinner(f"Generando descripción de escena para el Capítulo {index + 1}..."):
            progress_bar = st.progress(0)
            result = make_api_request(payload)
            progress_bar.progress(50)
            content, error = validate_api_response(result)
            if error:
                st.session_state.error = f"No se pudo generar la descripción de escena para el Capítulo {index + 1}: {error}"
            else:
                st.session_state.chapter_scene_descriptions[index] = content
            progress_bar.progress(100)
    except requests.exceptions.RequestException as err:
        st.session_state.error = f"Error al generar descripción de escena para el Capítulo {index + 1}: {str(err)}. Revisa tu conexión."
    finally:
        st.session_state.loading_states[f"chapter_scene_{index}"] = False

# Function to generate chapter dialogue snippet
def generate_chapter_dialogue_snippet(chapter, index):
    st.session_state.loading_states[f"chapter_dialogue_{index}"] = True
    st.session_state.error = None

    if not (st.session_state.novel_outline_data and st.session_state.chapters_data and
            st.session_state.narrative_technique and st.session_state.narrator_pov):
        st.session_state.error = "Genera primero el esquema de la novela, la tabla de contenidos y selecciona la técnica narrativa y el punto de vista."
        st.session_state.loading_states[f"chapter_dialogue_{index}"] = False
        return

    dialogue_prompt = f"""
    Basándote en la síntesis general de la novela: "{st.session_state.novel_outline_data['synthesis']}",
    la trama general: "{st.session_state.novel_outline_data['plot']}",
    la técnica narrativa: {st.session_state.narrative_technique} y
    el punto de vista del narrador: {st.session_state.narrator_pov},
    y específicamente en el capítulo '{chapter['title']}' (descripción: '{chapter['description']}'),
    genera un breve fragmento de diálogo (2-4 líneas) entre dos personajes relevantes para este capítulo.
    El diálogo debe ser relevante para la trama o los personajes en este punto de la historia, y debe utilizar rayas (guion largo '—') para indicar las intervenciones de los personajes, no comillas.
    """
    payload = {"model": api_model, "messages": [{"role": "user", "content": dialogue_prompt}]}

    try:
        with st.spinner(f"Generando diálogo para el Capítulo {index + 1}..."):
            progress_bar = st.progress(0)
            result = make_api_request(payload)
            progress_bar.progress(50)
            content, error = validate_api_response(result)
            if error:
                st.session_state.error = f"No se pudo generar el diálogo para el Capítulo {index + 1}: {error}"
            else:
                st.session_state.chapter_dialogue_snippets[index] = ensure_em_dash_dialogue(content)
            progress_bar.progress(100)
    except requests.exceptions.RequestException as err:
        st.session_state.error = f"Error al generar diálogo para el Capítulo {index + 1}: {str(err)}. Revisa tu conexión."
    finally:
        st.session_state.loading_states[f"chapter_dialogue_{index}"] = False

# Function to generate chapter sub plot ideas
def generate_chapter_sub_plot_ideas(chapter, index):
    st.session_state.loading_states[f"chapter_sub_plot_{index}"] = True
    st.session_state.error = None

    if not (st.session_state.novel_outline_data and st.session_state.chapters_data and
            st.session_state.narrative_technique and st.session_state.narrator_pov):
        st.session_state.error = "Genera primero el esquema de la novela, la tabla de contenidos y selecciona la técnica narrativa y el punto de vista."
        st.session_state.loading_states[f"chapter_sub_plot_{index}"] = False
        return

    sub_plot_prompt = f"""
    Basándote en la síntesis general de la novela: "{st.session_state.novel_outline_data['synthesis']}",
    la trama general: "{st.session_state.novel_outline_data['plot']}",
    la técnica narrativa: {st.session_state.narrative_technique} y
    el punto de vista del narrador: {st.session_state.narrator_pov},
    y específicamente en el capítulo '{chapter['title']}' (descripción: '{chapter['description']}'),
    sugiere 1-2 ideas para subtramas que puedan enriquecer la narrativa principal en este capítulo o en los siguientes.
    Para cada idea, describe brevemente la subtrama y cómo podría conectarse con la historia principal o los personajes.
    """
    payload = {"model": api_model, "messages": [{"role": "user", "content": sub_plot_prompt}]}

    try:
        with st.spinner(f"Generando ideas de subtramas para el Capítulo {index + 1}..."):
            progress_bar = st.progress(0)
            result = make_api_request(payload)
            progress_bar.progress(50)
            content, error = validate_api_response(result)
            if error:
                st.session_state.error = f"No se pudieron generar ideas de subtramas para el Capítulo {index + 1}: {error}"
            else:
                st.session_state.chapter_sub_plot_ideas[index] = content
            progress_bar.progress(100)
    except requests.exceptions.RequestException as err:
        st.session_state.error = f"Error al generar ideas de subtramas para el Capítulo {index + 1}: {str(err)}. Revisa tu conexión."
    finally:
        st.session_state.loading_states[f"chapter_sub_plot_{index}"] = False

# Function to generate chapter key events
def generate_chapter_key_events(chapter, index):
    st.session_state.loading_states[f"chapter_key_events_{index}"] = True
    st.session_state.error = None

    if not (st.session_state.novel_outline_data and st.session_state.chapters_data and
            st.session_state.narrative_technique and st.session_state.narrator_pov):
        st.session_state.error = "Genera primero el esquema de la novela, la tabla de contenidos y selecciona la técnica narrativa y el punto de vista."
        st.session_state.loading_states[f"chapter_key_events_{index}"] = False
        return

    key_events_prompt = f"""
    Basándote en la síntesis general de la novela: "{st.session_state.novel_outline_data['synthesis']}",
    la trama general: "{st.session_state.novel_outline_data['plot']}",
    la ambientación: "{st.session_state.setting_details}",
    la técnica narrativa: {st.session_state.narrative_technique} y
    el punto de vista del narrador: {st.session_state.narrator_pov},
    y específicamente en el capítulo '{chapter['title']}' (descripción: '{chapter['description']}'),
    sugiere 2-3 eventos clave o puntos de inflexión que deberían ocurrir en este capítulo.
    Describe brevemente cada evento y cómo contribuye al avance de la trama.
    """
    payload = {"model": api_model, "messages": [{"role": "user", "content": key_events_prompt}]}

    try:
        with st.spinner(f"Generando eventos clave para el Capítulo {index + 1}..."):
            progress_bar = st.progress(0)
            result = make_api_request(payload)
            progress_bar.progress(50)
            content, error = validate_api_response(result)
            if error:
                st.session_state.error = f"No se pudieron generar eventos clave para el Capítulo {index + 1}: {error}"
            else:
                st.session_state.chapter_key_events[index] = content
            progress_bar.progress(100)
    except requests.exceptions.RequestException as err:
        st.session_state.error = f"Error al generar eventos clave para el Capítulo {index + 1}: {str(err)}. Revisa tu conexión."
    finally:
        st.session_state.loading_states[f"chapter_key_events_{index}"] = False

# Streamlit app layout
st.title("Generador de Novelas Personalizable")
st.write("Introduce el tema o la época para tu novela histórica de aventuras, y generaré su síntesis y trama. Luego podrás generar personajes, ambientación, y finalmente la tabla de contenidos con el número de capítulos que desees.")

# Initialize session state
initialize_session_state()

# User input for novel theme
st.session_state.user_theme = st.text_area("Tema o Época de la Novela:", placeholder="Ej: la Revolución Francesa, el Antiguo Egipto, la Conquista de América, etc.")

# User input for number of chapters
st.session_state.num_chapters = st.number_input("Número de Capítulos (9-30):", min_value=9, max_value=30, value=25)

# Button to generate initial outline
if st.button("Generar Esquema Inicial"):
    generate_initial_outline()

# Display error message
if st.session_state.error:
    st.error(st.session_state.error)

# Display novel outline data
if st.session_state.novel_outline_data:
    if isinstance(st.session_state.novel_outline_data, dict) and "raw_content" in st.session_state.novel_outline_data:
        st.subheader("Esquema Inicial (Contenido Crudo - No JSON)")
        st.write(st.session_state.novel_outline_data["raw_content"])
    else:
        st.subheader("Síntesis")
        st.write(st.session_state.novel_outline_data["synthesis"])

        st.subheader("Descripción")
        st.write(st.session_state.novel_outline_data["description"])

        st.subheader("Trama")
        st.write(st.session_state.novel_outline_data["plot"])

    # Narrative technique and POV selection
    st.subheader("Selecciona la Técnica Narrativa y el Punto de Vista")
    st.session_state.narrative_technique = st.radio("Técnica Narrativa:", ["first_person", "third_person_omniscient", "third_person_limited"])
    
    if st.session_state.narrative_technique == "first_person":
        st.session_state.narrator_pov = st.radio("Punto de Vista del Narrador:", ["protagonist", "witness"])
    elif st.session_state.narrative_technique == "third_person_omniscient":
        st.session_state.narrator_pov = st.radio("Punto de Vista del Narrador:", ["omniscient"])
    elif st.session_state.narrative_technique == "third_person_limited":
        st.session_state.narrator_pov = st.radio("Punto de Vista del Narrador:", ["limited"])

    # Buttons for generating characters, setting details, and plot twist
    if st.button("Generar Personajes"):
        generate_characters()

    if st.session_state.characters_data:
        if st.button("Generar Ambientación"):
            generate_setting_details()

    if st.session_state.setting_details:
        if st.button("Generar Giro Argumental"):
            generate_plot_twist()

    # Display generated characters
    if st.session_state.characters_data:
        st.subheader("Personajes Principales")
        if isinstance(st.session_state.characters_data, dict) and "raw_content" in st.session_state.characters_data:
            st.write("Contenido crudo (no JSON):")
            st.write(st.session_state.characters_data["raw_content"])
        else:
            for char in st.session_state.characters_data:
                st.write(f"**{char['name']}** ({char['role']}): {char['description']}")

    # Display generated setting details
    if st.session_state.setting_details:
        st.subheader("Detalles de Ambientación")
        st.write(st.session_state.setting_details)

    # Display generated plot twist
    if st.session_state.plot_twist_data:
        st.subheader("Giros Argumentales Sugeridos")
        st.write(st.session_state.plot_twist_data)

    # Button to generate table of contents
    if st.button("Generar Tabla de Contenidos"):
        generate_table_of_contents()

    # Display table of contents
    if st.session_state.chapters_data:
        st.subheader(f"Tabla de Contenidos ({st.session_state.num_chapters} Capítulos)")
        if isinstance(st.session_state.chapters_data, dict) and "raw_content" in st.session_state.chapters_data:
            st.write("Contenido crudo (no JSON):")
            st.write(st.session_state.chapters_data["raw_content"])
        else:
            for index, chapter in enumerate(st.session_state.chapters_data):
                st.write(f"**{chapter['title']}**")
                st.write(chapter['description'])

                # Buttons for generating chapter-specific details
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"Eventos Clave - Cap. {index + 1}"):
                        generate_chapter_key_events(chapter, index)
                    if st.button(f"Conflicto - Cap. {index + 1}"):
                        generate_chapter_conflict(chapter, index)
                with col2:
                    if st.button(f"Subtramas - Cap. {index + 1}"):
                        generate_chapter_sub_plot_ideas(chapter, index)
                    if st.button(f"Escena - Cap. {index + 1}"):
                        generate_chapter_scene_description(chapter, index)
                with col3:
                    if st.button(f"Diálogo - Cap. {index + 1}"):
                        generate_chapter_dialogue_snippet(chapter, index)
                    if st.button(f"Contenido - Cap. {index + 1}"):
                        generate_chapter_content(chapter, index)

                # Display chapter-specific details
                if st.session_state.chapter_key_events.get(index):
                    st.subheader("Eventos Clave Sugeridos")
                    st.write(st.session_state.chapter_key_events[index])

                if st.session_state.chapter_conflicts.get(index):
                    st.subheader("Conflicto/Obstáculo Sugerido")
                    st.write(st.session_state.chapter_conflicts[index])

                if st.session_state.chapter_sub_plot_ideas.get(index):
                    st.subheader("Ideas para Subtramas")
                    st.write(st.session_state.chapter_sub_plot_ideas[index])

                if st.session_state.chapter_scene_descriptions.get(index):
                    st.subheader("Descripción de Escena Sugerida")
                    st.write(st.session_state.chapter_scene_descriptions[index])

                if st.session_state.chapter_dialogue_snippets.get(index):
                    st.subheader("Fragmento de Diálogo Sugerido")
                    st.write(st.session_state.chapter_dialogue_snippets[index])

                if st.session_state.chapter_contents.get(index):
                    st.subheader("Contenido del Capítulo")
                    st.write(st.session_state.chapter_contents[index])

    # Export novel data
    if st.button("Exportar Novela"):
        novel_data = {
            "outline": st.session_state.novel_outline_data,
            "characters": st.session_state.characters_data,
            "setting": st.session_state.setting_details,
            "plot_twist": st.session_state.plot_twist_data,
            "chapters": st.session_state.chapters_data,
            "chapter_contents": st.session_state.chapter_contents,
            "chapter_conflicts": st.session_state.chapter_conflicts,
            "chapter_scene_descriptions": st.session_state.chapter_scene_descriptions,
            "chapter_dialogue_snippets": st.session_state.chapter_dialogue_snippets,
            "chapter_sub_plot_ideas": st.session_state.chapter_sub_plot_ideas,
            "chapter_key_events": st.session_state.chapter_key_events
        }
        st.download_button(
            label="Descargar Novela",
            data=json.dumps(novel_data, indent=2, ensure_ascii=False),
            file_name="novel_data.json",
            mime="application/json"
        )
