# 👁️ ARGUS - Hygiene Market Intelligence System

Strategic market observation and supply chain simulation platform for the Hygiene & Personal Care industry.

## Overview

ARGUS is a Streamlit-based intelligence dashboard designed to compile financial data, analyze competitive landscapes, and simulate supply chain flows for key industry players like Kimberly-Clark, Essity, and Ontex.

## Features

- **Market Dashboard**: Real-time financial metrics (Stock Price, Market Cap) via Yahoo Finance API.
- **AI Strategic Analyst**: RAG (Retrieval-Augmented Generation) engine powered by OpenAI or Perplexity to answer strategic questions using company transcripts and reports.
- **Supply Chain Simulator**: Interactive map and Sankey diagrams visualizing manufacturing and distribution flows across North America.
- **Knowledge Base**: Integrated document viewer for earnings call transcripts and annual reports.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/argus-financial-compiler.git
   cd argus-financial-compiler
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

To use the AI Analyst features, you need to configure your API keys.

1. **Create a secrets file:**
   Create a file named `.streamlit/secrets.toml` in the project root.

2. **Add your keys:**
   ```toml
   # .streamlit/secrets.toml
   OPENAI_API_KEY = "sk-..."
   PERPLEXITY_API_KEY = "pplx-..."
   ```

   *Note: The application also supports entering keys manually in the UI if you prefer.*

## Usage

Run the application locally:

```bash
streamlit run app.py
```

### Access Control
The application is protected by a simple demo security PIN.
- **PIN**: `8191`

## Project Structure

- `app.py`: Main application entry point.
- `utils/`: Helper modules for data loading (`data_loader.py`) and RAG logic (`rag_engine.py`).
- `documents/`: Directory to store PDF/TXT transcripts for the Knowledge Base.
- `transcripts/`: (Legacy) Additional transcript storage.

## Disclaimer
This tool is for educational and analytical purposes. Financial data is sourced from third-party APIs and may be delayed.
