import prompts
import config
from tools import search_web
from state import ResearchState
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

json_parser = JsonOutputParser()
bg_prompt = ChatPromptTemplate.from_messages([("system", prompts.background)])

model = ChatGoogleGenerativeAI(
    google_api_key=config.llm_api_key,
    model=config.model_name,
    temperature=config.temperature
    )

# LLM agents
# ================

def orchestrator_agent(state: ResearchState) -> ResearchState:
    """
    Break down the topic into research questions
    :state: The state of research topic
    :return: Returns the state of research topic
    """
    llm_orchestrator = (bg_prompt + prompts.orchestrator) | model | json_parser
    
    result = llm_orchestrator.invoke({"topic": state["topic"]})
    
    # Extract questions from the JSON response
    state["research_questions"] = result["research_questions"]
    state["current_step"] = "search"
    return state

def search_agent(state: ResearchState) -> ResearchState:
    """
    Search for information on each research question
    :state: The state of research topic
    :return: Returns the state of research topic
    """
    # For now, we'll simulate web search. In a real implementation,
    # you'd integrate with a web search API like Tavily or SerpAPI
    
    llm_search = (bg_prompt + prompts.search) | model | json_parser
    
    search_results = []
    for question in state["research_questions"]:
        web_results = search_web(question)
        
        # Process the web results and let LLM analyze them
        web_content = "\n".join([f"Source: {r.get('url', 'N/A')}\nContent: {r.get('content', '')}" for r in web_results])

        result = llm_search.invoke({
            "question": question,
            "web_search_results": web_content
            })
        search_results.append({
            "question": question,
            "key_findings": result["key_findings"],
            "sources": result["sources"]
        })
    
    state["search_results"] = search_results
    state["current_step"] = "critique"
    return state

def critique_agent(state: ResearchState) -> ResearchState:
    """
    Evaluate the quality of search results
    :state: The state of research topic
    :return: Returns the state of research topic
    """
    llm_critique = (bg_prompt + prompts.critique) | model | json_parser
    
    # For simplicity, we'll critique all results together
    all_results = "\n\n".join([f"Q: {r['question']}\nFindings: {r['key_findings']}" for r in state["search_results"]])
    
    result = llm_critique.invoke({
        "question": "Overall research quality",
        "search_results": all_results
    })
    
    state["critique_feedback"] = result["feedback"]
    
    # Simple logic to determine if revision is needed
    if result["status"] == "NEEDS_REVISION":
        state["needs_revision"] = True
        state["current_step"] = "search"  # Go back one step to search again
    else:
        state["needs_revision"] = False
        state["current_step"] = "write"
    
    return state

def writer_agent(state: ResearchState) -> ResearchState:
    """
    Write sections based on approved research
    :state: The state of research topic
    :return: Returns the state of research topic
    """
    llm_writer = (bg_prompt + prompts.writer) | model | json_parser
    
    written_sections = []
    for result in state["search_results"]:
        section = llm_writer.invoke({
            "question": result["question"],
            "research_content": result
        })
        written_sections.append({
            "question": result["question"],
            "content": section["section_content"]
        })
    
    state["written_sections"] = written_sections
    state["current_step"] = "edit"
    return state

def editor_agent(state: ResearchState) -> ResearchState:
    """
    Compile final research report and add References section into the report
    :state: The state of research topic
    :return: Returns the state of research topic
    """
    llm_editor = (bg_prompt + prompts.editor) | model | json_parser
    
    sections_text = "\n\n".join([f"Section: {s['question']}\n{s['content']}" for s in state["written_sections"]])
    
    # Extract sources from search_results
    sources = set()
    for result_item in state["search_results"]:
        if 'sources' in result_item and result_item['sources']:
            if isinstance(result_item['sources'], list):
                for source in result_item['sources']:
                    if isinstance(source, str):
                        sources.add(source)
                    elif isinstance(source, dict) and 'url' in source:
                        sources.add(source['url'])
            elif isinstance(result_item['sources'], str):
                import re
                source_list = re.split(r'[,;\n]', result_item['sources'])
                for source in source_list:
                    source = source.strip()
                    if source and (source.startswith('http') or source.startswith('www')):
                        sources.add(source)
    
    # Format references
    references_text = "\n\nReferences:\n"
    if sources:
        for i, source in enumerate(sorted(sources), 1):
            references_text += f"{i}. {source}\n"
    else:
        references_text += "No external sources were referenced in this report.\n"
    
    result = llm_editor.invoke({
        "topic": state["topic"],
        "sections": sections_text
    })
    
    state["final_report"] = result["final_report"] + references_text
    state["current_step"] = "complete"
    print('THE FINAL REPORT')
    print(state["final_report"])
    return state

# Helper Functions
# ================

def should_revise(state: ResearchState) -> str:
    """
    Determine whether to route to search (for revision) or write (to proceed)
    :param state: The current research state
    :return: "SEARCH" if revision needed, "WRITE" if ready to proceed
    """
    if state["needs_revision"]:
        return "SEARCH"
    else:
        return "WRITE"