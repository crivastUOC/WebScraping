# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 09:39:57 2019

@author: crivas
"""

# Parseja els arguments de entrada

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--Ruta", help="Entrar ruta")
args = parser.parse_args()

#Obté la ruta i nom del fitxer del dataset desitjat
ruta = args.Ruta

#Si no hi ha parametres assigna una ruta i nom del fitxer per defecte
if ruta == None :
    ruta = "D:\Practica1.csv"

#Assigna les urls de les pagines de les que fer scraping
str1 = "http://www.finanzas.com/ibex-35/datos-historicos.html"
str2 = "http://www.finanzas.com/divisas/eur-usd/datos-historicos.html"
str3 = "http://www.finanzas.com/euro-stoxx50/datos-historicos.html"
str4 = "http://www.finanzas.com/dow-jones/datos-historicos.html"
        
import requests
from bs4 import BeautifulSoup
import csv

#Funcio per registrar la fila de capçalera (comuna a totes les urls)
def FinanzasScraperHead (url, ruta):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, features="html.parser")
    ethead = soup.thead

    with open(ruta, 'w', newline='') as csvfile:
        spa = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        lhead = ["Tipo"]	
    
        for eth in ethead.find_all ('th'):
            lhead.append (eth.string)
        spa.writerow(lhead)

#Funcio per registrar les dades d'una url
def FinanzasScraperRow (url, ruta):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, features="html.parser")
    etbody = soup.tbody

    tipus = url.split ('/')[-2]

    with open(ruta, 'a', newline='') as csvfile:
        spa = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)

        for etr in etbody.find_all ('tr'):
            lrow = [tipus]
            for etb in etr.find_all ('td'):
                lrow.append (etb.string)
            spa.writerow(lrow)


#Crida a les funcions amb els parametres adequats 
FinanzasScraperHead (str1, ruta)
FinanzasScraperRow (str1, ruta)
FinanzasScraperRow (str2, ruta)
FinanzasScraperRow (str3, ruta)
FinanzasScraperRow (str4, ruta)

#Generacio de gràfiques
import pandas as pd
import numpy as np
import datetime
import pygal
#import cairosvg

#Llegir fitxer csv
df = pd.read_csv(ruta, delimiter=';', decimal=",", thousands=".", encoding='latin-1')

#Transformació variable fecha a tipus datetime
df["Fecha"] = pd.to_datetime(df["Fecha"])

#Transformació variable Volumen(m) a numeric, per fer-ho, s'eliminen els punts i es substitueixen "--" per 0.
df["Volumen(m)"] = [(x.replace('.','')) for x in df["Volumen(m)"]]
df["Volumen(m)"] = [(x.replace('--','0')) for x in df["Volumen(m)"]]
df["Volumen(m)"] = pd.to_numeric(df["Volumen(m)"])

#S'ordena el dataframe per data
df = df.sort_values(["Fecha"],ascending="true")

#Es creen quatre dataframes, un per a cada cotització
ibex = df[df['Tipo'] == "ibex-35"]
eurusd = df[df['Tipo'] == "eur-usd"]
eurs50 = df[df['Tipo'] == "euro-stoxx50"]
dowjones  = df[df['Tipo'] == "dow-jones"]

# Es crea una nova columna en aquests dataframes amb el % de la diferencia acumulada per a cada data.
ibex["Dif_acumulada"] = ibex["Dif.%"].cumsum()
eurusd["Dif_acumulada"] = eurusd["Dif.%"].cumsum()
eurs50["Dif_acumulada"] = eurs50["Dif.%"].cumsum()
dowjones["Dif_acumulada"] = dowjones["Dif.%"].cumsum()

from matplotlib import pylab, mlab, pyplot
plt = pyplot

# Es configura la mida de la figura
plt.figure(figsize = (10, 10))

# Es dibuixa cada una de les curves en un color diferent
plt.plot(ibex["Fecha"],ibex["Dif_acumulada"], color="blue", linewidth=1.5, linestyle="-", label="ibex")
plt.plot(eurusd["Fecha"],eurusd["Dif_acumulada"], color="red", linewidth=1.5, linestyle="-", label="eur-usd")
plt.plot(eurs50["Fecha"],eurs50["Dif_acumulada"], color="green", linewidth=1.5, linestyle="-", label="euro-stoxx50")
plt.plot(dowjones["Fecha"],dowjones["Dif_acumulada"], color="orange", linewidth=1.5, linestyle="-", label="dow-jones")

# S'inclou la llegenda i els titols
plt.legend(loc="best")
plt.ylabel("% de Diferencia")
plt.title("Cotitzacions")

# Es mostra el gràfic
plt.show()

# Es crea un index en el dataframe original amb la data
df.index = df['Fecha']

# Es creen 4 dataframe per a cada tipus de cotització
ibex = df[df['Tipo'] == "ibex-35"]
eurusd = df[df['Tipo'] == "eur-usd"]
eurs50 = df[df['Tipo'] == "euro-stoxx50"]
dowjones  = df[df['Tipo'] == "dow-jones"]

# Per a cadascun dels dataframes, s'agrupen els diferents resultats quadrimestralment
ibex = ibex.resample('Q').sum()
eurusd = eurusd.resample('Q').sum()
dowjones = dowjones.resample('Q').sum()
eurs50 = eurs50.resample('Q').sum()
fec = ibex.index

# Es crea el gràfic de barres apilat quatrimestral que mostra el total de volum de cadascuna de les cotitzacions
line_chart = pygal.StackedBar()
line_chart.title = 'Volum (m)'
line_chart.x_labels = fec
line_chart.add('ibex-35', ibex["Volumen(m)"])
line_chart.add('eur-usd', eurusd["Volumen(m)"])
line_chart.add('euro-stoxx50', eurs50["Volumen(m)"])
line_chart.add('dow-jones',dowjones["Volumen(m)"])

