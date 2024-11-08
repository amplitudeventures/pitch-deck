import streamlit as st
import time
import json
from datetime import datetime
from typing import Optional, Dict

class ProjectState:
    def __init__(self, project_id: str, vector_store):
        self.project_id = project_id
        self.vector_store = vector_store
        self.current_phase = 0
        self.current_language = "no"
        self.slides = {}
        
        # Initialize raw_responses in session state if not exists
        if 'raw_responses' not in st.session_state:
            st.session_state.raw_responses = {}

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

                # Update session state
                st.session_state.raw_responses[slide_type] = response
                
                # Store in vector store
                success = self.vector_store.store_slide(
                    project_id=self.project_id,
                    slide_type=slide_type,
                    content=response,
                    language=self.current_language
                )
                
                if success:
                    # Update local state
                    self.slides[slide_type] = response
                    return True

            return False
            
        except Exception as e:
            st.error(f"Failed to update slide: {e}")
            return False

    def save_state(self) -> bool:
        """Save current state to vector store"""
        try:
            state_data = {
                'current_phase': self.current_phase,
                'timestamp': datetime.now().isoformat()
            }
            return self.vector_store.store_state(self.project_id, json.dumps(state_data))
        except Exception as e:
            st.error(f"Failed to save state: {e}")
            return False