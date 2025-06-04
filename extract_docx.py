import docx

def extract_text_from_docx(file_path):
    try:
        doc = docx.Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text)
    except Exception as e:
        return f"Ошибка при чтении файла: {str(e)}"

if __name__ == "__main__":
    file_path = "методические указания .docx"
    text = extract_text_from_docx(file_path)
    print(text) 