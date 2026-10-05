from pathlib import Path

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


# --------------------------------------------------
# 1. Project paths
# --------------------------------------------------

project_root = Path(__file__).resolve().parent.parent

documents_path = project_root / "business_docs"
chroma_path = project_root / "data" / "chroma_db"


# --------------------------------------------------
# 2. Load business documents
# --------------------------------------------------

documents = []

for file in documents_path.glob("*.txt"):

    loader = TextLoader(
        str(file),
        encoding="utf-8"
    )

    documents.extend(loader.load())


print("Documents loaded:")
print(len(documents))


# --------------------------------------------------
# 3. Split documents into chunks
# --------------------------------------------------

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

chunks = text_splitter.split_documents(documents)


print("\nDocument chunks:")
print(len(chunks))


# --------------------------------------------------
# 4. Create embeddings
# --------------------------------------------------

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# --------------------------------------------------
# 5. Create Chroma vector database
# --------------------------------------------------

vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=str(chroma_path)
)


print("\nVector database created successfully!")
print(f"Location: {chroma_path}")