"""
Constants and configuration values for the AI Career Assistant
"""

# API Configuration
DEFAULT_API_KEY = None
GEMINI_MODEL = "gemini-2.5-flash"

# File Configuration
DEFAULT_RESUME = "data/Vinay_Ramesh_full_stack_developer.pdf"
DEFAULT_PROJECTS = "data/My_projects.txt"
SUPPORTED_FILE_TYPES = ['pdf', 'docx', 'txt']

# Personal Details Template
PERSONAL_DETAILS_TEMPLATE = """
Full Name: Vinay Ramesh
Email: vinayramesh6020@gmail.com
Contact Number: +1 (682) 273-5833
Portfolio: https://vinay2132.github.io/my_portfolio/
GitHub: https://github.com/vinay2132
Education: Master of Science in Data Science (UNT, Sep 2023 – Dec 2024), Bachelor of Technology in Computer Science (TKR College of Engineering & Technology, Jun 2017 – May 2021)
Current Location: Tracy, California, United States
Relocation: Yes
Availability to Take Call: Yes
Availability to Join: Within 1-2 weeks
Relevant Experience: 3+ years in Full Stack Development
Visa/Work Authorization: F1 OPT
"""

# AI Persona Configuration
AI_PERSONA_TEMPLATE = """
You are an AI coding assistant. Your persona is a **mid-level full-stack developer with 3-4 years of professional experience**.

Your communication style must follow these rules:
1. **Human-like Tone:** Respond like a real colleague. Be helpful and confident, but not overly robotic or formal. It's okay to use contractions (like "don't" or "it's").
2. **Intentional Flaws:** Your responses should occasionally include minor, natural-sounding grammatical mistakes. For example, you might misuse a preposition, forget an article ("the" or "a"), or have a slight run-on sentence. Do not make major, nonsensical errors.
3. **Concise and Efficient:** Get straight to the point. Your answers must be **crisp, short, and efficient**. Avoid filler phrases and unnecessary explanations.
4. **Key Formatting:** You MUST use **Markdown** to format your response.
   * **Bold** any critical keywords, function names, file names, or concepts (e.g., `**React hook**`, `**.env file**`, `**asynchronous**`).
5. **Focus:** Act as a pair programmer helping with a job application task. Your primary goal is to provide useful, direct code or information.
"""

# Writing Guidelines Template
WRITING_GUIDELINES_TEMPLATE = """
CRITICAL WRITING GUIDELINES - MUST FOLLOW FOR ALL OUTPUTS:

1. TONE & STYLE:
   - Write as a seasoned professional with 3+ years of experience
   - Make it sound HUMAN and natural, NOT AI-generated
   - Be professional, confident, and recruiter-friendly
   - Avoid over-formal or robotic language

2. FORMATTING RULES:
   - DO NOT use highlighting, bold text, asterisks (**), or excessive markdown
   - Keep content clean and simple
   - For emails: Include a relevant subject line at the top
   - Use proper paragraph spacing, but keep it minimal

3. EMAIL-SPECIFIC RULES:
   - Keep emails SHORT (1-2 concise paragraphs maximum)
   - Highlight specific technologies from BOTH job description and resume
   - If no hiring manager name is provided, use: "Dear Hiring Manager,"
   - ALWAYS mention F1 OPT work authorization clearly when relevant
   - ALWAYS include portfolio and GitHub links in signature
   - ALWAYS use this exact signature format:

--
Best regards,
Vinay Ramesh
Senior Full Stack Developer
📧 vinayramesh6020@gmail.com
📞 +1 (682) 273-5833
🌐 Portfolio: https://vinay2132.github.io/my_portfolio/
🔗 LinkedIn: https://www.linkedin.com/in/vinayramesh6020/
💻 GitHub: https://github.com/vinay2132

4. CONTENT REQUIREMENTS:
   - Incorporate personal details naturally where relevant
   - Match technologies and skills to the job requirements
   - Be specific and avoid generic phrases
   - Show genuine interest and understanding of the role

5. GENERAL RULES FOR ALL OUTPUTS:
   - Prioritize clarity and readability
   - Use active voice
   - Be concise and to the point
   - Proofread for grammar and professionalism
"""

# Streamlit Page Configuration
PAGE_CONFIG = {
    "page_title": "AI Career Assistant",
    "page_icon": "💼",
    "layout": "wide"
}

# Tab Configuration
# UPDATED: Added new tab for DOCX Formatter
TABS = [
    "📧 Email Writer",
    "📄 Resume Updater",
    "🎯 DOCX Formatter",  # NEW TAB - 3-Stage Professional Resume Generator
    "✉️ Cover Letter",
    "💬 Q&A Assistant",
    "📊 Document Summary"
]