
from abc import ABC, abstractmethod

from app.reserch.schema import ResearchRequest, ResearchResult


class BaseResearch(ABC):
    """Common interface for all research services."""

    @abstractmethod
    def research(self, request: ResearchRequest) -> ResearchResult:
        """Execute research for the given topic and instructions."""
        
        pass
