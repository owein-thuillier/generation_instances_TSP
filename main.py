import json
import datetime
import time
import random
import glob
from asciiArt import *
import os # Commandes systèmes
import matplotlib.pyplot as plt

#################### Clé API : "mapquest" ####################

# url : https://developer.mapquest.com/
# Consumer Key : ...

APIKEY = ""

#################### Fonctions et procédures ####################


def tirageAleatoire(dataset, n): 
    # Tirage aléatoire de n locations dans le dataset selectionné et les écrit dans un fichier temporaire
    texte = ""
    tirages = [] # On maintient une liste des nombres tirés aléatoirement pour ne pas tirer deux fois le même
    with open(dataset, "r") as f:
        lignes = f.readlines()
        for i in range(n):
            tirage = random.randint(0, len(lignes)-1)
            while tirage in tirages:
                tirage = random.randint(0, len(lignes)-1)
            tirages.append(tirage)
            texte += lignes[tirage]

    with open("Temp/locationsChoisies", "a") as f: 
        f.write(texte) 


def lectureCoords(coords, noms, latitudes, longitudes):  
    ###### Lecture des coordonnées dans un fichier texte avec un format précis (nom,lat,long,)
    with open("Temp/locationsChoisies", "r") as f:
            for l in f:
                ligne = l.split(",")
                noms.append(ligne[0])
                coords.append(ligne[1] + "," + ligne[2])
                latitudes.append(float(ligne[1]))
                longitudes.append(float(ligne[2]))
    os.system("rm Temp/locationsChoisies")

def requete(coords):
    ###### Requête au serveur "mapquest" pour obtenir le distancier (API) à partir d'un ensemble de locations
    # Ecriture du corps de la requête dans un fichier json
    options = {"allToAll": True, "unit": "k", "routeType": "shortest", "locale": "fr_FR", "doReverseGeocode": False}
    corpsRequete = {"locations":coords, "options":options}
    with open("Temp/corps.json", "w") as json_file:
        json.dump(corpsRequete, json_file)


    # Requête json au serveur (clé API) avec le fichier "data.json" en corps de requête et création du fichier "res.json" contenant les élements de la réponse 
    os.system("curl -X POST -H \"Content-Type: application/json\" -d @Temp/corps.json \"http://www.mapquestapi.com/directions/v2/routematrix?key="+APIKEY+"\" > Temp/res.json") 


    # Lecture du fichier json contenant la réponse du serveur
    with open("Temp/res.json") as f:
        data = json.load(f)

    # Suppression des fichiers (inutiles désormais)
    os.system("rm Temp/res.json Temp/corps.json")

    return data


def affichageDistancier(data, noms, nbLocations, aSupprimer=[]):
    ###### Affichage de la matrice avec un arrondi à 1 chiffre après la virgule (pour avoir un affichage clean)
    # En-tête de la matrice
    print("\n\n                       .", end="")
    for i in range(nbLocations):
        print("-----",end="")
    print(".")

    print("                       |  ", end="")
    for i in range(nbLocations):
        print((i+1)%10," | ",end="")

    print("\n                .------.", end="")
    for i in range(nbLocations):
        print("-----",end="")
    print(".")

    # Corps de la matrice
    for i in range(nbLocations):
        print((noms[i]+"              ")[0:15],"| ",(str(i+1)+"   ")[0:4], end="") 
        print("| ", end="") 
        if i in aSupprimer:
           print(" *   "*(nbLocations-1), end="")
           print(" *  |")
        else:
            ligne = data["distance"][i]
            for j in range(nbLocations):
                if j in aSupprimer:
                     print(" *   ", end="")
                elif j == nbLocations-1: 
                    print(round(float(ligne[j]),1), "", end="")
                else:
                    print(round(float(ligne[j]),1), " ", end="")
            print("|") # Retour à la ligne 

    # Pied de la matrice
    print("                .------.", end="")
    for i in range(nbLocations):
        print("-----",end="")
    print(".")

    print("\n\n    --> Les distances correspondent au plus court chemin entre deux lieux (unité : km.)\n\n")
    #time.sleep(3)

def nettoyageDonnees(data, noms, nbLocations):
    ###### Nettoyage des données (on supprime les locations inaccessibles)
    aSupprimer = []
    for i in range(nbLocations):
        test = False
        for j in range(nbLocations):
            if float(data["distance"][i][j]) != 0.0:
                test = True
                break
        if test == False:
            aSupprimer.append(i)

    print("    Liste des locations erronées à supprimer :")
    print("    ------------------------------------------")
    for i in aSupprimer:
        print("      --> "+str(i+1)+") "+str(noms[i]))

    return aSupprimer

