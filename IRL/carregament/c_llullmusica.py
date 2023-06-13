import json
import pywikibot
import numpy as np
import os
from datetime import date
import re
from fuzzywuzzy import fuzz

def create_item(site, label_dict, valueid=None):
    has_claim = False
    aux_id = ''
    search_results = pywikibot.data.api.Request(site=site, action='wbsearchentities', search=label_dict['ca'], strictlanguage=True, language='ca', uselang='ca', limit = '10').submit()
    if search_results['search'] and fuzz.ratio(search_results['search'][0]['label'], label_dict['ca']) >= 0.75:
        for result in search_results["search"]:
            new_id = result['id']
            new_item = pywikibot.ItemPage(site, new_id)
            if valueid is not None:
                print('dins 1r if')
                if 'P82' in new_item.claims:
                    print('dins 2n if')
                    for claim in new_item.claims['P82']:
                        print('dins bucle')
                        print(claim)
                        if claim.target_equals(valueid):
                            print('dins 3r if')
                            has_claim = True
                            return new_id
            else:
                print('dins else')
                has_claim = True
                return new_id
    #crear des de zero
    new_item = pywikibot.ItemPage(site)
    new_item.editLabels(labels=label_dict, summary="Setting labels")
    new_id = new_item.getID()
    return new_id

def add_claim(site, repo, item, property_id, value, is_item=False):
    claim = pywikibot.Claim(repo, property_id)
    if is_item:
        claim_item = pywikibot.ItemPage(repo, value)
        claim.setTarget(claim_item)
    else:
        claim.setTarget(value)
    try:
        if property_id in item.claims.keys() and claim in item.claims[property_id]:
            print('claim already exists')
        else:
            item.addClaim(claim, summary=value)
    except pywikibot.exceptions.IsRedirectPageError as e:
        redirect = e.args[0]
        item_r = pywikibot.ItemPage(site, redirect.title())
        item_r.get()
        if property_id in item_r.claims.keys() and claim in item_r.claims[property_id]:
            print('claim already exists')
        else:
            item_r.addClaim(claim, summary=value)
    return claim

def add_reference(site, repo, url, claim):
    today = date.today()
    ref = pywikibot.Claim(repo, u'P93') #reference url
    ref.setTarget(url)

    retrieved = pywikibot.Claim(repo, u'P146') #date retrieved
    dateCre = pywikibot.WbTime(year=int(today.strftime("%Y")), month=int(today.strftime("%m")), day=int(today.strftime("%d"))) #retrieved -> %DATE TODAY%. Example retrieved -> 29.11.2020
    retrieved.setTarget(dateCre)
    claim.addSources([ref, retrieved], summary=u'Adding reference')

