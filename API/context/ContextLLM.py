class ContextDialog:
    def __init__(self,length=7,language="en"):
        self.system = []
        self.content = []
        self.maxLength = length
        self.language = language

    def add(self,item):
        if len(self.content) > self.maxLength:
            self.content.pop(0)
        self.content.append(item)

    def to_list(self):
        return self.system + self.content
    
    def __len__(self):
        return len(self.content)
    
    def __getitem__(self, i): 
        return self.content[i]
    
    def __setitem__(self, i, v):
        self.content[i] = v
    def __str__(self):
        return str(self.system + self.content)
    


class ContextTranslator(ContextDialog):
    restrictions = """
    - Use only classes and properties defined in the RDF graph, for this is important to use the same URIs for the properties and classes as defined in the original graph;
    - Include all the the prefixes used in the SPARQL query;
    - Declare non-essential properties to the question as OPTIONAL if needed;
    - DO NOT use specific resources in the query;
    - Declare filters on strings (like labels and names) as filters operations over REGEX function using the case insensitive flag."""
    def __init__(self,graph,length=7,language="en"):
        super().__init__(length,language)
        self.changeGraph(graph)
    
    def changeGraph(self,graph):
        self.system = []
        if self.language == "en":
            self.system.append({"role":"system","content":"Consider the following RDF graph written in Turtle syntax: "+str(graph)})
            # self.system.append({"role":"system","content":"""Write a SPARQL query for the question given by the user using only classes and properties defined in the RDF graph, for this is important to use the same URIs for the properties and classes as defined in the original graph. Also remember to include the prefixes. Moreover declare non-essential properties to the question as OPTIONAL if needed. Declare filters on strings (like labels and names) as filters operations over REGEX function using the case insensitive flag, for example use '''?a rdfs:label ?name. FILTER(REGEX(?name,"[VALUE NAME]","i"))''' instead of '''?a rdfs:label "[VALUE NAME]".''' ."""})
            self.system.append({"role":"system","content":f"""Write a SPARQL query for the question given by the user following the restrictions: \n{self.restrictions}
                Example:
                    Question: 'Who is Caio?'
                    Answer: ```sparql
                        SELECT ?caio ?name WHERE{{
                            ?caio rdfs:label ?name.
                            FILTER(REGEX(?name,"Caio","i"))
                        }}```
                            """})
        elif self.language ==  "pt":
            self.system.append({"role":"system","content":"Considere o seguinte grafo RDF escrito na sintaxe Turtle: "+str(graph)})
            self.system.append({"role":"system","content":"""Escreva uma consulta SPARQL para a questão dada pelo usuário utilizando apenas classes e propriedades definidas no grafo RDF, para isso é importante utilizar as mesmas URIs para as propriedades e classes como definidas no grafo original. Também é importante lembrar de incluir os prefixos. Além disso, declare propriedades não essenciais para a questão como como OPTINAL se necessárias. Declare filtros sobre strings (como labels e nomes) como operações de filtros sobre funções REGEX usando a flaf case insensitive, por exemplo use '''?a rdfs:label ?name. FILTER(REGEX(?name,"[VALUE NAME]","i"))''' ao invés de '''?a rdfs:label "[VALUE NAME]".'''"""})





class ContextChooseBestSPARQL(ContextDialog):
    def __init__(self,length=7):
        super().__init__(length)
        
    def changeGraph(self,graph):
        self.system = []
        self.system.append({"role":"system","content":"Consider the following RDF graph written in Turtle syntax: "+str(graph)})

    def changeQuestion(self,question,structured_results):
        prompt_best_selection = f"""
        Given the question: "{question}"
        Select the number of the option that better representes a SPARQL query for the given question:
        ```json
        {{"""

        for idx,structured_result in enumerate(structured_results):
            prompt_best_selection+= f"""{idx}:{structured_result},\n"""
        
        prompt_best_selection+= f"""}}```
        Use the following criteria to evaluate the options: {ContextTranslator.restrictions}
        Return only the number of the selected option and nothing more!"""
        # print(prompt_best_selection)
        self.system.append({"role":"system","content":prompt_best_selection})


     
        
        
class ContextNLGenerator(ContextDialog):
    def __init__(self,length=7,language="en"):
        super().__init__(length,language)
        if self.language == "en":
            self.system.append({"role":"system","content":"Use the SPARQL query and its result set as JSON object to write a answer to the user question. Remember to show the URIs of the objects you use in your response as plain text. DO NOT explain neither cite the SPARQL query and JSON in yours response."})
        elif self.language ==  "pt":
            self.system.append({"role":"system","content":"Use a consulta SPARQL e seu conjunto de resultados como um objeto JSON para responder a questão do usuário"})
