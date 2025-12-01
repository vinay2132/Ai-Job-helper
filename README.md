# 💼 AI Career Assistant

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-job-apper-stpsmek9axyvqxkskqn6yl.streamlit.app/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Gemini AI](https://img.shields.io/badge/AI-Gemini%202.5%20Flash-orange)](https://deepmind.google/technologies/gemini/)
[![LangChain](https://img.shields.io/badge/LangChain-Powered-green)](https://langchain.com/)

A powerful, secure, and modular AI-powered assistant designed to streamline your job application process. Built with **Streamlit** and **Google Gemini 2.5 Flash**, this tool helps you generate tailored emails, update resumes, create cover letters, and prepare for interviews using your own documents.

---

## 🌟 Live Demo

Check out the live application here: **[AI Career Assistant](https://ai-job-apper-stpsmek9axyvqxkskqn6yl.streamlit.app/)**

---

## 🚀 Features

### 📧 Smart Email Writer
Generates professional, tailored job application emails based on your resume and the specific job description. It highlights relevant skills and experience to grab the recruiter's attention.

### 📄 Resume Updater
Analyzes your current resume against a job description and suggests specific improvements and keyword additions to increase your chances of passing ATS (Applicant Tracking Systems).

### 🎯 Advanced DOCX Formatter
A 3-stage professional resume generator that formats your resume into a clean, modern DOCX document. It ensures consistent styling, proper margins, and professional typography.

### ✉️ Cover Letter Generator
Creates personalized, compelling cover letters that tell your professional story and explain why you are the perfect fit for the role.

### 💬 Q&A Assistant (RAG)
Chat with your documents! Uses **LangChain** and **ChromaDB** to create a Retrieval-Augmented Generation (RAG) system. Ask questions about your resume, projects, or the job description to prepare for interviews.

### 📊 Document Summary
Quickly get a summary of long job descriptions or your own resume to identify key points and requirements at a glance.

### 🔍 Job Preview & Fetcher
Automatically fetch and extract job descriptions directly from URLs. No need to copy-paste manually!

### 🔐 Secure Key Manager
Your API keys are stored securely using encryption. We prioritize your privacy and security.

---

## 📂 Project Structure

```
.
├── components/          # Streamlit UI components for each feature
├── config/              # Configuration files (constants, session state)
├── data/                # Directory for your resume and project files
├── tests/               # Unit tests
├── utils/               # Helper functions, document processing, and logic
├── main.py              # Main application entry point
├── requirements.txt     # Project dependencies
└── README.md            # Documentation
```

---

## 🛠️ Installation & Local Setup

Follow these steps to run the application on your local machine.

### 1. Clone the Repository
```bash
git clone https://github.com/vinay2132/Ai-Job-helper.git
cd Ai-Job-helper
```

### 2. Install Dependencies
Make sure you have Python installed. Then run:
```bash
pip install -r requirements.txt
```

### 3. Configure Personal Details
Open `config/constants.py` and update the `PERSONAL_DETAILS_TEMPLATE` with your own information (Name, Email, Phone, Links, etc.) to ensure the generated content is accurate for you.

### 4. Run the Application
```bash
streamlit run main.py
```

---

## 🚦 Usage Guide

1.  **Setup Security**: On the first run, you will be prompted to enter your **Gemini API Key**. This key is encrypted and stored locally. You will also create a password to unlock the app in future sessions.
    *   *Don't have a key? Get one from [Google AI Studio](https://makersuite.google.com/app/apikey).*

2.  **Upload Documents**:
    *   Place your resume (PDF) in the `data/` folder (default: `Vinay_Ramesh_full_stack_developer.pdf`).
    *   Place your projects list (TXT) in the `data/` folder (default: `My_projects.txt`).
    *   *Alternatively, use the sidebar to upload files manually.*

3.  **Configure Job Description**:
    *   Paste a Job Description manually in the sidebar.
    *   OR paste a Job URL to fetch the description automatically.

4.  **Generate Content**: Navigate through the tabs to generate emails, update your resume, or create cover letters.

---

## 💻 Technologies Used

*   **Frontend**: [Streamlit](https://streamlit.io/)
*   **LLM**: [Google Gemini 2.5 Flash](https://deepmind.google/technologies/gemini/)
*   **Orchestration**: [LangChain](https://langchain.com/)
*   **Vector Database**: [ChromaDB](https://www.trychroma.com/)
*   **Document Processing**: PyPDF2, python-docx, BeautifulSoup4

---

## 🤝 Contributing

Contributions are welcome! If you have suggestions or improvements, please fork the repository and submit a Pull Request.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 📞 Contact

**Vinay Ramesh**  
📧 [vinayramesh6020@gmail.com](mailto:vinayramesh6020@gmail.com)  
🔗 [LinkedIn](https://www.linkedin.com/in/vinayramesh6020/)  
🌐 [Portfolio](https://vinay2132.github.io/my_portfolio/)
