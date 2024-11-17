import random

import requests
import streamlit as st
import pdfkit
from googleapiclient.http import MediaIoBaseDownload

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from io import BytesIO

from google.oauth2 import service_account
from googleapiclient.discovery import build
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
    /* General app styling */
    .stApp {
        background-color: #1e1e1e !important;
        color: #e0e0e0 !important;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #2e2e2e !important;
        border-right: 1px solid #444 !important;
    }

    /* Header styling */
    header {
        background-color: #1e1e1e !important;
        color: #e0e0e0 !important;
    }

    /* Input fields styling */
    input, textarea, select, .stTextInput > div > div, .stTextArea > div > div, .stSelectbox > div > div {
        background-color: #3e3e3e !important;
        color: #e0e0e0 !important;
        border-color: #555 !important;
    }

    /* Dropdown menu styling */
    .stSelectbox div[data-baseweb="select"] {
        background-color: #3e3e3e !important;
    }
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #3e3e3e !important;
    }
    .stSelectbox div[data-baseweb="select"] .css-1wa3eu0-placeholder {
        color: red !important;
    }
    .stSelectbox div[data-baseweb="select"] .css-1uccc91-singleValue {
        color: red !important;
    }

    /* Force dropdown options to have a dark background and red text */
    .stSelectbox div[data-baseweb="select"] .css-1n7v3ny-option {
        background-color: #3e3e3e !important;
        color: red !important;
    }
    .stSelectbox div[data-baseweb="select"] .css-1n7v3ny-option:hover {
        background-color: #555 !important;
    }

    /* Dropdown menu panel */
    .stSelectbox div[data-baseweb="select"] .css-1pahdxg-control {
        background-color: #3e3e3e !important;
        color: red !important;
    }

    /* Additional targeting for dropdown text */
    .stSelectbox div[data-baseweb="select"] .css-1okebmr-indicatorContainer {
        color: red !important;
    }
    .stSelectbox div[data-baseweb="select"] .css-1hb7zxy-IndicatorsContainer {
        color: red !important;
    }

    /* Button styling */
    .stButton button {
        background-color: #007acc !important;
        color: white !important;
        border: none !important;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        border-color: #555 !important;
    }

    /* Success/Info/Error message styling */
    .stSuccess, .stInfo, .stWarning, .stError {
        background-color: #3e3e3e !important;
        color: #e0e0e0 !important;
        border: 1px solid #555 !important;
    }

    /* Code blocks */
    .stCodeBlock {
        background-color: #2e2e2e !important;
    }

    /* Table styling */
    .stTable {
        background-color: #2e2e2e !important;
        color: #e0e0e0 !important;
    }

    /* Ensure all text is visible */
    p, span, div, h1, h2, h3, h4, h5, h6, li, label {
        color: #e0e0e0 !important;
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
from messages import (PHASE_NAMES, PHASE_CONFIGS, SLIDE_TYPES_ENGLISH, SLIDE_TYPES_NORWEGIAN,
                      LANGUAGE_CONFIGS, EDITING_MODES, EXPORT_CONFIGS)
import jinja2

import sys
import traceback

import uuid

# First Streamlit command must be set_page_config

# Load environment variables
load_dotenv()


from fastapi import FastAPI

app = FastAPI()




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
            # Determine language for message content
            selected_language = st.session_state.project_state.current_language

            if selected_language == "no":
                # Norwegian prompt
                message_content = f"""Vennligst oppdater denne lysbilden basert på følgende forespørsel:

    Nåværende Innhold:
    {current_content}

    Redigeringsforespørsel:
    {edit_request}

    Vennligst behold samme format og struktur, men innlem de ønskede endringene."""
            else:
                # English prompt (default)
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
                    'slides': SLIDE_TYPES_ENGLISH,
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
                col1, col2, col3 = st.columns(3)

                with col1:
                    if st.button("Export as PDF"):
                        pdf_buffer = generate_pdf_from_text(st.session_state.project_state.slides)
                        st.download_button(
                            "Download PDF",
                            data=pdf_buffer,
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

                with col3:
                    if st.button("Export to Google Slides"):
                        # Trigger the Google Slides export function
                        export_to_google_slides(st.session_state.project_state.slides)
                        st.success("Pitch deck exported to Google Slides successfully!")
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
        selected_slide_types = {
            k: v for k, v in (
                SLIDE_TYPES_NORWEGIAN if st.session_state.current_language == 'no' else SLIDE_TYPES_ENGLISH).items()
            if k in st.session_state.selected_slides and st.session_state.selected_slides[k]
        }
        # Add each slide's content
        for slide_type, slide_data in st.session_state.project_state.slides.items():
            slide_config = selected_slide_types.get(slide_type, {})
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

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("Export as PDF"):
                pdf_buffer = generate_pdf_from_text(st.session_state.project_state.slides)
                st.download_button(
                    "Download PDF",
                    data=pdf_buffer,
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

        with col3:
            if st.button("Export to Google Slides"):
                # Trigger the Google Slides export function
                export_to_google_slides(st.session_state.project_state.slides)
                st.success("Pitch deck exported to Google Slides successfully!")
            st.success("HTML file downloaded successfully!")

    except Exception as e:
        st.error(f"Error generating preview: {str(e)}")


def draw_text_paragraph(c, text, y_position, x_position, max_width, font="Helvetica", font_size=10, line_height=14):
    """
    Draws a text paragraph within specified width, handling line wrapping.
    Returns the updated y_position after drawing the text.
    """
    c.setFont(font, font_size)
    words = text.split()
    line = ""

    for word in words:
        # Check if adding the next word would exceed max width
        if stringWidth(line + word, font, font_size) <= max_width:
            line += f"{word} "
        else:
            # Draw the current line and reset
            c.drawString(x_position, y_position, line.strip())
            y_position -= line_height
            line = f"{word} "

    # Draw the last line if there is any leftover text
    if line:
        c.drawString(x_position, y_position, line.strip())
        y_position -= line_height

    return y_position


def generate_pdf_from_text(slides):
    """Generate a PDF document from text content, with each slide on a new page and adjusted formatting."""
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    width, height = A4
    margin = 60  # Increased margin for better readability
    y_position_start = height - margin

    # Set default font sizes
    title_font_size = 20  # Smaller but still prominent
    text_font_size = 10  # Smaller for body text
    line_height = 14  # Adjusted line height for readability

    first_page = True  # Track if it's the first page



    # Now access current_language from the instance
    selected_language = st.session_state.project_state.current_language
    bullet_symbol = "•" if selected_language == "en" else "-"  # Choose bullet symbol based on language

    # Loop through slides and add content
    for slide_type, slide_data in slides.items():
        if not first_page:
            c.showPage()  # Start each slide on a new page
        else:
            first_page = False  # Skip creating a new page for the first slide
        y_position = y_position_start

        # Retrieve slide configurations and title based on language
        slide_config = SLIDE_TYPES_ENGLISH.get(slide_type, {})
        slide_name = slide_config.get('name', slide_type.title())

        # Language-specific titles (if needed)
        if selected_language == "Norwegian":
            if slide_type == "introduction":
                slide_name = "Introduksjon"
            # Add other language-based title mappings here as needed

        # Draw slide title
        c.setFont("Helvetica-Bold", title_font_size)
        c.drawString(margin, y_position, slide_name)
        y_position -= title_font_size + 12  # Space after title

        # Language-specific content processing
        if slide_type == 'introduction':
            # Introduction slide with paragraph format
            content = st.session_state.raw_responses.get(slide_type, '').replace('**', '').strip()
            y_position = draw_text_paragraph(
                c, content, y_position, margin, width - 2 * margin,
                font="Helvetica", font_size=text_font_size, line_height=line_height
            )
        else:
            # Bullet point format for other slides
            content = st.session_state.raw_responses.get(slide_type, '')
            for line in content.split('\n'):
                if line.strip():
                    line = line.replace('**', '').strip()
                    if line.startswith('- '):
                        line = line[2:]

                    # Adjust x position and max width for bullet points
                    bullet_indent = margin + 10
                    bullet_width = width - 2 * margin - 20
                    c.setFont("Helvetica", text_font_size)
                    y_position = draw_text_paragraph(
                        c, f"{bullet_symbol} {line}", y_position, bullet_indent, bullet_width,
                        font="Helvetica", font_size=text_font_size, line_height=line_height
                    )

        y_position -= 30  # Space between slides

        # Ensure we avoid overflow by creating a new page if needed
        if y_position < margin:
            c.showPage()
            y_position = y_position_start

    c.save()
    pdf_buffer.seek(0)
    return pdf_buffer

def handle_export_tab():
    """Handle Export tab content with additional Google Slides export option."""
    st.header("Export Options")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Export as PDF"):
            pdf_buffer = generate_pdf_from_text(st.session_state.project_state.slides)
            st.download_button(
                "Download PDF",
                data=pdf_buffer,
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

    with col3:
        if st.button("Export to Google Slides"):
            # Trigger the Google Slides export function
            export_to_google_slides(st.session_state.project_state.slides)
            st.success("Pitch deck exported to Google Slides successfully!")


def load_css():
    st.markdown("""
    <style>
        /* Apply red color to all text elements */
          div   {
            color: red !important;
        }
        
    </style>
    """, unsafe_allow_html=True)




from urllib.parse import quote
def extract_keywords(text, max_words=3):
    # Use a simple regex to extract words longer than 3 characters, which are likely to be more descriptive
    words = re.findall(r'\b\w{4,}\b', text)
    # Limit the number of keywords to avoid overly long URLs
    keywords = ' '.join(words[:max_words])
    return keywords



def generate_image_url(title, body):
    # Refine search for high-quality, dark-themed images with sharp resolution
    combined_keywords = f"{extract_keywords(title)} {extract_keywords(body)} dark moody night high resolution sharp clear".strip()

    headers = {
        "Authorization": "Pp6TvyGBYUcRlpWzdShoAExfMntaCj1UA1UQuz0vz5mYQHViak60S2ub"  # Replace with your Pexels API key
    }

    response = requests.get(f"https://api.pexels.com/v1/search?query={combined_keywords}&per_page=1", headers=headers)

    if response.status_code == 200 and response.json().get('photos'):
        # Choose 'large' for better quality without being too large
        return response.json()['photos'][0]['src']['large']  # 'large' is a good compromise between quality and size

    # Fallback to a default image if no result is found
    return "https://www.example.com/default-dark-image.jpg"  # Replace with your fallback image URL


# Use this in your Google Slides export function

def export_to_google_slides(slides):
    # Authenticate and initialize the Google Slides API service with necessary scopes
    creds = service_account.Credentials.from_service_account_file(
        "psychic-trainer-378112-7d76d802092f.json",
        scopes=["https://www.googleapis.com/auth/presentations", "https://www.googleapis.com/auth/drive"]
    )
    slides_service = build("slides", "v1", credentials=creds)

    # Create a new presentation
    presentation = slides_service.presentations().create(body={"title": st.session_state.project_name}).execute()
    presentation_id = presentation.get("presentationId")
    print(f"Created presentation with ID: {presentation_id}")

    # Format slides for Google Slides
    for slide_type, slide_data in slides.items():
        slide_content = st.session_state.raw_responses.get(slide_type, "")
        print(f"Slide Type: {slide_type}, Content: {slide_content}")

        # Step 1: Create a new slide with TITLE_AND_BODY layout
        create_slide_response = slides_service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={
                "requests": [
                    {
                        "createSlide": {
                            "slideLayoutReference": {"predefinedLayout": "TITLE_AND_BODY"}
                        }
                    }
                ]
            }
        ).execute()
        print("Create Slide Response:", json.dumps(create_slide_response, indent=2))

        # Retrieve the page ID of the newly created slide
        page_id = create_slide_response['replies'][0]['createSlide']['objectId']
        print(f"Created slide with page ID: {page_id}")

        title_text = slide_data.get('title', slide_type.title())
        image_url = generate_image_url(title_text, slide_content)

        # Step 2: Set the image as the slide background
        if image_url:
            slides_service.presentations().batchUpdate(
                presentationId=presentation_id,
                body={
                    "requests": [
                        {
                            "updatePageProperties": {
                                "objectId": page_id,
                                "pageProperties": {
                                    "pageBackgroundFill": {
                                        "stretchedPictureFill": {
                                            "contentUrl": image_url
                                        }
                                    }
                                },
                                "fields": "pageBackgroundFill"
                            }
                        }
                    ]
                }
            ).execute()

        # Step 3: Retrieve placeholders for title and body text boxes
        slide = slides_service.presentations().pages().get(
            presentationId=presentation_id,
            pageObjectId=page_id
        ).execute()
        print("Slide Structure:", json.dumps(slide, indent=2))

        title_id, body_id = None, None
        for element in slide.get('pageElements', []):
            element_id = element.get('objectId', '')
            placeholder_info = element.get('shape', {}).get('placeholder', {})
            placeholder_type = placeholder_info.get('type', '')

            if placeholder_type == "TITLE":
                title_id = element_id
            elif placeholder_type == "BODY":
                body_id = element_id

        # Step 4: Insert text into placeholders and update text color
        requests = []
        if title_id:
            # Insert title text
            requests.append({
                "insertText": {
                    "objectId": title_id,
                    "text": title_text
                }
            })
            # Set title text color to white
            requests.append({
                "updateTextStyle": {
                    "objectId": title_id,
                    "style": {
                        "foregroundColor": {
                            "opaqueColor": {
                                "rgbColor": {"red": 1.0, "green": 1.0, "blue": 1.0}
                            }
                        }
                    },
                    "textRange": {"type": "ALL"},
                    "fields": "foregroundColor"
                }
            })

        if body_id:
            # Insert body text
            requests.append({
                "insertText": {
                    "objectId": body_id,
                    "text": slide_content
                }
            })
            # Set body text color to white
            requests.append({
                "updateTextStyle": {
                    "objectId": body_id,
                    "style": {
                        "foregroundColor": {
                            "opaqueColor": {
                                "rgbColor": {"red": 1.0, "green": 1.0, "blue": 1.0}
                            }
                        }
                    },
                    "textRange": {"type": "ALL"},
                    "fields": "foregroundColor"
                }
            })

        # Execute the batch update to insert text and apply white color styling
        if requests:
            slides_service.presentations().batchUpdate(
                presentationId=presentation_id,
                body={"requests": requests}
            ).execute()

    st.write(f"Exported to Google Slides: {presentation_id}")


    drive_service = build('drive', 'v3', credentials=creds)


    file_format = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'  # PowerPoint (.pptx)
    request = drive_service.files().export_media(
        fileId=presentation_id,
        mimeType=file_format
    )


    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"Download progress: {int(status.progress() * 100)}%")
    fh.seek(0)


    st.download_button(
        label="Download Pitch Deck (PowerPoint)",
        data=fh,
        file_name=f"{st.session_state.project_name}_pitch_deck.pptx",
        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )




def main():

    if 'initialized' not in st.session_state:
        st.session_state.initialized = False


    if 'current_project_id' not in st.session_state or not st.session_state.current_project_id:
        st.title("Welcome to Pitch Deck Generator")
        project_name = st.text_input("Enter your project name:")
        if project_name:
            st.session_state.current_project_id = str(uuid.uuid4())
            st.session_state.project_name = project_name
            st.session_state.initialized = False
            st.rerun()
        st.stop()

    load_css()


    if not st.session_state.initialized:

        if 'vector_store' not in st.session_state:
            api_key = os.getenv('PINECONE_API_KEY')
            environment = "gcp-starter"


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


        if 'project_state' not in st.session_state:
            st.session_state.project_state = ProjectState(
                st.session_state.current_project_id,
                st.session_state.vector_store
            )

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
            'current_language': st.session_state.project_state.current_language if hasattr(
                st.session_state.project_state, 'current_language') else 'no',
            'upload_state': {
                'files_processed': [],
                'processing_complete': False
            }
        }


        for var, value in session_vars.items():
            if var not in st.session_state:
                st.session_state[var] = value

        st.session_state.initialized = True


    app = PitchDeckGenerator()






    st.sidebar.title("Pitch Deck Generator")


    st.sidebar.markdown(f"### Project: {st.session_state.project_name}")


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


    st.sidebar.markdown("### Editing Mode")
    editing_mode = st.sidebar.radio(
        "Select editing mode",
        options=list(EDITING_MODES.keys()),
        format_func=lambda x: EDITING_MODES[x]['name']
    )

    if editing_mode != st.session_state.editing_mode:
        st.session_state.editing_mode = editing_mode
        st.rerun()


    if st.session_state.project_state and hasattr(st.session_state.project_state, 'current_phase'):
        st.sidebar.markdown("### Progress")
        progress = st.sidebar.progress(0)
        current_phase = st.session_state.project_state.current_phase
        total_phases = len(PHASE_NAMES)
        progress.progress(current_phase / total_phases)
        st.sidebar.markdown(f"**Current Phase:** {PHASE_NAMES[current_phase]}")


    if st.sidebar.checkbox("Show Console Output", value=False):
        st.sidebar.markdown("### Console Output")
        if 'logger' in st.session_state and st.session_state.logger:
            for log in reversed(st.session_state.logger[-10:]):
                st.sidebar.text(log)
        else:
            st.sidebar.text("No console output available")


    st.sidebar.markdown("### Navigation")
    selected_tab = st.sidebar.radio(
        "Select Section",
        ["Documents", "Slides", "Preview", "Export"],
        key="navigation",
        index=["Documents", "Slides", "Preview", "Export"].index(st.session_state.active_tab)
    )


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









def parse_slide_response(response: str, slide_type:  str) -> dict:
    """Parse the AI's rich response into structured slide content."""
    try:
        # Set up data structure
        slide_content = {
            "sections": {
            },
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "references": [],
                "metrics": [],
                "sources": []
            }
        }

        # Unwanted phrases to filter out
        unwanted_phrases = ["Title Slide", "For the Title Slide", "Here's how you can structure it"]
        in_main_content = False
        main_content = []

        for line in str(response).split('\n'):
            line = line.strip()
            if not line:
                continue

            # Remove citation format and other unwanted symbols or bracketed text like 【】
            line = re.sub(r'【[^】]+】', '', line)  # Removes any citation in the format

            line = re.sub(r'\[[^\]]+\]|\【[^】]+】', '', line)
            # Skip lines containing any unwanted phrases
            if any(phrase in line for phrase in unwanted_phrases):
                continue



            # Skip lines starting with `##` or `###`
            if line.startswith('##') or line.startswith('###'):
                continue

            # Handle the '--' markers for main content collection
            if line == '--':
                in_main_content = not in_main_content  # Toggle in_main_content
                continue

            # Collect lines that are part of the main content
            if in_main_content:
                main_content.append(line)

        # Add the collected main content to the slide content
        slide_content["sections"]["main_content"] = {
            "content": [{"type": "simple", "content": item} for item in main_content]
        }

        return slide_content

    except Exception as e:
        print(f"Error parsing slide response: {str(e)}")  # For debugging purposes
        return {}