def musics(site, music):
    '''
    {""reference": "https://www.llull.cat/monografics/catalansounds/catalan_sounds.cfm", 
    "nom": "ATLETA", 
    "disc_titol": "Verdad ",
    "web": "http://aloudmusic.com", 
    "management": "ALOUD MUSIC", 
    "disc_any": "2011", 
    "nom_discografica": "ALOUD MUSIC", 
    "web_discografica": "http://aloudmusic.com"
    '''
    repo = site.data_repository()
    #creem primer el disc i després ja crearem el músic
    if music['disc_titol'] !='':
        music['disc_titol'] = music['disc_titol'].strip()
        search_results = pywikibot.data.api.Request(site=site, action='wbsearchentities', search=music['disc_titol'], language='ca', uselang='ca').submit()
        if search_results['search']:
            print('dins de search')
            disc_id = search_results['search'][0]['id']
            print(disc_id)
        else:
            labels = {"en": music['disc_titol'], "ca": music['disc_titol']}
            disc_id = create_item(site, labels)
        disc_item = pywikibot.ItemPage(repo,disc_id)
        
        #instance of (P82) album (Q1785)
        disc_claim = add_claim(site,repo,disc_item, 'P82', 'Q1785', True)
        add_reference(site, repo, music['reference'], disc_claim)
        
        #title (P95)
        disc_claim = add_claim(site,repo,disc_item, 'P95', music['disc_titol'])
        add_reference(site, repo, music['reference'], disc_claim)

        if music['disc_any'] =='':
            date = pywikibot.WbTime(year=int(music['disc_any']))
            
            #publication date (P151)
            disc_claim = add_claim(site,repo,disc_item, 'P151', date)
            add_reference(site, repo, music['reference'], disc_claim)
    
    if music['nom_discografica'] !='':
        music['nom_discografica'] = music['nom_discografica'].strip()
        #afegeix discogràfica
        search_results = pywikibot.data.api.Request(site=site, action='wbsearchentities', search=music['nom_discografica'], language='ca', uselang='ca').submit()
        if search_results['search']:
            print('dins de search')
            discografica_id = search_results['search'][0]['id']
            print(discografica_id)
        else:
            labels = {"en": music['nom_discografica'], "ca": music['nom_discografica']}
            discografica_id = create_item(site, labels)
        discografica_item = pywikibot.ItemPage(repo,discografica_id)
        
        #official website (P21)
        if music['web_discografica'] !='':
            discografica_claim = add_claim(site,repo,discografica_item, 'P21', 'https://'+music['web_discografica'].replace('http://',''))
            add_reference(site, repo, music['reference'], discografica_claim)
            
    #record label (P95963)
    if music['disc_titol'] !='':
        disc_claim = add_claim(site,repo,disc_item, 'P95963', discografica_id, True)
        add_reference(site, repo, music['reference'], disc_claim)
        music['nom'] = music['nom'].strip()
        
    #afegeix nom de l'autor
    search_results = pywikibot.data.api.Request(site=site, action='wbsearchentities', search=music['nom'], language='ca', uselang='ca').submit()
    if search_results['search']:
        print('dins de search')
        music_id = search_results['search'][0]['id']
        print(music_id)
    else:
        labels = {"en": music['nom'], "ca": music['nom']}
        music_id = create_item(site, labels)
    music_item = pywikibot.ItemPage(repo, music_id)
    
    #instance of (P82) human (Q497)
    music_claim = add_claim(site,repo,music_item, 'P82', 'Q497', True)
    add_reference(site, repo, music['reference'], music_claim)
    
    #instance of (P82) musician
    music_claim = add_claim(site,repo,music_item, 'P82', 'Q36741', True)
    add_reference(site, repo, music['reference'], music_claim)
    
    #occupation (P204) musician (Q36741)
    music_claim = add_claim(site,repo,music_item, 'P204', 'Q36741', True)
    add_reference(site, repo, music['reference'], music_claim)
    
    #official website (P21)
    if music['web'] !='':
        music_claim = add_claim(site,repo,music_item, 'P21', 'https://'+music['web'].replace('http://',''))
        add_reference(site, repo, music['reference'], music_claim)
    if music['management'] !='':
        music['management'] = music['management'].strip()
        #afegeix mànager
        search_results = pywikibot.data.api.Request(site=site, action='wbsearchentities', search=music['management'], language='ca', uselang='ca').submit()
        if search_results['search']:
            print('dins de search')
            management_id = search_results['search'][0]['id']
            print(management_id)
        else:
            labels = {"en": music['management'], "ca": music['management']}
            management_id = create_item(site, labels)
        #represents (P95550)
        music_claim = add_claim(site,repo,music_item, 'P95550', management_id, True)
        add_reference(site, repo, music['reference'], music_claim)
        
    #notable work
    if music['disc_titol'] !='':
        music_claim = add_claim(site,repo,music_item, 'P95835', disc_id, True)
        add_reference(site, repo, music['reference'], music_claim)
        

