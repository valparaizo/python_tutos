import yaml
import requests
import time
from datetime import datetime, timedelta, date
import pandas as pd

# INITIALISATION DE VARIABLES GLOBALES
sDateDebut = "2020-01-23"
sAujourdhui = date.today().strftime("%Y-%m-%d")
dDemarrageDate = datetime.fromisoformat(sDateDebut) 
cols = ['Date', 
        'FR Tot Cas Confirmés', 
        'FR Tot Décès', 
        'WW Tot Cas Confirmés', 
        'WW Tot Décès', 
        'Source',
        'FR Tot Guéris',
        'FR Tot Hospitalisés'
       ]

# FONCTIONS
def recupDataWithException2(_jsonout, _index1, _index2):
    try:
        data = _jsonout[_index1][_index2]
    except:
        data = 0
    return data

def AjouteSantePubliqueFrLigne(jsonout, df):
    df = df.append({
                    cols[0] : jsonout['date'] , 
                    cols[1] : recupDataWithException2(jsonout, 'donneesNationales', 'casConfirmes') , 
                    cols[2] : recupDataWithException2(jsonout, 'donneesNationales', 'deces'), 
                    cols[3] : recupDataWithException2(jsonout,'donneesMondiales', 'casConfirmes'),
                    cols[4] : recupDataWithException2(jsonout,'donneesMondiales', 'deces'),
                    cols[5] : 'sante-publique-france',
                    cols[6] : 0,
                    cols[7] : 0
                 } , 
                 ignore_index=True)
    return df

def ajouteLigneVide(df, madate):
    df = df.append({
                    cols[0] : madate , 
                    cols[1] : 0,
                    cols[2] : 0, 
                    cols[3] : 0,
                    cols[4] : 0,
                    cols[5] : 'no-data',
                    cols[6] : 0,
                    cols[7] : 0
                 } , 
                 ignore_index=True)
    return df

# RECUPERATION DONNEES SANTE PUBLIQUE FRANCE
def RecupereDonneesSantePubliqueFrance():
    print ('--> Démarrage du process')
    sDateParcours = sDateDebut
    i=1
    requesReturnCode=200
    yamls = pd.DataFrame()
    while (sDateParcours != sAujourdhui):
        myDate = dDemarrageDate + timedelta(days=i)
        sDateParcours = myDate.strftime("%Y-%m-%d")
        fichier = 'https://raw.githubusercontent.com/opencovid19-fr/data/master/sante-publique-france/' + sDateParcours + '.yaml'
        #print ('--> sante-publique-france / ', sDateParcours)
        req = requests.get(fichier)
        requesReturnCode = req.status_code
        if (requesReturnCode==200):
            yamlout = yaml.load(req.text, Loader=yaml.FullLoader)
            yamls = AjouteSantePubliqueFrLigne(yamlout, yamls)
        else:
            print ("(*) Pas de données pour ", myDate.strftime("%Y-%m-%d"))
            # ajoute une ligne vide
            yamls = ajouteLigneVide(yamls, myDate.strftime("%Y-%m-%d"))
        i=i+1
    print ('--> Fin du process')
    return yamls
    
# RECUPERATION DONNEES SANTE PUBLIQUE FRANCE
def RecupereDonneesMinistereSante(yamls):
    i=1
    sDateParcours = sDateDebut
    print ('--> Démarrage du process')
    while (sDateParcours != sAujourdhui):
        myDate = dDemarrageDate + timedelta(days=i)
        sDateParcours = myDate.strftime("%Y-%m-%d")
        #print("Traintement date: ",  dateParcours)
        fichier = 'https://raw.githubusercontent.com/opencovid19-fr/data/master/ministere-sante/' + sDateParcours + '.yaml'
        req = requests.get(fichier)
        requesReturnCode = req.status_code
        if (requesReturnCode==200):
            yamlout = yaml.load(req.text, Loader=yaml.FullLoader)
            if (yamls[cols[5]][i-1] == "no-data"):
                print ("(*) Modifie les données manquantes pour la date du ", myDate.strftime("%Y-%m-%d"))
                # Modifie toute la ligne
                yamls[cols[1]][i-1] = recupDataWithException2(yamlout, 'donneesNationales', 'casConfirmes')
                yamls[cols[2]][i-1] = recupDataWithException2(yamlout, 'donneesNationales', 'deces')
                yamls[cols[3]][i-1] = recupDataWithException2(yamlout, 'donneesMondiales', 'casConfirmes')
                yamls[cols[4]][i-1] = recupDataWithException2(yamlout, 'donneesMondiales', 'deces')
                yamls[cols[5]][i-1] = "ministere-sante"

            # Ajoute les nouveaux champs
            yamls[cols[6]][i-1] = recupDataWithException2(yamlout, 'donneesNationales', 'hospitalises')
            yamls[cols[7]][i-1] = recupDataWithException2(yamlout, 'donneesNationales', 'gueris')
        i=i+1
    print ('--> Fin du process')
    return yamls

def Bouchetrous(yamls):
    # On reparcourre toutes les lignes déjà récupérées précédemment
    i=1
    for index, row in yamls.iterrows():
        if (yamls[cols[5]][i-1] == "no-data"):
            for j in [1, 2, 3, 4, 6, 7]:
                yamls[cols[j]][i-1] = yamls[cols[j]][i-2]
        i += 1
    return yamls

# Programme principal
print ("Récupération des données de Santé Publique France")
data = RecupereDonneesSantePubliqueFrance()
print ("Récupération des données du ministère de la santé")
data = RecupereDonneesMinistereSante(data.copy())
print ("Comble les jours manquants")
data = Bouchetrous(data.copy())

data.to_csv("covid19.csv", index=False)

