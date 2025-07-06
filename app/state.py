from typing import List, Dict, Optional, Any
from typing_extensions import TypedDict

class ResearchState(TypedDict):
    """
    Custom class to manage research topic state
    """
    topic: str
    research_questions: List[str]
    search_results: List[Dict[str, Any]]  # [{"question": "", "content": "", "source": ""}]
    critique_feedback: Optional[str]
    written_sections: List[Dict[str, str]]  # [{"question": "", "content": ""}]
    final_report: Optional[str]
    current_step: str
    needs_revision: bool