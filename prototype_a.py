#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Prototyp für die Masterarbeit"""


import os, sys, glob, folium
import matplotlib.pyplot as plt
import matplotlib.dates as dt
import pandas as pd
from datetime import datetime


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

    access_rights = 0o755  # readable & accessible from all users, writeable by owner only
    try:
        os.mkdir(new_path_pdf, access_rights)
        os.mkdir(new_path_html, access_rights)
        os.mkdir(new_path_mod, access_rights)
        os.mkdir(new_path_csv, access_rights)
   
    except FileExistsError:
        #  print("Directory ", new_path_png, " already exists")
        print("Directory ", new_path_pdf, " already exists")
        print("Directory ", new_path_html, " already exists")
        print("Directory ", new_path_mod, " already exists")
        print("Directory ", new_path_csv, " already exists")
    else:
        print("Successfully created folders: Results_PDF, Results_HTML, CSV_mod, Results_CSV")


def mergeCSV():
    """ Zusammenfügen der CSV-Dateien in eine einzelne Datei inkl. Angabe der ursprünglichen Datei.
    Modifizierte Version von: https://blog.softhints.com/how-to-merge-multiple-csv-files-with-python/
    """
    cwd = os.getcwd()
    print("Current Working Direction: ", cwd)

    path = input("Enter the directory where the files are located: ")
    os.chdir(path)

    extension = 'csv'

    merged_df = pd.DataFrame()
    for f in sorted(glob.glob('*.{}'.format(extension))):
        df = pd.read_csv(f)
        df["file_source"] = f
        merged_df = merged_df.append(df)

    merged_filename = input("Enter the filename: ")
    os.chdir(cwd)
    merged_df.to_csv('Results_CSV/%s.csv' % merged_filename,
        index=False, encoding='utf-8-sig')


def uniqueCT():
    """ Erstellt jeweils eine CSV-Datei mit den einzigartigen Funkzellen für den weiteren Gebrauch in GIS-Programmen
    und eine CSV-Datei mit den einzigartigen Funkmasten für die geo_data Funktion"""

    #  CSV einlesen vom 1. Argument bei Skriptaufruf
    # first_arg = sys.argv[1]
    """ Funkzellen """
    path = input("Enter the directory where the file is located: ")
    df = pd.read_csv(path, sep=',')

    unique = df.Funkzelle.unique() # Ausgabe in Array
    unique.sort()
    unique = pd.Series(unique) # Transformation in Series
    unique_df = pd.DataFrame()
    unique_df[['A-Länge','A-Breite','A-Richtung','Rest']] = unique.str.split(expand=True)
    
    unique_df.to_csv('Results_CSV/UniqueFunkzellen_A.csv',
                  index=False, encoding='utf-8')

    """ Funkmasten """
    df2 = pd.read_csv(path, sep=',')

    unique2 = df2.Funkmast.unique()  # Ausgabe in Array
    unique2.sort()
    unique2 = pd.Series(unique2)  # Transformation in Series
    unique_df2 = pd.DataFrame()
    unique_df2[['A-Länge', 'A-Breite']] = unique2.str.split(expand=True)
    print(unique_df2)

    unique_df2.to_csv('Results_CSV/UniqueFunkmasten_A.csv',
                     index=False, encoding='utf-8')


def geo_data():
    """ Erstellt eine HTML-Datei, die die Funkmasten auf einer OSM-Karte zeigt.
     Als Datei, sollte die UniqueFunkmasten CSV verwendet werden."""

    path = input("Enter the directory where the file with the unique celltowers is located: ")
    df = pd.read_csv(path, sep=',')
    geo_df = pd.DataFrame(df)

    # Datentypen der Breiten- & Längengrade umwandeln
    geo_df['A-Länge'] = pd.to_numeric(df['A-Länge'], errors='coerce')
    geo_df['A-Breite'] = pd.to_numeric(df['A-Breite'], errors='coerce')

    geo_df = geo_df.dropna(
        subset=['A-Länge', 'A-Breite'])  # Entfernen der Zeilen, die keine Breiten-& Längengrade enthalten
    print("Building OpenStreetMap... Please wait.")

    """Folium Map initialisieren. Göttingen als Startpunkt"""
    m1 = folium.Map(location=[51.5412, 9.9158], zoom_start=9.5, control_scale=True)

    for (index, row) in geo_df.iterrows():
        folium.Marker(location=[row.loc['A-Breite'], row.loc['A-Länge']],
                      popup='Funkmast: ' + str(row['A-Länge']) + str(' ') + str(row['A-Breite'])).add_to(m1)

    m1.save('Results_HTML/CellTowers_MarkerMap_A.html')
    print("You can find the file in ../Results_HTML/CellTowers_MarkerMap_A.html")

