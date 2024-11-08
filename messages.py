from typing import Dict, List, Optional

PHASE_NAMES = [
    "Phase 0: Document Analysis",
    "Phase 1: Slide Planning",
    "Phase 2: Content Generation",
    "Phase 3: Language Processing",
    "Phase 4: HTML Preview",
    "Phase 5: PDF Generation",
    "Phase 6: Canva Export"
]

PHASE_CONFIGS = {
    "Phase 0: Document Analysis": {
        "assistant_id": "asst_uCXB3ZuddxaZZeEqPh8LZ5Zf",
        "description": "Analyzes uploaded documents to understand company information",
        "requires_previous": False,
        "output_format": "report"
    },
    "Phase 1: Slide Planning": {
        "assistant_id": "asst_uCXB3ZuddxaZZeEqPh8LZ5Zf",
        "description": "Plans slide structure and content distribution",
        "requires_previous": True,
        "output_format": "json"
    },
    "Phase 2: Content Generation": {
        "assistant_id": "asst_uCXB3ZuddxaZZeEqPh8LZ5Zf",
        "description": "Generates content for each slide based on analysis",
        "requires_previous": True,
        "output_format": "slides"
    },
    "Phase 3: Language Processing": {
        "assistant_id": "asst_uCXB3ZuddxaZZeEqPh8LZ5Zf",
        "description": "Handles translation and language optimization",
        "requires_previous": True,
        "output_format": "slides"
    },
    "Phase 4: HTML Preview": {
        "assistant_id": "asst_uCXB3ZuddxaZZeEqPh8LZ5Zf",
        "description": "Generates interactive HTML preview of slides",
        "requires_previous": True,
        "output_format": "html"
    },
    "Phase 5: PDF Generation": {
        "assistant_id": "asst_uCXB3ZuddxaZZeEqPh8LZ5Zf",
        "description": "Creates PDF version of the pitch deck",
        "requires_previous": True,
        "output_format": "pdf"
    },
    "Phase 6: Canva Export": {
        "assistant_id": "asst_uCXB3ZuddxaZZeEqPh8LZ5Zf",
        "description": "Prepares and exports content to Canva",
        "requires_previous": True,
        "output_format": "canva"
    }
}

