import csv
from pathlib import Path
import matplotlib.pyplot as plt
import time

BILDER_ORDNER = Path("Bilder_Starke_Gewichtung")
BILDER_ORDNER.mkdir(exist_ok=True)
Wichtige_Dateien = [
    'ArrowHead',
    'BME',
    'ECG5000',
    'GunPoint',
    'Trace',
    'Rock'
]

# Definieren der zeitreihen
Zeitreihe_X = [1, 2, 3, 4, 5]
Zeitreihe_Y = [2, 4, 6, 8, 10]

def Distanzfunktion(a: float, b: float) -> float:
    """Berechnet die Distanz zwischen zwei Punkten a und b und gibt diese zurück."""
    return abs(a - b)

def Lokale_Kostenmatrix_Erstellen(X: list, Y: list) -> list:
    """Erstellt eine lokale Kostenmatrix für die gegebenen Zeitreihen X und Y."""
    Kostenmatrix = []
    for i in range(len(X)):
        Kostenmatrix.append([])
        for j in range(len(Y)):
            Kostenmatrix[-1].append(Distanzfunktion(X[i], Y[j]))
    return Kostenmatrix

def Globale_Kostenmatrix_Erstellen(Kostenmatrix: list) -> list:
    """
    Erstellt eine globale Kostenmatrix basierend auf der lokalen Kostenmatrix.
    Fügt außerdem eine Gewichtung hinzu, um unnatürliche Verzerrungn zu vermeiden.
    """
    Globale_Kostenmatrix = [[0] * len(Kostenmatrix[0]) for _ in range(len(Kostenmatrix))]
    for i in range(len(Kostenmatrix)):
        for j in range(len(Kostenmatrix[0])):
            Abstand = Kostenmatrix[i][j]
            if i == 0 and j == 0:
                Globale_Kostenmatrix[i][j] = Abstand
            elif i == 0: 
                Globale_Kostenmatrix[i][j] = (Globale_Kostenmatrix[i][j-1] + Abstand)
            elif j == 0:
                Globale_Kostenmatrix[i][j] = (Globale_Kostenmatrix[i-1][j] + Abstand)
            else:
                Globale_Kostenmatrix[i][j] = (min(
                    Globale_Kostenmatrix[i-1][j] * 10,
                    Globale_Kostenmatrix[i][j-1] * 10,
                    Globale_Kostenmatrix[i-1][j-1]
                ) + Abstand)
    return Globale_Kostenmatrix

def Optimale_Warping_Pfad_Berechnen(Globale_Kostenmatrix: list) -> tuple:
    """Berechnet den optimalen Warping-Pfad basierend auf der globalen Kostenmatrix. Gibt diesen Pfad sowie die Gesamtkosten zurück."""
    i = len(Globale_Kostenmatrix) - 1
    j = len(Globale_Kostenmatrix[0]) - 1
    Gesamtkosten = Globale_Kostenmatrix[i][j]
    Optimaler_Pfad = [(i, j)]
    while not (i == 0 and j == 0):
        if i == 0:
            j -= 1
            Optimaler_Pfad.append((i, j))
        elif j == 0:
            i -= 1
            Optimaler_Pfad.append((i, j))
        else:
            diagonal = Globale_Kostenmatrix[i-1][j-1]
            oben = Globale_Kostenmatrix[i-1][j]
            links = Globale_Kostenmatrix[i][j-1]
            kleinster_vorgaenger = min(diagonal, oben, links)

            if diagonal == kleinster_vorgaenger:
                i -= 1
                j -= 1
                Optimaler_Pfad.append((i, j))
            elif oben == kleinster_vorgaenger:
                i -= 1
                Optimaler_Pfad.append((i, j))
            else:
                j -= 1
                Optimaler_Pfad.append((i, j))
    Optimaler_Pfad.reverse()
    
    return Optimaler_Pfad, Gesamtkosten

def Zeitreihen_Plotten(X: list, Y: list, Dateiname: str = "Zeitreihen.png") -> None:
    """Stellt die Zeitreihen X und Y jeweils in einem eigenen Graphen dar."""
    fig, achsen = plt.subplots(2, 1, sharex=True, figsize=(10, 6))

    achsen[0].plot(X, color="tab:blue")
    achsen[0].set_title("Zeitreihe X")
    achsen[0].set_ylabel("Wert")
    achsen[0].grid(True)

    achsen[1].plot(Y, color="tab:orange")
    achsen[1].set_title("Zeitreihe Y")
    achsen[1].set_xlabel("Zeitpunkt")
    achsen[1].set_ylabel("Wert")
    achsen[1].grid(True)

    plt.tight_layout()
    plt.savefig(BILDER_ORDNER / Dateiname, dpi=300)
    # plt.show()

