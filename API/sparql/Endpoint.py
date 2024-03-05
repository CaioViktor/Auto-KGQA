from rdflib import Graph
from rdflib.util import guess_format
from rdflib.plugins.sparql.results.jsonresults import JSONResultSerializer
from SPARQLWrapper import SPARQLWrapper, JSON
from re import finditer,findall
import io
from io import StringIO, BytesIO

def convertToTurtle(triples):
    str_in = StringIO(triples)
    g = Graph()
    g.parse(str_in, format='n3')
    return g.serialize(format="turtle")

class Endpoint:
    def __init__(self,url_endpoint):
        self.url_endpoint = url_endpoint
        self.visited_nodes = set()

    def __str__(self):
        g = Graph()
        return str(g.parse(self.url_endpoint,format=guess_format(self.url_endpoint)).serialize())
        
    def executeQuery(self,query):
        g = Graph()
        graph = g.parse(self.url_endpoint,format=guess_format(self.url_endpoint)).serialize()
        qres = graph.query(query)
        return qres

    def run_sparql(self,query):
        # print(query)
        result_set = []
        if 'http' in self.url_endpoint:
            #Enpoint is a valid remote SPARQL endpoint
            sparql = SPARQLWrapper(self.url_endpoint)
            sparql.setQuery(query)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            for result in results["results"]["bindings"]:
                result_item = {}
                for var in result:
                    if 'datatype' in result[var]:
                        result_item["?"+var] = f'\"{str(result[var]["value"])}\"^^<{str(result[var]["datatype"])}>'
                    else:
                        result_item["?"+var] = str(result[var]["value"])
                result_set.append(result_item)
        else:
            #Enpoint is a local file
            results= self.executeQuery(query)
            encoder = JSONResultSerializer(results)
            output = io.StringIO()
            encoder.serialize(output)
            print(file=output)
            for result in results:
                result_item = {}
                for var in results.vars:
                    result_item["?"+var] = str(result[var])
                result_set.append(result_item)
        return result_set
    
    def getOneResource(self,uri):
        query = f"""SELECT * WHERE{{
                        ?r a <{uri}>.
                        {{
                            SELECT ?r (COUNT(*) as ?qtd) WHERE{{
                                ?r ?s ?o
                            }}GROUP BY ?r
                        }}
                    }} ORDER BY DESC(?qtd)
                    LIMIT 1
                    """
        # print(query)
        result = self.run_sparql(query)
        resourceUri = result[0]["?r"]
        triples = self.describe_(resourceUri,0,2)[0]
        return triples
        
    def describe(self,uri,number_hops=2,limit_by_property=-1):
        triples,is_class = self.describe_(uri,number_hops,limit_by_property)
        if is_class:
            triples += self.getOneResource(uri)
        return triples
    
    def filterAxiomsTriples(self, uri):
        filterPrefixes = ['http://www.w3.org/2002/07/owl#','http://www.w3.org/1999/02/22-rdf-syntax-ns#','http://www.w3.org/2000/01/rdf-schema#','http://www.w3.org/2001/XMLSchema#']
        for filterPrefix in filterPrefixes:
            if uri.startswith(filterPrefix):
                return False
        return True
    
    def filterSelfEquivalenceAxioms(self,s ,p ,o):        
        if str(p) == "http://www.w3.org/2000/01/rdf-schema#subClassOf" and (str(s) == str(o)):
            return False
        if str(p) == "http://www.w3.org/2002/07/owl#equivalentClass" and (str(s) == str(o)):
            return False
        if str(p) == "http://www.w3.org/2002/07/owl#sameAs" and (str(s) == str(o)):
            return False
        return True
    
    def describe_(self,uri,number_hops=2,limit_by_property=-1):
        # print(f"visitando {uri}")
        is_class = False
        self.visited_nodes.add(uri)
        next_nodes = set()
        count_by_property = {}
        describe = ""
        query = f"""SELECT DISTINCT ?p ?o WHERE{{
            <{uri}> ?p ?o.
            FILTER(?o != <http://www.w3.org/2000/01/rdf-schema#Resource>)
            FILTER(?o != <http://www.w3.org/2002/07/owl#Thing>)
        }}"""
        # print(query)
        triples = self.run_sparql(query)
        #outgoing properties
        for triple in triples:
            # print(triple)
            if 'http' in triple["?o"] and not "^^" in triple["?o"]:
                if self.filterSelfEquivalenceAxioms(uri,triple["?p"],triple["?o"]):
                    describe += f"""<{uri}> <{triple["?p"]}> <{triple["?o"]}>.\n"""
                if triple["?p"] == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" and (triple["?o"] == "http://www.w3.org/2000/01/rdf-schema#Class" or triple["?o"] == "http://www.w3.org/2002/07/owl#Class"):
                    is_class = True
                if limit_by_property > -1:
                    if not triple["?p"] in count_by_property:
                        count_by_property[triple["?p"]] = 0
                    if count_by_property[triple["?p"]] < limit_by_property:
                        count_by_property[triple["?p"]]+=1
                        if self.filterAxiomsTriples(triple["?o"]):
                            next_nodes.add(triple["?o"])
                elif self.filterAxiomsTriples(triple["?o"]):
                    next_nodes.add(triple["?o"])
            else:
                if "^^" in triple["?o"]:
                    describe += f"""<{uri}> <{triple["?p"]}> {triple["?o"]}.\n"""
                else:
                    describe += f"""<{uri}> <{triple["?p"]}> "{triple["?o"]}".\n"""
        #ingoing properties
        query = f"""SELECT DISTINCT ?s ?p WHERE{{
            ?s ?p <{uri}>.
            FILTER(?p != <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>)
            FILTER(?s != <http://www.w3.org/2002/07/owl#Nothing>)
        }}"""
        # print(query)
        triples = self.run_sparql(query)
        for triple in triples:
            if self.filterSelfEquivalenceAxioms(triple["?s"],triple["?p"],uri):
                describe += f"""<{triple["?s"]}> <{triple["?p"]}> <{uri}>.\n"""
            if limit_by_property > -1:
                if not triple["?p"] in count_by_property:
                    count_by_property[triple["?p"]] = 0
                if count_by_property[triple["?p"]] < limit_by_property:
                    count_by_property[triple["?p"]]+=1
                    if self.filterAxiomsTriples(triple["?s"]):
                        next_nodes.add(triple["?s"])
            elif self.filterAxiomsTriples(triple["?s"]):
                next_nodes.add(triple["?s"])
        if number_hops > 0:
            number_hops-=1
            for next_node in next_nodes:
                if next_node not in self.visited_nodes:
                    describe += self.describe_(next_node,number_hops,limit_by_property)[0]
        return describe,is_class
    
    def camel_case_split(self,identifier):
        matches = finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
        return " ".join([m.group(0) for m in matches])

    def unpackNumber(self,text):
        number = 0 
        matchs = findall("\"[0-9]+\"",text)
        if len(matchs) > 0:
            number = int(matchs[0].replace("\"","").replace("\'",""))
        return number

    def listTerms(self,language="en",limit=10000):
        query =f"""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT DISTINCT ?term ?type ?label WHERE{{
            {{
                ?term a owl:Class.
                BIND("class" as ?type)
            }}UNION{{
                ?term a rdfs:Class.
                BIND("class" as ?type)
            }}UNION{{
                ?term a rdf:Property.
                BIND("property" as ?type)
            }}UNION{{
                ?term a owl:DatatypeProperty.
                BIND("property" as ?type)
            }}
            UNION{{
                ?term a owl:ObjectProperty.
                BIND("property" as ?type)
            }}
            
        OPTIONAL{{
                ?term rdfs:label ?label1.
                {'FILTER(LANG(?label1) = "'+language+'")' if language != None else ''}
                
            }}
            
            BIND(COALESCE(?label1,?term) as ?label)
        }}
        """
        count_query = query.replace("DISTINCT ?term ?type ?label","(COUNT(DISTINCT *) as ?qtd)")
        # print(query)
        # print(count_query)
        qtd = self.unpackNumber(self.run_sparql(count_query)[0]["?qtd"])
        query_limit_template = query+f"LIMIT {limit} OFFSET $offset"
        results = []
        offset = 0
        while offset < qtd:
            query_limit = query_limit_template.replace("$offset",str(offset))
            offset+=limit
            results+= self.run_sparql(query_limit)
        # print(results)
        for result in results:
            if 'http' in result['?label'] and not '^^' in result['?label']:
                result['?label'] = self.camel_case_split(result['?label'].split("/")[-1].split("#")[-1])
        return results

    def listResources(self,language=None,limit=10000):
        query =f"""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT DISTINCT ?term ?type ?label WHERE{{
            ?term ?p ?o.
            FILTER NOT EXISTS {{
                {{
                    ?term a owl:Class.
                }}UNION{{
                    ?term a rdfs:Class.
                }}UNION{{
                    ?term a rdf:Property.
                }}UNION{{
                    ?term a owl:DatatypeProperty.
                }}
                UNION{{
                    ?term a owl:ObjectProperty.
                }}
            }}
            OPTIONAL{{
                ?term rdfs:label ?label1.
                {'FILTER(LANG(?label1) = "'+language+'")' if language != None else ''}
                
            }}
            BIND("resource" as ?type)
            BIND(COALESCE(?label1,?term) as ?label)
        }}
        """
        count_query = query.replace("DISTINCT ?term ?type ?label","(COUNT(DISTINCT *) as ?qtd)")
        # print(query)
        qtd = self.unpackNumber(self.run_sparql(count_query)[0]["?qtd"])
        query_limit_template = query+f"LIMIT {limit} OFFSET $offset"
        results = []
        offset = 0
        while offset < qtd:
            query_limit = query_limit_template.replace("$offset",str(offset))
            offset+= limit
            results+= self.run_sparql(query_limit)
        for result in results:
            if 'http' in result['?label'] and not '^^' in result['?label']:
                result['?label'] = self.camel_case_split(result['?label'].split("/")[-1].split("#")[-1])
        return results
    
    def countRankResource(self,url):
        query = f"""
            SELECT (COUNT( DISTINCT *) as ?count) WHERE{{
                {{
                    <{url}> ?p ?o.
                }}UNION{{
                    ?s <{url}> ?o.
                }}UNION{{
                    ?s ?p <{url}>.
                }}
            }}
        """
        return int(self.run_sparql(query)[0]["?count"].replace('"^^<http://www.w3.org/2001/XMLSchema#integer>','').replace('"',""))
    
    def struct_result_query(self,sparql):
        query_results = self.run_sparql(sparql)
        question_forumlated = f'''
            {{"query":"```sparql {sparql}```",
            "result": {query_results} }}
            '''
        return question_forumlated,query_results
    