def bibliografies(site, bibliografia):
    repo = site.data_repository()
    '''
    "reference": "https://www.llull.cat/monografics/newcatalanmusic/catala/search.cfm", 
    "titol": "Xavier Benguerel", 
    "editorial": "Essay", 
    "lloc_edicio": "Barcelona", 
    "autor_llibre": "Josep Soler", 
    "any_edicio": "1969", 
    "music": "Xavier Benguerel"
    '''

    #creem primer el music i l'autor i després el llibre
    search_results = pywikibot.data.api.Request(site=site, action='wbsearchentities', search=bibliografia['autor_llibre'].strip(), language='ca', uselang='ca').submit()
    
    #afegeix autor
    if search_results['search']:
        autor_id = search_results['search'][0]['id']
    else:
        labels = {"en": bibliografia['autor_llibre'].strip(), "ca": bibliografia['autor_llibre'].strip()}
        autor_id = create_item(site, labels)
    print('id autor ' + autor_id)
    print('nom autor ' + bibliografia['autor_llibre'].strip())
    #afegeix music
    search_results = pywikibot.data.api.Request(site=site, action='wbsearchentities', search=bibliografia['music'].strip(), language='ca', uselang='ca').submit()
    if search_results['search']:
        music_id = search_results['search'][0]['id']
    else:
        labels = {"en": bibliografia['music'].strip(), "ca": bibliografia['music'].strip()}
        music_id = create_item(site, labels)
    print('id music ' + music_id)
    print('nom music ' + bibliografia['music'].strip())
    #afegeix editorial
    search_results = pywikibot.data.api.Request(site=site, action='wbsearchentities', search=bibliografia['editorial'].strip(), language='ca', uselang='ca').submit()
    if search_results['search']:
        editorial_id = search_results['search'][0]['id']
    else:
        labels = {"en": bibliografia['editorial'].strip(), "ca": bibliografia['editorial'].strip()}
        editorial_id = create_item(site, labels)
    print('id editorial ' + editorial_id)
    print('nom editorial ' + bibliografia['editorial'].strip())
    #afegeix ciutat
    if bibliografia['lloc_edicio'] !='':
        search_results = pywikibot.data.api.Request(site=site, action='wbsearchentities', search=bibliografia['lloc_edicio'].strip(), language='ca', uselang='ca').submit()
        if search_results['search']:
            city_id = search_results['search'][0]['id']
        else:
            labels = {"en": bibliografia['lloc_edicio'].strip(), "ca": bibliografia['lloc_edicio'].strip()}
            city_id = create_item(site, labels)
        print('id ciutat ' + city_id)
        print('nom ciutat ' + bibliografia['lloc_edicio'].strip())
    #ara creem el llibre
    labels = {"en": bibliografia['titol'].strip(), "ca": bibliografia['titol'].strip()}
    llibre_id = create_item(site, labels)
    print('id llibre ' + llibre_id)
    print('nom llibre ' + bibliografia['titol'].strip())
    llibre_item = pywikibot.ItemPage(repo,llibre_id)
    #instance of (P82) book (Q131598)
    llibre_claim = add_claim(site,repo,llibre_item, 'P82', 'Q131598', True)
    add_reference(site, repo, bibliografia['reference'], llibre_claim)
    
    #title (P95)
    llibre_claim = add_claim(site,repo,llibre_item, 'P95', bibliografia['titol'].strip())
    add_reference(site, repo, bibliografia['reference'], llibre_claim)
    
    #publisher (P145)
    llibre_claim = add_claim(site,repo,llibre_item, 'P145', editorial_id, True)
    add_reference(site, repo, bibliografia['reference'], llibre_claim)
    
    #author (P95656)
    llibre_claim = add_claim(site,repo,llibre_item, 'P95656', autor_id, True)
    add_reference(site, repo, bibliografia['reference'], llibre_claim)
    
    #author (P95656)
    llibre_claim = add_claim(site,repo,llibre_item, 'P95656', music_id, True)
    add_reference(site, repo, bibliografia['reference'], llibre_claim)
    
    #location (P286)
    if bibliografia['lloc_edicio'] !='':
        llibre_claim = add_claim(site,repo,llibre_item, 'P286', city_id, True)
        add_reference(site, repo, bibliografia['reference'], llibre_claim)
        
    date = pywikibot.WbTime(year=int(bibliografia['any_edicio']))
    
    #publication date (P151)
    llibre_claim = add_claim(site,repo,llibre_item, 'P151', date)
    add_reference(site, repo, bibliografia['reference'], llibre_claim)
    
    #language of work (P77090) Spanish (Q564)
    llibre_claim = add_claim(site,repo,llibre_item, 'P77090', 'Q564', True)
    add_reference(site, repo, bibliografia['reference'], llibre_claim)

