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

def companyies(site):
    '''
    {"reference": "https://www.llull.cat/monografics/performingarts/catala/companyia.cfm?id=10",
    "descr": "", 
    "nom": "Camut Band", 
    "web": "www.camutband.com"
    '''
    repo = site.data_repository()
    with open('./dades/catarts_companyies.txt', 'r') as fp:
        companyies = json.load(fp)
    companyia = companyies['10']
    labels = {"en": companyia['nom'], "ca": companyia['nom']}
    companyia_id = create_item(site, labels)
    companyia_item = pywikibot.ItemPage(repo, companyia_id)
    
    #instance of (P82) group (Q215138)
    comp_claim = add_claim(site,repo,companyia_item, 'P82', 'Q215138', True)
    add_reference(site, repo, companyia['reference'], comp_claim)
    
    #official website (P21)
    if companyia['web'] is not None and companyia['web'] != '':
        comp_claim = add_claim(site,repo,companyia_item, 'P21', 'https://' + companyia['web'].replace('http://',''))
        add_reference(site, repo, companyia['reference'], comp_claim)
        
    #afegint descripcions
    if companyia['descr'] !='':
        companyia_item.descriptions["en"] = companyia['descr']
        companyia_item.descriptions["ca"] = companyia['descr']
        companyia_item.editEntity(data = companyia_item.toJSON(),summary='descr')

def contactes(site):
    '''
    "reference": "https://www.llull.cat/monografics/performingarts/catala/index.cfm", 
    "carrec": "Director artístic", 
    "nom": "Rafael Méndez", 
    "web": null}
    '''
    repo = site.data_repository()
    with open('./dades/catarts_contactes.txt','r') as fp:
        contactes = json.load(fp)
    contacte = contactes['14']
    labels = {"en": contacte['nom'], 'ca': contacte['nom']}
    contacte_id = create_item(site, labels)
    contacte_item = pywikibot.ItemPage(repo, contacte_id)
    
    #instance of (P82) human (Q497)
    cont_claim = add_claim(site,repo,contacte_item, 'P82', 'Q497', True)
    add_reference(site, repo, contacte['reference'], cont_claim)
    
    #afegeix official website (P21) si existeix
    if contacte['web'] is not None and contacte['web'] != '':
        cont_claim = add_claim(site,repo,contacte_item, 'P21', 'https://' + contacte['web'].replace('http://',''))
        add_reference(site, repo, contacte['reference'], cont_claim)
    if contacte['carrec'] == 'Mànager':
        q = 'Q230223'
    elif contacte['carrec'] == 'Director artístic':
        q = 'Q230224'
    elif contacte['carrec'] == 'Coreògraf':
        q = 'Q230225'
    
    #occupation (P204)
    if contacte['carrec'] !='':
        cont_claim = add_claim(site,repo,contacte_item, 'P204', q, True)
        add_reference(site, repo, contacte['reference'], cont_claim)
    nom = contacte['nom'].split(' ')
    search_results = pywikibot.data.api.Request(site=site, action='wbsearchentities', search=nom[0], language='ca', uselang='ca').submit()
    
    #afegeix given name (P187)
    if search_results['search'] and search_results['search'][0]['label'] == nom[0]:
        print('dins de search')
        nom_id = search_results['search'][0]['id']
        print(nom_id)
    else:
        labels = {"en": nom[0], "ca": nom[0]}
        nom_id = create_item(site, labels)
    cont_claim = add_claim(site,repo,contacte_item, 'P187', nom_id, True)
    add_reference(site, repo, contacte['reference'], cont_claim)
    cognoms = nom[1:]
    for cognom in cognoms:
        search_results = pywikibot.data.api.Request(site=site, action='wbsearchentities', search=cognom, language='ca', uselang='ca').submit()
        
        #afegeix family name (P734)
        if search_results['search'] and search_results['search'][0]['label'] == cognom:
            print('dins de search')
            cognom_id = search_results['search'][0]['id']
            print(cognom_id)
        else:
            labels = {"en": cognom, "ca": cognom}
            cognom_id = create_item(site, labels)
        cont_claim = add_claim(site,repo,contacte_item, 'P734', cognom_id, True)
        add_reference(site, repo, contacte['reference'], cont_claim)
    