def display_slide_content(slide_type: str, content: str):
    """Display slide content with edit functionality"""
    slide_config = SLIDE_TYPES_ENGLISH.get(slide_type, {})

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


        for slide_type in SLIDE_TYPES_ENGLISH.keys():
            if slide_type not in st.session_state.project_state.slides:
                st.session_state.project_state.slides[slide_type] = {}

        st.session_state.project_state.save_state()
        return True
    except Exception as e:
        st.error(f"Failed to verify project state: {str(e)}")
        return False



def handle_slides_tab():
    """Handle Slides tab content"""
    st.header("Create Your Pitch Deck")

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


    if 'selected_slides' not in st.session_state:
        st.subheader("Select Slides to Include")

        selected_language = st.session_state.current_language

        st.markdown("#### Required Slides")
        required_slides_english = {
            "title": "Title Slide",
            "introduction": "Introduction",
            "problem": "Problem Statement",
            "solution": "Solution",
            "market": "Market Opportunity",
            "ask": "Ask",
        }

        required_slides_norwegian = {
            "title": "Tittelslide",
            "introduction": "Introduksjon",
            "problem": "Problemstilling",
            "solution": "Løsning",
            "market": "Markedmuligheter",
            "ask": "Forespørsel",
        }
        selected_language = st.session_state.current_language

        # Set the slide names based on the selected language
        if selected_language == "en":
            required_slides = required_slides_english

        elif selected_language == "no":
            required_slides = required_slides_norwegian

        else:
            # Default to English if no match
            required_slides = required_slides_english

        for slide_type, slide_name in required_slides.items():
            st.checkbox(slide_name, value=True, disabled=True, key=f"req_{slide_type}")


        st.markdown("#### Optional Slides")
        optional_slides_english = {
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

        optional_slides_norwegian = {
            "team": "Møt Teamet",
            "experience": "Vår Erfaring med Problemet",
            "revenue": "Inntektsmodell",
            "go_to_market": "Gå-til-marked Strategi",
            "demo": "Demo",
            "technology": "Teknologi",
            "pipeline": "Produktutviklingsplan",
            "expansion": "Produktutvidelse",
            "uniqueness": "Unikhet og Beskyttelse",
            "competition": "Konkurranselandskap",
            "traction": "Fremdrift og Milepæler",
            "financials": "Finansiell Oversikt",
            "use_of_funds": "Bruk av Midler"
        }
        selected_language = st.session_state.current_language

        # Set the slide names based on the selected language
        if selected_language == "en":

            optional_slides = optional_slides_english
        elif selected_language == "no":

            optional_slides = optional_slides_norwegian
        else:

            optional_slides = optional_slides_norwegian

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

                selected_slide_types = {
                    k: v for k, v in (
                        SLIDE_TYPES_NORWEGIAN if st.session_state.current_language == 'no' else SLIDE_TYPES_ENGLISH).items()
                    if k in st.session_state.selected_slides and st.session_state.selected_slides[k]
                }

                for slide_type, slide_config in selected_slide_types.items():
                    st.subheader(f"{slide_config['name']}")
                    slide_containers[slide_type] = st.empty()  # Create placeholder for each slide

                for idx, (slide_type, slide_config) in enumerate(selected_slide_types.items()):
                    progress_bar.progress((idx / len(selected_slide_types)))

                    # Update status in the slide's container
                    slide_containers[slide_type].info(f"Generating {slide_config['name']}...")

                    # Simply send the document content and slide type
                    # Define the content for each language
                    message_content_english = f"""
                    Create a **{slide_config['name']}** slide for a pitch deck using the provided company documents and the following detailed instructions.

                    ---

                    ### Slide Objective
                    Summarize the **{slide_config['name']}** slide in clear, concise bullet points that are ready for presentation. Focus on informative language, directly addressing the company’s context and goals without introductory phrases.

                    ### Content Guidelines:
                    * Use bullet points to clearly present key information.
                    * Aim for precision and relevance to the company’s objectives.
                    
                    * Include a minimum of three bullet points.

                    ---

                    ### Documented Content:
                    {doc_content}

                    ### Required Elements:
                    * {', '.join(slide_config['required_elements'])}

                    ### Tone and Style:
                    * Formal and professional.
                    * Engaging, easy to understand, and well-aligned with company goals.

                    ---

                    ### Prompt for Content Creation:
                    {slide_config['prompt']}

                    ---

                    Directly output the slide content below without additional instructions.
                    """

                    message_content_norwegian = f"""
                                        Svar på norsk. Svar kun med punktlister, og unngå introduksjonstekster og forklaringer.

                                        Lag en **{slide_config['name']}** for en presentasjon med utgangspunkt i selskapets dokumenter og følgende detaljerte instruksjoner.

                                        ### Mål for lysbilde
                                        Gi kun klare, konsise punkter for presentasjon. Unngå introduksjonsfraser eller kommentarer.

                                        ### Innholdskrav:
                                        * Bruk punktlister for å presentere nøkkelinformasjon.
                                        * Fokuser på presisjon og relevans for selskapets mål.
                                        * Hvert punkt skal være under 13 ord.
                                        * Inkluder minst tre punkter.

                                        ### Dokumentert innhold:
                                        {doc_content}

                                        ### Nødvendige elementer:
                                        * {', '.join(slide_config['required_elements'])}

                                        ### Tone og stil:
                                        * Formelt og profesjonelt.
                                        * Engasjerende og lett å forstå.

                                        ### Prompt for innhold:
                                        {slide_config['prompt']}
                                        """

                    # Now access current_language from the instance
                    selected_language = st.session_state.project_state.current_language


                    if selected_language == "en":
                        message_content = message_content_english
                    elif selected_language == "no":
                        message_content = message_content_norwegian
                    else:
                        message_content = message_content_norwegian  # Default to Norwegian if no match


                    # Send the message content
                    st.session_state.openai_client.beta.threads.messages.create(
                        thread_id=st.session_state.thread_id,
                        role="user",
                        content=message_content
                    )

                    run = st.session_state.openai_client.beta.threads.runs.create(
                        thread_id=st.session_state.thread_id,
                        assistant_id="asst_uCXB3ZuddxaZZeEqPh8LZ5Zf"
                    )


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

                        cleaned_response = clean_slide_content(response)

                        if 'raw_responses' not in st.session_state:
                            st.session_state.raw_responses = {}
                        st.session_state.raw_responses[slide_type] = cleaned_response



                        # Show the raw response
                        slide_containers[slide_type].markdown(f"""
                        `
                        {cleaned_response}
                      
                        """)


                        # Parse and save in background
                        slide_content = parse_slide_response(cleaned_response, slide_type)
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



import re

def clean_slide_content(response: str) -> str:
    # Remove text starting with '【' and everything after it on the same line

    # Remove any inline formatting indicators like triple backticks or stars around the text
    cleaned_text = re.sub(r"(```|\*\*|\*)", "", response)

    # Trim whitespace for final output and remove empty lines
    cleaned_text = re.sub(r"\n\s*\n", "\n", cleaned_text).strip()

    cleaned_text = re.sub(r"【.*", "", cleaned_text)

    return cleaned_text


if __name__ == "__main__":
    main()
