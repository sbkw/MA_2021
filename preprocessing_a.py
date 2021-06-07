#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import sys
import matplotlib.dates as dt
import pandas as pd
from datetime import datetime
import numpy as np

"""Vorbereiten der CSV-Dateien für die weitere Analyse. Präambel wird von den Teilnehmerdaten getrennt und anschließend werden die Teilnehmerdaten 
in einer neues CSV-Datei gespeichert"""

""" Setting Pandas Options"""
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

def pfad():
    """ Überprüfung, ob Pfade angelegt wurden. Falls nicht, dann werden diese angelegt"""

    directory = input("Enter the path where the results will be stored: ")
    if not os.path.exists(directory):
        os.makedirs(directory)

    #  Neuen Pfad anlegen, indem Ergebnisse gespeichert werden
    new_path_pdf = os.path.join(directory, r'Results_PDF')
    new_path_html = os.path.join(directory, r'Results_HTML')
    new_path_mod = os.path.join(directory, r'CSV_mod')
    new_path_csv = os.path.join(directory, r'Results_CSV')
    #  new_path_png = 'Results/PNG'
    access_rights = 0o755  # readable & accessible from all users, writeable by owner only
    try:
        os.mkdir(new_path_pdf, access_rights)
        os.mkdir(new_path_html, access_rights)
        os.mkdir(new_path_mod, access_rights)
        os.mkdir(new_path_csv, access_rights)
        #  os.mkdir(new_path_png, access_rights)

    except FileExistsError:
        #  print("Directory ", new_path_png, " already exists")
        print("Directory ", new_path_pdf, " already exists")
        print("Directory ", new_path_html, " already exists")
        print("Directory ", new_path_mod, " already exists")
        print("Directory ", new_path_csv, " already exists")
    else:
        print("Successfully created folders: Results_PDF, Results_HTML, CSV_mod, Results_CSV")