SLIDE_TYPES = {
    "title": {
        "name": "Title Slide",
        "feedback_options": ["Company Name", "Tagline", "Visual Theme"],
        "required_elements": ["company_name", "tagline"],
        "character_limit": 700
    },
    "introduction": {
        "name": "Introduction",
        "feedback_options": ["Clarity", "Length", "Key Message"],
        "required_elements": ["summary", "hook"],
        "character_limit": 700
    },
    "team": {
        "name": "Meet the Team",
        "feedback_options": ["Team Member Details", "Roles", "Experience"],
        "required_elements": ["members", "roles", "experience"],
        "character_limit": 700
    },
    "experience": {
        "name": "Our Experience with the Problem",
        "feedback_options": ["Relevance", "Credibility", "Impact"],
        "required_elements": ["background", "insights", "learnings"],
        "character_limit": 700
    },
    "problem": {
        "name": "Problem Statement",
        "feedback_options": ["Problem Clarity", "Market Impact", "Urgency"],
        "required_elements": ["problem_statement", "market_impact", "solution_need"],
        "character_limit": 700
    },
    "solution": {
        "name": "Solution",
        "feedback_options": ["Solution Clarity", "Value Proposition", "Innovation"],
        "required_elements": ["solution_description", "benefits", "unique_features"],
        "character_limit": 700
    },
    "revenue": {
        "name": "Revenue Model",
        "feedback_options": ["Model Clarity", "Viability", "Scalability"],
        "required_elements": ["revenue_streams", "pricing", "projections"],
        "character_limit": 700
    },
    "go_to_market": {
        "name": "Go-To-Market Strategy",
        "feedback_options": ["Strategy Clarity", "Channel Mix", "Timeline"],
        "required_elements": ["approach", "channels", "timeline"],
        "character_limit": 700
    },
    "demo": {
        "name": "Demo",
        "feedback_options": ["Clarity", "Impact", "Technical Detail"],
        "required_elements": ["features", "benefits", "use_cases"],
        "character_limit": 700
    },
    "technology": {
        "name": "Technology",
        "feedback_options": ["Technical Depth", "Innovation", "Feasibility"],
        "required_elements": ["tech_stack", "innovations", "advantages"],
        "character_limit": 700
    },
    "pipeline": {
        "name": "Product Development Pipeline",
        "feedback_options": ["Roadmap Clarity", "Milestones", "Timeline"],
        "required_elements": ["current_stage", "next_steps", "timeline"],
        "character_limit": 700
    },
    "expansion": {
        "name": "Product Expansion",
        "feedback_options": ["Vision", "Feasibility", "Market Fit"],
        "required_elements": ["future_products", "market_potential", "timeline"],
        "character_limit": 700
    },
    "uniqueness": {
        "name": "Uniqueness & Protectability",
        "feedback_options": ["Differentiation", "IP Strategy", "Barriers"],
        "required_elements": ["unique_features", "ip_protection", "moat"],
        "character_limit": 700
    },
    "competition": {
        "name": "Competitive Landscape",
        "feedback_options": ["Market Analysis", "Positioning", "Advantages"],
        "required_elements": ["competitors", "advantages", "positioning"],
        "character_limit": 700
    },
    "market": {
        "name": "Market Opportunity",
        "feedback_options": ["Market Size", "Growth Potential", "Target Segments"],
        "required_elements": ["market_size", "growth_rate", "target_segments"],
        "character_limit": 700
    },
    "traction": {
        "name": "Traction & Milestones",
        "feedback_options": ["Progress", "Achievements", "Future Goals"],
        "required_elements": ["current_status", "achievements", "roadmap"],
        "character_limit": 700
    },
    "financials": {
        "name": "Financial Overview",
        "feedback_options": ["Key Metrics", "Projections", "Investment Needs"],
        "required_elements": ["key_metrics", "projections", "funding_request"],
        "character_limit": 700
    },
    "ask": {
        "name": "Ask",
        "feedback_options": ["Clarity", "Justification", "Terms"],
        "required_elements": ["funding_request", "use_of_funds", "terms"],
        "character_limit": 700
    },
    "use_of_funds": {
        "name": "Use of Funds",
        "feedback_options": ["Allocation", "Timeline", "Impact"],
        "required_elements": ["allocation", "timeline", "expected_impact"],
        "character_limit": 700
    }
}

LANGUAGE_CONFIGS = {
    "no": {
        "name": "Norwegian",
        "date_format": "%d.%m.%Y",
        "currency_format": "NOK %s",
        "is_default": True,
        "special_characters": "æøåÆØÅ"
    },
    "en": {
        "name": "English",
        "date_format": "%Y-%m-%d",
        "currency_format": "$%s",
        "is_default": False,
        "special_characters": ""
    }
}

# Editing configurations
EDITING_MODES = {
    "structured": {
        "name": "Structured Feedback",
        "description": "Use predefined feedback options for each slide type",
        "allowed_operations": ["select_option", "provide_details"]
    },
    "guided": {
        "name": "Guided Editing",
        "description": "Step-by-step editing with AI assistance",
        "allowed_operations": ["modify_text", "regenerate", "translate"]
    }
}

# HTML/PDF Export configurations
EXPORT_CONFIGS = {
    "html": {
        "template_path": "templates/pitch_deck.html",
        "allowed_tags": ["h1", "h2", "p", "ul", "li", "strong", "em", "img"],
        "css_framework": "tailwind",
        "interactive": True
    },
    "pdf": {
        "page_size": "A4",
        "orientation": "landscape",
        "fonts": ["Arial", "Helvetica", "sans-serif"],
        "margin": {"top": 20, "right": 20, "bottom": 20, "left": 20}
    }
}

