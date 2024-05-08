import pytest
from llm_researcher.master.agent import LLMResearcher

def test_agent_constructor():
    query = "What happened in the latest burning man floods?"
    report_type = "research_report"

    researcher = LLMResearcher(query=query, report_type=report_type)
    expected_result = report_type
    actual_result = researcher.report_type
    # Assertion: Check that the function returns the expected result
    assert actual_result == expected_result

def test_get_context_by_search():
    query = "What happened in the latest burning man floods?"
    report_type = "research_report"

    researcher = LLMResearcher(query=query, report_type=report_type)

if __name__ == "__main__":
    pytest.main([__file__])