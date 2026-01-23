import zipfile
import xml.etree.ElementTree as ET
import sys
import os

def read_docx(file_path):
    """
    Extracts text from a .docx file without external dependencies (python-docx).
    Docx is essentially a zipped XML. We parse 'word/document.xml'.
    """
    try:
        with zipfile.ZipFile(file_path) as z:
            xml_content = z.read('word/document.xml')
            
        root = ET.fromstring(xml_content)
        
        # XML namespace for Word
        # Often defined as w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        # But ElementTree handling of namespaces can be verbose. 
        # We'll just look for 't' (text) and 'p' (paragraph) tags generically or via explicit namespace if needed.
        
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        
        text_parts = []
        
        # Iterate over all paragraphs
        for p in root.findall('.//w:p', ns):
            # Iterate over all runs in paragraph
            p_text = []
            for r in p.findall('.//w:r', ns):
                for t in r.findall('.//w:t', ns):
                    if t.text:
                        p_text.append(t.text)
            
            if p_text:
                text_parts.append(''.join(p_text))
            else:
                text_parts.append('') # Empty line for empty paragraph
                
        return '\n'.join(text_parts)
        
    except Exception as e:
        return f"Error reading docx: {e}"

if __name__ == "__main__":
    path = "docs_bem_utils/Occupancy Integration Plan.docx"
    print(f"Reading: {path}")
    content = read_docx(path)
    print("\n--- EXTRACTED CONTENT ---\n")
    print(content)
