import os
import mysql.connector as database
import numpy as np

def categories(data):
	categories={}
	try:
		for values in data:
			categories[values[0]] = values[1]
	except database.Error as e:
		print(f"Error retrieving entry from database: {e}")
	return categories

def editorials(data):
	editorials={}
	try:
		for values in data:
			editorials[values[0]] = {}
			editorials[values[0]]['nom'] = values[1]
			editorials[values[0]]['reference'] = 'https://www.llull.cat/catala/literatura/trac_traduccions.cfm'
	except database.Error as e:
		print(f"Error retrieving entry from database: {e}")
	return editorials


def contactes(data):
	contactes={}
	pids = {
	 1:'nom',
	 2:'mail',
	 3:'empresa',
	 4:'link'
	}
	try:
		for values in data:
			for i in range(0,5):
				if i == 0:
					contactes[values[0]] = {}
					contactes[values[0]]['reference'] = 'https://www.llull.cat/catala/literatura/trac_traduccions.cfm'
				else:
					contactes[values[0]][pids[i]] = values[i]
	except database.Error as e:
		print(f"Error retrieving entry from database: {e}")
	return contactes

def quad_premis(data):
	quad_premis={}
	pids = {
	 1:'nom',
	 2:'any',
	 3:'link_quad'
	}
	try:
		for values in data:
			for i in range(0,4):
				if i == 0:
					quad_premis[values[0]] = {}
					quad_premis[values[0]]['reference'] = 'https://www.llull.cat/catala/literatura/trac_traduccions.cfm'
				else:
					quad_premis[values[0]][pids[i]] = values[i]
	except database.Error as e:
		print(f"Error retrieving entry from database: {e}")
	return quad_premis

def documents(data, editorials, categories, idiomes):
	documents={}
	pids = {
	 1:'titol', 
	 2:'titol_original', 
	 3:'subtitol', 
	 4:'lloc_edicio', 
	 5:'isbn', 
	 6:'any_edicio', 
	 7:'editorial', 
	 8:'genere', 
	 9:'llengua', 
	 10:'categoria'
	}

	try:
		for values in data:
			for i in range(0,11):
				if i == 0:
					documents[values[0]] = {}
					documents[values[0]]['reference'] = 'https://www.llull.cat/catala/literatura/trac_traduccions.cfm'
				elif i == 7:
					append = ''
					if values[i] and values[i] != '':
						editorial = values[i].split(',')
						for ed in editorial:
							if int(ed) in editorials.keys():
								append += editorials[int(ed)]['nom'] + ', '
						append = append[:-2]
					documents[values[0]][pids[i]] = append
				elif i == 8:
					append = ''
					if values[i] and values[i] != '':
						genere = values[i].split(',')
						for g in genere:
							if int(g) in categories:
								append += categories[int(g)].split(' / ')[0] + ', '
						append = append[:-2]
					documents[values[0]][pids[i]] = append
				elif i == 9:
					append = ''
					if values[i] and values[i] != '':
						idioma = values[i].split(',')
						for a in idioma:
							if int(a) in idiomes:
								append += idiomes[int(a)].split(' / ')[0] + ', '
						append = append[:-2]
					documents[values[0]][pids[i]] = append
				elif i == 10:
					generes = documents[values[0]]['genere']
					if generes is None:
						generes = ''
					if values[i] in categories:
						generes += categories[int(values[i])]
					documents[values[0]][pids[i]] = generes 
				else:
					documents[values[0]][pids[i]] = values[i]
	except database.Error as e:
		print(f"Error retrieving entry from database: {e}")
	return documents

def llibres(data, editorials, categories, contactes, quad_premis):
	llibres={}
	pids = {
	 1:'titol_cat', 
	 2:'titol_eng', 
	 3:'format', 
	 4:'any', 
	 5:'pagines', 
	 6:'editorial', 
	 7:'contactes', 
	 8:'quadernet', 
	 9:'genere'
	}
	try:
		for values in data:
			for i in range(0,10):
				if i == 0:
					llibres[values[0]] = {}
					llibres[values[0]]['reference'] = 'https://www.llull.cat/catala/literatura/trac_traduccions.cfm'
				elif i == 6:
					if values[i] and values[i] != '':
						if int(values[i]) in editorials:
							llibres[values[0]][pids[i]] = editorials[int(values[i])]['nom']
				elif i == 7:
					append = ''
					if values[i] and values[i] != '':
						contacte = values[i].split(',')
						for c in contacte:
							if int(c) in contactes:
								append += contactes[int(c)]['nom'] + ', '
						append = append[:-2]
					llibres[values[0]][pids[i]] = append
				elif i == 8:
					if values[i] and values[i] != '':
						if int(values[i]) in quad_premis:
							llibres[values[0]][pids[i]] = quad_premis[int(values[i])]['nom']
				elif i == 9:
					if values[i] and values[i] != '':
						if int(values[i]) in categories:
							llibres[values[0]][pids[i]] = categories[int(values[i])]
				else:
					llibres[values[0]][pids[i]] = values[i]
	except database.Error as e:
		print(f"Error retrieving entry from database: {e}")
	return llibres

def traductors(data, idiomes, categories):
	traductors={}
	pids = {
	 1:'nom_complert',
	 2:'especialitat', 
	 3:'llengua'
	}
	try:
		for values in data:
			for i in range(0,4):
				if i == 0:
					if values[4] and values[4] != '':
						traductors[int(values[4])] = {}
						traductors[int(values[4])]['reference'] = 'https://www.llull.cat/catala/literatura/tralicat_traductors.cfm'
					else:
						traductors[values[0]] = {}
						traductors[values[0]]['reference'] = 'https://www.llull.cat/catala/literatura/tralicat_traductors.cfm'
				elif i == 2:
					append = ''
					if values[i] and values[i] != '':
						especialitat = values[i].split(',')
						for es in especialitat:
							if int(es) in categories:
								append += categories[int(es)] + ', '
						append = append[:-2]
					if values[4] and values[4] != '':
						traductors[int(values[4])][pids[i]] = append
					else:
						traductors[values[0]][pids[i]] = append
				elif i == 3:
					append = ''
					if values[i] and values[i] != '':
						idioma = values[i].split(',')
						for a in idioma:
							if int(a) in idiomes:
								append += idiomes[int(a)].split(' / ')[0] + ', '
						append = append[:-2]
					if values[4] and values[4] != '':
						traductors[int(values[4])][pids[i]] = append
					else:
						traductors[values[0]][pids[i]] = append
				else:
					if values[4] and values[4] != '':
						traductors[int(values[4])][pids[i]] = values[i]
					else:
						traductors[values[0]][pids[i]] = values[i]
	except database.Error as e:
		print(f"Error retrieving entry from database: {e}")
	return traductors


