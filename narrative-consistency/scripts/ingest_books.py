import csv
import os
import re

def clean_text(text):
    """
    Basic text cleaning to remove excessive whitespace and non-printable characters.
    """
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def ingest_books(books_dir, output_file, chunk_size=1000):
    """
    Reads .txt files from books_dir, chunks them, and writes to output_file (CSV).
    Schema: chunk_id, book_name, text
    """
    
    # Mapping based on implementation plan
    filename_map = {
        "In search of the castaways.txt": "In Search of the Castaways",
        "The Count of Monte Cristo.txt": "The Count of Monte Cristo"
    }

    chunks = []
    chunk_counter = 1

    if not os.path.exists(books_dir):
        print(f"Directory not found: {books_dir}")
        return

    files = [f for f in os.listdir(books_dir) if f.endswith('.txt')]
    print(f"Found {len(files)} books in {books_dir}")

    for filename in files:
        book_name = filename_map.get(filename, filename) # Fallback to filename if not in map
        file_path = os.path.join(books_dir, filename)
        
        print(f"Processing {filename} as '{book_name}'...")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
                
            # Remove Project Gutenberg headers/footers (heuristic)
            # Find START OF PROJECT GUTENBERG
            start_match = re.search(r'\*\*\* START OF (THE|THIS) PROJECT GUTENBERG EBOOK .* \*\*\*', text)
            if start_match:
                print(f"  Found start marker at position {start_match.end()}")
                text = text[start_match.end():]
                
            # Find END OF PROJECT GUTENBERG
            end_match = re.search(r'\*\*\* END OF (THE|THIS) PROJECT GUTENBERG EBOOK .* \*\*\*', text)
            if end_match:
                print(f"  Found end marker at position {end_match.start()}")
                text = text[:end_match.start()]
            
            # Simple chunking by character count (approx paragraphs would be better but this is robust)
            # For smarter chunking we could split by double newlines then group.
            # Let's try splitting by paragraphs first.
            paragraphs = text.split('\n\n')
            current_chunk = []
            current_length = 0
            
            for para in paragraphs:
                cleaned_para = clean_text(para)
                if not cleaned_para:
                    continue
                    
                if current_length + len(cleaned_para) > chunk_size and current_chunk:
                    # Flush current chunk
                    chunk_text = " ".join(current_chunk)
                    chunks.append([chunk_counter, book_name, chunk_text])
                    chunk_counter += 1
                    current_chunk = []
                    current_length = 0
                
                current_chunk.append(cleaned_para)
                current_length += len(cleaned_para)
            
            # Flush remaining
            if current_chunk:
                chunk_text = " ".join(current_chunk)
                chunks.append([chunk_counter, book_name, chunk_text])
                chunk_counter += 1
                
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    # Write to CSV
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["chunk_id", "book_name", "text"])
        writer.writerows(chunks)
    
    print(f"Ingestion complete. Wrote {len(chunks)} chunks to {output_file}")

if __name__ == "__main__":
    BOOKS_DIR = "data/Books"
    OUTPUT_FILE = "data/chunks.csv"
    ingest_books(BOOKS_DIR, OUTPUT_FILE)
