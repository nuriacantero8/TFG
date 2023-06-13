import json
import pywikibot
import numpy as np
import os
from datetime import date
import re
import c_llullmusica
import c_catarts
import c_llulltrac
import c_arxiuartdb


with open("./dades/llullmusica_musics.txt", "r") as fp:
    musics = json.load(fp)
site = pywikibot.Site("wikidata", "wikidata")

for key in musics.keys():
    c_llullmusica_prod.musics(site, musics[key])
