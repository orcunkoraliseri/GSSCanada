"""Convert markdown to PDF using fpdf2."""

import re
from fpdf import FPDF


def convert_md_to_pdf(md_path: str, pdf_path: str) -> None:
    """
    Convert a markdown file to PDF.
    
    Args:
        md_path: Path to the markdown file.
        pdf_path: Path for the output PDF file.
    """
    # Read the markdown file
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Create PDF with Letter size
    pdf = FPDF(format='letter')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_left_margin(20)
    pdf.set_right_margin(20)
    
    in_code_block = False
    
    # Process line by line
    lines = md_content.split('\n')
    
    for line in lines:
        # Replace Unicode emojis with ASCII equivalents first
        line = line.replace('✅', '[OK]')
        line = line.replace('❌', '[X]')
        line = line.replace('⚠️', '[!]')
        line = line.replace('→', '->')
        
        # Reset X position at start of each line
        pdf.set_x(20)
        
        # Handle code blocks
        if line.startswith('```'):
            in_code_block = not in_code_block
            continue
        
        if in_code_block:
            pdf.set_font('Courier', '', 8)
            pdf.set_fill_color(240, 240, 240)
            # Replace tree diagram characters with ASCII equivalents
            ascii_line = line.replace('├', '|').replace('└', '|').replace('─', '-').replace('│', '|')
            pdf.multi_cell(0, 4, ascii_line, fill=True)
            continue
        
        # Clean markdown formatting
        clean_line = line
        clean_line = re.sub(r'\*\*(.+?)\*\*', r'\1', clean_line)  # Bold
        clean_line = re.sub(r'\*(.+?)\*', r'\1', clean_line)  # Italic
        clean_line = re.sub(r'`(.+?)`', r'\1', clean_line)  # Inline code
        clean_line = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', clean_line)  # Links
        
        # Handle headers
        if line.startswith('# '):
            pdf.set_font('Helvetica', 'B', 16)
            pdf.ln(4)
            pdf.multi_cell(0, 8, clean_line[2:])
            pdf.ln(2)
        elif line.startswith('## '):
            pdf.set_font('Helvetica', 'B', 13)
            pdf.ln(4)
            pdf.multi_cell(0, 7, clean_line[3:])
            pdf.ln(2)
        elif line.startswith('### '):
            pdf.set_font('Helvetica', 'B', 11)
            pdf.ln(3)
            pdf.multi_cell(0, 6, clean_line[4:])
            pdf.ln(1)
        elif line.startswith('#### '):
            pdf.set_font('Helvetica', 'BI', 10)
            pdf.ln(2)
            pdf.multi_cell(0, 6, clean_line[5:])
            pdf.ln(1)
        elif line.startswith('---'):
            pdf.ln(2)
            pdf.line(20, pdf.get_y(), 190, pdf.get_y())
            pdf.ln(2)
        elif line.startswith('|'):
            # Table row
            pdf.set_font('Helvetica', '', 8)
            table_line = re.sub(r'\|', '  ', line).strip()
            if not re.match(r'^[\s\-|:]+$', line):  # Skip separator rows
                pdf.multi_cell(0, 4, table_line)
        elif line.startswith('- ') or line.startswith('  - '):
            pdf.set_font('Helvetica', '', 9)
            indent = 25 if line.startswith('  - ') else 20
            text = line.lstrip(' -').strip()
            pdf.set_x(indent)
            pdf.multi_cell(0, 5, '- ' + text)
        elif re.match(r'^\s*\d+\. ', line):
            pdf.set_font('Helvetica', '', 9)
            pdf.multi_cell(0, 5, clean_line)
        elif clean_line.strip():
            pdf.set_font('Helvetica', '', 9)
            pdf.multi_cell(0, 5, clean_line.strip())
        else:
            pdf.ln(2)
    
    pdf.output(pdf_path)
    print(f'PDF created successfully: {pdf_path}')


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) == 3:
        convert_md_to_pdf(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python md_to_pdf.py input.md output.pdf")
