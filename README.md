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

## 🏗️ Technical Implementation

### Dual Processing Strategy
The system employs a robust dual-strategy approach:
- **Primary**: Bookmark-based extraction for PDFs with embedded table of contents
- **Fallback**: Advanced layout analysis using font profiling and style clustering

### Advanced Features
- **Smart Content Filtering**: Removes page numbers, headers, and duplicate content
- **Hierarchical Level Detection**: Dynamic H1-H6 classification based on font characteristics
- **Error Recovery**: Comprehensive logging and graceful failure handling
- **Batch Processing**: Automated processing of entire PDF directories

## Libraries Used

-   **PyMuPDF (`fitz`)**: For high-performance PDF parsing and text extraction.

## 📁 Project Structure

```
adobe-hackathon-1a/
├── main.py              # Core processing engine
├── requirements.txt     # Python dependencies
├── dockerfile          # Container configuration
├── README.md           # This documentation
├── input/              # Directory for input PDF files
└── output/             # Generated JSON outline files
    ├── file01.json     # Sample output files
    ├── file02.json
    ├── file03.json
    ├── file04.json
    └── file05.json
```

## 📋 Output Format

Each processed PDF generates a JSON file with the following structure:

```json
{
    "title": "Document Title",
    "outline": [
        {
            "level": "H1",
            "text": "Chapter 1: Introduction",
            "page": 0
        },
        {
            "level": "H2",
            "text": "Section 1.1: Overview",
            "page": 1
        }
    ]
}
```

## How to Build and Run

### Build the Docker Image

```bash
docker build --platform linux/amd64 -t pdf-extractor .
```

### Run the Container

#### Option 1: Using Volume Mounts (Recommended)
```bash
# Create directories for input and output
mkdir -p ./input ./output

# Place your PDF files in the input directory
# Then run the container
docker run -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output pdf-extractor
```

#### Option 2: Interactive Mode
```bash
# Run container with interactive shell
docker run -it pdf-extractor bash

# In the container, copy PDFs to /app/input
# Then run: python main.py
```

### Windows Users
```cmd
# Build the image
docker build --platform linux/amd64 -t pdf-extractor .

# Run with volume mounts (Windows)
docker run -v %cd%\input:/app/input -v %cd%\output:/app/output pdf-extractor
```

## 🚀 Local Development

### Setup Environment
```bash
# Install Python dependencies
pip install -r requirements.txt

# Create directories
mkdir -p input output

# Place PDF files in input directory
cp your_pdfs/*.pdf input/

# Run the processor
python main.py
```

### Processing Workflow
1. Place PDF files in the `input/` directory
2. Run the script: `python main.py`
3. Check `output/` directory for generated JSON files
4. Review `final_processing_log.log` for detailed processing information

## 📊 Performance & Capabilities

- **Processing Speed**: Optimized for fast batch processing of multiple PDFs
- **Memory Efficient**: Streams documents without loading entire files into memory
- **Error Recovery**: Continues processing even if individual files fail
- **Comprehensive Logging**: Detailed logs for debugging and monitoring
- **Scalability**: Designed for processing large document collections

## 🌍 Multilingual Support

The system supports documents in various languages through:
- **UTF-8 Handling**: Full Unicode support for international characters
- **Language-Agnostic Logic**: No reliance on language-specific patterns or rules
- **Font-Based Analysis**: Uses visual hierarchy rather than textual patterns
- **Encoding Robustness**: Handles various PDF encoding formats seamlessly

## 🔍 Sample Results

The system successfully processes various document types including:
- **Technical Documentation**: Software testing manuals, RFPs, technical specifications
- **Educational Materials**: STEM pathway documents, course outlines, academic papers
- **Government Forms**: Application forms and official documents
- **Marketing Materials**: Event announcements and promotional content
- **Multilingual Documents**: Including Japanese and other non-Latin scripts

## 🛠️ Troubleshooting

### Common Issues
- **Empty Outlines**: Check if PDF has embedded text (not scanned images)
- **Missing Titles**: Verify PDF structure and font consistency on first page
- **Docker Permission Issues**: Ensure proper volume mounting and file permissions
- **Font Detection Problems**: Check if document uses consistent font sizing

### Debugging
- Check `final_processing_log.log` for detailed processing information
- Verify input PDFs are not password-protected or corrupted
- Ensure Docker has sufficient memory allocation for large documents

## 🔧 Dependencies

```
PyMuPDF>=1.23.0
```

## 📝 Notes

- The system prioritizes accuracy over speed, ensuring reliable outline extraction
- Designed specifically for the Adobe Hackathon Round 1A challenge requirements
- Handles edge cases like single-page documents and documents without clear hierarchies
- Optimized for both English and international document formats