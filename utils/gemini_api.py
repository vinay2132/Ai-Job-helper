"""
Gemini API utilities with RAG support
"""

import streamlit as st
import google.generativeai as genai
from config.constants import GEMINI_MODEL, FALLBACK_API_KEY


def call_gemini(prompt, api_key):
    """Call Gemini API with the given prompt, using fallback key if needed"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name=GEMINI_MODEL)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # Try fallback key if it exists and is different from the primary key
        if FALLBACK_API_KEY and FALLBACK_API_KEY != api_key:
            try:
                print(f"Primary key failed ({str(e)}). Attempting fallback key...")
                genai.configure(api_key=FALLBACK_API_KEY)
                model = genai.GenerativeModel(model_name=GEMINI_MODEL)
                response = model.generate_content(prompt)
                return response.text
            except Exception as fallback_error:
                return f"Error: Primary key failed ({str(e)}) and separate Fallback key also failed ({str(fallback_error)})"
        
        return f"Error: {str(e)}"


def get_context():
    """Build context - LEGACY function for backward compatibility"""
    context = f"""{st.session_state.writing_guidelines}

PERSONAL DETAILS:
{st.session_state.personal_details}

TARGET JOB DESCRIPTION:
{st.session_state.job_description}

RESUME AND DOCUMENTS:
"""
    from config.constants import DEFAULT_RESUME, DEFAULT_PROJECTS
    
    # Add resume first if available
    if DEFAULT_RESUME in st.session_state.documents:
        context += f"\n--- {DEFAULT_RESUME} ---\n{st.session_state.documents[DEFAULT_RESUME]}\n"
    
    # Add projects file second if available
    if DEFAULT_PROJECTS in st.session_state.documents:
        context += f"\n--- {DEFAULT_PROJECTS} (PROJECT PORTFOLIO) ---\n{st.session_state.documents[DEFAULT_PROJECTS]}\n"
    
    # Add other documents
    for doc_name, doc_content in st.session_state.documents.items():
        if doc_name not in [DEFAULT_RESUME, DEFAULT_PROJECTS]:
            context += f"\n--- {doc_name} ---\n{doc_content}\n"
    
    return context


def generate_content_with_context(prompt_template, api_key, **kwargs):
    """
    Generate content with smart RAG if available, fallback to full context
    
    This function intelligently chooses between RAG and standard mode:
    - If RAG is enabled and initialized: Uses semantic search for relevant chunks
    - Otherwise: Uses the original method (send all documents)
    """
    # Check if RAG system is enabled and initialized
    use_rag = st.session_state.get('use_rag', False)
    
    if use_rag and 'rag_system' in st.session_state:
        # Use RAG system for intelligent retrieval
        rag = st.session_state.rag_system
        
        # Build query context from the task and parameters
        query_context = f"Task: {prompt_template[:300]}\n"
        for key, value in kwargs.items():
            if value and len(str(value)) > 0:
                query_context += f"{key}: {str(value)[:150]}\n"
        
        # Generate using RAG
        return rag.generate_with_rag(prompt_template, query_context, **kwargs)
    else:
        # Fallback to original method (send all documents)
        context = get_context()
        full_prompt = f"{context}\n\n{prompt_template.format(**kwargs)}"
        return call_gemini(full_prompt, api_key)