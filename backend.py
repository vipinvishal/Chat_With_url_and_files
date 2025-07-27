import os
import pandas as pd
from euriai.langgraph import EuriaiLangGraph



# EURI API Key
EURI_API_KEY = "euri-ec46960a6b9348cf03a2cb42ee521494091f14da15d15f065e8ea7b86c1a0e11"

graph = EuriaiLangGraph(
    api_key=EURI_API_KEY,
    default_model="gpt-4.1-nano"
)

# Add these imports
import mimetypes

def ingest_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    mime, _ = mimetypes.guess_type(file_path)
    if ext == ".csv":
        df = pd.read_csv(file_path)
        return df.to_string()
    elif ext in [".xls", ".xlsx"]:
        df = pd.read_excel(file_path)
        return df.to_string()
    elif ext == ".docx":
        from docx import Document
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    elif ext == ".pdf":
        import PyPDF2
        text = ""
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
        return text
    else:
        raise ValueError("Unsupported file type: " + ext)

def crawl_website(url):
    # Minimalistic placeholder for crawling
    import requests
    from bs4 import BeautifulSoup
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    text = ' '.join([p.get_text() for p in soup.find_all('p')])
    return text

def index_data(data):
    # Only add the node if it doesn't already exist
    if "processor" not in graph.graph.nodes:
        graph.add_ai_node(
            "processor",
            "Process and enhance this text: {input}"
        )
        graph.set_entry_point("processor")
        graph.set_finish_point("processor")
    result = graph.run({"input": data})
    return result