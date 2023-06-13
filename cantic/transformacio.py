import os
import mysql.connector as database
import numpy as np
import pywikibot
import json
import csv
import pandas as pd
import glob

def nom_persones(data, titol):
	nom = data.split(',')
	
	if len(nom) > 1:
		if '.' in data and '(' in titol:
			pos1 = titol.find('(')+1
			pos2 = titol.find(')')
			noms = titol[pos1:pos2]
			print(noms)
		else:
			noms = nom[1].strip().strip('.')
		cognoms = nom[0]
		nom = noms + ' ' + cognoms
	else:
		nom = nom[0]
	return nom

def titol(data):
	dades = data.split('.')
	titol = ''
	any_publicacio = None
	idioma = ''
	if len(dades) > 1:
		parentesis2 = dades[0].find(')')
		if parentesis2 == -1:
			titol = dades[0]
		else:
			parentesis1 = dades[0].find('(')+1
			nom = dades[0][parentesis1:parentesis2]
			if nom.isdigit():
				any_publicacio = int(nom)
			titol = dades[0][parentesis2+1:].strip(',').strip()
		#2 opcions: titol.idioma o titol.seleccions
		if dades[1] != 'Seleccions':
			idioma = dades[1]
		else:
			idioma = ''
			titol = titol + '.' + dades[1]
	return[titol, idioma, any_publicacio]

def naixement_defuncio(dates):
	dates = dates.split('-')
	return dates

def nom_entitats(nom):
	sep = nom.split('.')
	if len(sep) < 2:
		maxim = 1
		sep = [sep[0]]
	else:
		maxim = 2
		sep = [sep[0], sep[1]]
	i = 0
	while i < maxim:
		if '(' in sep[i]:
			index = sep[i].index('(')
			sep[i] = sep[i][0:index]
		i += 1
	return sep

def nom_congressos(nom):
	dic = {}
	nom = nom.split('(')
	if len(nom) > 2:
		nom = [nom[0],nom[2]]
	if len(nom) > 1:
		dic['nom'] = nom[0]
		altres = nom[1].split(':')
		if '' in altres:
			altres.remove('')
		for i in (0,len(altres)-1):
			altres[i] = altres[i].strip()
		any1 = altres[0].strip().replace('[','').replace(']','').split('-')
		if any1[0].isnumeric():
			dic['any_inici'] = altres[0]
			anys = altres[0].split('-')
			if len(anys) > 1:
				dic['any_inici'] = anys[0]
				dic['any_fi'] = anys[1]
			else:
				dic['any_inici'] = altres[0]
				dic['any_fi'] = ''
			dic['edicio'] = ''
			if len(altres) > 1:
				loc = altres[1].split(',')
				if len(loc) > 1:
					dic['ciutat'] = loc[0].strip()
					dic['pais'] = loc[1].strip().replace(')','')
				else:
					dic['ciutat'] = ''
					dic['pais'] = ''
			else:
				dic['ciutat'] = ''
				dic['pais'] = ''
		elif len(altres) > 1:
			if altres[1].split('-')[0].isnumeric():
				anys = altres[1].split('-')
				if len(anys) > 1:
					dic['any_inici'] = anys[0]
					dic['any_fi'] = anys[1]
				else:
					dic['any_inici'] = altres[0]
					dic['any_fi'] = ''
				dic['edicio'] = altres[0]
				if len(altres) > 2:
					dic['ciutat'] = altres[2].split(',')[0]
					dic['pais'] = altres[2].split(',')[1].replace(')','')
		else:
			dic['edicio'] = ''
			dic['any_inici'] = ''
			dic['any_fi'] = ''
			loc = altres[0].split(',')
			if len(loc) > 1:
				dic['ciutat'] = loc[0].strip()
				dic['pais'] = loc[1].strip().replace(')','')
			else:
				dic['ciutat'] = ''
				dic['pais'] = ''

	else:
		dic['nom'] = nom[0]
		dic['edicio'] = ''
		dic['any_inici'] = ''
		dic['any_fi'] = ''
		dic['ciutat'] = ''
		dic['pais'] = ''
	return dic

