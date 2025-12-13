"""
Updated Sidebar component with URL fetching capability (Fixed - No Nested Expanders)
"""

import streamlit as st
from utils.helpers import (
    get_api_key,
    mask_api_key,
    show_success_message,
    show_info_message,
    show_warning_message,
    show_error_message
)
from utils.document_processing import process_uploaded_file
from config.constants import DEFAULT_RESUME as RESUME_FILENAME, DEFAULT_PROJECTS as PROJECTS_FILENAME

# Import the new job URL fetcher
try:
    from utils.job_url_fetcher import fetch_and_display_job, save_job_to_session
    URL_FETCHER_AVAILABLE = True
except ImportError:
    URL_FETCHER_AVAILABLE = False


def render_sidebar():
    """Render the sidebar with secure configuration options"""
    
    # === Secure API Key Configuration ===
    st.title("🔐 Security")
    
    from utils.security import is_key_set, encrypt_api_key, decrypt_api_key, clear_key
    
    # Initialize session state for unlocked key if not present
    if 'unlocked_api_key' not in st.session_state:
        st.session_state.unlocked_api_key = None
        
    api_key = st.session_state.unlocked_api_key
    
    # Check if a key is already stored securely
    has_secure_key = is_key_set()
    
    if not has_secure_key:
        st.warning("⚠️ No secure key found")
        st.markdown("### 🛠️ Setup Secure Access")
        
        with st.form("setup_security"):
            st.info("Your API key will be encrypted with this password. You'll only need the password to unlock the app next time.")
            
            new_api_key = st.text_input("Enter Gemini API Key", type="password")
            new_password = st.text_input("Create a Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            submitted = st.form_submit_button("🔒 Encrypt & Save Key")
            
            if submitted:
                if not new_api_key:
                    st.error("Please enter an API key")
                elif not new_password:
                    st.error("Please create a password")
                elif new_password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    if encrypt_api_key(new_api_key, new_password):
                        st.session_state.unlocked_api_key = new_api_key
                        st.success("✅ Key encrypted and saved!")
                        st.rerun()
                    else:
                        st.error("Failed to save key")
                        
    elif api_key is None:
        # Key exists but is locked
        st.info("🔒 App is Locked")
        
        with st.form("unlock_app"):
            password = st.text_input("Enter Password to Unlock", type="password")
            submitted = st.form_submit_button("🔓 Unlock App")
            
            if submitted:
                decrypted_key = decrypt_api_key(password)
                if decrypted_key:
                    st.session_state.unlocked_api_key = decrypted_key
                    st.success("✅ Unlocked!")
                    st.rerun()
                else:
                    st.error("❌ Incorrect password")
                    
    else:
        # Key is unlocked
        st.success("✅ App Unlocked & Ready")
        st.caption("Your API key is securely loaded in memory.")
        
        if st.button("🔒 Lock App", use_container_width=True):
            st.session_state.unlocked_api_key = None
            st.rerun()
            
        with st.expander("⚙️ Advanced Security"):
            if st.button("🗑️ Reset / Change Key", type="primary", use_container_width=True):
                clear_key()
                st.session_state.unlocked_api_key = None
                st.rerun()

    st.divider()
    
    # Only show the rest of the sidebar if unlocked
    if api_key:
        # === Job Description Configuration ===
        st.header("🎯 Configure Target Job Description (Optional)")
        st.markdown("Choose your input method:")

        # Tabs for input methods
        jd_tab1, jd_tab2 = st.tabs(["📝 Manual Entry", "🔗 Fetch from URL"])

        # --- Manual Entry Tab ---
        with jd_tab1:
            def update_job_description():
                st.session_state.job_description = st.session_state.manual_jd_input
                st.session_state.jd_configured = bool(st.session_state.manual_jd_input.strip())
                if "job_url" in st.session_state:
                    del st.session_state.job_url
                if "job_details" in st.session_state:
                    del st.session_state.job_details
                # We don't need to show a success message on every keystroke/blur, 
                # but the state is updated instantly.

            st.markdown("**Paste job description manually:**")
            job_desc_input = st.text_area(
                "Job Description",
                value=st.session_state.job_description,
                height=300,
                placeholder="Paste full job description here...",
                key="manual_jd_input",
                on_change=update_job_description
            )

            col1, col2 = st.columns(2)
            with col1:
                # Spacer to keep layout aligned if we want, or we can just have the clear button take full width or stay in col2
                # Let's keep the Clear button in a column but maybe make it full width if it's the only action, 
                # or just leave it in col2 to prevent layout shift.
                # Actually, simply removing col1 and having Clear button might be cleaner, 
                # but let's stick to the plan of removing the save button.
                pass 
            with col2:
                if st.button("🗑️ Clear Job Description", use_container_width=True):
                    st.session_state.job_description = ""
                    st.session_state.jd_configured = False
                    for key in ["job_url", "job_details", "manual_jd_input"]:
                        if key in st.session_state:
                           if key == "manual_jd_input":
                               # We can't delete the key associated with the widget effectively while it renders, 
                               # but setting job_description to "" handling re-render usually works.
                               pass 
                           else:
                               st.session_state.pop(key, None)
                    
                    # Force a rerun to clear the widget visually via the 'value' param
                    st.rerun()


        # --- URL Fetching Tab ---
        with jd_tab2:
            if not URL_FETCHER_AVAILABLE:
                st.warning("⚠️ URL fetching not available. Install required packages:")
                st.code("pip install requests beautifulsoup4", language="bash")
            else:
                st.markdown("**Fetch content from ANY URL:**")
                st.success("✅ Works with job boards, career pages, and any website!")

                # Supported sources (use help text instead of nested expander)
                st.info(
                    """
                    **Optimized for Job Boards:**
                    - LinkedIn, Indeed, Glassdoor, Workday
                    - Greenhouse, Lever, Monster, Dice, ZipRecruiter

                    **Also works with:**
                    - Any job posting URL
                    - Company websites or general web pages
                    - Career portals

                    Extracts: job titles, descriptions, requirements, skills, benefits.
                    """
                )

                job_url = st.text_input(
                    "Website URL",
                    placeholder="https://example.com/jobs/software-engineer",
                    key="job_url_input"
                )

                fetch_button = st.button(
                    "🌐 Fetch Content from URL",
                    use_container_width=True,
                    disabled=not job_url.strip()
                )

                if fetch_button and job_url.strip():
                    st.session_state.fetching_job_url = job_url
                    st.session_state.show_job_preview = True
                    st.rerun()

                if st.session_state.get("job_url"):
                    st.success("✅ Currently using content from URL")
                    st.caption(f"Source: {st.session_state.job_url[:50]}...")

                    if st.button("🔄 Fetch from Different URL", use_container_width=True):
                        for key in ["fetching_job_url", "show_job_preview"]:
                            st.session_state.pop(key, None)
                        st.rerun()

        st.divider()

        # === Personal Details ===
        with st.expander("✏️ Edit Personal Details"):
            st.markdown("**Update your personal information:**")
            personal_details_input = st.text_area(
                "Personal Details",
                value=st.session_state.personal_details,
                height=300,
            )
            if st.button("💾 Save Personal Details"):
                st.session_state.personal_details = personal_details_input
                show_success_message("Personal details updated!")
                st.rerun()

        st.divider()

        # === Smart RAG System ===
        st.subheader("🧠 LangChain RAG System")
        st.markdown(
            "**Semantic Document Search** uses AI to find only relevant document sections."
        )

        use_rag = st.toggle(
            "Enable Smart Document Search (RAG)",
            value=st.session_state.get("use_rag", False),
            key="rag_toggle",
        )
        st.session_state.use_rag = use_rag

        if use_rag:
            try:
                from utils.rag_system import initialize_rag_system, index_documents_if_needed, render_rag_status_sidebar

                rag_system = initialize_rag_system(api_key)
                if st.session_state.documents:
                    # Check if we need to index (first run)
                    index_documents_if_needed(rag_system)
                
                # Render the status and controls
                render_rag_status_sidebar()
                
            except Exception as e:
                st.error(f"❌ Error initializing RAG: {e}")
                st.session_state.use_rag = False
        else:
            st.caption("📄 Standard mode: All documents sent with each request.")

        st.divider()

        # === Portfolio & GitHub ===
        st.subheader("🌐 Portfolio & GitHub")
        portfolio_status = st.session_state.get("portfolio_loaded", False)

        if portfolio_status:
            st.success("✅ Portfolio content loaded")
            col1, col2 = st.columns(2)
            col1.markdown(f"[🌐 Portfolio]({st.session_state.get('portfolio_url', 'N/A')})")
            col2.markdown(f"[💻 GitHub]({st.session_state.get('github_url', 'N/A')})")

            if st.button("🔄 Refresh Portfolio", use_container_width=True):
                from utils.portfolio_fetcher import refresh_portfolio_content

                if refresh_portfolio_content():
                    show_success_message("Portfolio refreshed!")
                    st.rerun()
        else:
            st.info("📡 Portfolio content not loaded")
            if st.button("📥 Fetch Portfolio & GitHub", use_container_width=True):
                from utils.portfolio_fetcher import load_portfolio_content

                with st.spinner("Fetching content..."):
                    if load_portfolio_content():
                        show_success_message("✅ Portfolio and GitHub content loaded!")
                        st.rerun()
                    else:
                        st.error("❌ Could not fetch portfolio content. Check internet connection.")

        st.caption("Fetches live content from your portfolio website and GitHub profile.")
        st.divider()

        # === Document Upload Section ===
        st.subheader("📁 Upload Documents")
        uploaded_files = st.file_uploader(
            "Upload Resume or Additional Documents",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True,
        )

        if uploaded_files:
            for file in uploaded_files:
                if file.name not in st.session_state.documents:
                    text = process_uploaded_file(file)
                    if text:
                        st.session_state.documents[file.name] = text
                        show_success_message(f"✅ {file.name} uploaded!")

        # Display all loaded documents
        if st.session_state.documents:
            st.divider()
            st.subheader("📚 Loaded Documents")
            for doc_name in list(st.session_state.documents.keys()):
                col1, col2 = st.columns([3, 1])
                col1.text(f"⭐ {doc_name}" if doc_name == RESUME_FILENAME else doc_name)
                if col2.button("🗑️", key=f"delete_{doc_name}"):
                    del st.session_state.documents[doc_name]
                    st.rerun()

    return api_key
