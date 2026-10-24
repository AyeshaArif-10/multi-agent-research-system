'''from agents import build_reader_agent , build_search_agent , writer_chain , critic_chain

def run_research_pipeline(topic : str) -> dict:

    state = {}

    #search agent working 
    print("\n"+" ="*50) 
    print("step 1 - search agent is working ...")
    print("="*50)

    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages" : [("user", f"Find recent, reliable and detailed information about: {topic}")]
    })
    state["search_results"] = search_result['messages'][-1].content #-1 last message

    print("\n search result ",state['search_results'])

    #step 2 - reader agent 
    print("\n"+" ="*50)
    print("step 2 - Reader agent is scraping top resources ...")
    print("="*50)

    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_results'][:800]}"
        )]
    })

    state['scraped_content'] = reader_result['messages'][-1].content

    print("\nscraped content: \n", state['scraped_content'])

    #step 3 - writer chain 

    print("\n"+" ="*50)
    print("step 3 - Writer is drafting the report ...")
    print("="*50)

    research_combined = (
        f"SEARCH RESULTS : \n {state['search_results']} \n\n"
        f"DETAILED SCRAPED CONTENT : \n {state['scraped_content']}"
    )

    state["report"] = writer_chain.invoke({
        "topic" : topic,
        "research" : research_combined
    })

    print("\n Final Report\n",state['report'])

    #critic report 

    print("\n"+" ="*50)
    print("step 4 - critic is reviewing the report ")
    print("="*50)

    state["feedback"] = critic_chain.invoke({
        "report":state['report']
    })

    print("\n critic report \n", state['feedback'])

    return state



if __name__ == "__main__":
    topic = input("\n Enter a research topic : ")
    run_research_pipeline(topic)'''








from agents import (
    build_reader_agent,
    build_search_agent,
    writer_chain,
    critic_chain
)

import traceback


def run_research_pipeline(topic: str) -> dict:
    state = {}

    # STEP 1: SEARCH AGENT
    try:
        print("\n" + "=" * 50, flush=True)
        print("STEP 1 - Search Agent is working...", flush=True)
        print("=" * 50, flush=True)

        print("Building Search Agent...", flush=True)
        search_agent = build_search_agent()

        print("Search Agent initialized successfully.", flush=True)
        print("Searching for information. Please wait...", flush=True)

        search_result = search_agent.invoke({
            "messages": [
                (
                    "user",
                    f"Find recent, reliable and detailed information about: {topic}"
                )
            ]
        })

        messages = search_result.get("messages", [])

        if not messages:
            raise ValueError("Search Agent returned no messages.")

        state["search_results"] = messages[-1].content

        if not state["search_results"]:
            raise ValueError("Search Agent returned empty content.")

        print("\nSEARCH RESULTS:\n", state["search_results"], flush=True)

    except Exception:
        print("\nERROR IN SEARCH AGENT:", flush=True)
        traceback.print_exc()
        return {"error": "Search Agent failed."}

    # STEP 2: READER AGENT
    try:
        print("\n" + "=" * 50, flush=True)
        print("STEP 2 - Reader Agent is scraping resources...", flush=True)
        print("=" * 50, flush=True)

        reader_agent = build_reader_agent()

        reader_result = reader_agent.invoke({
            "messages": [
                (
                    "user",
                    f"Based on the following search results about '{topic}', "
                    f"identify a relevant URL and scrape it for detailed content.\n\n"
                    f"Search Results:\n{state['search_results'][:800]}"
                )
            ]
        })

        reader_messages = reader_result.get("messages", [])

        if not reader_messages:
            raise ValueError("Reader Agent returned no messages.")

        state["scraped_content"] = reader_messages[-1].content

        if not state["scraped_content"]:
            raise ValueError("Reader Agent returned empty content.")

        print(
            "\nSCRAPED CONTENT:\n",
            state["scraped_content"],
            flush=True
        )

    except Exception:
        print("\nERROR IN READER AGENT:", flush=True)
        traceback.print_exc()
        return {"error": "Reader Agent failed."}

    # STEP 3: WRITER
    try:
        print("\n" + "=" * 50, flush=True)
        print("STEP 3 - Writer is drafting the report...", flush=True)
        print("=" * 50, flush=True)

        research_combined = (
            f"SEARCH RESULTS:\n{state['search_results']}\n\n"
            f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
        )

        state["report"] = writer_chain.invoke({
            "topic": topic,
            "research": research_combined
        })

        print("\nFINAL REPORT:\n", state["report"], flush=True)

    except Exception:
        print("\nERROR IN WRITER:", flush=True)
        traceback.print_exc()
        return {"error": "Writer failed."}

    # STEP 4: CRITIC
    try:
        print("\n" + "=" * 50, flush=True)
        print("STEP 4 - Critic is reviewing the report...", flush=True)
        print("=" * 50, flush=True)

        state["feedback"] = critic_chain.invoke({
       "topic": topic,
       "research": str(state.get("research", state.get("report", state.get("search_results", "No research available")))),
       "report": state["report"]})

        print("\nCRITIC FEEDBACK:\n", state["feedback"], flush=True)

    except Exception:
        print("\nERROR IN CRITIC:", flush=True)
        traceback.print_exc()
        return {"error": "Critic failed."}

    # PIPELINE COMPLETED
    print("\n" + "=" * 50, flush=True)
    print("RESEARCH PIPELINE COMPLETED SUCCESSFULLY!", flush=True)
    print("=" * 50, flush=True)

    return state


if __name__ == "__main__":
    topic = input("\nEnter a research topic: ").strip()

    if topic:
        result = run_research_pipeline(topic)

        if "error" in result:
            print("\nPipeline stopped:", result["error"])
        else:
            print("\nAll steps completed successfully.")
    else:
        print("Please enter a research topic.")
