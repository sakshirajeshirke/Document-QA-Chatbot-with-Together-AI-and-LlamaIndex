import os
import streamlit as st
import tempfile
import uuid
from datetime import datetime
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.llms.together import TogetherLLM
from llama_index.embeddings.together import TogetherEmbedding
from llama_index.core.postprocessor import SimilarityPostprocessor
from langfuse import Langfuse
from langfuse.llama_index import LlamaIndexCallbackHandler
from llama_index.core.callbacks import CallbackManager

# Custom CSS for enhanced UI
def load_css():
    st.markdown("""
    <style>
    /* Main app styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Header styling */
    h1 {
        color: #4A56A6;
        font-size: 2.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    h2, h3, h4 {
        color: #4A56A6;
    }
    
    /* Chat message styling */
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.8rem;
        margin-bottom: 1rem;
        display: flex;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }
    
    .user-message {
        background-color: #E9F0FF;
        border-left: 5px solid #4A56A6;
    }
    
    .assistant-message {
        background-color: #F5F5F5;
        border-left: 5px solid #42A5F5;
    }
    
    /* File uploader styling */
    .uploadedFile {
        border: 1px solid #ddd;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
        background-color: #f9f9f9;
    }
    
    /* Custom buttons */
    .custom-button {
        background-color: #4A56A6;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        text-align: center;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    
    .custom-button:hover {
        background-color: #394480;
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-active {
        background-color: #4CAF50;
    }
    
    .status-inactive {
        background-color: #F44336;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background-color: #f5f7f9;
    }
    
    /* Loading spinner */
    .stSpinner > div > div {
        border-color: #4A56A6 !important;
    }
    
    /* Card container */
    .card-container {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        margin-top: 2rem;
        padding-top: 1rem;
        color: #6c757d;
        font-size: 0.8rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Set page configuration - MUST BE FIRST STREAMLIT COMMAND
st.set_page_config(page_title="Document QA Chatbot", page_icon="🤖", layout="wide")

# Load custom CSS
load_css()

# Load environment variables from .env file
load_dotenv()

# Get environment variables
together_api_key = os.getenv("TOGETHER_API_KEY")
langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY")
langfuse_host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

# Title and description with improved layout
col1, col2 = st.columns([1, 3])
with col1:
    st.image("https://img.freepik.com/free-vector/cute-robot-holding-phone-with-laptop-cartoon-vector-icon-illustration-science-technology-isolated_138676-4870.jpg?t=st=1746967647~exp=1746971247~hmac=e474420e7dd3c1aed5a1ef472467b1e8b2c13c9cce1fb75328241b4550026473&w=740", width=300)
with col2:
    st.title("📄 Document QA Chatbot")
    st.markdown("""
    <p style="font-size: 1.2rem; color: #666;">
        Interact with your documents using AI-powered question answering
    </p>
    """, unsafe_allow_html=True)

# Check if Together API key exists
if not together_api_key:
    st.error("Together API key not found in .env file. Please create a .env file with your TOGETHER_API_KEY.")
    st.code("TOGETHER_API_KEY=your-api-key-here", language="text")
    st.stop()

# Initialize Langfuse if credentials are available
langfuse_available = False
langfuse_client = None
langfuse_error = None

if langfuse_public_key and langfuse_secret_key:
    try:
        # Print debug info to console
        print(f"Initializing Langfuse with: Host={langfuse_host}, Public Key={langfuse_public_key[:5]}..., Secret Key={langfuse_secret_key[:5]}...")
        
        langfuse_client = Langfuse(
            public_key=langfuse_public_key,
            secret_key=langfuse_secret_key,
            host=langfuse_host
        )
        
        # Test Langfuse connection using trace() method instead of log_event()
        # This is more compatible with different Langfuse versions
        test_session_id = str(uuid.uuid4())
        print(f"Testing Langfuse connection with session_id: {test_session_id}")
        
        # Create a simple trace to test the connection
        trace = langfuse_client.trace(
            name="connection_test",
            id=test_session_id
        )
        
        # If we got here without an exception, connection is successful
        langfuse_available = True
        
        # Create the LlamaIndex callback handler for Langfuse
        langfuse_handler = LlamaIndexCallbackHandler(
            langfuse_client=langfuse_client,
            project_name="document-qa-chatbot"
        )
        callback_manager = CallbackManager([langfuse_handler])
        print("Langfuse initialized successfully!")
    except Exception as e:
        langfuse_error = str(e)
        print(f"Langfuse initialization error: {langfuse_error}")
        callback_manager = None
else:
    callback_manager = None
    langfuse_error = "Missing Langfuse credentials"

# Sidebar for model settings with improved design
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h3 style="color: #4A56A6;">⚙️ Configuration</h3>
        <hr style="margin: 0.5rem 0;">
    </div>
    """, unsafe_allow_html=True)
    
    # Status indicators with better design
    st.markdown("""
    <div style="background-color: white; padding: 15px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
        <h4 style="color: #4A56A6; margin-top: 0;">System Status</h4>
    """, unsafe_allow_html=True)
    
    # Together API status
    if together_api_key:
        st.markdown("""
        <div style="display: flex; align-items: center; margin-bottom: 10px;">
            <div class="status-indicator status-active"></div>
            <span style="font-weight: 500;">Together API: Connected</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="display: flex; align-items: center; margin-bottom: 10px;">
            <div class="status-indicator status-inactive"></div>
            <span style="font-weight: 500;">Together API: Disconnected</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Langfuse status
    if langfuse_available:
        st.markdown("""
        <div style="display: flex; align-items: center;">
            <div class="status-indicator status-active"></div>
            <span style="font-weight: 500;">Langfuse: Connected</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="display: flex; align-items: center;">
            <div class="status-indicator status-inactive"></div>
            <span style="font-weight: 500;">Langfuse: Disconnected</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Model selection with better UI
    st.markdown("""
    <div style="background-color: white; padding: 15px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
        <h4 style="color: #4A56A6; margin-top: 0;">AI Models</h4>
    """, unsafe_allow_html=True)
    
    llm_model = st.selectbox(
        "LLM Model",
        ["mistralai/Mistral-7B-Instruct-v0.2", 
         "meta-llama/Llama-2-13b-chat-hf",
         "togethercomputer/Llama-2-7B-32K-Instruct",
         "mistralai/Mixtral-8x7B-Instruct-v0.1",
         "Qwen/Qwen3-235B-A22B-fp8-tput"]
    )
    
    embedding_model = st.selectbox(
        "Embedding Model",
        ["togethercomputer/m2-bert-80M-8k-retrieval"]
    )
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Advanced settings
    st.markdown("""
    <div style="background-color: white; padding: 15px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
        <h4 style="color: #4A56A6; margin-top: 0;">Advanced Settings</h4>
    """, unsafe_allow_html=True)
    
    # Similarity threshold with explanation tooltip
    similarity_threshold = st.slider(
        "Similarity Threshold", 
        0.0, 1.0, 0.7, 0.1,
        help="Higher values require closer match between query and document content"
    )
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Actions section with styled buttons
    st.markdown("""
    <div style="background-color: white; padding: 15px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
        <h4 style="color: #4A56A6; margin-top: 0;">Actions</h4>
    """, unsafe_allow_html=True)
    
    clear_chat = st.button("🔄 Clear Chat", key="clear_chat")
    reset_index = st.button("🗑️ Reset Index", key="reset_index")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="footer">
        <hr style="margin: 1rem 0;">
        <p>Made with ❤️ using Together AI and LlamaIndex</p>
        <p>© 2025 Document QA System</p>
    </div>
    """, unsafe_allow_html=True)

# Session state initialization
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'index' not in st.session_state:
    st.session_state.index = None
if 'ready' not in st.session_state:
    st.session_state.ready = False
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Main section with two columns for chat and file upload
col_chat, col_upload = st.columns([2, 1])

with col_upload:
    st.markdown("""
    <div class="card-container">
        <h3 style="color: #4A56A6; margin-top: 0;">📁 Document Upload</h3>
    """, unsafe_allow_html=True)
    
    # File uploader with better UI
    uploaded_files = st.file_uploader(
        "Upload your documents", 
        accept_multiple_files=True, 
        type=["pdf", "docx", "txt"],
        help="Supported formats: PDF, DOCX, TXT"
    )
    
    # Show uploaded files with custom styling
    if uploaded_files:
        st.markdown("### Uploaded Files:")
        for file in uploaded_files:
            file_ext = file.name.split('.')[-1].upper()
            icon = "📄"
            if file_ext == "PDF":
                icon = "📕"
            elif file_ext == "DOCX":
                icon = "📘"
            elif file_ext == "TXT":
                icon = "📝"
            
            st.markdown(f"""
            <div class="uploadedFile">
                <div style="display: flex; align-items: center;">
                    <div style="font-size: 1.5rem; margin-right: 10px;">{icon}</div>
                    <div>
                        <div style="font-weight: bold;">{file.name}</div>
                        <div style="color: #666; font-size: 0.8rem;">{round(file.size/1024, 2)} KB</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0; color: #666;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📄</div>
            <p>Drag and drop your files or click to browse</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # System status and information
    if st.session_state.ready:
        st.markdown("""
        <div class="card-container" style="margin-top: 20px;">
            <h3 style="color: #4A56A6; margin-top: 0;">📊 System Status</h3>
            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <div class="status-indicator status-active"></div>
                <span style="font-weight: 500;">Index: Ready</span>
            </div>
            <p>Your documents are indexed and ready for querying!</p>
        </div>
        """, unsafe_allow_html=True)

with col_chat:
    # Chat interface with improved styling
    st.markdown("""
    <div class="card-container">
        <h3 style="color: #4A56A6; margin-top: 0;">💬 Chat</h3>
    """, unsafe_allow_html=True)
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        if not st.session_state.messages:
            st.markdown("""
            <div style="text-align: center; padding: 3rem 0; color: #666;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">👋</div>
                <p style="font-size: 1.2rem; margin-bottom: 0.5rem;">Welcome to Document QA Chatbot!</p>
                <p>Upload your documents and start asking questions.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Display styled chat messages
            for i, message in enumerate(st.session_state.messages):
                if message["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <div style="width: 30px; margin-right: 15px; flex-shrink: 0; align-self: start;">
                            <div style="background-color: #4A56A6; color: white; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                                👤
                            </div>
                        </div>
                        <div style="flex-grow: 1;">
                            <div style="font-weight: bold; margin-bottom: 5px;">You</div>
                            <div>{message["content"]}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message assistant-message">
                        <div style="width: 30px; margin-right: 15px; flex-shrink: 0; align-self: start;">
                            <div style="background-color: #42A5F5; color: white; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                                🤖
                            </div>
                        </div>
                        <div style="flex-grow: 1;">
                            <div style="font-weight: bold; margin-bottom: 5px;">Assistant</div>
                            <div>{message["content"]}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Chat input area
    if st.session_state.ready:
        query = st.chat_input("Ask a question about your documents...")
    else:
        st.markdown("""
        <div style="background-color: #f9f9f9; padding: 15px; border-radius: 10px; text-align: center; margin-top: 10px;">
            <p style="margin: 0; color: #666;">📝 Please upload documents to start chatting</p>
        </div>
        """, unsafe_allow_html=True)
        query = None

# Process files and build index
if uploaded_files and not st.session_state.ready and together_api_key:
    with st.spinner("Processing your documents..."):
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()
        
        # Save uploaded files to the temporary directory
        for file in uploaded_files:
            file_path = os.path.join(temp_dir, file.name)
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())
        
        # Initialize LLM and embedding model
        llm = TogetherLLM(
            model=llm_model,
            api_key=together_api_key,
            callback_manager=callback_manager
        )
        
        embed_model = TogetherEmbedding(
            model_name=embedding_model,
            api_key=together_api_key,
            callback_manager=callback_manager
        )
        
        try:
            # Load and index documents 
            start_time = datetime.now()
            documents = SimpleDirectoryReader(temp_dir).load_data()
            
            # Create index
            index = VectorStoreIndex.from_documents(
                documents, 
                embed_model=embed_model,
                callback_manager=callback_manager
            )
            
            # Save to session state
            st.session_state.index = index
            st.session_state.ready = True
            
            # Log document count and processing time manually
            if langfuse_available and langfuse_client:
                processing_time = (datetime.now() - start_time).total_seconds()
                try:
                    # Use trace instead of log_event for better compatibility
                    trace = langfuse_client.trace(
                        name="documents_processed",
                        id=str(uuid.uuid4())
                    )
                    trace.update(
                        metadata={
                            "file_count": len(uploaded_files),
                            "document_count": len(documents),
                            "processing_time_seconds": processing_time,
                            "file_types": [f.name.split('.')[-1] for f in uploaded_files],
                            "session_id": st.session_state.session_id
                        }
                    )
                except Exception as e:
                    print(f"Error logging to Langfuse: {str(e)}")
            
            # Add system message
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"✅ Documents processed! I've indexed {len(documents)} files. Ask me anything about your documents."
            })
            
        except Exception as e:
            # Log error
            if langfuse_available and langfuse_client:
                langfuse_client.log_event(
                    name="document_processing_error",
                    input={"file_count": len(uploaded_files)},
                    output={"error": str(e)},
                    session_id=st.session_state.session_id
                )
            st.error(f"Error processing documents: {str(e)}")
        
        st.rerun()

# Query input and response
if st.session_state.ready and query:
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": query})
    
    # Display assistant response
    with st.spinner("Searching for information..."):
        # Create query engine with similarity reranker
        reranker = SimilarityPostprocessor(similarity_cutoff=similarity_threshold)
        
        # Create a unique trace ID for this query
        query_id = f"query_{str(uuid.uuid4())}"
        
        # Initialize query engine with callback manager
        query_engine = st.session_state.index.as_query_engine(
            llm=TogetherLLM(
                model=llm_model, 
                api_key=together_api_key,
                callback_manager=callback_manager
            ),
            postprocessors=[reranker]
        )
        
        try:
            start_time = datetime.now()
            # Get response
            response = query_engine.query(query)
            response_text = str(response)
            query_time = (datetime.now() - start_time).total_seconds()
            
            # Log query and response manually
            if langfuse_available and langfuse_client:
                query_time = (datetime.now() - start_time).total_seconds()
                try:
                    # Use trace instead of log_event
                    trace = langfuse_client.trace(
                        name="query_response",
                        id=str(uuid.uuid4())
                    )
                    trace.update(
                        metadata={
                            "query": query,
                            "response": response_text,
                            "model": llm_model,
                            "response_time_seconds": query_time,
                            "similarity_threshold": similarity_threshold,
                            "sources_count": len(response.source_nodes) if hasattr(response, "source_nodes") else 0,
                            "session_id": st.session_state.session_id
                        }
                    )
                except Exception as e:
                    print(f"Error logging to Langfuse: {str(e)}")
            
            # Add assistant message to chat
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_text
            })
            
        except Exception as e:
            error_message = f"❌ Error: {str(e)}"
            
            # Log error
            if langfuse_available and langfuse_client:
                try:
                    # Use trace instead of log_event
                    trace = langfuse_client.trace(
                        name="query_error",
                        id=str(uuid.uuid4())
                    )
                    trace.update(
                        metadata={
                            "query": query,
                            "error": str(e),
                            "session_id": st.session_state.session_id
                        }
                    )
                except Exception as log_err:
                    print(f"Error logging to Langfuse: {str(log_err)}")
            
            # Add error message to chat
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_message
            })
    
    # Rerun to display the new messages
    st.rerun()

# Handle clear chat button
if 'clear_chat' in locals() and clear_chat:
    # Log event
    if langfuse_available and langfuse_client:
        try:
            # Use trace instead of log_event
            trace = langfuse_client.trace(
                name="clear_chat",
                id=str(uuid.uuid4())
            )
            trace.update(
                metadata={
                    "session_id": st.session_state.session_id
                }
            )
        except Exception as e:
            print(f"Error logging to Langfuse: {str(e)}")
    
    st.session_state.messages = []
    st.rerun()

# Handle reset index button
if 'reset_index' in locals() and reset_index:
    # Log event
    if langfuse_available and langfuse_client:
        try:
            # Use trace instead of log_event
            trace = langfuse_client.trace(
                name="reset_index",
                id=str(uuid.uuid4())
            )
            trace.update(
                metadata={
                    "session_id": st.session_state.session_id
                }
            )
        except Exception as e:
            print(f"Error logging to Langfuse: {str(e)}")
    
    st.session_state.index = None
    st.session_state.ready = False
    st.session_state.messages = []
    st.rerun()