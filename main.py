import os
import streamlit as st
import logging
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai.llm import LLM  # Import CrewAI's LLM class
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from propmpts import qna_agent_prompt, questions_list, diagnostic_agent_prompt, research_agent_prompt, coordinator_agent_prompt, critique_agent_prompt, presentation_agent_prompt
from models import PatientQnA
import json
from PIL import Image
import io
from crewai.tools import tool, BaseTool
from typing import List, Dict, Any

# Load environment variables
load_dotenv()

# Helper function for processing tabular data in markdown
def process_markdown_tables(content):
    """Process markdown content to enhance table display in Streamlit"""
    import re
    
    # Handle CrewOutput object - convert to string
    if hasattr(content, 'raw') and hasattr(content, 'pydantic_output'):
        # CrewOutput object - extract the string content
        content_str = str(content.raw) if content.raw else str(content)
        logger.info("Converted CrewOutput to string for table processing")
    elif hasattr(content, '__str__'):
        # Any object with string representation
        content_str = str(content)
    else:
        # Already a string
        content_str = content
    
    # Find all markdown tables in the content
    table_pattern = r'(\|[^\n]+\|(?:\n\|[^\n]+\|)*)'
    tables = re.findall(table_pattern, content_str)
    
    if tables:
        logger.info(f"Found {len(tables)} tables in the assessment output")
        
        # Split content by tables to handle each section separately
        parts = re.split(table_pattern, content_str)
        processed_content = ""
        
        table_count = 0
        for i, part in enumerate(parts):
            if part.strip().startswith('|') and '\n|' in part:
                # This is a table - display it with enhanced formatting
                table_count += 1
                if table_count == 1:
                    processed_content += f"\n\n**📋 Assessment Summary:**\n\n"
                elif table_count == 2:
                    processed_content += f"\n\n**📊 Risk Factors Summary:**\n\n"
                else:
                    processed_content += f"\n\n**📈 Additional Data:**\n\n"
                processed_content += part.strip() + "\n\n"
            else:
                processed_content += part
        
        return processed_content
    
    return content_str

# Helper function for auto-scrolling
def scroll_to_bottom():
    """Add JavaScript to auto-scroll chat to bottom"""
    st.markdown(
        """
        <script>
            function scrollToBottom() {
                // Scroll the main content area
                parent.window.scrollTo({
                    top: parent.document.body.scrollHeight,
                    behavior: 'smooth'
                });
                
                // Also try to scroll any chat containers
                var containers = parent.document.querySelectorAll('[data-testid="stVerticalBlock"]');
                containers.forEach(function(container) {
                    container.scrollTop = container.scrollHeight;
                });
            }
            // Delay scroll to ensure content is rendered
            setTimeout(scrollToBottom, 150);
        </script>
        """,
        unsafe_allow_html=True
    )

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ckd_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global variable to track current provider for tools
_current_provider = None

# Configure page
st.set_page_config(
    page_title="Chronic Kidney Disease Assistant",
    page_icon="🩺",
    layout="wide"
)

# LLM Provider selection - updated to use CrewAI's LLM class
def get_llm(provider, model=None):
    global _current_provider
    _current_provider = provider  # Update global provider
    
    if provider == "openai":
        return LLM(
            model="openai/gpt-4o",
            temperature=0.2
        )
    elif provider == "groq":
        groq_models = {
            "llama": "llama-3.3-70b-versatile",
            "deepseek": "deepseek-r1-distill-llama-70b",
            "mistral": "mixtral-8x7b-32768"
        }
        selected_model = groq_models.get(model, "llama-3.3-70b-versatile")
        return LLM(
            model=f"groq/{selected_model}",
            temperature=0.2
        )
    else:
        raise ValueError(f"Unsupported provider: {provider}")

# Get embeddings based on LLM provider
def get_embeddings(provider):
    if provider == "openai":
        return OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))
    else:  # groq models
        return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Initialize vector store