def statistics():
    """Führt eine Statistik-Analyse von der durchschnittlichen Nutzungsdauer der Dienste
        und der meistbenutzten Funkmasten durch."""

    global file_name


    path = input("Enter the directory where the file is located: ")
    z = pd.read_csv(path, sep=',')

    """ Anzahl an Personen, Einträgen insgesamt in der CSV-Datei etc"""
    row_counts = z.shape[0]
    anum_counts = z['A-Nummer'].nunique()
    funkmast_counts = z['Funkmast'].nunique()
    funkzelle_counts = z['Funkzelle'].nunique()

    print('CSV Infos:')
    print("Zeilen Einträge: %s" % row_counts)
    print("Einzigartige A-Nummern: %s" % anum_counts)
    print("Einzigartige Funkmasten: %s" % funkmast_counts)
    print("Einzigartige Funkzellen: %s" % funkzelle_counts,"\n")

    """ Verhältnisse der jeweiligen Provider"""
    prov_counts = z['Provider'].value_counts()
    prov_norm = z['Provider'].value_counts(normalize=True).round(6)
    prov_proz = z['Provider'].value_counts(normalize=True).mul(100).round(2)

    z_prov_counts = pd.DataFrame(prov_counts).reset_index() # transformieren in dataframes
    z_prov_norm = pd.DataFrame(prov_norm).reset_index()
    z_prov_proz = pd.DataFrame(prov_proz).reset_index()

    z_prov_counts.columns = ['Provider', 'Gesamtanzahl_Eintraege'] # umbenennen der Spalten
    z_prov_norm.columns = ['Provider', 'Gesamtanzahl_norm']
    z_prov_proz.columns = ['Provider', 'Gesamtanzahl_%']

    result_prov = pd.merge(pd.merge(z_prov_counts, z_prov_proz, on="Provider"), z_prov_norm, on="Provider")
    print("Verhältnisse der Provider:")
    print(result_prov, "\n")

    """Generelle Nutzung der Dienste"""
    dienst_counts = z['Dienst'].value_counts()
    dienst_norm = z['Dienst'].value_counts(normalize=True).round(4)
    dienst_proz = z['Dienst'].value_counts(normalize=True).mul(100).round(2)
    avg_diedauer = z.groupby('Dienst', as_index=False)['Dauer'].mean().round(2)

    z_dienst_counts = pd.DataFrame(dienst_counts).reset_index()
    z_dienst_norm = pd.DataFrame(dienst_norm).reset_index()
    z_dienst_proz = pd.DataFrame(dienst_proz).reset_index()
    z_avg_diedauer = pd.DataFrame(avg_diedauer)

    z_dienst_counts.columns = ['Dienst', 'Gesamtanzahl']
    z_dienst_norm.columns = ['Dienst', 'Gesamtanzahl_norm.']
    z_dienst_proz.columns = ['Dienst', 'Gesamtanzahl_%']
    z_avg_diedauer.columns = ['Dienst', 'AVG_Dauer']

    dienst_list = [z_dienst_counts, z_dienst_proz, z_dienst_norm, z_avg_diedauer]
    z_dienst = dienst_list[0]
    for z_dienst_ in dienst_list[1:]:
        z_dienst = z_dienst.merge(z_dienst_, on='Dienst')
    print("Generelle Nutzung der Dienste (ohne Berücksichtigung der Provider):")
    print(z_dienst, "\n")

    """"Generelle Nutzung der Dienste unter Berücksichtigung der Provider"""
    prov_diecounts = z.groupby(['Provider', 'Dienst']).size().to_frame('Gesamtanzahl')
    prov_diecounts_norm = z.groupby(['Provider', 'Dienst']).size().to_frame('Gesamtanzahl_norm.')
    prov_diecounts_proz = z.groupby(['Provider', 'Dienst']).size().to_frame('Gesamtanzahl_%')
    a2 = prov_diecounts_norm.groupby('Provider')['Gesamtanzahl_norm.'].transform('sum')
    prov_diecounts_norm['Gesamtanzahl_norm.'] = prov_diecounts_norm['Gesamtanzahl_norm.'].div(a2)
    prov_diecounts_proz['Gesamtanzahl_%'] = prov_diecounts_norm['Gesamtanzahl_norm.'].mul(100).round(2)

    prov_avg_diedauer = z.groupby(['Provider', 'Dienst'])['Dauer'].mean().round(2).to_frame('AVG_Dauer')
    prov_avgdiedauer_norm = z.groupby(['Provider', 'Dienst'])['Dauer'].mean().round(2).to_frame('AVG_Dauer_norm.')
    prov_avgdiedauer_proz = z.groupby(['Provider', 'Dienst'])['Dauer'].mean().round(2).to_frame('AVG_Dauer_%')
    a3 = prov_avgdiedauer_norm.groupby('Provider')['AVG_Dauer_norm.'].transform('sum')
    prov_avgdiedauer_norm['AVG_Dauer_norm.'] = prov_avgdiedauer_norm['AVG_Dauer_norm.'].div(a3)
    prov_avgdiedauer_proz['AVG_Dauer_%'] = prov_avgdiedauer_norm['AVG_Dauer_norm.'].mul(100).round(2)

    z_prov_diecounts = pd.DataFrame(prov_diecounts)
    z_prov_diecounts_norm = pd.DataFrame(prov_diecounts_norm)
    z_prov_diecounts_proz = pd.DataFrame(prov_diecounts_proz)
    z_prov_avg_diedauer = pd.DataFrame(prov_avg_diedauer)
    z_prov_avgdiedauer_norm = pd.DataFrame(prov_avgdiedauer_norm)
    z_prov_avgdiedauer_proz = pd.DataFrame(prov_avgdiedauer_proz)

    dienst_list2 = [z_prov_diecounts, z_prov_diecounts_proz,z_prov_diecounts_norm, z_prov_avg_diedauer,
        z_prov_avgdiedauer_proz,z_prov_avgdiedauer_norm]
    z_dienst2 = dienst_list2[0]
    for z_dienst2_ in dienst_list2[1:]:
        z_dienst2 = z_dienst2.merge(z_dienst2_, on=["Provider", "Dienst"])

    print("Generelle Nutzung der Dienste (unter Berücksichtigung der Provider):")
    print(z_dienst2, "\n")


    """Darstellung der meistbenutzten Funkzellen"""
    data = {}
    cell_tower = pd.DataFrame(data)
    cell_tower['Gesamtanzahl'] = z.value_counts('Funkzelle')  # Häufigkeitsangabe
    cell_tower['Gesamtanzahl_norm.'] = z.value_counts('Funkzelle', normalize=True).round(6)
    cell_tower['Gesamtanzahl_%'] = (cell_tower['Gesamtanzahl_norm.'] * 100).round(3)
    print("Meistbenutzte Funkzellen:")
    print(cell_tower, "\n")

    """Darstellung der meistbenutzten Funkmasten"""
    data1 = {}
    funkmast1 = pd.DataFrame(data1)
    funkmast1['Gesamtanzahl'] = z.value_counts('Funkmast')
    funkmast1['Gesamtanzahl_norm.'] = z.value_counts('Funkmast', normalize=True).round(6)
    funkmast1['Gesamtanzahl_%'] = (funkmast1['Gesamtanzahl_norm.'] * 100).round(3)
    print("Meistbenutzte Funkmasten:")
    print(funkmast1, "\n")


    # Speichern in Excel-Datei
    with pd.ExcelWriter('Results_CSV/Statistics_A.xlsx') as writer:

        result_prov.to_excel(writer, sheet_name='Verhaeltnisse der Provider')
        z_dienst.to_excel(writer, sheet_name='Dienstnutzung ohne Provider')
        z_dienst2.to_excel(writer, sheet_name='Dienstnutzung mit Provider')
        cell_tower.to_excel(writer, sheet_name='Meistbenutzte Funkzellen')
        funkmast1.to_excel(writer, sheet_name='Meistbenutzte Funkzellmasten')
    writer.save()

if __name__ == '__main__':
    pfad()
    #mergeCSV()
    #uniqueCT() 
    #geo_data() 
    #statistics()    

    sys.exit()
