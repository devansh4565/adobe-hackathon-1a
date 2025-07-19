import fitz  # PyMuPDF
import json
import os
import collections
import re

# --- Configuration ---
INPUT_DIR = "/app/input"
OUTPUT_DIR = "/app/output"
HEADING_LEVELS = 3
HEADING_SIZE_FACTOR = 1.1
PAGE_MARGIN_TOP = 0.12
PAGE_MARGIN_BOTTOM = 0.12
NEGATIVE_KEYWORDS = [
    'figure', 'table', 'university', 'department', 'institute',
    'inc.', 'llc', 'copyright', 'issn', 'editor', 'author',
    'reviewed by', 'letter from', 'in this issue', 'continued', 'www.'
]

def consolidate_outline(outline):
    if not outline:
        return []
    consolidated = []
    current_heading = outline[0]
    for i in range(1, len(outline)):
        next_heading = outline[i]
        if (next_heading['page'] == current_heading['page'] and
            next_heading['level'] == current_heading['level']):
            current_heading['text'] += " " + next_heading['text']
        else:
            consolidated.append(current_heading)
            current_heading = next_heading
    consolidated.append(current_heading)
    return consolidated

def is_valid_heading(line_text):
    text_lower = line_text.lower()
    if not text_lower.strip() or len(text_lower) > 200:
        return False
    if any(keyword in text_lower for keyword in NEGATIVE_KEYWORDS):
        return False
    if re.search(r'\S+@\S+', text_lower):
        return False
    return True

def process_pdf(pdf_path):
    with fitz.open(pdf_path) as doc:
        all_lines = []
        font_sizes = collections.defaultdict(int)

        for page_num, page in enumerate(doc):
            page_height = page.rect.height
            body_top = page_height * PAGE_MARGIN_TOP
            body_bottom = page_height * (1 - PAGE_MARGIN_BOTTOM)
            
            blocks = page.get_text("dict", flags=fitz.TEXTFLAGS_DICT)["blocks"]
            for block in blocks:
                if block["type"] == 0:  # Text block
                    for line in block["lines"]:
                        # Check if line is within the body margin
                        line_y = line['bbox'][1]
                        if body_top < line_y < body_bottom:
                            line_text = " ".join(span['text'] for span in line['spans']).strip()
                            if line_text:
                                first_span = line['spans'][0]
                                all_lines.append({
                                    "text": line_text,
                                    "size": first_span['size'],
                                    "page": page_num # Use 0-indexed page number
                                })
                                font_sizes[round(first_span['size'])] += len(line_text)
        
        if not font_sizes:
            return {"title": "Untitled Document", "outline": []}

        body_size = max(font_sizes, key=font_sizes.get)
        potential_heading_sizes = [s for s in font_sizes if s > body_size * HEADING_SIZE_FACTOR]
        potential_heading_sizes.sort(reverse=True)
        heading_sizes = potential_heading_sizes[:HEADING_LEVELS]
        size_to_level = {size: f"H{i+1}" for i, size in enumerate(heading_sizes)}

        title_text = "Untitled Document"
        for line in all_lines:
             if line['page'] <= 1 and round(line['size']) >= (heading_sizes[0] if heading_sizes else body_size * 1.5):
                if 'perspectives' in line['text'].lower() or 'journal' in line['text'].lower():
                    title_text = line['text']
                    break

        outline = []
        for line in all_lines:
            font_size = round(line['size'])
            if font_size in size_to_level and is_valid_heading(line['text']):
                outline.append({
                    "level": size_to_level[font_size],
                    "text": line['text'],
                    "page": line['page']
                })
        
        final_outline = consolidate_outline(outline)
        result = {"title": title_text, "outline": final_outline}
        
    return result

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for filename in os.listdir(INPUT_DIR):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(INPUT_DIR, filename)
            output_path = os.path.join(OUTPUT_DIR, os.path.splitext(filename)[0] + ".json")
            print(f"Processing {pdf_path}...")
            try:
                data = process_pdf(pdf_path)
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"Successfully generated {output_path}")
            except Exception as e:
                print(f"Error processing {pdf_path}: {e}")
    print("Processing complete.")