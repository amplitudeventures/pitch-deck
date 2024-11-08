import streamlit as st
from dotenv import load_dotenv

# Must be the first Streamlit command
st.set_page_config(
    page_title="Pitch Deck Generator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS right after page config
st.markdown("""
    <style>
    /* Basic dark theme */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Text visibility */
    .stMarkdown, p, span, div, label {
        color: #fafafa;
    }
    
    /* Remove white boxes */
    .element-container {
        background-color: transparent;
        padding: 0;
        margin: 0;
    }
    
    /* Clean up sidebar */
    section[data-testid="stSidebar"] {
        background-color: #262730;
    }
    
    /* Keep buttons visible */
    .stButton button {
        width: 100%;
        margin: 0.5rem 0;
        background-color: #0066cc;
        color: white;
    }
    
    /* Remove white backgrounds from expanders */
    .stExpander {
        background-color: transparent;
        border: none;
    }
    </style>
""", unsafe_allow_html=True)

# Rest of your imports and code...

import os
from pathlib import Path
from project_state import ProjectState
import time
import re 
from vector_store import VectorStore
from datetime import datetime
import asyncio
from pathlib import Path
import PyPDF2
from dotenv import load_dotenv
import base64
from typing import Dict, List, Optional, Any
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io
from openai import OpenAI
import json
from messages import (PHASE_NAMES, PHASE_CONFIGS, SLIDE_TYPES, 
                     LANGUAGE_CONFIGS, EDITING_MODES, EXPORT_CONFIGS)
import jinja2

import sys
import traceback

import uuid


# First Streamlit command must be set_page_config

# Load environment variables
load_dotenv()


# Debug environment variables
# st.write("### Debugging Environment Variables")
# st.write(f"Current working directory: {Path('.env').absolute()}")
# st.write(f".env file exists: {Path('.env').exists()}")

# api_key = os.getenv('PINECONE_API_KEY')
# env = os.getenv('PINECONE_ENVIRONMENT')

# st.write("PINECONE_API_KEY:", "Set" if api_key else "Not Set")
# st.write("OPENAI_API_KEY:", "Set" if os.getenv('OPENAI_API_KEY') else "Not Set")
# st.write("PINECONE_ENVIRONMENT:", env if env else "Not Set")

# Rest of your imports

# ... rest of your code ...

class ProjectState:
    def __init__(self, project_id: str, vector_store: VectorStore):
        self.project_id = project_id
        self.vector_store = vector_store
        self.current_phase = 0
        self.current_language = "no"
        self.slides = {}
        self.phase_reports = {}
        self.feedback_history = {}
        self.html_preview = None
        self.pdf_generated = False
        
    def save_state(self) -> bool:
        """Store current state in vector store with improved error handling"""
        try:
            state_data = {
                'project_id': self.project_id,
                'current_phase': self.current_phase,
                'current_language': self.current_language,
                'slides': self.slides,
                'phase_reports': self.phase_reports,
                'feedback_history': self.feedback_history,
                'html_preview': self.html_preview,
                'pdf_generated': self.pdf_generated,
                'timestamp': datetime.now().isoformat()
            }
            
            # Convert state data to JSON string
            state_json = json.dumps(state_data)
            
            # Store in vector store
            success = self.vector_store.store_state(self.project_id, state_json)
            
            if not success:
                st.error("Failed to store project state in vector store")
                return False
            
            st.session_state.last_saved_state = state_data
            return True
            
        except Exception as e:
            st.error(f"Error saving state: {str(e)}")
            return False

    def load_state(self) -> bool:
        """Load state from vector store"""
        try:
            state_data = self.vector_store.get_project_state(self.project_id)
            
            if state_data:
                self.current_phase = state_data.get('current_phase', 0)
                self.current_language = state_data.get('current_language', 'no')
                self.slides = state_data.get('slides', {})
                self.phase_reports = state_data.get('phase_reports', {})
                self.feedback_history = state_data.get('feedback_history', {})
                self.html_preview = state_data.get('html_preview')
                self.pdf_generated = state_data.get('pdf_generated', False)
                return True
            
            return False
            
        except Exception as e:
            st.error(f"Error loading state: {str(e)}")
            return False

    def save_slide(self, slide_type: str, content: Dict) -> bool:
        """Save slide content"""
        try:
            self.slides[slide_type] = content
            return self.save_state()
        except Exception as e:
            st.error(f"Error saving slide: {str(e)}")
            return False

    def get_slide(self, slide_type: str) -> Optional[Dict]:
        """Get slide content"""
        return self.slides.get(slide_type)

    def add_feedback(self, slide_type: str, feedback: str) -> bool:
        """Add feedback for a slide"""
        try:
            if slide_type not in self.feedback_history:
                self.feedback_history[slide_type] = []
            
            self.feedback_history[slide_type].append({
                'feedback': feedback,
                'timestamp': datetime.now().isoformat()
            })
            
            return self.save_state()
        except Exception as e:
            st.error(f"Error adding feedback: {str(e)}")
            return False

    def save_phase_report(self, phase: int, report: Dict) -> bool:
        """Save phase completion report"""
        try:
            self.phase_reports[str(phase)] = {
                'report': report,
                'timestamp': datetime.now().isoformat()
            }
            return self.save_state()
        except Exception as e:
            st.error(f"Error saving phase report: {str(e)}")
            return False

    def update_slide(self, slide_type: str, edit_request: str, current_content: str) -> bool:
        """Update a specific slide based on edit request"""
        try:
            # Create message for AI
            message_content = f"""Please update this slide based on the following request:

Current Content:
{current_content}

Edit Request:
{edit_request}

Please maintain the same format and structure, but incorporate the requested changes."""

            # Send message to OpenAI
            message = st.session_state.openai_client.beta.threads.messages.create(
                thread_id=st.session_state.thread_id,
                role="user",
                content=message_content
            )
            
            run = st.session_state.openai_client.beta.threads.runs.create(
                thread_id=st.session_state.thread_id,
                assistant_id="asst_uCXB3ZuddxaZZeEqPh8LZ5Zf"
            )
            
            # Wait for completion with status updates
            with st.spinner("Updating slide..."):
                while run.status in ["queued", "in_progress"]:
                    time.sleep(1)
                    run = st.session_state.openai_client.beta.threads.runs.retrieve(
                        thread_id=st.session_state.thread_id,
                        run_id=run.id
                    )
            
            if run.status == "completed":
                messages = st.session_state.openai_client.beta.threads.messages.list(
                    thread_id=st.session_state.thread_id
                )
                response = messages.data[0].content[0].text.value
                
                # Update both raw response and parsed content
                st.session_state.raw_responses[slide_type] = response
                
                # Store in vector store
                success = st.session_state.vector_store.store_slide(
                    project_id=st.session_state.current_project_id,
                    slide_type=slide_type,
                    content=response
                )
                
                if success:
                    return True
            
            return False
            
        except Exception as e:
            st.error(f"Error updating slide: {str(e)}")
            return False

class PitchDeckGenerator:
    def __init__(self):
        """Initialize the application"""
        self.init_session_state()
        self.setup_openai_client()
        self.setup_vector_store()
        self.setup_templates()

    def log_api_call(self, action: str, details: str, error: bool = False):
        """Log API calls and important events with enhanced error checking"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            status = "❌" if error else "✅"
            log_entry = f"[{timestamp}] {status} {action}: {details}"
            
            # Initialize logger if it doesn't exist
            if 'logger' not in st.session_state:
                st.session_state.logger = []
            
            # Check for 'setIn' related errors
            if "setIn' cannot be called on an ElementNode" in str(details):
                error_context = """
                Error: Attempted to modify a Streamlit element after rendering.
                This usually happens when trying to update UI elements outside the normal flow.
                Solution: Move the modification before the element is rendered.
                """
                log_entry += f"\nContext: {error_context}"
                st.error(error_context)
            
            st.session_state.logger.append(log_entry)
            
            # Keep only last 100 entries
            if len(st.session_state.logger) > 100:
                st.session_state.logger = st.session_state.logger[-100:]
                
        except Exception as e:
            st.error(f"Logging failed: {str(e)}")

    def init_session_state(self):
        """Initialize all session state variables with error handling"""
        try:
            if 'initialized' not in st.session_state:
                st.session_state.initialized = False
                
            if not st.session_state.initialized:
                session_vars = {
                    'current_project_id': None,
                    'project_state': None,
                    'thread_id': None,
                    'files_uploaded': False,
                    'document_cache': {},
                    'logger': [],
                    'error_log': [],
                    'chat_history': [],
                    'should_rerun': False,
                    'editing_mode': 'structured',
                    'current_slide': None,
                    'preview_html': None,
                    'active_tab': "Documents",  # Initialize active_tab
                    'current_tab': 0,  # Initialize current_tab
                    'last_error': None,
                    'system_messages': []
                }
                
                for var, value in session_vars.items():
                    if var not in st.session_state:
                        st.session_state[var] = value
                
                st.session_state.initialized = True
                self.log_api_call("Initialization", "Session state initialized successfully")
                
        except Exception as e:
            self.log_error(e, "Session State Initialization")
            st.error("Failed to initialize session state. Please refresh the page.")

    def setup_openai_client(self):
        """Initialize OpenAI client"""
        try:
            if 'client' not in st.session_state:
                st.session_state.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                self.log_api_call("Initialization", "OpenAI client initialized")
        except Exception as e:
            self.log_api_call("Error", f"OpenAI client initialization failed: {str(e)}", error=True)
            raise

    def setup_vector_store(self):
        """Initialize vector store"""
        try:
            api_key = os.getenv('PINECONE_API_KEY')
            environment = "gcp-starter"
            
            if not api_key:
                st.error("Missing required environment variables")
                st.error("Please check your .env file for PINECONE_API_KEY")
                st.stop()
                
            if 'vector_store' not in st.session_state:
                st.session_state.vector_store = VectorStore(
                    api_key=api_key,
                    environment=environment,
                    log_function=self.log_api_call
                )
                self.log_api_call("Initialization", "Vector store initialized")
                
        except Exception as e:
            st.error(f"Failed to initialize vector store: {str(e)}")
            st.error("Please verify your Pinecone API key and environment settings")
            raise

    def setup_templates(self):
        """Initialize Jinja2 templates"""
        try:
            # Create templates directory if it doesn't exist
            templates_dir = Path('templates')
            templates_dir.mkdir(exist_ok=True)
            
            # Initialize Jinja2 environment
            self.template_env = jinja2.Environment(
                loader=jinja2.FileSystemLoader('templates'),
                autoescape=True
            )
            
            # Create default template if it doesn't exist
            default_template_path = templates_dir / 'pitch_deck.html'
            if not default_template_path.exists():
                default_template = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Pitch Deck</title>
                    <style>
                        body { font-family: Arial, sans-serif; }
                        .slide { margin: 20px; padding: 20px; border: 1px solid #ccc; }
                        .slide-title { font-size: 24px; margin-bottom: 15px; }
                        .slide-content { font-size: 16px; }
                    </style>
                </head>
                <body>
                    {% for slide_type, content in slides.items() %}
                    <div class="slide">
                        <div class="slide-title">{{ slide_type }}</div>
                        <div class="slide-content">
                            {% for key, value in content.items() %}
                            <p><strong>{{ key }}:</strong> {{ value }}</p>
                            {% endfor %}
                        </div>
                    </div>
                    {% endfor %}
                </body>
                </html>
                """
                with open(default_template_path, 'w') as f:
                    f.write(default_template)
            
            self.log_api_call("Initialization", "Templates initialized")
            
        except Exception as e:
            error_msg = f"Template initialization failed: {str(e)}"
            self.log_api_call("Error", error_msg, error=True)
            raise Exception(error_msg)

    def sidebar_content(self):
        """Display sidebar content and controls with error checking"""
        if not self.check_ui_modifications():
            return
        
        try:
            st.sidebar.title("Pitch Deck Generator")
            
            # Language selector
            st.sidebar.markdown("### Language")
            selected_language = st.sidebar.selectbox(
                "Select Language",
                options=list(LANGUAGE_CONFIGS.keys()),
                format_func=lambda x: LANGUAGE_CONFIGS[x]['name'],
                index=0 if self.current_language == "no" else 1
            )
            
            if selected_language != self.current_language:
                self.current_language = selected_language
                self.save_state()
                st.rerun()
            
            # Editing mode selector
            st.sidebar.markdown("### Editing Mode")
            editing_mode = st.sidebar.radio(
                "Select editing mode",
                options=list(EDITING_MODES.keys()),
                format_func=lambda x: EDITING_MODES[x]['name']
            )
            
            if editing_mode != self.editing_mode:
                self.editing_mode = editing_mode
                st.rerun()
            
            # Progress tracking
            if self.current_phase:
                st.sidebar.markdown("### Progress")
                progress = st.sidebar.progress(0)
                current_phase = self.current_phase
                total_phases = len(PHASE_NAMES)
                progress.progress(current_phase / total_phases)
                
                st.sidebar.markdown(f"**Current Phase:** {PHASE_NAMES[current_phase]}")
            
            # Console output
            self.display_console()
            
        except Exception as e:
            if "setIn' cannot be called on an ElementNode" in str(e):
                st.error("""
                UI Modification Error:
                Cannot modify elements after they're rendered.
                Please refresh the page and try again.
                """)
                self.log_error(e, "Sidebar Content - ElementNode Error")
            else:
                self.log_error(e, "Sidebar Content")

    def display_console(self):
        """Display console output with enhanced error detection"""
        try:
            if st.sidebar.checkbox("Show Console Output", value=False):
                st.sidebar.markdown("### Console Output")
                
                # Add error detection for ElementNode issues
                element_node_errors = [
                    log for log in st.session_state.get('logger', [])
                    if "setIn' cannot be called on an ElementNode" in log
                ]
                
                if element_node_errors:
                    st.sidebar.error("""
                    ElementNode Error Detected!
                    Common causes:
                    1. Modifying UI elements after they're rendered
                    2. Incorrect state management
                    3. Async operations affecting UI
                    
                    Try:
                    1. Moving state modifications earlier in the code
                    2. Using st.session_state for state management
                    3. Ensuring all UI updates happen in the main flow
                    """)
                
                # Add system info
                st.sidebar.markdown("#### System Information")
                st.sidebar.code(f"""
Python Version: {sys.version}
Streamlit Version: {st.__version__}
Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                """)
                
                # Add session state debug info
                st.sidebar.markdown("#### Session State")
                st.sidebar.code(f"""
Initialized: {st.session_state.get('initialized', False)}
Current Phase: {self.current_phase if hasattr(self, 'current_phase') else 'Not Set'}
Files Uploaded: {st.session_state.get('files_uploaded', False)}
Current Tab: {st.session_state.get('active_tab', 'Not Set')}
                """)
                
                # Add error log section
                st.sidebar.markdown("#### Error Log")
                if 'error_log' not in st.session_state:
                    st.session_state.error_log = []
                
                for error in st.session_state.error_log[-5:]:  # Show last 5 errors
                    st.sidebar.error(error)
                
                # Add general log section
                st.sidebar.markdown("#### General Log")
                if 'logger' in st.session_state and st.session_state.logger:
                    for log in reversed(st.session_state.logger[-10:]):  # Show last 10 entries
                        st.sidebar.text(log)
                else:
                    st.sidebar.text("No console output available")
                
        except Exception as e:
            self.log_error(e, "Console Display")

    def log_error(self, error: Exception, context: str = ""):
        """Enhanced error logging function"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_msg = f"""
[{timestamp}] ERROR in {context}
Type: {type(error).__name__}
Message: {str(error)}
Traceback:
{traceback.format_exc()}
Session State Keys: {list(st.session_state.keys())}
        """
        
        if 'error_log' not in st.session_state:
            st.session_state.error_log = []
        st.session_state.error_log.append(error_msg)
        
        # Also log to standard logger
        self.log_api_call("Error", error_msg, error=True)

    def display_html_preview(self):
        """Display HTML preview of the pitch deck"""
        if not self.slides:
            st.info("No slides to preview yet. Create some slides first!")
            return

        try:
            # Get the template
            template = self.template_env.get_template('pitch_deck.html')
            
            # Render the template with current slides
            html_content = template.render(
                slides=self.slides,
                language=self.current_language,
                configs={
                    'slides': SLIDE_TYPES,
                    'language': LANGUAGE_CONFIGS
                }
            )
            
            # Store the preview
            if self.vector_store.store_html_preview(
                self.current_project_id,
                html_content
            ):
                self.html_preview = html_content
                
                # Display preview
                st.components.v1.html(
                    html_content,
                    height=600,
                    scrolling=True
                )
                
                # Download button
                if st.download_button(
                    "Download HTML",
                    html_content,
                    file_name="pitch_deck_preview.html",
                    mime="text/html"
                ):
                    self.log_api_call("Export", "HTML preview downloaded")
                    
            else:
                st.error("Failed to generate preview")
                
        except Exception as e:
            st.error(f"Error generating preview: {str(e)}")
            self.log_api_call("Error", f"Preview generation failed: {str(e)}", error=True)

    # Add this helper method to check for UI modification issues
    def check_ui_modifications(self):
        """Check for potential UI modification issues"""
        try:
            if hasattr(st.session_state, '_is_rendering'):
                st.warning("""
                Potential UI modification during rendering detected.
                This might cause 'setIn' ElementNode errors.
                Please ensure all state modifications happen before rendering UI elements.
                """)
                return False
            return True
        except Exception as e:
            self.log_error(e, "UI Modification Check")
            return False

def handle_preview_tab():
    """Handle Preview tab content"""
    st.header("Preview Pitch Deck")
    
    if not st.session_state.project_state.slides:
        st.info("No slides to preview yet. Create some slides first!")
        return
        
    try:
        # Create simple HTML content with white text and proper encoding
        html_content = """
        <!DOCTYPE html>
        <html lang="no">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {
                    background-color: #0e1117;
                    color: white;
                    font-family: Arial, sans-serif;
                    padding: 20px;
                }
                .slide {
                    margin-bottom: 40px;
                    color: white;
                }
                .slide-title {
                    color: white;
                    font-size: 24px;
                    margin-bottom: 15px;
                    border-bottom: 1px solid #ffffff40;
                    padding-bottom: 10px;
                }
                .slide-content {
                    color: white;
                    font-size: 16px;
                    line-height: 1.5;
                    padding-left: 20px;
                }
                .bullet-point {
                    color: white;
                    margin-bottom: 8px;
                    padding-left: 15px;
                    position: relative;
                }
                .bullet-point:before {
                    content: "•";
                    position: absolute;
                    left: 0;
                    color: white;
                }
                .introduction-text {
                    color: white;
                    font-size: 16px;
                    line-height: 1.6;
                    padding-left: 20px;
                    margin-bottom: 20px;
                }
            </style>
        </head>
        <body>
        """
        
        # Add each slide's content
        for slide_type, slide_data in st.session_state.project_state.slides.items():
            slide_config = SLIDE_TYPES.get(slide_type, {})
            slide_name = slide_config.get('name', slide_type.title())
            
            html_content += f'<div class="slide"><div class="slide-title">{slide_name}</div>'
            
            if slide_type == 'introduction':
                # Special handling for introduction slide - paragraph format
                if slide_type in st.session_state.get('raw_responses', {}):
                    content = st.session_state.raw_responses[slide_type]
                    # Clean the content
                    content = content.replace('**', '').strip()
                    html_content += f'<div class="introduction-text">{content}</div>'
            else:
                # Regular bullet point format for other slides
                html_content += '<div class="slide-content">'
                if slide_type in st.session_state.get('raw_responses', {}):
                    content = st.session_state.raw_responses[slide_type]
                    for line in content.split('\n'):
                        if line.strip():
                            # Clean the line
                            line = line.replace('**', '').strip()
                            if line.startswith('- '):
                                line = line[2:]
                            html_content += f'<div class="bullet-point">{line}</div>'
                html_content += '</div>'
            
            html_content += '</div>'
        
        html_content += """
        </body>
        </html>
        """
        
        # Display preview
        st.components.v1.html(
            html_content,
            height=600,
            scrolling=True
        )
        
        # Add download button
        if st.download_button(
            "Download HTML",
            html_content.encode('utf-8'),
            file_name="pitch_deck.html",
            mime="text/html"
        ):
            st.success("HTML file downloaded successfully!")
            
    except Exception as e:
        st.error(f"Error generating preview: {str(e)}")

def handle_export_tab():
    """Handle Export tab content"""
    st.header("Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Export as PDF"):
            st.download_button(
                "Download PDF",
                data=b"PDF content here",  # Replace with actual PDF generation
                file_name="pitch_deck.pdf",
                mime="application/pdf"
            )
    
    with col2:
        if st.button("Export as HTML"):
            if st.session_state.project_state.html_preview:
                st.download_button(
                    "Download HTML",
                    st.session_state.project_state.html_preview,
                    file_name="pitch_deck.html",
                    mime="text/html"
                )

def load_css():
    st.markdown("""
        <style>
        /* Make background dark */
        .stApp {
            background-color: #0e1117;
        }
        
        /* Remove all white boxes and make text visible */
        .element-container, .stExpander, .stTextArea textarea {
            background-color: transparent !important;
            border: none !important;
            padding: 0 !important;
            margin: 0 !important;
            color: #fafafa !important;
        }
        
        /* Fix text visibility */
        .stMarkdown, p, span, div, label, .stText {
            color: #fafafa !important;
        }
        
        /* Keep buttons visible but clean */
        .stButton button {
            width: 100%;
            margin: 0.5rem 0;
            background-color: #0066cc;
            color: white;
        }

        /* Fix expander styling */
        .streamlit-expanderHeader {
            background-color: transparent !important;
            color: #fafafa !important;
            border: none !important;
        }
        
        /* Fix JSON display */
        .stJson {
            background-color: #262730 !important;
            border-radius: 4px;
            padding: 0.5rem !important;
        }

        /* Remove white backgrounds from success/info messages */
        .element-container div[data-testid="stMarkdownContainer"] {
            background-color: transparent !important;
        }
        </style>
    """, unsafe_allow_html=True)

def main():
    # Initialize session state first
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False
        
    # Project name input if not already set
    if 'current_project_id' not in st.session_state or not st.session_state.current_project_id:
        st.title("Welcome to Pitch Deck Generator")
        project_name = st.text_input("Enter your project name:")
        if project_name:
            st.session_state.current_project_id = str(uuid.uuid4())
            st.session_state.project_name = project_name
            st.session_state.initialized = False
            st.rerun()
        st.stop()

    # Load CSS after basic setup
    load_css()
    
    # Initialize all required session state variables
    if not st.session_state.initialized:
        # Initialize vector store first
        if 'vector_store' not in st.session_state:
            api_key = os.getenv('PINECONE_API_KEY')
            environment = "gcp-starter"
            # Define a proper log function that accepts error parameter
            def log_function(action: str, details: str, error: bool = False):
                if error:
                    st.error(f"{action}: {details}")
                else:
                    st.write(f"{action}: {details}")
                    
            st.session_state.vector_store = VectorStore(
                api_key=api_key,
                environment=environment,
                log_function=log_function
            )
        
        # Initialize project state
        if 'project_state' not in st.session_state:
            st.session_state.project_state = ProjectState(
                st.session_state.current_project_id,
                st.session_state.vector_store
            )
            # Try to load existing state
            st.session_state.project_state.load_state()
        
        session_vars = {
            'thread_id': None,
            'files_uploaded': False,
            'document_cache': {},
            'logger': [],
            'error_log': [],
            'chat_history': [],
            'should_rerun': False,
            'editing_mode': 'structured',
            'current_slide': None,
            'preview_html': None,
            'active_tab': "Documents",
            'current_tab': 0,
            'last_error': None,
            'system_messages': [],
            'current_language': st.session_state.project_state.current_language if hasattr(st.session_state.project_state, 'current_language') else 'no',
            'upload_state': {
                'files_processed': [],
                'processing_complete': False
            }
        }
        
        # Only set session vars if they don't exist
        for var, value in session_vars.items():
            if var not in st.session_state:
                st.session_state[var] = value
        
        st.session_state.initialized = True
    
    # Initialize the PitchDeckGenerator
    app = PitchDeckGenerator()
    
    # Sidebar content
    st.sidebar.title("Pitch Deck Generator")
    
    # Project info
    st.sidebar.markdown(f"### Project: {st.session_state.project_name}")
    
    # Language selector
    st.sidebar.markdown("### Language")
    selected_language = st.sidebar.selectbox(
        "Select Language",
        options=list(LANGUAGE_CONFIGS.keys()),
        format_func=lambda x: LANGUAGE_CONFIGS[x]['name'],
        index=list(LANGUAGE_CONFIGS.keys()).index(st.session_state.current_language)
    )
    
    if selected_language != st.session_state.current_language:
        st.session_state.current_language = selected_language
        st.session_state.project_state.current_language = selected_language
        st.session_state.project_state.save_state()
        st.rerun()
    
    # Editing mode selector
    st.sidebar.markdown("### Editing Mode")
    editing_mode = st.sidebar.radio(
        "Select editing mode",
        options=list(EDITING_MODES.keys()),
        format_func=lambda x: EDITING_MODES[x]['name']
    )
    
    if editing_mode != st.session_state.editing_mode:
        st.session_state.editing_mode = editing_mode
        st.rerun()
    
    # Progress tracking
    if st.session_state.project_state and hasattr(st.session_state.project_state, 'current_phase'):
        st.sidebar.markdown("### Progress")
        progress = st.sidebar.progress(0)
        current_phase = st.session_state.project_state.current_phase
        total_phases = len(PHASE_NAMES)
        progress.progress(current_phase / total_phases)
        st.sidebar.markdown(f"**Current Phase:** {PHASE_NAMES[current_phase]}")
    
    # Console output
    if st.sidebar.checkbox("Show Console Output", value=False):
        st.sidebar.markdown("### Console Output")
        if 'logger' in st.session_state and st.session_state.logger:
            for log in reversed(st.session_state.logger[-10:]):
                st.sidebar.text(log)
        else:
            st.sidebar.text("No console output available")
    
    # Navigation
    st.sidebar.markdown("### Navigation")
    selected_tab = st.sidebar.radio(
        "Select Section",
        ["Documents", "Slides", "Preview", "Export"],
        key="navigation",
        index=["Documents", "Slides", "Preview", "Export"].index(st.session_state.active_tab)
    )
    
    # Handle tab content based on selection
    if selected_tab == "Documents":
        handle_documents_tab()
    elif selected_tab == "Slides":
        handle_slides_tab()
    elif selected_tab == "Preview":
        handle_preview_tab()
    elif selected_tab == "Export":
        handle_export_tab()

def handle_documents_tab():
    """Handle Documents tab content"""
    st.header("Upload Documents")
    
    # Initialize upload state if needed
    if 'upload_state' not in st.session_state:
        st.session_state.upload_state = {
            'files_processed': [],
            'processing_complete': False
        }
    
    # Now we can safely access current_phase
    if not st.session_state.upload_state['processing_complete']:
        uploaded_files = st.file_uploader(
            "Upload company documents",
            accept_multiple_files=True,
            type=['txt', 'pdf', 'doc', 'docx'],
            key="document_uploader"
        )
        
        # Process files only if new ones are uploaded
        if uploaded_files:
            new_files = [f for f in uploaded_files if f.name not in st.session_state.upload_state['files_processed']]
            
            if new_files:
                progress_container = st.empty()
                with progress_container.container():
                    with st.spinner("Processing documents..."):
                        for file in new_files:
                            try:
                                if handle_document_upload(file):
                                    st.session_state.upload_state['files_processed'].append(file.name)
                                    st.success(f"✅ Processed: {file.name}")
                            except Exception as e:
                                st.error(f"❌ Error processing {file.name}: {str(e)}")
        
        # Display processed files
        if st.session_state.upload_state['files_processed']:
            st.success("🎉 Documents processed:")
            for file_name in st.session_state.upload_state['files_processed']:
                st.write(f"✅ {file_name}")
            
            if st.button("Complete Document Upload", type="primary"):
                st.session_state.upload_state['processing_complete'] = True
                st.session_state.project_state.current_phase = 1  # Set to Slide Planning phase
                st.session_state.project_state.save_state()
                st.success("Moving to Slides section...")
                st.session_state.active_tab = "Slides"
                st.rerun()
    else:
        # Show completed state
        st.success("🎉 Documents have been processed!")
        for file_name in st.session_state.upload_state['files_processed']:
            st.write(f"✅ {file_name}")
        
        if st.button("Upload More Documents"):
            st.session_state.upload_state['processing_complete'] = False
            st.rerun()

def handle_slides_tab():
    """Handle Slides tab content"""
    st.header("Create Your Pitch Deck")
    
    # Add debug information
    if st.checkbox("Show Debug Info"):
        st.write("Session State:", {
            k: v for k, v in st.session_state.items() 
            if k not in ['openai_client', 'vector_store']
        })
        st.write("Current Phase:", st.session_state.project_state.current_phase)
        st.write("Slides Present:", bool(st.session_state.project_state.slides))
    
    if not st.session_state.upload_state.get('processing_complete', False):
        st.info("Please complete the document analysis phase first.")
        if st.button("Go to Documents Section"):
            st.session_state.active_tab = "Documents"
            st.rerun()
        return
    
    # Add phase tracking
    current_phase = st.session_state.project_state.current_phase
    if current_phase < 2:  # Content Generation phase
        st.session_state.project_state.current_phase = 2
        st.session_state.project_state.save_state()
    
    # Initialize OpenAI client if not already done
    if 'openai_client' not in st.session_state:
        st.session_state.openai_client = OpenAI()
    
    # Generate initial slide content if not already done
    if not st.session_state.project_state.slides:
        with st.spinner("🤖 AI is analyzing your documents and generating pitch deck content..."):
            try:
                # Create thread if needed
                if not st.session_state.get('thread_id'):
                    thread = st.session_state.openai_client.beta.threads.create()
                    st.session_state.thread_id = thread.id
                
                # Get documents
                docs = st.session_state.vector_store.get_documents(st.session_state.current_project_id)
                if not docs:
                    st.warning("No documents found. Please upload documents first.")
                    return
                
                doc_content = "\n\n".join([doc['content'] for doc in docs if 'content' in doc])
                
                # Generate slides one by one
                progress_bar = st.progress(0)
                for idx, (slide_type, slide_config) in enumerate(SLIDE_TYPES.items()):
                    progress_bar.progress((idx / len(SLIDE_TYPES)))
                    st.write(f"Generating {slide_config['name']}...")
                    
                    # Create message for specific slide
                    message_content = f"""Based on these company documents, create the {slide_config['name']} slide:

Company Documents:
{doc_content}

Required elements: {', '.join(slide_config['required_elements'])}
Character limit: {slide_config['character_limit']}

Please follow these rules:
1. Include all required elements
2. Stay within character limit
3. Use bullet points under 13 words
4. Make content specific to this company
5. Follow professional tone guidelines"""

                    # Send message and run assistant
                    st.session_state.openai_client.beta.threads.messages.create(
                        thread_id=st.session_state.thread_id,
                        role="user",
                        content=message_content
                    )
                    
                    run = st.session_state.openai_client.beta.threads.runs.create(
                        thread_id=st.session_state.thread_id,
                        assistant_id="asst_uCXB3ZuddxaZZeEqPh8LZ5Zf"
                    )
                    
                    # Wait for completion
                    while run.status in ["queued", "in_progress"]:
                        time.sleep(1)
                        run = st.session_state.openai_client.beta.threads.runs.retrieve(
                            thread_id=st.session_state.thread_id,
                            run_id=run.id
                        )
                    
                    if run.status == "completed":
                        messages = st.session_state.openai_client.beta.threads.messages.list(
                            thread_id=st.session_state.thread_id
                        )
                        response = messages.data[0].content[0].text.value
                        
                        # Pass slide_type to parse_slide_response
                        slide_content = parse_slide_response(response, slide_type)
                        success = st.session_state.project_state.save_slide(slide_type, slide_content)
                        
                        if not success:
                            st.error(f"Failed to save {slide_config['name']}")
                            return
                    else:
                        st.error(f"Failed to generate {slide_config['name']}")
                        return
                
                progress_bar.progress(1.0)
                st.success("✨ All slides generated successfully!")
                st.rerun()
                    
            except Exception as e:
                st.error(f"Error generating slides: {str(e)}")
    else:
        # Display slides UI
        st.write("### Pitch Deck Slides")
        for slide_type, content in st.session_state.project_state.slides.items():
            display_slide_content(slide_type, content)

def parse_slide_response(response: str, slide_type: str) -> dict:
    """Parse the AI's rich response into structured slide content"""
    try:
        # Create a unique ID for this parsing session
        parse_id = f"{slide_type}_{int(time.time())}"  # Add time import if needed
        
        slide_content = {
            "sections": {},
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "references": [],
                "metrics": [],
                "sources": set()
            }
        }
        
        current_section = None
        
        for line in response.split('\n'):
            try:
                line = line.strip()
                if not line:
                    continue
                    
                # Extract references
                if '【' in line:
                    refs = re.findall(r'【([^】]+)】', line)
                    for ref in refs:
                        slide_content["metadata"]["sources"].add(ref)
                        
                # Extract metrics
                if any(char.isdigit() for char in line):
                    metrics = re.findall(r'(\d[\d,.-]*\s*(?:million|k|NOK|%|users|songs))', line)
                    if metrics:
                        slide_content["metadata"]["metrics"].extend(metrics)
                
                # Process section headers
                if line.startswith('###'):
                    parts = line.replace('### ', '').split('. ', 1)
                    if len(parts) == 2 and parts[0].isdigit():
                        number, title = parts
                        current_section = title.strip()
                        slide_content["sections"][current_section] = {
                            "order": int(number),
                            "content": [],
                            "references": []
                        }
                
                # Process bullet points
                elif line.startswith('-'):
                    if current_section:
                        bullet = line[1:].strip()
                        if '**' in bullet:
                            # Structured bullet with header
                            header_end = bullet.find('**:', 2)
                            if header_end != -1:
                                header = bullet[2:header_end].strip()
                                content = bullet[header_end+3:].strip()
                                slide_content["sections"][current_section]["content"].append({
                                    "type": "structured",
                                    "header": header,
                                    "content": content
                                })
                        else:
                            # Simple bullet
                            slide_content["sections"][current_section]["content"].append({
                                "type": "simple",
                                "content": bullet
                            })
                            
            except Exception as line_error:
                st.warning(f"Skipped line due to error: {line}", key=f"warning_{parse_id}")
                continue
        
        # Convert sources set to list for JSON serialization
        slide_content["metadata"]["sources"] = list(slide_content["metadata"]["sources"])
        
        # Debug output with truly unique key
        if st.checkbox("Show Parser Debug", key=f"debug_checkbox_{parse_id}"):
            st.write(f"Raw Response for {slide_type}:", response, key=f"raw_{parse_id}")
            st.write(f"Parsed Content for {slide_type}:", slide_content, key=f"parsed_{parse_id}")
        
        return slide_content
        
    except Exception as e:
        st.error(f"Error parsing slide response: {str(e)}", key=f"error_{parse_id}")
        return {}

