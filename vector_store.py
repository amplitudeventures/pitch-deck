from pinecone import Pinecone
import os
from openai import OpenAI
import streamlit as st
from datetime import datetime
from threading import Lock
import functools
import hashlib
import json
from typing import List, Dict, Optional, Any, Callable
import PyPDF2
from io import BytesIO

def with_storage_lock(func):
    """Decorator to ensure thread-safe storage operations"""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        with self._storage_lock:
            return func(self, *args, **kwargs)
    return wrapper

class VectorStore:
    def __init__(self, api_key: str, environment: str = "gcp-starter", log_function: Callable = None):
        """Initialize VectorStore with API key and optional logging function"""
        try:
            # First, set up logging function
            self.log_function = log_function or (lambda action, details, error=False: None)
            
            # Validate inputs
            if not api_key or not api_key.startswith('pcsk_'):
                raise ValueError("Invalid Pinecone API key format")
                
            if not environment:
                raise ValueError("Environment must be specified")
            
            # Initialize core attributes
            self.dimension = 1536  # OpenAI ada-002 dimension
            self._storage_lock = Lock()
            self._document_cache = {}
            self._slide_cache = {}
            self._html_cache = {}
            
            # Initialize Pinecone with additional error handling
            try:
                self.pc = Pinecone(
                    api_key=api_key,
                    environment=environment
                )
                self.log_function("Initialization", "Pinecone client initialized")
                
                # Check if index exists, create if it doesn't
                index_name = "pitchdeckcreator-zjwe571"
                try:
                    # List all indexes
                    indexes = self.pc.list_indexes()
                    
                    # Create index if it doesn't exist
                    if index_name not in [index.name for index in indexes]:
                        self.pc.create_index(
                            name=index_name,
                            dimension=self.dimension,
                            metric="cosine",
                            spec={
                                "pod": {
                                    "environment": environment,
                                    "pod_type": "starter"
                                }
                            }
                        )
                        self.log_function("Initialization", f"Created new Pinecone index: {index_name}")
                    
                    # Connect to the index
                    self.index = self.pc.Index(index_name)
                    
                    # Test connection
                    test_result = self.index.query(
                        vector=[0.1] * self.dimension,
                        top_k=1,
                        include_metadata=True
                    )
                    self.log_function("Initialization", "Pinecone index connected successfully")
                    
                except Exception as e:
                    raise Exception(f"Failed to setup Pinecone index: {str(e)}")
                
            except Exception as e:
                raise Exception(f"Pinecone initialization failed: {str(e)}")
                
            # Initialize OpenAI client
            try:
                self.client = OpenAI()
                self.log_function("Initialization", "OpenAI client initialized")
            except Exception as e:
                self.log_function("Error", f"OpenAI client initialization failed: {str(e)}", error=True)
                raise
                
            self.log_function("Initialization", "VectorStore initialization complete")
            
        except Exception as e:
            # Ensure we have logging function before final error
            if not hasattr(self, 'log_function'):
                self.log_function = log_function or (lambda action, details, error=False: None)
            self.log_function("Error", f"VectorStore initialization failed: {str(e)}", error=True)
            raise Exception(f"Failed to initialize VectorStore: {str(e)}")

    def get_project_namespace(self, project_id: str, namespace_type: Optional[str] = None) -> str:
        """Get unified namespace for project"""
        clean_id = project_id.replace('proj_', '')
        base_namespace = f"proj_{clean_id}"
        if namespace_type:
            return f"{base_namespace}_{namespace_type}"
        return base_namespace

    @with_storage_lock
    def store_document(self, project_id: str, content: str, metadata: Dict) -> bool:
        """Store document with proper tracking"""
        try:
            namespace = self.get_project_namespace(project_id, 'docs')
            
            # Generate a unique document ID
            doc_id = f"doc_{datetime.now().timestamp()}"
            
            # Create embedding for content
            vector = self.embed_text(content)
            if not vector:
                return False
            
            # Prepare metadata with tracking info
            full_metadata = {
                'project_id': project_id,
                'doc_id': doc_id,
                'content': content,
                'timestamp': datetime.now().isoformat(),
                **metadata
            }
            
            # Store in Pinecone
            self.index.upsert(
                vectors=[(doc_id, vector, full_metadata)],
                namespace=namespace
            )
            
            # Update cache with new document
            if project_id not in self._document_cache:
                self._document_cache[project_id] = {}
            self._document_cache[project_id][doc_id] = {
                'content': content,
                'metadata': full_metadata
            }
            
            return True
            
        except Exception as e:
            self.log_function("Error", f"Failed to store document: {str(e)}", error=True)
            return False

    def _extract_content(self, file_obj: Any) -> Optional[str]:
        """Extract text content from various file types"""
        try:
            if file_obj.type == "text/plain":
                return file_obj.read().decode('utf-8', errors='ignore')
            elif file_obj.type == "application/pdf":
                pdf_reader = PyPDF2.PdfReader(BytesIO(file_obj.read()))
                return "\n".join(page.extract_text() for page in pdf_reader.pages)
            else:
                self.log_function("⚠️", f"Unsupported file type: {file_obj.type}")
                return None
        except Exception as e:
            self.log_function("🔴", f"Content extraction failed: {str(e)}")
            return None

    def chunk_text(self, text: str, max_chunk_size: int = 4000) -> List[str]:
        """Split text into chunks of maximum size"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            word_size = len(word) + 1  # +1 for space
            if current_size + word_size > max_chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_size = word_size
            else:
                current_chunk.append(word)
                current_size += word_size
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks

    def embed_text(self, text: str) -> Optional[List[float]]:
        """Create embedding for text using OpenAI ada-002"""
        try:
            response = self.client.embeddings.create(
                input=text,
                model="text-embedding-ada-002"  # Using ada-002 for 1536 dimensions
            )
            
            embedding = response.data[0].embedding
            return embedding
            
        except Exception as e:
            self.log_function("🔴", f"Embedding failed: {str(e)}")
            return None

    @with_storage_lock
    def store_slide(self, project_id: str, slide_type: str, content: Dict, 
                   language: str = "no") -> bool:
        """Store slide content with version control"""
        try:
            namespace = self.get_project_namespace(project_id, 'slides')
            
            # Create composite key for slide
            slide_key = f"{slide_type}_{language}"
            
            # Add metadata
            metadata = {
                "project_id": project_id,
                "slide_type": slide_type,"language": language,
                "version": datetime.now().isoformat(),
                "content": content,
                "timestamp": datetime.now().isoformat()
            }
            
            # Create embedding for slide content
            vector = self.embed_text(json.dumps(content))
            if not vector:
                return False
                
            # Store slide
            slide_id = f"slide_{slide_key}_{datetime.now().timestamp()}"
            self.index.upsert(
                vectors=[(slide_id, vector, metadata)],
                namespace=namespace
            )
            
            # Update slide cache
            if project_id not in self._slide_cache:
                self._slide_cache[project_id] = {}
            self._slide_cache[project_id][slide_key] = {
                "content": content,
                "metadata": metadata
            }
            
            return True
            
        except Exception as e:
            self.log_function("🔴", f"Failed to store slide: {str(e)}")
            return False

    def store_html_preview(self, project_id: str, html_content: str, 
                          metadata: Optional[Dict] = None) -> bool:
        """Store HTML preview of pitch deck"""
        try:
            namespace = self.get_project_namespace(project_id, 'html')
            
            # Create embedding for HTML content
            vector = self.embed_text(html_content)
            if not vector:
                return False
                
            # Add metadata
            full_metadata = {
                "project_id": project_id,
                "type": "html_preview",
                "timestamp": datetime.now().isoformat(),
                "content": html_content,
                **(metadata or {})
            }
            
            # Store HTML preview
            preview_id = f"html_{datetime.now().timestamp()}"
            self.index.upsert(
                vectors=[(preview_id, vector, full_metadata)],
                namespace=namespace
            )
            
            # Update HTML cache
            self._html_cache[project_id] = {
                "content": html_content,
                "metadata": full_metadata
            }
            
            return True
            
        except Exception as e:
            self.log_function("🔴", f"Failed to store HTML preview: {str(e)}")
            return False

    @with_storage_lock
    def get_latest_slides(self, project_id: str, language: str = "no") -> Dict:
        """Retrieve latest version of all slides for a project"""
        try:
            namespace = self.get_project_namespace(project_id, 'slides')
            
            # Check cache first
            if project_id in self._slide_cache:
                return {k: v for k, v in self._slide_cache[project_id].items() 
                       if k.endswith(f"_{language}")}
            
            # Query for all slides in the specified language
            results = self.index.query(
                namespace=namespace,
                vector=[0.1] * self.dimension,
                filter={
                    "project_id": project_id,
                    "language": language
                },
                top_k=100,
                include_metadata=True
            )
            
            slides = {}
            for match in results.matches:
                metadata = match.metadata
                slide_type = metadata.get("slide_type")
                if slide_type:
                    slide_key = f"{slide_type}_{language}"
                    slides[slide_key] = {
                        "content": metadata.get("content", {}),
                        "metadata": metadata
                    }
            
            # Update cache
            self._slide_cache[project_id] = slides
            return slides
            
        except Exception as e:
            self.log_function("🔴", f"Failed to retrieve slides: {str(e)}")
            return {}

    def get_html_preview(self, project_id: str) -> Optional[Dict]:
        """Retrieve latest HTML preview for a project"""
        try:
            namespace = self.get_project_namespace(project_id, 'html')
            
            # Check cache first
            if project_id in self._html_cache:
                return self._html_cache[project_id]
            
            # Query for latest HTML preview
            results = self.index.query(
                namespace=namespace,
                vector=[0.1] * self.dimension,
                filter={"project_id": project_id, "type": "html_preview"},
                top_k=1,
                include_metadata=True
            )
            
            if results.matches:
                metadata = results.matches[0].metadata
                preview_data = {
                    "content": metadata.get("content", ""),
                    "metadata": metadata
                }
                self._html_cache[project_id] = preview_data
                return preview_data
            
            return None
            
        except Exception as e:
            self.log_function("🔴", f"Failed to retrieve HTML preview: {str(e)}")
            return None

    @with_storage_lock
    def clear_project_data(self, project_id: str) -> bool:
        """Clear all project data with improved error handling"""
        try:
            # Clear data from each namespace
            namespaces = ['docs', 'slides', 'html']
            for ns_type in namespaces:
                namespace = self.get_project_namespace(project_id, ns_type)
                self.index.delete(
                    namespace=namespace,
                    filter={"project_id": project_id}
                )
            
            # Clear caches
            self._document_cache.pop(project_id, None)
            self._slide_cache.pop(project_id, None)
            self._html_cache.pop(project_id, None)
            
            if hasattr(st.session_state, 'document_cache'):
                st.session_state.document_cache.pop(project_id, None)
            
            return True
            
        except Exception as e:
            self.log_function("🔴", f"Failed to clear project data: {str(e)}")
            return False

    def _update_cache(self, project_id: str, content: str, metadata: Dict, 
                     content_hash: str) -> None:
        """Update document cache with new content"""
        if not hasattr(self, '_document_cache'):
            self._document_cache = {}
            
        if project_id not in self._document_cache:
            self._document_cache[project_id] = []
            
        # Remove old entries with same content hash
        self._document_cache[project_id] = [
            entry for entry in self._document_cache[project_id]
            if entry['content_hash'] != content_hash
        ]
        
        # Add new entry
        cache_entry = {
            'content': content,
            'metadata': metadata,
            'content_hash': content_hash,
            'timestamp': datetime.now().isoformat()
        }
        
        self._document_cache[project_id].append(cache_entry)
        
        # Limit cache size
        max_cache_entries = 100
        if len(self._document_cache[project_id]) > max_cache_entries:
            self._document_cache[project_id] = self._document_cache[project_id][-max_cache_entries:]
        
        # Update session state cache
        if hasattr(st.session_state, 'document_cache'):
            st.session_state.document_cache = self._document_cache.copy()

    def ensure_project_namespaces(self, project_id: str) -> bool:
        """Ensure that the project namespace exists in the vector store."""
        try:
            namespaces = ['docs', 'slides', 'html', 'state']
            for ns_type in namespaces:
                namespace = self.get_project_namespace(project_id, ns_type)
                # Check if namespace exists
                try:
                    self.index.query(
                        namespace=namespace,
                        vector=[0.1] * self.dimension,
                        top_k=1
                    )
                except Exception:
                    # If query fails, namespace might not exist
                    # Create it with a dummy vector
                    self.index.upsert(
                        vectors=[
                            (
                                f"init_{ns_type}",
                                [0.1] * self.dimension,
                                {"type": "namespace_init"}
                            )
                        ],
                        namespace=namespace
                    )
            return True
        except Exception as e:
            self.log_function("Error", f"Failed to ensure project namespaces: {str(e)}", error=True)
            return False

    @with_storage_lock
    def store_state(self, project_id: str, state_data: str) -> bool:
        """Store project state in vector store"""
        try:
            namespace = self.get_project_namespace(project_id, 'state')
            
            # Create vector from state data
            vector = self.embed_text(state_data)
            if not vector:
                return False
            
            # Store state with timestamp
            state_id = f"state_{datetime.now().timestamp()}"
            metadata = {
                'project_id': project_id,
                'type': 'project_state',
                'timestamp': datetime.now().isoformat(),
                'state_data': state_data
            }
            
            self.index.upsert(
                vectors=[(state_id, vector, metadata)],
                namespace=namespace
            )
            
            return True
            
        except Exception as e:
            self.log_function("Error", f"Failed to store state: {str(e)}", error=True)
            return False

    def get_project_state(self, project_id: str) -> Optional[Dict]:
        """Retrieve latest project state"""
        try:
            namespace = self.get_project_namespace(project_id, 'state')
            
            # Query for latest state
            results = self.index.query(
                namespace=namespace,
                vector=[0.1] * self.dimension,
                filter={
                    "project_id": project_id,
                    "type": "project_state"
                },
                top_k=1,
                include_metadata=True
            )
            
            if results.matches:
                state_data = results.matches[0].metadata.get('state_data')
                if state_data:
                    return json.loads(state_data)
            
            return None
            
        except Exception as e:
            self.log_function("Error", f"Failed to retrieve state: {str(e)}", error=True)
            return None

    @with_storage_lock
    def get_documents(self, project_id: str) -> List[Dict]:
        """Retrieve all documents for a project"""
        try:
            namespace = self.get_project_namespace(project_id, 'docs')
            
            # Check cache first
            if project_id in self._document_cache:
                # Convert cache dictionary to list
                return list(self._document_cache[project_id].values())
            
            # Query for all documents
            results = self.index.query(
                namespace=namespace,
                vector=[0.1] * self.dimension,
                filter={"project_id": project_id},
                top_k=100,
                include_metadata=True
            )
            
            # Process results
            documents = []
            self._document_cache[project_id] = {}  # Initialize cache
            
            for match in results.matches:
                metadata = match.metadata
                if metadata and 'content' in metadata and 'doc_id' in metadata:
                    doc = {
                        'content': metadata['content'],
                        'metadata': metadata
                    }
                    documents.append(doc)
                    # Cache using doc_id as key
                    self._document_cache[project_id][metadata['doc_id']] = doc
            
            return documents
            
        except Exception as e:
            self.log_function("Error", f"Failed to retrieve documents: {str(e)}", error=True)
            return []

    @with_storage_lock
    def store_slides(self, project_id: str, slides: Dict, language: str = "no") -> bool:
        """Store slides in vector store"""
        try:
            namespace = self.get_project_namespace(project_id, 'slides')
            
            # Store each slide separately
            for slide_type, content in slides.items():
                # Create vector from slide content
                content_str = json.dumps(content)
                vector = self.embed_text(content_str)
                if not vector:
                    continue
                
                # Create unique ID for this slide version
                slide_id = f"slide_{slide_type}_{datetime.now().timestamp()}"
                
                # Prepare metadata
                metadata = {
                    'project_id': project_id,
                    'slide_type': slide_type,
                    'content': content,
                    'language': language,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Store in Pinecone
                self.index.upsert(
                    vectors=[(slide_id, vector, metadata)],
                    namespace=namespace
                )
            
            # Update cache
            self._slide_cache[project_id] = slides
            return True
            
        except Exception as e:
            self.log_function("Error", f"Failed to store slides: {str(e)}", error=True)
            return False

    @with_storage_lock
    def get_latest_slides(self, project_id: str, language: str = "no") -> Dict:
        """Retrieve latest slides with improved error handling"""
        try:
            namespace = self.get_project_namespace(project_id, 'slides')
            
            # Check cache first
            if project_id in self._slide_cache:
                return self._slide_cache[project_id]
            
            # Query for all slides
            results = self.index.query(
                namespace=namespace,
                vector=[0.1] * self.dimension,
                filter={
                    "project_id": project_id,
                    "language": language
                },
                top_k=100,
                include_metadata=True
            )
            
            # Process results, keeping only the latest version of each slide
            slides = {}
            latest_timestamps = {}
            
            for match in results.matches:
                metadata = match.metadata
                if metadata and all(k in metadata for k in ['slide_type', 'content', 'timestamp']):
                    slide_type = metadata['slide_type']
                    timestamp = datetime.fromisoformat(metadata['timestamp'])
                    
                    # Keep only the latest version of each slide
                    if slide_type not in latest_timestamps or timestamp > latest_timestamps[slide_type]:
                        slides[slide_type] = metadata['content']
                        latest_timestamps[slide_type] = timestamp
            
            # Update cache
            self._slide_cache[project_id] = slides
            return slides
            
        except Exception as e:
            self.log_function("Error", f"Failed to retrieve slides: {str(e)}", error=True)
            return {}