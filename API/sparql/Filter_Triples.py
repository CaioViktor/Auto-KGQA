# from langchain.vectorstores import FAISS
from langchain_community.vectorstores import FAISS
from rdflib.term import Literal,URIRef
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph
from sparql.Utils import getGraph, isLabel, list_to_rdf_graph, edges_to_triples, uris_list_to_rdflib_refs_list,is_valid_uri
import networkx as nx
from sparql.Endpoint  import Endpoint
import warnings

class Filter_Triples:
    def __init__(self,triples,embedding_function,relevance_threshold=0.4, max_hits_rate=0.1) -> None:
        self.endpoint = Endpoint.from_rdflib_in_string(triples)
        self.embedding_function = embedding_function
        self.graph = getGraph(triples)
        # print("Tiples before:")
        # print(self.graph.serialize(format="ttl"))
        # print("------------------------------")
        self.triples = self.graph.serialize(format="nt")
        self.relevance_threshold = relevance_threshold
        self.max_hits_rate = max_hits_rate
        self.k = int(max_hits_rate * len(self.graph))
        self.index = self.create_filter_index()
        # self.index_no_threshhold = self.create_filter_index(-1,k)


    def create_filter_index(self):
        dataset = []
        sentences = {}
        metadata = []
        for triple in self.graph:
            s = self.endpoint.get_labels(triple[0])[0][0]
            if str(triple[1]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
                p = "is a"
            elif isLabel(triple[1]):
                p = "has name"
            else:
                p = self.endpoint.get_labels(triple[1])[0][0]
            if triple[2].__class__ == URIRef:
                o = self.endpoint.get_labels(triple[2])[0][0]
            else:   
                o = triple[2]
            key = f"{s} {p}"
            if not key in sentences:
                sentence = f"{s} {p} {o}"
                sentences[key] = ["",[],p]
            else:
                sentence = sentences[key][0]
                if o not in sentence:
                    sentence+= ", " + o
            sentences[key][0] = sentence
            sentences[key][1].append(triple) 
        for key in sentences:
            sentece = sentences[key][0]
            dataset.append(sentece)
            triples = sentences[key][1]
            metadata.append({'triples':triples,'property':sentences[key][2]})
        faiss = FAISS.from_texts(dataset, self.embedding_function, metadata)
        
        return faiss
    

    def filter_triples_relevance(self, question, print_hits=False,needed_nodes=None,needed_properties=None):
        selected_triples = []
        
        # print(self.triples)


        # convert subgraph to netowkx graph to run steiner tree
        graph_netorkx = rdflib_to_networkx_multidigraph(self.graph)
        G = graph_netorkx.to_undirected()
                
        nx.set_edge_attributes(G,1, "weight")
        
        # get relevant triples to the question using faiss
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            hits_ = self.index.similarity_search_with_relevance_scores(question,self.k)
            hits = []
            for hit in hits_:
                if hit[1] >= self.relevance_threshold:
                    hits.append(hit[0])
                else:
                    break
            if len(hits) == 0:
                print("Nothing with minimun relevance!")
                hits = [hit[0] for hit in hits_]

        if print_hits:
            print(hits)

        if hits != None and len(hits) > 0:
            selected_triples = []
            if needed_nodes != None:
                needed_nodes = uris_list_to_rdflib_refs_list(needed_nodes)
                nodes = set(needed_nodes) # Nodes (resources) already included in the selected triples
            else:
                nodes = set() # Nodes (resources) already included in the selected triples
            if needed_properties != None:
                needed_properties = uris_list_to_rdflib_refs_list(needed_properties)
                properties = set(needed_properties) # Properties already included in the selected triples    
            else:
                properties = set() # Properties already included in the selected triples
            for hit in hits: # Unpackage selected triples from faiss result
                selected_triples+= hit.metadata['triples']
                for triple in hit.metadata['triples']:
                    nodes.add(triple[0])
                    properties.add(triple[1])
                    if triple[2].__class__ == URIRef:
                        nodes.add(triple[2])
            # get a connected graph from selected nodes
            sub_graph = nx.approximation.steiner_tree(G,list(nodes),method='mehlhorn')  
            complementary_triples, complementary_properties = edges_to_triples(sub_graph.edges,graph_netorkx)
            selected_triples += complementary_triples
            properties = properties.union(complementary_properties)
            for node in sub_graph.nodes:
                # if ("http" in str(node)) and (not "^^" in str(node)):
                if is_valid_uri(node):
                    nodes.add(node)

            # get metada for resources and classes in the selected triples
            for node in nodes:
                metadata_graph = getGraph(self.endpoint.get_metadata(str(node)))

                selected_triples+= list(metadata_graph)

            # get metada for properties in the selected triples
            for property in properties:
                metadata_graph = getGraph(self.endpoint.get_metada_property(str(property)))
                selected_triples+= list(metadata_graph)
            return list(set(selected_triples))
        else:
            print("Não consegiu filtrar!")
            return list(self.graph)