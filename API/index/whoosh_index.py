from whoosh.fields import Schema, STORED, ID, KEYWORD, TEXT
from whoosh.index import create_in
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
import json
import os

class Index:
    def __init__(self,path_index,endpoint,normalizer) -> None:
        self.path_index = path_index
        self.endpoint = endpoint
        self.normalizer = normalizer
        self.type = "WHOOSH"
        if not os.path.isdir(path_index):
            print("Creating new index...")
            os.makedirs(path_index)
            self.loadTerms(endpoint)
            self.index = self.create()
            print("New index created!")
        else: 
            print("Loading existing index...")
            self.index = open_dir(self.path_index)
            print("Existing index Loaded!")


    def loadTerms(self,endpoint):
        pass

    def create(self):
        schema = Schema(label=TEXT(stored=True), content=TEXT(stored=True))
        if not os.path.exists(self.path_index):
            os.mkdir(self.path_index)
        ix = create_in(self.path_index,schema)
        writer = ix.writer()
        for term in self.terms:
            label = self.normalizer.normalizeSentece(term["?label"])
            writer.add_document(label=label,content=str(json.dumps(term)))
        writer.commit()
        return ix

    def search(self,term):
        # print("search: "+term)
        results = []
        with self.index.searcher() as searcher:
            parser = QueryParser("label", self.index.schema)
            myquery = parser.parse(term)
            results = searcher.search(myquery)
            r = []
            for i in results:
                r.append({'label':i['label'],'content':json.loads(i['content']),'score':float(i.score)})
            results = r
        return results
    
    def exists(self):
        try:
            if os.path.exists(self.path_index) and open_dir(self.path_index) != None:
                return True
        except:
            return False

class TBoxIndex(Index):
    def __init__(self, endpoint, normalizer) -> None:
        path_index = "index/temp/t_box_index/whoosh"
        super().__init__(path_index, endpoint, normalizer)

    def loadTerms(self,endpoint):
        self.terms = endpoint.listTerms()

class ABoxIndex(Index):
    def __init__(self, endpoint, normalizer) -> None:
        path_index = "index/temp/a_box_index/whoosh"
        super().__init__(path_index, endpoint, normalizer)

    def loadTerms(self,endpoint):
        self.terms = endpoint.listResources()