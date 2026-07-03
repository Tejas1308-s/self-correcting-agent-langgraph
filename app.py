import streamlit as st
from dotenv import load_dotenv
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults

load_dotenv()

st.set_page_config(page_title="Agentic RAG Engine", layout="wide")

class AgentState(TypedDict):
    query: str
    raw_data: str
    grade: str
    final_report: str

# Stable & Fast Enterprise Search Tool
search_tool = TavilySearchResults(max_results=2)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)

def research_node(state: AgentState):
    query = state["query"]
    # Direct search invoke list handling
    search_results = search_tool.invoke({"query": query})
    context = "\n".join([res.get("content", "") for res in search_results])
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
    """
    response = llm.invoke(prompt)
    grade_result = response.content.strip().lower()
    return {"grade": "good" if "good" in grade_result else "bad"}

def fix_report_node(state: AgentState):
    extra_search = search_tool.invoke({"query": f"{state['query']} deep technical analysis details"})
    extra_context = "\n".join([res.get("content", "") for res in extra_search])
    combined_context = state["raw_data"] + "\n\nAdditional Data:\n" + extra_context
    
    prompt = f"Rewrite this report: {state['final_report']} by integrating this new crucial context: {combined_context}"
    response = llm.invoke(prompt)
    return {"final_report": response.content}

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
