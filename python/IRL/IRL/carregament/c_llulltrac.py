import json
import pywikibot
import numpy as np
import os
from datetime import date
import re
from fuzzywuzzy import fuzz

def create_item(site, label_dict, descr=None):
    search_results = pywikibot.data.api.Request(site=site, action='wbsearchentities', search=label_dict['ca'], strictlanguage=True, language='ca', uselang='ca', limit = '10').submit()
    if search_results['search'] and fuzz.ratio(search_results['search'][0]['label'], label_dict['ca']) >= 0.75:
        for result in search_results["search"]:
            print(result['id'])
            print(result)
            if 'description' in result['display'].keys() and 'ca' in result['display']['description']['language']:
                print('dins 1r if')
                if fuzz.ratio(result['display']['description']['value'],descr) >= 0.5 and (result['display']['description']['language'] == 'ca' or result['display']['description']['language'] == 'en'):
                    print(fuzz.ratio(result['display']['description']['value'],descr))
                    print('descripció ja existeix')
                    new_id = result['id']
                    return new_id
        print(fuzz.ratio(search_results['search'][0]['label'], label_dict['ca']))
        new_id = search_results['search'][0]['id']
        new_item = pywikibot.ItemPage(site, new_id)
    else:
        new_item = pywikibot.ItemPage(site)
        new_item.editLabels(labels=label_dict, summary="Setting labels")
        new_id = new_item.getID()
    if descr is not None:
        if 'ca' in new_item.descriptions.keys():
            new_item.descriptions['ca'] = new_item.descriptions['ca'] + ' ' + descr
        else:
            new_item.descriptions['ca'] = descr
        if 'en' in new_item.descriptions.keys():
            new_item.descriptions['en'] = new_item.descriptions['en'] + ' ' + descr
        else:
            new_item.descriptions['en'] = descr
    new_item.editEntity(data = new_item.toJSON(),summary='descr')
    
    # Add description here or in another function
    return new_id

def add_claim(site, repo, item, property_id, value, is_item=False):
    claim = pywikibot.Claim(repo, property_id)
    if is_item:
        claim_item = pywikibot.ItemPage(repo, value)
        claim.setTarget(claim_item)
    else:
        claim.setTarget(value)
    if property_id in item.claims.keys() and claim in item.claims[property_id]:
        print('The claim already exists')
    else:
        print('New claim')
        item.addClaim(claim, summary=value)
    return claim

def add_reference(site, repo, url, claim):
    today = date.today()
    ref = pywikibot.Claim(repo, u'P93') #reference url
    ref.setTarget(url)

    retrieved = pywikibot.Claim(repo, u'P146') #date retrieved
    dateCre = pywikibot.WbTime(year=int(today.strftime("%Y")), month=int(today.strftime("%m")), day=int(today.strftime("%d"))) #retrieved -> %DATE TODAY%. Example retrieved -> 29.11.2020
    retrieved.setTarget(dateCre)
    claim.addSources([ref, retrieved], summary=u'Adding reference')


def contactes(site):
    repo = site.data_repository()
    with open('./dades/llulltrac_contactes.txt', 'r') as fp:
        contactes = json.load(fp)
    '''
    "nom": "* Contacte de proves", 
    "mail": "online@zelig.net", 
    "empresa": "Servei Tècnic", 
    "link": "https://www.xtraz.net"
    '''
    contacte = contactes['33120']
    print(contacte)
    labels = {"en": contacte['nom'], "ca": contacte['nom']}
    contacte_id = create_item(site, labels)
    contacte_item = pywikibot.ItemPage(repo, contacte_id)
    
    #instance of (P82) human (Q497)
    cont_claim = add_claim(site,repo,contacte_item, 'P82', 'Q497', True)
    add_reference(site, repo, contacte['reference'], cont_claim)
    
    #afegeix l'empresa
    if contacte['empresa'] != '':
        search_results = pywikibot.data.api.Request(site=site, action='wbsearchentities', search=contacte['empresa'], language='ca', uselang='ca').submit()
        if search_results['search']:
            print('dins de search')
            empresa_id = search_results['search'][0]['id']
            print(empresa_id)
        else:
            labels = {"en": contacte['empresa'], "ca": contacte['empresa']}
            empresa_id = create_item(site, labels)
        #member of (P120)
        cont_claim = add_claim(site,repo,contacte_item, 'P120', empresa_id, True)
        add_reference(site, repo, contacte['reference'], cont_claim)
        
    #official website (P206)
    if contacte['link'] != '':
        cont_claim = add_claim(site,repo,contacte_item, 'P206', 'https://' + contacte['link'].replace('http://','').replace('https://','').strip())
        add_reference(site, repo, contacte['reference'], cont_claim)
        
