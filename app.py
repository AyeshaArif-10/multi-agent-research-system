"""
Streamlit UI for the Multi-Agent Research System.
 
Run with:
    streamlit run app.py
 
Place this file in the same folder as agents.py, pipeline.py and tools.py.
"""
 
import time
import traceback
 
import streamlit as st
 
from agents import (
    build_reader_agent,
    build_search_agent,
    writer_chain,
    critic_chain,
)
 
# ----------------------------------------------------------------------------
# Page config
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Multi-Agent Research System",
    page_icon="🔎",
    layout="wide",
)
 
# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
def to_text(content) -> str:
    """Normalize LLM message content (str or list of blocks) into plain text."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict):
                parts.append(block.get("text", ""))
            else:
                parts.append(getattr(block, "text", str(block)))
        return "\n".join(p for p in parts if p)
    return str(content)
 
 
def last_message_text(result: dict, agent_name: str) -> str:
    messages = result.get("messages", [])
    if not messages:
        raise ValueError(f"{agent_name} returned no messages.")
    text = to_text(messages[-1].content)
    if not text.strip():
        raise ValueError(f"{agent_name} returned empty content.")
    return text
 
 
def init_state():
    defaults = {"results": None, "topic": "", "error": None, "elapsed": None}
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)
 
 
init_state()
 
# ----------------------------------------------------------------------------
# Pipeline (same steps as pipeline.py, but reporting progress to the UI)
# ----------------------------------------------------------------------------
def run_pipeline_ui(topic: str):
    """Runs the 4 steps and updates the Streamlit UI live. Returns state dict."""
    state = {}
    start = time.time()
 
    progress = st.progress(0, text="Starting pipeline...")
 
    # STEP 1: SEARCH
    with st.status("🔍 Step 1 — Search Agent is searching...", expanded=True) as status:
        try:
            st.write("Building Search Agent...")
            search_agent = build_search_agent()
            st.write("Searching for information. Please wait...")
            search_result = search_agent.invoke(
                {
                    "messages": [
                        (
                            "user",
                            f"Find recent, reliable and detailed information about: {topic}",
                        )
                    ]
                }
            )
            state["search_results"] = last_message_text(search_result, "Search Agent")
            status.update(label="✅ Step 1 — Search complete", state="complete", expanded=False)
        except Exception:
            status.update(label="❌ Step 1 — Search Agent failed", state="error")
            st.code(traceback.format_exc())
            return {"error": "Search Agent failed."}
    progress.progress(25, text="Search complete")
 
    # STEP 2: READER
    with st.status("📄 Step 2 — Reader Agent is scraping resources...", expanded=True) as status:
        try:
            reader_agent = build_reader_agent()
            reader_result = reader_agent.invoke(
                {
                    "messages": [
                        (
                            "user",
                            f"Based on the following search results about '{topic}', "
                            f"identify a relevant URL and scrape it for detailed content.\n\n"
                            f"Search Results:\n{state['search_results'][:800]}",
                        )
                    ]
                }
            )
            state["scraped_content"] = last_message_text(reader_result, "Reader Agent")
            status.update(label="✅ Step 2 — Scraping complete", state="complete", expanded=False)
        except Exception:
            status.update(label="❌ Step 2 — Reader Agent failed", state="error")
            st.code(traceback.format_exc())
            return {"error": "Reader Agent failed."}
    progress.progress(50, text="Scraping complete")
 
    # STEP 3: WRITER
    with st.status("✍️ Step 3 — Writer is drafting the report...", expanded=True) as status:
        try:
            state["research"] = (
                f"SEARCH RESULTS:\n{state['search_results']}\n\n"
                f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
            )
            report = writer_chain.invoke({"topic": topic, "research": state["research"]})
            state["report"] = to_text(getattr(report, "content", report))
            status.update(label="✅ Step 3 — Report drafted", state="complete", expanded=False)
        except Exception:
            status.update(label="❌ Step 3 — Writer failed", state="error")
            st.code(traceback.format_exc())
            return {"error": "Writer failed."}
    progress.progress(75, text="Report drafted")
 
    # STEP 4: CRITIC
    with st.status("🧐 Step 4 — Critic is reviewing the report...", expanded=True) as status:
        try:
            feedback = critic_chain.invoke(
                {
                    "topic": topic,
                    "research": state["research"],
                    "report": state["report"],
                }
            )
            state["feedback"] = to_text(getattr(feedback, "content", feedback))
            status.update(label="✅ Step 4 — Review complete", state="complete", expanded=False)
        except Exception:
            status.update(label="❌ Step 4 — Critic failed", state="error")
            st.code(traceback.format_exc())
            return {"error": "Critic failed."}
    progress.progress(100, text="Pipeline completed!")
 
    state["elapsed"] = time.time() - start
    return state
 
 
# ----------------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------------
with st.sidebar:
    st.title("🔎 Research System")
    st.caption("A multi-agent pipeline that searches, reads, writes and critiques.")
 
    st.markdown("### How it works")
    st.markdown(
        """
