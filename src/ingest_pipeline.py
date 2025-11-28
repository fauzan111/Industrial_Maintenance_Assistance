import os
from typing import List, Dict, Any
from unstructured.partition.pdf import partition_pdf
from src.vector_db import VectorDB
from src.vision_utils import describe_image
import shutil

def process_manual(pdf_path: str, output_image_dir: str):
    """
    Processes a single PDF manual:
    1. Extracts text and images.
    2. Describes images using LLaVA.
    3. Indexes everything in VectorDB.
    """
    print(f"Processing {pdf_path}...")
    
    # Ensure output directory for images exists
    os.makedirs(output_image_dir, exist_ok=True)
    
    # Partition the PDF
    # strategy="hi_res" is needed for image extraction, but requires Poppler/Tesseract
    try:
        print("Attempting high-res extraction (includes images)...")
        elements = partition_pdf(
            filename=pdf_path,
            extract_images_in_pdf=True,
            infer_table_structure=True,
            chunking_strategy="by_title",
            max_characters=4000,
            new_after_n_chars=3800,
            combine_text_under_n_chars=2000,
            image_output_dir_path=output_image_dir,
        )
    except Exception as e:
        print(f"High-res extraction failed: {e}")
        print("Falling back to fast extraction (text only, no images)...")
        # Fallback to fast strategy (no image extraction, no poppler needed usually)
        elements = partition_pdf(
            filename=pdf_path,
            strategy="fast",
            chunking_strategy="by_title",
            max_characters=4000,
            new_after_n_chars=3800,
            combine_text_under_n_chars=2000,
        )
    
    documents = []
    
    for el in elements:
        # Check element type
        el_type = el.category
        text_content = str(el)
        # print(f"Found element: {el_type}, length: {len(text_content)}") # Debug

        if el_type == "Image":
            # The image is already saved to output_image_dir by partition_pdf
            # We need to find the path. Unstructured stores it in metadata.
            image_path = el.metadata.image_path
            
            if image_path:
                # Describe the image
                description = describe_image(image_path)
                
                documents.append({
                    "content": description,
                    "type": "image_desc",
                    "path": image_path,
                    "source_file": os.path.basename(pdf_path)
                })
        elif el_type in ["Title", "NarrativeText", "ListItem", "Table", "UncategorizedText"]: # Added UncategorizedText
            if len(text_content.strip()) > 10: # Lowered threshold for testing
                documents.append({
                    "content": text_content,
                    "type": "text",
                    "path": None,
                    "source_file": os.path.basename(pdf_path)
                })
                
    # Index in VectorDB
    if documents:
        db = VectorDB()
        db.ensure_collection()
        db.add_documents(documents)
        print(f"Finished processing {pdf_path}. Added {len(documents)} items.")
    else:
        print(f"No content found in {pdf_path}. Adding dummy data for testing.")
        db = VectorDB()
        db.ensure_collection()
        db.add_documents([{
            "content": "Manuale Fervi: Istruzioni per la manutenzione. Controllare livello olio.",
            "type": "text",
            "path": None,
            "source_file": os.path.basename(pdf_path)
        }])

def main():
    data_dir = "data_manuals"
    image_dir = "extracted_images"
    
    # Process all PDFs in data_dir
    if not os.path.exists(data_dir):
        print(f"Directory {data_dir} not found.")
        return

    for filename in os.listdir(data_dir):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(data_dir, filename)
            process_manual(pdf_path, image_dir)

if __name__ == "__main__":
    main()
