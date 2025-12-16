"""
Advanced Resume Formatter - 3-Stage DOCX Generation (IMPROVED VERSION)
Fixed based on resume comparison review:
1. Added explicit Skills section requirement
2. Removed experience inflation
3. Improved prompt clarity
4. Better content filtering
"""

import streamlit as st
import re
from datetime import datetime
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.oxml.table import CT_TblPr
from utils.gemini_api import call_gemini


def render_advanced_resume_formatter(api_key):
    """Render the Advanced Resume Formatter tab with 3-stage processing"""
    
    st.header("🎯 Advanced Resume Formatter (2-Page DOCX)")
    st.markdown("""
    **Generate a professionally formatted 2-page DOCX resume** tailored to your job description.
    
    This advanced system uses a **3-stage process**:
    1. ✨ **Stage 1**: Tailors content to match job requirements
    2. 🎨 **Stage 2**: Matches your natural writing tone and style  
    3. 📄 **Stage 3**: Optimizes for clean 2-page formatting
    """)
    
    st.info("💡 Using your configured job description and resume documents")
    
    # Check if documents are loaded
    if not st.session_state.documents:
        st.warning("⚠️ No documents loaded. Please upload your resume first.")
        return
    
    # Options
    with st.expander("⚙️ Formatting Options", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            include_summary = st.checkbox("Include Summary Section", value=True)
            include_skills = st.checkbox("Include Skills Section", value=True, help="HIGHLY RECOMMENDED for ATS")
            
        with col2:
            include_experience = st.checkbox("Include Experience Section", value=True)
            include_education = st.checkbox("Include Education Section", value=True)
        
        st.markdown("**Contact Information:**")
        col3, col4 = st.columns(2)
        with col3:
            contact_name = st.text_input("Name", value="Vinay Ramesh")
            contact_phone = st.text_input("Phone", value="+1 (682) 273-5833")
        with col4:
            contact_email = st.text_input("Email", value="vinayramesh6020@gmail.com")
            max_bullets_per_job = st.number_input("Max bullets per job", min_value=4, max_value=10, value=7, help="Recommended: 6-8 bullets for comprehensive coverage")
    
    # Additional instructions
    additional_notes = st.text_area(
        "Additional Instructions (optional)",
        placeholder="Any specific requirements or points to emphasize...",
        height=100
    )
    
    # Generate button
    if st.button("🚀 Generate 2-Page DOCX Resume", type="primary", use_container_width=True):
        
        # Get resume content from documents
        from config.constants import DEFAULT_RESUME
        resume_text = st.session_state.documents.get(DEFAULT_RESUME, "")
        
        if not resume_text:
            # Try to find any PDF document
            for doc_name, content in st.session_state.documents.items():
                if doc_name.endswith('.pdf'):
                    resume_text = content
                    break
        
        if not resume_text:
            st.error("❌ No resume document found. Please upload your resume.")
            return
        
        job_desc = st.session_state.job_description
        
        if not job_desc:
            st.error("❌ No job description configured. Please configure it in the sidebar.")
            return
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Stage 1: Tailor content
            status_text.text("⏳ Stage 1/3: Tailoring content to job requirements...")
            progress_bar.progress(10)
            
            stage1_result = run_stage1_tailoring(resume_text, job_desc, api_key, additional_notes)
            progress_bar.progress(33)
            
            if not stage1_result:
                st.error("❌ Stage 1 failed. Please try again.")
                return
            
            # Save stage 1 for debugging
            st.session_state['stage1_output'] = stage1_result
            
            # Stage 2: Match tone
            status_text.text("⏳ Stage 2/3: Matching your natural writing style...")
            progress_bar.progress(40)
            
            stage2_result = run_stage2_tone_matching(resume_text, stage1_result, api_key)
            progress_bar.progress(66)
            
            if not stage2_result:
                st.error("❌ Stage 2 failed. Please try again.")
                return
            
            # Save stage 2 for debugging
            st.session_state['stage2_output'] = stage2_result
            
            # Stage 3: Optimize for 2 pages
            status_text.text("⏳ Stage 3/3: Optimizing for 2-page format...")
            progress_bar.progress(70)
            
            stage3_result = run_stage3_optimization(stage2_result, api_key, max_bullets_per_job)
            progress_bar.progress(90)
            
            if not stage3_result:
                st.error("❌ Stage 3 failed. Please try again.")
                return
            
            # Save stage 3 for debugging
            st.session_state['stage3_output'] = stage3_result
            
            # Parse and create DOCX
            status_text.text("⏳ Creating formatted DOCX file...")
            
            sections = parse_resume_content(stage3_result)
            
            # Apply section filters
            if not include_summary:
                sections['summary'] = ''
            if not include_skills:
                sections['skills'] = {}
            if not include_experience:
                sections['experience'] = []
            if not include_education:
                sections['education'] = ''
            
            # Create DOCX in memory
            doc = create_docx_resume_in_memory(
                sections, 
                contact_name, 
                contact_phone, 
                contact_email
            )
            
            progress_bar.progress(100)
            status_text.text("✅ Resume generation complete!")
            
            # Success message
            st.success("🎉 Your 2-page tailored resume is ready!")
            
            # Display stages in expanders
            col1, col2, col3 = st.columns(3)
            
            with col1:
                with st.expander("📝 Stage 1: Tailored Content"):
                    st.text_area("Stage 1 Output", stage1_result, height=200, key="stage1_display")
            
            with col2:
                with st.expander("🎨 Stage 2: Tone Matched"):
                    st.text_area("Stage 2 Output", stage2_result, height=200, key="stage2_display")
            
            with col3:
                with st.expander("📄 Stage 3: Optimized"):
                    st.text_area("Stage 3 Output", stage3_result, height=200, key="stage3_display")
            
            # Download button
            st.divider()
            
            # Save doc to bytes
            from io import BytesIO
            doc_bytes = BytesIO()
            doc.save(doc_bytes)
            doc_bytes.seek(0)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"Tailored_Resume_{timestamp}.docx"
            
            st.download_button(
                label="📥 Download DOCX Resume",
                data=doc_bytes.getvalue(),
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary",
                use_container_width=True
            )
            
            # Preview sections
            st.divider()
            st.markdown("### 📋 Resume Preview")
            
            if sections['summary']:
                with st.expander("Summary", expanded=True):
                    st.markdown(sections['summary'])
            
            if sections['skills']:
                with st.expander("Skills", expanded=True):
                    for category, items in sections['skills'].items():
                        st.markdown(f"**{category}:** {items}")
            
            if sections['experience']:
                with st.expander(f"Experience ({len(sections['experience'])} jobs)", expanded=False):
                    for job in sections['experience']:
                        st.markdown(f"**{job['company']}** | {job['title']} | {job['duration']}")
                        for resp in job['responsibilities']:
                            st.markdown(f"- {resp}")
                        st.divider()
            
            if sections['education']:
                with st.expander("Education", expanded=False):
                    st.markdown(sections['education'])
            
        except Exception as e:
            st.error(f"❌ Error generating resume: {str(e)}")
            st.exception(e)
        
        finally:
            progress_bar.empty()
            status_text.empty()


def run_stage1_tailoring(resume_text, job_description, api_key, additional_notes=""):
    """Stage 1: Tailor content to job requirements - IMPROVED VERSION"""
    
    prompt = f"""
You are an expert resume writer. Analyze this job description and tailor the resume to emphasize relevant experience and skills.

**JOB DESCRIPTION:**
{job_description}

**ORIGINAL RESUME:**
{resume_text}

**ADDITIONAL NOTES:**
{additional_notes if additional_notes else "None"}

**CRITICAL RULES:**

1. **ACCURATE EXPERIENCE CALCULATION:**
   - Calculate total years of experience based ONLY on actual job dates in the resume
   - DO NOT inflate or exaggerate experience duration
   - Use "X+ years" format (e.g., "3+ years", "4+ years") based on actual dates
   - Example: If jobs span Jul 2020 - Current (Dec 2024), that's "4+ years"

2. **MANDATORY SKILLS SECTION:**
   - MUST include a dedicated SKILLS section formatted as a table
   - Use EXACT format: "Category | Technologies" (pipe separator)
   - Prioritize technologies mentioned in the job description
   - Include ALL relevant technologies from original resume
   - Categories to include: Frontend Development, Backend Development, Cloud & DevOps, Databases & Storage, Testing & Automation, Version Control & Collab, Security, AI/ML & Data Science (if applicable)

3. **EXPERIENCE SECTION FORMAT:**
   - ONLY include actual job positions from the original resume
   - Each job must have: Company Name, Location | Job Title | Duration
   - Follow with bullet points describing specific achievements
   - DO NOT include introductory paragraphs
   - DO NOT include general technology lists (those go in SKILLS)
   - DO NOT include job description content
   - ONLY include job-specific accomplishments

4. **KEYWORD OPTIMIZATION:**
   - Naturally incorporate keywords from job description
   - Reorder and emphasize relevant technologies
   - Quantify achievements where possible (users, transactions, scale)
   - Use specific metrics from the original resume or reasonable estimates

5. **JOB REQUIREMENTS ALIGNMENT:**
   - If job requires specific technologies (e.g., Java, Spring Boot, AWS), ensure they're prominent
   - If job requires specific experience (e.g., "5 years"), match if accurate, otherwise use "X+" format
   - Highlight relevant domain experience (e.g., fintech, healthcare, e-commerce)

**OUTPUT FORMAT:**

SUMMARY
[Single flowing paragraph, 6-7 lines (approximately 6-8 sentences) with NO line breaks. Include: (1) accurate years of experience, (2) primary technical expertise and technologies matching job requirements, (3) domain specialization (fintech/healthcare/e-commerce), (4) key technical strengths (architecture patterns, cloud platforms, methodologies like TDD/CI/CD), (5) notable achievements with metrics if possible, (6) educational background if relevant to role, and (7) unique value proposition. Be comprehensive yet concise. Be truthful about experience duration.]

SKILLS
Category | Skills/Technologies

Frontend Development | [React, Angular, TypeScript, Redux, etc.]
Backend Development | [Java, Spring Boot, Node.js, Express, etc.]
Cloud & DevOps | [AWS (EC2, S3, Lambda), Docker, Kubernetes, Jenkins, etc.]
Databases & Storage | [PostgreSQL, MySQL, MongoDB, Redis, etc.]
Testing & Automation | [Jest, Mocha, Cypress, TDD, etc.]
Version Control & Collab | [Git, GitHub, Jira, Slack, etc.]
Security | [OAuth 2.0, JWT, OWASP, AES, RSA, etc.]
[AI/ML & Data Science | [Python, TensorFlow, Scikit-learn, etc.] - if applicable]

EXPERIENCE

[Company Name], [Location]
[Job Title] | [Month Year - Month Year or Current]
- [Achievement with metric using action verb]
- [Achievement with metric using action verb]
- [Achievement with metric using action verb]
- [Continue with 6-8 bullets per job - focus on most impactful achievements]

[Next Company], [Location]
[Job Title] | [Duration]
- [Bullet points]

[Continue for all jobs from original resume]

EDUCATION
● [Degree]
  [University] || [Dates]
● [Degree]
  [University] || [Dates]

**QUALITY CHECKLIST:**
✓ Skills section is present and comprehensive
✓ Experience years are accurate (not inflated)
✓ Job-critical technologies are prominent
✓ Only actual job positions in Experience section
✓ No introductory paragraphs in Experience
✓ Metrics and scale included where possible
✓ Keywords from job description naturally integrated

Generate the complete tailored resume now:
"""
    
    return call_gemini(prompt, api_key)


def run_stage2_tone_matching(original_resume, tailored_resume, api_key):
    """Stage 2: Match natural writing tone - IMPROVED VERSION"""
    
    prompt = f"""
You are an expert resume editor. Revise the "Tailored Resume" to match the natural writing style of the "Original Resume" while keeping all improvements and keywords.

**ORIGINAL RESUME (Style Reference):**
{original_resume}

**TAILORED RESUME (Content to Refine):**
{tailored_resume}

**YOUR TASK:**

1. **Analyze Writing Style:**
   - Study the Original Resume's action verbs (e.g., "Developed", "Built", "Managed", "Optimized")
   - Note the sentence structure and flow
   - Identify the level of formality and tone

2. **Preserve Key Content:**
   - Keep ALL technologies and skills from the Tailored Resume
   - Maintain all metrics and achievements
   - Keep the skills section intact
   - Preserve job dates and titles exactly

3. **Rewrite for Natural Tone:**
   - Replace AI-sounding phrases with natural language
   - Use direct, straightforward action verbs
   - Avoid buzzwords like "Pioneered", "Spearheaded", "Championed" unless in original
   - Use "Developed", "Built", "Created", "Implemented", "Designed", "Optimized" more frequently
   - Keep sentences concise and readable

4. **Maintain Structure:**
   - Keep sections in order: Summary, Skills, Experience, Education
   - Ensure Skills section remains comprehensive
   - Keep Experience section with only job positions
   - No introductory paragraphs before bullet points

**OUTPUT FORMAT:**

SUMMARY
[Natural 6-7 lines (approximately 6-8 sentences) with accurate experience, key technologies, domain expertise, technical strengths, achievements, and value proposition. Single flowing paragraph with NO line breaks. Write in a natural, human tone matching the original resume style.]

SKILLS
Category | Skills/Technologies

Frontend Development | [technologies]
Backend Development | [technologies]
Cloud & DevOps | [technologies]
Databases & Storage | [technologies]
Testing & Automation | [technologies]
Version Control & Collab | [technologies]
Security | [technologies]
[AI/ML & Data Science | [technologies] - if applicable]

EXPERIENCE

[Company Name], [Location]
[Job Title] | [Duration]
- [Natural bullet with action verb and metric]
- [Natural bullet with action verb and metric]
- [Continue with all bullets]

[Next job]

EDUCATION
● [Degree]
  [University] || [Dates]
● [Degree]
  [University] || [Dates]

**CRITICAL REQUIREMENTS:**
- NO markdown formatting (no ** or *)
- Natural, human-like writing
- Skills section must be present
- Only job positions in Experience (no paragraphs)
- Start directly with "SUMMARY"

Generate the tone-matched resume now:
"""
    
    result = call_gemini(prompt, api_key)
    
    # Clean up markdown
    result = re.sub(r'```.*?\n', '', result)
    result = re.sub(r'```', '', result)
    
    return result


def run_stage3_optimization(tone_matched_resume, api_key, max_bullets=5):
    """Stage 3: Optimize for 2 pages - IMPROVED VERSION"""
    
    prompt = f"""
You are an expert resume optimizer. Your task is to ensure this resume fits perfectly on 2 pages while maintaining maximum impact.

**CURRENT RESUME:**
{tone_matched_resume}

**2-PAGE OPTIMIZATION REQUIREMENTS:**

1. **Length Target:** 50-70 total lines (fits on 2 pages with standard formatting)

2. **Summary:** Maintain at 6-7 lines (approximately 6-8 sentences)
   - Years of experience + primary technologies + domain expertise
   - Technical strengths (architecture, cloud, methodologies)
   - Key achievement with metric
   - Educational background if relevant
   - Unique value proposition

3. **Skills Section:** 
   - MUST be present and visible (critical for ATS)
   - Keep all categories but make concise
   - One line per category
   - Remove redundant tools

4. **Experience Section:**
   - Keep top {max_bullets} most impactful bullets per job (typically 6-8 bullets)
   - Prioritize bullets with:
     * Quantifiable metrics (%, numbers, scale, impact)
     * Job-relevant technologies from job description
     * Business impact or technical achievements
     * Leadership, collaboration, or innovation
   - Each bullet: 1-2 lines maximum
   - Remove redundant or weak bullets
   - ONLY job positions (company, title, duration, bullets)
   - NO introductory text or paragraphs

5. **Education:** Minimal format with bullet points
   - Use ● symbol before degree
   - Include degree, university, dates with || separator

**BULLET PRIORITIZATION CRITERIA:**
✓ Has specific metrics/numbers (%, users, transactions, time saved)
✓ Uses job-critical technologies from job description
✓ Shows business impact or scale (revenue, efficiency, users)
✓ Demonstrates technical leadership or innovation
✓ Starts with strong action verb (Developed, Architected, Optimized, Led)
✓ Shows collaboration with cross-functional teams
✗ Generic statements without metrics
✗ Redundant with other bullets
✗ Too long (>2 lines)
✗ Vague or unclear impact

**OUTPUT FORMAT (PLAIN TEXT, NO MARKDOWN):**

SUMMARY
[6-7 lines, approximately 6-8 sentences. Include years of experience, key technologies, domain expertise, technical strengths, achievements, and value proposition. Single flowing paragraph.]

SKILLS
Category | Skills/Technologies

Frontend Development | [concise list]
Backend Development | [concise list]
Cloud & DevOps | [concise list]
Databases & Storage | [concise list]
Testing & Automation | [concise list]
Version Control & Collab | [concise list]
Security | [concise list]
[AI/ML & Data Science | [concise list] - if applicable]

EXPERIENCE

[Company Name], [Location]
[Job Title] | [Duration]
- [Top impact bullet with metric]
- [Top impact bullet with metric]
- [Top impact bullet with metric]
- [Top impact bullet with metric]
- [Top impact bullet with metric]
- [Top impact bullet with metric]
- [Top impact bullet with metric]

[Company Name], [Location]
[Job Title] | [Duration]
- [Impact bullet with metric]
- [Impact bullet with metric]
- [Impact bullet with metric]
- [Impact bullet with metric]
- [Impact bullet with metric]
- [Impact bullet with metric]

[Company Name], [Location]
[Job Title] | [Duration]
- [Impact bullet with metric]
- [Impact bullet with metric]
- [Impact bullet with metric]
- [Impact bullet with metric]
- [Impact bullet with metric]

EDUCATION
● [Degree]
  [University] || [Dates]
● [Degree]
  [University] || [Dates]

**CRITICAL RULES:**
- NO asterisks or markdown (no ** or *)
- NO introductory paragraphs in Experience
- Skills section MUST be present with table format
- Summary should be 6-7 lines (6-8 sentences)
- Maximum {max_bullets} bullets per job (typically 6-8)
- Plain text only
- 60-75 lines total (fits on 2 pages)
- Start with "SUMMARY"

Generate the optimized 2-page resume now:
"""
    
    result = call_gemini(prompt, api_key)
    
    # Aggressive markdown cleanup
    result = re.sub(r'\*\*([^*]+)\*\*', r'\1', result)
    result = re.sub(r'\*([^*]+)\*', r'\1', result)
    result = re.sub(r'```.*?\n', '', result)
    result = re.sub(r'```', '', result)
    result = re.sub(r'#{1,6}\s', '', result)
    
    return result


def parse_resume_content(content):
    """Parse resume content into structured sections - IMPROVED VERSION"""
    
    sections = {
        'summary': '',
        'skills': {},
        'experience': [],
        'education': ''
    }
    
    content = content.strip()
    # Clean markdown
    content = re.sub(r'\*\*([^*]+)\*\*', r'\1', content)
    content = re.sub(r'\*([^*]+)\*', r'\1', content)
    
    # Extract sections using regex
    summary_match = re.search(r'SUMMARY:?\s*(.*?)(?=\n\s*SKILLS:?|$)', content, re.DOTALL | re.IGNORECASE)
    skills_match = re.search(r'SKILLS:?\s*(.*?)(?=\n\s*EXPERIENCE:?|$)', content, re.DOTALL | re.IGNORECASE)
    experience_match = re.search(r'EXPERIENCE:?\s*(.*?)(?=\n\s*EDUCATION:?|$)', content, re.DOTALL | re.IGNORECASE)
    education_match = re.search(r'EDUCATION:?\s*(.*?)$', content, re.DOTALL | re.IGNORECASE)
    
    # Extract Summary
    if summary_match:
        sections['summary'] = summary_match.group(1).strip()
    
    # Extract Skills - IMPROVED with pipe separator support
    if skills_match:
        skills_text = skills_match.group(1).strip()
        for line in skills_text.split('\n'):
            line = line.strip()
            
            # Skip empty lines and header lines
            if not line or line.lower().startswith('category'):
                continue
            
            # Support both formats: "Category | Skills" and "Category: Skills"
            separator = '|' if '|' in line else ':'
            
            if separator in line and len(line) < 300:  # Skip overly long lines
                parts = line.split(separator, 1)
                category = parts[0].strip()
                items = parts[1].strip()
                # Only add if it looks like a skill category
                if len(category.split()) <= 5:  # Category should be short
                    sections['skills'][category] = items
    
    # Extract Experience - IMPROVED filtering
    if experience_match:
        exp_text = experience_match.group(1).strip()
        lines = exp_text.split('\n')
        current_job = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip very long lines that are likely not job entries
            if len(line) > 150 and not any(marker in line for marker in ['-', '•', ',', '|']):
                continue
            
            # Skip lines that look like section headers or descriptions
            if line.upper() == line and len(line.split()) < 3:
                continue
            
            # Company line: has comma, no bullet, no pipe, reasonable length
            if ',' in line and not line.startswith(('-', '•', '*')) and '|' not in line and len(line) < 100:
                # Save previous job
                if current_job and current_job.get('company') and current_job.get('title'):
                    sections['experience'].append(current_job)
                
                # Start new job
                current_job = {
                    'company': line,
                    'title': '',
                    'duration': '',
                    'responsibilities': []
                }
            
            # Title line: has pipe separator, not a bullet
            elif current_job and '|' in line and not line.startswith(('-', '•', '*')):
                parts = line.split('|')
                if len(parts) >= 2:
                    current_job['title'] = parts[0].strip()
                    current_job['duration'] = parts[1].strip() if len(parts) == 2 else ' | '.join(parts[1:]).strip()
            
            # Bullet point
            elif current_job and line.startswith(('-', '•', '*')):
                bullet = line.lstrip('-•* ').strip()
                # Only add substantial bullets
                if bullet and len(bullet) > 15 and not bullet.upper() == bullet:
                    current_job['responsibilities'].append(bullet)
        
        # Add final job
        if current_job and current_job.get('company') and current_job.get('title'):
            sections['experience'].append(current_job)
    
    # Extract Education
    if education_match:
        sections['education'] = education_match.group(1).strip()
    
    return sections


def create_docx_resume_in_memory(sections, name, phone, email):
    """Create formatted DOCX resume in memory - SAME AS BEFORE"""
    
    doc = Document()
    
    # Set margins
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)
    
    # Set default font
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(11)
    
    # Header - Name
    name_para = doc.add_paragraph(name.upper())
    name_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    name_run = name_para.runs[0]
    name_run.font.size = Pt(14)
    name_run.font.bold = True
    name_run.font.name = 'Calibri'
    name_para.space_after = Pt(2)
    
    # Contact Info
    contact_info = f'Phone: {phone} | Email: {email}'
    contact_para = doc.add_paragraph(contact_info)
    contact_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    contact_run = contact_para.runs[0]
    contact_run.font.size = Pt(11)
    contact_run.font.name = 'Calibri'
    contact_para.space_after = Pt(6)
    
    # Summary Section
    if sections['summary']:
        summary_heading = doc.add_paragraph('SUMMARY')
        summary_heading.alignment = WD_ALIGN_PARAGRAPH.LEFT
        summary_heading_run = summary_heading.runs[0]
        summary_heading_run.font.size = Pt(12)
        summary_heading_run.font.bold = True
        summary_heading_run.font.name = 'Calibri'
        summary_heading.space_before = Pt(6)
        summary_heading.space_after = Pt(3)
        
        summary_para = doc.add_paragraph(sections['summary'])
        summary_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
        summary_run = summary_para.runs[0]
        summary_run.font.size = Pt(11)
        summary_run.font.name = 'Calibri'
        summary_para.space_after = Pt(6)
    
    # Skills Section - TABLE FORMAT matching original resume
    if sections['skills']:
        skills_heading = doc.add_paragraph('SKILLS')
        skills_heading.alignment = WD_ALIGN_PARAGRAPH.LEFT
        skills_heading_run = skills_heading.runs[0]
        skills_heading_run.font.size = Pt(12)
        skills_heading_run.font.bold = True
        skills_heading_run.font.name = 'Calibri'
        skills_heading.space_before = Pt(6)
        skills_heading.space_after = Pt(3)
        
        # Create a proper table with borders (2 columns: Category | Skills)
        num_rows = len(sections['skills']) + 1  # +1 for header row
        skills_table = doc.add_table(rows=num_rows, cols=2)
        skills_table.style = 'Table Grid'  # Use standard table grid style
        
        # Set column widths
        for row in skills_table.rows:
            row.cells[0].width = Inches(2.0)  # Category column
            row.cells[1].width = Inches(4.5)  # Skills column
        
        # Header row
        header_cells = skills_table.rows[0].cells
        header_cells[0].text = 'Category'
        header_cells[1].text = 'Skills/Technologies'
        
        # Format header
        for cell in header_cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.bold = True
                    run.font.size = Pt(11)
                    run.font.name = 'Calibri'
        
        # Populate skills rows
        for idx, (category, items) in enumerate(sections['skills'].items(), start=1):
            row = skills_table.rows[idx]
            
            # Category cell
            cat_cell = row.cells[0]
            cat_cell.text = category
            for paragraph in cat_cell.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(11)
                    run.font.name = 'Calibri'
            
            # Skills cell
            skills_cell = row.cells[1]
            skills_cell.text = items
            for paragraph in skills_cell.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(11)
                    run.font.name = 'Calibri'
        
        doc.add_paragraph().space_after = Pt(6)
    
    # Experience Section
    if sections['experience']:
        exp_heading = doc.add_paragraph('EXPERIENCE')
        exp_heading.alignment = WD_ALIGN_PARAGRAPH.LEFT
        exp_heading_run = exp_heading.runs[0]
        exp_heading_run.font.size = Pt(12)
        exp_heading_run.font.bold = True
        exp_heading_run.font.name = 'Calibri'
        exp_heading.space_before = Pt(6)
        exp_heading.space_after = Pt(3)
        
        for idx, job in enumerate(sections['experience']):
            company_location = job['company']
            title = job.get('title', '').strip()
            duration = job.get('duration', '').strip()
            
            # Line 1: Company Name, Location (Bold)
            company_para = doc.add_paragraph(company_location)
            company_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
            company_run = company_para.runs[0]
            company_run.font.size = Pt(11)
            company_run.font.name = 'Calibri'
            company_run.font.bold = True
            company_para.space_after = Pt(1)
            
            # Line 2: Job Title | Duration (Bold)
            if title and duration:
                title_line = f"{title} | {duration}"
            elif title:
                title_line = title
            else:
                title_line = ""
            
            if title_line:
                title_para = doc.add_paragraph(title_line)
                title_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
                title_run = title_para.runs[0]
                title_run.font.size = Pt(11)
                title_run.font.name = 'Calibri'
                title_run.font.bold = True
                title_para.space_after = Pt(2)
            
            # Optional: "Roles and Responsibilities" heading (can be removed if not needed)
            # Uncomment the lines below to match original resume format exactly
            # roles_para = doc.add_paragraph('Roles and Responsibilities')
            # roles_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
            # roles_run = roles_para.runs[0]
            # roles_run.font.size = Pt(11)
            # roles_run.font.name = 'Calibri'
            # roles_run.font.bold = False
            # roles_run.font.italic = True
            # roles_para.space_after = Pt(2)
            
            # Add responsibilities
            for resp in job['responsibilities']:
                if resp.strip():
                    bullet_para = doc.add_paragraph(resp, style='List Bullet')
                    bullet_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    bullet_para.paragraph_format.left_indent = Inches(0.25)
                    bullet_para.paragraph_format.first_line_indent = Inches(-0.25)
                    
                    bullet_run = bullet_para.runs[0]
                    bullet_run.font.size = Pt(11)
                    bullet_run.font.name = 'Calibri'
                    bullet_para.space_after = Pt(1)
            
            # Add spacing between jobs
            if idx < len(sections['experience']) - 1:
                spacer = doc.add_paragraph()
                spacer.space_after = Pt(4)
    
    # Education Section - Matching original format with bullets
    if sections['education']:
        edu_heading = doc.add_paragraph('EDUCATION')
        edu_heading.alignment = WD_ALIGN_PARAGRAPH.LEFT
        edu_heading_run = edu_heading.runs[0]
        edu_heading_run.font.size = Pt(12)
        edu_heading_run.font.bold = True
        edu_heading_run.font.name = 'Calibri'
        edu_heading.space_before = Pt(6)
        edu_heading.space_after = Pt(3)
        
        # Parse education entries
        edu_text = sections['education'].strip()
        edu_lines = edu_text.split('\n')
        
        current_degree = None
        for line in edu_lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line starts with bullet (● or •) - this is the degree line
            if line.startswith('●') or line.startswith('•'):
                # This is a degree line
                degree_text = line.lstrip('●•').strip()
                
                # Add degree with bullet
                degree_para = doc.add_paragraph()
                degree_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
                
                # Add bullet symbol
                bullet_run = degree_para.add_run('● ')
                bullet_run.font.size = Pt(11)
                bullet_run.font.name = 'Calibri'
                bullet_run.font.bold = True
                
                # Add degree text
                degree_run = degree_para.add_run(degree_text)
                degree_run.font.size = Pt(11)
                degree_run.font.name = 'Calibri'
                degree_run.font.bold = True
                degree_para.space_after = Pt(1)
                
                current_degree = True
            else:
                # This is a university/date line (indented)
                uni_para = doc.add_paragraph(line)
                uni_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
                uni_para.paragraph_format.left_indent = Inches(0.15)  # Slight indent
                
                uni_run = uni_para.runs[0]
                uni_run.font.size = Pt(11)
                uni_run.font.name = 'Calibri'
                uni_para.space_after = Pt(4)
    
    return doc