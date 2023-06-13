# Agregador Cultural d'Artistes Catalans
L'Institut Ramon Llull és una organització pública que té com a principal objectiu donar a conèixer la cultura catalana. És per això que aquest projecte s'adequa a la perfecció amb la feina que realitza a diari l'Institut. A més, l'IRL emmagatzema dades de tots aquells artistes que en algun moment de la història de l'Institut, han demanat subvencions i ajuts per a projectes personals que tenen connexió amb la llengua i cultura catalana. És d'aquí d'on surten les dades que s'utilitzaran més endavant en el projecte.

A banda d'això, l'Institut Ramon Llull també té connexió amb altres entitats i organitzacions que emmagatzemen dades culturals catalanes. Al realitzar el treball amb l'IRL, permet agrupar una major quantitat de dades que les pròpies de l'organització, ja que altres fonts de dades cedeixen les seves dades a l'Institut per a un projecte d'aquesta magnitud.

El codi que hi ha en aquest repositori es pot copiar, però no es podrà replicar el projecte, ja que les dades utilitzades són propietat de l'Institut Ramon Llull (IRL) i del Catàleg d'Autoritats de Noms i Títols de Catalunya (CANTIC).

## Requeriments
Es necessita Python, així com les llibreries següents:
* pywikibot
* datetime
* fuzzywuzzy
* json
* pandas
* altair
* mysql

També es necessita OpenRefine per a poder executar els fitxers tar.gz relacionat amb el projecte.

Per últim, alguna eina semblant a Google Colaboratory és necessària per a poder recrear els gràfics de l'anàlisi de dades.

## Estructura
Les carpetes anomenades IRL i cantic són les que contenen el codi del procés ETL per al mètode en què s'utilitza Python.

La carpeta grafics conté un Jupyter Notebook amb el codi per la creació dels gràfics de la memòria.

Per últim, la carpeta OpenRefine conté mostres dels diferents conjunts de dades que s'han utilitzat, així com el procés realitzat per fer la conciliació amb Wikidata.
