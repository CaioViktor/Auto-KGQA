from rdflib import Graph
from rdflib.term import URIRef
from io import StringIO
import re

def getGraph(triples):
    triples = triples.replace("\\&","")
    str_in = StringIO(triples)
    g = Graph()
    g.parse(str_in, format='n3')
    return g

def uri_to_rdflib_ref(uri):
    return URIRef(uri.replace("<","").replace(">",""))

def uris_list_to_rdflib_refs_list(uris):
    results = []
    for uri in uris:
        results.append(uri_to_rdflib_ref(uri))
    return results

def convertToTurtle(triples):
    g = getGraph(triples)
    return g.serialize(format="turtle")

def isLabel(property):
    labels= ["http://www.w3.org/2000/01/rdf-schema#label",
            "http://xmlns.com/foaf/0.1/name",
            "http://www.w3.org/2004/02/skos/core#prefLabel",
            "http://purl.org/dc/terms/title",
            "http://purl.org/dc/elements/1.1/title",
            "http://dbpedia.org/ontology/name",
            "http://dbpedia.org/property/name",
            "http://dbpedia.org/ontology/label",
            "http://dbpedia.org/property/label",]
    for label in labels:
        if str(property) == label:
            return True
    return False

def list_to_string_triples(triples):
    triples_str = ""
    for triple in triples:
        triples_str+= f"<{triple[0]}> <{triple[1]}> "
        if triple[2].__class__ == URIRef:
            triples_str+=f"<{triple[2]}>.\n"
        else:
            value = str(triple[2])
            if "\n" in value:
                value = '"""'+value+'"""'
            else:
                value = '"'+value+'"'
            if triple[2].datatype:
                triples_str+=f"{value}^^<{triple[2].datatype}>.\n"
            else:
                triples_str+=f"{value}.\n"
    return triples_str

def list_to_rdf_graph(triples):
    triples_str = ""
    for triple in triples:
        triples_str+= f"<{triple[0]}> <{triple[1]}> "
        if triple[2].__class__ == URIRef:
            triples_str+=f"<{triple[2]}>.\n"
        else:
            value = f"\"{triple[2]}\"^^<{triple[2].datatype}>.\n"
            if "\n" in value:
                value = value.replace('"','"""')
            triples_str+= value
    graph = getGraph(triples_str)
    return graph

def edges_to_triples(edges,graph):
    triples = set()
    properties = set()
    for edge in edges:
        if edge not in graph.edges:
            # print("inverse triple: "+str(edge))
            triples.add((edge[1],edge[2],edge[0]))
        else:
            triples.add((edge[0],edge[2],edge[1]))
        properties.add(edge[2])
    return list(triples),properties


def getPrefixes_from_query(q):
    prefix_uri_template = "PREFIX .*"
    prefixes_str = re.findall(prefix_uri_template,q,flags=re.IGNORECASE)
    new_q = q
    prefixes = {}
    for prefix_str in prefixes_str:
        new_q = new_q.replace(prefix_str,"")
        prefix_str = prefix_str[7:]
        sep = prefix_str.index(" ")
        prefix_name = prefix_str[0:sep].strip()
        prefix_uri = prefix_str[sep:].strip().replace("<","").replace(">","")
        prefixes[prefix_name] = prefix_uri

    return prefixes,new_q

def getExplicitUris_from_query(q):
    explicit_uri_template = "<.*?>"
    uris = []
    new_q = q
    uris_found = re.findall(explicit_uri_template,q,flags=re.IGNORECASE)
    for uri in uris_found:
        uris.append(uri.replace("<","").replace(">",""))
        new_q = new_q.replace(uri,"")
    return uris,new_q


def getImplicitUris_from_query(prefixes, q):
    implict_uri_template = "\S*:\S*"
    resources = set()
    new_q = q
    ignore_prefixes = ['rdfs:','rdf:','owl:']
    uris = re.findall(implict_uri_template,q)
    for uri in uris:
        uri = uri.replace(";","").replace(",","").replace("]","").replace("[","")
        
        if "[" in uri:
            uri = uri[uri.index("[")+1:]
        if "(" in uri:
            uri = uri[uri.index("(")+1:]

        if "]" in uri:
            uri = uri[:uri.index("")]
        if ")" in uri:
            uri = uri[:uri.index(")")]

        sep = uri.find(":")
        prefix_name = uri[0:sep+1].strip()
        body = uri[sep+1:].strip()
        if body[-1]==".":
            body= body[:-1]
        # print(prefix_name)
        if prefix_name not in ignore_prefixes:
            resources.add(prefixes[prefix_name]+body)
        new_q = new_q.replace(uri,"")
        
    return list(resources), new_q


def getUris_from_query(q):
    uris = []
    prefixes,q = getPrefixes_from_query(q)
    uris_explicit,q = getExplicitUris_from_query(q)
    uris_implicit,q = getImplicitUris_from_query(prefixes, q)

    uris = uris_explicit + uris_implicit
    return list(set(uris)),q