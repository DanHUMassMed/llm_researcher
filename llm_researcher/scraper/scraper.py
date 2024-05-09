from concurrent.futures.thread import ThreadPoolExecutor

import llm_researcher.scraper.scraper_methods
from llm_researcher.scraper.scraper_methods import *


class Scraper:
    """
    Scraper class to extract the content from the links
    """

    def __init__(self, urls, scraper_nm):
        """
        Initialize the Scraper class.
        Args:
            urls:
        """
        self.urls = urls
        self.scraper_nm = scraper_nm


    def run(self):
        with ThreadPoolExecutor(max_workers=20) as executor:
            #contents = executor.map(lambda url: self.extract_data_from_link(self.scraper, url), self.urls)
            contents = executor.map(self.extract_data_from_link, self.urls)
        res = [content for content in contents if content["raw_content"] is not None]
        return res

    def extract_data_from_link(self, scraper_nm, link):
        """
        Extracts the data from the link
        """

        if link.endswith(".pdf"):
            scraper_nm = "pdf_scraper"
        elif "arxiv.org" in link:
            scraper_nm = "arxiv_scraper"
        else:
            scraper_nm = self.scraper_nm

        content = ""
        try:
            scraper = getattr(llm_researcher.scraper.scraper_methods, scraper_nm)
            content = scraper(link)

            if len(content) < 100:
                return {"url": link, "raw_content": None}
            return {"url": link, "raw_content": content}
        except Exception:
            return {"url": link, "raw_content": None}

    