from configs import *
from sparql.Endpoint import *
from sparql.Utils import convertToTurtle
import os

class Generator_T_Box:
    def __init__(self,endpoint) -> None:
        self.classes= {}
        self.properties= {}
        self.endpoint = endpoint
        temp_dir = "sparql/temp"
        if not os.path.isdir(temp_dir):
            os.makedirs(temp_dir)
    
    def extract_classes_explicit(self):
        query = """
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX dbp: <http://dbpedia.org/property/>
        SELECT DISTINCT ?term ?label ?comments ?superclass WHERE{
            {
                ?term a owl:Class
            }UNION{
                ?term a rdfs:Class
            }
            OPTIONAL{
                    ?term ?property ?label.
                    FILTER(
                        ?property = rdfs:label ||
                        ?property = foaf:name ||
                        ?property = skos:prefLabel ||
                        ?property = dc:title ||
                        ?property = dcterms:title ||
                        ?property = dbo:name ||
                        ?property = dbp:name ||
                        ?property = dbo:name ||
                        ?property = dbp:name 
                    )                
                }
            OPTIONAL{
                ?term rdfs:comment ?comments
            }
            OPTIONAL{
                ?term rdfs:subClassOf ?superclass
                FILTER(?term != ?superclass)
            }
        }
        """
        classes_= self.endpoint.run_sparql(query)
        return classes_
    
    def extract_classes_implicit(self):
        query = """
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX dbp: <http://dbpedia.org/property/>
        SELECT DISTINCT ?term ?label ?comments ?superclass WHERE{
            ?a a ?term.
            OPTIONAL{
                    ?term ?property ?label.
                    FILTER(
                        ?property = rdfs:label ||
                        ?property = foaf:name ||
                        ?property = skos:prefLabel ||
                        ?property = dc:title ||
                        ?property = dcterms:title ||
                        ?property = dbo:name ||
                        ?property = dbp:name ||
                        ?property = dbo:name ||
                        ?property = dbp:name 
                    )                
                }
            OPTIONAL{
                ?term rdfs:comment ?comments
            }
            OPTIONAL{
                ?term rdfs:subClassOf ?superclass
                FILTER(?term != ?superclass)
            }
        }
        """
        classes_= self.endpoint.run_sparql(query)
        return classes_
    
    def parser_classes(self, classes, classes_):
        for class_ in classes_:
            if class_['?term'] not in classes:
                classes[class_['?term']] = {'uri':class_['?term'],'super_classes':set(),'labels':set(),'comments':set(),'count':'"1"^^<http://www.w3.org/2001/XMLSchema#integer>'}
            if '?label' in class_:
                classes[class_['?term']]['labels'].add(class_['?label'])
            if '?superclass' in class_:
                classes[class_['?term']]['super_classes'].add(class_['?superclass'])
            if '?comments' in class_:
                classes[class_['?term']]['comments'].add(class_['?comments'])
        return classes
    
    def count_relevance_classes(self,classes):
        query = """
        SELECT ?term (COUNT(*) as ?qtd)  WHERE{
            ?a a ?term.
            FILTER(!REGEX(STR(?term),"http://www.w3.org/2002/07/owl#","i"))
            FILTER(!REGEX(STR(?term),"http://www.w3.org/2000/01/rdf-schema#","i"))
            FILTER(!REGEX(STR(?term),"http://www.w3.org/1999/02/22-rdf-syntax-ns#","i"))
            FILTER(!REGEX(STR(?term),"http://www.w3.org/2001/XMLSchema#","i"))  
            FILTER(!REGEX(STR(?term),"http://www.ontotext.com/","i"))  
            
        }GROUP BY ?term
        """
        classes_counts= self.endpoint.run_sparql(query)
        for count in classes_counts:
            if count['?term'] in classes:
                classes[count['?term']]['count'] = count['?qtd']
        return classes
    
    def triplefy_classes(self,classes):
        #classes[uri] = {'uri':class_['?term'],'super_classes':set(),'labels':set(),'comments':set(),'count':'"1"^^<http://www.w3.org/2001/XMLSchema#integer>''}
        triples = "# Classes\n"
        for uri in classes:
            class_ = classes[uri]
            triples_class = f"<{uri}> a owl:Class.\n"
            if len(class_['super_classes']) > 0:
                for super_class in class_['super_classes']:
                    triples_class += f"<{uri}> rdfs:subClassOf <{super_class}>.\n"
            if len(class_['labels']) > 0:
                for label in class_['labels']:
                    triples_class += f'<{uri}> rdfs:label "{label}".\n'
            else:
                triples_class += f'<{uri}> rdfs:label "{self.endpoint.uri_to_label(uri)}".\n'
            if len(class_['comments']) > 0:
                for comment in class_['comments']:
                    triples_class += f'<{uri}> rdfs:comment "{comment}".\n'
                triples_class += f'<{uri}> rdfs:comment "{comment}".\n'
            triples_class += f'<{uri}> kgqa:count {class_["count"]}.\n'
            triples+=triples_class
        return triples
    
    def extract_properties_explicit(self):
        query = """
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX dbp: <http://dbpedia.org/property/>
        SELECT DISTINCT ?term ?label ?comments ?superproperty ?domain ?range WHERE{
            {
                ?term a rdf:Property
            }UNION{
                ?term a  owl:DatatypeProperty
            }UNION{
                ?term a  owl:ObjectProperty
            }UNION{
                ?term rdfs:domain ?domain
            }
            UNION{
                ?term rdfs:range ?range
            }
            OPTIONAL{
                ?term ?property ?label.
                FILTER(
                    ?property = rdfs:label ||
                    ?property = foaf:name ||
                    ?property = skos:prefLabel ||
                    ?property = dc:title ||
                    ?property = dcterms:title ||
                    ?property = dbo:name ||
                    ?property = dbp:name ||
                    ?property = dbo:name ||
                    ?property = dbp:name 
                )                
            }
            OPTIONAL{
                ?term rdfs:comment ?comments
            }
            OPTIONAL{
                ?term rdfs:subPropertyOf ?superproperty
                FILTER(?term != ?superproperty)
            }
            OPTIONAL{
                ?term rdfs:domain ?domain
            }
            OPTIONAL{
                ?term rdfs:range ?range
            }
        }
        """
        properties_= self.endpoint.run_sparql(query)
        return properties_
    
    
    def extract_properties_implicit(self):
        query = """
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX dbp: <http://dbpedia.org/property/>
        SELECT DISTINCT ?term ?label ?comments ?superproperty ?domain ?range WHERE{
            ?a ?term ?b.
            FILTER(?term!=rdf:type)
            FILTER(?term!=rdfs:subPropertyOf)
            FILTER(?term!=rdfs:subClassOf)
            FILTER(?term!=rdfs:domain)
            FILTER(?term!=rdfs:range)
            FILTER(?term!=rdfs:comment)
            FILTER(?term!=owl:sameAs)
            FILTER(?term!=owl:equivalentProperty)
            FILTER(?term!=owl:equivalentClass)
            OPTIONAL{
                ?term ?property ?label.
                FILTER(
                    ?property = rdfs:label ||
                    ?property = foaf:name ||
                    ?property = skos:prefLabel ||
                    ?property = dc:title ||
                    ?property = dcterms:title ||
                    ?property = dbo:name ||
                    ?property = dbp:name ||
                    ?property = dbo:name ||
                    ?property = dbp:name 
                )                
            }
            OPTIONAL{
                ?term rdfs:comment ?comments
            }
            OPTIONAL{
                ?term rdfs:subPropertyOf ?superproperty
                FILTER(?term != ?superproperty)
            }
            OPTIONAL{
                ?a a ?domain
            }
            OPTIONAL{
                ?b a ?range
            }
        }
        """
        properties_= self.endpoint.run_sparql(query)
        return properties_
    
    def parser_properties(self, properties, properties_):
        for property in properties_:
            if property['?term'] not in properties:
                properties[property['?term']] = {'uri':property['?term'],'super_properties':set(),'labels':set(),'comments':set(),'domain':set(),'range':set(),'count':'"1"^^<http://www.w3.org/2001/XMLSchema#integer>'}
            if '?label' in property:
                properties[property['?term']]['labels'].add(property['?label'])
            if '?superproperty' in property:
                properties[property['?term']]['super_properties'].add(property['?superproperty'])
            if '?comments' in property:
                properties[property['?term']]['comments'].add(property['?comments'])
            if '?domain' in property:
                properties[property['?term']]['domain'].add(property['?domain'])
            if '?range' in property:
                properties[property['?term']]['range'].add(property['?range'])
        return properties
    
    def triplefy_properties(self,properties):
        #properties[uri] = {'uri':property['?term'],'super_properties':set(),'labels':set(),'comments':set(),'domain':set(),'range':set(),'count':'"1"^^<http://www.w3.org/2001/XMLSchema#integer>'}
        triples = "# Properties\n"
        for uri in properties:
            property = properties[uri]
            triples_class = f"<{uri}> a rdf:Property.\n"
            if len(property['super_properties']) > 0:
                for super_class in property['super_properties']:
                    triples_class += f"<{uri}> rdfs:subClassOf <{super_class}>.\n"
            if len(property['domain']) > 0:
                for domain in property['domain']:
                    triples_class += f"<{uri}> rdfs:domain <{domain}>.\n"
            if len(property['range']) > 0:
                for range in property['range']:
                    triples_class += f"<{uri}> rdfs:range <{range}>.\n"
            if len(property['labels']) > 0:
                for label in property['labels']:
                    triples_class += f'<{uri}> rdfs:label "{label}".\n'
            else:
                triples_class += f'<{uri}> rdfs:label "{self.endpoint.uri_to_label(uri)}".\n'
            if len(property['comments']) > 0:
                for comment in property['comments']:
                    triples_class += f'<{uri}> rdfs:comment "{comment}".\n'
            triples_class += f'<{uri}> kgqa:count {property["count"]}.\n'
            triples+=triples_class
        return triples
    
    def count_relevance_properties(self,properties):
        query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        SELECT ?term (COUNT(*) as ?qtd)  WHERE{
            ?a ?term ?b.
            FILTER(?term!=rdf:type)
            FILTER(?term!=rdfs:subPropertyOf)
            FILTER(?term!=rdfs:subClassOf)
            FILTER(?term!=rdfs:domain)
            FILTER(?term!=rdfs:range)
            FILTER(?term!=rdfs:comment)
            FILTER(?term!=owl:sameAs)
            FILTER(?term!=owl:equivalentProperty)
            FILTER(?term!=owl:equivalentClass)
            
        }GROUP BY ?term
        """
        properties_counts= self.endpoint.run_sparql(query)
        for count in properties_counts:
            if count['?term'] in properties:
                properties[count['?term']]['count'] = count['?qtd']
        return properties
    
    def generate_t_box(self)->str:
        classes_explicit = self.extract_classes_explicit()
        print("Explicit classes: "+str(len(classes_explicit)))
        self.classes = self.parser_classes(self.classes,classes_explicit)
        classes_implicit = self.extract_classes_implicit()
        print("Implicit classes: "+str(len(classes_implicit)))
        self.classes = self.parser_classes(self.classes,classes_implicit)
        print("Unique Classes: "+str(len(self.classes)))
        self.classes = self.count_relevance_classes(self.classes)
        triples_classes = self.triplefy_classes(self.classes)

        properties_explicit = self.extract_properties_explicit()
        print("Explicit properties: "+str(len(properties_explicit)))
        self.properties = self.parser_properties(self.properties,properties_explicit)
        properties_implicit = self.extract_properties_implicit()
        print("Implicit properties: "+str(len(properties_implicit)))
        self.properties = self.parser_properties(self.properties,properties_implicit)
        print("Unique properties: "+str(len(self.properties)))
        self.properties = self.count_relevance_properties(self.properties)
        triples_properties = self.triplefy_properties(self.properties)

        triples_full = """@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        @prefix owl: <http://www.w3.org/2002/07/owl#> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        @prefix kgqa: <http://www.kgqa.com/>.
        
        """
        triples_full+= triples_classes+"\n\n"+triples_properties
        triples_full_ttl = convertToTurtle(triples_full)
        return triples_full_ttl




    