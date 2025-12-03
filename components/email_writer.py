"""
Email Writer component for generating professional emails
"""

import streamlit as st
import os
from utils.gemini_api import generate_content_with_context
from utils.helpers import download_button
from utils.email_sender import send_email, get_smtp_config, validate_email
from config.constants import DEFAULT_RESUME


def render_email_writer(api_key):
    """Render the Email Writer tab"""
    
    st.header("📧 Professional Email Writer")
    st.markdown("Generate professional emails based on your configured job description.")
    if st.session_state.get('jd_configured') and st.session_state.get('job_description'):
        st.info("💡 Using your configured job description as context")
    else:
        st.info("💡 No job description configured - using generic professional context")
    
    col1, col2 = st.columns(2)
    with col1:
        email_purpose = st.selectbox(
            "Email Purpose",
            ["Job Application", "Follow-up", "Networking", "Thank You", "Custom"]
        )
    with col2:
        email_tone = st.selectbox(
            "Tone",
            ["Professional", "Confident", "Friendly", "Formal"]
        )
    
    hiring_manager_name = st.text_input(
        "Hiring Manager Name (optional)",
        placeholder="Leave empty if unknown - will use 'Dear Hiring Manager,'",
        help="Enter the hiring manager's name if known"
    )
    
    additional_context = st.text_area(
        "Additional Context (optional)",
        placeholder="Add any extra details or specific points you want to mention...",
        height=100
    )
    
    if st.button("✨ Generate Email", key="generate_email"):
        with st.spinner("Generating email..."):
            salutation = f"Dear {hiring_manager_name}," if hiring_manager_name else "Dear Hiring Manager,"
            
            # Check if JD is configured
            jd_context = ""
            if st.session_state.get('jd_configured') and st.session_state.get('job_description'):
                jd_context = "Reference the TARGET JOB DESCRIPTION provided in the context"
            else:
                jd_context = "Focus on my general skills and experience as I haven't provided a specific job description"

            prompt_template = f"""
TASK: Write a {{email_tone}} job application email for: {{email_purpose}}

SALUTATION: {{salutation}}

ADDITIONAL CONTEXT (if provided):
{{additional_context}}

REQUIREMENTS:
- Start with: Subject: [create a short, relevant subject line]
- Use the salutation: {{salutation}}
- Keep it to 1-2 SHORT paragraphs maximum
- Highlight specific technologies that match BOTH the target job description (if provided) and my resume
- Reference relevant projects from my PROJECT PORTFOLIO that demonstrate the required skills
- Mention specific project achievements that align with the job requirements
- Clearly mention F1 OPT work authorization
- IMPORTANT: Include portfolio and GitHub links in the signature
- End with the EXACT signature format from the guidelines (with portfolio and GitHub URLs)
- Make it sound human, natural, and confident
- NO bold text, asterisks, or highlighting
- {jd_context}
- You can mention "View more projects at my portfolio" if relevant

Generate the email now:
"""
            
            email = generate_content_with_context(
                prompt_template, 
                api_key,
                email_tone=email_tone,
                email_purpose=email_purpose,
                salutation=salutation,
                additional_context=additional_context
            )
            
            # Store email in session state for persistence
            st.session_state.generated_email = email
            
    # Display generated email if it exists
    if hasattr(st.session_state, 'generated_email') and st.session_state.generated_email:
        st.markdown("### Generated Email:")
        st.text(st.session_state.generated_email)
        
        # Action buttons in columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Escape the email content for JavaScript
            import json
            email_json = json.dumps(st.session_state.generated_email)
            
            # Copy button styled like download button
            copy_html = f"""
            <script>
            function copyEmail() {{
                navigator.clipboard.writeText({email_json});
            }}
            </script>
            <button onclick="copyEmail()" style="
                background: transparent;
                border: 1px solid rgba(250, 250, 250, 0.2);
                color: rgb(250, 250, 250);
                padding: 0.25rem 0.75rem;
                text-align: center;
                font-size: 14px;
                cursor: pointer;
                border-radius: 0.5rem;
                width: 100%;
                font-family: 'Source Sans Pro', sans-serif;
                font-weight: 400;
                line-height: 1.6;
                transition: border-color 0.2s, color 0.2s;
            " onmouseover="this.style.borderColor='rgb(250, 250, 250)'; this.style.color='rgb(255, 255, 255)';" 
               onmouseout="this.style.borderColor='rgba(250, 250, 250, 0.2)'; this.style.color='rgb(250, 250, 250)';">
                📋 Copy Email
            </button>
            """
            st.components.v1.html(copy_html, height=50)
        
        with col2:
            # Download button
            download_button(
                label="📥 Download Email",
                data=st.session_state.generated_email,
                file_name_prefix="email"
            )
        
        with col3:
            # Send email button
            if st.button("📮 Send Email", use_container_width=True, key="send_email_btn"):
                st.session_state.show_email_form = True
                # Initialize editable email content
                if 'editable_email_content' not in st.session_state:
                    st.session_state.editable_email_content = st.session_state.generated_email
        
        # Email sending form - Two step process
        if st.session_state.get('show_email_form', False):
            st.divider()
            
            # Check if we're in preview/edit mode or send mode
            if not st.session_state.get('ready_to_send', False):
                # STEP 1: Preview and Edit Email
                st.markdown("### 📝 Review & Edit Email")
                
                # Load the default resume path
                resume_path = DEFAULT_RESUME if os.path.exists(DEFAULT_RESUME) else None
                if resume_path:
                    st.info(f"📎 Resume will be attached: `{resume_path}`")
                else:
                    st.warning("⚠️ Resume file not found. Email will be sent without attachment.")
                
                # Editable email content
                editable_content = st.text_area(
                    "Edit your email content:",
                    value=st.session_state.editable_email_content,
                    height=300,
                    help="Make any final edits before sending"
                )
                
                # Save editable content
                st.session_state.editable_email_content = editable_content
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("✅ Ready to Send", use_container_width=True, key="ready_to_send_btn"):
                        st.session_state.ready_to_send = True
                        st.rerun()
                
                with col2:
                    if st.button("❌ Cancel", use_container_width=True, key="cancel_preview"):
                        st.session_state.show_email_form = False
                        st.session_state.ready_to_send = False
                        if 'editable_email_content' in st.session_state:
                            del st.session_state.editable_email_content
                        st.rerun()
            
            else:
                # STEP 2: Final Send Form
                st.markdown("### 📮 Send Email")
                
                # Show attachment info
                resume_path = DEFAULT_RESUME if os.path.exists(DEFAULT_RESUME) else None
                if resume_path:
                    st.success(f"📎 Resume will be attached: `{resume_path}`")
                
                with st.form("email_sender_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        sender_email = st.text_input(
                            "Your Email",
                            value="vinayramesh6020@gmail.com",
                            help="The email address from which to send"
                        )
                        recipient_email = st.text_input(
                            "Recipient Email",
                            placeholder="recipient@example.com",
                            help="Who should receive this email"
                        )
                    
                    with col2:
                        app_password = st.text_input(
                            "App Password",
                            type="password",
                            value="vxhc hbez xeso ezum",
                            help="⚠️ Use an app-specific password, not your regular password!"
                        )
                        sender_name = st.text_input(
                            "Your Name (optional)",
                            value="Vinay Ramesh",
                            help="Name to display as sender"
                        )
                    
                    # Show provider info if email is entered
                    if sender_email:
                        smtp_config = get_smtp_config(sender_email)
                        if smtp_config:
                            st.info(f"📧 Provider detected: {smtp_config['provider']}")
                        else:
                            st.warning("⚠️ Provider not automatically detected. Supported: Gmail, Outlook, Yahoo, AOL")
                    
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        send_button = st.form_submit_button("📮 Send Email", use_container_width=True, type="primary")
                    
                    with col2:
                        back_button = st.form_submit_button("← Back to Edit", use_container_width=True)
                    
                    with col3:
                        help_button = st.form_submit_button("💡 Help", use_container_width=True)
                    
                    if back_button:
                        st.session_state.ready_to_send = False
                        st.rerun()
                    
                    if help_button:
                        st.info("""
                        **How to get an App Password:**
                        
                        **Gmail:**
                        1. Go to your Google Account settings
                        2. Enable 2-Step Verification
                        3. Go to Security → App passwords
                        4. Generate a new app password
                        5. Use that 16-character password here
                        
                        **Outlook/Hotmail:**
                        1. Go to account.microsoft.com/security
                        2. Enable two-step verification
                        3. Generate an app password
                        4. Use that password here
                        
                        **Other providers:** Check their security settings for app passwords.
                        """)
                    
                    if send_button:
                        # Validate inputs
                        if not sender_email or not app_password or not recipient_email:
                            st.error("❌ Please fill in all required fields!")
                        elif not validate_email(sender_email):
                            st.error("❌ Invalid sender email format!")
                        elif not validate_email(recipient_email):
                            st.error("❌ Invalid recipient email format!")
                        else:
                            # Send email with attachment
                            with st.spinner("Sending email..."):
                                success, message = send_email(
                                    sender_email=sender_email,
                                    app_password=app_password,
                                    recipient_email=recipient_email,
                                    email_content=st.session_state.editable_email_content,
                                    custom_sender_name=sender_name if sender_name else None,
                                    attachment_path=resume_path
                                )
                                
                                if success:
                                    st.success(message)
                                    # Clear form state
                                    st.session_state.show_email_form = False
                                    st.session_state.ready_to_send = False
                                    if 'editable_email_content' in st.session_state:
                                        del st.session_state.editable_email_content
                                    st.rerun()
                                else:
                                    st.error(f"❌ {message}")
                                    st.info("💡 Make sure you're using an app-specific password, not your regular password!")