import pytest
from llm_researcher.config.config import Config, ReportType
from llm_researcher.master.functions import choose_agent

@pytest.mark.asyncio
async def test_choose_agent():
    query = "What happened in the latest burning man floods?"
    cfg = Config()
    expected_result = "📰 News Analyst Agent"
    
    server_actual_result, agent_role_prompt_actual_result =  await choose_agent(query, cfg)
    # Assertion: Check that the function returns the expected result
    print(server_actual_result)
    assert server_actual_result == expected_result

@pytest.mark.asyncio
async def test_get_sub_queries():
    pass


if __name__ == "__main__":
    pytest.main([__file__])