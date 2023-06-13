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

def add_identifiers(site, repo, property_id, value, reference, item):
    claim = pywikibot.Claim(repo, property_id, datatype='external-id')
    claim.setTarget(value)
    if property_id not in item.claims.keys():
        item.addClaim(claim, summary='Adding external identifier {}'.format(value))
        add_reference(site, repo, reference, claim)
    elif property_id in item.claims.keys() and claim not in item.claims[property_id]:
        item.addClaim(claim, summary='Adding external identifier {}'.format(value))
        add_reference(site, repo, reference, claim)
    else:
        print('id already exists')

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

def persones(site):
    repo = site.data_repository()
    with open('./dades_transf/cantic_persones.txt', 'r') as fp:
        persones = json.load(fp)
    persona = persones['293919']
    print(persona)
    '''
    {'nom': 'Sara Barquinero del Toro', 
    'dates': '', 
    'titol': 'Terminal', 
    'url_viaf': 'https://viaf.org/viaf/6304162906478978110000', 
    'cantic': '981058479227706706', 
    'idioma': 'Català', 
    'any_publicacio': None, 
    'data_naixement': '', 
    'data_defuncio': ''}
    '''
    labels = {'en':persona['nom'], 'ca': persona['nom']}
    persona_id = create_item(site, labels)
    persona_item = pywikibot.ItemPage(repo, persona_id)
    persona_item.get()
    #instance of (P82) human (Q497)
    persona_claim = add_claim(site,repo,persona_item, 'P82', 'Q497', True)
    add_reference(site, repo, persona['url_viaf'], persona_claim)
    
    #date of birth (p18)
    if persona['data_naixement'] != '':
        data = pywikibot.WbTime(year=int(persona['data_naixement'].strip().strip('.')))
        persona_claim = add_claim(site,repo,persona_item, 'P18', data)
        add_reference(site, repo, persona['url_viaf'], persona_claim)
    
    #date of death (P25)
    if persona['data_defuncio'] != '':
        data = pywikibot.WbTime(year=int(persona['data_defuncio'].strip().strip('.')))
        persona_claim = add_claim(site,repo,persona_item, 'P25', data)
        add_reference(site, repo, persona['url_viaf'], persona_claim)
    
    #publication date (P761)
    if persona['any_publicacio'] is not None:
        data = pywikibot.WbTime(year=int(persona['any_publicacio']))
        persona_claim = add_claim(site,repo,persona_item, 'P761', data)
        add_reference(site, repo, persona['url_viaf'], persona_claim)
    
    #CANTIC ID (P89586)
    add_identifiers(site, repo, 'P89586', persona['cantic'], persona['url_viaf'], persona_item)
    
    #VIAF ID (P765)
    viaf = persona['url_viaf'].replace('https://viaf.org/viaf/','')
    add_identifiers(site, repo, 'P765', viaf, persona['url_viaf'], persona_item)
    
    #creem obra si existeix el títol i no està creat l'ítem
    if persona['titol'] != '':
        search_results = pywikibot.data.api.Request(site=site, action='wbsearchentities', search=persona['titol'], strictlanguage=True, language='ca', uselang='ca').submit()
        if search_results['search'] and fuzz.ratio(search_results['search'][0]['label'], persona['titol']) >= 0.75:
            print('dins de search')
            obra_id = search_results['search'][0]['id']
            print(obra_id)
        else:
            labels = {"en": persona['titol'], "ca": persona['titol']}
            obra_id = create_item(site, labels)
        
        #notable work (P95835)
        persona_claim = add_claim(site,repo,persona_item, 'P95835', obra_id, True)
        add_reference(site, repo, persona['url_viaf'], persona_claim)
        obra_item = pywikibot.ItemPage(repo, obra_id)
    
    #afegeix idioma si hi és i no existeix l'ítem
    if persona['idioma'] != '' and not persona['idioma'].strip().isdigit():
        search_results = pywikibot.data.api.Request(site=site, action='wbsearchentities', search=persona['idioma'], strictlanguage=True, language='ca', uselang='ca').submit()
        if search_results['search'] and fuzz.ratio(search_results['search'][0]['label'], persona['idioma']) >= 0.75:
            print('dins de search')
            idioma_id = search_results['search'][0]['id']
            print(idioma_id)
        else:
            labels = {"en": persona['idioma'], "ca": persona['idioma']}
            idioma_id = create_item(site, labels)
        
        #language (P226)
        obra_claim = add_claim(site,repo,obra_item, 'P226', idioma_id, True)
        add_reference(site, repo, persona['url_viaf'], obra_claim)
    
def entitats(site):
    '''
    {'nom': 'Care Collective', 
    'titol': 'Care manifesto.', 
    'url_viaf': 'https://viaf.org/viaf/4889162906467078110005', 
    'cantic': '981058503920806706'
    '''
    repo = site.data_repository()
    with open('./dades_transf/cantic_entitats.txt', 'r') as fp:
        entitats = json.load(fp)
    entitat = entitats['31423']
    print(entitat)
    labels = {'en':entitat['nom'], 'ca': entitat['nom']}
    entitat_id = create_item(site, labels, entitat['titol'].strip().strip('.'))
    entitat_item = pywikibot.ItemPage(repo, entitat_id)
    entitat_item.get()

    #instance of (P82) entity (Q223336)
    entitat_claim = add_claim(site,repo,entitat_item, 'P82', 'Q223336', True)
    add_reference(site, repo, entitat['url_viaf'], entitat_claim)
    
    #CANTIC ID (P89586)
    add_identifiers(site, repo, 'P89586', entitat['cantic'], entitat['url_viaf'], entitat_item)
    
    #VIAF ID (P765)
    viaf = entitat['url_viaf'].replace('https://viaf.org/viaf/','')
    add_identifiers(site, repo, 'P765', viaf, entitat['url_viaf'], entitat_item)
    
