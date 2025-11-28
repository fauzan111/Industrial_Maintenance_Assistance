import ollama
from pathlib import Path

def describe_image(image_path: str, language: str = "Italiano") -> str:
    """
    Sends the image to LLaVA via Ollama and gets a description in the specified language.
    """
    if language == "English":
        prompt = (
            "Describe this technical image in detail. "
            "List visible components, numeric labels, and the purpose of the diagram. "
            "Answer in English."
        )
        mock_response = "Simulated description: Technical image of a mechanical component (Ollama unavailable)."
    else:
        prompt = (
            "Descrivi dettagliatamente questa immagine tecnica. "
            "Elenca i componenti visibili, le etichette numeriche e lo scopo del diagramma. "
            "Rispondi in Italiano."
        )
        mock_response = "Descrizione simulata: Immagine tecnica di un componente meccanico (Ollama non disponibile)."
    
    print(f"Generating description for {image_path} in {language}...")
    
    try:
        response = ollama.chat(
            model='llava',
            messages=[
                {
                    'role': 'user',
                    'content': prompt,
                    'images': [image_path]
                }
            ]
        )
        return response['message']['content']
    except Exception as e:
        print(f"Error describing image {image_path}: {e}")
        return mock_response

if __name__ == "__main__":
    # Test (requires an image path)
    pass
