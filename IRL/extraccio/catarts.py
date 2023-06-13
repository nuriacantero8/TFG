import os
import mysql.connector as database
import numpy as np

def categories(data):
	categories = {}
	pids = {
		1:'nom'
	}
	try:
		for values in data:
			categories[values[0]] = values[1]
	except database.Error as e:
		print(f"Error retrieving entry from database: {e}")
	return categories

def companyies(data):
	companyies = {}
	pids = {
		1:'descr',
		2:'nom',
		3:'web',
		4:'facebook',
		5:'twitter',
		6:'myspace'
	}
	try:
		for values in data:
			for i in range(0,7):
				if i == 0:
					companyies[values[0]] = {}
					companyies[values[0]]['reference'] = 'https://www.llull.cat/monografics/performingarts/catala/companyia.cfm?id=' + str(values[0])
				else:
					companyies[values[0]][pids[i]] = values[i]
	except database.Error as e:
		print(f"Error retrieving entry from database: {e}")
	return companyies

def contactes(data, companyies, carrecs):
	contactes = {}
	pids = {
		1:'companyia', 
		2:'carrec', 
		3:'nom', 
		4:'adresa', 
		5:'cp', 
		6:'localitat', 
		#7:'telf', 
		7:'email', 
		8:'facebook', 
		9:'twitter', 
		10:'myspace', 
		11:'altres', 
		12:'web'
	}
	try:
		for values in data:
			for i in range(0,13):
				if i == 0:
					contactes[values[0]] = {}
					contactes[values[0]]['reference'] = 'https://www.llull.cat/monografics/performingarts/catala/index.cfm'
				elif i == 1:
					if values[i] in companyies:
						contactes[values[0]][pids[i]] = companyies[int(values[i])]['nom']
				elif i == 2:
					append = ''
					if values[i] and values[i] != '':
						car = values[i].split(',')
						for c in car:
						  append += carrecs[int(c)] + ', '
					append = append[:-2]
					contactes[values[0]][pids[i]] = append
				else:
					contactes[values[0]][pids[i]] = values[i]
				
	except database.Error as e:
		print(f"Error retrieving entry from database: {e}")
	return contactes

def espectacles(data, categories, companyies, idiomes, generes):
	espectacles = {}
	pids = {
		1:'titol', 
		2:'companyia', 
		3:'espai', 
		4:'genere', 
		5:'idioma_espectacle', 
		6:'any', 
		7:'autor', 
		8:'direccio', 
		9:'num_interprets', 
		10:'mesures_espai_escenic', 
		11:'durada', 
		12:'video_embed', 
		13:'coreografia'
	}
	try:
		for values in data:
			for i in range(0,14):
				if i == 0:
					espectacles[values[0]] = {}
					espectacles[values[0]]['reference'] = 'https://www.llull.cat/monografics/performingarts/catala/espectacle.cfm?id=' + str(values[0])
				elif i == 2:
					if int(values[i]) in companyies:
						espectacles[values[0]][pids[i]] = companyies[int(values[i])]['nom']
					else:
						espectacles[values[0]][pids[i]] = ''
				elif i == 3:
					append = ''
					if values[i] and values[i] != '':
						espais = values[i].split(',')
						for es in espais:
							if int(es) in categories:
								append += categories[int(es)] + ', '
						append = append[:-2]
					espectacles[values[0]][pids[i]] = append
				elif i == 4:
					append = ''
					if values[i] and values[i] != '':
						genere = values[i].split(',')
						for g in genere:
							if int(g) in generes:
								append += generes[int(g)] + ', '
						append = append[:-2]
					espectacles[values[0]][pids[i]] = append
				elif i == 5:
					append = ''
					if values[i] and values[i] != '':
						idioma = values[i].split(',')
						for d in idioma:
							if int(d) in idiomes:
								append += idiomes[int(d)] + ', '
						append = append[:-2]
					espectacles[values[0]][pids[i]] = append
				else:
					espectacles[values[0]][pids[i]] = values[i]
	except database.Error as e:
		print(f"Error retrieving entry from database: {e}")
	return espectacles

def festivals(data, generes):
	festivals = {}
	pids = {
		1:'nom',
		2:'descr', 
		3:'dates', 
		4:'ubicacio', 
		5:'categoria', 
		6:'web'
	}
	try:
		for values in data:
			for i in range(0,7):
				if i == 0:
					festivals[values[0]] = {}
					festivals[values[0]]['reference'] = 'https://www.llull.cat/monografics/performingarts/catala/index.cfm'
				elif i == 5:
					append = ''
					if values[i] and values[i] != '':
						cat = values[i].split(',')
						for c in cat:
							append += generes[int(c)] + ', '
						append = append[:-2]
					festivals[values[0]][pids[i]] = append
				else:
					festivals[values[0]][pids[i]] = values[i]
	except database.Error as e:
		print(f"Error retrieving entry from database: {e}")
	return festivals

def generes(data):
	categories = {}
	pids = {
		1:'nom'
	}
	try:
		for values in data:
			categories[values[0]] = values[1]
			categories[values[0]]['reference'] = 'https://www.llull.cat/monografics/performingarts/catala/index.cfm'

	except database.Error as e:
		print(f"Error retrieving entry from database: {e}")
	return categories

def idiomes(data):
	categories = {}
	pids = {
		1:'nom'
	}
	try:
		for values in data:
			categories[values[0]] = values[1]
			categories[values[0]]['reference'] = 'https://www.llull.cat/monografics/performingarts/catala/index.cfm'

	except database.Error as e:
		print(f"Error retrieving entry from database: {e}")
	return categories

