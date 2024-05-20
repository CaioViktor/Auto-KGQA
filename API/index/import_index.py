from configs import *
#Import T-Box index
if INDEX_T_BOX == "WHOOSH":
    from index.whoosh_index import TBoxIndex
elif INDEX_T_BOX == "FAISS":
    from index.vector_distance_index import TBoxIndex
elif INDEX_T_BOX == "SPOTLIGHT":
    from index.spotlight import TBoxIndex

#Import A-Box index
if INDEX_A_BOX == "WHOOSH":
    from index.whoosh_index import ABoxIndex
elif INDEX_A_BOX == "FAISS":
    from index.vector_distance_index import ABoxIndex
elif INDEX_A_BOX == "SPOTLIGHT":
    from index.spotlight import ABoxIndex