def documents(site):
    repo = site.data_repository()
    with open('./dades/llulltrac_documents.txt','r') as fp:
        documents = json.load(fp)
    '''
    "reference": "https://www.llull.cat/catala/literatura/trac_traduccions.cfm", 
    "titol": "Ernestina", 
    "titol_original": "Les ales d'Ernestina",
    "lloc_edicio": "Barcelona",
    "any_edicio": 1910, 
    "editorial": "E. Domènech", 
    "genere": "Narrativa, altres", 
    "llengua": "Castellà, altres", 
    "categoria": "Narrativa, altres"
    '''

    #categoria té tot, gèneres i categories
    document = documents['5444']
    print(document)
    if document['titol'] is None or document['titol'] == '':
        return
    labels = {'en': document['titol'], 'ca': document['titol']}
    doc_id = create_item(site, labels)
    doc_item = pywikibot.ItemPage(repo, doc_id)
    
    #instance of (P82) document (Q215177)
    doc_claim = add_claim(site,repo,doc_item, 'P82', 'Q215177', True)
    add_reference(site, repo, document['reference'], doc_claim)
    
    #title
    doc_claim = add_claim(site,repo,doc_item, 'P95', document['titol'])
    add_reference(site, repo, document['reference'], doc_claim)
    
    #title
    if document['titol_original'] is not None and document['titol_original'] != '':
        doc_claim = add_claim(site,repo,doc_item, 'P95', document['titol_original'])
        add_reference(site, repo, document['reference'], doc_claim)
        
    #afegeix ciutat
    if document['lloc_edicio'] is not None and document['lloc_edicio'] != '':
        search_results = pywikibot.data.api.Request(site=site, action='wbsearchentities', search=document['lloc_edicio'], language='ca', uselang='ca').submit()
        if search_results['search']:
            print('dins de search')
            city_id = search_results['search'][0]['id']
            print(city_id)
        else:
            labels = {"en": document['lloc_edicio'], "ca": document['lloc_edicio']}
            city_id = create_item(site, labels)
        #place of publication (P95837)
        doc_claim = add_claim(site,repo,doc_item, 'P95837', city_id, True)
        add_reference(site, repo, document['reference'], doc_claim)
        date = pywikibot.WbTime(year=int(document['any_edicio']))
        
    #publication date
    if document['any_edicio'] is not None:
        doc_claim = add_claim(site,repo,doc_item, 'P761', date)
        add_reference(site, repo, document['reference'], doc_claim)
        
    #afegeix editorial
    if document['editorial'] !='':
        search_results = pywikibot.data.api.Request(site=site, action='wbsearchentities', search=document['editorial'], language='ca', uselang='ca').submit()
        if search_results['search']:
            print('dins de search')
            editorial_id = search_results['search'][0]['id']
            print(editorial_id)
        else:
            labels = {"en": document['editorial'], "ca": document['editorial']}
            editorial_id = create_item(site, labels)
        
        #publisher (P145)
        doc_claim = add_claim(site,repo,doc_item, 'P145', editorial_id, True)
        add_reference(site, repo, document['reference'], doc_claim)
        
    #afegeix idiomes
    if document['llengua'] !='':
        for idioma in document['llengua'].split(', '):
            search_results = pywikibot.data.api.Request(site=site, action='wbsearchentities', search=idioma, language='ca', uselang='ca').submit()
            if search_results['search']:
                print('dins de search')
                idioma_id = search_results['search'][0]['id']
                print(idioma_id)
            else:
                labels = {"en": idioma, "ca": idioma}
                idioma_id = create_item(site, labels)
            #language (P226)
            doc_claim = add_claim(site,repo,doc_item, 'P226', idioma_id, True)
            add_reference(site, repo, document['reference'], doc_claim)
        
    #afegeix categories
    if document['categoria'] !='':
        for categoria in document['categoria'].split(', '):
            search_results = pywikibot.data.api.Request(site=site, action='wbsearchentities', search=categoria, language='ca', uselang='ca').submit()
            if search_results['search']:
                print('dins de search')
                categoria_id = search_results['search'][0]['id']
                print(categoria_id)
            else:
                labels = {"en": categoria, "ca": categoria}
                categoria_id = create_item(site, labels)
            #type (P797)
            doc_claim = add_claim(site,repo,doc_item, 'P797', categoria_id, True)
            add_reference(site, repo, document['reference'], doc_claim)
        