def initialize_vector_store(provider="openai"):
    db_path = f"./chroma_db_{provider}"
    
    # Check if we already have a vector store for this provider
    if os.path.exists(db_path):
        # Load existing vector store
        embeddings = get_embeddings(provider)
        return Chroma(persist_directory=db_path, embedding_function=embeddings)
    
    # Create new vector store
    # Load documents from data directory (PDFs and TXT files)
    pdf_loader = DirectoryLoader("./data", glob="**/*.pdf", loader_cls=PyPDFLoader)
    txt_loader = DirectoryLoader("./data", glob="**/*.txt", loader_cls=TextLoader)
    
    pdf_documents = pdf_loader.load()
    txt_documents = txt_loader.load()
    documents = pdf_documents + txt_documents
    
    logger.info(f"Loaded {len(pdf_documents)} PDF documents and {len(txt_documents)} TXT documents")
    
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(documents)
    
    # Create vector store
    embeddings = get_embeddings(provider)
    vector_store = Chroma.from_documents(
        documents=chunks, 
        embedding=embeddings,
        persist_directory=db_path
    )
    vector_store.persist()
    return vector_store

# Load patient response data
def load_patient_data():
    try:
        # Load past patient responses
        with open("data/past_patient_responses.json", "r") as f:
            past_data = json.load(f)
        
        # Load present patient responses
        with open("data/present_patient_responses.json", "r") as f:
            present_data = json.load(f)
        
        # Limit the data to a reasonable size for the prompt
        # Take first 5 patients as examples
        past_sample = past_data[:5]
        present_sample = present_data[:5]
        
        return json.dumps(past_sample, indent=1), json.dumps(present_sample, indent=1)
    except FileNotFoundError:
        # Return empty data if files don't exist
        print("Warning: Patient response data files not found. Run scripts/data_converter.py first.")
        return "[]", "[]"
    except Exception as e:
        print(f"Error loading patient data: {str(e)}")
        return "[]", "[]"

@tool("Analyze Diagnostic Image")
def analyze_diagnostic_image(image_bytes: str) -> str:
    """Analyze a diagnostic image for signs of kidney disease"""
    # This would typically call an image analysis API or model
    # For now, we'll return a placeholder response
    return "Analysis of diagnostic image shows potential indicators of kidney function changes."

@tool("Search Medical Knowledge")
def search_medical_knowledge(query: str) -> str:
    """Search for relevant medical information about chronic kidney disease from KDIGO guidelines and medical literature"""
    try:
        # Get current provider from global variable or session state
        if hasattr(st, 'session_state') and 'current_llm_provider' in st.session_state:
            provider = st.session_state.current_llm_provider
        else:
            provider = _current_provider
            if provider is None:
                raise ValueError(f"No LLM provider set! Current provider: {_current_provider}, Session state available: {hasattr(st, 'session_state')}")
        vector_store = initialize_vector_store(provider)
        logger.info(f"Searching medical knowledge for: {query} using {provider} embeddings")
        
        # Search for relevant documents
        results = vector_store.similarity_search(query, k=5)
        
        if not results:
            logger.warning(f"No results found for query: {query}")
            return "No relevant medical information found for this query."
        
        # Format the results with source information
        formatted_results = []
        for i, doc in enumerate(results, 1):
            source = doc.metadata.get('source', 'Unknown source')
            content = doc.page_content.strip()
            formatted_results.append(f"Source {i} ({source}):\n{content}")
        
        combined_results = "\n\n" + "="*50 + "\n\n".join(formatted_results)
        logger.info(f"Found {len(results)} relevant documents for query: {query}")
        
        return combined_results
        
    except Exception as e:
        logger.error(f"Error searching medical knowledge: {str(e)}")
        return f"Error accessing medical knowledge base: {str(e)}"

