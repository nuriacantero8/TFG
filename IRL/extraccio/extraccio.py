import os
import mysql.connector as database
import numpy as np
import llullmusica
import catarts
import llulltrac
import arxiuartdb
import pywikibot
import json
import csv

def save_nodict(file, data):
    header = ['nom']
    with open(file, "w") as fp:
        #json.dump(editorials, fp)
        writer = csv.writer(fp, delimiter = '\t')
        writer.writerow(['name'])
        for key in data.keys():
            writer.writerow(data[key])

def save(file, data):
    keys = list(data.keys())
    header = list(data[keys[0]].keys())
    with open(file, "w") as fp:
        #json.dump(editorials, fp)
        writer = csv.DictWriter(fp, fieldnames=header, delimiter = '\t')
        writer.writeheader()
        for key in keys:
            writer.writerow(data[key])

username = 'root'
password = '2701'

connection = database.connect(
    user=username,
    password=password,
    host="localhost",
    database="llull_musica")
cursor = connection.cursor()

statement = "SELECT distinct registro, nom, replace(replace(adresa, '\r', ''), '\n', ', ') as adresa, case when telf like '%/%' then substring(telf, 1, instr(telf, ' /')-1) else telf end, fax, email, web FROM editorials WHERE idioma = 1"
cursor.execute(statement)
editorials = llullmusica.editorials(cursor)
save("./dades/llullmusica_editorials.txt", editorials)

statement = "SELECT DISTINCT b.registro, titol, editorial, lloc_edicio, autor_llibre, any_edicio,concat(nom,' ',cognoms) from bibliografia b inner join biografies f on b.autor = f.registro where b.idioma = 1;"
cursor.execute(statement)
bibliografies = llullmusica.bibliografia(cursor)
save("./dades/llullmusica_bibliografies.txt", bibliografies)

statement = "SELECT DISTINCT registro, nom from categories where idioma = 1"
cursor.execute(statement)
categories = llullmusica.categories(cursor)

file = "./dades/llullmusica_categories.txt"
save_nodict("./dades/llullmusica_categories.txt", categories)


statement = "SELECT DISTINCT d.registro, titol, discografica, referencia, any_edicio, concat(nom, ' ', cognoms) from discografia d inner join biografies b on d.autor = b.registro where d.idioma = 1;"
cursor.execute(statement)
discografiques = llullmusica.discografica(cursor)
save("./dades/llullmusica_discografiques.txt", discografiques)

statement = "SELECT DISTINCT registro, nom, disc_titol, email, disc_discografica, web, facebook, twitter, myspace, youtube, spotify, management, disc_any, telf, fax, skype, categoria, cloud_tags, nom_discografica, web_discografica from musics where idioma = 1;"
cursor.execute(statement)
musics = llullmusica.musics(cursor, categories)
save("./dades/llullmusica_musics.txt", musics)

statement = "SELECT DISTINCT registro, nom, cognoms, email, lloc_naixement, web, facebook, twitter, myspace, youtube, linkedin, cataleg, any_naixement, editorials, altres from biografies where idioma = 1;"
cursor.execute(statement)
biografies = llullmusica.biografies(cursor, editorials)
save("./dades/llullmusica_biografies.txt", biografies)

connection.close()


connection = database.connect(
    user=username,
    password=password,
    host="localhost",
    database="catarts")

cursor = connection.cursor()

statement = "SELECT DISTINCT registro_id, nom from CATEGORIES where idioma = 1"
cursor.execute(statement)
categories = catarts.categories(cursor)
save_nodict("./dades/catarts_categories.txt", categories)

statement = "SELECT DISTINCT registro_id, descr, nom, web, facebook, twitter, myspace from COMPANYIES where idioma = 2;"
cursor.execute(statement)
companyies = catarts.companyies(cursor)
save("./dades/catarts_companyies.txt", companyies)

statement = "SELECT DISTINCT registro_id, companyia, carrec, nom, adresa, cp, localitat, tels, email, facebook, twitter, myspace, altres, web from CONTACTES where idioma = 1;"
cursor.execute(statement)
contactes = catarts.contactes(cursor, companyies, categories)
save("./dades/catarts_contactes.txt", contactes)

statement = "SELECT DISTINCT registro_id, nom from GENERES where idioma = 1;"
cursor.execute(statement)
generes = catarts.categories(cursor)
save_nodict("./dades/catarts_generes.txt", generes)

statement = "SELECT DISTINCT registro_id, idioma_espectacle from IDIOMES where idioma = 1;"
cursor.execute(statement)
idiomes = catarts.categories(cursor)
save_nodict("./dades/catarts_idiomes.txt", idiomes)