def Warping_Pfad_Plotten(X: list, Y: list, Optimaler_Pfad: list, Dateiname: str, Laufzeit: float) -> None:
    """Stellt den Warping-Pfad und die dadurch verzerrte Zeitreihe Y dar."""
    fig, achsen = plt.subplots(2, 1, figsize=(12, 8))
    fig.suptitle(f'Laufzeit: {Laufzeit:.4f} Sekunden; Datenpunkte: {len(X)}', fontsize=16)

    y_verschiebung = min(X + Y) - max(X + Y) - 1
    Y_verschoben = [wert + y_verschiebung for wert in Y]

    achsen[0].plot(X, color="tab:blue", label="Zeitreihe X")
    achsen[0].plot(Y_verschoben, color="tab:orange", label="Zeitreihe Y (verschoben)")

    for i, j in Optimaler_Pfad:
        achsen[0].plot(
            [i, j],
            [X[i], Y_verschoben[j]],
            color="gray",
            alpha=0.25,
            linewidth=0.8
        )

    achsen[0].set_title("Zuordnung der Punkte durch den Warping-Pfad")
    achsen[0].set_xlabel("Zeitpunkt")
    achsen[0].set_ylabel("Wert")
    achsen[0].legend()
    achsen[0].grid(True)

    Y_Werte_Pro_X = [[] for _ in range(len(X))]
    for i, j in Optimaler_Pfad:
        Y_Werte_Pro_X[i].append(Y[j])

    Verzerrte_Zeitreihe_Y = []
    for werte in Y_Werte_Pro_X:
        Verzerrte_Zeitreihe_Y.append(sum(werte) / len(werte))

    achsen[1].plot(X, color="tab:blue", label="Zeitreihe X")
    achsen[1].plot(Verzerrte_Zeitreihe_Y, color="tab:green", label="Verzerrte Zeitreihe Y")
    achsen[1].set_title("Zeitreihe Y nach der Verzerrung durch DTW")
    achsen[1].set_xlabel("Zeitpunkt von X")
    achsen[1].set_ylabel("Wert")
    achsen[1].legend()
    achsen[1].grid(True)

    plt.tight_layout(rect= [0,0,1,0.96])
    plt.savefig(BILDER_ORDNER / f'{Dateiname}.png', dpi=300)
    # plt.show()

from pathlib import Path

ordner = Path("UCRArchive_2018")

for datei in ordner.iterdir():
    if datei.is_dir():
        if datei.name in Wichtige_Dateien:
            Datensatz = []
            try:
                with open(f'UCRArchive_2018/{datei.name}/{datei.name}_TRAIN.tsv', "r", encoding="utf-8") as file:
                    reader = csv.reader(file, delimiter="\t")
                    
                    for zeile in reader:
                        Datensatz.append([])
                        for Wert in zeile[1:]:
                            Datensatz[-1].append(float(Wert))
            except Exception as e:
                print(f"Fehler beim Einlesen der Datei {datei.name}: {e}")
                continue
                

            # for i in range(len(Datensatz) - 1):
            Zeitreihe_X = Datensatz[0]
            Zeitreihe_Y = Datensatz[1]
            
            Start = time.time()

            Lokale_Kostenmatrix = Lokale_Kostenmatrix_Erstellen(Zeitreihe_X, Zeitreihe_Y)
            Globale_Kostenmatrix = Globale_Kostenmatrix_Erstellen(Lokale_Kostenmatrix)
            Optimaler_Pfad, Gesamtkosten = Optimale_Warping_Pfad_Berechnen(Globale_Kostenmatrix)
            
            Ende = time.time()

            # Zeitreihen_Plotten(Zeitreihe_X, Zeitreihe_Y, f'{datei.name}_Zeitreihen.png')
            Warping_Pfad_Plotten(Zeitreihe_X, Zeitreihe_Y, Optimaler_Pfad, datei.name, Ende - Start)
