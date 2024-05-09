# llm_researcher
llm_researcher

## Flow of Research report

* Create the researcher object
    * This is done by establishing the research question/statement and the type of report to generate
        * query = "What happened in the latest burning man floods?"
        * report_type = "research_report"
        * researcher = LLMResearcher(query=query, report_type=report_type)
    * The constructor also initalizes the following:
        * `report_prompt` based on the report_type (This is a validator and can be removed)
        * `retriever` based on search_retriever from config
        * `memory` whic is an Object based on the embedding provider
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


    

