import os
# from langchain.embeddings import SentenceTransformerEmbeddings
from langchain_community.embeddings import SentenceTransformerEmbeddings
# from langchain.vectorstores import FAISS
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.faiss import DistanceStrategy



class Index:
    def __init__(self,path_index,endpoint,normalizer) -> None:
        self.path_index = path_index
        self.endpoint = endpoint
        self.normalizer = normalizer
        self.type = "FAISS"
        self.embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        if not os.path.isdir(path_index):
            print("Creating new index...")
            self.loadTerms(endpoint)
            self.index = self.create()
            print("New index created!")
        else: 
            print("Loading existing index...")
            self.index = FAISS.load_local(self.path_index, self.embedding_function)
            print("Existing index Loaded!")
    
    def loadTerms(self,endpoint):
        pass

    def prepare_dataset(self,terms):
        keys = []
        metadata = []
        # print(terms)
        for term in terms:
            keys_r = self.endpoint.get_labels(term['?term'])
            for key in keys_r:
                # print(f"{term}:{key[0]}")
                keys.append(key[0])
                metadata.append(term)
        return keys,metadata

    def create(self):
        keys,metadata = self.prepare_dataset(self.terms)
        faiss = FAISS.from_texts(keys, self.embedding_function, metadata)
        faiss.save_local(self.path_index)
        return faiss

    def search(self,term,hits=5):
        # print("search: "+term)
        results = []
        results = self.index.similarity_search_with_score(term,hits)
        r = []
        for i in results:
            metadata = i[0].metadata
            r.append({'label':metadata['?label'],'content':metadata,'score':float(i[1])})
        results = r
        return results
    
    def exists(self):
        try:
            if os.path.exists(self.path_index) and FAISS.load_local(self.path_index, self.embedding_function) != None:
                return True
        except:
            return False

class TBoxIndex(Index):
    def __init__(self, endpoint, normalizer) -> None:
        path_index = path_index = "index/temp/t_box_index/faiss"
        super().__init__(path_index, endpoint, normalizer)
    
    def loadTerms(self,endpoint):
        self.terms = endpoint.listTerms()

class ABoxIndex(Index):
    def __init__(self, endpoint, normalizer) -> None:
        path_index = path_index = "index/temp/a_box_index/faiss"
        super().__init__(path_index, endpoint, normalizer)
    
    def loadTerms(self,endpoint):
        self.terms = endpoint.listResources()
