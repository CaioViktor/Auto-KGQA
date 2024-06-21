import tiktoken
import pandas as pd
from configs import *
from core.QuestionHandler import QuestionHandler
from dotenv import load_dotenv
from nlp.normalizer import *
from sparql.Endpoint import Endpoint
from datetime import datetime
#Import T-Box index
from index.import_index import *

from core.ChatHandler import ChatHandler

#OpenAI
load_dotenv()

#Normalizer
normalizer = Normalizer()

#T-Box
endpoint_t_box = Endpoint(ENDPOINT_T_BOX_URL)
t_box_index = TBoxIndex(endpoint_t_box,normalizer)

#A-Box
endpoint_a_box = endpoint_t_box
if ENDPOINT_A_BOX_URL and ENDPOINT_T_BOX_URL != ENDPOINT_A_BOX_URL:
    endpoint_a_box = Endpoint(ENDPOINT_A_BOX_URL)
a_box_index = ABoxIndex(endpoint_a_box,normalizer)

def countTokens(input):
    encoding = tiktoken.encoding_for_model(LLM_MODEL)
    encoded = encoding.encode(input)
    # print(encoded)
    return len(encoded)



question = "What is John's age?" #Natural Language Question

print(f"Question: "+question)

qa = QuestionHandler(endpoint_a_box,t_box_index,normalizer,a_box_index=a_box_index,model_name=LLM_MODEL)
# result = qa.processQuestion(question)
# print(f"consulta  finalizada: "+result['answer'])

ttl = qa.getRelevantGraph(question)
print("KG Given to LLM:")
print(ttl)

queries,results,selected = qa.textToSPARQL(question,ttl)
for idx,q in enumerate(queries):
    print("Query "+str(idx)+":")
    print(q)
    print("result:")
    print(str(results[idx]))
    print("----------------------------------")
print("Query choosed: "+str(selected))
print(queries[selected])


sparql_selected = queries[selected]
results_selected = results[selected]
answer = qa.generateNLResponse(question,sparql_selected,results_selected)
print("answer:")
print(answer)

