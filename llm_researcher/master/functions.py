import asyncio
import json
from concurrent.futures.thread import ThreadPoolExecutor


import markdown

from llm_researcher.master.prompts import *
from llm_researcher.utils.llm import create_chat_completion
import llm_researcher.scraper.scraper_methods


async def choose_agent(query, cfg):
    """
    Chooses the agent automatically
    Args:
        query: original query
        cfg: Config

    Returns:
        agent: Agent name
        agent_role_prompt: Agent role prompt
    """
    try:
        response = await create_chat_completion(
            model=cfg.smart_llm_model,
            messages=[
                {"role": "system", "content": f"{auto_agent_instructions()}"},
                {"role": "user", "content": f"task: {query}"}],
            temperature=0,
            llm_provider=cfg.llm_provider
        )
        agent_dict = json.loads(response)
        return agent_dict["server"], agent_dict["agent_role_prompt"]
    except Exception as e:
        return "Default Agent", "You are an AI critical thinker research assistant. Your sole purpose is to write well written, critically acclaimed, objective and structured reports on given text."

async def stream_output(output_type, output, websocket=None, logging=True):
    """
    Streams output to the websocket
    Args:
        type:
        output:

    Returns:
        None
    """
    if not websocket or logging:
        print(output)

    if websocket:
        await websocket.send_json({"type": output_type, "output": output})
        
async def get_sub_queries(query: str, agent_role_prompt: str, cfg, parent_query: str, report_type:str):
    """
    Gets the sub queries
    Args:
        query: original query
        agent_role_prompt: agent role prompt
        cfg: Config

    Returns:
        sub_queries: List of sub queries

    """
    max_research_iterations = cfg.max_iterations if cfg.max_iterations else 1
    response = await create_chat_completion(
        model=cfg.smart_llm_model,
        messages=[
            {"role": "system", "content": f"{agent_role_prompt}"},
            {"role": "user", "content": generate_search_queries_prompt(query, parent_query, report_type, max_iterations=max_research_iterations)}],
        temperature=0,
        llm_provider=cfg.llm_provider
    )
    sub_queries = json.loads(response)
    return sub_queries


def scrape_urls(urls, cfg):
    """
    Scrapes the urls
    Args:
        urls: List of urls
        cfg: Config (optional)

    Returns:
        text: str

    """
    def extract_data_from_link(scraper_nm, link):
        print(f"extract_data_from_link {scraper_nm=}, {link=}")
        if link.endswith(".pdf"):
            scraper_nm = "pdf_scraper"
        elif "arxiv.org" in link:
            scraper_nm = "arxiv_scraper"

        content = ""
        try:
            scraper = getattr(llm_researcher.scraper.scraper_methods, scraper_nm)
            content = scraper(link)

            if len(content) < 100:
                return {"url": link, "raw_content": None}
            return {"url": link, "raw_content": content}
        except Exception:
            return {"url": link, "raw_content": None}

    content_list = []
    try:
        with ThreadPoolExecutor(max_workers=20) as executor:
            contents = executor.map(lambda url: extract_data_from_link(cfg.scraper_nm, url), urls)
        content_list = [content for content in contents if content["raw_content"] is not None]

    except Exception as e:
        print(f"Error in scrape_urls: {e}")
    return content_list



