import os
import mysql.connector as database
import numpy as np
import pywikibot
import json
import csv
import pandas as pd
import glob

def main():
	#PERSONES
	persones = {}
	line_count = 0
	csv_files = ['./dades_cantic/cantic_20230311_1_100.csv', './dades_cantic/cantic_20230311_2_100.csv']
	for f in csv_files:
		with open(f, mode='r') as csv_file:
			csv_reader = csv.reader(csv_file, delimiter = '\t')
			for row in csv_reader:
				#data = row.split('\t')
				if line_count != 0:
					persones[line_count] = {}
					persones[line_count]['nom'] = row[0]
					persones[line_count]['dates'] = row[1]
					persones[line_count]['titol'] = row[2]
					persones[line_count]['url_viaf'] = row[3]
					persones[line_count]['cantic'] = row[4]
					#['Autor', 'Dates', 'Títol', 'URL VIAF', 'ID CANTIC']
				line_count += 1
	print(persones[1])
	with open("./dades/cantic_persones.txt", "w") as fp:
	    json.dump(persones, fp)


	#ENTITATS
	entitats = {}
	line_count = 0
	csv_files = ['./dades_cantic/cantic_20230311_1_110.csv', './dades_cantic/cantic_20230311_2_110.csv']
	for f in csv_files:
		with open(f, mode='r') as csv_file:
			csv_reader = csv.reader(csv_file, delimiter = '\t')
			for row in csv_reader:
				#data = row.split('\t')
				if line_count != 0:
					entitats[line_count] = {}
					entitats[line_count]['nom'] = row[0]
					entitats[line_count]['titol'] = row[1]
					entitats[line_count]['url_viaf'] = row[2]
					entitats[line_count]['cantic'] = row[3]
					#Entitat	Títol	URL VIAF	ID CANTIC
				line_count += 1
	print(entitats[1])
	with open("./dades/cantic_entitats.txt", "w") as fp:
	    json.dump(entitats, fp)

	#CONGRESSOS
	congressos = {}
	line_count = 0
	csv_files = ['./dades_cantic/cantic_20230311_1_111.csv', './dades_cantic/cantic_20230311_2_111.csv']
	for f in csv_files:
		with open(f, mode='r') as csv_file:
			csv_reader = csv.reader(csv_file, delimiter = '\t')
			for row in csv_reader:
				if line_count != 0:
					congressos[line_count] = {}
					congressos[line_count]['nom'] = row[0]
					congressos[line_count]['titol'] = row[1]
					congressos[line_count]['url_viaf'] = row[2]
					congressos[line_count]['cantic'] = row[3]
					#Congrés	Títol	URL VIAF	ID CANTIC
				line_count += 1
	print(congressos[1])
	with open("./dades/cantic_congressos.txt", "w") as fp:
	    json.dump(congressos, fp)

	#OBRES
	obres = {}
	line_count = 0
	csv_files = ['./dades_cantic/cantic_20230311_1_130.csv', './dades_cantic/cantic_20230311_2_130.csv']
	for f in csv_files:
		with open(f, mode='r') as csv_file:
			csv_reader = csv.reader(csv_file, delimiter = '\t')
			for row in csv_reader:
				if line_count != 0:
					obres[line_count] = {}
					obres[line_count]['titol'] = row[0]
					obres[line_count]['url_viaf'] = row[1]
					obres[line_count]['cantic'] = row[2]
					#Títol	URL VIAF	ID CANTIC
				line_count += 1
	print(obres[1])
	with open("./dades/cantic_obres.txt", "w") as fp:
	    json.dump(obres, fp)

	#GEOGRAFICS
	geografics = {}
	line_count = 0
	csv_files = ['./dades_cantic/cantic_20230311_1_151.csv', './dades_cantic/cantic_20230311_2_151.csv']
	for f in csv_files:
		with open(f, mode='r') as csv_file:
			csv_reader = csv.reader(csv_file, delimiter = '\t')
			for row in csv_reader:
				if line_count != 0:
					geografics[line_count] = {}
					geografics[line_count]['titol'] = row[0]
					geografics[line_count]['url_viaf'] = row[1]
					geografics[line_count]['cantic'] = row[2]
					#Títol	URL VIAF	ID CANTIC
				line_count += 1
	print(geografics[1])
	with open("./dades/cantic_geografics.txt", "w") as fp:
	    json.dump(geografics, fp)

main()
