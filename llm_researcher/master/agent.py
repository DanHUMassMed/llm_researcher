import asyncio
import time


from llm_researcher.master.functions import stream_output, choose_agent, scrape_urls, get_sub_queries, generate_report, get_report_introduction
from llm_researcher.master.prompts import get_prompt_by_report_type
from llm_researcher.utils.llm import construct_subtopics
from llm_researcher.memory.embeddings import Memory
from llm_researcher.config.config import Config, ReportType
from llm_researcher.context.compression import ContextCompressor

import inspect
import logging
logging.basicConfig(filename='llm_researcher.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)

class LLMResearcher:
    def __init__(
        self,
        query: str,
        report_type: str = ReportType.ResearchReport,
        source_urls=None,
        websocket=None,
        agent=None,
        role=None,
        parent_query: str = "",
        subtopics: list = [],
        visited_urls: set = set()
    ):
        self.query = query
        self.agent = agent
        self.role = role
        self.report_type = report_type
        self.report_prompt = get_prompt_by_report_type(self.report_type)  # this validates the report type
        self.websocket = websocket
        self.cfg = Config()
        self.retriever = self.cfg.search_retriever
        self.context = []
        self.source_urls = source_urls ########## NOT USED!!!!
        self.memory = Memory(self.cfg.embedding_provider)
        self.visited_urls = visited_urls

        # Only relevant for DETAILED REPORTS
        # --------------------------------------

        # Stores the main query of the detailed report
        self.parent_query = parent_query

        # Stores all the user provided subtopics
        self.subtopics = subtopics ########## NOT USED!!!!

    async def conduct_research(self):
        function_name = inspect.currentframe().f_code.co_name
        logger.debug(f"TRACE: Entering {function_name}")
        print(f"🔎 Running research for '{self.query}'...")
        
        # Generate Agent
        if not (self.agent and self.role):
            self.agent, self.role = await choose_agent(self.query, self.cfg)
        await stream_output("logs", self.agent, self.websocket)

        self.context = await self.get_context_by_search(self.query)
        time.sleep(2)
        logger.debug(f"TRACE: Exiting  {function_name}")


    async def write_report(self, existing_headers: list = []):
        """
        Writes the report based on research conducted

        Returns:
            str: The report
        """
        function_name = inspect.currentframe().f_code.co_name
        logger.debug(f"TRACE: Entering {function_name}")

        # Write Research Report
        if self.report_type == "custom_report":
            self.role = self.cfg.agent_role if self.cfg.agent_role else self.role

        await stream_output("logs", f"✍️ Writing summary for research task: {self.query}...", self.websocket)

        if self.report_type == "custom_report":
            self.role = (self.cfg.agent_role if self.cfg.agent_role else self.role)
        elif self.report_type == "subtopic_report":
            report = await generate_report(
                query=self.query,
                context=self.context,
                agent_role_prompt=self.role,
                report_type=self.report_type,
                websocket=self.websocket,
                cfg=self.cfg,
                main_topic=self.parent_query,
                existing_headers=existing_headers
            )
        else:
            report = await generate_report(
                query=self.query,
                context=self.context,
                agent_role_prompt=self.role,
                report_type=self.report_type,
                websocket=self.websocket,
                cfg=self.cfg
            )

        logger.debug(f"TRACE: Exiting  {function_name}")
        return report


    async def get_context_by_search(self, query):
        """
           Generates the context for the research task by searching the query and scraping the results
        Returns:
            context: List of context
        """
        function_name = inspect.currentframe().f_code.co_name
        logger.debug(f"TRACE: Entering {function_name}")

        context = []
        # Generate Sub-Queries including original query
        sub_queries = await get_sub_queries(query, self.role, self.cfg, self.parent_query, self.report_type) + [query]
        await stream_output("logs",
                            f"🧠 I will conduct my research based on the following queries: {sub_queries}...",
                            self.websocket)

        # Using asyncio.gather to process the sub_queries asynchronously
        context = await asyncio.gather(*[self.process_sub_query(sub_query) for sub_query in sub_queries])
        logger.debug(f"TRACE: Exiting  {function_name}")

        return context

    async def process_sub_query(self, sub_query: str):
        """Takes in a sub query and scrapes urls based on it and gathers context.

        Args:
            sub_query (str): The sub-query generated from the original query

        Returns:
            str: The context gathered from search
        """
        function_name = inspect.currentframe().f_code.co_name
        logger.debug(f"TRACE: Entering {function_name}")

        await stream_output("logs", f"\n🔎 Running research for '{sub_query}'...", self.websocket)

        scraped_sites = await self.scrape_sites_by_query(sub_query)
        content = await self.get_similar_content_by_query(sub_query, scraped_sites)

        if content:
            await stream_output("logs", f"📃 {content}", self.websocket)
        else:
            await stream_output("logs", f"🤷 No content found for '{sub_query}'...", self.websocket)
        logger.debug(f"TRACE: Exiting  {function_name}")
        return content

    async def get_new_urls(self, url_set_input):
        """ Gets the new urls from the given url set.
        Args: url_set_input (set[str]): The url set to get the new urls from
        Returns: list[str]: The new urls from the given url set
        """
        function_name = inspect.currentframe().f_code.co_name
        logger.debug(f"TRACE: Entering {function_name}")

        new_urls = []
        for url in url_set_input:
            if url not in self.visited_urls:
                await stream_output("logs", f"✅ Adding source url to research: {url}\n", self.websocket)

                self.visited_urls.add(url)
                new_urls.append(url)

        logger.debug(f"TRACE: Exiting  {function_name}")
        return new_urls

    async def scrape_sites_by_query(self, sub_query):
        """
        Runs a sub-query
        Args:
            sub_query:

        Returns:
            Summary
        """
        function_name = inspect.currentframe().f_code.co_name
        logger.debug(f"TRACE: Entering {function_name}")

        # Get Urls
        search_results = self.retriever(sub_query,max_results=self.cfg.max_search_results_per_query)
        new_search_urls = await self.get_new_urls([url.get("href") for url in search_results])

        # Scrape Urls
        # await stream_output("logs", f"📝Scraping urls {new_search_urls}...\n", self.websocket)
        await stream_output("logs", "Researching for relevant information...\n", self.websocket)
        scraped_content_results = scrape_urls(new_search_urls, self.cfg)
        logger.debug(f"TRACE: Exiting  {function_name}")
        return scraped_content_results


    async def get_similar_content_by_query(self, query, pages):
        function_name = inspect.currentframe().f_code.co_name
        logger.debug(f"TRACE: Entering {function_name}")

        await stream_output("logs", f"📝 Getting relevant content based on query: {query}...", self.websocket)
        # Summarize Raw Data
        context_compressor = ContextCompressor(documents=pages, embeddings=self.memory.get_embeddings())
        # Run Tasks
        logger.debug(f"TRACE: Exiting  {function_name}")
        return context_compressor.get_context(query, max_results=8)

    ########################################################################################

    # DETAILED REPORT

    async def write_introduction(self):
        function_name = inspect.currentframe().f_code.co_name
        logger.debug(f"TRACE: Entering {function_name}")

        # Construct Report Introduction from main topic research
        introduction = await get_report_introduction(self.query, self.context, self.role, self.cfg, self.websocket)

        logger.debug(f"TRACE: Exiting  {function_name}")
        return introduction

    async def get_subtopics(self):
        """
        This async function generates subtopics based on user input and other parameters.

        Returns:
          The `get_subtopics` function is returning the `subtopics` that are generated by the
        `construct_subtopics` function.
        """
        function_name = inspect.currentframe().f_code.co_name
        logger.debug(f"TRACE: Entering {function_name}")

        await stream_output("logs", f"🤔 Generating subtopics...", self.websocket)

        subtopics = await construct_subtopics(
            task=self.query,
            data=self.context,
            config=self.cfg,
            # This is a list of user provided subtopics
            subtopics=self.subtopics,
        )

        await stream_output("logs", f"📋Subtopics: {subtopics}", self.websocket)
        subtopics =  subtopics.dict()["subtopics"]

        logger.debug(f"TRACE: Exiting  {function_name}")
        return subtopics