def biografies(site, biografia):
    repo = site.data_repository()
    
    '''
    "reference": "https://www.llull.cat/monografics/newcatalanmusic/catala/bio.cfm?id=3002", 
    "nom": "Joan Albert", 
    "cognoms": "Amargós", 
    "lloc_naixement": "Barcelona", 
    "web": "www.accompositors.com/compositores-curriculum.php?idComp=4", 
    "cataleg": "www.accompositors.com/compositores-curriculum.php?idComp=4", 
    "any_naixement": "1950", 
    "editorials": "Catalana d'Edicions Musicals, Editorial de Música Boileau, UME - Unión Musical Ediciones "
    '''
    
    nom_complert = biografia['nom'] + ' ' + biografia['cognoms']
    labels = {"en": nom_complert.strip(), "ca": nom_complert.strip()}
    autor_id = create_item(site,labels)
    autor_item = pywikibot.ItemPage(repo,autor_id)
    print('id autor ' + autor_id)
    print('nom autor ' + nom_complert.strip())
    #instance of (P82) human (Q497)
    autor_claim = add_claim(site,repo,autor_item, 'P82', 'Q497', True)
    add_reference(site, repo, biografia['reference'], autor_claim)
    
    #afegint given name (P187)
    search_results = pywikibot.data.api.Request(site=site, action='wbsearchentities', search=biografia['nom'].strip(), language='ca', uselang='ca').submit()
    if search_results['search']:
        nom_id = search_results['search'][0]['id']
    else:
        labels = {"en": biografia['nom'].strip(), "ca": biografia['nom'].strip()}
        nom_id = create_item(site, labels)
    print('given name ' + nom_id)
    autor_claim = add_claim(site,repo,autor_item, 'P187', nom_id, True)
    add_reference(site, repo, biografia['reference'], autor_claim)
    
    #afegint family name (P734)
    cognoms = biografia['cognoms'].split(' ')
    for cognom in cognoms:
        if cognom.strip() is not None and cognom.strip() != '':
            search_results = pywikibot.data.api.Request(site=site, action='wbsearchentities', search=cognom.strip(), language='ca', uselang='ca').submit()
            if search_results['search']:
                cognom_id = search_results['search'][0]['id']
            else:
                labels = {"en": cognom.strip(), "ca": cognom.strip()}
                cognom_id = create_item(site, labels)
            print('cognom ' + cognom_id)
            autor_claim = add_claim(site,repo,autor_item, 'P734', cognom_id, True)
            add_reference(site, repo, biografia['reference'], autor_claim)
        
    #afegint lloc de naixement (P286)
    search_results = pywikibot.data.api.Request(site=site, action='wbsearchentities', search=biografia['lloc_naixement'].strip(), language='ca', uselang='ca').submit()
    if search_results['search']:
        city_id = search_results['search'][0]['id']
    else:
        labels = {"en": biografia['lloc_naixement'].strip(), "ca": biografia['lloc_naixement'].strip()}
        city_id = create_item(site, labels)
    print('ciutat ' + city_id)
    autor_claim = add_claim(site,repo,autor_item, 'P286', city_id, True)
    add_reference(site, repo, biografia['reference'], autor_claim)
    
    #official website (P21)
    if biografia['web'] !='':
        autor_claim = add_claim(site,repo,autor_item,'P21','https://'+biografia['web'].replace('http://', '').replace('https://','').strip())
        add_reference(site, repo, biografia['reference'], autor_claim)
        
    #official website (P21)
    if biografia['cataleg'] !='':
        autor_claim = add_claim(site,repo,autor_item,'P21','https://'+biografia['cataleg'].replace('http://', '').replace('https://','').strip())
        add_reference(site, repo, biografia['reference'], autor_claim)
        
    date = pywikibot.WbTime(year=int(biografia['any_naixement'].strip()))
    
    #date of birth (P18)
    autor_claim = add_claim(site,repo,autor_item,'P18',date)
    add_reference(site, repo, biografia['reference'], autor_claim)
    
    #afegint editorials publisher (P145)
    if biografia['editorials'] !='':
        editorials = biografia['editorials'].split(', ')
        for editorial in editorials:
            search_results = pywikibot.data.api.Request(site=site, action='wbsearchentities', search=editorial.strip(), language='ca', uselang='ca').submit()
            if search_results['search']:
                editorial_id = search_results['search'][0]['id']
            else:
                labels = {"en": editorial.strip(), "ca": editorial.strip()}
                editorial_id = create_item(site, labels)
            print('editorial ' + editorial_id)
            autor_claim = add_claim(site,repo,autor_item, 'P145', editorial_id, True)
            add_reference(site, repo, biografia['reference'], autor_claim)

