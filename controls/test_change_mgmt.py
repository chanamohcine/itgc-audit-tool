# ============================================================
# TEST ITGC N°3 : Change Management Non Autorisé
# Framework : COBIT 2019 - BAI06 / BAI07
# Règle 1 : Toute modification en PRODUCTION doit être APPROUVEE
# Règle 2 : Aucune modification en PRODUCTION entre 20h et 6h
# ============================================================

import pandas as pd
import os
from datetime import datetime

# ----------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------
BASE_DIR        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FICHIER_CHANGES = os.path.join(BASE_DIR, "data", "change_log.csv")
FICHIER_RAPPORT = os.path.join(BASE_DIR, "reports", "rapport_change_mgmt.xlsx")

HEURE_DEBUT_NUIT = 20   # à partir de 20h = hors heures ouvrées
HEURE_FIN_NUIT   = 6    # jusqu'à 6h = hors heures ouvrées

# ----------------------------------------------------------
# ÉTAPE A : Charger les données
# ----------------------------------------------------------
df = pd.read_csv(FICHIER_CHANGES)

# Convertir heure_changement en nombre entier pour comparer
# "23:45" → 23
df["heure"] = pd.to_datetime(df["heure_changement"], format="%H:%M").dt.hour

print("=== Changements chargés ===")
print(df[["change_id", "user_name", "type_changement",
          "environnement", "statut_ticket", "heure"]])

# ----------------------------------------------------------
# ÉTAPE B : Règle 1 — Modifications PRODUCTION sans approbation
# ----------------------------------------------------------
# On garde uniquement les lignes PRODUCTION
# dont le ticket n'est PAS approuvé
cas_non_approuve = df[
    (df["environnement"] == "PRODUCTION") &
    (df["statut_ticket"] != "APPROUVE")
].copy()
cas_non_approuve["type_violation"] = "Modification PROD sans approbation"

print(f"\n=== Règle 1 : Non approuvés en PROD ===")
print(f"Violations : {len(cas_non_approuve)}")
print(cas_non_approuve[["change_id", "user_name",
                          "statut_ticket", "type_violation"]])

# ----------------------------------------------------------
# ÉTAPE C : Règle 2 — Modifications PRODUCTION hors heures ouvrées
# ----------------------------------------------------------
# Hors heures = heure >= 20h OU heure < 6h
cas_hors_heures = df[
    (df["environnement"] == "PRODUCTION") &
    (
        (df["heure"] >= HEURE_DEBUT_NUIT) |
        (df["heure"] < HEURE_FIN_NUIT)
    )
].copy()
cas_hors_heures["type_violation"] = "Modification PROD hors heures ouvrées"

print(f"\n=== Règle 2 : Hors heures ouvrées en PROD ===")
print(f"Violations : {len(cas_hors_heures)}")
print(cas_hors_heures[["change_id", "user_name",
                         "heure", "type_violation"]])

# ----------------------------------------------------------
# ÉTAPE D : Fusionner et dédoublonner
# ----------------------------------------------------------
# Un changement peut violer les DEUX règles à la fois
# (non approuvé ET fait à 3h du matin)
# pd.concat = empile les deux tableaux
# drop_duplicates = garde une seule ligne par change_id si doublon
violations = pd.concat(
    [cas_non_approuve, cas_hors_heures],
    ignore_index=True
)

# Pour les doublons, on concatène les types de violation
violations_groupees = violations.groupby("change_id").agg(
    user_id          = ("user_id", "first"),
    user_name        = ("user_name", "first"),
    type_changement  = ("type_changement", "first"),
    environnement    = ("environnement", "first"),
    statut_ticket    = ("statut_ticket", "first"),
    date_changement  = ("date_changement", "first"),
    heure_changement = ("heure_changement", "first"),
    heure            = ("heure", "first"),
    type_violation   = ("type_violation", lambda x: " + ".join(x.unique()))
).reset_index()

print(f"\n=== TOTAL VIOLATIONS UNIQUES ===")
print(f"Nombre : {len(violations_groupees)}")
print(violations_groupees[["change_id", "user_name",
                             "statut_ticket", "heure", "type_violation"]])

# ----------------------------------------------------------
# ÉTAPE E : Criticité
# ----------------------------------------------------------
def criticite_change(row):
    # Violation double (non approuvé + nuit) = risque maximum
    if "+" in row["type_violation"]:
        return "🔴 CRITIQUE"
    elif row["statut_ticket"] == "NON_APPROUVE":
        return "🔴 CRITIQUE"
    elif row["heure"] >= HEURE_DEBUT_NUIT or row["heure"] < HEURE_FIN_NUIT:
        return "🟠 ÉLEVÉ"
    else:
        return "🟡 MOYEN"

violations_groupees["criticite"]      = violations_groupees.apply(criticite_change, axis=1)
violations_groupees["controle"]       = "Change Management - COBIT BAI06"
violations_groupees["recommandation"] = "Reverter le changement et ouvrir une investigation"

# ----------------------------------------------------------
# ÉTAPE F : Export Excel
# ----------------------------------------------------------
colonnes = [
    "controle", "change_id", "user_id", "user_name",
    "type_changement", "environnement", "statut_ticket",
    "date_changement", "heure_changement",
    "type_violation", "criticite", "recommandation"
]

rapport = violations_groupees[colonnes].copy()
rapport.to_excel(FICHIER_RAPPORT, index=False)

print(f"\n✅ Rapport exporté : {FICHIER_RAPPORT}")
print(f"📋 {len(rapport)} violation(s) documentée(s)")