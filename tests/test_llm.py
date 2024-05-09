import pytest
import json
import inspect
from llm_researcher.master.prompts import auto_agent_instructions
from llm_researcher.utils.llm import create_chat_completion
from llm_researcher.config.config import Config

from tests.utils_for_pytest import dump_api_call

@pytest.mark.asyncio
async def test_create_chat_completion():
    function_name = inspect.currentframe().f_code.co_name
    query = "What happened in the latest burning man floods?"
    cfg = Config()
    actual_result = await create_chat_completion(
            model=cfg.smart_llm_model,
            messages=[
                {"role": "system", "content": f"{auto_agent_instructions()}"},
                {"role": "user", "content": f"task: {query}"}],
            temperature=0,
            llm_provider=cfg.llm_provider
        )

    actual_result = json.loads(actual_result)
    dump_api_call(function_name, actual_result) 
    expected_result = "You are a well-informed AI news analyst"
    # Assertion: Check that the function returns the expected result
    actual_result = actual_result["agent_role_prompt"]
    assert actual_result.startswith(expected_result)

if __name__ == "__main__":
    pytest.main([__file__])