def editorials(site):
    '''
    {'nom': 'Eichborn', 
    'reference': 'https://www.llull.cat/catala/literatura/trac_traduccions.cfm'}
    '''
    repo = site.data_repository()
    with open('./dades/llulltrac_editorials.txt','r') as fp:
        editorials = json.load(fp)
    editorial = editorials['754']
    labels = {'en': editorial['nom'], 'ca': editorial['nom']}
    editorial_id = create_item(site, labels)
    editorial_item = pywikibot.ItemPage(repo, editorial_id)
    #instance of (P82) publisher (Q214707)
    editorial_claim = add_claim(site,repo,editorial_item, 'P82', 'Q214707', True)
    add_reference(site, repo, editorial['reference'], editorial_claim)

def llibres(site):
    repo = site.data_repository()
    with open('./dades/llulltrac_llibres.txt','r') as fp:
        llibres = json.load(fp)
    '''
    "reference": "https://www.llull.cat/catala/literatura/trac_traduccions.cfm", 
    "titol_cat": "Wolfgang i el seu pare ", 
    "titol_eng": "Wolfgang and His Father's Secret",
    "any": "2019", 
    "pagines": "224", 
    "editorial": "Columna", 
    "contactes": "Pilar Lafuente", 
    "quadernet": "Catalan Children's and Young Adult Books  2020", 
    "genere": "Literatura Infantil i juvenil"
    '''

    llibre = llibres['33147']
    labels = {'en': llibre['titol_eng'].strip(), 'ca': llibre['titol_cat'].strip()}
    llibre_id = create_item(site, labels)
    llibre_item = pywikibot.ItemPage(repo, llibre_id)
    #instance of (P82) book (Q131598)
    llibre_claim = add_claim(site,repo,llibre_item, 'P82', 'Q131598', True)
    add_reference(site, repo, llibre['reference'], llibre_claim)
    date = pywikibot.WbTime(year = int(llibre['any'].strip()))
    
    #publication date (P761)
    llibre_claim = add_claim(site,repo,llibre_item, 'P761', date)
    add_reference(site, repo, llibre['reference'], llibre_claim)
    unit_item = pywikibot.ItemPage(repo, 'Q230387')
    if llibre['pagines'] !='' and llibre['pagines'].strip().isdigit():
        pages = pywikibot.WbQuantity(amount = int(llibre['pagines'].strip()), unit = unit_item, site = site)
        #number of pages (P97584)
        llibre_claim = add_claim(site,repo,llibre_item, 'P97584', pages)
        add_reference(site, repo, llibre['reference'], llibre_claim)
        
    #afegeix editorial
    search_results = pywikibot.data.api.Request(site=site, action='wbsearchentities', search=llibre['editorial'], language='ca', uselang='ca').submit()
    if search_results['search']:
        print('dins de search')
        editorial_id = search_results['search'][0]['id']
        print(editorial_id)
    else:
        labels = {"en": llibre['editorial'], "ca": llibre['editorial']}
        editorial_id = create_item(site, labels)
    #publisher (P145)
    llibre_claim = add_claim(site,repo,llibre_item, 'P145', editorial_id, True)
    add_reference(site, repo, llibre['reference'], llibre_claim)
    
    #afegeix contactes
    if llibre['contactes'] !='':
        for contacte in llibre['contactes'].split(', '):
            search_results = pywikibot.data.api.Request(site=site, action='wbsearchentities', search=contacte, language='ca', uselang='ca').submit()
            if search_results['search']:
                print('dins de search')
                contacte_id = search_results['search'][0]['id']
                print(contacte_id)
            else:
                labels = {"en": contacte, "ca": contacte}
                contacte_id = create_item(site, labels)
            
            #represented by (P97585)
            llibre_claim = add_claim(site,repo,llibre_item, 'P97585', contacte_id, True)
            add_reference(site, repo, llibre['reference'], llibre_claim)
        
    #afegeix quadernet
    search_results = pywikibot.data.api.Request(site=site, action='wbsearchentities', search=llibre['quadernet'], language='ca', uselang='ca').submit()
    if search_results['search']:
        print('dins de search')
        quad_id = search_results['search'][0]['id']
        print(quad_id)
    else:
        labels = {"en": llibre['quadernet'], "ca": llibre['quadernet']}
        quad_id = create_item(site, labels)
    #has part (209)
    llibre_claim = add_claim(site,repo,llibre_item, 'P209', quad_id, True)
    add_reference(site, repo, llibre['reference'], llibre_claim)
    
    #afegeix gènere
    search_results = pywikibot.data.api.Request(site=site, action='wbsearchentities', search=llibre['genere'], language='ca', uselang='ca').submit()
    if search_results['search']:
        print('dins de search')
        genere_id = search_results['search'][0]['id']
        print(genere_id)
    else:
        labels = {"en": llibre['genere'], "ca": llibre['genere']}
        genere_id = create_item(site, labels)
    #type (P797)
    llibre_claim = add_claim(site,repo,llibre_item, 'P797', genere_id, True)
    add_reference(site, repo, llibre['reference'], llibre_claim)
    
