from pathlib import Path
import os

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate


# --------------------------------------------------
# 1. Project paths
# --------------------------------------------------

project_root = Path(__file__).resolve().parent.parent

documents_path = project_root / "business_docs"
chroma_path = project_root / "data" / "chroma_db"


# --------------------------------------------------
# 2. Load embeddings
# --------------------------------------------------

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# --------------------------------------------------
# 3. Load existing Chroma vector database
# --------------------------------------------------

vectorstore = Chroma(
    persist_directory=str(chroma_path),
    embedding_function=embeddings
)


# --------------------------------------------------
# 6. Load Groq LLM
# --------------------------------------------------

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    groq_api_key=GROQ_API_KEY
)


# --------------------------------------------------
# 7. RAG Agent
# --------------------------------------------------

def rag_agent(question):

    # Retrieve relevant documents
    retrieved_documents = vectorstore.similarity_search(
        question,
        k=1
    )

    # Create context
    context = "\n\n".join(
        document.page_content
        for document in retrieved_documents
    )

    # Prompt
    rag_prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""
You are a business policy assistant.

Answer the user's question using only the information
provided in the context.

If the answer is not present in the context,
say that the information is not available.

Context:
{context}

User Question:
{question}

Answer clearly and concisely.
"""
    )

    prompt = rag_prompt.format(
        context=context,
        question=question
    )

    # Generate answer
    response = llm.invoke(prompt)

    # Collect sources
    sources = [
        document.metadata.get("source")
        for document in retrieved_documents
    ]

    return {
        "question": question,
        "status": "success",
        "answer": response.content,
        "sources": sources
    }


# --------------------------------------------------
# 8. Test RAG Agent
# --------------------------------------------------

if __name__ == "__main__":

    question = "How many days do customers have to request a return?"

    result = rag_agent(question)

    print("\nRAG AGENT")
    print("=" * 50)

    print("\nQuestion:")
    print(result["question"])

    print("\nAnswer:")
    print(result["answer"])

    print("\nSources:")
    for source in result["sources"]:
        print(source)