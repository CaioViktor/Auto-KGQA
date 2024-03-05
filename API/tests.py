from sparql.Endpoint import Endpoint
endpoint = Endpoint("http://localhost:7200/repositories/artigo")
terms = endpoint.listTerms()
print("Endpoint Test:")
print(terms)

from nlp.normalizer import *
from index.whoosh_index import *

normalizer = Normalizer()

print("T-Box index Test:")
t_box_index = TBoxIndex(endpoint,normalizer)
result_t_box = t_box_index.search("Person")
print(result_t_box)
print("-----------------------------------------------------------")

print("A-Box index Test:")
a_box_index = ABoxIndex(endpoint,normalizer)
result_a_box = a_box_index.search("John")
print(result_a_box)
print("-----------------------------------------------------------")

from context.ContextLLM import *

print("Creating ContextTranslator...")
messagesTranslater = ContextTranslator("")
print("ContextTranslator created with success!")
print("--------------------------------------------------")
print("Creating ContextNLGenerator...")
messagesNL = ContextNLGenerator()
print("ContextNLGenerator created with success!")
print("--------------------------------------------------")
print("Creating ContextDialog...")
generalConversation = ContextDialog()
print("ContextDialog created with success!")
print("--------------------------------------------------")
print("Creating ContextChooseBestSPARQL...")
messagesChooseBest = ContextChooseBestSPARQL("")
print("ContextChooseBestSPARQL created with success!")
print("--------------------------------------------------")


from core.QuestionHandler import QuestionHandler
import json
print("Creatin QuestionHandler...")
qa = QuestionHandler(endpoint,t_box_index,normalizer,a_box_index=a_box_index)

question = "Who is John?"
print("Processing question: "+question)
result = qa.processQuestion(question)
# print(json.dumps(result,indent=4))
qa.printAnswer(result)
print("--------------------------------------------------")

question = "List all the persons"
print("Processing question: "+question)
result = qa.processQuestion(question)
# print(json.dumps(result,indent=4))
qa.printAnswer(result)
print("--------------------------------------------------")