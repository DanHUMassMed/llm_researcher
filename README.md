# llm_researcher
llm_researcher

## Flow of Research report

* Create the researcher object
    * This is done by establishing the research question/statement and the type of report to generate
        * query = "What happened in the latest burning man floods?"
        * report_type = "research_report"
        * researcher = LLMResearcher(query=query, report_type=report_type)
    * The constructor also initalizes the following:
        * `report_prompt` based on the report_type get the prompt to use
        * `retriever` based on search_retriever from config
        * `memory` which is an Object based on the embedding provider
* Conduct Research
    * Here we choose the `agent` and define the `role` using `choose_agent` 
        * This is done by prompting the LLM to create these items based on the provide research request and a prompts to the system
        * A few example are provided for the expected return values
    * Once we have the `agent` and `role` we `get_context_by_search`
        



# Report types identified
* research_report  (generate_report_prompt)
* resource_report  (generate_resource_report_prompt)
* outline_report   (generate_outline_report_prompt)
* custom_report    (generate_custom_report_prompt)
* subtopic_report  (generate_subtopic_report_prompt)
* detailed_report  ()

# Process

1. Get __Query__ from the user
2. From the __Query__ determine:
    *  __Agent__ : The system/search agent name prompt
    *  __Role__: The systems role prompt
3. Using __Query__ and __Role__ prompt, find a list of sub_topics to queries 
    * __Topics__: A list of topics to search including the original query
4. For each __Topic__ in __Topics__ search for URLs/sites to scrape
    * Find __URLS__: Executa a search that returns related websites (filter search results and drop an duplicate URLs)
5. For each __Topics__  __URLS__ scrape the site for content
    * for all __Scaped_Content_for_Topic__ consolidate content that is simalary with __ContextualCompressionRetriever__
6. Aggregate all content from Step 5
    * this is the completed reseach!!

    


