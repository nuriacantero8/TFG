import os
import mysql.connector as database
import numpy as np
import re

def editorials(data):
  editorials = {}
  pids = {
    1:"nom",
    2:"adresa",
    3:"telf",
    4:"fax",
    5:"email",
    6:"web"
  }
  try:
    for values in data:
      for i in range(0,7):
        if i == 3:
          telf = values[i].split(' / ')
          editorials[values[0]][pids[i]] = telf[0]
        elif i == 2:
          adresa = values[i].split(', ')
          if adresa[-1] == '':
              adresa = adresa[:-1]
          if len(adresa) > 1:
              if adresa[-1] == 'USA':
                  #print('USA')
                  adresa[-2] = adresa[-3]
          
              country = adresa[-1]
              city = adresa[-2]
              city = city.split(' ')
              if re.search(r'\d', city[0]):
                  city = city[1]
              else:
                  if len(city) > 1 and not re.search(r'\d', city[1]):
                      city = city[0] + ' ' + city[1]
                  else:
                      city = city[0]
          editorials[values[0]]['ciutat'] = city
          editorials[values[0]]['pais'] = country
        elif i == 0:
          editorials[values[0]] = {}
          editorials[values[0]]['reference'] = 'https://www.llull.cat/monografics/newcatalanmusic/catala/search.cfm'
        else:
          editorials[values[0]][pids[i]] = values[i]
    #print(f"{editorials[3025]}")
  except database.Error as e:
    print(f"Error retrieving entry from database: {e}")
  return editorials

def bibliografia(data):
  llibres = {}
  pids = {
    1:"titol",
    2:"editorial",
    3:"lloc_edicio",
    4:"autor_llibre",
    5:"any_edicio",
    6:"music"
  }
  try:
    for values in data:
      for i in range(0,7):
        if i == 0:
          llibres[values[0]] = {}
          llibres[values[0]]['reference'] = 'https://www.llull.cat/monografics/newcatalanmusic/catala/search.cfm'
        else:
          llibres[values[0]][pids[i]] = values[i]
    #print(f"{llibres[5]}")
  except database.Error as e:
    print(f"Error retrieving entry from database: {e}")
  return llibres

def categories(data):
  categories = {}
  pids = {1:"nom"}
  try:
    for values in data:
      categories[values[0]] = values[1]
    #print(categories[3028])
  except database.Error as e:
    print(f"Error retrieving entry from database: {e}")
  return categories 

def discografica(data):
  disc = {}
  pids = {
    1:'titol',
    2:'discografica',
    3:'referencia',
    4:'any_edicio',
    5:'autor'
  } 
  try:
    for values in data:
      for i in range(0,6):
        if i == 0:
          disc[values[0]] = {}
          disc[values[0]]['reference'] = 'https://www.llull.cat/monografics/newcatalanmusic/catala/search.cfm'
        else:
          disc[values[0]][pids[i]] = values[i]
    #print(f"{disc[3]}")
  except database.Error as e:
    print(f"Error retrieving entry from database: {e}")
  return disc 

def musics(data, categories):
  musics = {}
  pids = {
  1:'nom',
  2:'disc_titol',
  3:'email',
  4:'disc_discografica',
  5:'web',
  6:'facebook',
  7:'twitter',
  8:'myspace', 
  9:'youtube', 
  10:'spotify', 
  11:'management', 
  12:'disc_any', 
  13:'telf', 
  14:'fax', 
  15:'skype', 
  16:'categoria',
  18:'nom_discografica', 
  19:'web_discografica'}
  try:
    for values in data:
      append = ''
      for i in range(0,20):
        if i == 0:
          musics[values[i]] = {}
          musics[values[0]]['reference'] = 'https://www.llull.cat/monografics/catalansounds/catalan_sounds.cfm'
        elif i == 16 or i == 17:
          if values[i]:
            cat = values[i].split(',')
            for c in cat:
              append += categories[int(c)] + ', '
          if i == 17:
            append = append[:-2]
            musics[values[0]][pids[i-1]] = append
        else:
          musics[values[0]][pids[i]] = values[i]
    #print(musics[3109])
  except database.Error as e:
    print(f"Error retrieving entry from database: {e}")
  return musics

def biografies(data, editorials):
  biografies = {}
  pids = {
    1:'nom',
    2:'cognoms', 
    3:'email', 
    4:'lloc_naixement', 
    5:'web', 
    6:'facebook', 
    7:'twitter', 
    8:'myspace', 
    9:'youtube', 
    10:'linkedin', 
    11:'cataleg', 
    12:'any_naixement', 
    13:'editorials', 
    14:'altres'
  }
  try:
    for values in data:
      for i in range (0,15):
        if i == 0:
          biografies[values[i]] = {}
          biografies[values[0]]['reference'] = 'https://www.llull.cat/monografics/newcatalanmusic/catala/bio.cfm?id='+str(values[0])
        elif i == 13:
          append = ''
          if values[i]:
            edit = values[i].split(',')
            for e in edit:
              append += editorials[int(e)]['nom'] + ', '
            append = append[:-2]
          biografies[values[0]][pids[i]] = append
        else:
          biografies[values[0]][pids[i]] = values[i]
    #print(biografies[3002]['editorials'])
  except database.Error as e:
    print(f"Error retrieving entry from database: {e}")
  return biografies

