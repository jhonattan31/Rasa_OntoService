from asyncio.windows_events import NULL
from email import message
from pandas import notnull
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Text, Dict, Any, List
from rdflib import Graph, Literal, RDF, URIRef, Namespace 
from rdflib.namespace import XSD, SKOS, OWL, RDFS
from SPARQLWrapper import SPARQLWrapper, JSON
import requests

def ActionResult(query):
    query += """\n      } \n LIMIT 1"""
    #g = Graph()
    #g = g.parse("C:\\Users\\jh0nn\\Documents\\TesteRasas\\rasa_ontologias_exemplo-master\\testexml.owl", format="application/rdf+xml")     
    #serv = Namespace("http://servicos.gov.ce.br/")
    #g.bind("serv", serv)
    #qres = g.query(query)
    #for row in qres:
    #    print(row) 
    print(query)
    sparql = SPARQLWrapper("http://localhost:3030/onto_service/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    print(results)

    #for result in results["results"]["bindings"]:
    #    print(result["nome"]["value"])     
    #dispatcher.utter_message(text=row)    
    
    return results

class ActionHorFunc(Action):
    def name(self) -> Text:
        return "action_hor_func"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.latest_message['intent']
        entities = tracker.latest_message['entities']
        neg = False
        print(intent.get('name'))
        query = ""

        for entity in tracker.latest_message['entities']:
            entity_saved = False
            for i in range(0, len(entities)):
                if(entities[i]['value'] == entity['value'] or (entities[i]['start'] >= entity['start'] and entities[i]['end'] <= entity['end']) or (entity['start'] >= entities[i]['start'] and entity['end'] <= entities[i]['end'])):
                    entity_saved = True
                    if(entity['extractor'] == 'RegexEntityExtractor'):
                        entities[i] = entity
            if(not entity_saved):
                entities.append(entity)

        if(intent.get('name') == 'hor_func'):
            query = """PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n PREFIX serv: <http://servicos.gov.ce.br/>\n SELECT ?uri ?nome ?time\n        WHERE {\n           ?uri rdfs:label ?nome. """     
            for entity in entities:
                print(entity['entity'])
                if(entity['entity'] == 'nomServico'):
                    print("Valor do campo nomServico: " + entity['value'])
                    query+= """\n           FILTER CONTAINS (?nome, "{}").""".format((entity['value']).lower())                      
                elif(entity['entity'] == 'horarioAtendimento'):
                    print("Valor do campo horario atendimento: " + entity['value'])
                    query += """\n          ?uri serv:horarioAtendimento ?time .""" 
                    query += """\n           FILTER CONTAINS (?time, "{}").""".format((entity['value']).lower())                                                                      
        results = ActionResult(query)
        resposta = "Encontramos a seguinte resposta para sua consulta: \n" 
        for result in results["results"]["bindings"]:
            resposta += result["nome"]["value"] + "\n"
            resposta += result["time"]["value"] + "\n"
        dispatcher.utter_message(text=resposta)
        return []

class ActionAcesso(Action):
    def name(self) -> Text:
        return "action_acesso"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.latest_message['intent']
        entities = tracker.latest_message['entities']
        neg = False
        print(intent.get('name'))
        query = ""
        for entity in tracker.latest_message['entities']:
            entity_saved = False
            for i in range(0, len(entities)):
                if(entities[i]['value'] == entity['value'] or (entities[i]['start'] >= entity['start'] and entities[i]['end'] <= entity['end']) or (entity['start'] >= entities[i]['start'] and entity['end'] <= entities[i]['end'])):
                    entity_saved = True
                    if(entity['extractor'] == 'RegexEntityExtractor'):
                        entities[i] = entity
            if(not entity_saved):
                entities.append(entity)

        if(intent.get('name') == 'forma_acesso'):
            query = """PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n PREFIX serv: <http://servicos.gov.ce.br/>\n SELECT ?uri ?nome ?acPresen ?acRemote\n      WHERE {\n           ?uri rdfs:label ?nome. """
            for entity in entities:
                print(entity['entity'])
                if (entity['entity'] == 'acessoPres'):
                    query += """\n          ?uri serv:acessoPres ?acPresen."""
                elif (entity['entity'] == 'acessoOnline'):
                    query += """\n          ?uri serv:acessoOnline ?acRemote.\n         FILTER (!EXISTS{\n              FILTER (?acPresen = "S") .\n                FILTER (?acRemote = "N") .\n            }) ."""
                elif(entity['entity'] == 'nomServico'):
                    query+= """\n           FILTER CONTAINS (?nome, "{}").""".format((entity['value']).lower())
        results = ActionResult(query)
        resposta = "Encontramos a seguinte resposta para sua consulta: \n" 
        for result in results["results"]["bindings"]:
            resposta += result["nome"]["value"] + "\n"
            resposta += result["acPresen"]["value"] + "\n"
            resposta += result["?acRemote"]["value"] + "\n"
        dispatcher.utter_message(text=resposta)
        return[]

class ActionReqServ(Action):
    def name(self) -> Text:
        return "action_req_serv"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.latest_message['intent']
        entities = tracker.latest_message['entities']
        neg = False
        print(intent.get('name'))
        query = ""
        for entity in tracker.latest_message['entities']:
            entity_saved = False
            for i in range(0, len(entities)):
                if(entities[i]['value'] == entity['value'] or (entities[i]['start'] >= entity['start'] and entities[i]['end'] <= entity['end']) or (entity['start'] >= entities[i]['start'] and entity['end'] <= entities[i]['end'])):
                    entity_saved = True
                    if(entity['extractor'] == 'RegexEntityExtractor'):
                        entities[i] = entity
            if(not entity_saved):
                entities.append(entity)

        if(intent.get('name') == 'req_serv'):
            query = """PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n PREFIX serv: <http://servicos.gov.ce.br/>\n SELECT ?uri ?nome ?req\n         WHERE {\n           ?uri rdfs:label ?nome. """
            for entity in entities:
                print(entity['entity'])
                if(entity['entity'] == 'requisitos'):
                    query += """\n          ?uri serv:requisitos ?req."""
                elif(entity['entity'] == 'nomServico'):
                    query+= """\n            FILTER CONTAINS (?nome, "{}").""".format((entity['value']).lower())
        results = ActionResult(query)
        resposta = "Encontramos a seguinte resposta para sua consulta: \n"
        for result in results["results"]["bindings"]:
            resposta += result["nome"]["value"] + "\n"
            resposta += result["req"]["value"] + "\n"
        dispatcher.utter_message(text=resposta)
        return[]

class ActionTempServ(Action):
    def name(self) -> Text:
        return "action_temp_serv"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.latest_message['intent']
        entities = tracker.latest_message['entities']
        neg = False
        print(intent.get('name'))
        query = ""
        for entity in tracker.latest_message['entities']:
            entity_saved = False
            for i in range(0, len(entities)):
                if(entities[i]['value'] == entity['value'] or (entities[i]['start'] >= entity['start'] and entities[i]['end'] <= entity['end']) or (entity['start'] >= entities[i]['start'] and entity['end'] <= entities[i]['end'])):
                    entity_saved = True
                    if(entity['extractor'] == 'RegexEntityExtractor'):
                        entities[i] = entity
            if(not entity_saved):
                entities.append(entity)

        if(intent.get('name') == 'temp_serv'):
            query = """PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n PREFIX serv: <http://servicos.gov.ce.br/>\n SELECT ?nome ?desc\n         WHERE {\n           ?uri rdfs:label ?nome."""     
            for entity in entities:
                print(entity['entity'])                   
                if(entity['entity'] == 'tempoAtendimento'):
                    query += """\n          ?uri serv:tempoAtendimento ?desc."""
                elif(entity['entity'] == 'nomServico'):
                    query+= """\n           FILTER CONTAINS (?nome, "{}").""".format((entity['value']).lower())                 
        
        results = ActionResult(query)
        resposta = "Encontramos a seguinte resposta para sua consulta: \n"
        for result in results["results"]["bindings"]:
            resposta += result["nome"]["value"] + "\n"
            resposta += result["desc"]["value"] +"\n"
        dispatcher.utter_message(text=resposta)
        return[]

class ActionDescServ(Action):
    def name(self) -> Text:
        return "action_desc_serv"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.latest_message['intent']
        entities = tracker.latest_message['entities']
        neg = False
        print(intent.get('name'))
        query = ""
        for entity in tracker.latest_message['entities']:
            entity_saved = False
            for i in range(0, len(entities)):
                if(entities[i]['value'] == entity['value'] or (entities[i]['start'] >= entity['start'] and entities[i]['end'] <= entity['end']) or (entity['start'] >= entities[i]['start'] and entity['end'] <= entities[i]['end'])):
                    entity_saved = True
                    if(entity['extractor'] == 'RegexEntityExtractor'):
                        entities[i] = entity
            if(not entity_saved):
                entities.append(entity)
 
        if(intent.get('name') == 'desc_serv'): 
            query = """PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n PREFIX serv: <http://servicos.gov.ce.br/>\n SELECT ?nome ?desc\n         WHERE {\n           ?uri rdfs:label ?nome."""     
            for entity in entities:
                print(entity['entity'])               
                if(entity['entity'] == 'finalidade'):
                    query += """\n          ?uri serv:finalidade ?desc."""
                elif(entity['entity'] == 'nomServico'):
                    query+= """\n           FILTER CONTAINS (?nome, "{}").""".format((entity['value']).lower())                    
        results = ActionResult(query)
        resposta = "Encontramos a seguinte resposta para sua consulta: \n"
        for result in results["results"]["bindings"]:
            resposta += result["nome"]["value"] + "\n"
            resposta += result["desc"]["value"] + "\n"
        dispatcher.utter_message(text=resposta)
        return[]
                
class ActionDocNeces(Action):
    def name(self) -> Text:
        return "action_doc_neces"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.latest_message['intent']
        entities = tracker.latest_message['entities']
        neg = False
        print(intent.get('name'))
        query = ""
        
        for entity in tracker.latest_message['entities']:
            entity_saved = False
            for i in range(0, len(entities)):
                if(entities[i]['value'] == entity['value'] or (entities[i]['start'] >= entity['start'] and entities[i]['end'] <= entity['end']) or (entity['start'] >= entities[i]['start'] and entity['end'] <= entities[i]['end'])):
                    entity_saved = True
                    if(entity['extractor'] == 'RegexEntityExtractor'):
                        entities[i] = entity
            if(not entity_saved):
                entities.append(entity)

        if(intent.get('name') == 'doc_neces'): 
            query = """PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            \n PREFIX serv: <http://servicos.gov.ce.br/>\n SELECT ?nome ?trans ?req
            \n       WHERE {"""     
            for entity in entities:
                print(entity['entity'])
                if(entity['entity'] == 'docNeces'):
                    query += """\n          ?trans serv:docNeces ?req .
                    \n           FILTER CONTAINS (?req, "{}").""".format((entity['value']).lower())                                 
                elif(entity['entity'] == 'nomServico'):
                    query += """\n          ?trans rdfs:label ?nome."""
                    query+= """\n           FILTER CONTAINS (?nome, "{}").""".format((entity['value']).lower())
        results = ActionResult(query)
        resposta = "Encontramos a seguinte resposta para sua consulta: \n"
        for result in results["results"]["bindings"]:
            resposta += result["nome"]["value"] + "\n"
            resposta += result["req"]["value"] + "\n"
        dispatcher.utter_message(text=resposta)
        return[]

class ActionServGratis(Action):
    def name(self) -> Text:
        return "action_serv_gratis"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.latest_message['intent']
        entities = tracker.latest_message['entities']
        neg = False
        print(intent.get('name'))
        query = ""
        for entity in tracker.latest_message['entities']:
            entity_saved = False
            for i in range(0, len(entities)):
                if(entities[i]['value'] == entity['value'] or (entities[i]['start'] >= entity['start'] and entities[i]['end'] <= entity['end']) or (entity['start'] >= entities[i]['start'] and entity['end'] <= entities[i]['end'])):
                    entity_saved = True
                    if(entity['extractor'] == 'RegexEntityExtractor'):
                        entities[i] = entity
            if(not entity_saved):
                entities.append(entity)

        if(intent.get('name') == 'serv_gratis'): 
            query = """PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n PREFIX serv: <http://servicos.gov.ce.br/>\n SELECT ?nome ?val ?time\n        WHERE {\n           ?uri rdfs:label ?nome."""     
            for entity in entities:
                print(entity['entity'])
                if(entity['entity'] == 'nomServico'):
                    query+= """\n           FILTER CONTAINS (?nome, "{}").""".format((entity['value']).lower())               
                elif(entity['entity'] == 'servGratuito'):
                    query += """\n          ?uri serv:servGratuito ?val ."""
                elif(entity['entity'] == 'horarioAtendimento'):
                    query += """\n          ?uri serv:horarioAtendimento\n            ?time FILTER CONTAINS (?time, "{}").""".format((entity['value']).lower())                 
        results = ActionResult(query)
        resposta = "Encontramos a seguinte resposta para sua consulta: \n"
        for result in results["results"]["bindings"]:
            resposta += result["nome"]["value"] + "\n"
            resposta += result["val"]["value"] + "\n"
            resposta += result["time"]["value"] + "\n"
        dispatcher.utter_message(text=resposta)
        return[]

class ActionPresOn(Action):
    def name(self) -> Text:
        return "action_pres_on"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.latest_message['intent']
        entities = tracker.latest_message['entities']
        neg = False
        print(intent.get('name'))
        query = ""
        for entity in tracker.latest_message['entities']:
            entity_saved = False
            for i in range(0, len(entities)):
                if(entities[i]['value'] == entity['value'] or (entities[i]['start'] >= entity['start'] and entities[i]['end'] <= entity['end']) or (entity['start'] >= entities[i]['start'] and entity['end'] <= entities[i]['end'])):
                    entity_saved = True
                    if(entity['extractor'] == 'RegexEntityExtractor'):
                        entities[i] = entity
            if(not entity_saved):
                entities.append(entity)

        if(intent.get('name') == 'serv_pres_on'): 
            query = """PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n PREFIX serv: <http://servicos.gov.ce.br/>\n SELECT ?nome ?req ?acRemote\n        WHERE {\n           ?uri rdfs:label ?nome."""     
            for entity in entities:
                print(entity['entity'])
                if(entity['entity'] == 'nomServico'):
                    query+= """\n           FILTER CONTAINS (?nome, "{}").""".format((entity['value']).lower())               
                elif ((entity['entity'] == 'acessoPres') & (neg == False)):
                    query += """\n          OPTIONAL {\n                ?uri serv:acessoPres ?req\n              FILTER(?req = "S")\n         }"""
                elif ((entity['entity'] == 'acessoOnline') & (neg == False)):
                    query += """\n          OPTIONAL {\n               ?uri serv:acessoOnline ?acRemote.\n             FILTER(?acRemote = "S")\n          }"""                  
                elif (entity['entity'] == 'negacao'):
                    neg = True
                elif (entity['start'] == 'negacao'):
                    print("Frase negada completamente")
                    break
                else:
                    neg = False
        results = ActionResult(query)
        resposta = "Encontramos a seguinte resposta para sua consulta: \n"
        for result in results["results"]["bindings"]:
            resposta += result["nome"]["value"] + "\n"
            resposta += result["re"]["value"] + "\n"
            resposta += result["acRemote"]["value"] + "\n"
        dispatcher.utter_message(text=resposta)
        return[]

class ActionOnlineDesc(Action):
    def name(self) -> Text:
        return "action_online_desc"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.latest_message['intent']
        entities = tracker.latest_message['entities']
        neg = False
        print(intent.get('name'))
        query = ""
        for entity in tracker.latest_message['entities']:
            entity_saved = False
            for i in range(0, len(entities)):
                if(entities[i]['value'] == entity['value'] or (entities[i]['start'] >= entity['start'] and entities[i]['end'] <= entity['end']) or (entity['start'] >= entities[i]['start'] and entity['end'] <= entities[i]['end'])):
                    entity_saved = True
                    if(entity['extractor'] == 'RegexEntityExtractor'):
                        entities[i] = entity
            if(not entity_saved):
                entities.append(entity)

        if(intent.get('name') == 'serv_online_desc'): 
            query = """PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n PREFIX serv: <http://servicos.gov.ce.br/>\n SELECT ?nome ?remote. ?end ?req\n      WHERE {\n          ?uri rdfs:label ?nome."""     
            for entity in entities:
                print(entity['entity'])
                if(entity['entity'] == 'nomServico'):
                    query+= """\n           FILTER CONTAINS (?nome, "{}").""".format((entity['value']).lower())               
                elif (entity['entity'] == 'acessoOnline'):
                    query += """\n          ?uri serv:acessoOnline ?remote.""" 
                elif (entity['entity'] == 'enderecoOnline'):
                    query += """\n          ?uri serv:dsc_acesso_online ?end."""
                elif (entity['entity'] == 'requisitos'):
                    query += """\n          ?uri serv:requisitos ?req.\n         FILTER(?remote, "S") ."""                      
        results = ActionResult(query)
        resposta = "Encontramos a seguinte resposta para sua consulta: \n"
        for result in results["results"]["bindings"]:
            resposta += result["nome"]["value"] + "\n"
            resposta += result["remote"]["value"] + "\n"
            resposta += result["end"]["value"] + "\n"
            resposta += result["req"]["value"] + "\n"
        dispatcher.utter_message(text=resposta)
        return[]

class ActionPresDesc(Action):
    def name(self) -> Text:
        return "action_pres_desc"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.latest_message['intent']
        entities = tracker.latest_message['entities']
        neg = False
        print(intent.get('name'))
        query = ""
        for entity in tracker.latest_message['entities']:
            entity_saved = False
            for i in range(0, len(entities)):
                if(entities[i]['value'] == entity['value'] or (entities[i]['start'] >= entity['start'] and entities[i]['end'] <= entity['end']) or (entity['start'] >= entities[i]['start'] and entity['end'] <= entities[i]['end'])):
                    entity_saved = True
                    if(entity['extractor'] == 'RegexEntityExtractor'):
                        entities[i] = entity
            if(not entity_saved):
                entities.append(entity)

        if(intent.get('name') == 'serv_pres_desc'): 
            query = """PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n PREFIX serv: <http://servicos.gov.ce.br/>\n SELECT ?nome ?pres ?end ?req\n     WHERE {\n           ?uri rdfs:label ?nome."""     
            for entity in entities:
                print(entity['entity'])
                if(entity['entity'] == 'nomServico'):
                    query+= """\n           FILTER CONTAINS (?nome, "{}").""".format((entity['value']).lower())               
                elif (entity['entity'] == 'acessoPres'):
                    query += """\n         uri serv:acessoPres ?pres.""" 
                elif (entity['entity'] == 'enderecoPresencial'):
                    query += """\n         ?uri serv:enderecoPresencial ?end."""
                elif (entity['entity'] == 'requisitos'):
                    query += """\n        ?uri serv:requisitos ?req .\n          FILTER(?pres, "N") ."""                                   
        results = ActionResult(query)
        resposta = "Encontramos a seguinte resposta para sua consulta: \n"
        for result in results["results"]["bindings"]:
            resposta += result["nome"]["value"] + "\n"
            resposta += result["pres"]["value"] + "\n"
            resposta += result["end"]["value"] + "\n"
            resposta += result["req"]["value"] + "\n"
        dispatcher.utter_message(text=resposta)
        return[]
        