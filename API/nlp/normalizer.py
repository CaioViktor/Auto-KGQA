import spacy
class Normalizer():
    def __init__(self,language="en"):
        if language == "pt":
            self.nlp = spacy.load('pt_core_news_sm')
        else:
            self.nlp = spacy.load('en_core_web_md')

    def normalizeSentece(self,sentence):
        sentence = sentence.lower()
        doc = self.nlp(sentence)
        result = ""
        for token in doc:
            result+=(token.lemma_)+" "
        return result.strip()