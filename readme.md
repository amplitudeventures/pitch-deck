# AI Pitch Deck Generator

An AI-powered Streamlit application that generates professional pitch decks by analyzing company documents. The system supports both Norwegian and English content generation, with built-in editing capabilities and export options to PDF and Canva.

## 🌟 Features

### Document Processing
- Multi-file upload support (PDF, DOCX, TXT)
- Intelligent content extraction and analysis
- Document embedding using Pinecone vector store
- Automatic content categorization

### Content Generation
- AI-powered slide content creation
- Bilingual support (Norwegian/English)
- Consistent tone and style
- Professional formatting

### Editing Capabilities
- Structured feedback system
- Slide-specific editing options
- Real-time AI-assisted revisions
- Version tracking

### Export Options
- Interactive HTML preview
- Professional PDF generation
- Canva export preparation
- Consistent styling

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- OpenAI API key
- Pinecone API key
- Virtual environment (recommended)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-pitch-deck-generator.git
cd ai-pitch-deck-generator
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
```

5. Run the application:
```bash
streamlit run main.py
```

## 📁 Project Structure

```
ai-pitch-deck-generator/
├── main.py                 # Main application file
├── messages.py            # Configuration and message templates
├── vector_store.py        # Document storage and retrieval
├── requirements.txt       # Project dependencies
├── README.md             # Project documentation
├── templates/            # HTML templates
│   └── pitch_deck.html   # Base template for deck
├── static/              # Static assets
│   ├── css/            # Stylesheets
│   └── js/             # JavaScript files
└── tests/              # Test files
```

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key
- `PINECONE_API_KEY`: Your Pinecone API key

### Language Support
- Default: Norwegian (no)
- Alternative: English (en)
- Language can be switched per slide

## 💡 Usage

1. Create New Project
   - Enter project name
   - System generates unique project ID

2. Upload Documents
   - Support for multiple file types
   - Automatic content extraction
   - Progress tracking

3. Generate Content
   - AI analyzes documents
   - Creates slide content
   - Maintains consistency

4. Edit Content
   - Use structured feedback
   - AI-assisted revisions
   - Real-time updates

5. Preview and Export
   - Interactive HTML preview
   - Generate PDF
   - Export to Canva

## 🎯 Slide Types

- Title Slide
- Introduction
- Team
- Problem Statement
- Solution
- Market Analysis
- Business Model
- Financial Projections
- Ask
- Contact

## 🔒 Security

- Secure API key handling
- Document encryption
- Access control
- Data persistence

## 📊 Performance

- Document processing: ~2-3 seconds per page
- Content generation: ~5-10 seconds per slide
- PDF generation: ~3-5 seconds
- Concurrent user support: Up to 10

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Support

For support, email support@example.com or create an issue in the repository.

## 🙏 Acknowledgments

- OpenAI for GPT models
- Streamlit for framework
- Pinecone for vector storage
- Community contributors

## 🚨 Known Issues

- PDF generation might be slow for large decks
- Limited formatting options in export
- Language detection occasionally needs manual override

## 🗺️ Roadmap

### Version 1.1
- Enhanced language support
- Additional export formats
- Improved editing interface

### Version 1.2
- Custom template support
- Advanced formatting options
- Analytics integration

### Version 2.0
- Multi-user support
- Version control
- Custom design templates

## 📈 Status
- Current Version: 1.0.0
- Status: Beta
- Last Updated: February 2024
