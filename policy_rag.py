from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import FakeEmbeddings 

def build_policy_vector_db():
    loader = DirectoryLoader("policies/", glob="*.txt", loader_cls=TextLoader)
    documents = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
    docs = text_splitter.split_documents(documents)
    
    # Offline-compatible deterministic embeddings
    embeddings = FakeEmbeddings(size=100) 
    vectorstore = FAISS.from_documents(docs, embeddings)
    return vectorstore.as_retriever(search_kwargs={"k": 2})

def query_policy(query: str):
    retriever = build_policy_vector_db()
    results = retriever.invoke(query)
    return "\n".join([doc.page_content for doc in results])
