"""
Q&A Assistant component for career advice and chat functionality
"""

import streamlit as st
from utils.gemini_api import generate_content_with_context


def render_qa_assistant(api_key):
    """Render the Q&A Assistant tab"""
    
    st.header("💬 Career Q&A Assistant")
    st.markdown("Ask questions about the job description, your resume, or career advice.")
    if st.session_state.get('jd_configured') and st.session_state.get('job_description'):
        st.info("💡 All responses will consider your configured job description")
    else:
        st.info("💡 Answering based on your profile and general career knowledge")
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if question := st.chat_input("Ask me anything about your career, the target job, resume match, etc..."):
        # Add user message to chat
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Check if JD is configured
                jd_instruction = ""
                if st.session_state.get('jd_configured') and st.session_state.get('job_description'):
                    jd_instruction = "and the TARGET JOB DESCRIPTION"
                else:
                    jd_instruction = "(no specific job description provided)"

                prompt_template = f"""
USER QUESTION: {{question}}

Based on my background, documents, personal details, {jd_instruction}, provide a helpful, accurate, and personalized answer.
- If the question is about the target job, provide specific insights about how I match the requirements
- If comparing my profile to the job description, be specific about strengths and areas to highlight
- Keep responses natural, conversational, and professional
- Mention F1 OPT if work authorization is relevant to the question

Answer the question:
"""
                
                answer = generate_content_with_context(
                    prompt_template,
                    api_key,
                    question=question
                )
                st.markdown(answer)
                
                # Add assistant response to chat
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()
