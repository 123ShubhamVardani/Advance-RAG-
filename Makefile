# Makefile for LangChain Chatbot with RAG & Voice

.PHONY: help setup install run clean test lint format

# Default target
help:
	@echo "LangChain Chatbot with RAG & Voice - Available commands:"
	@echo ""
	@echo "  setup     - Set up the development environment"
	@echo "  install   - Install dependencies"
	@echo "  run       - Run the Streamlit application"
	@echo "  clean     - Clean temporary files and cache"
	@echo "  test      - Run tests (if available)"
	@echo "  lint      - Run code linting"
	@echo "  format    - Format code with black"
	@echo ""

# Set up development environment
setup:
	python setup.py

# Install dependencies
install:
	pip install -r requirements.txt

# Run the application
run:
	streamlit run app.py

# Clean temporary files
clean:
	@echo "Cleaning temporary files..."
	@if exist __pycache__ rmdir /s /q __pycache__
	@if exist *.pyc del /q *.pyc
	@if exist *.pyo del /q *.pyo
	@if exist .pytest_cache rmdir /s /q .pytest_cache
	@if exist chat_log.txt del /q chat_log.txt
	@if exist startup_debug.log del /q startup_debug.log
	@if exist temp.* del /q temp.*
	@echo "✅ Cleanup completed"

# Run linting
lint:
	@echo "Running code linting..."
	@python -m pylint app.py main.py || echo "Pylint completed with warnings"

# Format code
format:
	@echo "Formatting code..."
	@python -m black app.py main.py setup.py || echo "Black formatter not installed"
