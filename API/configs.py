ENDPOINT_T_BOX_URL = "http://localhost:7200/repositories/artigo"
ENDPOINT_A_BOX_URL = None #Comment this line and use the one below if T-Box and A-Box are on different endpoints
# ENDPOINT_A_BOX_URL = "http://localhost:7200/repositories/artigo"

DATASET_FILE = "questions_dataset.csv" #File name for query persistence and feedback

NUMBER_HOPS = 2 # Number of hops in neighborhood in the prefetch step to retrieve the the relevant triples for the selected resource
LIMIT_BY_PROPERTY = -1 # Maximum number of triple for each property in the prefetch step to retrieve the the relevant triples for the selected resource. Set -1 for retrieve all values for each property
MAX_SCORE_PARSER_TRIPLES = 0.85

INDEX_T_BOX = "FAISS" # Value "FAISS": Index based in vector distance using langchain.faiss; "WHOOSH": Index based in text similarity using whoosh; "SPOTLIGHT"
INDEX_A_BOX = "WHOOSH" # Value "FAISS": Index based in vector distance using langchain.faiss; "WHOOSH": Index based in text similarity using whoosh; "SPOTLIGHT"

LLM_MODEL = "gpt-4o" # Exemples: "gpt-3.5-turbo","gpt-3.5-turbo-16k","gpt-4","gpt-4o"
TEMPERATURE_TRANSLATE = 1
SIZE_CONTEXT_WINDOW_TRANSLATE = 7
TEMPERATURE_SELECT = 0.3
SIZE_CONTEXT_WINDOW_SELECT  = 7
TEMPERATURE_FINAL_ANSWER = 1.2
SIZE_CONTEXT_WINDOW_FINAL_ANSWER = 7

FILTER_GRAPH = True # Filter triples after initial neighborhood retrieaval for referenced terms 
RELEVANCE_THRESHOLD = 0.45 # Threshhold for filter triples based on question embedding distance vector
MAX_HITS_RATE = 0.1 # percentage of the total triples allowed to be passed in the subgraph triples filter
PRINT_HITS = False # Show list of triples marked as relevant to the query according to vector distance

VISUALIZATION_TOOL_URL="http://localhost:7200/graphs-visualizations?uri="