def creationDossier(nbLocations, nomInstance):
    ###### Génération du dossier contenant l'instance générée et les documents associés
    #ajd = datetime.date.today()
    #nomDossier = ajd.isoformat()+"#"+str(round(time.time())) # Création d'un dossier unique avec la date + epoch unix
    with open("compteur", "r") as f:
        lignes = f.readlines()
        identifiant = int(lignes[0])
    os.system("echo '"+str(identifiant+1)+"' > compteur")       
    nomDossier = "instance_"+str(nomInstance)+"_"+str(nbLocations)+"#"+str(identifiant)
    os.system("mkdir "+nomDossier+"")
    return nomDossier, identifiant
    


def generationImage(coords, latitudes, longitudes, nbLocations, aSupprimer, nomInstance):
    ###### Génération de l'image
    minLat = min(latitudes)
    maxLat = max(latitudes)
    minLong = min(longitudes)
    maxLong = max(longitudes)

    # Liste des locations à mettre sur l'image
    loc = ""
    for i in range(nbLocations-1):
        if i not in aSupprimer:
            loc += coords[i] + "||"
        else:
            loc += coords[i] + "|marker-num-D51A1A" + "||" 

    if (nbLocations-1) not in aSupprimer:
        loc += coords[nbLocations-1]
    else:
        loc += coords[nbLocations-1] + "|marker-num-D51A1A"


    # Génération de l'url et download de l'image
    url = "https://www.mapquestapi.com/staticmap/v5/map?key="+APIKEY+"&boundingBox="+str(maxLat)+","+str(minLong)+","+str(minLat)+","+str(maxLong)+"&size=1000,1000&defaultMarker=marker-num&locations="+loc+"&banner="+nomInstance+" (n = "+str(nbLocations-len(aSupprimer))+")&scalebar=true&type=map&margin=100"
    os.system("wget \""+url+"\"")
    # On garde l'image dans le dossier racine (mais on la renome), nécessaire pour la compilaton du pdf LaTeX
    os.system("mv map* image.jpeg")