def quad_premis(site):
    repo = site.data_repository()
    with open('./dades/llulltrac_quad_premis.txt','r') as fp:
        quad_premis = json.load(fp)
    '''
    "reference": "https://www.llull.cat/catala/literatura/trac_traduccions.cfm", 
    "nom": "Catalan Literary Non-fiction 2020", 
    "any": "2020", 
    "link_quad": "https://llull.cat/IMAGES_2/cataleg-nf-2020-m9-ok.pdf"
    '''
    quad = quad_premis['33038']
    labels = {'en': quad['nom'], 'ca': quad['nom']}
    quad_id = create_item(site, labels)
    quad_item = pywikibot.ItemPage(repo, quad_id)
    #instance of (P82) award (Q210299)
    quad_claim = add_claim(site,repo,quad_item, 'P82', 'Q210299', True)
    add_reference(site, repo, quad['reference'], quad_claim)
    date = pywikibot.WbTime(year = int(quad['any'].strip()))
    
    #publication date (P761)
    quad_claim = add_claim(site,repo,quad_item, 'P761', date)
    add_reference(site, repo, quad['reference'], quad_claim)
    
    #official website (P206)
    quad_claim = add_claim(site,repo,quad_item, 'P206', 'https://' + quad['link_quad'].replace('http://','').replace('https://','').strip())
    add_reference(site, repo, quad['reference'], quad_claim)
    
def traductors(site):
    repo = site.data_repository()
    with open('./dades/llulltrac_traductors.txt','r') as fp:
        traductors = json.load(fp)
    '''
    "reference": "https://www.llull.cat/catala/literatura/tralicat_traductors.cfm", 
    "nom_complert": "Maria Antònia Oliver ", 
    "especialitat": "", 
    "llengua": ""
    '''
    traductor = traductors['4943']
    if traductor['nom_complert'] is None or traductor['nom_complert'] =='':
        return
    labels = {'en': traductor['nom_complert'].strip(), 'ca': traductor['nom_complert'].strip()}
    traductor_id = create_item(site, labels)
    traductor_item = pywikibot.ItemPage(repo, traductor_id)
    
    #instance of (P82) human (Q497)
    trad_claim = add_claim(site,repo,traductor_item, 'P82', 'Q497', True)
    add_reference(site, repo, traductor['reference'], trad_claim)
    
    #afegeix especialitats
    if traductor['especialitat'] !='':
        for esp in traductor['especialitat'].split(', '):
            search_results = pywikibot.data.api.Request(site=site, action='wbsearchentities', search=esp, language='ca', uselang='ca').submit()
            if search_results['search']:
                print('dins de search')
                esp_id = search_results['search'][0]['id']
                print(esp_id)
            else:
                labels = {"en": esp, "ca": esp}
                esp_id = create_item(site, labels)
            #field of work (P128)
            trad_claim = add_claim(site,repo,traductor_item, 'P128', esp_id, True)
            add_reference(site, repo, traductor['reference'], trad_claim)
    #occupation (P204) translator (Q136303)
    trad_claim = add_claim(site,repo,traductor_item, 'P204', 'Q136303', True)
    add_reference(site, repo, traductor['reference'], trad_claim)
    
    #afegeix idiomes
    if traductor['llengua'] !='':
        for idioma in traductor['llengua'].split(', '):
            search_results = pywikibot.data.api.Request(site=site, action='wbsearchentities', search=idioma, language='ca', uselang='ca').submit()
            if search_results['search']:
                print('dins de search')
                idioma_id = search_results['search'][0]['id']
                print(idioma_id)
            else:
                labels = {"en": idioma, "ca": idioma}
                idioma_id = create_item(site, labels)
            #language (P226)
            trad_claim = add_claim(site,repo,traductor_item, 'P226', idioma_id, True)
            add_reference(site, repo, traductor['reference'], trad_claim)
        