def discografies(site, discografica):
    #primer s'han de crear les discogràfiques
    #després es crea la discografia
    #per afegir l'autor, creem el ítem però l'omplim més tard

    '''"reference": "https://www.llull.cat/monografics/newcatalanmusic/catala/search.cfm", 
    "titol": "Concerto pour clarinette, Sonatas, Trio", 
    "discografica": "Harmonia Mundi", 
    "any_edicio": "1996", 
    "autor": "Joan Albert Amarg\u00f3s"
    '''
    repo = site.data_repository()
    if discografica['discografica'] =='':
        return
    labels = {"en": discografica['discografica'].strip(), "ca": discografica['discografica'].strip()}
    discografica_id = create_item(site, labels)
    discografica_item = item = pywikibot.ItemPage(repo, discografica_id)
    print('id discografica ' + discografica_id)
    print('nom discografica ' + discografica['discografica'].strip())
    #instance of (P82) record label (Q1793)
    discografica_claim = add_claim(site,repo,discografica_item, 'P82', 'Q1793', True)
    add_reference(site, repo, discografica['reference'], discografica_claim)
    
    #ara que tenim la discografica, creem la discografia
    labels = {"en": discografica['titol'].strip(), "ca": discografica['titol'].strip()}
    disc_id = create_item(site, labels)
    disc_item = pywikibot.ItemPage(repo, disc_id)
    print('id disc ' + disc_id)
    print('nom disc ' + discografica['titol'].strip())
    
    #instance of (P82) album (Q1785)
    disc_claim = add_claim(site, repo, disc_item, 'P82', 'Q1785', True)
    add_reference(site, repo, discografica['reference'], disc_claim)
    
    #title (P95)
    disc_claim = add_claim(site, repo, disc_item, 'P95', discografica['titol'].strip())
    add_reference(site, repo, discografica['reference'], disc_claim)
    
    #record label (P95963)
    disc_claim = add_claim(site, repo, disc_item, 'P95963', discografica_id, True)
    add_reference(site, repo, discografica['reference'], disc_claim)
    date = pywikibot.WbTime(year = int(discografica['any_edicio']))
    
    #publication date (P151)
    disc_claim = add_claim(site, repo, disc_item, 'P151', date)
    add_reference(site, repo, discografica['reference'], disc_claim)
    
    #creem el músic i el guardem al dict
    labels = {"en": discografica['autor'].strip(), "ca": discografica['autor'].strip()}
    
    #afegint author (P95656)
    search_results = pywikibot.data.api.Request(site=site, action='wbsearchentities', search=discografica['autor'].strip(), language='ca', uselang='ca').submit()
    if search_results['search']:
        autor_id = search_results['search'][0]['id']
    else:
        autor_id = create_item(site, labels)
    print('autor ' + autor_id)
    autor_item = pywikibot.ItemPage(repo, autor_id)
    disc_claim = add_claim(site, repo, disc_item, 'P95656', autor_id, True)
    add_reference(site, repo, discografica['reference'], disc_claim)

    return [discografica_id, autor_id]

def editorials(site, editorial):
    
    #for item in editorials.keys():
    '''
    {'reference': 'https://www.llull.cat/monografics/newcatalanmusic/catala/search.cfm', 
    'nom': 'BabelScores', 
    'ciutat': 'Paris', 
    'pais': 'França', 
    'web': 'www.babelscores.com'}
    '''
    repo = site.data_repository()
    
    #creem item i li posem nom
    labels = {"en": editorial['nom'],"ca": editorial['nom']}
    item_id = create_item(site, labels,'Q214707')
    print('editorial ' + item_id)
    print('nom ' + editorial['nom'])
    item = pywikibot.ItemPage(repo, item_id)
    
    #official website (P21)
    if editorial['web'] !='':
        stringclaim = add_claim(site,repo,item,'P21','https://'+editorial['web'].replace('http://','').replace('https://','').strip())
        #afegim referències al claim (reference url P93, date retrieved P146 a test:wikidata)
        add_reference(site, repo, editorial['reference'], stringclaim)
        
    #instance of (P82) publisher (Q214707)
    stringclaim = add_claim(site,repo,item,'P82','Q214707',True)
    add_reference(site, repo, editorial['reference'], stringclaim)

    #afegint location (P286) ciutat
    labels = {"en": editorial['ciutat'],"ca": editorial['ciutat']}
    city_id = create_item(site, labels)
    print('city ' + city_id)
    cityclaim = add_claim(site,repo,item,'P286',city_id, True)
    add_reference(site, repo, editorial['reference'], cityclaim)

    #afegint location (P286) país
    labels = {"en": editorial['pais'],"ca": editorial['pais']}
    country_id = create_item(site, labels)
    print('country ' + country_id)
    countryclaim = add_claim(site,repo,item,'P286',country_id, True)
    add_reference(site, repo, editorial['reference'], countryclaim)