# Add this custom tool for asking questions
class QuestionAsker(BaseTool):
    name: str = "ask_question"
    description: str = "Ask the patient a question and get their response"
    
    def __init__(self):
        super().__init__()
        # Initialize question tracking
        if "current_question_index" not in st.session_state:
            st.session_state.current_question_index = 0
            logger.info("Initialized current_question_index to 0")
        if "collected_answers" not in st.session_state:
            st.session_state.collected_answers = []
            logger.info("Initialized collected_answers as empty list")
        
        # Always refresh questions from prompts.py to handle changes
        current_questions = [q.strip() for q in questions_list.strip().split('\n') if q.strip()]
        
        # Check if questions have changed or need initialization
        if ("questions" not in st.session_state or 
            st.session_state.questions != current_questions):
            
            st.session_state.questions = current_questions
            logger.info(f"Updated questions list with {len(st.session_state.questions)} questions from prompts.py")
            
            # Reset session if questions changed mid-session
            if "questions" in st.session_state and st.session_state.current_question_index > 0:
                logger.warning("Questions list changed mid-session - resetting QnA state")
                st.session_state.current_question_index = 0
                st.session_state.collected_answers = []
                st.session_state.waiting_for_answer = False
        
        if "waiting_for_answer" not in st.session_state:
            st.session_state.waiting_for_answer = False
            logger.info("Initialized waiting_for_answer to False")
        if "current_question" not in st.session_state:
            st.session_state.current_question = ""
            logger.info("Initialized current_question as empty string")
    
    def _run(self, query: str = None) -> str:
        """Ask the next question or get the current answer"""
        logger.info(f"QuestionAsker._run called - waiting_for_answer: {st.session_state.waiting_for_answer}, current_question_index: {st.session_state.current_question_index}")
        
        # If we're waiting for an answer, return the latest user response
        if st.session_state.waiting_for_answer:
            if "latest_user_response" in st.session_state and st.session_state.latest_user_response:
                # Get the response
                response = st.session_state.latest_user_response
                logger.info(f"Received patient response: {response}")
                
                # Store the answer
                answer_data = {
                    "question": st.session_state.current_question,
                    "answer": response
                }
                st.session_state.collected_answers.append(answer_data)
                logger.info(f"Stored answer #{len(st.session_state.collected_answers)}: {answer_data}")
                
                # Clear the response and move to next question
                st.session_state.latest_user_response = ""
                st.session_state.waiting_for_answer = False
                st.session_state.current_question_index += 1
                
                logger.info(f"Moving to next question. New index: {st.session_state.current_question_index}")
                return f"Patient answered: {response}"
            else:
                logger.info("Still waiting for patient response...")
                return "Waiting for patient response..."
        
        # If we have more questions to ask
        if st.session_state.current_question_index < len(st.session_state.questions):
            # Get the next question
            question = st.session_state.questions[st.session_state.current_question_index]
            st.session_state.current_question = question
            
            # Mark that we're waiting for an answer
            st.session_state.waiting_for_answer = True
            
            logger.info(f"Asking question #{st.session_state.current_question_index + 1}: {question}")
            
            # Return the question to be asked
            return f"QUESTION: {question}"
        else:
            # All questions have been asked
            final_json = json.dumps(st.session_state.collected_answers, indent=2)
            logger.info("All questions completed!")
            logger.info(f"Final collected answers JSON:\n{final_json}")
            logger.info(f"Total answers collected: {len(st.session_state.collected_answers)}")
            
            # Display the JSON in Streamlit for debugging
            with st.expander("DEBUG: View Collected QnA Data", expanded=False):
                st.json(st.session_state.collected_answers)
                st.text(f"Total questions answered: {len(st.session_state.collected_answers)}")
            
            return "All questions have been asked. Here are the collected answers: " + final_json

# Streamlit UI

