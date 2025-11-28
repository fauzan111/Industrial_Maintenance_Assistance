import streamlit as st
import os
from PIL import Image
from src.vector_db import VectorDB
from src.vision_utils import describe_image
import ollama

# Language Selector
st.sidebar.header("Language / Lingua")
language = st.sidebar.radio("Select Language", ["Italiano", "English"])

# Translations
translations = {
    "Italiano": {
        "title": "🏭 Assistente Manutenzione Industriale",
        "subtitle": "### RAG Multimodale per Manuali Tecnici",
        "settings": "Impostazioni",
        "model": "Modello LLM",
        "ollama_info": "Assicurati che Ollama sia in esecuzione.",
        "input_header": "Input",
        "input_type": "Tipo di Input",
        "text": "Testo",
        "image": "Immagine",
        "text_placeholder": "Descrivi il problema:",
        "text_default": "Come risolvo l'errore pressione olio?",
        "upload_label": "Carica una foto del problema/macchina",
        "image_caption": "Immagine caricata",
        "search_btn": "Cerca Soluzione",
        "results_header": "Risultati",
        "analyzing": "Analisi in corso...",
        "image_analysis": "**Analisi Immagine:**",
        "results_found": "Trovati {} risultati pertinenti.",
        "result_label": "Risultato {} (Fonte: {})",
        "diagram_caption": "Diagramma Trovato",
        "image_not_found": "Immagine non trovata: {}",
        "no_results": "Nessun risultato trovato.",
        "solution_header": "Soluzione Generata",
        "ollama_error": "Ollama non disponibile ({}). Uso risposta simulata.",
        "simulated_response": "Risposta simulata: Controllare la pressione dell'olio e verificare le guarnizioni come indicato nel manuale.",
        "prompt_system": "Sei un esperto assistente per la manutenzione industriale. Usa il seguente contesto dai manuali tecnici per rispondere alla domanda dell'utente. Se il contesto contiene descrizioni di immagini, fai riferimento ad esse. Rispondi in Italiano.",
        "prompt_context": "Contesto:\n{}\n\nDomanda Utente: {}\n\nRisposta:"
    },
    "English": {
        "title": "🏭 Industrial Maintenance Assistant",
        "subtitle": "### Multimodal RAG for Technical Manuals",
        "settings": "Settings",
        "model": "LLM Model",
        "ollama_info": "Ensure Ollama is running.",
        "input_header": "Input",
        "input_type": "Input Type",
        "text": "Text",
        "image": "Image",
        "text_placeholder": "Describe the problem:",
        "text_default": "How do I fix the oil pressure error?",
        "upload_label": "Upload a photo of the problem/machine",
        "image_caption": "Uploaded Image",
        "search_btn": "Search Solution",
        "results_header": "Results",
        "analyzing": "Analyzing...",
        "image_analysis": "**Image Analysis:**",
        "results_found": "Found {} relevant results.",
        "result_label": "Result {} (Source: {})",
        "diagram_caption": "Found Diagram",
        "image_not_found": "Image not found: {}",
        "no_results": "No results found.",
        "solution_header": "Generated Solution",
        "ollama_error": "Ollama unavailable ({}). Using simulated response.",
        "simulated_response": "Simulated response: Check oil pressure and verify seals as indicated in the manual.",
        "prompt_system": "You are an expert industrial maintenance assistant. Use the following context from technical manuals to answer the user's question. If the context contains image descriptions, refer to them. Answer in English.",
        "prompt_context": "Context:\n{}\n\nUser Question: {}\n\nAnswer:"
    }
}

t = translations[language]

st.set_page_config(page_title=t["title"], layout="wide")

st.title(t["title"])
st.markdown(t["subtitle"])

# Sidebar
with st.sidebar:
    st.header(t["settings"])
    model_name = st.selectbox(t["model"], ["mistral", "llama3", "gemma"])
    st.info(t["ollama_info"])

# Main Interface
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader(t["input_header"])
    input_type = st.radio(t["input_type"], [t["text"], t["image"]])
    
    query_text = ""
    query_image = None
    
    if input_type == t["text"]:
        query_text = st.text_area(t["text_placeholder"], t["text_default"])
    else:
        query_image = st.file_uploader(t["upload_label"], type=["jpg", "png", "jpeg"])
        if query_image:
            st.image(query_image, caption=t["image_caption"], use_column_width=True)
            # Save temp image for processing
            with open("temp_query_image.jpg", "wb") as f:
                f.write(query_image.getbuffer())

    search_button = st.button(t["search_btn"])

with col2:
    st.subheader(t["results_header"])
    
    if search_button:
        db = VectorDB()
        results = []
        
        with st.spinner(t["analyzing"]):
            # 1. Determine search query
            if input_type == t["image"] and query_image:
                # Describe image first
                description = describe_image("temp_query_image.jpg", language)
                st.write(f"{t['image_analysis']} {description}")
                search_query = description
            else:
                search_query = query_text
            
            # 2. Search Vector DB
            if search_query:
                results = db.search(search_query, limit=4)
            
            # 3. Display Results & Context
            context_text = ""
            
            if results:
                st.success(t["results_found"].format(len(results)))
                
                for i, res in enumerate(results):
                    with st.expander(t["result_label"].format(i+1, res.get('source_file', 'N/A'))):
                        st.write(res['content'])
                        if res['type'] == 'image_desc' and res['path']:
                            if os.path.exists(res['path']):
                                st.image(res['path'], caption=t["diagram_caption"])
                            else:
                                st.warning(t["image_not_found"].format(res['path']))
                        
                        context_text += f"\n---\nContenuto: {res['content']}\n"
            else:
                st.warning(t["no_results"])
                
            # 4. Generate Answer
            if context_text:
                st.subheader(t["solution_header"])
                prompt = (
                    f"{t['prompt_system']}\n\n"
                    f"{t['prompt_context'].format(context_text, search_query)}"
                )
                
                response_placeholder = st.empty()
                full_response = ""
                
                try:
                    # Check if Ollama is reachable first (simple check)
                    # If not, use dummy response
                    try:
                        ollama.list()
                    except:
                        raise Exception("Ollama unreachable")

                    for chunk in ollama.chat(model=model_name, messages=[{'role': 'user', 'content': prompt}], stream=True):
                        content = chunk['message']['content']
                        full_response += content
                        response_placeholder.markdown(full_response + "▌")
                    response_placeholder.markdown(full_response)
                except Exception as e:
                    st.warning(t["ollama_error"].format(e))
                    # Generate a context-aware response based on retrieved documents
                    if language == "English":
                        full_response = f"**Based on the manual:**\n\n"
                        for i, res in enumerate(results[:2]):  # Use top 2 results
                            full_response += f"{i+1}. {res['content'][:200]}...\n\n"
                        full_response += "\n*Note: This is a simulated response. Install and run Ollama for AI-generated answers.*"
                    else:
                        full_response = f"**Basato sul manuale:**\n\n"
                        for i, res in enumerate(results[:2]):  # Use top 2 results
                            full_response += f"{i+1}. {res['content'][:200]}...\n\n"
                        full_response += "\n*Nota: Questa è una risposta simulata. Installa ed esegui Ollama per risposte generate dall'IA.*"
                    response_placeholder.markdown(full_response)
