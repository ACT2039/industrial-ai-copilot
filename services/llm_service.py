"""
LLM Integration Service

Handles context building, prompt engineering, and OpenRouter API integration
using the existing semantic retrieval and knowledge graph outputs.
"""
import streamlit as st
from openai import OpenAI
import time
import re
from services.config_service import load_config

def classify_intent(question: str) -> str:
    """Classifies user query into one of the supported domain intents."""
    q = question.lower()
    if any(k in q for k in ["repair", "fix", "broken", "replace", "fail"]):
        return "Troubleshooting"
    elif any(k in q for k in ["maintain", "maintenance", "service", "clean", "lubricate"]):
        return "Maintenance"
    elif any(k in q for k in ["safe", "hazard", "risk", "warn", "protect", "ppe"]):
        return "Safety"
    elif any(k in q for k in ["inspect", "check", "test", "measure", "verify"]):
        return "Inspection"
    elif any(k in q for k in ["install", "setup", "mount", "configure"]):
        return "Installation"
    else:
        return "Definition"

def build_context(retrieval_results: list, subgraph) -> str:
    """
    Constructs a structured text context from the FAISS chunks and NetworkX subgraph.
    """
    context_parts = []
    
    if retrieval_results:
        context_parts.append("--- RETRIEVED DOCUMENTS ---")
        for res in retrieval_results:
            doc = res.get("Document_Name", "Unknown Document")
            if str(doc).lower() in ["unknown", "unknown document", "nan", ""]:
                doc = "General Industrial Record"
                
            page = res.get("Page_Number", "N/A")
            if str(page).lower() in ["n/a", "unknown", "nan", ""]:
                page = "Section 1"
                
            text = res.get("Chunk_Text", "")
            context_parts.append(f"[Source: {doc}, Page: {page}]\n{text}\n")
            
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

def build_prompt(context: str, question: str, intent: str, is_general_ai: bool = False, conversation_history: list = None) -> str:
    """
    Constructs the final prompt string using domain-specific templates.
    """
    # ... (template logic remains same) ...
    if intent == "Troubleshooting":
        template = """### Executive Summary\n### Symptoms Identified\n### Root Cause Analysis\n### Resolution Steps\n### Safety Considerations\n### Referenced Documents\n### Confidence Assessment"""
    elif intent == "Maintenance":
        template = """### Executive Summary\n### Maintenance Requirements\n### Tools & Materials\n### Step-by-Step Procedure\n### Safety Considerations\n### Referenced Documents\n### Confidence Assessment"""
    elif intent == "Safety":
        template = """### Executive Summary\n### Primary Hazards\n### Required PPE & Precautions\n### Emergency Protocols\n### Referenced Documents\n### Confidence Assessment"""
    elif intent == "Inspection":
        template = """### Executive Summary\n### Inspection Criteria\n### Tolerance & Thresholds\n### Remedial Actions\n### Safety Considerations\n### Referenced Documents\n### Confidence Assessment"""
    else: # Definition / Default
        template = """### Executive Summary\n### Detailed Explanation\n### Recommended Actions\n### Safety Considerations\n### Referenced Documents\n### Confidence Assessment"""

    if is_general_ai:
        system_instruction = "You are the NEXUS AI Enterprise Industrial Copilot. You may use your general world knowledge in combination with the provided context to answer the user's question. If the context is missing, use your general knowledge."
    else:
        system_instruction = "You are the NEXUS AI Enterprise Industrial Copilot. You provide highly accurate, professional, and concise answers based STRICTLY on the provided context. If the context does not contain the answer, state that you do not have enough information. Do not hallucinate."

    # Build History String
    history_str = "No previous conversation."
    if conversation_history and len(conversation_history) > 0:
        history_parts = []
        for turn in conversation_history:
            history_parts.append(f"User: {turn.get('query')}\nAssistant: {turn.get('answer')}")
        history_str = "\n\n".join(history_parts)

    prompt = f"""{system_instruction}

You MUST structure your final response exactly using these Markdown headers:

{template}

### Follow-up Questions
(Generate exactly 3 intelligent follow-up questions as bullet points based on the current context)

### Explore Related Topics
(Generate exactly 3 intelligent related topics as bullet points that broaden the scope of the current context)

--- CONTEXT ---
{context}

--- CONVERSATION HISTORY ---
{history_str}

--- CURRENT USER QUESTION ---
{question}

Provide your structured answer below:
"""
    return prompt

def generate_answer(context: str, question: str, is_general_ai: bool = False, conversation_history: list = None) -> tuple:
    """
    Calls OpenRouter via the OpenAI client to generate an answer.
    Returns (answer_string, latency_seconds, tokens_used, intent_used).
    """
    config = load_config()
    api_key = config.get("OPENROUTER_API_KEY")
    
    intent = classify_intent(question)
    
    if not api_key or api_key == "dummy_key":
        return ("⚠ **Configuration Error:** OpenRouter API key is missing or invalid. Please check your `.env` file.", 0.0, 0, intent)
        
    prompt_text = build_prompt(context, question, intent, is_general_ai, conversation_history)
    
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
            max_tokens=2048,
            timeout=45.0
        )
        
        end_time = time.time()
        latency = round(end_time - start_time, 2)
        
        answer = response.choices[0].message.content
        tokens = response.usage.total_tokens if response.usage else 0
        
        return (answer, latency, tokens, intent)
        
    except Exception as e:
        return (f"⚠ **API Error:** Failed to generate response from OpenRouter.\n\nDetails: {str(e)}", 0.0, 0, intent)

def generate_smart_title(query: str) -> str:
    """Generates a short, professional title for a new investigation based on the first query."""
    config = load_config()
    api_key = config.get("OPENROUTER_API_KEY")
    if not api_key or api_key == "dummy_key":
        words = query.split()
        return " ".join(words[:4]).title() + " Investigation"
        
    try:
        client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
        response = client.chat.completions.create(
            model="google/gemini-2.5-flash",
            messages=[
                {"role": "system", "content": "You are a professional engineering assistant. Generate a 3-5 word concise title for the following query. Output ONLY the title, no quotes, no extra text. Example: Compressor Oil Inspection."},
                {"role": "user", "content": query}
            ],
            temperature=0.3,
            max_tokens=15,
            timeout=10.0
        )
        title = response.choices[0].message.content.strip().strip('"').strip("'")
        return title
    except:
        words = query.split()
        return " ".join(words[:4]).title() + " Investigation"
