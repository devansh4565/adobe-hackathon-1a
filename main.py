import fitz  # PyMuPDF
import json
import os
import re
from collections import Counter, defaultdict
import logging

# -- Setup detailed logging --
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s', filename='final_processing_log.log', filemode='w')

def clean_text(text: str) -> str:
    """A robust function to clean text from PDF extraction."""
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)
    text = text.replace('ﬁ', 'fi').replace('ﬂ', 'fl')
    return " ".join(text.split()).strip()

def get_outline_from_toc(doc: fitz.Document) -> tuple[str, list] | None:
    """PRIMARY STRATEGY: Build title and outline from bookmarks. Fully crash-proof."""
    toc = doc.get_toc(simple=False)
    if not toc:
        logging.warning(f"For '{os.path.basename(doc.name)}', no bookmarks found or call to library failed.")
        return None
        
    logging.info(f"For '{os.path.basename(doc.name)}', SUCCESS: Found bookmarks. Using high-fidelity TOC strategy.")
    outline, is_dict_format = [], isinstance(toc[0], dict)
    
    if is_dict_format:
        top_level = [item['title'] for item in toc if item.get('level') == 1]
    else:
        top_level = [item[1] for item in toc if len(item) > 1 and item[0] == 1]
    title = clean_text(" ".join(top_level[:2]))

    base_level = toc[0]['level'] if is_dict_format else toc[0][0]
    for item in toc:
        if is_dict_format:
            level, text, page = item.get('level', 1), item.get('title', ''), item.get('page', 1) - 1
        else:
            if len(item) < 3: continue
            level, text, page = item[0], item[1], item[2] - 1
        if clean_text(text):
            outline.append({"level": f"H{level - base_level + 1}", "text": clean_text(text), "page": page})
            
    return title, outline

def reconstruct_document_from_layout(doc: fitz.Document) -> tuple[str, list]:
    """FALLBACK ENGINE: A powerful document reconstructor that analyzes and clusters font styles."""
    logging.warning(f"For '{os.path.basename(doc.name)}', executing ADVANCED layout reconstruction.")
    
    # Pass 1: Intelligent Title Extraction from Page 1
    title, title_parts = "", set()
    if doc.page_count > 0:
        page = doc[0]
        # Get blocks from the top half, sorted by reading order (top to bottom)
        blocks = sorted([b for b in page.get_text("dict")["blocks"] if 'lines' in b and b['bbox'][3] < page.rect.height * 0.5], key=lambda b: b['bbox'][1])
        if blocks:
            # Find the most prominent font size in the title area
            max_font_size = max(s["size"] for b in blocks for l in b["lines"] for s in l["spans"])
            # The title is made of lines with prominent fonts
            title_lines = [clean_text(" ".join(s["text"] for s in l["spans"])) for b in blocks for l in b["lines"] if abs(l["spans"][0]["size"] - max_font_size) < 10]
            title = " ".join(title_lines)
            title_parts = set(title_lines)

    # Pass 2: Profile font styles across the entire document
    style_counts, lines_with_style = Counter(), []
    for page_num, page in enumerate(doc):
        for block in page.get_text("dict", sort=True)["blocks"]:
            for line in block.get("lines", []):
                if line.get("spans"):
                    span = line["spans"][0]
                    text = clean_text(" ".join(s["text"] for s in line["spans"]))
                    if not text or len(text) < 3: continue
                    is_bold = "bold" in span["font"].lower()
                    style = (round(span["size"]), is_bold)
                    lines_with_style.append({"text": text, "style": style, "page": page_num})
                    style_counts[style] += len(text)
    
    # Pass 3: Deduce hierarchy
    if not style_counts: return title, []
    body_style = style_counts.most_common(1)[0][0]
    heading_styles = [s for s in style_counts if s[0] > body_style[0]]
    heading_styles.sort(key=lambda s: s[0], reverse=True)
    level_map = {style: f"H{i+1}" for i, style in enumerate(heading_styles[:6])}

    # Pass 4: Construct the outline with correct filtering
    outline, processed = [], {title, *title_parts}
    for line in lines_with_style:
        if line["style"] in level_map and line["text"] not in processed:
             if not re.match(r"^\d+$", line["text"]) and not re.match(r"page \d+", line["text"], re.IGNORECASE):
                outline.append({"level": level_map[line["style"]], "text": line["text"], "page": line["page"]})
                processed.add(line["text"])
    
    return title, outline

def process_pdf(pdf_path: str) -> dict | None:
    """Main orchestrator with a robust hierarchical fallback strategy."""
    logging.info(f"--- Processing PDF: {os.path.basename(pdf_path)} ---")
    try: doc = fitz.open(pdf_path)
    except Exception as e:
        logging.error(f"FATAL: Could not open {pdf_path}. Reason: {e}")
        return None
        
    result = get_outline_from_toc(doc)
    
    if result is None:
        title, outline = reconstruct_document_from_layout(doc)
    else:
        title, outline = result

    doc.close()
    return {"title": title, "outline": outline if outline else []}

def main(input_dir: str, output_dir: str):
    """Main function to find and process all PDFs."""
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    print(f"Starting processing. See {logging.getLogger().handlers[0].baseFilename} for details.")
    for filename in sorted(os.listdir(input_dir)):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_dir, filename)
            print(f"Processing: {filename}")
            data = process_pdf(pdf_path)
            if data:
                json_path = os.path.join(output_dir, os.path.splitext(filename)[0] + ".json")
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                print(f"  -> SUCCESS: Created {os.path.basename(json_path)}")

if __name__ == '__main__':
    main(input_dir='./input', output_dir='./output')
    print("\nProcessing complete.")