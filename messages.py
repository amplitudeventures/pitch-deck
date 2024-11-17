from typing import Dict, List, Optional

# English phase names
PHASE_NAMES_ENGLISH = [
    "Phase 0: Document Analysis",
    "Phase 1: Slide Planning",
    "Phase 2: Content Generation",
    "Phase 3: Language Processing",
    "Phase 4: HTML Preview",
    "Phase 5: PDF Generation",
    "Phase 6: Canva Export"
]

# Norwegian phase names
PHASE_NAMES_NORWEGIAN = [
    "Fase 0: Dokumentanalyse",
    "Fase 1: Lysbildeplanlegging",
    "Fase 2: Innholdsgenerering",
    "Fase 3: Språkbehandling",
    "Fase 4: HTML-forhåndsvisning",
    "Fase 5: PDF-generering",
    "Fase 6: Canva-eksport"
]

# English phase configurations
PHASE_CONFIGS_ENGLISH = {
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

# Norwegian phase configurations
PHASE_CONFIGS_NORWEGIAN = {
    "Fase 0: Dokumentanalyse": {
        "assistant_id": "asst_uCXB3ZuddxaZZeEqPh8LZ5Zf",
        "description": "Analyserer opplastede dokumenter for å forstå selskapsinformasjon",
        "requires_previous": False,
        "output_format": "report"
    },
    "Fase 1: Lysbildeplanlegging": {
        "assistant_id": "asst_uCXB3ZuddxaZZeEqPh8LZ5Zf",
        "description": "Planlegger lysbildestruktur og innholdsdistribusjon",
        "requires_previous": True,
        "output_format": "json"
    },
    "Fase 2: Innholdsgenerering": {
        "assistant_id": "asst_uCXB3ZuddxaZZeEqPh8LZ5Zf",
        "description": "Genererer innhold for hvert lysbilde basert på analyse",
        "requires_previous": True,
        "output_format": "slides"
    },
    "Fase 3: Språkbehandling": {
        "assistant_id": "asst_uCXB3ZuddxaZZeEqPh8LZ5Zf",
        "description": "Håndterer oversettelse og språkopptimalisering",
        "requires_previous": True,
        "output_format": "slides"
    },
    "Fase 4: HTML-forhåndsvisning": {
        "assistant_id": "asst_uCXB3ZuddxaZZeEqPh8LZ5Zf",
        "description": "Genererer interaktiv HTML-forhåndsvisning av lysbilder",
        "requires_previous": True,
        "output_format": "html"
    },
    "Fase 5: PDF-generering": {
        "assistant_id": "asst_uCXB3ZuddxaZZeEqPh8LZ5Zf",
        "description": "Oppretter PDF-versjon av presentasjonen",
        "requires_previous": True,
        "output_format": "pdf"
    },
    "Fase 6: Canva-eksport": {
        "assistant_id": "asst_uCXB3ZuddxaZZeEqPh8LZ5Zf",
        "description": "Forbereder og eksporterer innhold til Canva",
        "requires_previous": True,
        "output_format": "canva"
    }
}

# English slide types

SLIDE_TYPES_ENGLISH = {
    "title": {
        "name": "Title Slide",
        "prompt": "Generate a title slide with the company's name, tagline, and a cohesive visual theme that captures the company's essence.",
        "feedback_options": ["Company Name", "Tagline", "Visual Theme"],
        "required_elements": ["company_name", "tagline"],
        "character_limit": 700
    },
    "introduction": {
        "name": "Introduction",
        "prompt": "Provide a brief, engaging summary of the company, focusing on a hook that captures interest and explains the company's core value proposition.",
        "feedback_options": ["Clarity", "Length", "Key Message"],
        "required_elements": ["summary", "hook"],
        "character_limit": 700
    },
    "team": {
        "name": "Meet the Team",
        "prompt": "Introduce the team, including key members' roles, expertise, and achievements relevant to their position to showcase the team’s qualifications.",
        "feedback_options": ["Team Member Details", "Roles", "Experience"],
        "required_elements": ["members", "roles", "experience"],
        "character_limit": 700
    },
    "experience": {
        "name": "Our Experience with the Problem",
        "prompt": "Describe the team's background and prior experiences that led to the understanding of the problem, demonstrating credibility and relevance.",
        "feedback_options": ["Relevance", "Credibility", "Impact"],
        "required_elements": ["background", "insights", "learnings"],
        "character_limit": 700
    },
    "problem": {
        "name": "Problem Statement",
        "prompt": "Describe the market problem, detailing how it impacts the target audience and why a solution is urgently needed. Include data if available.",
        "feedback_options": ["Problem Clarity", "Market Impact", "Urgency"],
        "required_elements": ["problem_statement", "market_impact", "solution_need"],
        "character_limit": 700
    },
    "solution": {
        "name": "Solution",
        "prompt": "Outline the solution, emphasizing unique features and value propositions that address the problem effectively.",
        "feedback_options": ["Solution Clarity", "Value Proposition", "Innovation"],
        "required_elements": ["solution_description", "benefits", "unique_features"],
        "character_limit": 700
    },
    "revenue": {
        "name": "Revenue Model",
        "prompt": "Explain the revenue model, detailing how the company plans to generate income, including pricing strategies and revenue streams.",
        "feedback_options": ["Model Clarity", "Viability", "Scalability"],
        "required_elements": ["revenue_streams", "pricing", "projections"],
        "character_limit": 700
    },
    "go_to_market": {
        "name": "Go-To-Market Strategy",
        "prompt": "Describe the go-to-market approach, covering target channels, marketing strategies, and a high-level timeline for market entry.",
        "feedback_options": ["Strategy Clarity", "Channel Mix", "Timeline"],
        "required_elements": ["approach", "channels", "timeline"],
        "character_limit": 700
    },
    "demo": {
        "name": "Demo",
        "prompt": "Showcase the product's features, benefits, and potential use cases, providing a visual walkthrough or key aspects of functionality.",
        "feedback_options": ["Clarity", "Impact", "Technical Detail"],
        "required_elements": ["features", "benefits", "use_cases"],
        "character_limit": 700
    },
    "technology": {
        "name": "Technology",
        "prompt": "Highlight the technology stack, unique innovations, and technical advantages that distinguish the solution.",
        "feedback_options": ["Technical Depth", "Innovation", "Feasibility"],
        "required_elements": ["tech_stack", "innovations", "advantages"],
        "character_limit": 700
    },
    "pipeline": {
        "name": "Product Development Pipeline",
        "prompt": "Present the development timeline, key milestones achieved, and upcoming goals to provide a clear product roadmap.",
        "feedback_options": ["Roadmap Clarity", "Milestones", "Timeline"],
        "required_elements": ["current_stage", "next_steps", "timeline"],
        "character_limit": 700
    },
    "expansion": {
        "name": "Product Expansion",
        "prompt": "Outline future expansion plans, including new products, potential markets, and estimated timelines.",
        "feedback_options": ["Vision", "Feasibility", "Market Fit"],
        "required_elements": ["future_products", "market_potential", "timeline"],
        "character_limit": 700
    },
    "uniqueness": {
        "name": "Uniqueness & Protectability",
        "prompt": "Explain what makes the product unique and how it is protected, such as intellectual property or barriers to entry.",
        "feedback_options": ["Differentiation", "IP Strategy", "Barriers"],
        "required_elements": ["unique_features", "ip_protection", "moat"],
        "character_limit": 700
    },
    "competition": {
        "name": "Competitive Landscape",
        "prompt": "Analyze competitors and demonstrate how the solution is positioned to offer competitive advantages.",
        "feedback_options": ["Market Analysis", "Positioning", "Advantages"],
        "required_elements": ["competitors", "advantages", "positioning"],
        "character_limit": 700
    },
    "market": {
        "name": "Market Opportunity",
        "prompt": "Describe the market opportunity, including size, growth potential, and target customer segments.",
        "feedback_options": ["Market Size", "Growth Potential", "Target Segments"],
        "required_elements": ["market_size", "growth_rate", "target_segments"],
        "character_limit": 700
    },
    "traction": {
        "name": "Traction & Milestones",
        "prompt": "Highlight key achievements, progress, and milestones that indicate traction and momentum in the market.",
        "feedback_options": ["Progress", "Achievements", "Future Goals"],
        "required_elements": ["current_status", "achievements", "roadmap"],
        "character_limit": 700
    },
    "financials": {
        "name": "Financial Overview",
        "prompt": "Present a financial summary, focusing on key metrics, projections, and any specific funding needs.",
        "feedback_options": ["Key Metrics", "Projections", "Investment Needs"],
        "required_elements": ["key_metrics", "projections", "funding_request"],
        "character_limit": 700
    },
    "ask": {
        "name": "Ask",
        "prompt": "Clearly state the investment amount being sought, its intended uses, and any terms being proposed.",
        "feedback_options": ["Clarity", "Justification", "Terms"],
        "required_elements": ["funding_request", "use_of_funds", "terms"],
        "character_limit": 700
    },
    "use_of_funds": {
        "name": "Use of Funds",
        "prompt": "Break down the allocation of funds, expected timeline for usage, and the impact these funds will have.",
        "feedback_options": ["Allocation", "Timeline", "Impact"],
        "required_elements": ["allocation", "timeline", "expected_impact"],
        "character_limit": 700
    }
}


SLIDE_TYPES_NORWEGIAN = {
    "title": {
        "name": "Tittelside",
        "prompt": "Generer en tittelside med selskapets navn, slagord og et sammenhengende visuelt tema som fanger selskapets essens.",
        "feedback_options": ["Firmanavn", "Slagord", "Visuelt Tema"],
        "required_elements": ["company_name", "tagline"],
        "character_limit": 700
    },
    "introduction": {
        "name": "Introduksjon",
        "prompt": "Gi en kort, engasjerende oppsummering av selskapet, med fokus på en krok som vekker interesse og forklarer selskapets kjerneverdier.",
        "feedback_options": ["Klarhet", "Lengde", "Hovedbudskap"],
        "required_elements": ["summary", "hook"],
        "character_limit": 700
    },
    "team": {
        "name": "Møt Teamet",
        "prompt": "Presenter teamet, inkludert nøkkelpersoners roller, ekspertise og relevante prestasjoner for å vise teamets kvalifikasjoner.",
        "feedback_options": ["Teammedlem-detaljer", "Roller", "Erfaring"],
        "required_elements": ["members", "roles", "experience"],
        "character_limit": 700
    },
    "experience": {
        "name": "Vår Erfaring med Problemet",
        "prompt": "Beskriv teamets bakgrunn og tidligere erfaringer som førte til forståelsen av problemet, og demonstrer troverdighet og relevans.",
        "feedback_options": ["Relevans", "Troverdighet", "Effekt"],
        "required_elements": ["background", "insights", "learnings"],
        "character_limit": 700
    },
    "problem": {
        "name": "Problemstilling",
        "prompt": "Beskriv markedsproblemet, hvordan det påvirker målgruppen og hvorfor en løsning er nødvendig. Inkluder data hvis tilgjengelig.",
        "feedback_options": ["Problemklarhet", "Markedsinnvirkning", "Hastepreg"],
        "required_elements": ["problem_statement", "market_impact", "solution_need"],
        "character_limit": 700
    },
    "solution": {
        "name": "Løsning",
        "prompt": "Beskriv løsningen, med fokus på unike funksjoner og verdiforslag som effektivt adresserer problemet.",
        "feedback_options": ["Løsningsklarhet", "Verdiforslag", "Innovasjon"],
        "required_elements": ["solution_description", "benefits", "unique_features"],
        "character_limit": 700
    },
    "revenue": {
        "name": "Inntektsmodell",
        "prompt": "Forklar inntektsmodellen, inkludert hvordan selskapet planlegger å generere inntekter, prisstrategier og inntektsstrømmer.",
        "feedback_options": ["Modellklarhet", "Levedyktighet", "Skalerbarhet"],
        "required_elements": ["revenue_streams", "pricing", "projections"],
        "character_limit": 700
    },
    "go_to_market": {
        "name": "Markedsstrategi",
        "prompt": "Beskriv markedsstrategien, inkludert målkanaler, markedsføringsstrategier og en overordnet tidslinje for markedsinngang.",
        "feedback_options": ["Strategiklarhet", "Kanalblanding", "Tidslinje"],
        "required_elements": ["approach", "channels", "timeline"],
        "character_limit": 700
    },
    "demo": {
        "name": "Demo",
        "prompt": "Vis produktets funksjoner, fordeler og potensielle bruksområder, og gi en visuell gjennomgang eller hovedaspekter av funksjonalitet.",
        "feedback_options": ["Klarhet", "Effekt", "Teknisk Detalj"],
        "required_elements": ["features", "benefits", "use_cases"],
        "character_limit": 700
    },
    "technology": {
        "name": "Teknologi",
        "prompt": "Fremhev teknologistacken, unike innovasjoner og tekniske fordeler som skiller løsningen.",
        "feedback_options": ["Teknisk Dybde", "Innovasjon", "Gjennomførbarhet"],
        "required_elements": ["tech_stack", "innovations", "advantages"],
        "character_limit": 700
    },
    "pipeline": {
        "name": "Produktutviklingsprosess",
        "prompt": "Presenter utviklingstidslinjen, oppnådde milepæler og kommende mål for å gi en tydelig produktvei.",
        "feedback_options": ["Veikartklarhet", "Milepæler", "Tidslinje"],
        "required_elements": ["current_stage", "next_steps", "timeline"],
        "character_limit": 700
    },
    "expansion": {
        "name": "Produktutvidelse",
        "prompt": "Beskriv fremtidige ekspansjonsplaner, inkludert nye produkter, potensielle markeder og estimerte tidslinjer.",
        "feedback_options": ["Visjon", "Gjennomførbarhet", "Markedstilpasning"],
        "required_elements": ["future_products", "market_potential", "timeline"],
        "character_limit": 700
    },
    "uniqueness": {
        "name": "Unikhet & Beskyttelse",
        "prompt": "Forklar hva som gjør produktet unikt og hvordan det er beskyttet, for eksempel gjennom immaterielle rettigheter eller hindringer for inntrenging.",
        "feedback_options": ["Differensiering", "IP-strategi", "Barriere"],
        "required_elements": ["unique_features", "ip_protection", "moat"],
        "character_limit": 700
    },
    "competition": {
        "name": "Konkurransesituasjon",
        "prompt": "Analyser konkurrenter og vis hvordan løsningen er posisjonert for å tilby konkurransefordeler.",
        "feedback_options": ["Markedsanalyse", "Posisjonering", "Fordeler"],
        "required_elements": ["competitors", "advantages", "positioning"],
        "character_limit": 700
    },
    "market": {
        "name": "Markedsmulighet",
        "prompt": "Beskriv markedsmuligheten, inkludert størrelse, vekstpotensial og målsegmenter.",
        "feedback_options": ["Markedsstørrelse", "Vekstpotensial", "Målsegmenter"],
        "required_elements": ["market_size", "growth_rate", "target_segments"],
        "character_limit": 700
    },
    "traction": {
        "name": "Traksjon & Milepæler",
        "prompt": "Fremhev nøkkelfremgang, prestasjoner og milepæler som viser traksjon og momentum i markedet.",
        "feedback_options": ["Fremgang", "Prestasjoner", "Fremtidige Mål"],
        "required_elements": ["current_status", "achievements", "roadmap"],
        "character_limit": 700
    },
    "financials": {
        "name": "Finansiell Oversikt",
        "prompt": "Presentér en finansiell oppsummering, med fokus på nøkkelmetrikker, prognoser og eventuelle spesifikke finansieringsbehov.",
        "feedback_options": ["Nøkkelmetrikker", "Prognoser", "Investeringsbehov"],
        "required_elements": ["key_metrics", "projections", "funding_request"],
        "character_limit": 700
    },
    "ask": {
        "name": "Anmodning",
        "prompt": "Oppgi klart investeringsbeløpet som søkes, dets tiltenkte bruksområder og eventuelle foreslåtte vilkår.",
        "feedback_options": ["Klarhet", "Begrunnelse", "Vilkår"],
        "required_elements": ["funding_request", "use_of_funds", "terms"],
        "character_limit": 700
    },
    "use_of_funds": {
        "name": "Bruk av Midler",
        "prompt": "Beskriv fordelingen av midlene, forventet tidslinje for bruk og hvilken innvirkning disse midlene vil ha.",
        "feedback_options": ["Fordeling", "Tidslinje", "Innvirkning"],
        "required_elements": ["allocation", "timeline", "expected_impact"],
        "character_limit": 700
    }
}


# Language configurations
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

# Function to get phase names based on language
def get_phase_names(language: str) -> List[str]:
    if language == "no":
        return PHASE_NAMES_NORWEGIAN
    return PHASE_NAMES_ENGLISH

# Function to get phase configurations based on language
def get_phase_configs(language: str) -> Dict[str, Dict]:
    if language == "no":
        return PHASE_CONFIGS_NORWEGIAN
    return PHASE_CONFIGS_ENGLISH

# Function to get slide template based on language
def get_slide_template(slide_type: str, language: str) -> Optional[Dict]:
    if language == "no":
        base_template = SLIDE_TYPES_NORWEGIAN.get(slide_type)
    else:
        base_template = SLIDE_TYPES_ENGLISH.get(slide_type)
    
    if not base_template:
        return None

    lang_config = LANGUAGE_CONFIGS.get(language, LANGUAGE_CONFIGS['en'])
    template = base_template.copy()
    template['language'] = lang_config
    template['original_language'] = language
    return template

# Function to get phase configuration based on language
def get_phase_config(phase_name: str, language: str = "en") -> Optional[Dict]:
    phase_configs = get_phase_configs(language)
    return phase_configs.get(phase_name)

# Function to get system message based on language
def get_system_message(message_type: str, language: str = "en", **kwargs) -> str:
    message_template = SYSTEM_MESSAGES.get(message_type, {}).get(language)
    if not message_template:
        message_template = SYSTEM_MESSAGES.get(message_type, {}).get('en', "")
    return message_template.format(**kwargs)


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