# ============================================================
# TEST ITGC N°2 : Comptes Inactifs avec Accès Sensibles
# Framework : COBIT 2019 - DSS05.04 / APO09
# ============================================================

import pandas as pd
import os
from datetime import datetime

# ----------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------
BASE_DIR        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FICHIER_ACCES   = os.path.join(BASE_DIR, "data", "user_access.csv")
FICHIER_RAPPORT = os.path.join(BASE_DIR, "reports", "rapport_acces_inactifs.xlsx")

SEUIL_JOURS  = 90
DATE_AUDIT   = datetime.today()

ROLES_SENSIBLES = [
    "SAISIE_FACTURE",
    "VALIDATION_PAIEMENT",
    "ADMIN_SYSTEME"
]

# ----------------------------------------------------------
# ÉTAPE A : Charger et préparer les données
# ----------------------------------------------------------
df = pd.read_csv(FICHIER_ACCES)
df["last_login"] = pd.to_datetime(df["last_login"])
df["jours_inactif"] = (DATE_AUDIT - df["last_login"]).dt.days

print("=== Jours d'inactivité calculés ===")
print(df[["user_id", "user_name", "status", "last_login", "jours_inactif"]])

# ----------------------------------------------------------
# ÉTAPE B : Deux cas de violation distincts
# ----------------------------------------------------------

# CAS A : Compte officiellement INACTIF avec rôle sensible
# → Le compte aurait dû être révoqué dès la désactivation
cas_A = df[
    (df["status"] == "INACTIF") &
    (df["role"].isin(ROLES_SENSIBLES))
].copy()
cas_A["type_violation"] = "Compte désactivé — accès non révoqué"

# CAS B : Compte ACTIF mais aucune connexion depuis >90 jours
# → Compte dormant, probablement oublié, potentiellement exploitable
cas_B = df[
    (df["status"] == "ACTIF") &
    (df["jours_inactif"] > SEUIL_JOURS) &
    (df["role"].isin(ROLES_SENSIBLES))
].copy()
cas_B["type_violation"] = f"Compte actif sans connexion depuis >{SEUIL_JOURS}j"

# Fusionner les deux cas dans un seul rapport
violations = pd.concat([cas_A, cas_B], ignore_index=True)

print(f"\n=== VIOLATIONS DÉTECTÉES ===")
print(f"Cas A (comptes désactivés) : {len(cas_A)}")
print(f"Cas B (comptes dormants)   : {len(cas_B)}")
print(f"Total                      : {len(violations)}")
print(violations[["user_id","user_name","role","status","jours_inactif","type_violation"]])

# ----------------------------------------------------------
# ÉTAPE C : Niveau de criticité
# ----------------------------------------------------------
def criticite_acces(row):
    if row["role"] == "ADMIN_SYSTEME":
        return "🔴 CRITIQUE"
    elif row["status"] == "INACTIF":
        return "🔴 CRITIQUE"
    elif row["jours_inactif"] > 180:
        return "🔴 CRITIQUE"
    else:
        return "🟠 ÉLEVÉ"

violations["criticite"]      = violations.apply(criticite_acces, axis=1)
violations["controle"]       = "Accès Inactifs - COBIT DSS05.04"
violations["recommandation"] = "Désactiver le compte et révoquer les accès"

# ----------------------------------------------------------
# ÉTAPE D : Export Excel
# ----------------------------------------------------------
colonnes = [
    "controle", "type_violation", "user_id", "user_name",
    "department", "role", "status",
    "last_login", "jours_inactif",
    "criticite", "recommandation"
]

rapport = violations[colonnes].copy()
rapport.to_excel(FICHIER_RAPPORT, index=False)

print(f"\n✅ Rapport exporté : {FICHIER_RAPPORT}")
print(f"📋 {len(rapport)} violation(s) documentée(s)")