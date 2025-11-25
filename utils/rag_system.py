"""
LangChain RAG System Implementation
Replaces custom RAG with LangChain + Google GenAI + ChromaDB
"""
import os
import shutil
import streamlit as st
from typing import List, Dict, Tuple, Any
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.docstore.document import Document
from langchain.chains import ConversationalRetrievalChain

# Constants
CHROMA_DB_DIR = "./chroma_db"
COLLECTION_NAME = "job_assistant_collection"
EMBEDDING_MODEL = "models/embedding-001"
LLM_MODEL = "gemini-2.5-flash"

class LangChainRAGSystem:
    def __init__(self, api_key: str, persist_directory: str = CHROMA_DB_DIR):
        """Initialize the RAG system with LangChain components"""
        self.api_key = api_key
        self.persist_directory = persist_directory
        
        # Initialize Embeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=EMBEDDING_MODEL,
            google_api_key=api_key
        )
        
        # Initialize Vector Store (ChromaDB)
        self.vector_store = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings,
            collection_name=COLLECTION_NAME
        )
        
        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(
            model=LLM_MODEL,
            google_api_key=api_key,
            temperature=0.7,
            convert_system_message_to_human=True
        )
        
        # Initialize Memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        
        # Initialize Text Splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )

    def index_documents(self, documents: Dict[str, str], force_reindex: bool = False) -> bool:
        """
        Index documents into ChromaDB.
        
        Args:
            documents: Dictionary of {filename: content}
            force_reindex: If True, delete existing DB and rebuild
        """
        try:
            if not documents:
                return False
                
            # Check if we need to reindex
            current_count = self.vector_store._collection.count()
            if current_count > 0 and not force_reindex:
                return True  # Already indexed
                
            if force_reindex and os.path.exists(self.persist_directory):
                # Clear existing DB
                self.vector_store = None
                shutil.rmtree(self.persist_directory)
                # Re-initialize
                self.vector_store = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings,
                    collection_name=COLLECTION_NAME
                )
            
            # Process documents
            docs_to_index = []
            for filename, content in documents.items():
                # Create Document objects
                raw_doc = Document(page_content=content, metadata={"source": filename})
                # Split into chunks
                chunks = self.text_splitter.split_documents([raw_doc])
                docs_to_index.extend(chunks)
            
            # Add to Vector Store
            if docs_to_index:
                self.vector_store.add_documents(docs_to_index)
                self.vector_store.persist()
                return True
                
            return False
            
        except Exception as e:
            st.error(f"Error indexing documents: {str(e)}")
            return False

    def retrieve_relevant_chunks(self, query: str, k: int = 5) -> List[Document]:
        """Retrieve relevant document chunks using MMR"""
        try:
            # Use Max Marginal Relevance for diversity
            retriever = self.vector_store.as_retriever(
                search_type="mmr",
                search_kwargs={"k": k, "fetch_k": k*2}
            )
            return retriever.get_relevant_documents(query)
        except Exception as e:
            print(f"Retrieval error: {e}")
            return []

    def generate_with_rag(self, prompt_template: str, query_context: str, **kwargs) -> str:
        """
        Generate content using RAG context.
        Compatible with existing generate_content_with_context signature.
        """
        try:
            # 1. Retrieve relevant context
            docs = self.retrieve_relevant_chunks(query_context)
            context_text = "\n\n".join([doc.page_content for doc in docs])
            
            # 2. Format prompt with context
            # We inject the RAG context into the prompt
            rag_prompt = f"""
            Context information is below.
            ---------------------
            {context_text}
            ---------------------
            Given the context information and not prior knowledge, answer the query.
            
            {prompt_template}
            """
            
            # 3. Generate response using LLM
            # We format the prompt with kwargs if needed, but usually the template is already formatted
            # or we let the LLM handle it. Here we assume prompt_template is the main instruction.
            
            messages = [{"role": "user", "content": rag_prompt}]
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            st.error(f"RAG Generation Error: {str(e)}")
            return "Error generating content with RAG."

    def generate_with_conversation(self, query: str) -> Tuple[str, List[Document]]:
        """Generate a response for Q&A with memory"""
        try:
            retriever = self.vector_store.as_retriever(
                search_type="mmr",
                search_kwargs={"k": 4}
            )
            
            qa_chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=retriever,
                memory=self.memory,
                return_source_documents=True,
                verbose=True
            )
            
            result = qa_chain({"question": query})
            return result["answer"], result["source_documents"]
            
        except Exception as e:
            return f"Error in conversation: {str(e)}", []

    def get_statistics(self) -> Dict:
        """Get stats about the vector store"""
        try:
            count = self.vector_store._collection.count()
            # Get unique sources (this is a bit hacky with Chroma but works)
            # We'll just return basic stats
            return {
                "total_chunks": count,
                "storage_path": self.persist_directory,
                "status": "Active"
            }
        except Exception:
            return {"total_chunks": 0, "status": "Error"}

    def clear_memory(self):
        """Clear conversation memory"""
        self.memory.clear()

    def similarity_search(self, query: str, k: int = 5) -> List[Tuple[Document, float]]:
        """Raw similarity search with scores"""
        return self.vector_store.similarity_search_with_score(query, k=k)


# Helper Functions

def initialize_rag_system(api_key: str) -> LangChainRAGSystem:
    """Initialize or return existing RAG system"""
    if 'rag_system' not in st.session_state or st.session_state.rag_system is None:
        st.session_state.rag_system = LangChainRAGSystem(api_key)
    return st.session_state.rag_system

def index_documents_if_needed(rag_system: LangChainRAGSystem, force_reindex: bool = False):
    """Index documents if they haven't been indexed yet"""
    if st.session_state.documents:
        with st.spinner("🔄 Indexing documents into ChromaDB..."):
            rag_system.index_documents(st.session_state.documents, force_reindex)

def render_rag_status_sidebar():
    """Render RAG status in the sidebar"""
    if 'rag_system' in st.session_state and st.session_state.rag_system:
        rag = st.session_state.rag_system
        stats = rag.get_statistics()
        
        st.success("✅ ChromaDB Active")
        st.caption(f"Storage: {stats.get('storage_path', 'N/A')}")
        
        col1, col2 = st.columns(2)
        col1.metric("Embeddings", stats.get("total_chunks", 0))
        col2.metric("Docs Loaded", len(st.session_state.documents))
        
        col3, col4 = st.columns(2)
        with col3:
            if st.button("🔄 Re-index", help="Rebuild vector database"):
                index_documents_if_needed(rag, force_reindex=True)
                st.rerun()
        with col4:
            if st.button("🗑️ Clear Mem", help="Clear chat history"):
                rag.clear_memory()
                st.success("Memory cleared!")