def espectacles(site):
    repo = site.data_repository()
    with open('./dades/catarts_espectacles.txt', 'r') as fp:
        espectacles = json.load(fp)
    espectacle = espectacles['1251']

    print(espectacle)
    '''
    {"17": {"reference": "https://www.llull.cat/monografics/performingarts/catala/espectacle.cfm?id=17", 
    "titol": "Kiting Kita Walking with rhythm.", 
    "companyia": "Camut Band",
    "idioma_espectacle": "català, castellà, anglès, francès, ''", 
    "any": "2005", 
    "autor": "", nom
    "direccio": "", nom
    "num_interprets": "5", 
    "durada": "1 h. 20 min"
    '''
    #busquem companyia, idioma, autor i direcció
    if espectacle['companyia'] !='':
        search_results = pywikibot.data.api.Request(site=site, action='wbsearchentities', search=espectacle['companyia'], language='ca', uselang='ca').submit()
        if search_results['search'] and search_results['search'][0]['label'] == espectacle['companyia']:
            print('dins de search')
            comp_id = search_results['search'][0]['id']
            print(comp_id)
        else:
            labels = {"en": espectacle['companyia'], "ca": espectacle['companyia']}
            comp_id = create_item(site, labels)
    if espectacle['idioma_espectacle'] !='':
        idiomes = espectacle['idioma_espectacle'].split(', ')
        idiomes_arr = []
        for idioma in idiomes:
            search_results = pywikibot.data.api.Request(site=site, action='wbsearchentities', search=idioma, language='ca', uselang='ca').submit()
            if search_results['search'] and search_results['search'][0]['label'] == idioma:
                print('dins de search')
                idioma_id = search_results['search'][0]['id']
                print(idioma_id)
            else:
                labels = {"en": idioma, "ca": idioma}
                idioma_id = create_item(site, labels)
            idiomes_arr.append(idioma_id)
    if espectacle['autor'] is not None and espectacle['autor'] != '':
        search_results = pywikibot.data.api.Request(site=site, action='wbsearchentities', search=espectacle['autor'], language='ca', uselang='ca').submit()
        if search_results['search'] and search_results['search'][0]['label'] == espectacle['autor']:
            print('dins de search')
            autor_id = search_results['search'][0]['id']
            print(autor_id)
        else:
            labels = {"en": espectacle['autor'], "ca": espectacle['autor']}
            autor_id = create_item(site, labels)
    if espectacle['direccio'] is not None and espectacle['direccio'] != '':
        search_results = pywikibot.data.api.Request(site=site, action='wbsearchentities', search=espectacle['direccio'], language='ca', uselang='ca').submit()
        if search_results['search'] and search_results['search'][0]['label'] == espectacle['direccio']:
            print('dins de search')
            dir_id = search_results['search'][0]['id']
            print(dir_id)
        else:
            labels = {"en": espectacle['direccio'], "ca": espectacle['direccio']}
            dir_id = create_item(site, labels)
        
    espectacle['titol'] = espectacle['titol'].strip().strip('.')
    print(espectacle['titol'])
    labels = {'en': espectacle['titol'], 'ca': espectacle['titol']}
    espectacle_id = create_item(site, labels)
    espectacle_item = pywikibot.ItemPage(repo, espectacle_id)
    
    #instance of (P82) show (Q223670)
    esp_claim = add_claim(site,repo,espectacle_item, 'P82', 'Q223670', True)
    add_reference(site, repo, espectacle['reference'], esp_claim)
    
    #author (P95656)
    if espectacle['companyia'] !='':
        esp_claim = add_claim(site,repo,espectacle_item, 'P95656', comp_id, True)
        add_reference(site, repo, espectacle['reference'], esp_claim)
    
    if espectacle['idioma_espectacle'] !='':
        for idioma_id in idiomes_arr:
            #language (P226)
            esp_claim = add_claim(site,repo,espectacle_item, 'P226', idioma_id, True)
            add_reference(site, repo, espectacle['reference'], esp_claim)
    
    if espectacle['any'] is not None and espectacle['any'] != '':
        date = pywikibot.WbTime(year=int(espectacle['any']))
        #date of publication (P151)
        esp_claim = add_claim(site,repo,espectacle_item, 'P151', date)
        add_reference(site, repo, espectacle['reference'], esp_claim)
        
    #author (P95656)
    if espectacle['autor'] is not None and espectacle['autor'] != '':
        esp_claim = add_claim(site,repo,espectacle_item, 'P95656', autor_id, True)
        add_reference(site, repo, espectacle['reference'], esp_claim)
        
    #director (P778)
    if espectacle['direccio'] is not None and espectacle['direccio'] != '':
        esp_claim = add_claim(site,repo,espectacle_item, 'P778', dir_id, True)
        add_reference(site, repo, espectacle['reference'], esp_claim)
    
    if espectacle['num_interprets'] is not None and espectacle['num_interprets'] != '':
        quant = pywikibot.WbQuantity(int(espectacle['num_interprets']), site = site)
        #member count (P97564)
        esp_claim = add_claim(site,repo,espectacle_item, 'P97564', quant)
        add_reference(site, repo, espectacle['reference'], esp_claim)
    
    if espectacle['durada'] is not None and espectacle['durada'] != '':
        duration = espectacle['durada']
        duration = list(map(int, re.findall(r'\d+', duration)))
        print(duration)
        if len(duration) > 1: #h i mins
            duration = duration[0]*60 + duration[1]
        else: #només mins
            duration = duration[0]
        print(duration)
        unit_item = pywikibot.ItemPage(site, 'Q230331')
        duration = pywikibot.WbQuantity(amount = duration, unit = unit_item, site = site)
        #duration (P374)
        esp_claim = add_claim(site,repo,espectacle_item, 'P374', duration)
        add_reference(site, repo, espectacle['reference'], esp_claim)

