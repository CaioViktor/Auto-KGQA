import tiktoken
from configs import *
from core.QuestionHandler import QuestionHandler
from dotenv import load_dotenv
from nlp.normalizer import *
from datetime import datetime

from core.ChatHandler import ChatHandler
from core.Configs_loader import load_configs

#OpenAI
load_dotenv()

#KG endpoints and indexes
normalizer, endpoint_t_box, t_box_index, endpoint_a_box, a_box_index = load_configs()

def countTokens(input):
    encoding = tiktoken.encoding_for_model(LLM_MODEL)
    encoded = encoding.encode(input)
    # print(encoded)
    return len(encoded)



question = "What is John's age?" #Natural Language Question
# question = "What is the most common Knowledge representation method?" #Natural Language Question
print(f"Question: "+question)

qa = QuestionHandler(endpoint_a_box,endpoint_t_box,t_box_index,normalizer,a_box_index=a_box_index,model_name=LLM_MODEL)
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

