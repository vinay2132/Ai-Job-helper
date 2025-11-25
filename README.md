# 💼 AI Career Assistant

A powerful, secure, and modular AI-powered assistant designed to streamline your job application process. Built with **Streamlit** and **Google Gemini 2.5 Flash**.

## 🚀 Features

-   **🔐 Secure Key Manager**: Encrypted storage for your API key. No more hardcoding keys or using `.env` files insecurely.
-   **📧 Smart Email Writer**: Generates tailored emails based on your resume and job description.
-   **📄 Resume Updater**: Suggests improvements to your resume to match specific job requirements.
-   **🎯 DOCX Formatter**: Professional resume formatting.
-   **✉️ Cover Letter Generator**: Creates personalized cover letters.
-   **💬 Q&A Assistant**: Chat with your documents to prepare for interviews.
-   **📊 Document Summary**: Quickly analyze job descriptions and resumes.
-   **🧠 RAG System**: Semantic search across your documents for accurate context.

## 📂 Project Structure

```
.
├── components/          # Streamlit UI components
├── config/              # Configuration files
├── data/                # Your resume and project files (Place files here!)
├── tests/               # Unit tests
├── utils/               # Helper functions and logic
├── main.py              # Main application entry point
├── requirements.txt     # Project dependencies
└── README.md            # Documentation
```

## 🛠️ Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/vinay2132/Ai-Job-helper.git
    cd Ai-Job-helper
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## 🚦 Usage

1.  **Prepare your data**:
    *   Place your resume (PDF) in the `data/` folder.
    *   Place your projects list (TXT) in the `data/` folder.

2.  **Run the application**:
    ```bash
    streamlit run main.py
    ```

3.  **Setup Security**:
    *   On the first run, you will be asked to enter your **Gemini API Key** and create a **Password**.
    *   Your key will be securely encrypted.
    *   On subsequent runs, just enter your password to unlock the app.

## 🔑 API Key

Get your Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
