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

def artistes(data):
	artistes={}
	pids = {
		1:'nom', 
		2:'lloc_naixement',
		3:'any_naixement', 
		4:'residencia', 
		5:'web', 
		6:'email', 
		7:'telf', 
		8:'adresa', 
		9:'poblacio', 
		10:'cp'
	}
	try:
		for values in data:
			for i in range(0,11):
				if i == 0:
					artistes[values[0]] = {}
					artistes[values[0]]['reference'] = 'http://aa.xtraz.net/ca/cerca'
				else:
					artistes[values[0]][pids[i]] = values[i]
	except database.Error as e:
		print(f"Error retrieving entry from database: {e}")
	return artistes

def obres(data, artistes):
	obres={}
	pids = {
		1:'artista', 
		2:'titol', 
		3:'any', 
		4:'link', 
		5:'mides'
	}
	try:
		for values in data:
			for i in range(0,6):
				if i == 0:
					obres[values[0]] = {}
					obres[values[0]]['reference'] = 'http://aa.xtraz.net/ca/cerca'
				elif i == 1:
					if values[i] and values[i] != '':
						if int(values[i]) in artistes:
							obres[values[0]][pids[i]] = artistes[int(values[i])]['nom']
				else:
					obres[values[0]][pids[i]] = values[i]
	except database.Error as e:
		print(f"Error retrieving entry from database: {e}")
	return obres

def relacions(data, artistes, categories):
	try:
		for values in data:
			if 'categoria' in artistes[int(values[0])]:
				artistes[int(values[0])]['categoria'].append(categories[int(values[1])])
			else:
				artistes[int(values[0])]['categoria'] = []
				artistes[int(values[0])]['categoria'].append(categories[int(values[1])])
	except database.Error as e:
		print(f"Error retrieving entry from database: {e}")
	return artistes

