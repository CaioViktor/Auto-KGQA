from sparql.Endpoint import convertToTurtle
from nlp.parsers import *
import openai
import re
from context.ContextLLM import *

class QuestionHandler:
    def __init__(self,endpoint,t_box_index,normalizer,messagesTranslater=ContextTranslator(""),messagesNL=ContextNLGenerator(),generalConversation=ContextDialog(),messagesChooseBest = ContextChooseBestSPARQL(""),a_box_index=None,model_name="gpt-3.5-turbo-16k") -> None:
        self.endpoint = endpoint
        self.t_box_index = t_box_index
        self.normalizer = normalizer
        self.messagesTranslater = messagesTranslater
        self.messagesNL = messagesNL
        self.generalConversation = generalConversation
        self.messagesChooseBest = messagesChooseBest
        self.a_box_index = a_box_index
        self.model_name = model_name
    
    def processQuestion(self,question,number_hops=0,limit_by_property=-1):
        self.endpoint.visited_nodes = set()
        triples = self.getRelatedTriples(question,self.t_box_index)
        if self.a_box_index != None:
            # print("a_box_index")
            triples2= self.getRelatedTriples(question,self.a_box_index,number_hops,limit_by_property)
            triples+= triples2
        ttl = convertToTurtle(triples)
        # print("triples:"+ttl)
        self.endpoint.visited_nodes = set()
        self.messagesTranslater.changeGraph(ttl)
        self.messagesChooseBest.changeGraph(ttl)
        llmAnswer,sparqls = self.askQuestion(question)
        llmAnswer['fragments'] = ttl
        llmAnswer['sparqls'] = sparqls
        return llmAnswer
    
    def getRelatedTriples(self,question,index,number_hops=2,limit_by_property=-1):
        # print("getRelatedTriples: "+question)
        matchs = parseText(question,index,self.normalizer,self.endpoint)
        triples = ""
        for match in matchs:
            triples+= self.endpoint.describe(match["content"]["?term"],number_hops,limit_by_property)
        return triples

    def askQuestion(self,question):
        self.messagesTranslater.add({"role":"user","content":question})
        self.generalConversation.add({"role":"user","content":question})
        # completion = openai.ChatCompletion.create(model="gpt-3.5-turbo",messages=messagesTranslater.to_list(),temperature=0.2)
        # print(self.messagesTranslater.to_list())
        completion = openai.ChatCompletion.create(model=self.model_name,messages=self.messagesTranslater.to_list(),n=5)
        results = []
        sparqls = []
        structured_results = []
        for choice in completion.choices:
            sparql = choice.message.content
            try:
                question_forumlated,query_results = self.endpoint.struct_result_query(sparql)
                structured_results.append(question_forumlated)
                results.append(query_results)
                sparqls.append(sparql)
            except:
                sparql = self.extractSPARQL(sparql)
                try:
                    question_forumlated,query_results = self.endpoint.struct_result_query(sparql)
                    structured_results.append(question_forumlated)
                    results.append(query_results)
                    sparqls.append(sparql)
                except:
                    continue
        # sparql = fixQuery(sparql)
        # print(sparql)
        if len(results) > 0:
            self.messagesChooseBest.changeQuestion(question,structured_results)
            completion = openai.ChatCompletion.create(model=self.model_name,messages=self.messagesChooseBest.to_list())
            selection = completion.choices[0].message.content
            # print(f"input:{prompt_best_selection}")
            # print(f"output:{selection}")
            # print("--------------\n"*10)
            # return
            try:
                selection_number = [int(s) for s in re.findall(r'\b\d+\b', selection)] [0]
                sparql_selected = sparqls[selection_number]
                results_selected = results[selection_number]
            except:
            # print(selection_number)
                # print("Escolha deu errado!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                # print(selection)
                selection_number = 0
                sparql_selected = sparqls[selection_number]
                results_selected = results[selection_number]
            # self.messagesTranslater.add({"role":"assistant","content":sparql_selected})

            question_forumlated = f"""
            User question: "{question}";
            SPARQL query:
            ```sparql
            {sparql_selected}
            ```;
            JSON result set:
            ```json
            {results_selected}
            ```;
            """
            self.messagesNL.add({"role":"user","content":question_forumlated})
            completion = openai.ChatCompletion.create(model=self.model_name,messages=self.messagesNL.to_list())
            answer = completion.choices[0].message.content
            self.messagesNL.add({"role":"assistant","content":answer})
            self.messagesTranslater.add({"role":"assistant","content":f"""{{
    "SPARQL":"```sparql\n{sparql_selected}\n```",
    "SPARQL_result":"{results_selected}",
    "answer":"{answer}"
    }}"""})
            if self.generalConversation[-1]["role"] == "assistant":
                self.generalConversation[-1]["content"] = self.generalConversation[-1]["content"] + f"\nSPARQL:```sparql\n{sparql_selected}```\n{answer}"
            else:
                self.generalConversation.add({"role":"assistant","content":f"\nSPARQL:```sparql\n{sparql_selected}```\n{answer}"})
            
            return {'answer':answer,'question':question,'sparql':sparql_selected}, sparqls
        else:
            print("Não gerou consulta SPARQL válida")
            self.generalConversation.add({"role":"user","content":question})
            completion = openai.ChatCompletion.create(model=self.model_name, messages=self.generalConversation.to_list())
            answer = completion.choices[0].message.content
            self.generalConversation.add({"role":"assistant","content":answer})

            return {'answer':answer,'question':question,'sparql':None},[]
    
    
    @staticmethod
    def extractSPARQL(text):
        searchSPARQL = re.search("```(.|\n)*```",text)
        if searchSPARQL is None:
            return ''
        start,end = searchSPARQL.span()
        sparql = text[start:end]
        sparql = sparql.replace("```","").replace("sparql","")
        return sparql
    

    @staticmethod
    def printAnswer(llmAnswer):
        if llmAnswer['sparql'] is not None:
            finalAnswer = f"""User: {llmAnswer['question']}\nGPT: {llmAnswer['answer']}\n\n\n\nSPARQL:\n{llmAnswer['sparql']}\n-------------------------------------------------------------\n"""
        else:
            finalAnswer =f"""User: {llmAnswer['question']}\nGPT: {llmAnswer['answer']}\n-------------------------------------------------------------\n"""
        print(finalAnswer)