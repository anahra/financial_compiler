import os
import numpy as np
from openai import OpenAI
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pypdf import PdfReader

class RAGEngine:
    def __init__(self, transcripts_dir, api_key, provider="OpenAI"):
        self.transcripts_dir = transcripts_dir
        self.api_key = api_key
        self.provider = provider
        
        # Configure Client
        if provider == "Perplexity":
            self.client = OpenAI(
                api_key=api_key, 
                base_url="https://api.perplexity.ai"
            )
            self.model_name = "sonar-pro"
        else:
            self.client = OpenAI(api_key=api_key)
            self.model_name = "gpt-3.5-turbo"

        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = None
        self.chunks = []
        
    def process_documents(self):
        """Loads documents (txt, pdf), splits them, and creates a TF-IDF index."""
        if not os.path.exists(self.transcripts_dir):
            return "Documents directory not found."

        all_text = []
        for root, dirs, files in os.walk(self.transcripts_dir):
            for filename in files:
                filepath = os.path.join(root, filename)
                try:
                    text = ""
                    if filename.lower().endswith(".txt"):
                        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                            text = f.read()
                            # Basic cleanup for common scraping artifacts (like the ones from Cloudflare)
                            if "<html" in text.lower() and "401 authorization required" in text.lower():
                                print(f"Skipping blocked file: {filename}")
                                text = ""  # Skip this file content
                            elif "<!doctype html>" in text.lower() or "<html" in text.lower():
                                # Very rough heuristic: if it looks like raw HTML and not a transcript summary
                                # we might want to strip tags or just skip if it's junk.
                                # For now, let's just warn and maybe try to start after the <body> tag if simple
                                # or better, just rely on our manually created clean summaries
                                # But specifically for the error user saw:
                                if "challenge-platform" in text or "401 Authorization Required" in text:
                                     text = ""
                    elif filename.lower().endswith(".pdf"):
                        reader = PdfReader(filepath)
                        for page in reader.pages:
                            text += page.extract_text() + "\n"
                    
                    if text:
                        all_text.append({"filename": filename, "text": text})
                except Exception as e:
                    print(f"Skipping {filename}: {e}")

        if not all_text:
            return "No documents found in the directory."

        # Chunking Strategy
        self.chunks = []
        chunk_size = 1000  # characters
        overlap = 100

        raw_chunks = []
        for doc in all_text:
            text = doc["text"]
            for i in range(0, len(text), chunk_size - overlap):
                chunk_text = text[i:i + chunk_size]
                self.chunks.append(f"Source: {doc['filename']}\n\n{chunk_text}")
                raw_chunks.append(chunk_text)

        if not self.chunks:
            return "Documents were empty."

        # TF-IDF Vectorization
        try:
            self.tfidf_matrix = self.vectorizer.fit_transform(raw_chunks)
            return f"Successfully processed {len(all_text)} documents into {len(self.chunks)} chunks."
        except Exception as e:
            return f"Error creating index: {str(e)}"

    def answer_question(self, query):
        """Answers a question based on the processed documents."""
        if self.tfidf_matrix is None:
            return "Please process the documents first."
        
        try:
            # Transform query
            query_vec = self.vectorizer.transform([query])
            
            # Compute Similarities
            similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
            
            # Get Top K indices
            k = 5
            related_docs_indices = similarities.argsort()[:-k-1:-1]
            
            # Retrieve context
            context_chunks = [self.chunks[i] for i in related_docs_indices]
            context = "\n\n---\n\n".join(context_chunks)

            # Generate Answer
            if self.provider == "Perplexity":
                system_prompt = """You are a strategic financial analyst assistant. 
                Your goal is to answer the user's question.
                Use the provided context from earnings call transcripts, reports, and presentations as your primary source.
                However, if the answer is not in the context, you MAY use your internal knowledge search to answer strategic questions about the company's history.
                Focus on strategic initiatives, supply chain choices, operational impacts, and forward-looking statements.
                Reference the source company/file when possible."""
            else:
                system_prompt = """You are a strategic financial analyst assistant. 
                Your goal is to answer the user's question based ONLY on the provided context from earnings call transcripts, reports, and presentations.
                Focus on strategic initiatives, supply chain choices, operational impacts, and forward-looking statements.
                If the answer is not in the context, say so.
                Reference the source company/file when possible."""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
            ]

            chat_response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.3
            )

            return chat_response.choices[0].message.content
        except Exception as e:
            return f"Error answering question: {str(e)}"
