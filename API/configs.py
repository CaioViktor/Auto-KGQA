ENDPOINT_KNOWLEDGE_GRAPH_URL = "../Demo/ontology_example.ttl" # Knowledge graph endpoint can be a triples store http endpoint URL or a filepath containing the triples.
# ENDPOINT_A_BOX_URL = "http://localhost:7200/repositories/artigo"
EXTRACT_T_BOX = True # The script will perform queries on ENDPOINT_KNOWLEDGE_GRAPH_URL to extract the necessary information that would form the T-Box. The triples will be saved in the file ENDPOINT_T_BOX_URL. If you already have the T-Box separated, set this value to False.
ENDPOINT_T_BOX_URL = "sparql/temp/t_box.ttl" # Change this line only if you already have the T-Box separated, you need to set EXTRACT_T_BOX = False. Set the value to a local file when extracting the T-Box

DATASET_FILE = "questions_dataset.csv" #File name for query persistence and feedback

NUMBER_HOPS = 2 # Number of hops in neighborhood in the prefetch step to retrieve the the relevant triples for the selected resource
LIMIT_BY_PROPERTY = -1 # Maximum number of triple for each property in the prefetch step to retrieve the the relevant triples for the selected resource. Set -1 for retrieve all values for each property
MAX_SCORE_PARSER_TRIPLES_FAISS = 0.85 # Maximum acceptable score for hits using the FAISS index
MIN_SCORE_PARSER_TRIPLES_WOOSH = 0.95 # Minimun acceptable score for hits using the WOOSH index

INDEX_T_BOX = "FAISS" # Value "FAISS": Index based in vector distance using langchain.faiss; "WHOOSH": Index based in text similarity using whoosh; "SPOTLIGHT"
USE_A_BOX_INDEX = True # Indicates whether to use the A-Box index. For very large KGs it is preferable to set False.
INDEX_A_BOX = "WHOOSH" # Value "FAISS": Index based in vector distance using langchain.faiss; "WHOOSH": Index based in text similarity using whoosh; "SPOTLIGHT"

LLM_MODEL = "gpt-4o-mini" # Exemples: "gpt-3.5-turbo","gpt-3.5-turbo-16k","gpt-4","gpt-4o","gpt-4-turbo","gpt-4o-mini"
TEMPERATURE_TRANSLATE = 1 # LLM temperature to generate SPARQL
SIZE_CONTEXT_WINDOW_TRANSLATE = 7 # Number of messages passed by LLM when generating SPARQL
TEMPERATURE_SELECT = 0.3 # LLM temperature to select best SPARQL
SIZE_CONTEXT_WINDOW_SELECT  = 7 # Number of messages passed by LLM when selecting the best SPARQL
TEMPERATURE_FINAL_ANSWER = 1.2 # LLM temperature to generate final answer in natural language
SIZE_CONTEXT_WINDOW_FINAL_ANSWER = 7 # Number of messages passed by LLM when generating the final answer in natural language

FILTER_GRAPH = True # Filter triples after initial neighborhood retrieaval for referenced terms 
RELEVANCE_THRESHOLD = 0.45 # Threshhold for filter triples based on question embedding distance vector
MAX_HITS_RATE = 0.1 # percentage of the total triples allowed to be passed in the subgraph triples filter
PRINT_HITS = False # Show list of triples marked as relevant to the query according to vector distance

VISUALIZATION_TOOL_URL="http://localhost:7200/graphs-visualizations?uri=" # URL for a KG navigation tool displayed when clicking on URI links

