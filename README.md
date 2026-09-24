# Sunbeam Agentic RAG Chatbot

An AI-powered chatbot for the Sunbeam website using web scraping,
RAG, ChromaDB, LangChain agents, and configurable local/cloud LLMs.

## Features

- Sunbeam website scraping using Selenium
- Course information extraction
- About Us information extraction
- Contact information extraction
- Internship information extraction
- JSON-based knowledge snapshot
- Section-level document chunking
- Local vector database using ChromaDB
- Agentic RAG architecture
- Tool-based knowledge retrieval
- Conversation history
- Context-controlled conversation memory
- Local LLM support through LM Studio
- Online Gemini LLM support
- Login system
- Admin controls
- Knowledge index rebuilding
- Streamlit interface

## Architecture

```text
Sunbeam Website
      |
      v
Selenium Scrapers
      |
      v
output.json
      |
      v
Section-Level Chunking
      |
      v
Embeddings
      |
      v
ChromaDB
      |
      v
Agent
      |
      v
RAG Retrieval Tool
      |
      v
Relevant Context
      |
      +----------------+
      |                |
      v                v
 LM Studio          Gemini
      |                |
      +-------+--------+
              |
              v
           Answer