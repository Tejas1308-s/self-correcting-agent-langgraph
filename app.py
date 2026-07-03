import streamlit as st
import os
from dotenv import load_dotenv
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults

# 1. Environment variables load karna
load_dotenv()

# Deep env structural check
if not os.environ.get("TAVILY_API_KEY") and ".env" in os.listdir():
    with open(".env", "r") as f:
        for line in f:
            if "TAVILY_API_KEY" in line:
                os.environ["TAVILY_API_KEY"] = line.split("=")[1].strip().strip('"').strip("'")
            if "GROQ_API_KEY" in line:
                os.environ["GROQ_API_KEY"] = line.split("=")[1].strip().strip('"').strip("'")

st.set_page_config(page_title="Agentic RAG Engine", layout="wide")

class AgentState(TypedDict):
    query: str
    raw_data: str
    grade: str
    final_report: str

# Fast Enterprise Tools Configuration
search_tool = TavilySearchResults(max_results=2)
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1)

# Safely extract text from data layers
def extract_content(results) -> str:
    extracted = []
    if isinstance(results, list):
        for res in results:
            if isinstance(res, dict):
                extracted.append(res.get("content", str(res)))
            else:
                extracted.append(str(res))
    elif isinstance(results, dict):
        extracted.append(results.get("content", str(results)))
    else:
        extracted.append(str(results))
    return "\n".join(extracted)

# Graph Logic Nodes Setup
def research_node(state: AgentState):
    query = state["query"]
    search_results = search_tool.invoke({"query": query})
    context = extract_content(search_results)
    return {"raw_data": context}

def writer_node(state: AgentState):
    prompt = f"Using this data: {state['raw_data']}, write a detailed report about: {state['query']}"
    response = llm.invoke(prompt)
    return {"final_report": response.content}

def grader_node(state: AgentState):
    prompt = f"""
    Analyze this report: '{state['final_report']}'. 
    Does it clearly answer the original question '{state['query']}'? 
    Reply with exactly one word: 'good' if it answers it perfectly, or 'bad' if it lacks deep data.
    Do not add punctuation or extra words.
    """
    response = llm.invoke(prompt)
    grade_result = response.content.strip().lower()
    return {"grade": "good" if "good" in grade_result else "bad"}

def fix_report_node(state: AgentState):
    extra_search = search_tool.invoke({"query": f"{state['query']} deep technical analysis details"})
    extra_context = extract_content(extra_search)
    combined_context = state["raw_data"] + "\n\nAdditional Data:\n" + extra_context
    
    prompt = f"Rewrite this report: {state['final_report']} by integrating this new crucial context: {combined_context}"
    response = llm.invoke(prompt)
    return {"final_report": response.content}

# Workflow Architecture Setup
workflow = StateGraph(AgentState)

workflow.add_node("research", research_node)
workflow.add_node("writer", writer_node)
workflow.add_node("grader", grader_node)
workflow.add_node("fix_report", fix_report_node)

workflow.add_edge(START, "research")
workflow.add_edge("research", "writer")
workflow.add_edge("writer", "grader")

workflow.add_conditional_edges(
    "grader",
    lambda state: state["grade"],
    {
        "good": END,
        "bad": "fix_report"
    }
)
workflow.add_edge("fix_report", END)
app = workflow.compile()

# UI System Layout
st.title("🤖 Self-Correcting LangGraph Research Agent")
st.caption("An autonomous AI workflow that evaluates and self-corrects its own information gathering loops.")

user_query = st.text_input("Enter a complex research topic:", "What are the latest breakthroughs in solid-state EV battery architecture?")

if st.button("Activate Agent Graph", type="primary"):
    with st.spinner("Executing agent logic nodes... Checking quality thresholds..."):
        try:
            initial_state = {"query": user_query}
            final_output = app.invoke(initial_state)
            
            st.success("Workflow completed successfully!")
            st.markdown("### 📋 Final Verified Report:")
            st.markdown(final_output["final_report"])
        except Exception as e:
            st.error(f"Execution Error: {e}")
