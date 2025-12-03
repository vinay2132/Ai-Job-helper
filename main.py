"""
AI Career Assistant - Main Application
A modular Streamlit application for career management powered by Gemini AI
"""

import streamlit as st

# Import configuration and utilities
from config.constants import PAGE_CONFIG, TABS, DEFAULT_RESUME, DEFAULT_PROJECTS
from config.session_state import initialize_session_state
from utils.helpers import setup_environment
from utils.document_processing import auto_load_default_resume, auto_load_projects_file, auto_load_additional_documents

# Import components
from components.sidebar import render_sidebar
from components.email_writer import render_email_writer
from components.resume_updater import render_resume_updater
from components.advanced_resume_formatter import render_advanced_resume_formatter  # NEW IMPORT
from components.cover_letter import render_cover_letter
from components.qa_assistant import render_qa_assistant
from components.document_analysis import render_document_analysis


def render_job_preview():
    """Render content preview when fetching from URL"""
    if not st.session_state.get('show_job_preview', False):
        return False
    
    if not st.session_state.get('fetching_job_url'):
        return False
    
    try:
        from utils.job_url_fetcher import fetch_and_display_job, save_job_to_session
        
        st.info("🔍 **Content Preview** - Review the extracted information below")
        st.caption("The system works with any URL - job postings or general websites")
        
        url = st.session_state.fetching_job_url
        job_details = fetch_and_display_job(url)
        
        if job_details:
            # Check if we got meaningful content
            has_content = job_details.description and len(job_details.description.strip()) > 50
            
            if not has_content:
                st.warning("⚠️ Limited content extracted. This might be due to:")
                st.markdown("""
                - JavaScript-rendered content (page loads content dynamically)
                - Access restrictions or authentication required
                - Page structure is very complex
                
                **Suggestion:** Try copying the content manually or use a different URL.
                """)
            
            # Show action buttons
            st.divider()
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                if st.button("✅ Use This Content", 
                           use_container_width=True, 
                           type="primary",
                           key="use_fetched_jd_main",
                           disabled=not has_content):
                    save_job_to_session(job_details)
                    # Clear preview flags
                    del st.session_state.fetching_job_url
                    del st.session_state.show_job_preview
                    st.success("✅ Content configured from URL!")
                    st.rerun()
            
            with col2:
                if st.button("🔄 Try Different URL", 
                           use_container_width=True,
                           key="refetch_jd_main"):
                    del st.session_state.fetching_job_url
                    del st.session_state.show_job_preview
                    st.rerun()
            
            with col3:
                if st.button("❌ Cancel", 
                           use_container_width=True,
                           key="cancel_jd_main"):
                    del st.session_state.fetching_job_url
                    del st.session_state.show_job_preview
                    st.rerun()
            
            return True
        else:
            st.error("❌ Could not fetch content from URL.")
            st.info("💡 **Troubleshooting tips:**")
            st.markdown("""
            1. Check if the URL is accessible in your browser
            2. Some sites block automated access
            3. Try copying the content manually instead
            4. Make sure you have internet connection
            """)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Try Again", use_container_width=True, key="retry_fetch"):
                    st.rerun()
            with col2:
                if st.button("🔙 Go Back", use_container_width=True, key="go_back_fetch"):
                    del st.session_state.fetching_job_url
                    del st.session_state.show_job_preview
                    st.rerun()
            return True
            
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.info("This might be a temporary issue. Try again or use manual entry.")
        
        if st.button("🔙 Go Back", key="error_go_back"):
            if 'fetching_job_url' in st.session_state:
                del st.session_state.fetching_job_url
            if 'show_job_preview' in st.session_state:
                del st.session_state.show_job_preview
            st.rerun()
        return True

        
def main():
    """Main application function"""
    
    # Setup
    setup_environment()
    st.set_page_config(**PAGE_CONFIG)
    initialize_session_state()
    
    # Auto-load documents on first run
    if not st.session_state.auto_loaded:
        resume_loaded = auto_load_default_resume()
        projects_loaded = auto_load_projects_file()
        additional_loaded = auto_load_additional_documents()
        
        # Auto-load portfolio content
        if not st.session_state.get('portfolio_loaded', False):
            from utils.portfolio_fetcher import load_portfolio_content
            try:
                load_portfolio_content()
            except Exception as e:
                pass  # Silently fail, user can manually load later
        
        st.session_state.auto_loaded = True
    
    # Render sidebar and get API key
    with st.sidebar:
        api_key = render_sidebar()
    
    # Main Content
    st.title("💼 AI Career Assistant")
    st.markdown("*Your personal AI assistant for career management powered by Gemini*")
    
    # Check if we need to show job preview
    if render_job_preview():
        # Stop here and show only the preview
        return
    
    # Check for API key
    if not api_key:
        st.info("👈 Please unlock the application in the sidebar to continue.")
        st.stop()
    
    # Check if documents are loaded
    if not st.session_state.documents:
        st.error(f"⚠️ No documents loaded. Please make sure your files are in the same folder as this script, or upload them manually in the sidebar.")
        st.info("""
        ### Getting Started:
        1. Place your resume file named `Vinay_Ramesh_full_stack_developer.pdf` in the `data/` folder
        2. Place your projects file named `My_projects.txt` in the `data/` folder
        3. Or upload your files manually using the sidebar
        4. Configure your target job description in the sidebar
        5. Choose a task from the tabs below once your documents are loaded
        """)
        st.stop()
    
    # Check if job description is configured
    if not st.session_state.jd_configured or not st.session_state.job_description.strip():
        st.warning("⚠️ No target job description configured. Features will use generic context.")
        st.info("💡 Tip: Configure a job description in the sidebar for better results!")
    else:
        # Show job description status
        st.success(f"✅ Target job configured! All features are using your job description as context.")
    
    # Show source information
    col1, col2 = st.columns([3, 1])
    with col1:
        with st.expander("📋 View Current Job Description"):
            job_desc_preview = st.session_state.job_description[:500] + "..." if len(st.session_state.job_description) > 500 else st.session_state.job_description
            st.text(job_desc_preview)
    
    with col2:
        if st.session_state.get('job_url'):
            st.caption("📌 Source: URL")
        else:
            st.caption("📌 Source: Manual")
    
    # Create tabs for different functionalities
    # UPDATED: Now 6 tabs instead of 5
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(TABS)
    
    # Tab 1: Email Writer
    with tab1:
        render_email_writer(api_key)
    
    # Tab 2: Resume Updater (Text-based)
    with tab2:
        render_resume_updater(api_key)
    
    # Tab 3: Advanced DOCX Formatter (NEW!)
    with tab3:
        render_advanced_resume_formatter(api_key)
    
    # Tab 4: Cover Letter Generator
    with tab4:
        render_cover_letter(api_key)
    
    # Tab 5: Q&A Assistant
    with tab5:
        render_qa_assistant(api_key)
    
    # Tab 6: Document Analysis
    with tab6:
        render_document_analysis(api_key)
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>💼 AI Career Assistant | Powered by Google Gemini</p>
        <p style='font-size: 0.8em;'>Your data is processed securely and not stored permanently.</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()