# System messages for the OpenAI assistant
SYSTEM_MESSAGES = {
    "document_analysis": """You are analyzing company documents for pitch deck creation.
Focus on extracting key information about: company overview, problem statement, solution,
market size, business model, team, and financials. Use the following format:
ANALYSIS_START
{analysis_content}
ANALYSIS_END""",
    
    "slide_generation": """You are generating content for a pitch deck slide.
Follow these guidelines:
1. Structure:
   - Use ### for slide titles with numbers (e.g., ### 1. Title Slide)
   - Use bullet points with bold headers (e.g., - **Header**: Content)
   - Include source references in 【】format

2. Content Requirements:
   - Clear, concise language
   - Focus on key messages
   - Maintain consistent tone
   - Include metrics and data where relevant
   - Add source references for key claims

3. Format Example:
   ### [Number]. [Slide Title]
   - **[Header]**: [Content]【source】
   - **[Metric]**: [Value]【source】
   Additional context or details...

4. Source References:
   - Use 【X:Y】format for citations
   - Include page/section numbers
   - Link to specific documents

5. Special Elements:
   - Bold text for emphasis
   - Metrics in clear format
   - Bullet points for readability
   - Citations for credibility

Format your response as:
SLIDE_START
[Your structured content following above format]
SLIDE_END""",
    
    # Add a new message type for rich content parsing
    "content_structure": {
        "slide_title": {
            "format": "### NUMBER. TITLE",
            "required": True
        },
        "bullet_points": {
            "format": "- **Header**: Content",
            "required": True
        },
        "references": {
            "format": "【source:page】",
            "required": False
        },
        "metrics": {
            "format": "NUMBER UNIT",
            "required": False
        }
    }
}

# Add content structure validation
def validate_slide_content(content: str) -> bool:
    """Validate if content follows required structure"""
    # Has title
    if not content.strip().startswith('###'):
        return False
    
    # Has bullet points
    if '- **' not in content:
        return False
        
    # Has at least one reference
    if '【' not in content or '】' not in content:
        return False
        
    return True

# Import from application writer's system prompts
TECHNICAL_CONSTRAINTS = """OPERATIONAL CONSTRAINTS:
1. Document Access:
   - READ-ONLY access to Pinecone documents
   - Can RETRIEVE and ANALYZE documents
   - CANNOT write or modify stored data
   - CANNOT create new document entries

2. Output Requirements:
   - Begin responses with "ANALYSIS_START"
   - End responses with "ANALYSIS_COMPLETE"
   - Follow format: {current_phase} > {analysis} > {recommendations}
   - Report errors as "ERROR: <message>"

3. Analysis Requirements:
   - Verify document completeness before analysis
   - Check data quality and report gaps
   - Apply pitch deck best practices consistently
   - Document all assumptions made

4. Response Format:
   - Use markdown for structure
   - Include timestamps for analysis steps
   - Tag uncertainties with confidence levels
   - Cite specific document references"""

def get_slide_template(slide_type: str, language: str) -> Optional[Dict]:
    """Get template for specific slide type in specified language"""
    # Validate inputs
    if not slide_type or not language:
        return None
        
    base_template = SLIDE_TYPES.get(slide_type)
    if not base_template:
        return None
        
    lang_config = LANGUAGE_CONFIGS.get(language)
    if not lang_config:
        # Fall back to English if language not supported
        lang_config = LANGUAGE_CONFIGS.get('en')
        if not lang_config:
            return base_template
        
    # Merge language-specific configurations
    template = base_template.copy()
    template['language'] = lang_config
    template['original_language'] = language
    return template

def get_phase_config(phase_name: str) -> Optional[Dict]:
    """Get configuration for specific phase"""
    return PHASE_CONFIGS.get(phase_name)

def get_system_message(message_type: str, **kwargs) -> str:
    """Get formatted system message for specific use case"""
    message_template = SYSTEM_MESSAGES.get(message_type)
    if not message_template:
        return ""
    return message_template.format(**kwargs)
