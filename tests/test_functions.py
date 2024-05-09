import pytest
import inspect
from tests.utils_for_pytest import dump_api_call

from llm_researcher.config.config import Config
from llm_researcher.master.functions import choose_agent, get_sub_queries, scrape_urls


@pytest.mark.asyncio
async def test_choose_agent():
    function_name = inspect.currentframe().f_code.co_name
    query = "What happened in the latest burning man floods?"
    cfg = Config()    
    server_actual_result, agent_role_prompt_actual_result =  await choose_agent(query, cfg)
    # Assertion: Check that the function returns the expected result
    actual_result = f"{server_actual_result}\n{agent_role_prompt_actual_result}"
    expected_result = "📰 News Analyst Agent"
    dump_api_call(function_name, actual_result, to_json=False) 
    assert server_actual_result == expected_result

@pytest.mark.asyncio
async def test_get_sub_queries():
    function_name = inspect.currentframe().f_code.co_name
    query = "What happened in the latest burning man floods?"
    cfg = Config()
    report_type = 'research_report'
    parent_query = ""
    role = "You are a well-informed AI news analyst assistant. Your main task is to compile detailed, insightful, unbiased, and well-organized news reports on recent events, including natural disasters, by gathering information from various reliable news sources and providing a comprehensive overview."
    actual_result = await get_sub_queries(query, role, cfg, parent_query, report_type)
    expected_result = 3
    dump_api_call(function_name, actual_result)
    assert len(actual_result) == expected_result
    
def test_scrape_urls():
    function_name = inspect.currentframe().f_code.co_name
    cfg = Config()
    urls = ['https://www.foxweather.com/weather-news/burning-man-festival-nevada-death-flooding-monsoon',
            'https://apnews.com/article/burning-man-festival-flooding-entrance-closed-d6cd88ee009c6e1f6d2d92739ec1ca18',
            'https://www.foxweather.com/weather-news/burning-man-festival-mud-rain-desert',
            'https://www.pbs.org/newshour/nation/death-at-burning-man-festival-under-investigation-as-flooding-strands-thousands',
            'https://www.washingtonpost.com/climate-environment/2023/09/05/burning-man-exodus-flooding-climate-change/']
    
    actual_result = scrape_urls(urls, cfg)
    expected_result = 5
    dump_api_call(function_name, actual_result)
    assert len(actual_result) == expected_result

if __name__ == "__main__":
    pytest.main([__file__])