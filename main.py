#!/usr/bin/env python3
"""
Main entry point for the LangChain Chatbot with RAG & Voice
"""

import subprocess
import sys
import os

def main():
    """Run the Streamlit app"""
    try:
        # Check if streamlit is available
        import streamlit
        print("🚀 Starting LangChain Chatbot with RAG & Voice...")
        
        # Run the Streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            os.path.join(os.path.dirname(__file__), "app.py"),
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false"
        ])
        
    except ImportError:
        print("❌ Streamlit not found. Please install requirements:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
