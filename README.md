# 🔎 Multi-Agent Research System

An AI-powered research application that automates the process of gathering information, extracting relevant content, generating structured research reports, and evaluating report quality using multiple specialized AI agents.

Built using **Python, Streamlit, LangChain, LangGraph, and Google Gemini**, the system follows a four-stage workflow:

- **Search Agent:** Searches the web for recent and relevant information using DuckDuckGo.
- **Reader Agent:** Extracts meaningful content from relevant webpages using web scraping.
- **Writer Chain:** Generates a detailed, structured research report using Google Gemini.
- **Critic Chain:** Evaluates the generated report, assigns a score out of 10, and provides constructive feedback.

The application provides an interactive Streamlit interface where users can enter a research topic, monitor the execution of each stage, view the generated report and feedback, and download results in Markdown format.

## ✨ Key Features

- Automated web research using DuckDuckGo.
- Webpage content extraction using Requests and BeautifulSoup.
- Four-stage AI research workflow.
- AI-powered structured report generation.
- Automated report evaluation with scores and feedback.
- Live progress tracking through Streamlit.
- Separate tabs for reports, feedback, search results, and scraped content.
- Downloadable research reports in Markdown format.
- Error handling at individual pipeline stages.
