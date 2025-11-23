import sys
print("Starting imports...")
sys.stdout.flush()

try:
    print("Importing TextLoader...")
    from langchain_community.document_loaders import TextLoader
    print("TextLoader imported.")
    sys.stdout.flush()
    
    print("Importing UnstructuredHTMLLoader...")
    from langchain_community.document_loaders import UnstructuredHTMLLoader
    print("UnstructuredHTMLLoader imported.")
    sys.stdout.flush()

    print("Importing RecursiveCharacterTextSplitter...")
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    print("RecursiveCharacterTextSplitter imported.")
    sys.stdout.flush()

    print("Importing FakeEmbeddings...")
    from langchain_community.embeddings import FakeEmbeddings
    print("FakeEmbeddings imported.")
    sys.stdout.flush()

    print("Importing Chroma...")
    from langchain_community.vectorstores import Chroma
    print("Chroma imported.")
    sys.stdout.flush()

except Exception as e:
    print(f"Error: {e}")
