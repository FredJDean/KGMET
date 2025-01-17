import re

from SPARQLWrapper import SPARQLWrapper, JSON
from typing import List, Literal, Optional
from urllib.error import HTTPError
import json
import time


# Wikidata query service setting
wikidata_url = "https://query.wikidata.org/sparql"
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36" # HTTP User-Agent header
sparql = SPARQLWrapper(wikidata_url, agent=user_agent)

def safe_sparql_request(sparql):
    """Make a SPARQL request with error handling."""
    while True:
        try:
            # Requests that make too many calls may result in a 429 error.
            results = sparql.query().convert()
            return results

        except HTTPError as e:
            if e.code == 429:
                print("429 error occurred. Pausing execution for a while...")
                time.sleep(15)  # Sleep for 15 seconds before retrying.
            else:
                # If the error code is not 429, re-raise the exception.
                raise e


# According to the property id, get the label of the relation.
def get_property_label(property_id: str) -> str:
    """Get the label of a property given its ID."""
    queryString = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX wikibase: <http://wikiba.se/ontology#>
    PREFIX bd: <http://www.bigdata.com/rdf#>

    SELECT ?propertyLabel WHERE {
    wd:%s rdfs:label ?propertyLabel.
    FILTER(LANG(?propertyLabel) = "en")
    }
    """ % property_id

    sparql.setQuery(queryString)
    sparql.setTimeout(30)
    sparql.setReturnFormat(JSON)

    max_retries = 5

    # results = sparql.query().convert()

    for attempt in range(max_retries):
        try:
            sparql.setQuery(queryString)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            return results['results']['bindings'][0]['propertyLabel']['value']
        except Exception as e:
            print(f"Error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                print("Retrying...")
                time.sleep(5)  # 等待5秒后重试
            else:
                print("Max retries reached, failing.")
                return None

    # return results['results']['bindings'][0]['propertyLabel']['value']


# According to the item id, get the neighbor triples of the entity.
def get_neighbor_triples(item_id: str) -> str:
    """Get the triples of the neighbors of an entity given its ID."""
    queryString = """
    CONSTRUCT {
      ?s ?p ?o .
      ?p rdfs:label ?pLabel .
      ?o rdfs:label ?oLabel .
    } 
    WHERE { 
      BIND(wd:%s AS ?s) 
      ?s ?p ?o .
      ?wdProp wikibase:directClaim ?p .
      
      SERVICE wikibase:label {
        bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". 
        ?wdProp rdfs:label ?pLabel .
        ?o rdfs:label ?oLabel .
      }

      FILTER(STRSTARTS(STR(?p), STR(wdt:))) .
      FILTER(STRSTARTS(STR(?o), STR(wd:))) .
      FILTER(!STRSTARTS(STR(?p), STR(wdt:P910))) .
      FILTER(!STRSTARTS(STR(?p), STR(wdt:P1423))) .
    } 
    """ % item_id

    sparql.setQuery(queryString)

    sparql.setReturnFormat(JSON)
    label = sparql.query().convert()

    return label


def extract_wikidata_id(url: str) -> str:
    """从维基数据的URL中提取ID部分（例如 Q459180）。"""
    match = re.search(r'\/entity\/(Q\d+)', url)
    if match:
        return match.group(1)
    return None

def get_property_id_from_label(property_label: str) -> str:
    """根据给定的标签查找属性ID。"""
    queryString = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX wikibase: <http://wikiba.se/ontology#>
    PREFIX bd: <http://www.bigdata.com/rdf#>

    SELECT ?property WHERE {
      ?property rdfs:label "%s"@en.
    }
    """ % property_label

    sparql.setQuery(queryString)
    sparql.setTimeout(30)
    sparql.setReturnFormat(JSON)

    max_retries = 5

    for attempt in range(max_retries):
        try:
            results = sparql.query().convert()
            if results['results']['bindings']:
                # 返回找到的第一个属性ID
                property_url = results['results']['bindings'][0]['property']['value']
                property_id = extract_wikidata_id(property_url)
                return property_id
            else:
                print(f"No property found with label '{property_label}'.")
                return None
        except Exception as e:
            print(f"Error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                print("Retrying...")
                time.sleep(5)  # 等待5秒后重试
            else:
                print("Max retries reached, failing.")
                return None


def get_neighbor_triples_by_label(label: str) -> str:
    item_id = get_property_id_from_label(label)
    print("id:", item_id)
    """Get the triples of the neighbors of an entity given its ID."""
    queryString = """
    CONSTRUCT {
      ?s ?p ?o .
      ?p rdfs:label ?pLabel .
      ?o rdfs:label ?oLabel .
    } 
    WHERE { 
      BIND(wd:%s AS ?s) 
      ?s ?p ?o .
      ?wdProp wikibase:directClaim ?p .

      SERVICE wikibase:label {
        bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". 
        ?wdProp rdfs:label ?pLabel .
        ?o rdfs:label ?oLabel .
      }

      FILTER(STRSTARTS(STR(?p), STR(wdt:))) .
      FILTER(STRSTARTS(STR(?o), STR(wd:))) .
      FILTER(!STRSTARTS(STR(?p), STR(wdt:P910))) .
      FILTER(!STRSTARTS(STR(?p), STR(wdt:P1423))) .
    } 
    """ % item_id

    sparql.setQuery(queryString)

    sparql.setReturnFormat(JSON)
    label = sparql.query().convert()

    return label