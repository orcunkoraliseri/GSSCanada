import PyPDF2
import sys

def get_var_text(pdf_path, var_name):
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text = page.extract_text()
                if text and var_name in text:
                    lines = text.split('\n')
                    for i, line in enumerate(lines):
                        if var_name in line:
                            # Print following 25 lines
                            print(f"\n==== {var_name} in {pdf_path} ====")
                            print('\n'.join(lines[max(0, i-2):i+25]))
                            return
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")

print("Extracting codebook data...")
get_var_text("codebooks/Codebook_2005/12M0019GPE.pdf", "INCM ")
get_var_text("codebooks/Codebook_2010/Main File - Data Dictionary and Alphabetical Index.pdf", "INCM ")
get_var_text("codebooks/Codebook_2015/GSS29_PUMF_main.pdf", "INCG1")
get_var_text("codebooks/Codebook_2022/TU_2022_Main_PUMF.pdf", "INC_C")
get_var_text("codebooks/Codebook_2022/TU_2022_Main_PUMF.pdf", "WHWD140G")
get_var_text("codebooks/Codebook_2005/12M0019GPE.pdf", "LANCH")
get_var_text("codebooks/Codebook_2022/TU_2022_Main_PUMF.pdf", "LAN_01")
