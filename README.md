# Chronic Kidney Disease Multi-Agent System

This project uses a multi-agent system powered by CrewAI to predict chronic kidney disease and assess its severity. It combines medical knowledge, diagnostic capabilities, and research insights to provide comprehensive information about CKD.

## Features

- Multi-agent system with specialized medical agents
- Support for both OpenAI and Groq LLMs
- Interactive Streamlit chat interface
- Vector database for medical knowledge retrieval
- Prediction of CKD likelihood and severity assessment

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   GROQ_API_KEY=your_groq_api_key_here
   ```
5. Run the application:
   ```
   streamlit run main.py
   ```

## Usage

1. Select your preferred LLM provider (OpenAI or Groq) in the sidebar
2. If using Groq, select a specific model (Llama, DeepSeek, or Mistral)
3. Type your question about chronic kidney disease in the chat input
4. The multi-agent system will analyze your query, make predictions, and provide recommendations

## Project Structure

- `main.py`: Main application file with Streamlit UI and agent definitions
- `data/`: Directory containing medical information about CKD
- `chroma_db/`: Vector database for storing document embeddings (created on first run)

## Technologies Used

- Python
- Streamlit
- LangChain
- ChromaDB
- CrewAI
- OpenAI
- Groq 