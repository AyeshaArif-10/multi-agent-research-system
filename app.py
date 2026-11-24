
"""
Streamlit UI for the Multi-Agent Research System.

Run with:
    streamlit run app.py
"""

import time
import traceback
import re

import streamlit as st

from agents import (
    build_reader_agent,
    build_search_agent,
    writer_chain,
    critic_chain,
    llm,
)

from tools import web_search, scrape_url


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
    """Normalize LLM message content into plain text."""

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

    defaults = {
        "results": None,
        "topic": "",
        "error": None,
        "elapsed": None
    }

    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


init_state()


# ----------------------------------------------------------------------------
# Pipeline
# ----------------------------------------------------------------------------

def run_pipeline_ui(topic: str):

    state = {}
    start = time.time()

    progress = st.progress(0, text="Starting pipeline...")

    # STEP 1: SEARCH


    # STEP 1: SEARCH
    # Direct DuckDuckGo search without Gemini

    with st.status(
        "🔍 Step 1 — Searching the web...",
        expanded=True
    ) as status:

        try:

            st.write("Searching DuckDuckGo...")

            search_results = web_search(topic)

            if (
                not search_results
                or search_results.startswith("Web search failed:")
                or search_results.startswith("No search results")
            ):
                raise ValueError(
                    f"Search failed: {search_results}"
                )

            state["search_results"] = search_results

            st.write("Search results collected successfully.")

            status.update(
                label="✅ Step 1 — Search complete",
                state="complete",
                expanded=False
            )

        except Exception:

            status.update(
                label="❌ Step 1 — Search failed",
                state="error"
            )

            st.code(traceback.format_exc())

            return {"error": "Search failed."}

    progress.progress(25, text="Search complete")


    # STEP 2: READER
    # Direct webpage scraping without Gemini

    with st.status(
        "📄 Step 2 — Reader is scraping resources...",
        expanded=True
    ) as status:

        try:

            st.write("Extracting URLs from search results...")

            urls = re.findall(
                r'https?://[^\s<>"\']+',
                state["search_results"]
            )

            # Remove duplicate URLs
            urls = list(dict.fromkeys(urls))

            if not urls:
                raise ValueError(
                    "No URLs found in the search results."
                )

            scraped_pages = []

            # Scrape up to three webpages
            for url in urls[:3]:

                st.write(f"Scraping: {url}")

                content = scrape_url(url)

                if (
                    content
                    and not content.startswith("Webpage reading failed:")
                ):

                    scraped_pages.append(
                        f"SOURCE: {url}\n\n{content}"
                    )

            if not scraped_pages:

                raise ValueError(
                    "Could not scrape any webpage from the search results."
                )

            state["scraped_content"] = "\n\n".join(
                scraped_pages
            )

            status.update(
                label="✅ Step 2 — Scraping complete",
                state="complete",
                expanded=False
            )

        except Exception:

            status.update(
                label="❌ Step 2 — Reader failed",
                state="error"
            )

            st.code(traceback.format_exc())

            return {"error": "Reader failed."}

    progress.progress(50, text="Scraping complete")

    # STEP 3: WRITER

    with st.status(
        "✍️ Step 3 — Writer is drafting the report...",
        expanded=True
    ) as status:

        try:

            state["research"] = (
                f"SEARCH RESULTS:\n{state['search_results']}\n\n"
                f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
            )

            report = writer_chain.invoke(
                {
                    "topic": topic,
                    "research": state["research"]
                }
            )

            state["report"] = to_text(
                getattr(report, "content", report)
            )

            status.update(
                label="✅ Step 3 — Report drafted",
                state="complete",
                expanded=False
            )

        except Exception:

            status.update(
                label="❌ Step 3 — Writer failed",
                state="error"
            )

            st.code(traceback.format_exc())

            return {"error": "Writer failed."}

    progress.progress(75, text="Report drafted")

    # STEP 4: CRITIC

    with st.status(
        "🧐 Step 4 — Critic is reviewing the report...",
        expanded=True
    ) as status:

        try:

            feedback = critic_chain.invoke(
                {
                    "topic": topic,
                    "research": state["research"],
                    "report": state["report"],
                }
            )

            state["feedback"] = to_text(
                getattr(feedback, "content", feedback)
            )

            status.update(
                label="✅ Step 4 — Review complete",
                state="complete",
                expanded=False
            )

        except Exception:

            status.update(
                label="❌ Step 4 — Critic failed",
                state="error"
            )

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

    st.caption(
        "A multi-agent pipeline that searches, reads, writes and critiques."
    )

    st.markdown("### How it works")

    st.markdown(
        """
1. **Search Agent** finds recent sources
2. **Reader** extracts webpage content
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

st.write(
    "Enter a topic and let the agents do the research for you."
)


# ----------------------------------------------------------------------------
# TEMPORARY TEST 1: GEMINI API
# ----------------------------------------------------------------------------

if st.button("Test Gemini API"):

    try:

        with st.spinner("Testing Gemini connection..."):

            response = llm.invoke(
                "Explain artificial intelligence in one sentence."
            )

        st.success("Gemini API is working!")

        st.write(response.content)

    except Exception as e:

        st.error(
            f"Gemini API failed: {type(e).__name__}: {str(e)}"
        )


# ----------------------------------------------------------------------------
# TEMPORARY TEST 2: GEMINI TOOL CALLING
# ----------------------------------------------------------------------------

if st.button("Test Gemini Tool Calling"):

    try:

        with st.spinner("Testing Gemini tool calling..."):

            llm_with_tools = llm.bind_tools([web_search])

            response = llm_with_tools.invoke(
                "Search the web for the latest developments in artificial intelligence."
            )

        st.success("Gemini tool calling is working!")

        st.write(response.content)

        if response.tool_calls:

            st.write("Tool calls detected:")

            st.write(response.tool_calls)

    except Exception as e:

        st.error(
            f"Tool calling failed: {type(e).__name__}: {str(e)}"
        )


# ----------------------------------------------------------------------------
# TEMPORARY TEST 3: DUCKDUCKGO SEARCH
# ----------------------------------------------------------------------------

if st.button("Test DuckDuckGo Search"):

    try:

        with st.spinner("Searching DuckDuckGo..."):

            result = web_search(
                "latest developments in artificial intelligence 2026"
            )

        st.success("DuckDuckGo search completed!")

        st.text(result)

    except Exception as e:

        st.error(
            f"Search failed: {type(e).__name__}: {str(e)}"
        )


# ----------------------------------------------------------------------------
# TEMPORARY TEST 4: SEARCH AGENT
# ----------------------------------------------------------------------------

if st.button("Test Search Agent"):

    try:

        search_agent = build_search_agent()

        with st.spinner("Inspecting Search Agent execution..."):

            for step in search_agent.stream(
                {
                    "messages": [
                        (
                            "user",
                            "Search for recent developments in artificial intelligence."
                        )
                    ]
                },
                config={"recursion_limit": 10},
                stream_mode="updates"
            ):

                st.write("Execution step:")
                st.write(step)

        st.success("Search Agent execution finished!")

    except Exception as e:

        st.error(
            f"Search Agent failed: {type(e).__name__}: {str(e)}"
        )

        st.code(traceback.format_exc())


# ----------------------------------------------------------------------------
# TEMPORARY TEST 5: WEBPAGE SCRAPER
# ----------------------------------------------------------------------------

if st.button("Test Webpage Scraper"):

    try:

        with st.spinner("Scraping webpage..."):

            result = scrape_url(
                "https://www.ibm.com/think/news/ai-tech-trends-2026"
            )

        if result.startswith("Webpage reading failed:"):

            st.error(result)

        elif not result.strip():

            st.warning("The scraper returned empty content.")

        else:

            st.success("Webpage scraper is working!")

            st.write("Extracted webpage content:")

            st.text(result[:3000])

    except Exception as e:

        st.error(
            f"Scraper failed: {type(e).__name__}: {str(e)}"
        )

        st.code(traceback.format_exc())


# ----------------------------------------------------------------------------
# TEMPORARY TEST 6: READER AGENT
# ----------------------------------------------------------------------------

if st.button("Test Reader Agent"):

    try:

        with st.spinner("Testing Reader Agent..."):

            reader_agent = build_reader_agent()

            result = reader_agent.invoke(
                {
                    "messages": [
                        (
                            "user",
                            "Visit this URL and extract its important information: "
                            "https://www.ibm.com/think/news/ai-tech-trends-2026"
                        )
                    ]
                },
                config={"recursion_limit": 10}
            )

        st.success("Reader Agent completed!")

        st.write(result)

    except Exception as e:

        st.error(
            f"Reader Agent failed: {type(e).__name__}: {str(e)}"
        )

        st.code(traceback.format_exc())


# ----------------------------------------------------------------------------
# RESEARCH FORM
# ----------------------------------------------------------------------------

with st.form("research_form", clear_on_submit=False):

    topic_input = st.text_input(
        "Research topic",
        value=st.session_state.topic,
        placeholder="e.g. Latest advances in solid-state batteries",
    )

    submitted = st.form_submit_button(
        "🚀 Run research",
        type="primary"
    )


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

    st.error(
        f"Pipeline stopped: {st.session_state.error}"
    )


# ----------------------------------------------------------------------------
# RESULTS
# ----------------------------------------------------------------------------

results = st.session_state.results

if results:

    st.success(
        f"Research on **{st.session_state.topic}** completed"
        + (
            f" in {st.session_state.elapsed:.1f}s."
            if st.session_state.elapsed
            else "."
        )
    )

    tab_report, tab_feedback, tab_search, tab_scraped = st.tabs(
        [
            "📝 Final Report",
            "🧐 Critic Feedback",
            "🔍 Search Results",
            "📄 Scraped Content"
        ]
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