def generationDocumentLatex(nomDossier, data, noms, latitudes, longitudes, nbLocations, aSupprimer, identifiant):
    ###### Génération documentation LaTeX
    with open(""+nomDossier+"/documentation", "a") as f:
        # En-tête du document
        chaine = "\\documentclass{article}"
        chaine += "\n\\usepackage{float}"
        chaine += "\n\\usepackage{graphicx, multicol}"
        chaine += "\n\\usepackage{multirow}"
        chaine += "\n\\usepackage{hyperref}"
        chaine += "\n\\parskip8pt"
        chaine += "\n\\begin{document}"
        chaine += "\n\\renewcommand{\\contentsname}{Table des matières}"
        chaine += "\n\\tableofcontents"
        f.write(chaine)
        # Tableau des coordonnées
        f.write("\n\n\\newpage")
        #chaine = "\n\\vspace*{\\fill}"
        chaine = "\n\\section{Instance $n^{o}"+str(identifiant)+"$}" 
        chaine += "\n\\subsection{Coordonnées géographiques}"         
        chaine += "\n\n\\renewcommand{\\arraystretch}{1.6}"
        chaine += "\n\\begin{table}[H]"
        chaine += "\n\\begin{center}"
        chaine += "\n\\begin{tabular}{|c|c|c|c|}"
        chaine += "\n\\hline"
        chaine += "\n\\textbf{Identifiant} & \\textbf{Lieu} & \\textbf{Latitude} & \\textbf{Longitude} \\\\"
        chaine += "\n\\hline"
        for i in range(nbLocations):
            if i not in aSupprimer:
                chaine += "\n\\textbf{"+str(i+1)+"} & "+noms[i]+" & "+str(latitudes[i])+" & "+str(longitudes[i])+" \\\\ "        
                chaine += "\n\\hline"  
        chaine += "\n\\end{tabular}"
        #chaine += "\n\\caption{Coordonnées géographiques}"  
        chaine += "\n\\end{center}" 
        chaine += "\n\\end{table}"
        #chaine += "\n\\vspace*{\\fill}"                  
        f.write(chaine)
        # Distancier (matrice)
        f.write("\n\n\\newpage")
        #chaine = "\n\\vspace*{\\fill}"    
        chaine = "\n\\subsection{Distancier (unité : km.)}"          
        chaine += "\\renewcommand{\\arraystretch}{1.6}"
        chaine += "\n\\begin{table}[H]"
        chaine += "\n\\begin{center}"
        col = "|c|"
        for i in range(nbLocations):
            if i not in aSupprimer:
                col += "c|"
        chaine += "\n\\begin{tabular}{"+col+"}"
        chaine += "\n\\cline{2-"+str(nbLocations+1-len(aSupprimer))+"}"
        chaine += "\n\\multicolumn{1}{c|}{}"
        for i in range(nbLocations-1): 
            if i not in aSupprimer: 
                chaine += "& \\textbf{"+str(i+1)+"}"  
        if (nbLocations-1) not in aSupprimer: 
            chaine += "& \\textbf{"+str(nbLocations)+"} \\\\" 
        else:
            chaine += "\\\\"
        chaine += "\n\\hline"
        for i in range(nbLocations):
            if i not in aSupprimer:
                chaine += "\n\\textbf{"+str(i+1)+"}"
                for j in range(nbLocations-1):
                    if j not in aSupprimer:
                        chaine += " & "+str(round(float(data["distance"][i][j]),1))
                if (nbLocations-1) not in aSupprimer: 
                    chaine += " & "+str(round(float(data["distance"][i][nbLocations-1]),1))+"\\\\"
                else:
                    chaine += "\\\\"
                chaine += "\n\\hline"  
        chaine += "\n\\end{tabular}"
        #chaine += "\n\\caption{Distancier}"  
        chaine += "\n\\end{center}" 
        chaine += "\n\\end{table}" 
        #chaine += "\n\\vspace*{\\fill}"     
        f.write(chaine)
        # Figure
        f.write("\n\n\\newpage")
        f.write("\n\n")
        #chaine = "\n\\vspace*{\\fill}"  
        chaine = "\n\\subsection{Illustration}"            
        chaine += "\n\\begin{figure}[H]"     
        chaine += "\n\\center"  
        chaine += "\n\\includegraphics[scale=0.36]{image.jpeg}"
        #chaine += "\n\\caption{Illustration}"
        chaine += "\n\\end{figure}"
        #chaine += "\n\\vspace*{\\fill}"      
        f.write(chaine) 
        # Pied de document
        chaine = "\n\n\\end{document}"
        f.write(chaine)

    # Création du pdf
    os.system("pdflatex -output-directory="+nomDossier+" "+nomDossier+"/documentation")
    # Il faut compiler deux fois pour obtenir la table des matières
    os.system("pdflatex -output-directory="+nomDossier+" "+nomDossier+"/documentation") 
    # On replace l'image dans le dossier une fois la compilation terminé
    os.system("mv image.jpeg "+nomDossier+"/")
    os.system("rm "+nomDossier+"/*.aux")
    os.system("rm "+nomDossier+"/*.log")
    os.system("rm "+nomDossier+"/*.out")
    os.system("rm "+nomDossier+"/*.toc")




def generationInstance(nomDossier, data, noms, latitudes, longitudes, nbLocations, aSupprimer, identifiant):
    ###### Génération de l'instance à proprement parler (au format textuel)
    with open(""+nomDossier+"/instance_"+str(identifiant)+"", "a") as f:  
        chaine = str(nbLocations) 
        chaine += "\n"
        # Coordonnées
        for i in range(nbLocations):
            if i not in aSupprimer:
                chaine += "\n"+noms[i]+","+str(latitudes[i])+","+str(longitudes[i])+","    
        f.write(chaine)
        # Distancier
        chaine = "\n"
        for i in range(nbLocations):
            if i not in aSupprimer:
                chaine += "\n"         
                for j in range(nbLocations):
                    if j not in aSupprimer:
                        chaine += str(round(float(data["distance"][i][j]),1))+","
        f.write(chaine)


#################### Programme principal - 1 instance à la fois ####################

