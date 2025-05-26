import streamlit as st
import requests
import json

# Load API key from Streamlit secrets
api_key = st.secrets["OPENROUTER_API_KEY"]
api_url = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# Initialize session state
if "novel_outline_data" not in st.session_state:
    st.session_state.novel_outline_data = None
if "characters_data" not in st.session_state:
    st.session_state.characters_data = None
if "setting_details" not in st.session_state:
    st.session_state.setting_details = None
if "plot_twist_data" not in st.session_state:
    st.session_state.plot_twist_data = None
if "chapters_data" not in st.session_state:
    st.session_state.chapters_data = None
if "chapter_contents" not in st.session_state:
    st.session_state.chapter_contents = {}
if "chapter_conflicts" not in st.session_state:
    st.session_state.chapter_conflicts = {}
if "chapter_scene_descriptions" not in st.session_state:
    st.session_state.chapter_scene_descriptions = {}
if "chapter_dialogue_snippets" not in st.session_state:
    st.session_state.chapter_dialogue_snippets = {}
if "chapter_sub_plot_ideas" not in st.session_state:
    st.session_state.chapter_sub_plot_ideas = {}
if "chapter_key_events" not in st.session_state:
    st.session_state.chapter_key_events = {}
if "error" not in st.session_state:
    st.session_state.error = None
if "loading" not in st.session_state:
    st.session_state.loading = False

