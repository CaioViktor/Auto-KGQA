from sparql.Endpoint import Endpoint
from nlp.normalizer import *
from index.whoosh_index import *
from configs import *

def createIndexes():
    print("Creating T-Box endpoint")
    endpoint_t_box = Endpoint(ENDPOINT_T_BOX_URL)
    print("-----------------------------------------------------------")

    endpoint_a_box = endpoint_t_box
    if ENDPOINT_A_BOX_URL and ENDPOINT_T_BOX_URL != ENDPOINT_A_BOX_URL:
        print("Creating A-Box endpoint")
        endpoint_a_box = Endpoint(ENDPOINT_A_BOX_URL)
        print("-----------------------------------------------------------")

    print("Creating Nomrmalizer")
    normalizer = Normalizer()
    print("-----------------------------------------------------------")

    print("Creating T-Box index")
    t_box_index = TBoxIndex(endpoint_t_box,normalizer)
    print("T-Box index created: "+str(t_box_index.exists()))
    print("-----------------------------------------------------------")

    print("Creating T-Box index")
    a_box_index = ABoxIndex(endpoint_a_box,normalizer)
    print("A-Box index created: "+str(a_box_index.exists()))
    print("-----------------------------------------------------------")

if __name__ == "__main__":
    createIndexes()
