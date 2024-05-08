import asyncio
import time

from llm_researcher.master.functions import stream_output, choose_agent, scrape_urls, get_sub_queries
from llm_researcher.master.prompts import get_prompt_by_report_type
from llm_researcher.memory.embeddings import Memory
from llm_researcher.config.config import Config, ReportType
from llm_researcher.context.compression import ContextCompressor

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
        self.source_urls = source_urls
        self.memory = Memory(self.cfg.embedding_provider)
        self.visited_urls = visited_urls

        # Only relevant for DETAILED REPORTS
        # --------------------------------------

        # Stores the main query of the detailed report
        self.parent_query = parent_query

        # Stores all the user provided subtopics
        self.subtopics = subtopics

    async def conduct_research(self):
        print(f"🔎 Running research for '{self.query}'...")
        
        # Generate Agent
        if not (self.agent and self.role):
            self.agent, self.role = await choose_agent(self.query, self.cfg)
        await stream_output("logs", self.agent, self.websocket)

        # If specified, the researcher will use the given urls as the context for the research.
        if self.source_urls:
            self.context = await self.get_context_by_urls(self.source_urls)
        else:
            self.context = await self.get_context_by_search(self.query)

        time.sleep(2)

    async def get_context_by_urls(self, urls):
        """
            Scrapes and compresses the context from the given urls
        """
        new_search_urls = await self.get_new_urls(urls)
        await stream_output("logs",
                            f"🧠 I will conduct my research based on the following urls: {new_search_urls}...",
                            self.websocket)
        scraped_sites = scrape_urls(new_search_urls, self.cfg)
        return await self.get_similar_content_by_query(self.query, scraped_sites)

    async def get_context_by_search(self, query):
        """
           Generates the context for the research task by searching the query and scraping the results
        Returns:
            context: List of context
        """
        context = []
        # Generate Sub-Queries including original query
        sub_queries = await get_sub_queries(query, self.role, self.cfg, self.parent_query, self.report_type) + [query]
        await stream_output("logs",
                            f"🧠 I will conduct my research based on the following queries: {sub_queries}...",
                            self.websocket)

        # Using asyncio.gather to process the sub_queries asynchronously
        context = await asyncio.gather(*[self.process_sub_query(sub_query) for sub_query in sub_queries])
        return context

    async def process_sub_query(self, sub_query: str):
        """Takes in a sub query and scrapes urls based on it and gathers context.

        Args:
            sub_query (str): The sub-query generated from the original query

        Returns:
            str: The context gathered from search
        """
        await stream_output("logs", f"\n🔎 Running research for '{sub_query}'...", self.websocket)

        scraped_sites = await self.scrape_sites_by_query(sub_query)
        content = await self.get_similar_content_by_query(sub_query, scraped_sites)

        if content:
            await stream_output("logs", f"📃 {content}", self.websocket)
        else:
            await stream_output("logs", f"🤷 No content found for '{sub_query}'...", self.websocket)
        return content

    async def get_new_urls(self, url_set_input):
        """ Gets the new urls from the given url set.
        Args: url_set_input (set[str]): The url set to get the new urls from
        Returns: list[str]: The new urls from the given url set
        """

        new_urls = []
        for url in url_set_input:
            if url not in self.visited_urls:
                await stream_output("logs", f"✅ Adding source url to research: {url}\n", self.websocket)

                self.visited_urls.add(url)
                new_urls.append(url)

        return new_urls

    async def scrape_sites_by_query(self, sub_query):
        """
        Runs a sub-query
        Args:
            sub_query:

        Returns:
            Summary
        """
        # Get Urls
        retriever = self.retriever(sub_query)
        search_results = retriever.search(
            max_results=self.cfg.max_search_results_per_query)
        new_search_urls = await self.get_new_urls([url.get("href") for url in search_results])

        # Scrape Urls
        # await stream_output("logs", f"📝Scraping urls {new_search_urls}...\n", self.websocket)
        await stream_output("logs", "Researching for relevant information...\n", self.websocket)
        scraped_content_results = scrape_urls(new_search_urls, self.cfg)
        return scraped_content_results


    async def get_similar_content_by_query(self, query, pages):
        await stream_output("logs", f"📝 Getting relevant content based on query: {query}...", self.websocket)
        # Summarize Raw Data
        context_compressor = ContextCompressor(
            documents=pages, embeddings=self.memory.get_embeddings())
        # Run Tasks
        return context_compressor.get_context(query, max_results=8)