# Function to generate initial novel outline
def generate_initial_outline():
    st.session_state.loading = True
    st.session_state.novel_outline_data = None
    st.session_state.error = None

    theme = st.session_state.user_theme.strip()
    if not theme:
        theme = "una novela histórica de aventuras ambientada en la Guerra de Independencia Española (1808-1814), con un protagonista que lucha contra la ocupación napoleónica, intrigas, resistencia popular, y una visión realista de la época."
    else:
        theme = f"una novela histórica de aventuras ambientada en {theme}. La novela debe presentar un protagonista fuerte, intrigas, y una visión realista de la época."

    prompt = f"Genera la síntesis, la descripción y la trama de {theme} La respuesta debe estar en formato JSON."

    payload = {
        "model": "mistralai/devstral-small:free",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        result = response.json()

        if result.get("choices") and result["choices"][0].get("message") and result["choices"][0]["message"].get("content"):
            jsonString = result["choices"][0]["message"]["content"]
            parsedJson = json.loads(jsonString)
            st.session_state.novel_outline_data = parsedJson
        else:
            st.session_state.error = "No se pudo generar el esquema inicial de la novela. Inténtalo de nuevo."
    except Exception as err:
        st.session_state.error = "Error al conectar con la API para el esquema inicial. Por favor, revisa tu conexión o intenta de nuevo más tarde."
    finally:
        st.session_state.loading = False

# Function to generate main characters
def generate_characters():
    st.session_state.loading = True
    st.session_state.characters_data = None
    st.session_state.error = None

    if not st.session_state.novel_outline_data or not st.session_state.narrative_technique or not st.session_state.narrator_pov:
        st.session_state.error = "Por favor, genera primero el esquema inicial de la novela y selecciona la técnica narrativa y el punto de vista."
        st.session_state.loading = False
        return

    characters_prompt = f"Basándote en la siguiente información de la novela:\nSíntesis General: {st.session_state.novel_outline_data['synthesis']}\nTrama General: {st.session_state.novel_outline_data['plot']}\nTécnica Narrativa: {st.session_state.narrative_technique}\nPunto de Vista del Narrador: {st.session_state.narrator_pov}\n\nGenera 3-5 personajes principales para esta novela. Para cada personaje, proporciona su nombre, su rol en la historia (ej. 'protagonista', 'antagonista', 'aliado', 'interés amoroso'), y una breve descripción de su personalidad y su relevancia para la trama. Responde en formato JSON como un array de objetos, donde cada objeto tiene las propiedades 'name', 'role', y 'description'."

    payload = {
        "model": "mistralai/devstral-small:free",
        "messages": [
            {"role": "user", "content": characters_prompt}
        ]
    }

    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        result = response.json()

        if result.get("choices") and result["choices"][0].get("message") and result["choices"][0]["message"].get("content"):
            jsonString = result["choices"][0]["message"]["content"]
            parsedJson = json.loads(jsonString)
            st.session_state.characters_data = parsedJson
        else:
            st.session_state.error = "No se pudieron generar los personajes. Inténtalo de nuevo."
    except Exception as err:
        st.session_state.error = "Error al generar personajes. Por favor, revisa tu conexión o intenta de nuevo más tarde."
    finally:
        st.session_state.loading = False

# Function to generate setting details
def generate_setting_details():
    st.session_state.loading = True
    st.session_state.setting_details = None
    st.session_state.error = None

    if not st.session_state.novel_outline_data or not st.session_state.characters_data or not st.session_state.narrative_technique or not st.session_state.narrator_pov:
        st.session_state.error = "Por favor, genera primero el esquema inicial, los personajes y selecciona la técnica narrativa y el punto de vista."
        st.session_state.loading = False
        return

    setting_prompt = f"Basándote en el tema de la novela: '{st.session_state.user_theme.strip() or 'Guerra de Independencia Española'}', la descripción general de la novela: '{st.session_state.novel_outline_data['description']}', la técnica narrativa: {st.session_state.narrative_technique} y el punto de vista del narrador: {st.session_state.narrator_pov}, genera una descripción detallada de la ambientación o un aspecto histórico/cultural clave de la novela. Incluye detalles sobre la atmósfera, la sociedad, la vida cotidiana, y elementos visuales relevantes. Aproximadamente 500-700 palabras."

    payload = {
        "model": "mistralai/devstral-small:free",
        "messages": [
            {"role": "user", "content": setting_prompt}
        ]
    }

    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        result = response.json()

        if result.get("choices") and result["choices"][0].get("message") and result["choices"][0]["message"].get("content"):
            content = result["choices"][0]["message"]["content"]
            st.session_state.setting_details = content
        else:
            st.session_state.error = "No se pudieron generar los detalles de ambientación. Inténtalo de nuevo."
    except Exception as err:
        st.session_state.error = "Error al generar detalles de ambientación. Por favor, revisa tu conexión o intenta de nuevo más tarde."
    finally:
        st.session_state.loading = False

# Function to generate plot twist
def generate_plot_twist():
    st.session_state.loading = True
    st.session_state.plot_twist_data = None
    st.session_state.error = None

    if not st.session_state.novel_outline_data or not st.session_state.characters_data or not st.session_state.setting_details or not st.session_state.narrative_technique or not st.session_state.narrator_pov:
        st.session_state.error = "Por favor, genera el esquema inicial, los personajes, la ambientación y selecciona la técnica narrativa y el punto de vista antes de generar giros argumentales."
        st.session_state.loading = False
        return

    plot_twist_prompt = f"Basándote en la síntesis general: \"{st.session_state.novel_outline_data['synthesis']}\", la trama general: \"{st.session_state.novel_outline_data['plot']}\", los personajes: {', '.join([char['name'] for char in st.session_state.characters_data])}, la ambientación: \"{st.session_state.setting_details}\", la técnica narrativa: {st.session_state.narrative_technique} y el punto de vista del narrador: {st.session_state.narrator_pov}, sugiere 1-2 giros argumentales sorprendentes y significativos para la novela. Describe cómo podrían impactar la trama y los personajes. Aproximadamente 300-500 palabras."

    payload = {
        "model": "mistralai/devstral-small:free",
        "messages": [
            {"role": "user", "content": plot_twist_prompt}
        ]
    }

    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        result = response.json()

        if result.get("choices") and result["choices"][0].get("message") and result["choices"][0]["message"].get("content"):
            content = result["choices"][0]["message"]["content"]
            st.session_state.plot_twist_data = content
        else:
            st.session_state.error = "No se pudieron generar los giros argumentales. Inténtalo de nuevo."
    except Exception as err:
        st.session_state.error = "Error al generar giros argumentales. Por favor, revisa tu conexión o intenta de nuevo más tarde."
    finally:
        st.session_state.loading = False

# Function to generate table of contents
def generate_table_of_contents():
    st.session_state.loading = True
    st.session_state.chapters_data = None
    st.session_state.error = None

    if not st.session_state.novel_outline_data or not st.session_state.characters_data or not st.session_state.setting_details or not st.session_state.plot_twist_data or not st.session_state.narrative_technique or not st.session_state.narrator_pov:
        st.session_state.error = "Por favor, genera el esquema inicial, los personajes, la ambientación, los giros argumentales y selecciona la técnica narrativa y el punto de vista antes de generar la tabla de contenidos."
        st.session_state.loading = False
        return

    if st.session_state.num_chapters < 9 or st.session_state.num_chapters > 30:
        st.session_state.error = "El número de capítulos debe estar entre 9 y 30."
        st.session_state.loading = False
        return

    chapters_prompt = f"Basándote en la síntesis general: \"{st.session_state.novel_outline_data['synthesis']}\", la trama general: \"{st.session_state.novel_outline_data['plot']}\", la ambientación: \"{st.session_state.setting_details}\", los personajes principales: {', '.join([char['name'] for char in st.session_state.characters_data])}, los giros argumentales: \"{st.session_state.plot_twist_data}\", la técnica narrativa: {st.session_state.narrative_technique} y el punto de vista del narrador: {st.session_state.narrator_pov}, genera una tabla de contenidos para una novela de {st.session_state.num_chapters} capítulos. Cada capítulo debe tener un título y una breve descripción de su contenido, siguiendo el estilo de una novela histórica de aventuras. Responde en formato JSON como un array of objects, where each object has the properties 'title' and 'description'."

    payload = {
        "model": "mistralai/devstral-small:free",
        "messages": [
            {"role": "user", "content": chapters_prompt}
        ]
    }

    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        result = response.json()

        if result.get("choices") and result["choices"][0].get("message") and result["choices"][0]["message"].get("content"):
            jsonString = result["choices"][0]["message"]["content"]
            parsedJson = json.loads(jsonString)
            st.session_state.chapters_data = parsedJson
        else:
            st.session_state.error = "No se pudo generar la tabla de contenidos. Inténtalo de nuevo."
    except Exception as err:
        st.session_state.error = "Error al generar la tabla de contenidos. Por favor, revisa tu conexión o intenta de nuevo más tarde."
    finally:
        st.session_state.loading = False

# Function to generate chapter content
def generate_chapter_content(chapter, index):
    st.session_state.loading = True
    st.session_state.error = None

    if not st.session_state.novel_outline_data or not st.session_state.chapters_data or not st.session_state.narrative_technique or not st.session_state.narrator_pov:
        st.session_state.error = "Por favor, genera primero el esquema de la novela, la tabla de contenidos y selecciona la técnica narrativa y el punto de vista."
        st.session_state.loading = False
        return

    chapter_prompt = f"Basándote en la siguiente información de la novela:\nSíntesis General: {st.session_state.novel_outline_data['synthesis']}\nTrama General: {st.session_state.novel_outline_data['plot']}\nAmbientación: {st.session_state.setting_details}\nPersonajes Principales: {', '.join([f'{char['name']} ({char['role']})' for char in st.session_state.characters_data])}\nGiros Argumentales de la Novela: {st.session_state.plot_twist_data or 'No especificados'}\nTécnica Narrativa: {st.session_state.narrative_technique}\nPunto de Vista del Narrador: {st.session_state.narrator_pov}\nConflicto del Capítulo: {st.session_state.chapter_conflicts.get(index, 'No especificado')}\nDescripción de Escena del Capítulo: {st.session_state.chapter_scene_descriptions.get(index, 'No especificado')}\nDiálogo del Capítulo: {st.session_state.chapter_dialogue_snippets.get(index, 'No especificado')}\nSubtramas del Capítulo: {st.session_state.chapter_sub_plot_ideas.get(index, 'No especificadas')}\nEventos Clave del Capítulo: {st.session_state.chapter_key_events.get(index, 'No especificados')}\n\nEscribe el contenido completo para el capítulo '{chapter['title']}' (Capítulo {index + 1}). El capítulo debe tener aproximadamente 1200 palabras y expandir la descripción: '{chapter['description']}'. Asegúrate de que el tono y estilo sean coherentes con una novela histórica de aventuras. Asegúrate de que los diálogos utilicen rayas (guion largo '—') en lugar de comillas."

    payload = {
        "model": "mistralai/devstral-small:free",
        "messages": [
            {"role": "user", "content": chapter_prompt}
        ]
    }

    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        result = response.json()

        if result.get("choices") and result["choices"][0].get("message") and result["choices"][0]["message"].get("content"):
            content = result["choices"][0]["message"]["content"]
            st.session_state.chapter_contents[index] = content
        else:
            st.session_state.error = f"No se pudo generar el contenido para el Capítulo {index + 1}. Inténtalo de nuevo."
    except Exception as err:
        st.session_state.error = f"Error al generar el contenido para el Capítulo {index + 1}. Por favor, revisa tu conexión o intenta de nuevo más tarde."
    finally:
        st.session_state.loading = False

# Function to generate chapter conflict
def generate_chapter_conflict(chapter, index):
    st.session_state.loading = True
    st.session_state.error = None

    if not st.session_state.novel_outline_data or not st.session_state.chapters_data or not st.session_state.narrative_technique or not st.session_state.narrator_pov:
        st.session_state.error = "Por favor, genera primero el esquema de la novela, la tabla de contenidos y selecciona la técnica narrativa y el punto de vista."
        st.session_state.loading = False
        return

    conflict_prompt = f"Basándote en la síntesis general de la novela: \"{st.session_state.novel_outline_data['synthesis']}\", la trama general: \"{st.session_state.novel_outline_data['plot']}\", la técnica narrativa: {st.session_state.narrative_technique} y el punto de vista del narrador: {st.session_state.narrator_pov}, y específicamente en el capítulo '{chapter['title']}' (descripción: '{chapter['description']}'), sugiere un conflicto o un obstáculo significativo que podría surgir en este capítulo. Describe la naturaleza del conflicto, sus posibles implicaciones para el protagonista y la trama dentro de este capítulo, y cómo podría resolverse o evolucionar. Aproximadamente 300-500 palabras."

    payload = {
        "model": "mistralai/devstral-small:free",
        "messages": [
            {"role": "user", "content": conflict_prompt}
        ]
    }

    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        result = response.json()

        if result.get("choices") and result["choices"][0].get("message") and result["choices"][0]["message"].get("content"):
            content = result["choices"][0]["message"]["content"]
            st.session_state.chapter_conflicts[index] = content
        else:
            st.session_state.error = f"No se pudo generar el conflicto para el Capítulo {index + 1}. Inténtalo de nuevo."
    except Exception as err:
        st.session_state.error = f"Error al generar el conflicto para el Capítulo {index + 1}. Por favor, revisa tu conexión o intenta de nuevo más tarde."
    finally:
        st.session_state.loading = False

# Function to generate chapter scene description
def generate_chapter_scene_description(chapter, index):
    st.session_state.loading = True
    st.session_state.error = None

    if not st.session_state.novel_outline_data or not st.session_state.chapters_data or not st.session_state.narrative_technique or not st.session_state.narrator_pov:
        st.session_state.error = "Por favor, genera primero el esquema de la novela, la tabla de contenidos y selecciona la técnica narrativa y el punto de vista."
        st.session_state.loading = False
        return

    scene_prompt = f"Basándote en el tema de la novela: '{st.session_state.user_theme.strip() or 'Guerra de Independencia Española'}', la descripción general de la novela: '{st.session_state.novel_outline_data['description']}', la técnica narrativa: {st.session_state.narrative_technique} y el punto de vista del narrador: {st.session_state.narrator_pov}, y específicamente en el capítulo '{chapter['title']}' (descripción: '{chapter['description']}'), genera una descripción detallada de una escena clave o un lugar significativo dentro de este capítulo. Enfócate en los detalles sensoriales (vista, sonido, olfato, tacto), la atmósfera, y cómo el entorno influye en los personajes en esta escena. Aproximadamente 500-700 palabras."

    payload = {
        "model": "mistralai/devstral-small:free",
        "messages": [
            {"role": "user", "content": scene_prompt}
        ]
    }

    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        result = response.json()

        if result.get("choices") and result["choices"][0].get("message") and result["choices"][0]["message"].get("content"):
            content = result["choices"][0]["message"]["content"]
            st.session_state.chapter_scene_descriptions[index] = content
        else:
            st.session_state.error = f"No se pudo generar la descripción de la escena para el Capítulo {index + 1}. Inténtalo de nuevo."
    except Exception as err:
        st.session_state.error = f"Error al generar la descripción de la escena para el Capítulo {index + 1}. Por favor, revisa tu conexión o intenta de nuevo más tarde."
    finally:
        st.session_state.loading = False

# Function to generate chapter dialogue snippet
def generate_chapter_dialogue_snippet(chapter, index):
    st.session_state.loading = True
    st.session_state.error = None

    if not st.session_state.novel_outline_data or not st.session_state.chapters_data or not st.session_state.narrative_technique or not st.session_state.narrator_pov:
        st.session_state.error = "Por favor, genera primero el esquema de la novela, la tabla de contenidos y selecciona la técnica narrativa y el punto de vista."
        st.session_state.loading = False
        return

    dialogue_prompt = f"Basándote en la síntesis general de la novela: \"{st.session_state.novel_outline_data['synthesis']}\", la trama general: \"{st.session_state.novel_outline_data['plot']}\", la técnica narrativa: {st.session_state.narrative_technique} y el punto de vista del narrador: {st.session_state.narrator_pov}, y específicamente en el capítulo '{chapter['title']}' (descripción: '{chapter['description']}'), genera un breve fragmento de diálogo (2-4 líneas) entre dos personajes relevantes para este capítulo. El diálogo debe ser relevante para la trama o los personajes en este punto de la historia, y debe utilizar rayas (guion largo '—') para indicar las intervenciones de los personajes, no comillas."

    payload = {
        "model": "mistralai/devstral-small:free",
        "messages": [
            {"role": "user", "content": dialogue_prompt}
        ]
    }

    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        result = response.json()

        if result.get("choices") and result["choices"][0].get("message") and result["choices"][0]["message"].get("content"):
            content = result["choices"][0]["message"]["content"]
            st.session_state.chapter_dialogue_snippets[index] = content
        else:
            st.session_state.error = f"No se pudo generar el fragmento de diálogo para el Capítulo {index + 1}. Inténtalo de nuevo."
    except Exception as err:
        st.session_state.error = f"Error al generar el fragmento de diálogo para el Capítulo {index + 1}. Por favor, revisa tu conexión o intenta de nuevo más tarde."
    finally:
        st.session_state.loading = False

# Function to generate chapter sub plot ideas
def generate_chapter_sub_plot_ideas(chapter, index):
    st.session_state.loading = True
    st.session_state.error = None

    if not st.session_state.novel_outline_data or not st.session_state.chapters_data or not st.session_state.narrative_technique or not st.session_state.narrator_pov:
        st.session_state.error = "Por favor, genera primero el esquema de la novela, la tabla de contenidos y selecciona la técnica narrativa y el punto de vista."
        st.session_state.loading = False
        return

    sub_plot_prompt = f"Basándote en la síntesis general de la novela: \"{st.session_state.novel_outline_data['synthesis']}\", la trama general: \"{st.session_state.novel_outline_data['plot']}\", la técnica narrativa: {st.session_state.narrative_technique} y el punto de vista del narrador: {st.session_state.narrator_pov}, y específicamente en el capítulo '{chapter['title']}' (descripción: '{chapter['description']}'), sugiere 1-2 ideas para subtramas que puedan enriquecer la narrativa principal en este capítulo o en los siguientes. Para cada idea, describe brevemente la subtrama y cómo podría conectarse con la historia principal o los personajes."

    payload = {
        "model": "mistralai/devstral-small:free",
        "messages": [
            {"role": "user", "content": sub_plot_prompt}
        ]
    }

    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        result = response.json()

        if result.get("choices") and result["choices"][0].get("message") and result["choices"][0]["message"].get("content"):
            content = result["choices"][0]["message"]["content"]
            st.session_state.chapter_sub_plot_ideas[index] = content
        else:
            st.session_state.error = f"No se pudieron generar las ideas de subtramas para el Capítulo {index + 1}. Inténtalo de nuevo."
    except Exception as err:
        st.session_state.error = f"Error al generar ideas de subtramas para el Capítulo {index + 1}. Por favor, revisa tu conexión o intenta de nuevo más tarde."
    finally:
        st.session_state.loading = False

# Function to generate chapter key events
def generate_chapter_key_events(chapter, index):
    st.session_state.loading = True
    st.session_state.error = None

    if not st.session_state.novel_outline_data or not st.session_state.chapters_data or not st.session_state.narrative_technique or not st.session_state.narrator_pov:
        st.session_state.error = "Por favor, genera primero el esquema de la novela, la tabla de contenidos y selecciona la técnica narrativa y el punto de vista."
        st.session_state.loading = False
        return

    key_events_prompt = f"Basándote en la síntesis general de la novela: \"{st.session_state.novel_outline_data['synthesis']}\", la trama general: \"{st.session_state.novel_outline_data['plot']}\", la ambientación: \"{st.session_state.setting_details}\", la técnica narrativa: {st.session_state.narrative_technique} y el punto de vista del narrador: {st.session_state.narrator_pov}, y específicamente en el capítulo '{chapter['title']}' (descripción: '{chapter['description']}'), sugiere 2-3 eventos clave o puntos de inflexión que deberían ocurrir en este capítulo. Describe brevemente cada evento y cómo contribuye al avance de la trama."

    payload = {
        "model": "mistralai/devstral-small:free",
        "messages": [
            {"role": "user", "content": key_events_prompt}
        ]
    }

    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        result = response.json()

        if result.get("choices") and result["choices"][0].get("message") and result["choices"][0]["message"].get("content"):
            content = result["choices"][0]["message"]["content"]
            st.session_state.chapter_key_events[index] = content
        else:
            st.session_state.error = f"No se pudieron generar los eventos clave para el Capítulo {index + 1}. Inténtalo de nuevo."
    except Exception as err:
        st.session_state.error = f"Error al generar eventos clave para el Capítulo {index + 1}. Por favor, revisa tu conexión o intenta de nuevo más tarde."
    finally:
        st.session_state.loading = False

# Helper function to check if all chapter-specific details are generated for a given index
def are_chapter_details_generated(index):
    return (
        st.session_state.chapter_conflicts.get(index) and
        st.session_state.chapter_scene_descriptions.get(index) and
        st.session_state.chapter_dialogue_snippets.get(index) and
        st.session_state.chapter_sub_plot_ideas.get(index) and
        st.session_state.chapter_key_events.get(index)
    )

# Streamlit app layout
st.title("Generador de Novelas Personalizable")

st.write("Introduce el tema o la época para tu novela histórica de aventuras, y generaré su síntesis y trama. Luego podrás generar personajes, ambientación, y finalmente la tabla de contenidos con el número de capítulos que desees.")

# User input for novel theme
st.session_state.user_theme = st.text_area("Tema o Época de la Novela:", placeholder="Ej: la Revolución Francesa, el Antiguo Egipto, la Conquista de América, etc.")

# User input for number of chapters
st.session_state.num_chapters = st.number_input("Número de Capítulos (9-30):", min_value=9, max_value=30, value=25)

# Button to generate initial outline
if st.button("Generar Esquema Inicial"):
    generate_initial_outline()

# Display loading state
if st.session_state.loading:
    st.spinner("Creando el esquema inicial de tu épica aventura...")

# Display error message
if st.session_state.error:
    st.error(st.session_state.error)

# Display novel outline data
if st.session_state.novel_outline_data:
    st.subheader("Síntesis")
    st.write(st.session_state.novel_outline_data["synthesis"])

    st.subheader("Descripción")
    st.write(st.session_state.novel_outline_data["description"])

    st.subheader("Trama")
    st.write(st.session_state.novel_outline_data["plot"])

    # Narrative technique and POV selection
    st.subheader("Selecciona la Técnica Narrativa y el Punto de Vista")
    narrative_technique = st.radio("Técnica Narrativa:", ["first_person", "third_person_omniscient", "third_person_limited"])
    st.session_state.narrative_technique = narrative_technique

    if narrative_technique == "first_person":
        narrator_pov = st.radio("Punto de Vista del Narrador:", ["protagonist", "witness"])
    elif narrative_technique == "third_person_omniscient":
        narrator_pov = st.radio("Punto de Vista del Narrador:", ["omniscient"])
    elif narrative_technique == "third_person_limited":
        narrator_pov = st.radio("Punto de Vista del Narrador:", ["limited"])
    st.session_state.narrator_pov = narrator_pov

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
        for index, chapter in enumerate(st.session_state.chapters_data):
            st.write(f"**{chapter['title']}**")
            st.write(chapter['description'])

            # Buttons for generating chapter-specific details
            if st.button(f"Generar Eventos Clave - Capítulo {index + 1}"):
                generate_chapter_key_events(chapter, index)

            if st.button(f"Generar Conflicto - Capítulo {index + 1}"):
                generate_chapter_conflict(chapter, index)

            if st.button(f"Ideas para Subtramas - Capítulo {index + 1}"):
                generate_chapter_sub_plot_ideas(chapter, index)

            if st.button(f"Descripción de Escena - Capítulo {index + 1}"):
                generate_chapter_scene_description(chapter, index)

            if st.button(f"Generar Diálogo - Capítulo {index + 1}"):
                generate_chapter_dialogue_snippet(chapter, index)

            if st.button(f"Generar Contenido - Capítulo {index + 1}"):
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
