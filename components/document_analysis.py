"""
Document Analysis component for insights and summaries
"""

import streamlit as st
from utils.gemini_api import generate_content_with_context
from utils.helpers import download_button


def render_document_analysis(api_key):
    """Render the Document Analysis tab"""
    
    st.header("📊 Document Summary & Analysis")
    st.markdown("Get insights and summaries based on your documents and target job.")
    if st.session_state.get('jd_configured') and st.session_state.get('job_description'):
        st.info("💡 Analysis will include job match assessment")
    else:
        st.info("💡 Analysis will focus on your documents and portfolio")
    
    analysis_type = st.selectbox(
        "What would you like to analyze?",
        [
            "Job match analysis",
            "Project portfolio analysis",
            "Extract key skills matching the job",
            "List relevant projects for this job",
            "Compare my projects to job requirements",
            "Identify strengths and gaps for this role",
            "Generate career summary for this position",
            "Summarize all documents"
        ]
    )
    
    if st.button("📊 Analyze", key="analyze_docs"):
        with st.spinner("Analyzing your documents..."):
            # Check if JD is configured
            jd_context = ""
            if st.session_state.get('jd_configured') and st.session_state.get('job_description'):
                jd_context = "- The TARGET JOB DESCRIPTION\n- How well I match the job requirements"
            else:
                jd_context = "- General career best practices (since no job description is provided)"

            prompt_template = f"""
TASK: {{analysis_type}}

Provide a comprehensive analysis based on the request, considering:
- My resume and documents
- My PROJECT PORTFOLIO with detailed project information
{jd_context}
- Which specific projects demonstrate the required skills

Be specific, detailed, and actionable:
- Reference specific projects from my portfolio when relevant
- Keep formatting clean and minimal
- Make it professional and easy to read
- Avoid excessive bold text or highlighting
- Provide concrete recommendations where applicable

Generate the analysis:
"""
            
            analysis = generate_content_with_context(
                prompt_template,
                api_key,
                analysis_type=analysis_type
            )
            
            st.markdown("### Analysis Results:")
            st.markdown(analysis)
            
            # Download button
            download_button(
                label="📥 Download Analysis",
                data=analysis,
                file_name_prefix="analysis"
            )


