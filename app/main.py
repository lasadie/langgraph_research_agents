import os
from state import ResearchState
from agents import *
from utils import logging, parse_report_to_markdown
from langgraph.graph import StateGraph, START, END

# Create the graph
workflow = StateGraph(ResearchState)

# LLM nodes
workflow.add_node("orchestrate", orchestrator_agent)
workflow.add_node("search", search_agent)
workflow.add_node("critique", critique_agent)
workflow.add_node("write", writer_agent)
workflow.add_node("edit", editor_agent)

# Edges
workflow.add_edge(START, "orchestrate")
workflow.add_edge("orchestrate", "search")
workflow.add_edge("search", "critique")
workflow.add_conditional_edges(
    "critique",
    should_revise,
    {
        "SEARCH": "search",
        "WRITE": "write"
    }
)
workflow.add_edge("write", "edit")
workflow.add_edge("edit", END)

# Compile the graph
app = workflow.compile()

if __name__ == "__main__":
    topic = input("Enter a research topic: ")
    
    initial_state = ResearchState(
        topic=topic,
        research_questions=[],
        search_results=[],
        critique_feedback=None,
        written_sections=[],
        final_report=None,
        current_step="orchestrator",
        needs_revision=False
    )
    
    logging.info(f"Starting research on: {topic}")
    
    # Run the workflow
    final_state = app.invoke(initial_state)
    
    logging.info("Research complete!")
    content = parse_report_to_markdown(final_state["final_report"])

    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
    os.makedirs(output_dir, exist_ok=True)

    filepath = os.path.join(output_dir, "final_report.md")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\nResearch report saved to: {filepath}")