def main():
    asciiArtDebut()

    # Choix du dataset
    fichiers = glob.glob("Data/*")
    print("    Liste des dataset disponibles :")
    print("    -------------------------------")
    i = 1
    for f in fichiers:
        print("      --> "+str(i)+") "+f.split("/")[1])
        i += 1
    choix = int(input("\n    --> Choix du dataset : "))
    dataset = fichiers[choix-1]

    # Tirage aléatoire de n locations à partir du dataset selectionné
    n = int(input("\n    --> Nombre de locations : "))
    print("\n\n")
    os.system("mkdir Temp")
    tirageAleatoire(dataset, n)

    # Lecture des coordonnées dans le fichier temporaire contenant les n locations tirées aléatoirement à partir du dataset
    coords = []
    noms = []
    latitudes = [] 
    longitudes = [] 
    lectureCoords(coords, noms, latitudes, longitudes)

    # Requête JSON au serveur "mapquest" pour obtenir le distancier (API)
    data = requete(coords)
    nbLocations = len(data["distance"])

    # Affichage du distancier 
    affichageDistancier(data, noms, nbLocations)

    # Nettoyage des données (il peut y avoir des données erronées)
    aSupprimer = nettoyageDonnees(data, noms, nbLocations)

    # Affichage du distancier après nettoyage
    affichageDistancier(data, noms, nbLocations, aSupprimer)

    # Création du dossier qui contiendra les différents fichiers de l'instance générée    
    nomInstance = (dataset.split("/")[1]).split("_")[0]
    nomDossier, identifiant = creationDossier(nbLocations-len(aSupprimer), nomInstance)

    # Génération de l'image illustrant l'instance générée
    generationImage(coords, latitudes, longitudes, nbLocations, aSupprimer, nomInstance)

    # Génération du document LaTeX décrivant l'instance (coordonnées, distancier, image)
    generationDocumentLatex(nomDossier, data, noms, latitudes, longitudes, nbLocations, aSupprimer, identifiant)

    # Génération de l'instance à proprement parler (format textuel)
    generationInstance(nomDossier, data, noms, latitudes, longitudes, nbLocations, aSupprimer, identifiant)
    
    # Déplacement de l'instance générée dans le dossier contenant toutes les instances générées jusqu'à lors
    os.system("mkdir Instances")
    os.system("mv instance_* Instances/")

    # On supprime le dossier temporaire
    os.system("rm -r Temp")

    # Fin du programme
    asciiArtFin()


#################### Programme principal - n instances à la fois ####################

def bulk(nbInstance):
    for i in range(nbInstance):
        # Choix du dataset
        fichiers = glob.glob("Data/*")
        choix = random.randint(0, len(fichiers)-1)
        dataset = fichiers[choix]
        
        # Tirage aléatoire de n locations à partir du dataset selectionné
        borneSup = int((dataset.split("/")[1]).split("_")[1]) # nombre de locations dans le dataset sélectionné
        if borneSup < 25:
            n = random.randint(3, borneSup)
        else:
            n = random.randint(3, 25)  # On ne peut pas faire plus de 25 locations

        os.system("mkdir Temp")
        tirageAleatoire(dataset, n)

        # Lecture des coordonnées dans le fichier temporaire contenant les n locations tirées aléatoirement à partir du dataset
        coords = []
        noms = []
        latitudes = [] 
        longitudes = [] 
        lectureCoords(coords, noms, latitudes, longitudes)

        # Requête JSON au serveur "mapquest" pour obtenir le "distancier" (API)
        data = requete(coords)
        nbLocations = len(data["distance"])

        # Nettoyage des données (il peut y avoir des données erronées)
        aSupprimer = nettoyageDonnees(data, noms, nbLocations)

        # Création du dossier qui contiendra les différents fichiers de l'instance générée    
        nomInstance = (dataset.split("/")[1]).split("_")[0]
        nomDossier, identifiant = creationDossier(nbLocations-len(aSupprimer), nomInstance)

        # Génération de l'image illustrant l'instance générée
        generationImage(coords, latitudes, longitudes, nbLocations, aSupprimer, nomInstance)

        # Génération du document LaTeX décrivant l'instance (coordonnées, distancier, image)
        generationDocumentLatex(nomDossier, data, noms, latitudes, longitudes, nbLocations, aSupprimer, identifiant)

        # Génération de l'instance à proprement parler (format textuel)
        generationInstance(nomDossier, data, noms, latitudes, longitudes, nbLocations, aSupprimer, identifiant)
    
        # Déplacement de l'instance générée dans le dossier contenant toutes les instances générées jusqu'à lors
        os.system("mkdir Instances")
        os.system("mv instance_* Instances/")

        # On supprime le dossier temporaire
        os.system("rm -r Temp")



#################### Appel de la fonction principale ####################

main()

#bulk(20)