def fileoperations():
    #  CSV einlesen vom 1. argument bei Skriptaufruf
    first_arg = sys.argv[1]

    df_comma = pd.read_csv(first_arg, nrows=1, sep=",")
    df_semi = pd.read_csv(first_arg, nrows=1, sep=";")
    if df_comma.shape[1] > df_semi.shape[1]:
        print("comma delimited")
    else:
        print("semicolon delimited")

    df = pd.read_csv(first_arg, sep=';', skiprows=[9], encoding='ISO-8859-15', engine='python', error_bad_lines=False)

    global file_name
    global file_name_we # with extension
    file_name = os.path.basename(first_arg)
    file_name_we = os.path.splitext(first_arg)[0]

    """Telefonica"""
    if len(df[df['Verpflichteter'] == 'Telefonica']):
        header1 = df.iloc[10:]  # Alle Spalten ab Zeile 11
        header1.to_csv('CSV_mod/FZ_Telefonica_mod.csv', header=False, index=False)
        tf_mod = pd.read_csv('CSV_mod/FZ_Telefonica_mod.csv')
        tf_mod = tf_mod.loc[:, ["Record-Nummer", "Start", 'Ende', 'Dauer', 'Dienst', 'A-Nummer', 'A-Länge', 'A-Breite','A-Richtung']]  # Wahl der Spalten ab Zeile 11

        # Zeitspalten
        tf_mod['Datum'] = pd.to_datetime(tf_mod['Start'], errors='coerce').dt.date
        tf_mod['Start'] = pd.to_datetime(tf_mod['Start'], errors='coerce').dt.time
        tf_mod['Ende'] = pd.to_datetime(tf_mod['Ende'], errors='coerce').dt.time


        # Hinzufügen Providerspalte & Ordnen der Spalten
        tf_mod['Provider'] = 'Telefonica'
        cols = tf_mod.columns.tolist()
        cols = cols[-1:] + cols[:-1]  # neue spalte nach vorne setzen
        tf_mod = tf_mod[cols]  # DataFrame neu ordnen

        # Entfernen der Richtungsbuchstaben aus den Koordinaten
        tf_mod['A-Länge'] = tf_mod['A-Länge'].str[3:]
        tf_mod['A-Breite'] = tf_mod['A-Breite'].str[1:]
        tf_mod['A-Länge'] = pd.to_numeric(tf_mod['A-Länge'], errors='coerce')
        tf_mod['A-Breite'] = pd.to_numeric(tf_mod['A-Breite'], errors='coerce')
        tf_mod['A-Länge'] = tf_mod['A-Länge'].fillna(np.nan)
        tf_mod['A-Breite'] = tf_mod['A-Breite'].fillna(np.nan)

        tf_mod = tf_mod.dropna(axis=0, subset=['A-Länge'])

        # Hinzufügen der Funkmasten und Funkzellennamesspalte
        tf_mod['Funkzelle'] = tf_mod['A-Länge'].map(str) + ' ' + tf_mod['A-Breite'].map(str) + \
                              ' - ' + tf_mod['A-Richtung'].map(str)
        tf_mod['Funkmast'] = tf_mod['A-Länge'].map(str) + ' ' + tf_mod['A-Breite'].map(str)


        # Datentypen ändern
        tf_mod['Dauer'] = tf_mod['Dauer'].astype(float)  # for a column that contains numeric values stored as strings

        tf_mod.to_csv('CSV_mod/Mod_Relevant_%s.csv' % file_name_we, index=False)
        #return tf_mod

    """Telekom"""
    if len(df[df['Verpflichteter'] == 'Deutsche Telekom AG']):
        header2 = df.iloc[10:]
        header2.to_csv('CSV_mod/FZ_Telekom_mod.csv', header=False, index=False)
        te_mod = pd.read_csv('CSV_mod/FZ_Telekom_mod.csv')
        te_mod = te_mod.loc[:, ["Record-Nummer", "Start", 'Ende', 'Dauer', 'Dienst', 'A-Nummer', 'A-Länge', 'A-Breite', 'A-Richtung']]

        # Zeitspalten
        te_mod['Datum'] = pd.to_datetime(te_mod['Start'], errors='coerce').dt.date
        te_mod['Start'] = pd.to_datetime(te_mod['Start'], errors='coerce').dt.time
        te_mod['Ende'] = pd.to_datetime(te_mod['Ende'], errors='coerce').dt.time


        # Hinzufügen Providerspalte & Ordnen der Spalten
        te_mod['Provider'] = 'Deutsche Telekom AG'
        cols = te_mod.columns.tolist()
        cols = cols[-1:] + cols[:-1]  # neue spalte nach vorne setzen
        te_mod = te_mod[cols]  # DataFrame neu ordnen

        # Entfernen der Richtungsbuchstaben aus den Koordinaten
        te_mod['A-Länge'] = te_mod['A-Länge'].str[3:]
        te_mod['A-Breite'] = te_mod['A-Breite'].str[1:]
        te_mod['A-Länge'] = pd.to_numeric(te_mod['A-Länge'], errors='coerce')
        te_mod['A-Breite'] = pd.to_numeric(te_mod['A-Breite'], errors='coerce')
        te_mod['A-Länge'] = te_mod['A-Länge'].fillna(np.nan)
        te_mod['A-Breite'] = te_mod['A-Breite'].fillna(np.nan)


        te_mod = te_mod.dropna(axis=0, subset=['A-Länge'])

        # Hinzufügen der Funkzellenspalte
        te_mod['Funkzelle'] = te_mod['A-Länge'].map(str) + ' ' + te_mod['A-Breite'].map(str) + \
                              ' - ' + te_mod['A-Richtung'].map(str)
        te_mod['Funkmast'] = te_mod['A-Länge'].map(str) + ' ' + te_mod['A-Breite'].map(str)


        # Datentyp ändern
        te_mod['Dauer'] = te_mod['Dauer'].astype(float)

        te_mod.to_csv('CSV_mod/Mod_Relevant_%s.csv' % file_name_we, index=False)

        #return te_mod

    """Vodafone"""
    if len(df[df['Verpflichteter'] == 'Vodafone']):
        header3 = df.iloc[10:]
        header3.to_csv('CSV_mod/FZ_Vodafone_mod.csv', header=False, index=False)
        vd_mod = pd.read_csv('CSV_mod/FZ_Vodafone_mod.csv')
        vd_mod = vd_mod.loc[:,["Record-Nummer", "Start", 'Ende', 'Dauer', 'Dienst', 'A-Nummer', 'A-Länge', 'A-Breite', 'A-Richtung']]

        # Zeitspalten
        vd_mod['Datum'] = pd.to_datetime(vd_mod['Start'], errors='coerce').dt.date
        vd_mod['Start'] = pd.to_datetime(vd_mod['Start'], errors='coerce').dt.time
        vd_mod['Ende'] = pd.to_datetime(vd_mod['Ende'], errors='coerce').dt.time


        # Hinzufügen Providerspalte & Ordnen der Spalten
        vd_mod['Provider'] = 'Vodafone'
        cols = vd_mod.columns.tolist()
        cols = cols[-1:] + cols[:-1]  # neue spalte nach vorne setzen
        vd_mod = vd_mod[cols]  # DataFrame neu ordnen

        # Entfernen der Richtungsbuchstaben aus den Koordinaten
        vd_mod['A-Länge'] = vd_mod['A-Länge'].str[3:]
        vd_mod['A-Breite'] = vd_mod['A-Breite'].str[1:]
        vd_mod['A-Länge'] = pd.to_numeric(vd_mod['A-Länge'], errors='coerce') # umwandeln in numerisches format
        vd_mod['A-Breite'] = pd.to_numeric(vd_mod['A-Breite'], errors='coerce')
        vd_mod['A-Länge'] = vd_mod['A-Länge'].fillna(np.nan) # füllen mit numpy-nans
        vd_mod['A-Breite'] = vd_mod['A-Breite'].fillna(np.nan)

        vd_mod = vd_mod.dropna(axis=0, subset=['A-Länge']) # löschen aller zeilen, die keinen wert im breitengrad haben

        # Hinzufügen der Funkzellenspalte
        vd_mod['Funkzelle'] = vd_mod['A-Länge'].map(str) + ' ' + vd_mod['A-Breite'].map(str) + \
                              ' - ' + vd_mod['A-Richtung'].map(str)
        vd_mod['Funkmast'] = vd_mod['A-Länge'].map(str) + ' ' + vd_mod['A-Breite'].map(str)


        # Datentyp ändern
        vd_mod['Dauer'] = vd_mod['Dauer'].astype(float)

        vd_mod.to_csv('CSV_mod/Mod_Relevant_%s.csv' % file_name_we, index=False)
        #return vd_mod

if __name__ == '__main__':
    pfad()
    fileoperations()
    sys.exit()
