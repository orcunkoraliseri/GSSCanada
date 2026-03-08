import PyPDF2

def search_pdf(pdf_path, terms):
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for i in range(len(reader.pages)):
                text = reader.pages[i].extract_text()
                if not text:
                    continue
                for term in terms:
                    if term.lower() in text.lower():
                        lines = text.split('\n')
                        for j, line in enumerate(lines):
                            if term.lower() in line.lower():
                                print(f"\n==== '{term}' @ Page {i+1} in {pdf_path} ====")
                                print('\n'.join(lines[max(0, j-2):min(len(lines), j+20)]))
                                break
    except Exception as e:
        print(f"Error: {e}")

print("=== Checking 2005 for WKWEHR_C ===")
search_pdf("codebooks/Codebook_2005/12M0019GPE.pdf", ["WKWEHR_C"])

print("\n=== Checking 2015 for WHWD140C ===")
search_pdf("codebooks/Codebook_2015/GSS29_PUMF_main.pdf", ["WHWD140C", "WHW_140"])