def nom_obres(titol):
	nom = titol.split('(')
	dic = {}
	if len(nom) > 1:
		dic['nom'] = nom[0].strip()
		dic['tipus'] = 'pel·lícula'
		part = nom[1].split(':')
		if len(part) > 1:
			any_p = part[1].strip().replace(')','')
			if any_p[-4:].isnumeric():
				dic['any'] = any_p[-4:]
			else:
				dic['any'] = ''
		else:
			dic['any'] = ''
	else:
		dic['nom'] = nom[0].strip()
		dic['any'] = ''
		dic['tipus'] = ''
	if '.' in nom[0]:
		idioma = nom[0].split('.')
		dic['nom'] = idioma[0]
		dic['idioma'] = idioma[1]
	else:
		dic['idioma'] = ''
	return dic

def nom_geografics(nom):
	nom = nom.split('(')
	dic = {}
	dic['comunitat'] = 'Catalunya'
	if len(nom) > 1:
		dic['municipi'] = nom[0].strip()
		detalls = nom[1].split(',')
		if len(detalls) > 1:
			dic['comarca'] = detalls[0].strip().replace('(', '')
		else:
			dic['comarca'] = ''
	else:
		dic['municipi'] = ''
		dic['comarca'] = ''
	return dic

def main():
	with open("./dades/cantic_persones.txt", "r") as fp:
	    persones = json.load(fp)

	for key in persones.keys():
		persones[key]['nom'] = nom_persones(persones[key]['nom'], persones[key]['titol'])
		altres = titol(persones[key]['titol'])
		persones[key]['titol'] = altres[0]
		persones[key]['idioma'] = altres[1]
		persones[key]['any_publicacio'] = altres[2]
		dates = naixement_defuncio(persones[key]['dates'])
		persones[key]['data_naixement'] = dates[0]
		if(len(dates) > 1):
			persones[key]['data_defuncio'] = dates[1]
		else:
			persones[key]['data_defuncio'] = ''
		persones[key]['url_viaf'] = persones[key]['url_viaf'].replace('http', 'https')

	with open("./dades_transf/cantic_persones.txt", "w") as fp:
	    json.dump(persones,fp)

	with open("./dades/cantic_entitats.txt", "r") as fp:
	    entitats = json.load(fp)

	for key in entitats.keys():
		entitats[key]['url_viaf'] = entitats[key]['url_viaf'].replace('http', 'https')
		nom = nom_entitats(entitats[key]['nom'])
		if len(nom) > 1:
			entitats[key]['nom'] = nom[0]
			entitats[key]['subtipus'] = nom[1]
		else:
			entitats[key]['nom'] = nom[0]
			entitats[key]['subtipus'] = ''

	with open("./dades_transf/cantic_entitats.txt", "w") as fp:
	    json.dump(entitats,fp)

	with open("./dades/cantic_congressos.txt", "r") as fp:
	    congressos = json.load(fp)

	for key in congressos.keys():
		#NOM en alguns casos: nom(edicio:any:ciutat,comunitat autònoma / país)
		#TITOL: eliminar '.' al final
		if congressos[key]['titol'] != '' and congressos[key]['titol'][-1] == '.':
			congressos[key]['titol'] = congressos[key]['titol'][:-1]
		congressos[key]['url_viaf'] = congressos[key]['url_viaf'].replace('http', 'https')
		dic = nom_congressos(congressos[key]['nom'])
		congressos[key].pop('nom')
		congressos[key].update(dic)

	with open("./dades_transf/cantic_congressos.txt", "w") as fp:
	    json.dump(congressos,fp)

	with open("./dades/cantic_obres.txt", "r") as fp:
	    obres = json.load(fp)
	for key in obres.keys():
		dic = nom_obres(obres[key]['titol'])
		obres[key].pop('titol')
		obres[key].update(dic)
		obres[key]['url_viaf'] = obres[key]['url_viaf'].replace('http','https')
		
	with open("./dades_transf/cantic_obres.txt", "w") as fp:
	    json.dump(obres,fp)

	with open("./dades/cantic_geografics.txt", "r") as fp:
	    geografics = json.load(fp)
	for key in list(geografics):
		#centrar-se només en Catalunya ??
		if 'Catalunya' not in geografics[key]['titol']:
			geografics.pop(key)
		else:
			#nom municipi (comarca a vegades, Catalunya)
			dic = nom_geografics(geografics[key]['titol'])
			geografics[key].pop('titol')
			geografics[key].update(dic)
			geografics[key]['url_viaf'] = geografics[key]['url_viaf'].replace('http','https')
		
	with open("./dades_transf/cantic_geografics.txt", "w") as fp:
	    json.dump(geografics,fp)
main()