1. **Search Agent** finds recent sources  
2. **Reader Agent** scrapes a relevant page  
3. **Writer** drafts the report  
4. **Critic** reviews the report
        """
    )
 
    st.divider()
    if st.button("🗑️ Clear results", use_container_width=True):
        st.session_state.results = None
        st.session_state.topic = ""
        st.session_state.error = None
        st.session_state.elapsed = None
        st.rerun()
 
# ----------------------------------------------------------------------------
# Main page
# ----------------------------------------------------------------------------
st.title("Multi-Agent Research System")
st.write("Enter a topic and let the agents do the research for you.")
 
with st.form("research_form", clear_on_submit=False):
    topic_input = st.text_input(
        "Research topic",
        value=st.session_state.topic,
        placeholder="e.g. Latest advances in solid-state batteries",
    )
    submitted = st.form_submit_button("🚀 Run research", type="primary")
 
if submitted:
    topic = topic_input.strip()
    if not topic:
        st.warning("Please enter a research topic.")
    else:
        st.session_state.topic = topic
        st.session_state.results = None
        st.session_state.error = None
 
        result = run_pipeline_ui(topic)
 
        if "error" in result:
            st.session_state.error = result["error"]
        else:
            st.session_state.results = result
            st.session_state.elapsed = result.get("elapsed")
 
if st.session_state.error:
    st.error(f"Pipeline stopped: {st.session_state.error}")
 
# ----------------------------------------------------------------------------
# Results
# ----------------------------------------------------------------------------
results = st.session_state.results
if results:
    st.success(
        f"Research on **{st.session_state.topic}** completed"
        + (f" in {st.session_state.elapsed:.1f}s." if st.session_state.elapsed else ".")
    )
 
    tab_report, tab_feedback, tab_search, tab_scraped = st.tabs(
        ["📝 Final Report", "🧐 Critic Feedback", "🔍 Search Results", "📄 Scraped Content"]
    )
 
    with tab_report:
        st.markdown(results["report"])
        st.download_button(
            "⬇️ Download report (.md)",
            data=results["report"],
            file_name="research_report.md",
            mime="text/markdown",
        )
 
    with tab_feedback:
        st.markdown(results["feedback"])
 
    with tab_search:
        st.markdown(results["search_results"])
 
    with tab_scraped:
        st.markdown(results["scraped_content"])
 
    full_export = (
        f"# Research Report: {st.session_state.topic}\n\n"
        f"{results['report']}\n\n---\n\n"
        f"## Critic Feedback\n\n{results['feedback']}\n\n---\n\n"
        f"## Search Results\n\n{results['search_results']}\n\n---\n\n"
        f"## Scraped Content\n\n{results['scraped_content']}\n"
    )
    st.download_button(
        "⬇️ Download everything (.md)",
        data=full_export,
        file_name="research_full_output.md",
        mime="text/markdown",
    )