def create_genres(site, repo):
    with open('./dades/catarts_generes.txt', 'r') as fp:
        generes = json.load(fp)
    result = {}
    for key in generes.keys():
        search_results = pywikibot.data.api.Request(site=site, action='wbsearchentities', search=generes[key], language='ca', uselang='ca').submit()
        if search_results['search'] and search_results['search'][0]['label'] == generes[key]:
            print('dins de search')
            genere_id = search_results['search'][0]['id']
            print(genere_id)
        else:
            labels = {"en": generes[key], "ca": generes[key]}
            genere_id = create_item(site, labels)
        result[generes[key]] = genere_id
    return result

def festivals(site):
    '''
    {"736": {"reference": "https://www.llull.cat/monografics/performingarts/catala/index.cfm", 
    "nom": "* Festival de proves", 
    "descr": "",
    "ubicacio": "", 
    "categoria": "", 
    "web": "http://www.proves.com"}
    '''
    repo = site.data_repository()
    with open('./dades/catarts_festivals.txt', 'r') as fp:
        festivals = json.load(fp)
    festival = festivals['877']
    
    genres = create_genres(site, repo)
    labels = {'en': festival['nom'], 'ca': festival['nom']}
    festival_id = create_item(site, labels)
    festival_item = pywikibot.ItemPage(repo, festival_id)
    if festival['descr'] !='':
        festival_item.descriptions["ca"] = festival['descr'][0:250]
        festival_item.editEntity(data = festival_item.toJSON(),summary='descr')
        
    #instance of (P82) festival (Q230239)
    fest_claim = add_claim(site,repo,festival_item, 'P82', 'Q230239', True)
    add_reference(site, repo, festival['reference'], fest_claim)
    if festival['ubicacio'] !='':
        cities = festival['ubicacio'].split(',')
        #afegeix totes les ciutats on s'ha fet el festival
        for city in cities:
            city = city.strip()
            search_results = pywikibot.data.api.Request(site=site, action='wbsearchentities', search=city, language='ca', uselang='ca').submit()
            if search_results['search'] and search_results['search'][0]['label'] == city:
                print('dins de search')
                city_id = search_results['search'][0]['id']
                print(city_id)
            else:
                labels = {"en": city, "ca": city}
                city_id = create_item(site, labels)
            #location (P286)
            fest_claim = add_claim(site,repo,festival_item, 'P286', city_id, True)
            add_reference(site, repo, festival['reference'], fest_claim)
        
    #official website (P206)
    if festival['web'] !='':
        fest_claim = add_claim(site,repo,festival_item, 'P206', 'https://' + festival['web'].replace('http://','').strip())
        add_reference(site, repo, festival['reference'], fest_claim)
    if festival['categoria'] !='':
        for item in festival['categoria'].split(', '):
            genere_id = genres[item]
            #type (P797)
            fest_claim = add_claim(site,repo,festival_item, 'P797', genere_id, True)
            add_reference(site, repo, festival['reference'], fest_claim)
