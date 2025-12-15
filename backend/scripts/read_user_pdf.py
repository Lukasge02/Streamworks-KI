import fitz


def read_pdf(path):
    try:
        doc = fitz.open(path)
        print(f"--- Document: {path} ---")
        print(f"Pages: {len(doc)}")
        for page in doc:
            print(f"\n--- Page {page.number + 1} ---")
            print(page.get_text())
    except Exception as e:
        print(f"Error reading PDF: {e}")


if __name__ == "__main__":
    pdf_path = "/Applications/Programmieren/Visual Studio/Bachelorarbeit/Streamworks-KI/Streamworks-DDD-CR24850-Physically-Delete-Agents.pdf"
    read_pdf(pdf_path)
