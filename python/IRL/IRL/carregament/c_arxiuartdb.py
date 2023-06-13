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

def artistes(site):
    repo = site.data_repository()
    with open('./dades/arxiuartdb_artistes.txt', 'r') as fp:
        artistes = json.load(fp)
    '''
    "reference": "...",
    "nom": "Ignasi Aballó", 
    "lloc_naixement": "Barcelona", 
    "any_naixement": 1958, 
    "residencia": "Barcelona", 
    "web": null,
    "categoria": ["Pintura", "Dibuix", "Art processual", "Instal·lació"]
    '''
    artista = artistes['1']
    labels = {'en': artista['nom'], 'ca': artista['nom']}
    artista_id = create_item(site, labels)
    artista_item = pywikibot.ItemPage(repo, artista_id)
    
    #instance of (P82) human (Q497)
    artista_claim = add_claim(site,repo,artista_item, 'P82', 'Q497', True)
    add_reference(site, repo, artista['reference'], artista_claim)
    
    #afegir totes les localitats de lloc_naixement
    if artista['lloc_naixement'] is not None:
        for location in artista['lloc_naixement'].split(', '):
            search_results = pywikibot.data.api.Request(site=site, action='wbsearchentities', search=location, language='ca', uselang='ca').submit()
            if search_results['search'] and search_results['search'][0]['label'] == location:
                print('dins de search')
                city_id = search_results['search'][0]['id']
                print(city_id)
            else:
                labels = {"en": location, "ca": location}
                city_id = create_item(site, labels)
            
            #place of birth (P342)
            artista_claim = add_claim(site,repo,artista_item, 'P342', city_id, True)
            add_reference(site, repo, artista['reference'], artista_claim)
    if artista['any_naixement'] is not None:
        date = pywikibot.WbTime(year=int(artista['any_naixement']))
        #date of birth (P18)
        artista_claim = add_claim(site,repo,artista_item, 'P18', date)
        add_reference(site, repo, artista['reference'], artista_claim)
        
    #afegir web oficial de l'artista si existeix
    if artista['web'] is not None:
        #official website (P206)
        artista_claim = add_claim(site,repo,artista_item, 'P206', 'https://' + artista['web'].replace('https://','').replace('http://','').strip())
        add_reference(site, repo, artista['reference'], artista_claim)
    if 'categoria' in artista.keys():
        for cat in artista['categoria']:
            search_results = pywikibot.data.api.Request(site=site, action='wbsearchentities', search=cat, language='ca', uselang='ca').submit()
            if search_results['search'] and search_results['search'][0]['label'] == cat:
                print('dins de search')
                cat_id = search_results['search'][0]['id']
                print(cat_id)
            else:
                labels = {"en": cat, "ca": cat}
                cat_id = create_item(site, labels)
            
            #type (P797)
            artista_claim = add_claim(site,repo,artista_item, 'P797', cat_id, True)
            add_reference(site, repo, artista['reference'], artista_claim)
    
def obres(site):
    repo = site.data_repository()
    with open('./dades/arxiuartdb_obres.txt', 'r') as fp:
        obres = json.load(fp)
    '''
    "reference": "http://aa.xtraz.net/ca/cerca", 
    "artista": "Carme Sanglas", 
    "titol": "Penombra, reflex i transparència", 
    "any": "2009", 
    "link": null, 
    "mides": "99 x 69 cm"
    '''
    obra = obres['311']
    if obra['titol'] is None:
        return
    labels = {'en': obra['titol'], 'ca': obra['titol']}
    obra_id = create_item(site, labels)
    obra_item = pywikibot.ItemPage(repo, obra_id)
    
    #instance of (P82) work of art (Q230406)
    obra_claim = add_claim(site,repo,obra_item, 'P82', 'Q230406', True)
    add_reference(site, repo, obra['reference'], obra_claim)
    search_results = pywikibot.data.api.Request(site=site, action='wbsearchentities', search=obra['artista'], language='ca', uselang='ca').submit()
    if search_results['search'] and search_results['search'][0]['label'] == obra['artista']:
        print('dins de search')
        artista_id = search_results['search'][0]['id']
        print(artista_id)
    else:
        labels = {"en":obra['artista'], "ca": obra['artista']}
        artista_id = create_item(site, labels)
    
    #author (P95656)
    obra_claim = add_claim(site,repo,obra_item, 'P95656', artista_id, True)
    add_reference(site, repo, obra['reference'], obra_claim)
    
    if obra['any'] is not None:
        date = pywikibot.WbTime(year=int(obra['any'].strip()))
        
        #date of birth (P761)
        obra_claim = add_claim(site,repo,obra_item, 'P761', date)
        add_reference(site, repo, obra['reference'], obra_claim)
        
    #afegeix official website (P206) si existeix
    if obra['link'] is not None:
        obra_claim = add_claim(site,repo,obra_item, 'P206', 'https://' + obra['link'].replace('http://','').replace('https://','').strip())
        add_reference(site, repo, obra['reference'], obra_claim)
    if obra['mides'] is not None:
        mesures = list(map(int, re.findall(r'\d+', obra['mides'])))
        unit_item = pywikibot.ItemPage(repo, 'Q179632')
        if len(mesures) > 2:
            #3 dimensions
            #ordre: height P81773, length P372, width P81774
            height = pywikibot.WbQuantity(amount = mesures[0], unit = unit_item, site = site)
            length = pywikibot.WbQuantity(amount = mesures[1], unit = unit_item, site = site)
            width = pywikibot.WbQuantity(amount = mesures[2], unit = unit_item, site = site)
            
            #height (P81773)
            obra_claim = add_claim(site,repo,obra_item, 'P81773', height)
            add_reference(site, repo, obra['reference'], obra_claim)
            
            #length (P372)
            obra_claim = add_claim(site,repo,obra_item, 'P372', length)
            add_reference(site, repo, obra['reference'], obra_claim)
            
            #width (P81774)
            obra_claim = add_claim(site,repo,obra_item, 'P81774', width)
            add_reference(site, repo, obra['reference'], obra_claim)
        elif len(mesures) > 1:
            #2 dimensions
            #la resta es descarten
            #ordre: height, length
            height = pywikibot.WbQuantity(amount = mesures[0], unit = unit_item, site = site)
            length = pywikibot.WbQuantity(amount = mesures[1], unit = unit_item, site = site)
            
            #height (P81773)
            obra_claim = add_claim(site,repo,obra_item, 'P81773', height)
            add_reference(site, repo, obra['reference'], obra_claim)
            
            #length (P372)
            obra_claim = add_claim(site,repo,obra_item, 'P372', length)
            add_reference(site, repo, obra['reference'], obra_claim)
        

