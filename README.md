# Adobe Hackathon: Round 1A - PDF Outline Extractor

This solution extracts a structured outline (Title, H1, H2, H3) from PDF documents. It is designed to be fast, efficient, and language-agnostic to support the multilingual bonus challenge.

## Approach

The solution uses a set of language-agnostic heuristics to identify headings rather than relying on language-specific patterns.

1.  **PDF Parsing**: The `PyMuPDF` library is used to parse the PDF. It's chosen for its high speed and its ability to extract detailed metadata for each text span, including font size, font name, and flags (e.g., bold).

2.  **Font Profiling**: The script first performs a pass over the entire document to analyze the font styles. It identifies the most frequently used font size, which is assumed to be the body text.

3.  **Heading Detection**: Any text significantly larger than the body text is considered a heading candidate. These candidates are sorted by size to determine their levels (H1, H2, H3). This method is language-agnostic, as relative font size is a universal indicator of importance.

4.  **Title Extraction**: The title is assumed to be the largest piece of text on the first page, prioritizing bolded text.

5.  **Multilingual Support**: The entire pipeline handles text as UTF-8, and the logic avoids language-specific rules like capitalization. This allows it to work on documents in various languages, such as the Japanese example mentioned in the challenge.

6.  **Automation**: The script is designed to run within a Docker container, automatically processing all PDFs from a mounted `/app/input` volume and saving the corresponding JSON files to `/app/output`.

## Libraries Used

-   **PyMuPDF (`fitz`)**: For high-performance PDF parsing and text extraction.

## How to Build and Run

### Build the Docker Image

```bash
docker build --platform linux/amd64 -t pdf-extractor .