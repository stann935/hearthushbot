import os
import random

BOOKS_DIR = "books"

CATEGORY_BOOKS = {
    "attraction": ["attraction"],
    "breakup": ["relationships"],
    "attachment": ["relationships"],
    "communication": ["communication"],
    "confidence": ["relationships", "attraction"],
    "power_boundaries": ["power"],
    "business_goals": ["business"],
    "companion": ["relationships"],
}


def get_book_passage(category, max_chars=1500):
    folders = CATEGORY_BOOKS.get(category, ["relationships"])
    
    all_passages = []
    
    for folder in folders:
        folder_path = os.path.join(BOOKS_DIR, folder)
        if not os.path.exists(folder_path):
            continue
            
        books = [f for f in os.listdir(folder_path) if f.endswith(".txt")]
        if not books:
            continue
            
        book_file = random.choice(books)
        book_path = os.path.join(folder_path, book_file)
        
        try:
            with open(book_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            # Remove gutenberg header/footer
            start = content.find("*** START")
            end = content.find("*** END")
            if start != -1:
                content = content[start + 50:]
            if end != -1:
                content = content[:end]
            
            # Get random passage
            content = content.strip()
            if len(content) > max_chars:
                start_pos = random.randint(0, len(content) - max_chars)
                passage = content[start_pos:start_pos + max_chars]
                # Clean up partial sentences
                first_period = passage.find(".")
                if first_period != -1:
                    passage = passage[first_period + 1:]
            else:
                passage = content
                
            all_passages.append(passage.strip())
            
        except Exception as e:
            continue
    
    if all_passages:
        return random.choice(all_passages)
    return ""


def enrich_context_with_books(category, system_context):
    passage = get_book_passage(category)
    
    if not passage:
        return system_context
    
    enriched = system_context + f"""

Reference material from your knowledge library 
(use the wisdom in this naturally, never quote directly):

---
{passage}
---

Draw on the insights above to deepen your response.
Never mention where this comes from.
"""
    return enriched

