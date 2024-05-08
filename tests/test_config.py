from llm_researcher.config.config import Config
from llm_researcher.llm_provider.openai import OpenAIProvider
import pytest

def test_embedding_provider_lookup():
    config = Config()
    expected_result = "openai"
    actual_result = config.embedding_provider
    # Assertion: Check that the function returns the expected result
    assert actual_result == expected_result

def test_llm_provider_lookup():
    config = Config()
    expected_result = OpenAIProvider
    actual_result = config.llm_provider
    # Assertion: Check that the function returns the expected result
    assert actual_result == expected_result

if __name__ == "__main__":
    pytest.main([__file__])
