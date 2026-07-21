"""
LLM Integration Service

Handles context building, prompt engineering, and OpenRouter API integration
using the existing semantic retrieval and knowledge graph outputs.
"""
import streamlit as st
from openai import OpenAI
import time
from services.config_service import load_config

def build_context(retrieval_results: list, subgraph) -> str:
    """
    Constructs a structured text context from the FAISS chunks and NetworkX subgraph.
    """
    context_parts = []
    
    # 1. Add Semantic Chunks
    if retrieval_results:
        context_parts.append("--- RETRIEVED DOCUMENTS ---")
        for res in retrieval_results:
            doc = res.get("Document_Name", "Unknown")
            page = res.get("Page_Number", "N/A")
            text = res.get("Chunk_Text", "")
            context_parts.append(f"[Source: {doc}, Page: {page}]\n{text}\n")
            
    # 2. Add Knowledge Graph Context
    if subgraph and subgraph.number_of_nodes() > 0:
        context_parts.append("--- KNOWLEDGE GRAPH ENTITIES & RELATIONSHIPS ---")
        edges_added = 0
        for source, target, data in subgraph.edges(data=True):
            rel = data.get("type", "related_to")
            context_parts.append(f"Entity '{source}' -> {rel} -> Entity '{target}'")
            edges_added += 1
            if edges_added >= 50:
                context_parts.append("... (additional relationships truncated)")
                break
                
    if not context_parts:
        return "No context available."
        
    return "\n".join(context_parts)

def build_prompt(context: str, question: str) -> str:
    """
    Constructs the final prompt string using a strict SYSTEM/CONTEXT/USER format.
    """
    prompt = f"""You are the NEXUS AI Enterprise Industrial Copilot.
You provide highly accurate, professional, and concise answers based strictly on the provided context.
If the context does not contain the answer, state that you do not have enough information. Do not hallucinate.

--- CONTEXT ---
{context}

--- USER QUESTION ---
{question}

Provide your answer below in clean markdown format:
"""
    return prompt

def generate_answer(context: str, question: str) -> tuple:
    """
    Calls OpenRouter via the OpenAI client to generate an answer.
    Returns (answer_string, latency_seconds, tokens_used).
    """
    config = load_config()
    api_key = config.get("OPENROUTER_API_KEY")
    
    if not api_key or api_key == "dummy_key":
        return ("⚠ **Configuration Error:** OpenRouter API key is missing or invalid. Please check your `.env` file.", 0.0, 0)
        
    prompt_text = build_prompt(context, question)
    
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        
        start_time = time.time()
        
        response = client.chat.completions.create(
            model="google/gemini-2.5-flash",
            messages=[
                {"role": "user", "content": prompt_text}
            ],
            temperature=0.0,
            max_tokens=1024,
            timeout=30.0
        )
        
        end_time = time.time()
        latency = round(end_time - start_time, 2)
        
        answer = response.choices[0].message.content
        tokens = response.usage.total_tokens if response.usage else 0
        
        return (answer, latency, tokens)
        
    except Exception as e:
        return (f"⚠ **API Error:** Failed to generate response from OpenRouter.\n\nDetails: {str(e)}", 0.0, 0)
