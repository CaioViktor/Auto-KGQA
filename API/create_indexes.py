from sparql.Endpoint import Endpoint
from nlp.normalizer import *
from sparql.Generator_T_Box import Generator_T_Box
# from index.whoosh_index import *
from configs import *
from index.import_index import *
import os
import shutil

def createIndexes():
    if os.path.exists("sparql/temp/labels.obj"):
        os.remove("sparql/temp/labels.obj")
        print("Old file removed: sparql/temp/labels.obj")

    if os.path.exists("sparql/temp/counts.obj"):
        os.remove("sparql/temp/counts.obj")
        print("Old file removed: sparql/temp/counts.obj")

    if os.path.exists("index/temp/t_box_index/"+INDEX_T_BOX.lower()):
        shutil.rmtree("index/temp/t_box_index/"+INDEX_T_BOX.lower())
        print("Old index removed: index/temp/t_box_index/"+INDEX_T_BOX.lower())

    if os.path.exists("index/temp/a_box_index/"+INDEX_A_BOX.lower()):
        shutil.rmtree("index/temp/a_box_index/"+INDEX_A_BOX.lower())
        print("Old index removed: index/temp/a_box_index/"+INDEX_A_BOX.lower())


    
    print("Creating A-Box endpoint")
    endpoint_a_box = Endpoint(ENDPOINT_KNOWLEDGE_GRAPH_URL)
    print("-----------------------------------------------------------")

    if EXTRACT_T_BOX:
        print("Extracting T-Box...")
        t_box_generator = Generator_T_Box(endpoint_a_box)
        triples_full_ttl = t_box_generator.generate_t_box()
        print("Triples in T-Box extracted: "+ str(len(triples_full_ttl.splitlines())))
        with open(ENDPOINT_T_BOX_URL,"w") as t_box_file:
            t_box_file.write(triples_full_ttl)
        print("T-Box saved to: "+ENDPOINT_T_BOX_URL)

    print("Creating T-Box endpoint")
    endpoint_t_box = Endpoint(ENDPOINT_T_BOX_URL)
    print("-----------------------------------------------------------")

    

    print("Creating Normalizer")
    normalizer = Normalizer()
    print("-----------------------------------------------------------")

    print("Creating T-Box index")
    t_box_index = TBoxIndex(endpoint_t_box,normalizer)
    print("T-Box index created: "+str(t_box_index.exists()) + " Type: "+t_box_index.type)
    print("-----------------------------------------------------------")

    if USE_A_BOX_INDEX:
        print("Creating A-Box index")
        a_box_index = ABoxIndex(endpoint_a_box,normalizer)
        print("A-Box index created: "+str(a_box_index.exists()) + " Type: "+a_box_index.type)
        print("-----------------------------------------------------------")

    print("Saving T-Box Endpoint labels cache...")
    endpoint_t_box.save_labels()
    print("T-Box Endpoint labels Saved")

    print("Saving T-Box Endpoint counts cache...")
    endpoint_t_box.save_counts()
    print("T-Box Endpoint counts Saved")

    if USE_A_BOX_INDEX and endpoint_a_box != endpoint_t_box:
        print("Saving A-Box Endpoint labels cache...")
        endpoint_a_box.save_labels()
        print("A-Box Endpoint labels Saved")

        print("Saving A-Box Endpoint counts cache...")
        endpoint_a_box.save_counts()
        print("A-Box Endpoint counts Saved")
    else:
        print("T-Box Endpoint and A-Box Endpoint are the same!")

if __name__ == "__main__":
    createIndexes()