def display_slide_content(slide_type: str, content: str):
    """Display slide content with edit functionality"""
    slide_config = SLIDE_TYPES.get(slide_type, {})
    
    # Display slide title and content
    st.subheader(slide_config.get('name', slide_type.title()))
    
    # Get the raw response text from session state
    if slide_type in st.session_state.get('raw_responses', {}):
        slide_text = st.session_state.raw_responses[slide_type]
        st.markdown(slide_text)
    else:
        st.markdown(content)
    
    # Initialize edit state for this slide if not exists
    if f"editing_{slide_type}" not in st.session_state:
        st.session_state[f"editing_{slide_type}"] = False
    
    # Add edit button or show edit interface
    if not st.session_state[f"editing_{slide_type}"]:
        if st.button("✏️ Edit", key=f"edit_btn_{slide_type}"):
            st.session_state[f"editing_{slide_type}"] = True
            st.rerun()
    else:
        edit_request = st.text_area(
            "What changes would you like to make?",
            key=f"edit_{slide_type}"
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Cancel", key=f"cancel_{slide_type}"):
                st.session_state[f"editing_{slide_type}"] = False
                st.rerun()
        with col2:
            if st.button("Update", key=f"update_{slide_type}"):
                if edit_request:
                    try:
                        success = st.session_state.project_state.update_slide(
                            slide_type=slide_type,
                            edit_request=edit_request,
                            current_content=st.session_state.raw_responses[slide_type]
                        )
                        if success:
                            st.session_state[f"editing_{slide_type}"] = False
                            st.success("✨ Updated!")
                            st.rerun()
                        else:
                            st.error("Update failed. Please try again.")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

def handle_document_upload(uploaded_file):
    """Handle document upload with proper tracking"""
    try:
        content = st.session_state.vector_store._extract_content(uploaded_file)
        if not content:
            st.error(f"Failed to extract content from {uploaded_file.name}")
            return False
            
        # Prepare metadata
        metadata = {
            'filename': uploaded_file.name,
            'file_type': uploaded_file.type,
            'upload_time': datetime.now().isoformat()
        }
        
        # Store document with tracking
        success = st.session_state.vector_store.store_document(
            project_id=st.session_state.current_project_id,
            content=content,
            metadata=metadata
        )
        
        if success:
            st.success(f"Successfully uploaded {uploaded_file.name}")
            return True
        else:
            st.error(f"Failed to store {uploaded_file.name}")
            return False
            
    except Exception as e:
        st.error(f"Error processing upload: {str(e)}")
        return False

def verify_project_state():
    """Verify and recover project state if needed"""
    try:
        if not hasattr(st.session_state.project_state, 'slides'):
            st.session_state.project_state.slides = {}
        
        if not hasattr(st.session_state.project_state, 'current_phase'):
            st.session_state.project_state.current_phase = 0
        
        # Verify each required slide type exists
        for slide_type in SLIDE_TYPES.keys():
            if slide_type not in st.session_state.project_state.slides:
                st.session_state.project_state.slides[slide_type] = {}
        
        st.session_state.project_state.save_state()
        return True
    except Exception as e:
        st.error(f"Failed to verify project state: {str(e)}")
        return False

# Call this at the start of handle_slides_tab
def handle_slides_tab():
    """Handle Slides tab content"""
    st.header("Create Your Pitch Deck")
    
    # Add debug information
    if st.checkbox("Show Debug Info"):
        st.write("Session State:", {
            k: v for k, v in st.session_state.items() 
            if k not in ['openai_client', 'vector_store']
        })
        st.write("Current Phase:", st.session_state.project_state.current_phase)
        st.write("Slides Present:", bool(st.session_state.project_state.slides))
    
    if not st.session_state.upload_state.get('processing_complete', False):
        st.info("Please complete the document analysis phase first.")
        if st.button("Go to Documents Section"):
            st.session_state.active_tab = "Documents"
            st.rerun()
        return

    # Add slide selection interface if not already done
    if 'selected_slides' not in st.session_state:
        st.subheader("Select Slides to Include")
        
        # Required slides (always checked and disabled)
        st.markdown("#### Required Slides")
        required_slides = {
            "title": "Title Slide",
            "introduction": "Introduction",
            "problem": "Problem Statement",
            "solution": "Solution",
            "market": "Market Opportunity",
            "ask": "Ask",
        }
        for slide_type, slide_name in required_slides.items():
            st.checkbox(slide_name, value=True, disabled=True, key=f"req_{slide_type}")
        
        # Optional slides
        st.markdown("#### Optional Slides")
        optional_slides = {
            "team": "Meet the Team",
            "experience": "Our Experience with the Problem",
            "revenue": "Revenue Model",
            "go_to_market": "Go-To-Market Strategy",
            "demo": "Demo",
            "technology": "Technology",
            "pipeline": "Product Development Pipeline",
            "expansion": "Product Expansion",
            "uniqueness": "Uniqueness & Protectability",
            "competition": "Competitive Landscape",
            "traction": "Traction & Milestones",
            "financials": "Financial Overview",
            "use_of_funds": "Use of Funds"
        }
        
        selected_optional = {}
        col1, col2 = st.columns(2)
        
        # Split optional slides between two columns
        half = len(optional_slides) // 2
        for idx, (slide_type, slide_name) in enumerate(optional_slides.items()):
            with col1 if idx < half else col2:
                selected_optional[slide_type] = st.checkbox(slide_name, value=False, key=f"opt_{slide_type}")
        
        # Confirm selection button
        if st.button("Confirm Slide Selection"):
            # Combine required and selected optional slides
            st.session_state.selected_slides = {
                **{k: True for k in required_slides.keys()},
                **selected_optional
            }
            st.rerun()
        return
    
    # Add phase tracking
    current_phase = st.session_state.project_state.current_phase
    if current_phase < 2:  # Content Generation phase
        st.session_state.project_state.current_phase = 2
        st.session_state.project_state.save_state()
    
    # Initialize OpenAI client if not already done
    if 'openai_client' not in st.session_state:
        st.session_state.openai_client = OpenAI()
    
    # Generate initial slide content if not already done
    if not st.session_state.project_state.slides:
        with st.spinner("🤖 AI is analyzing your documents and generating pitch deck content..."):
            try:
                # Create thread if needed
                if not st.session_state.get('thread_id'):
                    thread = st.session_state.openai_client.beta.threads.create()
                    st.session_state.thread_id = thread.id
                
                # Get documents
                docs = st.session_state.vector_store.get_documents(st.session_state.current_project_id)
                if not docs:
                    st.warning("No documents found. Please upload documents first.")
                    return
                
                doc_content = "\n\n".join([doc['content'] for doc in docs if 'content' in doc])
                
                # Generate slides one by one
                progress_bar = st.progress(0)
                slide_containers = {}
                
                # Only create containers for selected slides
                selected_slide_types = {k: v for k, v in SLIDE_TYPES.items() 
                                     if k in st.session_state.selected_slides and 
                                     st.session_state.selected_slides[k]}
                
                for slide_type, slide_config in selected_slide_types.items():
                    st.subheader(f"{slide_config['name']}")
                    slide_containers[slide_type] = st.empty()  # Create placeholder for each slide
                
                for idx, (slide_type, slide_config) in enumerate(selected_slide_types.items()):
                    progress_bar.progress((idx / len(selected_slide_types)))
                    
                    # Update status in the slide's container
                    slide_containers[slide_type].info(f"Generating {slide_config['name']}...")
                    
                    # Simply send the document content and slide type
                    message_content = f"""Please create the {slide_config['name']} slide based on the provided company documents:

{doc_content}"""
                    
                    # Send message and run assistant
                    st.session_state.openai_client.beta.threads.messages.create(
                        thread_id=st.session_state.thread_id,
                        role="user",
                        content=message_content
                    )
                    
                    run = st.session_state.openai_client.beta.threads.runs.create(
                        thread_id=st.session_state.thread_id,
                        assistant_id="asst_uCXB3ZuddxaZZeEqPh8LZ5Zf"
                    )
                    
                    # Wait for completion while showing status
                    while run.status in ["queued", "in_progress"]:
                        slide_containers[slide_type].info(f"Generating {slide_config['name']}... Status: {run.status}")
                        time.sleep(1)
                        run = st.session_state.openai_client.beta.threads.runs.retrieve(
                            thread_id=st.session_state.thread_id,
                            run_id=run.id
                        )
                    
                    if run.status == "completed":
                        messages = st.session_state.openai_client.beta.threads.messages.list(
                            thread_id=st.session_state.thread_id
                        )
                        response = messages.data[0].content[0].text.value
                        
                        # Store the raw response in session state for persistence
                        if 'raw_responses' not in st.session_state:
                            st.session_state.raw_responses = {}
                        st.session_state.raw_responses[slide_type] = response
                        
                        # Show the raw response
                        slide_containers[slide_type].markdown(f"""
                        **Generated Content:**
                        ```
                        {response}
                        ```
                        """)
                        
                        # Parse and save in background
                        slide_content = parse_slide_response(response, slide_type)
                        success = st.session_state.project_state.save_slide(slide_type, slide_content)
                        
                        if not success:
                            st.error(f"Failed to save {slide_config['name']}")
                            return
                    else:
                        slide_containers[slide_type].error(f"Failed to generate {slide_config['name']}")
                        return
                
                progress_bar.progress(1.0)
                st.success("✨ All slides generated successfully!")
                    
            except Exception as e:
                st.error(f"Error generating slides: {str(e)}")
    else:
        # Display slides UI
        st.write("### Your Pitch Deck Slides")
        for slide_type, content in st.session_state.project_state.slides.items():
            if slide_type in st.session_state.selected_slides and st.session_state.selected_slides[slide_type]:
                display_slide_content(slide_type, content)
    
    # Add option to modify slide selection
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Modify Slide Selection"):
            del st.session_state.selected_slides
            if 'project_state' in st.session_state:
                st.session_state.project_state.slides = {}
            st.rerun()
    
    with col2:
        if st.button("Go to Preview"):
            st.session_state.active_tab = "Preview"
            st.rerun()

# Move this to the very end of the file, with no indentation
if __name__ == "__main__":
    main()

