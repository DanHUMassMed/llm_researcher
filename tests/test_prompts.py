import pytest
import inspect
from tests.utils_for_pytest import dump_api_call

from llm_researcher.config.config import Config
from llm_researcher.master.prompts import get_prompt_by_report_type, generate_report_prompt


    
def test_get_prompt_by_report_type():
    function_name = inspect.currentframe().f_code.co_name
    report_type = 'research_report'
    actual_result = get_prompt_by_report_type(report_type)
    actual_result = actual_result.__name__
    expected_result = generate_report_prompt.__name__
    dump_api_call(function_name, actual_result, to_json=False)
    assert actual_result == expected_result

if __name__ == "__main__":
    pytest.main([__file__])