def congressos(site):
    '''
    {'titol': 'Deuxièmes Journées psychiatriques, Paris 5-6- mars 1966', 
    'url_viaf': 'https://viaf.org/viaf/5225157527294927300004', 
    'cantic': '981058601709606706', 
    'nom': 'Journées psychiatriques'}
    '''
    repo = site.data_repository()
    with open('./dades_transf/cantic_congressos.txt', 'r') as fp:
        congressos = json.load(fp)
    congres = congressos['746']
    print(congres)
    labels = {"en": congres['nom'], "ca": congres['nom']}
    congres_id = create_item(site, labels, congres['titol'])
    congres_item = pywikibot.ItemPage(repo, congres_id)
    congres_item.get()
    print(congres_item)

    #instance of (P82) event (Q215099)
    congres_claim = add_claim(site,repo,congres_item, 'P82', 'Q215099', True)
    add_reference(site, repo, congres['url_viaf'], congres_claim)
    
    #CANTIC ID (P89586)
    add_identifiers(site, repo, 'P89586', congres['cantic'], congres['url_viaf'], congres_item)
    
    #VIAF ID (P765)
    viaf = congres['url_viaf'].replace('https://viaf.org/viaf/','')
    add_identifiers(site, repo, 'P765', viaf, congres['url_viaf'], congres_item)

def obres(site):
    '''
    {'url_viaf': 'https://viaf.org/viaf/6162902626077781583', 
    'cantic': '981058479246606706', 
    'nom': 'HideOut', 
    'any': '', 
    'tipus': ''
    '''
    repo = site.data_repository()
    with open('./dades_transf/cantic_obres.txt', 'r') as fp:
        obres = json.load(fp)
    obra = obres['13080']
    print(obra)
    labels = {'en':obra['nom'], 'ca': obra['nom']}
    obra_id = create_item(site, labels)
    obra_item = pywikibot.ItemPage(repo, obra_id)
    obra_item.get()

    #instance of (P82) work of art (Q230406)
    obra_claim = add_claim(site,repo,obra_item, 'P82', 'Q230406', True)
    add_reference(site, repo, obra['url_viaf'], obra_claim)
    
    if obra['any'] != '':
        #publication date (P151)
        date = pywikibot.WbQuantity(year=int(obra['any']))
        obra_claim = add_claim(site,repo,obra_item, 'P151', date)
        add_reference(site, repo, obra['url_viaf'], obra_claim)

    if obra['tipus'] != '':
        #type (P797) film (Q229658)
        obra_claim = add_claim(site,repo,obra_item, 'P797', 'Q229658', True)
        add_reference(site, repo, obra['url_viaf'], obra_claim)

    #CANTIC ID (P89586)
    add_identifiers(site, repo, 'P89586', obra['cantic'], obra['url_viaf'], obra_item)
    
    #VIAF ID (P765)
    viaf = obra['url_viaf'].replace('https://viaf.org/viaf/','')
    add_identifiers(site, repo, 'P765', viaf, obra['url_viaf'], obra_item)
    
    
def geografia(site):
    '''
    {'url_viaf': 'https://viaf.org/viaf/7961167807272618130009', 
    'cantic': '981060918659806706', 
    'comunitat': 'Catalunya', 
    'municipi': 'Foixà', 
    'comarca': ''}
    '''
    repo = site.data_repository()
    with open('./dades_transf/cantic_geografics.txt', 'r') as fp:
        geografics = json.load(fp)
    geo = geografics['12']
    print(geo)
    labels = {'en':geo['municipi'], 'ca': geo['municipi']}
    geo_id = create_item(site, labels)
    geo_item = pywikibot.ItemPage(repo, geo_id)
    geo_item.get()

    #instance of (P82) municipality of Catalonia (Q230463)
    geo_claim = add_claim(site,repo,geo_item, 'P82', 'Q230463', True)
    add_reference(site, repo, geo['url_viaf'], geo_claim)
    
    #part of (P791) Catalonia (Q230464)
    geo_claim = add_claim(site,repo,geo_item, 'P791', 'Q230464', True)
    add_reference(site, repo, geo['url_viaf'], geo_claim)
    
    #si comarca està informat, mira si existeix l'ítem
    if geo['comarca'] != '' and geo['comarca'] is not None:
        search_results = pywikibot.data.api.Request(site=site, action='wbsearchentities', search=geo['comarca'], language='ca', uselang='ca').submit()
        if search_results['search'] and fuzz.ratio(search_results['search'][0]['label'], geo['comarca']) >= 0.75:
            print('dins de search')
            comarca_id = search_results['search'][0]['id']
            print(comarca_id)
        else:
            labels = {"en": geo['comarca'], "ca": geo['comarca']}
            comarca_id = create_item(site, labels)
        
        #located in the administrative territorial entity (P85136)
        geo_claim = add_claim(site,repo,geo_item, 'P85136', comarca_id, True)
        add_reference(site, repo, geo['url_viaf'], geo_claim)
    
    #CANTIC ID (P89586)
    add_identifiers(site, repo, 'P89586', geo['cantic'], geo['url_viaf'], geo_item)
    
    #VIAF ID (P765)
    viaf = geo['url_viaf'].replace('https://viaf.org/viaf/','')
    add_identifiers(site, repo, 'P765', viaf, geo['url_viaf'], geo_item)


