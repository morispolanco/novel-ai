import React, { useState, useEffect } from 'react';

// Main App component
const App = () => {
    // Novel-wide data states
    const [novelOutlineData, setNovelOutlineData] = useState(null); // Stores synthesis, description, plot
    const [charactersData, setCharactersData] = useState(null); // Stores generated character data
    const [settingDetails, setSettingDetails] = useState(null); // Stores generated setting details
    const [plotTwistData, setPlotTwistData] = useState(null); // State for plot twist
    const [chaptersData, setChaptersData] = useState(null); // Stores the chapters array (table of contents)

    // Loading states
    const [loadingOutline, setLoadingOutline] = useState(false);
    const [loadingCharacters, setLoadingCharacters] = useState(false);
    const [loadingSetting, setLoadingSetting] = useState(false);
    const [loadingPlotTwist, setLoadingPlotTwist] = useState(false);
    const [loadingChaptersOutline, setLoadingChaptersOutline] = useState(false);

    // Error state
    const [error, setError] = useState(null);

    // User input states
    const [userTheme, setUserTheme] = useState('');
    const [numChapters, setNumChapters] = useState(25); // Default to 25 chapters
    const [narrativeTechnique, setNarrativeTechnique] = useState(''); // New state for narrative technique
    const [narratorPOV, setNarratorPOV] = useState(''); // New state for narrator POV

    // Chapter-specific data and loading states
    const [chapterContents, setChapterContents] = useState({});
    const [generatingChapterContentIndex, setGeneratingChapterContentIndex] = useState(null);

    const [chapterConflicts, setChapterConflicts] = useState({});
    const [loadingChapterConflictIndex, setLoadingChapterConflictIndex] = useState(null);

    const [chapterSceneDescriptions, setChapterSceneDescriptions] = useState({});
    const [loadingChapterSceneIndex, setLoadingChapterSceneIndex] = useState(null);

    const [chapterDialogueSnippets, setChapterDialogueSnippets] = useState({});
    const [loadingChapterDialogueIndex, setLoadingChapterDialogueIndex] = useState(null);

    const [chapterSubPlotIdeas, setChapterSubPlotIdeas] = useState({});
    const [loadingChapterSubPlotIndex, setLoadingChapterSubPlotIndex] = useState(null);

    const [chapterKeyEvents, setChapterKeyEvents] = useState({});
    const [loadingChapterKeyEventsIndex, setLoadingChapterKeyEventsIndex] = useState(null);

    // Effect to reset narratorPOV when narrativeTechnique changes
    useEffect(() => {
        if (narrativeTechnique === 'first_person') {
            setNarratorPOV('protagonist');
        } else if (narrativeTechnique === 'third_person_omniscient') {
            setNarratorPOV('omniscient');
        } else if (narrativeTechnique === 'third_person_limited') {
            setNarratorPOV('limited');
        } else {
            setNarratorPOV(''); // Clear if no technique selected
        }
    }, [narrativeTechnique]);

    // Function to generate initial novel outline (synthesis, description, plot)
    const generateInitialOutline = async () => {
        setLoadingOutline(true);
        setNovelOutlineData(null);
        // Clear all previous data including narrative choices
        setCharactersData(null);
        setSettingDetails(null);
        setPlotTwistData(null);
        setChaptersData(null);
        setChapterContents({});
        setChapterConflicts({});
        setChapterSceneDescriptions({});
        setChapterDialogueSnippets({});
        setChapterSubPlotIdeas({});
        setChapterKeyEvents({});
        setNarrativeTechnique(''); // Reset narrative choices
        setNarratorPOV(''); // Reset narrative choices
        setError(null);

        const theme = userTheme.trim() === ''
            ? 'una novela histórica de aventuras ambientada en la Guerra de Independencia Española (1808-1814), con un protagonista que lucha contra la ocupación napoleónica, intrigas, resistencia popular, y una visión realista de la época.'
            : `una novela histórica de aventuras ambientada en ${userTheme}. La novela debe presentar un protagonista fuerte, intrigas, y una visión realista de la época.`;

        const prompt = `Genera la síntesis, la descripción y la trama de ${theme} La respuesta debe estar en formato JSON.`;

        let chatHistory = [];
        chatHistory.push({ role: "user", parts: [{ text: prompt }] });

        const payload = {
            contents: chatHistory,
            generationConfig: {
                responseMimeType: "application/json",
                responseSchema: {
                    type: "OBJECT",
                    properties: {
                        "synthesis": { "type": "STRING" },
                        "description": { "type": "STRING" },
                        "plot": { "type": "STRING" },
                    },
                    "propertyOrdering": ["synthesis", "description", "plot"]
                }
            }
        };

        try {
            const apiKey = "";
            const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`;
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (result.candidates && result.candidates.length > 0 &&
                result.candidates[0].content && result.candidates[0].content.parts &&
                result.candidates[0].content.parts.length > 0) {
                const jsonString = result.candidates[0].content.parts[0].text;
                const parsedJson = JSON.parse(jsonString);
                setNovelOutlineData(parsedJson);
            } else {
                setError("No se pudo generar el esquema inicial de la novela. Inténtalo de nuevo.");
                console.error("Unexpected API response structure:", result);
            }
        } catch (err) {
            setError("Error al conectar con la API para el esquema inicial. Por favor, revisa tu conexión o intenta de nuevo más tarde.");
            console.error("Fetch error:", err);
        } finally {
            setLoadingOutline(false);
        }
    };

    // Function to generate main characters (Novel-wide)
    const generateCharacters = async () => {
        setLoadingCharacters(true);
        setCharactersData(null);
        setError(null);

        if (!novelOutlineData || !narrativeTechnique || !narratorPOV) {
            setError("Por favor, genera primero el esquema inicial de la novela y selecciona la técnica narrativa y el punto de vista.");
            setLoadingCharacters(false);
            return;
        }

        const charactersPrompt = `Basándote en la siguiente información de la novela:
Síntesis General: ${novelOutlineData.synthesis}
Trama General: ${novelOutlineData.plot}
Técnica Narrativa: ${narrativeTechnique === 'first_person' ? 'Primera Persona' : narrativeTechnique === 'third_person_omniscient' ? 'Tercera Persona Omnisciente' : 'Tercera Persona Limitada'}
Punto de Vista del Narrador: ${narratorPOV === 'protagonist' ? 'Protagonista' : narratorPOV === 'witness' ? 'Testigo' : narratorPOV === 'omniscient' ? 'Omnisciente' : 'Limitado'}

Genera 3-5 personajes principales para esta novela. Para cada personaje, proporciona su nombre, su rol en la historia (ej. "protagonista", "antagonista", "aliado", "interés amoroso"), y una breve descripción de su personalidad y su relevancia para la trama. Responde en formato JSON como un array de objetos, donde cada objeto tiene las propiedades "name", "role", y "description".`;

        let chatHistory = [];
        chatHistory.push({ role: "user", parts: [{ text: charactersPrompt }] });

        const payload = {
            contents: chatHistory,
            generationConfig: {
                responseMimeType: "application/json",
                responseSchema: {
                    type: "ARRAY",
                    items: {
                        type: "OBJECT",
                        properties: {
                            "name": { "type": "STRING" },
                            "role": { "type": "STRING" },
                            "description": { "type": "STRING" }
                        },
                        "propertyOrdering": ["name", "role", "description"]
                    }
                }
            }
        };

        try {
            const apiKey = "";
            const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`;
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (result.candidates && result.candidates.length > 0 &&
                result.candidates[0].content && result.candidates[0].content.parts &&
                result.candidates[0].content.parts.length > 0) {
                const jsonString = result.candidates[0].content.parts[0].text;
                const parsedJson = JSON.parse(jsonString);
                setCharactersData(parsedJson);
            } else {
                setError("No se pudieron generar los personajes. Inténtalo de nuevo.");
                console.error("Unexpected API response structure for characters:", result);
            }
        } catch (err) {
            setError("Error al generar personajes. Por favor, revisa tu conexión o intenta de nuevo más tarde.");
            console.error("Fetch error for characters:", err);
        } finally {
            setLoadingCharacters(false);
        }
    };

    // Function to generate setting details (Novel-wide)
    const generateSettingDetails = async () => {
        setLoadingSetting(true);
        setSettingDetails(null);
        setError(null);

        if (!novelOutlineData || !charactersData || !narrativeTechnique || !narratorPOV) {
            setError("Por favor, genera primero el esquema inicial, los personajes y selecciona la técnica narrativa y el punto de vista.");
            setLoadingSetting(false);
            return;
        }

        const settingPrompt = `Basándote en el tema de la novela: '${userTheme.trim() === '' ? 'Guerra de Independencia Española' : userTheme}', la descripción general de la novela: '${novelOutlineData.description}', la técnica narrativa: ${narrativeTechnique === 'first_person' ? 'Primera Persona' : narrativeTechnique === 'third_person_omniscient' ? 'Tercera Persona Omnisciente' : 'Tercera Persona Limitada'} y el punto de vista del narrador: ${narratorPOV === 'protagonist' ? 'Protagonista' : narratorPOV === 'witness' ? 'Testigo' : narratorPOV === 'omniscient' ? 'Omnisciente' : 'Limitado'}, genera una descripción detallada de la ambientación o un aspecto histórico/cultural clave de la novela. Incluye detalles sobre la atmósfera, la sociedad, la vida cotidiana, y elementos visuales relevantes. Aproximadamente 500-700 palabras.`;

        let chatHistory = [];
        chatHistory.push({ role: "user", parts: [{ text: settingPrompt }] });

        const payload = {
            contents: chatHistory,
        };

        try {
            const apiKey = "";
            const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`;
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (result.candidates && result.candidates.length > 0 &&
                result.candidates[0].content && result.candidates[0].content.parts &&
                result.candidates[0].content.parts.length > 0) {
                const content = result.candidates[0].content.parts[0].text;
                setSettingDetails(content);
            } else {
                setError("No se pudieron generar los detalles de ambientación. Inténtalo de nuevo.");
                console.error("Unexpected API response structure for setting details:", result);
            }
        } catch (err) {
            setError("Error al generar detalles de ambientación. Por favor, revisa tu conexión o intenta de nuevo más tarde.");
            console.error("Fetch error for setting details:", err);
        } finally {
            setLoadingSetting(false);
        }
    };

    // Function: Generate Plot Twist (Novel-wide)
    const generatePlotTwist = async () => {
        setLoadingPlotTwist(true);
        setPlotTwistData(null);
        setError(null);

        if (!novelOutlineData || !charactersData || !settingDetails || !narrativeTechnique || !narratorPOV) {
            setError("Por favor, genera el esquema inicial, los personajes, la ambientación y selecciona la técnica narrativa y el punto de vista antes de generar giros argumentales.");
            setLoadingPlotTwist(false);
            return;
        }

        const plotTwistPrompt = `Basándote en la síntesis general: "${novelOutlineData.synthesis}", la trama general: "${novelOutlineData.plot}", los personajes: ${charactersData ? charactersData.map(c => c.name).join(', ') : 'No disponibles'}, la ambientación: "${settingDetails}", la técnica narrativa: ${narrativeTechnique === 'first_person' ? 'Primera Persona' : narrativeTechnique === 'third_person_omniscient' ? 'Tercera Persona Omnisciente' : 'Tercera Persona Limitada'} y el punto de vista del narrador: ${narratorPOV === 'protagonist' ? 'Protagonista' : narratorPOV === 'witness' ? 'Testigo' : narratorPOV === 'omniscient' ? 'Omnisciente' : 'Limitado'}, sugiere 1-2 giros argumentales sorprendentes y significativos para la novela. Describe cómo podrían impactar la trama y los personajes. Aproximadamente 300-500 palabras.`;

        let chatHistory = [];
        chatHistory.push({ role: "user", parts: [{ text: plotTwistPrompt }] });

        const payload = {
            contents: chatHistory,
        };

        try {
            const apiKey = "";
            const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`;
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (result.candidates && result.candidates.length > 0 &&
                result.candidates[0].content && result.candidates[0].content.parts &&
                result.candidates[0].content.parts.length > 0) {
                const content = result.candidates[0].content.parts[0].text;
                setPlotTwistData(content);
            } else {
                setError("No se pudieron generar los giros argumentales. Inténtalo de nuevo.");
                console.error("Unexpected API response structure for plot twist:", result);
            }
        } catch (err) {
            setError("Error al generar giros argumentales. Por favor, revisa tu conexión o intenta de nuevo más tarde.");
            console.error("Fetch error for plot twist:", err);
        } finally {
            setLoadingPlotTwist(false);
        }
    };


    // Function: Generate Table of Contents
    const generateTableOfContents = async () => {
        setLoadingChaptersOutline(true);
        setChaptersData(null);
        setError(null);

        if (!novelOutlineData || !charactersData || !settingDetails || !plotTwistData || !narrativeTechnique || !narratorPOV) {
            setError("Por favor, genera el esquema inicial, los personajes, la ambientación, los giros argumentales y selecciona la técnica narrativa y el punto de vista antes de generar la tabla de contenidos.");
            setLoadingChaptersOutline(false);
            return;
        }

        if (numChapters < 9 || numChapters > 30) {
            setError("El número de capítulos debe estar entre 9 y 30.");
            setLoadingChaptersOutline(false);
            return;
        }

        const chaptersPrompt = `Basándote en la síntesis general: "${novelOutlineData.synthesis}", la trama general: "${novelOutlineData.plot}", la ambientación: "${settingDetails}", los personajes principales: ${charactersData ? charactersData.map(c => c.name).join(', ') : 'No disponibles'}, los giros argumentales: "${plotTwistData}", la técnica narrativa: ${narrativeTechnique === 'first_person' ? 'Primera Persona' : narrativeTechnique === 'third_person_omniscient' ? 'Tercera Persona Omnisciente' : 'Tercera Persona Limitada'} y el punto de vista del narrador: ${narratorPOV === 'protagonist' ? 'Protagonista' : narratorPOV === 'witness' ? 'Testigo' : narratorPOV === 'omniscient' ? 'Omnisciente' : 'Limitado'}, genera una tabla de contenidos para una novela de ${numChapters} capítulos. Cada capítulo debe tener un título y una breve descripción de su contenido, siguiendo el estilo de una novela histórica de aventuras. Responde en formato JSON como un array de objetos, donde cada objeto tiene las propiedades "title" y "description".`;

        let chatHistory = [];
        chatHistory.push({ role: "user", parts: [{ text: chaptersPrompt }] });

        const payload = {
            contents: chatHistory,
            generationConfig: {
                responseMimeType: "application/json",
                responseSchema: {
                    type: "ARRAY",
                    items: {
                        type: "OBJECT",
                        properties: {
                            "title": { "type": "STRING" },
                            "description": { "type": "STRING" }
                        },
                        "propertyOrdering": ["title", "description"]
                    },
                    "minItems": numChapters,
                    "maxItems": numChapters
                }
            }
        };

        try {
            const apiKey = "";
            const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`;
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (result.candidates && result.candidates.length > 0 &&
                result.candidates[0].content && result.candidates[0].content.parts &&
                result.candidates[0].content.parts.length > 0) {
                const jsonString = result.candidates[0].content.parts[0].text;
                const parsedJson = JSON.parse(jsonString);
                setChaptersData(parsedJson);
            } else {
                setError("No se pudo generar la tabla de contenidos. Inténtalo de nuevo.");
                console.error("Unexpected API response structure for chapters outline:", result);
            }
        } catch (err) {
            setError("Error al generar la tabla de contenidos. Por favor, revisa tu conexión o intenta de nuevo más tarde.");
            console.error("Fetch error for chapters outline:", err);
        } finally {
            setLoadingChaptersOutline(false);
        }
    };

    // Function to generate content for a specific chapter
    const generateChapterContent = async (chapter, index) => {
        setGeneratingChapterContentIndex(index);
        setError(null);

        if (!novelOutlineData || !chaptersData || !narrativeTechnique || !narratorPOV) {
            setError("Por favor, genera primero el esquema de la novela, la tabla de contenidos y selecciona la técnica narrativa y el punto de vista.");
            setGeneratingChapterContentIndex(null);
            return;
        }

        const chapterPrompt = `Basándote en la siguiente información de la novela:
Síntesis General: ${novelOutlineData.synthesis}
Trama General: ${novelOutlineData.plot}
Ambientación: ${settingDetails}
Personajes Principales: ${charactersData ? charactersData.map(c => `${c.name} (${c.role})`).join(', ') : 'No disponibles'}
Giros Argumentales de la Novela: ${plotTwistData || 'No especificados'}
Técnica Narrativa: ${narrativeTechnique === 'first_person' ? 'Primera Persona' : narrativeTechnique === 'third_person_omniscient' ? 'Tercera Persona Omnisciente' : 'Tercera Persona Limitada'}
Punto de Vista del Narrador: ${narratorPOV === 'protagonist' ? 'Protagonista' : narratorPOV === 'witness' ? 'Testigo' : narratorPOV === 'omniscient' ? 'Omnisciente' : 'Limitado'}
Conflicto del Capítulo: ${chapterConflicts[index] || 'No especificado'}
Descripción de Escena del Capítulo: ${chapterSceneDescriptions[index] || 'No especificado'}
Diálogo del Capítulo: ${chapterDialogueSnippets[index] || 'No especificado'}
Subtramas del Capítulo: ${chapterSubPlotIdeas[index] || 'No especificadas'}
Eventos Clave del Capítulo: ${chapterKeyEvents[index] || 'No especificados'}

Escribe el contenido completo para el capítulo '${chapter.title}' (Capítulo ${index + 1}). El capítulo debe tener aproximadamente 1200 palabras y expandir la descripción: '${chapter.description}'. Asegúrate de que el tono y estilo sean coherentes con una novela histórica de aventuras. Asegúrate de que los diálogos utilicen rayas (guion largo '—') en lugar de comillas.`;

        let chatHistory = [];
        chatHistory.push({ role: "user", parts: [{ text: chapterPrompt }] });

        const payload = {
            contents: chatHistory,
        };

        try {
            const apiKey = "";
            const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`;
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (result.candidates && result.candidates.length > 0 &&
                result.candidates[0].content && result.candidates[0].content.parts &&
                result.candidates[0].content.parts.length > 0) {
                const content = result.candidates[0].content.parts[0].text;
                setChapterContents(prevContents => ({
                    ...prevContents,
                    [index]: content
                }));
            } else {
                setError(`No se pudo generar el contenido para el Capítulo ${index + 1}. Inténtalo de nuevo.`);
                console.error("Unexpected API response structure for chapter content:", result);
            }
        } catch (err) {
            setError(`Error al generar el contenido para el Capítulo ${index + 1}. Por favor, revisa tu conexión o intenta de nuevo más tarde.`);
            console.error("Fetch error for chapter content:", err);
        } finally {
            setGeneratingChapterContentIndex(null);
        }
    };

    // Function: Generate Conflict/Obstacle (Chapter-specific)
    const generateChapterConflict = async (chapter, index) => {
        setLoadingChapterConflictIndex(index);
        setError(null);

        if (!novelOutlineData || !chaptersData || !narrativeTechnique || !narratorPOV) {
            setError("Por favor, genera primero el esquema de la novela, la tabla de contenidos y selecciona la técnica narrativa y el punto de vista.");
            setLoadingChapterConflictIndex(null);
            return;
        }

        const conflictPrompt = `Basándote en la síntesis general de la novela: "${novelOutlineData.synthesis}", la trama general: "${novelOutlineData.plot}", la técnica narrativa: ${narrativeTechnique === 'first_person' ? 'Primera Persona' : narrativeTechnique === 'third_person_omniscient' ? 'Tercera Persona Omnisciente' : 'Tercera Persona Limitada'} y el punto de vista del narrador: ${narratorPOV === 'protagonist' ? 'Protagonista' : narratorPOV === 'witness' ? 'Testigo' : narratorPOV === 'omniscient' ? 'Omnisciente' : 'Limitado'}, y específicamente en el capítulo '${chapter.title}' (descripción: '${chapter.description}'), sugiere un conflicto o un obstáculo significativo que podría surgir en este capítulo. Describe la naturaleza del conflicto, sus posibles implicaciones para el protagonista y la trama dentro de este capítulo, y cómo podría resolverse o evolucionar. Aproximadamente 300-500 palabras.`;

        let chatHistory = [];
        chatHistory.push({ role: "user", parts: [{ text: conflictPrompt }] });

        const payload = {
            contents: chatHistory,
        };

        try {
            const apiKey = "";
            const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`;
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (result.candidates && result.candidates.length > 0 &&
                result.candidates[0].content && result.candidates[0].content.parts &&
                result.candidates[0].content.parts.length > 0) {
                const content = result.candidates[0].content.parts[0].text;
                setChapterConflicts(prev => ({ ...prev, [index]: content }));
            } else {
                setError(`No se pudo generar el conflicto para el Capítulo ${index + 1}. Inténtalo de nuevo.`);
                console.error("Unexpected API response structure for chapter conflict:", result);
            }
        } catch (err) {
            setError(`Error al generar el conflicto para el Capítulo ${index + 1}. Por favor, revisa tu conexión o intenta de nuevo más tarde.`);
            console.error("Fetch error for chapter conflict:", err);
        } finally {
            setLoadingChapterConflictIndex(null);
        }
    };

    // Function: Generate Scene Description (Chapter-specific)
    const generateChapterSceneDescription = async (chapter, index) => {
        setLoadingChapterSceneIndex(index);
        setError(null);

        if (!novelOutlineData || !chaptersData || !narrativeTechnique || !narratorPOV) {
            setError("Por favor, genera primero el esquema de la novela, la tabla de contenidos y selecciona la técnica narrativa y el punto de vista.");
            setLoadingChapterSceneIndex(null);
            return;
        }

        const scenePrompt = `Basándote en el tema de la novela: '${userTheme.trim() === '' ? 'Guerra de Independencia Española' : userTheme}', la descripción general de la novela: '${novelOutlineData.description}', la técnica narrativa: ${narrativeTechnique === 'first_person' ? 'Primera Persona' : narrativeTechnique === 'third_person_omniscient' ? 'Tercera Persona Omnisciente' : 'Tercera Persona Limitada'} y el punto de vista del narrador: ${narratorPOV === 'protagonist' ? 'Protagonista' : narratorPOV === 'witness' ? 'Testigo' : narratorPOV === 'omniscient' ? 'Omnisciente' : 'Limitado'}, y específicamente en el capítulo '${chapter.title}' (descripción: '${chapter.description}'), genera una descripción detallada de una escena clave o un lugar significativo dentro de este capítulo. Enfócate en los detalles sensoriales (vista, sonido, olfato, tacto), la atmósfera, y cómo el entorno influye en los personajes en esta escena. Aproximadamente 500-700 palabras.`;

        let chatHistory = [];
        chatHistory.push({ role: "user", parts: [{ text: scenePrompt }] });

        const payload = {
            contents: chatHistory,
        };

        try {
            const apiKey = "";
            const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`;
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (result.candidates && result.candidates.length > 0 &&
                result.candidates[0].content && result.candidates[0].content.parts &&
                result.candidates[0].content.parts.length > 0) {
                const content = result.candidates[0].content.parts[0].text;
                setChapterSceneDescriptions(prev => ({ ...prev, [index]: content }));
            } else {
                setError(`No se pudo generar la descripción de la escena para el Capítulo ${index + 1}. Inténtalo de nuevo.`);
                console.error("Unexpected API response structure for chapter scene description:", result);
            }
        } catch (err) {
            setError(`Error al generar la descripción de la escena para el Capítulo ${index + 1}. Por favor, revisa tu conexión o intenta de nuevo más tarde.`);
            console.error("Fetch error for chapter scene description:", err);
        } finally {
            setLoadingChapterSceneIndex(null);
        }
    };

    // Function: Generate Dialogue Snippet (Chapter-specific)
    const generateChapterDialogueSnippet = async (chapter, index) => {
        setLoadingChapterDialogueIndex(index);
        setError(null);

        if (!novelOutlineData || !chaptersData || !narrativeTechnique || !narratorPOV) {
            setError("Por favor, genera primero el esquema de la novela, la tabla de contenidos y selecciona la técnica narrativa y el punto de vista.");
            setLoadingChapterDialogueIndex(null);
            return;
        }

        const dialoguePrompt = `Basándote en la síntesis general de la novela: "${novelOutlineData.synthesis}", la trama general: "${novelOutlineData.plot}", la técnica narrativa: ${narrativeTechnique === 'first_person' ? 'Primera Persona' : narrativeTechnique === 'third_person_omniscient' ? 'Tercera Persona Omnisciente' : 'Tercera Persona Limitada'} y el punto de vista del narrador: ${narratorPOV === 'protagonist' ? 'Protagonista' : narratorPOV === 'witness' ? 'Testigo' : narratorPOV === 'omniscient' ? 'Omnisciente' : 'Limitado'}, y específicamente en el capítulo '${chapter.title}' (descripción: '${chapter.description}'), genera un breve fragmento de diálogo (2-4 líneas) entre dos personajes relevantes para este capítulo. El diálogo debe ser relevante para la trama o los personajes en este punto de la historia, y debe utilizar rayas (guion largo '—') para indicar las intervenciones de los personajes, no comillas.`;

        let chatHistory = [];
        chatHistory.push({ role: "user", parts: [{ text: dialoguePrompt }] });

        const payload = {
            contents: chatHistory,
        };

        try {
            const apiKey = "";
            const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`;
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (result.candidates && result.candidates.length > 0 &&
                result.candidates[0].content && result.candidates[0].content.parts &&
                result.candidates[0].content.parts.length > 0) {
                const content = result.candidates[0].content.parts[0].text;
                setChapterDialogueSnippets(prev => ({ ...prev, [index]: content }));
            } else {
                setError(`No se pudo generar el fragmento de diálogo para el Capítulo ${index + 1}. Inténtalo de nuevo.`);
                console.error("Unexpected API response structure for chapter dialogue snippet:", result);
            }
        } catch (err) {
            setError(`Error al generar el fragmento de diálogo para el Capítulo ${index + 1}. Por favor, revisa tu conexión o intenta de nuevo más tarde.`);
            console.error("Fetch error for chapter dialogue snippet:", err);
        } finally {
            setLoadingChapterDialogueIndex(null);
        }
    };

    // Function: Generate Subplot Ideas (Chapter-specific)
    const generateChapterSubPlotIdeas = async (chapter, index) => {
        setLoadingChapterSubPlotIndex(index);
        setError(null);

        if (!novelOutlineData || !chaptersData || !narrativeTechnique || !narratorPOV) {
            setError("Por favor, genera primero el esquema de la novela, la tabla de contenidos y selecciona la técnica narrativa y el punto de vista.");
            setLoadingChapterSubPlotIndex(null);
            return;
        }

        const subPlotPrompt = `Basándote en la síntesis general de la novela: "${novelOutlineData.synthesis}", la trama general: "${novelOutlineData.plot}", la técnica narrativa: ${narrativeTechnique === 'first_person' ? 'Primera Persona' : narrativeTechnique === 'third_person_omniscient' ? 'Tercera Persona Omnisciente' : 'Tercera Persona Limitada'} y el punto de vista del narrador: ${narratorPOV === 'protagonist' ? 'Protagonista' : narratorPOV === 'witness' ? 'Testigo' : narratorPOV === 'omniscient' ? 'Omnisciente' : 'Limitado'}, y específicamente en el capítulo '${chapter.title}' (descripción: '${chapter.description}'), sugiere 1-2 ideas para subtramas que puedan enriquecer la narrativa principal en este capítulo o en los siguientes. Para cada idea, describe brevemente la subtrama y cómo podría conectarse con la historia principal o los personajes.`;

        let chatHistory = [];
        chatHistory.push({ role: "user", parts: [{ text: subPlotPrompt }] });

        const payload = {
            contents: chatHistory,
        };

        try {
            const apiKey = "";
            const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`;
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (result.candidates && result.candidates.length > 0 &&
                result.candidates[0].content && result.candidates[0].content.parts &&
                result.candidates[0].content.parts.length > 0) {
                const content = result.candidates[0].content.parts[0].text;
                setChapterSubPlotIdeas(prev => ({ ...prev, [index]: content }));
            } else {
                setError(`No se pudieron generar las ideas de subtramas para el Capítulo ${index + 1}. Inténtalo de nuevo.`);
                console.error("Unexpected API response structure for chapter subplot ideas:", result);
            }
        } catch (err) {
            setError(`Error al generar ideas de subtramas para el Capítulo ${index + 1}. Por favor, revisa tu conexión o intenta de nuevo más tarde.`);
            console.error("Fetch error for chapter subplot ideas:", err);
        } finally {
            setLoadingChapterSubPlotIndex(null);
        }
    };

    // Function: Generate Key Events (Chapter-specific)
    const generateChapterKeyEvents = async (chapter, index) => {
        setLoadingChapterKeyEventsIndex(index);
        setError(null);

        if (!novelOutlineData || !chaptersData || !narrativeTechnique || !narratorPOV) {
            setError("Por favor, genera primero el esquema de la novela, la tabla de contenidos y selecciona la técnica narrativa y el punto de vista.");
            setLoadingChapterKeyEventsIndex(null);
            return;
        }

        const keyEventsPrompt = `Basándote en la síntesis general de la novela: "${novelOutlineData.synthesis}", la trama general: "${novelOutlineData.plot}", la ambientación: "${settingDetails}", la técnica narrativa: ${narrativeTechnique === 'first_person' ? 'Primera Persona' : narrativeTechnique === 'third_person_omniscient' ? 'Tercera Persona Omnisciente' : 'Tercera Persona Limitada'} y el punto de vista del narrador: ${narratorPOV === 'protagonist' ? 'Protagonista' : narratorPOV === 'witness' ? 'Testigo' : narratorPOV === 'omniscient' ? 'Omnisciente' : 'Limitado'}, y específicamente en el capítulo '${chapter.title}' (descripción: '${chapter.description}'), sugiere 2-3 eventos clave o puntos de inflexión que deberían ocurrir en este capítulo. Describe brevemente cada evento y cómo contribuye al avance de la trama.`;

        let chatHistory = [];
        chatHistory.push({ role: "user", parts: [{ text: keyEventsPrompt }] });

        const payload = {
            contents: chatHistory,
        };

        try {
            const apiKey = "";
            const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`;
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (result.candidates && result.candidates.length > 0 &&
                result.candidates[0].content && result.candidates[0].content.parts &&
                result.candidates[0].content.parts.length > 0) {
                const content = result.candidates[0].content.parts[0].text;
                setChapterKeyEvents(prev => ({ ...prev, [index]: content }));
            } else {
                setError(`No se pudieron generar los eventos clave para el Capítulo ${index + 1}. Inténtalo de nuevo.`);
                console.error("Unexpected API response structure for chapter key events:", result);
            }
        } catch (err) {
            setError(`Error al generar eventos clave para el Capítulo ${index + 1}. Por favor, revisa tu conexión o intenta de nuevo más tarde.`);
            console.error("Fetch error for chapter key events:", err);
        } finally {
            setLoadingChapterKeyEventsIndex(null);
        }
    };

    // Helper function to check if all chapter-specific details are generated for a given index
    const areChapterDetailsGenerated = (index) => {
        return (
            chapterConflicts[index] &&
            chapterSceneDescriptions[index] &&
            chapterDialogueSnippets[index] &&
            chapterSubPlotIdeas[index] &&
            chapterKeyEvents[index]
        );
    };

    const handleNumChaptersChange = (e) => {
        const value = parseInt(e.target.value, 10);
        if (!isNaN(value) && value >= 9 && value <= 30) {
            setNumChapters(value);
            setError(null); // Clear error if input is valid
        } else if (e.target.value === '') {
            setNumChapters(''); // Allow empty for user to type
            setError(null);
        } else {
            setError("El número de capítulos debe estar entre 9 y 30.");
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 text-gray-100 p-4 sm:p-8 font-serif">
            <div className="max-w-4xl mx-auto bg-gray-800 rounded-xl shadow-2xl p-6 sm:p-10 border border-gray-700">
                <h1 className="text-4xl sm:text-5xl font-bold text-center text-amber-400 mb-8 tracking-wide">
                    Generador de Novelas Personalizable
                </h1>

                <p className="text-center text-gray-300 mb-8 text-lg">
                    Introduce el tema o la época para tu novela histórica de aventuras, y generaré su síntesis y trama. Luego podrás generar personajes, ambientación, y finalmente la tabla de contenidos con el número de capítulos que desees.
                </p>

                <div className="mb-6">
                    <label htmlFor="novelTheme" className="block text-amber-200 text-xl font-semibold mb-3">
                        Tema o Época de la Novela:
                    </label>
                    <textarea
                        id="novelTheme"
                        className="w-full p-4 bg-gray-700 text-gray-100 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500 text-lg resize-y min-h-[100px]"
                        placeholder="Ej: la Revolución Francesa, el Antiguo Egipto, la Conquista de América, etc."
                        value={userTheme}
                        onChange={(e) => setUserTheme(e.target.value)}
                    ></textarea>
                </div>

                <div className="mb-6">
                    <label htmlFor="numChapters" className="block text-amber-200 text-xl font-semibold mb-3">
                        Número de Capítulos (9-30):
                    </label>
                    <input
                        id="numChapters"
                        type="number"
                        min="9"
                        max="30"
                        className="w-full p-4 bg-gray-700 text-gray-100 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500 text-lg"
                        value={numChapters}
                        onChange={handleNumChaptersChange}
                    />
                </div>

                <div className="flex justify-center mb-10">
                    <button
                        onClick={generateInitialOutline}
                        disabled={loadingOutline}
                        className={`px-8 py-4 rounded-full text-xl font-semibold transition-all duration-300 ease-in-out
                            ${loadingOutline ? 'bg-gray-600 cursor-not-allowed' : 'bg-amber-500 hover:bg-amber-600 text-gray-900 shadow-lg transform hover:scale-105'}
                            focus:outline-none focus:ring-4 focus:ring-amber-500 focus:ring-opacity-50`}
                    >
                        {loadingOutline ? 'Generando Esquema Inicial...' : 'Generar Esquema Inicial'}
                    </button>
                </div>

                {loadingOutline && (
                    <div className="text-center text-amber-400 text-lg">
                        <div className="animate-spin inline-block w-8 h-8 border-4 border-amber-400 border-t-transparent rounded-full mb-4"></div>
                        <p>Creando el esquema inicial de tu épica aventura...</p>
                    </div>
                )}

                {error && (
                    <div className="bg-red-800 text-red-200 p-4 rounded-lg text-center border border-red-700">
                        <p>{error}</p>
                    </div>
                )}

                {novelOutlineData && (
                    <div className="mt-10 space-y-8">
                        {/* Synthesis */}
                        <section className="bg-gray-700 p-6 rounded-lg shadow-inner border border-gray-600">
                            <h2 className="text-3xl font-semibold text-amber-300 mb-4 border-b border-amber-400 pb-2">
                                Síntesis
                            </h2>
                            <p className="text-gray-200 leading-relaxed text-lg">{novelOutlineData.synthesis}</p>
                        </section>

                        {/* Description */}
                        <section className="bg-gray-700 p-6 rounded-lg shadow-inner border border-gray-600">
                            <h2 className="text-3xl font-semibold text-amber-300 mb-4 border-b border-amber-400 pb-2">
                                Descripción
                            </h2>
                            <p className="text-gray-200 leading-relaxed text-lg">{novelOutlineData.description}</p>
                        </section>

                        {/* Plot */}
                        <section className="bg-gray-700 p-6 rounded-lg shadow-inner border border-gray-600">
                            <h2 className="text-3xl font-semibold text-amber-300 mb-4 border-b border-amber-400 pb-2">
                                Trama
                            </h2>
                            <p className="text-gray-200 leading-relaxed text-lg">{novelOutlineData.plot}</p>
                        </section>

                        {/* New section for Narrative Technique and POV */}
                        <div className="mb-6 bg-gray-700 p-6 rounded-lg shadow-inner border border-gray-600">
                            <h2 className="text-3xl font-semibold text-amber-300 mb-4 border-b border-amber-400 pb-2">
                                Selecciona la Técnica Narrativa y el Punto de Vista
                            </h2>
                            <div className="flex flex-col sm:flex-row gap-6">
                                <div className="flex-1">
                                    <label className="block text-amber-200 text-xl font-semibold mb-2">
                                        Técnica Narrativa:
                                    </label>
                                    <div className="space-y-2">
                                        <label className="inline-flex items-center">
                                            <input
                                                type="radio"
                                                className="form-radio text-amber-500 h-5 w-5"
                                                name="narrativeTechnique"
                                                value="first_person"
                                                checked={narrativeTechnique === 'first_person'}
                                                onChange={(e) => setNarrativeTechnique(e.target.value)}
                                            />
                                            <span className="ml-2 text-gray-200 text-lg">Primera Persona</span>
                                        </label>
                                        <label className="inline-flex items-center ml-4">
                                            <input
                                                type="radio"
                                                className="form-radio text-amber-500 h-5 w-5"
                                                name="narrativeTechnique"
                                                value="third_person_omniscient"
                                                checked={narrativeTechnique === 'third_person_omniscient'}
                                                onChange={(e) => setNarrativeTechnique(e.target.value)}
                                            />
                                            <span className="ml-2 text-gray-200 text-lg">Tercera Persona Omnisciente</span>
                                        </label>
                                        <label className="inline-flex items-center ml-4">
                                            <input
                                                type="radio"
                                                className="form-radio text-amber-500 h-5 w-5"
                                                name="narrativeTechnique"
                                                value="third_person_limited"
                                                checked={narrativeTechnique === 'third_person_limited'}
                                                onChange={(e) => setNarrativeTechnique(e.target.value)}
                                            />
                                            <span className="ml-2 text-gray-200 text-lg">Tercera Persona Limitada</span>
                                        </label>
                                    </div>
                                </div>
                                <div className="flex-1">
                                    <label className="block text-amber-200 text-xl font-semibold mb-2">
                                        Punto de Vista del Narrador:
                                    </label>
                                    <div className="space-y-2">
                                        {narrativeTechnique === 'first_person' && (
                                            <>
                                                <label className="inline-flex items-center">
                                                    <input
                                                        type="radio"
                                                        className="form-radio text-amber-500 h-5 w-5"
                                                        name="narratorPOV"
                                                        value="protagonist"
                                                        checked={narratorPOV === 'protagonist'}
                                                        onChange={(e) => setNarratorPOV(e.target.value)}
                                                    />
                                                    <span className="ml-2 text-gray-200 text-lg">Protagonista</span>
                                                </label>
                                                <label className="inline-flex items-center ml-4">
                                                    <input
                                                        type="radio"
                                                        className="form-radio text-amber-500 h-5 w-5"
                                                        name="narratorPOV"
                                                        value="witness"
                                                        checked={narratorPOV === 'witness'}
                                                        onChange={(e) => setNarratorPOV(e.target.value)}
                                                    />
                                                    <span className="ml-2 text-gray-200 text-lg">Testigo</span>
                                                </label>
                                            </>
                                        )}
                                        {narrativeTechnique === 'third_person_omniscient' && (
                                            <label className="inline-flex items-center">
                                                <input
                                                    type="radio"
                                                    className="form-radio text-amber-500 h-5 w-5"
                                                    name="narratorPOV"
                                                    value="omniscient"
                                                    checked={narratorPOV === 'omniscient'}
                                                    onChange={(e) => setNarratorPOV(e.target.value)}
                                                />
                                                <span className="ml-2 text-gray-200 text-lg">Omnisciente</span>
                                            </label>
                                        )}
                                        {narrativeTechnique === 'third_person_limited' && (
                                            <label className="inline-flex items-center">
                                                <input
                                                    type="radio"
                                                    className="form-radio text-amber-500 h-5 w-5"
                                                    name="narratorPOV"
                                                    value="limited"
                                                    checked={narratorPOV === 'limited'}
                                                    onChange={(e) => setNarratorPOV(e.target.value)}
                                                />
                                                <span className="ml-2 text-gray-200 text-lg">Limitado</span>
                                            </label>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>


                        {/* Novel-wide Feature Buttons - Characters, Setting, Plot Twist */}
                        <div className="flex flex-col sm:flex-row justify-center gap-4 mt-8 flex-wrap">
                            <button
                                onClick={generateCharacters}
                                disabled={loadingCharacters || !novelOutlineData || !narrativeTechnique || !narratorPOV}
                                className={`px-6 py-3 rounded-full text-lg font-semibold transition-all duration-300 ease-in-out
                                    ${loadingCharacters ? 'bg-purple-600 cursor-not-allowed' : 'bg-purple-500 hover:bg-purple-600 text-white shadow-lg transform hover:scale-105'}
                                    focus:outline-none focus:ring-4 focus:ring-purple-500 focus:ring-opacity-50`}
                            >
                                {loadingCharacters ? 'Generando Personajes...' : 'Generar Personajes ✨'}
                            </button>
                            {charactersData && ( // Only show "Generar Ambientación" button after characters are generated
                                <button
                                    onClick={generateSettingDetails}
                                    disabled={loadingSetting || !novelOutlineData || !charactersData || !narrativeTechnique || !narratorPOV}
                                    className={`px-6 py-3 rounded-full text-lg font-semibold transition-all duration-300 ease-in-out
                                        ${loadingSetting ? 'bg-green-600 cursor-not-allowed' : 'bg-green-500 hover:bg-green-600 text-white shadow-lg transform hover:scale-105'}
                                        focus:outline-none focus:ring-4 focus:ring-green-500 focus:ring-opacity-50`}
                                >
                                    {loadingSetting ? 'Generando Ambientación...' : 'Detalles de Ambientación ✨'}
                                </button>
                            )}
                            {settingDetails && ( // Only show "Generar Giros Argumentales" button after setting details are generated
                                <button
                                    onClick={generatePlotTwist}
                                    disabled={loadingPlotTwist || !novelOutlineData || !charactersData || !settingDetails || !narrativeTechnique || !narratorPOV}
                                    className={`px-6 py-3 rounded-full text-lg font-semibold transition-all duration-300 ease-in-out
                                        ${loadingPlotTwist ? 'bg-red-600 cursor-not-allowed' : 'bg-red-500 hover:bg-red-600 text-white shadow-lg transform hover:scale-105'}
                                        focus:outline-none focus:ring-4 focus:ring-red-500 focus:ring-opacity-50`}
                                >
                                    {loadingPlotTwist ? 'Generando Giro...' : 'Generar Giro Argumental ✨'}
                                </button>
                            )}
                        </div>

                        {/* Display Generated Characters */}
                        {loadingCharacters && (
                            <div className="text-center text-purple-400 text-lg mt-4">
                                <div className="animate-spin inline-block w-6 h-6 border-3 border-purple-400 border-t-transparent rounded-full mr-2"></div>
                                Creando personajes...
                            </div>
                        )}
                        {charactersData && (
                            <section className="bg-gray-700 p-6 rounded-lg shadow-inner border border-gray-600 mt-8">
                                <h2 className="text-3xl font-semibold text-purple-300 mb-4 border-b border-purple-400 pb-2">
                                    Personajes Principales
                                </h2>
                                <ul className="list-disc list-inside space-y-3 text-gray-200 text-lg">
                                    {charactersData.map((char, idx) => (
                                        <li key={idx}>
                                            <strong className="text-purple-200">{char.name}</strong> ({char.role}): {char.description}
                                        </li>
                                    ))}
                                </ul>
                            </section>
                        )}

                        {/* Display Generated Setting Details */}
                        {loadingSetting && (
                            <div className="text-center text-green-400 text-lg mt-4">
                                <div className="animate-spin inline-block w-6 h-6 border-3 border-green-400 border-t-transparent rounded-full mr-2"></div>
                                Detallando la ambientación...
                            </div>
                        )}
                        {settingDetails && (
                            <section className="bg-gray-700 p-6 rounded-lg shadow-inner border border-gray-600 mt-8">
                                <h2 className="text-3xl font-semibold text-green-300 mb-4 border-b border-green-400 pb-2">
                                    Detalles de Ambientación
                                </h2>
                                <p className="text-gray-200 leading-relaxed text-lg whitespace-pre-wrap">{settingDetails}</p>
                            </section>
                        )}

                        {/* Display Generated Plot Twist */}
                        {loadingPlotTwist && (
                            <div className="text-center text-red-400 text-lg mt-4">
                                <div className="animate-spin inline-block w-6 h-6 border-3 border-red-400 border-t-transparent rounded-full mr-2"></div>
                                Generando giros argumentales...
                            </div>
                        )}
                        {plotTwistData && (
                            <section className="bg-gray-700 p-6 rounded-lg shadow-inner border border-gray-600 mt-8">
                                <h2 className="text-3xl font-semibold text-red-300 mb-4 border-b border-red-400 pb-2">
                                    Giros Argumentales Sugeridos
                                </h2>
                                <p className="text-gray-200 leading-relaxed text-lg whitespace-pre-wrap">{plotTwistData}</p>
                            </section>
                        )}


                        {/* Generate Table of Contents Button - Renders conditionally */}
                        {novelOutlineData && charactersData && settingDetails && plotTwistData && !chaptersData && (
                            <div className="flex justify-center mt-8">
                                <button
                                    onClick={generateTableOfContents}
                                    disabled={loadingChaptersOutline || numChapters < 9 || numChapters > 30 || !narrativeTechnique || !narratorPOV}
                                    className={`px-8 py-4 rounded-full text-xl font-semibold transition-all duration-300 ease-in-out
                                        ${loadingChaptersOutline ? 'bg-blue-600 cursor-not-allowed' : 'bg-blue-500 hover:bg-blue-600 text-white shadow-lg transform hover:scale-105'}
                                        focus:outline-none focus:ring-4 focus:ring-blue-500 focus:ring-opacity-50`}
                                >
                                    {loadingChaptersOutline ? 'Generando Tabla de Contenidos...' : 'Generar Tabla de Contenidos'}
                                </button>
                            </div>
                        )}

                        {loadingChaptersOutline && (
                            <div className="text-center text-blue-400 text-lg mt-4">
                                <div className="animate-spin inline-block w-6 h-6 border-3 border-blue-400 border-t-transparent rounded-full mr-2"></div>
                                Creando la tabla de contenidos...
                            </div>
                        )}

                        {/* Table of Contents - Renders conditionally */}
                        {chaptersData && (
                            <section className="bg-gray-700 p-6 rounded-lg shadow-inner border border-gray-600 mt-8">
                                <h2 className="text-3xl font-semibold text-amber-300 mb-4 border-b border-amber-400 pb-2">
                                    Tabla de Contenidos ({numChapters} Capítulos)
                                </h2>
                                <ol className="list-decimal list-inside space-y-4 text-gray-200 text-lg">
                                    {chaptersData.map((chapter, index) => (
                                        <li key={index} className="pl-4 mb-4 bg-gray-750 p-4 rounded-md border border-gray-600">
                                            <div className="flex flex-col gap-2">
                                                <strong className="text-amber-200 text-xl">{chapter.title}</strong>
                                                <p className="text-gray-300 mb-2">{chapter.description}</p>

                                                <div className="flex flex-wrap gap-2 mt-2">
                                                    {/* Reordered buttons */}
                                                    <button
                                                        onClick={() => generateChapterKeyEvents(chapter, index)}
                                                        disabled={loadingChapterKeyEventsIndex !== null}
                                                        className={`px-4 py-2 rounded-full text-md font-semibold transition-all duration-300 ease-in-out
                                                            ${loadingChapterKeyEventsIndex === index ? 'bg-purple-600 cursor-not-allowed' : 'bg-purple-500 hover:bg-purple-600 text-white shadow-md transform hover:scale-105'}
                                                            focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-opacity-50`}
                                                    >
                                                        {loadingChapterKeyEventsIndex === index ? 'Generando Eventos...' : 'Generar Eventos Clave ✨'}
                                                    </button>
                                                    <button
                                                        onClick={() => generateChapterConflict(chapter, index)}
                                                        disabled={loadingChapterConflictIndex !== null}
                                                        className={`px-4 py-2 rounded-full text-md font-semibold transition-all duration-300 ease-in-out
                                                            ${loadingChapterConflictIndex === index ? 'bg-red-600 cursor-not-allowed' : 'bg-red-500 hover:bg-red-600 text-white shadow-md transform hover:scale-105'}
                                                            focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-opacity-50`}
                                                    >
                                                        {loadingChapterConflictIndex === index ? 'Generando Conflicto...' : 'Generar Conflicto ✨'}
                                                    </button>
                                                    <button
                                                        onClick={() => generateChapterSubPlotIdeas(chapter, index)}
                                                        disabled={loadingChapterSubPlotIndex !== null}
                                                        className={`px-4 py-2 rounded-full text-md font-semibold transition-all duration-300 ease-in-out
                                                            ${loadingChapterSubPlotIndex === index ? 'bg-orange-600 cursor-not-allowed' : 'bg-orange-500 hover:bg-orange-600 text-white shadow-md transform hover:scale-105'}
                                                            focus:outline-none focus:ring-4 focus:ring-orange-500 focus:ring-opacity-50`}
                                                    >
                                                        {loadingChapterSubPlotIndex === index ? 'Generando Subtramas...' : 'Ideas para Subtramas ✨'}
                                                    </button>
                                                    <button
                                                        onClick={() => generateChapterSceneDescription(chapter, index)}
                                                        disabled={loadingChapterSceneIndex !== null}
                                                        className={`px-4 py-2 rounded-full text-md font-semibold transition-all duration-300 ease-in-out
                                                            ${loadingChapterSceneIndex === index ? 'bg-yellow-600 cursor-not-allowed' : 'bg-yellow-500 hover:bg-yellow-600 text-gray-900 shadow-md transform hover:scale-105'}
                                                            focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:ring-opacity-50`}
                                                    >
                                                        {loadingChapterSceneIndex === index ? 'Generando Escena...' : 'Descripción de Escena ✨'}
                                                    </button>
                                                    <button
                                                        onClick={() => generateChapterDialogueSnippet(chapter, index)}
                                                        disabled={loadingChapterDialogueIndex !== null}
                                                        className={`px-4 py-2 rounded-full text-md font-semibold transition-all duration-300 ease-in-out
                                                            ${loadingChapterDialogueIndex === index ? 'bg-indigo-600 cursor-not-allowed' : 'bg-indigo-500 hover:bg-indigo-600 text-white shadow-md transform hover:scale-105'}
                                                            focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-opacity-50`}
                                                    >
                                                        {loadingChapterDialogueIndex === index ? 'Generando Diálogo...' : 'Generar Diálogo ✨'}
                                                    </button>
                                                    {/* "Generar Contenido" button at the end, dependent on all other chapter details */}
                                                    <button
                                                        onClick={() => generateChapterContent(chapter, index)}
                                                        disabled={generatingChapterContentIndex !== null || !areChapterDetailsGenerated(index)}
                                                        className={`px-4 py-2 rounded-full text-md font-semibold transition-all duration-300 ease-in-out
                                                            ${generatingChapterContentIndex === index ? 'bg-blue-600 cursor-not-allowed' :
                                                            !areChapterDetailsGenerated(index) ? 'bg-gray-600 cursor-not-allowed' : 'bg-blue-500 hover:bg-blue-600 text-white shadow-md transform hover:scale-105'}
                                                            focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50`}
                                                    >
                                                        {generatingChapterContentIndex === index ? 'Generando Contenido...' : 'Generar Contenido'}
                                                    </button>
                                                </div>
                                            </div>

                                            {/* Display Chapter Content */}
                                            {chapterContents[index] && (
                                                <div className="mt-4 p-4 bg-gray-800 rounded-lg border border-gray-700 text-gray-200 whitespace-pre-wrap">
                                                    <h3 className="text-xl font-semibold text-amber-300 mb-2">Contenido del Capítulo:</h3>
                                                    {chapterContents[index]}
                                                </div>
                                            )}
                                            {generatingChapterContentIndex === index && (
                                                <div className="text-center text-blue-400 text-lg mt-4">
                                                    <div className="animate-spin inline-block w-6 h-6 border-3 border-blue-400 border-t-transparent rounded-full mr-2"></div>
                                                    Cargando contenido del capítulo...
                                                </div>
                                            )}

                                            {/* Display Chapter Key Events */}
                                            {chapterKeyEvents[index] && (
                                                <div className="mt-4 p-4 bg-gray-800 rounded-lg border border-gray-700 text-gray-200 whitespace-pre-wrap">
                                                    <h3 className="text-xl font-semibold text-purple-300 mb-2">Eventos Clave Sugeridos:</h3>
                                                    {chapterKeyEvents[index]}
                                                </div>
                                            )}
                                            {loadingChapterKeyEventsIndex === index && (
                                                <div className="text-center text-purple-400 text-lg mt-4">
                                                    <div className="animate-spin inline-block w-6 h-6 border-3 border-purple-400 border-t-transparent rounded-full mr-2"></div>
                                                    Generando eventos clave para el capítulo...
                                                </div>
                                            )}

                                            {/* Display Chapter Conflict */}
                                            {chapterConflicts[index] && (
                                                <div className="mt-4 p-4 bg-gray-800 rounded-lg border border-gray-700 text-gray-200 whitespace-pre-wrap">
                                                    <h3 className="text-xl font-semibold text-red-300 mb-2">Conflicto/Obstáculo Sugerido:</h3>
                                                    {chapterConflicts[index]}
                                                </div>
                                            )}
                                            {loadingChapterConflictIndex === index && (
                                                <div className="text-center text-red-400 text-lg mt-4">
                                                    <div className="animate-spin inline-block w-6 h-6 border-3 border-red-400 border-t-transparent rounded-full mr-2"></div>
                                                    Generando conflicto para el capítulo...
                                                </div>
                                            )}

                                            {/* Display Chapter Subplot Ideas */}
                                            {chapterSubPlotIdeas[index] && (
                                                <div className="mt-4 p-4 bg-gray-800 rounded-lg border border-gray-700 text-gray-200 whitespace-pre-wrap">
                                                    <h3 className="text-xl font-semibold text-orange-300 mb-2">Ideas para Subtramas:</h3>
                                                    {chapterSubPlotIdeas[index]}
                                                </div>
                                            )}
                                            {loadingChapterSubPlotIndex === index && (
                                                <div className="text-center text-orange-400 text-lg mt-4">
                                                    <div className="animate-spin inline-block w-6 h-6 border-3 border-orange-400 border-t-transparent rounded-full mr-2"></div>
                                                    Generando subtramas para el capítulo...
                                                </div>
                                            )}

                                            {/* Display Chapter Scene Description */}
                                            {chapterSceneDescriptions[index] && (
                                                <div className="mt-4 p-4 bg-gray-800 rounded-lg border border-gray-700 text-gray-200 whitespace-pre-wrap">
                                                    <h3 className="text-xl font-semibold text-yellow-300 mb-2">Descripción de Escena Sugerida:</h3>
                                                    {chapterSceneDescriptions[index]}
                                                </div>
                                            )}
                                            {loadingChapterSceneIndex === index && (
                                                <div className="text-center text-yellow-400 text-lg mt-4">
                                                    <div className="animate-spin inline-block w-6 h-6 border-3 border-yellow-400 border-t-transparent rounded-full mr-2"></div>
                                                    Generando descripción de escena para el capítulo...
                                                </div>
                                            )}

                                            {/* Display Chapter Dialogue Snippet */}
                                            {chapterDialogueSnippets[index] && (
                                                <div className="mt-4 p-4 bg-gray-800 rounded-lg border border-gray-700 text-gray-200 whitespace-pre-wrap">
                                                    <h3 className="text-xl font-semibold text-indigo-300 mb-2">Fragmento de Diálogo Sugerido:</h3>
                                                    {chapterDialogueSnippets[index]}
                                                </div>
                                            )}
                                            {loadingChapterDialogueIndex === index && (
                                                <div className="text-center text-indigo-400 text-lg mt-4">
                                                    <div className="animate-spin inline-block w-6 h-6 border-3 border-indigo-400 border-t-transparent rounded-full mr-2"></div>
                                                    Generando diálogo para el capítulo...
                                                </div>
                                            )}
                                        </li>
                                    ))}
                                </ol>
                            </section>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default App;
