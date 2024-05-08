import importlib.util
import os
import json
from enum import Enum

module_spec = importlib.util.find_spec(__name__)
package_path = os.path.dirname(module_spec.origin)
CONFIG_FILE_PATH = os.path.join(package_path, 'llm_researcher_config.json')


class ReportType(Enum):
    ResearchReport = 'research_report'
    ResourceReport = 'resource_report'
    OutlineReport = 'outline_report'
    CustomReport = 'custom_report'
    DetailedReport = 'detailed_report'
    SubtopicReport = 'subtopic_report'

class Config:
    """Config class for GPT Researcher."""

    def __init__(self):
        with open(CONFIG_FILE_PATH, "r") as json_file:
            config_json = json.load(json_file)
        self.__data = self._get_values_for_config(config_json)

    def __getattr__(self, name): 
        try:
            return getattr(self.__data, name) 
        except AttributeError:
            return self.__data[name] 
       
    def __dir__(self):
        return self.__data.keys()

    def _get_values_for_config(self, config_json):
        config_data = {}
        for key in config_json.keys():
            default_value = config_json[key]['default_val']
            env_var = config_json[key]['env_var']
            env_value = os.getenv(env_var)
            value = None
            if env_value is not None:
                if isinstance(default_value, int):
                    value = int(env_value)
                elif isinstance(default_value, float):
                    value = float(env_value)
                else:
                    value = env_value
            else:
                value = default_value

            if key == "search_retriever":
                value = self._get_search_retriever(value)

            if key == "llm_provider":
                value = self._get_llm_provider(value)

            config_data[key]=value

        return config_data

    def _get_search_retriever(self, search_retriever: str):
        match search_retriever:
            case "tavily":
                from llm_researcher.retrievers.search_retrievers import tavily_search
                retriever = tavily_search
            case _:
                raise Exception("Retriever not found.")

        return retriever
    
    def _get_llm_provider(self, llm_provider: str):
        match llm_provider:
            case "openai":
                from llm_researcher.llm_provider.openai import OpenAIProvider
                llm_provider = OpenAIProvider
            case _:
                raise Exception("LLM provider not found.")

        return llm_provider
