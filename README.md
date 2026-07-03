# 🤖 Self-Correcting Research Agent (LangGraph + Groq + Tavily + Streamlit)

An enterprise-grade autonomous research workflow built using **LangGraph** state machines. This system addresses AI hallucinations by implementing a self-correcting logic loop that evaluates and audits its own gathered information before finalizing reports.

🔗 **Live Platform Application**: [Click Here to Run the Live App](YAHAN_APNA_STREAMLIT_LIVE_LINK_PASTE_KARO)

## 🚀 Key Features
- **State Machine Architecture**: Designed using conditional nodes and edges with LangGraph for predictable, structured execution.
- **Autonomous Self-Correction**: Implements an evaluator (grader node) that scores LLM output and triggers secondary research loops if quality criteria aren't met.
- **Lightning-Fast Open Source Inference**: Powered by **Groq Cloud Engine** running the `llama-3.3-70b-versatile` model.
- **Production-Grade Data Gathering**: Uses **Tavily AI Search API** for deep, optimized web research loops.
- **Interactive Dashboard**: Built on Streamlit to visualize the multi-agent system execution flow dynamically.

## 🏗️ System Architecture Flow
```text
[START] ──> [Research Node (Tavily)] ──> [Writer Node (Draft Report)]
                                                    │
                                                    ▼
[END] <─── [Good Quality Target] <─── [Conditional Grader Node] ───> [Bad Quality] ──> [Fix & Re-write Node]
```

## 🛠️ Tech Stack & Frameworks
- **Core Engine**: Python 3.12+
- **Orchestration**: LangGraph
- **LLM Driver**: Groq Cloud (Llama 3.3)
- **Data Ingestion**: Tavily AI Search
- **Frontend Dashboard**: Streamlit

## 💻 Local Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com
   cd self-correcting-agent-langgraph
   ```

2. **Install all dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Create a `.env` file in the root directory and insert your secret keys:
   ```env
   GROQ_API_KEY=your_groq_api_key
   TAVILY_API_KEY=your_tavily_api_key
   ```

4. **Launch the platform application:**
   ```bash
   python -m streamlit run app.py
   ```
