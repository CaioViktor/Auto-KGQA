import spacy
import spacy_dbpedia_spotlight

class Index:
    def __init__(self,path_index=None,endpoint=None,normalizer=None) -> None:
        print("Setting up DBpedia Spotlight service")
        self.type = "SPOTLIGHT"
        self.index = spacy.load('en_core_web_md')
        self.index.add_pipe('dbpedia_spotlight')
        print("DBpedia Spotlight on!")


    def search(self,sentece):
        # print("search: "+term)
        results = []
        results = self.index(sentece).ents
        r = []
        for i in results:
            if i._.dbpedia_raw_result != None:
                data = i._.dbpedia_raw_result
                metadata = {'?term': data['@URI'], '?type': 'resource', '?label': data['@surfaceForm']}
                r.append({'label':data['@surfaceForm'],'content':metadata,'score':float(data['@similarityScore'])})
        results = r
        return results
    
    def exists(self):
        return True

class TBoxIndex(Index):
    def __init__(self, endpoint=None, normalizer=None) -> None:
        super().__init__()

class ABoxIndex(Index):
    def __init__(self, endpoint=None, normalizer=None) -> None:
        super().__init__()
    