statement = "SELECT DISTINCT registro_id, nom, descr, dates, ubicacio, categoria, web from FESTIVALS where idioma = 2;"
cursor.execute(statement)
festivals = catarts.festivals(cursor, generes)
save("./dades/catarts_festivals.txt", festivals)

statement = "SELECT DISTINCT registro_id, titol, companyia, espai, genere, idioma_espectacle, any, autor, direccio, num_interprets, mesures_espai_escenic, durada, video_embed, coreografia from ESPECTACLES where idioma = 1;"
cursor.execute(statement)
espectacles = catarts.espectacles(cursor, categories, companyies, idiomes, generes)
save("./dades/catarts_espectacles.txt", espectacles)

connection.close()


connection = database.connect(
    user=username,
    password=password,
    host="localhost",
    database="llulltrac")
cursor = connection.cursor()

statement = "SELECT DISTINCT registro_id, titol from CATEGORIES where idioma = 1;"
cursor.execute(statement)
categories = llulltrac.categories(cursor)
save_nodict("./dades/llulltrac_categories.txt", categories)

statement = "SELECT DISTINCT registro_id, nom, mail, empresa, link from contactes;"
cursor.execute(statement)
contactes = llulltrac.contactes(cursor)
save("./dades/llulltrac_contactes.txt", contactes)

statement = "SELECT DISTINCT registro_id, nom from editorials;"
cursor.execute(statement)
editorials = llulltrac.editorials(cursor)
save("./dades/llulltrac_editorials.txt", editorials)

statement = "SELECT * from funcions;"
cursor.execute(statement)
funcions = llulltrac.categories(cursor)
save_nodict("./dades/llulltrac_funcions.txt", funcions)


statement = "SELECT DISTINCT registro_id, llengua from idiomes where idioma = 1;"
cursor.execute(statement)
idiomes = llulltrac.categories(cursor)
save_nodict("./dades/llulltrac_idiomes.txt", idiomes)


statement = "SELECT DISTINCT registro_id, titol, any_, link_quad from quad_premis;"
cursor.execute(statement)
quad_premis = llulltrac.quad_premis(cursor)
save("./dades/llulltrac_quad_premis.txt", quad_premis)


statement = "SELECT DISTINCT registro_id, titol, titol_original, subtitol, lloc_edicio, isbn, any_edicio, editorial, genere, llengua, categoria from DOCUMENTS;"
cursor.execute(statement)
documents = llulltrac.documents(cursor, editorials, categories, idiomes)
save("./dades/llulltrac_documents.txt", documents)


statement = "SELECT DISTINCT registro_id, titol_cat, titol_eng, format_, any_, pagines, editorial, contactes, quadernet, genere from LLIBRES;"
cursor.execute(statement)
llibres = llulltrac.llibres(cursor, editorials, categories, contactes, quad_premis)
save("./dades/llulltrac_llibres.txt", llibres)


statement = "SELECT DISTINCT registro_id, nom_complert, replace(especialitat,'+',''), replace(llengua,'+',''), replace(id_trad,'+','') from traductors order by id_trad;"
cursor.execute(statement)
traductors = llulltrac.traductors(cursor, idiomes, categories)
save("./dades/llulltrac_traductors.txt", traductors)


connection.close()


connection = database.connect(
    user=username,
    password=password,
    host="localhost",
    database="arxiuartdb")
cursor = connection.cursor()

statement = "SELECT DISTINCT id, nom, lloc_naixement,any_naixement, residencia, web, email, telf, adresa, poblacio, cp from artistes;"
cursor.execute(statement)
artistes = arxiuartdb.artistes(cursor)

statement = "SELECT DISTINCT id, artista, titol, any_, link, mides from obres;"
cursor.execute(statement)
obres = arxiuartdb.obres(cursor, artistes)
save("./dades/arxiuartdb_obres.txt", obres)

statement = "SELECT * from categories;"
cursor.execute(statement)
categories = arxiuartdb.categories(cursor)
save_nodict("./dades/arxiuartdb_categories.txt", categories)

statement = "SELECT * from tecniques;"
cursor.execute(statement)
tecniques = arxiuartdb.categories(cursor)
save_nodict("./dades/arxiuartdb_tecniques.txt", tecniques)

statement = "SELECT * from relacions;"
cursor.execute(statement)
artistes = arxiuartdb.relacions(cursor, artistes, categories)
save("./dades/arxiuartdb_artistes.txt", artistes)

connection.close()


