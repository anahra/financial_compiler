def load_css():
    return """
    <style>
        /* Main Background */
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #e2e8f0;
            font-family: 'Inter', sans-serif;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: rgba(15, 23, 42, 0.95);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }

        /* Headings */
        h1, h2, h3 {
            color: #f8fafc !important;
            font-weight: 700;
        }
        h1 {
            background: linear-gradient(90deg, #60a5fa, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            padding-bottom: 1rem;
        }

        /* Cards/Containers */
        .metric-card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 1.5rem;
            backdrop-filter: blur(10px);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }
        .metric-card:hover {
            transform: translateY(-2px);
            border-color: #60a5fa;
            background: rgba(255, 255, 255, 0.08);
        }

        /* Custom Buttons */
        .stButton > button {
            background: linear-gradient(90deg, #3b82f6, #2563eb);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
            transform: translateY(-1px);
        }

        /* Dataframes */
        [data-testid="stDataFrame"] {
            background: rgba(255, 255, 255, 0.02);
            border-radius: 10px;
            padding: 1rem;
        }
    </style>
    """
