from configs import *
from nlp.normalizer import *
from sparql.Endpoint import Endpoint
#Import T-Box index
from index.import_index import *

def load_configs():
    #Normalizer
    normalizer = Normalizer()

    #T-Box
    endpoint_t_box = Endpoint(ENDPOINT_T_BOX_URL)
    t_box_index = TBoxIndex(endpoint_t_box,normalizer)

    #A-Box
    endpoint_a_box = endpoint_t_box
    if ENDPOINT_KNOWLEDGE_GRAPH_URL and ENDPOINT_T_BOX_URL != ENDPOINT_KNOWLEDGE_GRAPH_URL:
        endpoint_a_box = Endpoint(ENDPOINT_KNOWLEDGE_GRAPH_URL)
    if USE_A_BOX_INDEX:
        a_box_index = ABoxIndex(endpoint_a_box,normalizer)
    else:
        a_box_index = None
    return normalizer,endpoint_t_box,t_box_index,endpoint_a_box,a_box_index