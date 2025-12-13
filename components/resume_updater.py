"""
Resume Updater component for tailoring resumes to job descriptions
"""

import streamlit as st
from utils.gemini_api import generate_content_with_context
from utils.helpers import download_button


def render_resume_updater(api_key):
    """Render the Resume Updater tab"""
    
    st.header("📄 Resume Updater")
    st.markdown("Update your resume to match your configured job description.")
    if st.session_state.get('jd_configured') and st.session_state.get('job_description'):
        st.info("💡 Using your configured job description as context")
    else:
        st.info("💡 No job description configured - optimizing for general best practices")
    
    update_type = st.radio(
        "What would you like to update?",
        ["Tailor entire resume", "Update skills section", "Optimize summary", "Highlight relevant projects"]
    )
    
    additional_instructions = st.text_area(
        "Additional Instructions (optional)",
        placeholder="Any specific points to emphasize or changes to make...",
        height=100
    )
    
    if st.button("🔄 Update Resume", key="update_resume"):
        with st.spinner("Updating resume..."):
            # Check if JD is configured
            jd_instruction = ""
            if st.session_state.get('jd_configured') and st.session_state.get('job_description'):
                jd_instruction = "Based on my background and the TARGET JOB DESCRIPTION provided above"
            else:
                jd_instruction = "Based on my background and general best practices for a Full Stack Developer"

            prompt_template = f"""
TASK: {{update_type}}

{jd_instruction}, {{update_type_lower}}.

ADDITIONAL INSTRUCTIONS:
{{additional_instructions}}

REQUIREMENTS:
- Highlight relevant skills and experiences
- Use professional keywords
- Reference specific projects from my PROJECT PORTFOLIO that demonstrate required skills
- Include concrete project achievements and technologies used
- Maintain professional format WITHOUT excessive bold or highlighting
- Emphasize achievements
- Keep it concise and ATS-friendly
- Sound natural and human, not AI-generated

MANDATORY IMPROVEMENTS:
- **SKILLS FORMAT:** usage of a 2-column table is REQUIRED. Format the SKILLS section STRICTLY as:
  Category Name: Skill 1, Skill 2, Skill 3
  Category Name: Skill 1, Skill 2
  (Do NOT use bullet points for individual skills. Group them by category on a single line so they can be parsed into a table).
- **EXPERIENCE SUMMARY:** Explicitly state total relevant experience as "5.5 years" in the summary to match the "5+" requirement.
- **CS FUNDAMENTALS:** Explicitly include the exact phrase "Comprehensive computer science fundamentals in coding, object-oriented programming, data structures, and algorithms" in the Summary or as a dedicated bullet point.
- **SCALE:** For roles at "Loyalty Juggernaut" and "Hexaware Technologies", you MUST quantify scale using specific placeholders if exact numbers are unknown. Use format like "[X million transactions processed]" or "[Y user base]" to emphasize scale.

Provide the updated section or full resume:
"""
            
            updated_resume = generate_content_with_context(
                prompt_template,
                api_key,
                update_type=update_type,
                update_type_lower=update_type.lower(),
                additional_instructions=additional_instructions
            )
            
            st.markdown("### Updated Resume:")
            st.text(updated_resume)
            
            # Download button
            download_button(
                label="📥 Download Updated Resume",
                data=updated_resume,
                file_name_prefix="resume_updated"
            )