def main():
    st.title("Chronic Kidney Disease Assistant")
    
    # Sidebar for configuration
    st.sidebar.title("Configuration")
    llm_provider = st.sidebar.selectbox("Select LLM Provider", ["groq", "openai"])
    
    # Store provider in session state for embedding consistency
    st.session_state.current_llm_provider = llm_provider
    
    if llm_provider == "groq":
        groq_model = st.sidebar.selectbox("Select Groq Model", ["llama", "deepseek", "mistral"])
        llm = get_llm(llm_provider, groq_model)
    else:
        llm = get_llm(llm_provider)
    
    # Add session management
    st.sidebar.title("Session Management")
    if st.sidebar.button("🔄 Reset Session", help="Clear all questions and answers to start fresh"):
        # Reset all session state related to QnA
        keys_to_reset = [
            "current_question_index", "collected_answers", "questions", 
            "waiting_for_answer", "current_question", "latest_user_response", 
            "crew_running", "messages"
        ]
        for key in keys_to_reset:
            if key in st.session_state:
                del st.session_state[key]
        
        logger.info("Session reset by user")
        st.sidebar.success("Session reset! Refresh the page to start fresh.")
        st.rerun()
    
    # Display current session info
    if "questions" in st.session_state:
        st.sidebar.info(f"📋 Questions loaded: {len(st.session_state.questions)}")
        if "collected_answers" in st.session_state:
            st.sidebar.info(f"✅ Answers collected: {len(st.session_state.collected_answers)}")
        if "current_question_index" in st.session_state:
            progress = st.session_state.current_question_index / len(st.session_state.questions)
            st.sidebar.progress(progress, text=f"Progress: {st.session_state.current_question_index}/{len(st.session_state.questions)}")
    
    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Add image upload in sidebar
    st.sidebar.title("Diagnostic Images")
    uploaded_file = st.sidebar.file_uploader("Upload diagnostic images", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # Display the uploaded image
        image = Image.open(uploaded_file)
        st.sidebar.image(image, caption="Uploaded Diagnostic Image", use_column_width=True)
        
        # Store the image in session state for the diagnostic agent to use
        image_bytes = io.BytesIO()
        image.save(image_bytes, format=image.format)
        st.session_state.diagnostic_image = image_bytes.getvalue()
        st.sidebar.success("Image uploaded successfully! The diagnostic agent will analyze this image.")
    
    # Create chat container with auto-scroll
    chat_container = st.container()
    
    # Display chat history in container
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Auto-scroll to bottom after displaying messages
    if len(st.session_state.messages) > 0:
        scroll_to_bottom()
    
    # Initialize the question asker tool
    question_asker = QuestionAsker()
    
    # Check if we're in the middle of a QnA session
    if "crew_running" not in st.session_state:
        st.session_state.crew_running = False
    
    # Dynamic chat input based on state
    if not st.session_state.crew_running:
        chat_prompt = "Ask about chronic kidney disease..."
    elif st.session_state.waiting_for_answer:
        chat_prompt = "Your answer:"
    else:
        chat_prompt = "Please wait..."
    
    # Single chat input that changes based on state
    user_input = st.chat_input(chat_prompt)
    
    # Handle initial query to start QnA process
    if not st.session_state.crew_running and user_input:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("I'll help assess your risk of chronic kidney disease. I need to ask you some questions first.")
            
            # Add to chat history
            st.session_state.messages.append({"role": "assistant", "content": "I'll help assess your risk of chronic kidney disease. I need to ask you some questions first."})
            
            # Mark crew as running
            st.session_state.crew_running = True
            
            # Reset question index and collected answers for fresh start
            st.session_state.current_question_index = 0
            st.session_state.collected_answers = []
            st.session_state.waiting_for_answer = False
            
            logger.info(f"Starting fresh QnA session with {len(st.session_state.questions)} questions")
            
            # Auto-scroll after adding message
            scroll_to_bottom()
            
            # Rerun to start asking questions
            st.rerun()
    
    # If crew is running and we're waiting for an answer
    elif st.session_state.crew_running and st.session_state.waiting_for_answer:
        # Display the current question if not already displayed
        if st.session_state.messages[-1]["content"] != st.session_state.current_question:
            with st.chat_message("assistant"):
                st.markdown(st.session_state.current_question)
            
            # Add to chat history
            st.session_state.messages.append({"role": "assistant", "content": st.session_state.current_question})
            
            # Auto-scroll after adding question
            scroll_to_bottom()
        
        # Handle QnA responses using the same chat input
        if user_input:
            # Store the response
            st.session_state.latest_user_response = user_input
            
            # Add to chat history
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(user_input)
            
            # Auto-scroll after user response
            scroll_to_bottom()
            
            # Process the answer and move to next question
            question_asker._run()
            
            # Rerun to show next question or results
            st.rerun()
    
    # If crew is running but we've finished asking questions
    elif st.session_state.crew_running and st.session_state.current_question_index >= len(st.session_state.questions):
        # Execute crew
        with st.spinner("Analyzing your responses..."):
            try:
                # Prepare collected answers
                collected_answers_json = json.dumps(st.session_state.collected_answers, indent=2)
                logger.info(f"Starting crew analysis with {len(st.session_state.collected_answers)} patient responses")
                
                # Create agents with current patient data
                qna_agent, research_agent, diagnostic_agent, critique_agent, presentation_agent = create_agents(llm, collected_answers_json)
                
                # Create tasks with the collected answers
                tasks = create_tasks(qna_agent, research_agent, diagnostic_agent, critique_agent, presentation_agent, collected_answers_json)
                
                # Add image analysis if available
                if "diagnostic_image" in st.session_state:
                    diagnostic_agent.tools = [analyze_diagnostic_image]
                
                # Create crew with provider-specific memory configuration
                crew = Crew(
                    agents=[qna_agent, research_agent, diagnostic_agent, critique_agent, presentation_agent],
                    tasks=tasks,
                    verbose=True,
                    process=Process.sequential,
                    memory=False if st.session_state.current_llm_provider == "groq" else True  # Disable memory for Groq to avoid embedding issues
                )
                
                # Add image analysis if available
                if "diagnostic_image" in st.session_state:
                    diagnostic_agent.tools = [analyze_diagnostic_image]
                    logger.info("Diagnostic image available for analysis")
                
                # Run the crew
                logger.info("Starting CrewAI execution...")
                result = crew.kickoff()
                logger.info(f"CrewAI execution completed successfully. Result type: {type(result)}")
                
                # Log result structure for debugging
                if hasattr(result, 'raw'):
                    logger.info(f"CrewOutput.raw length: {len(str(result.raw))}")
                else:
                    logger.info(f"Result string length: {len(str(result))}")
                
            except Exception as e:
                logger.error(f"Error during crew execution: {str(e)}")
                st.error(f"An error occurred during analysis: {str(e)}")
                return
        
        # Process and display result with enhanced table formatting
        processed_result = process_markdown_tables(result)
        
        with st.chat_message("assistant"):
            st.markdown(processed_result)
        
        # Add to chat history (convert CrewOutput to string for consistency)
        result_str = str(result.raw) if hasattr(result, 'raw') else str(result)
        st.session_state.messages.append({"role": "assistant", "content": result_str})
        
        # Auto-scroll after final result
        scroll_to_bottom()
        
        # Reset crew state
        st.session_state.crew_running = False
        
    # If crew is running but we're not waiting for an answer, ask the next question
    elif st.session_state.crew_running and not st.session_state.waiting_for_answer:
        # Ask the next question
        next_question = question_asker._run()
        
        # If it's a real question (not a status message)
        if next_question.startswith("QUESTION:"):
            # Extract just the question text
            clean_question = next_question.replace("QUESTION: ", "")
            
            # Display the question
            with st.chat_message("assistant"):
                st.markdown(clean_question)
            
            # Add to chat history
            st.session_state.messages.append({"role": "assistant", "content": clean_question})
            
            # Auto-scroll after new question
            scroll_to_bottom()
            
            # Rerun to wait for answer
            st.rerun()

# Define agents
def create_agents(llm, current_patient_data=None):
    # Initialize vector store for RAG with matching provider
    provider = st.session_state.get('current_llm_provider', 'openai')
    vector_store = initialize_vector_store(provider)
    
    # Load historical patient data for research agent context
    past_patient_qna, present_patient_qna = load_patient_data()
    
    # QnA Agent
    qna_prompt = qna_agent_prompt.format(questions_list=questions_list)
    qna_agent = Agent(
        role="QnA Agent",
        goal="Ask the patient a series of questions to collect relevant medical information",
        backstory=qna_prompt,
        verbose=True,
        llm=llm,
        tools=[QuestionAsker()]  # Use our custom tool
    )
    
    # Research Agent - include current patient data if available
    if current_patient_data:
        ra_prompt = research_agent_prompt.format(
            past_patient_qna=past_patient_qna, 
            present_patient_qna=present_patient_qna,
            current_patient_responses=current_patient_data
        )
    else:
        ra_prompt = research_agent_prompt.format(
            past_patient_qna=past_patient_qna, 
            present_patient_qna=present_patient_qna
        )
    
    research_agent = Agent(
        role="Research Agent",
        goal="Research CKD and assess risk percentage based on current patient's responses and historical data patterns.",
        backstory=ra_prompt,
        verbose=True,
        llm=llm,
        tools=[search_medical_knowledge]
    )
    
    # Diagnostic Agent
    diagnostic_agent = Agent(
        role="Diagnostic Agent",
        goal="Analyze patient data and diagnostic images to predict CKD and assess its severity",
        backstory=diagnostic_agent_prompt,
        verbose=True,
        llm=llm,
        tools=[analyze_diagnostic_image]
    )
    
    # Critique Agent
    critique_agent = Agent(
        role="Critique Agent",
        goal="Ensure accuracy of CKD risk assessment and recommendations",
        backstory=critique_agent_prompt,
        verbose=True,
        llm=llm
    )
    
    # Add new Presentation Agent
    presentation_agent = Agent(
        role="Presentation Agent",
        goal="Present a clear, concise, and user-friendly CKD assessment to the patient",
        backstory=presentation_agent_prompt,
        verbose=True,
        llm=llm
    )
    
    return qna_agent, research_agent, diagnostic_agent, critique_agent, presentation_agent

# Define tasks
def create_tasks(qna_agent, research_agent, diagnostic_agent, critique_agent, presentation_agent, collected_patient_data):
    # Task 1: QnA agent processes collected patient information
    collect_info_task = Task(
        description=f"""
        Process the following patient responses collected from the questionnaire:
        
        {collected_patient_data}
        
        Your task is to:
        1. Review and validate the collected patient responses
        2. Organize the information in a structured format
        3. Identify any missing or unclear responses that might need clarification
        4. Format the data for analysis by other agents
        
        Focus on ensuring data quality and completeness for CKD risk assessment.
        """,
        agent=qna_agent,
        expected_output="Structured and validated patient questionnaire responses in JSON format"
    )
    
    # Task 2: Diagnostic agent analyzes patient data
    diagnostic_task = Task(
        description="Analyze the patient's responses and any diagnostic images to assess potential kidney issues",
        agent=diagnostic_agent,
        dependencies=[collect_info_task],
        expected_output="Diagnostic analysis of patient data and images"
    )
    
    # Task 3: Research agent makes comprehensive risk assessment
    research_task = Task(
        description="""
        Conduct a comprehensive CKD risk assessment using:
        1. Patient questionnaire responses from the QnA agent
        2. Diagnostic analysis from the diagnostic agent
        3. Historical patient data patterns
        4. KDIGO guidelines and medical knowledge
        
        Provide detailed factor analysis with:
        - Individual risk percentage for each factor
        - Evidence-based explanations
        - Overall risk calculation
        - Top 3 most concerning factors
        """,
        agent=research_agent,
        dependencies=[collect_info_task, diagnostic_task],
        expected_output="Comprehensive CKD risk assessment with detailed factor analysis and percentage contributions"
    )
    
    # Task 4: Critique agent reviews the assessment
    critique_task = Task(
        description="Review and critique the CKD risk assessment for accuracy and completeness",
        agent=critique_agent,
        dependencies=[research_task],
        expected_output="Final verified CKD assessment with critique and corrections"
    )
    
    # Add new Presentation task
    presentation_task = Task(
        description="Create a clear, user-friendly presentation of the CKD assessment results",
        agent=presentation_agent,
        dependencies=[critique_task],
        expected_output="User-friendly CKD assessment report"
    )
    
    tasks = [collect_info_task, diagnostic_task, research_task, critique_task, presentation_task]
    
    return tasks

if __name__ == "__main__":
    main()
