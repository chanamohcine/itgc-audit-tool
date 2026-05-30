# ============================================================
# TEST ITGC N°1 : Séparation des Tâches (SOD)
# Framework : COBIT 2019 - DSS05.04
# ============================================================

import pandas as pd
import os

# ----------------------------------------------------------
# CONFIGURATION : chemins
# ----------------------------------------------------------
BASE_DIR        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR        = os.path.join(BASE_DIR, "data")
REPORTS_DIR     = os.path.join(BASE_DIR, "reports")

FICHIER_ACCES   = os.path.join(DATA_DIR, "user_access.csv")
FICHIER_RAPPORT = os.path.join(REPORTS_DIR, "rapport_SOD.xlsx")

# ----------------------------------------------------------
# ÉTAPE A : Charger les données
# ----------------------------------------------------------
df = pd.read_csv(FICHIER_ACCES)

print("=== Données chargées ===")
print(df)
print(f"\nNombre total de lignes : {len(df)}")
print(f"Nombre d'utilisateurs distincts : {df['user_id'].nunique()}")

# ----------------------------------------------------------
# ÉTAPE B : Identifier les violations SOD
# ----------------------------------------------------------
ROLE_SAISIE     = "SAISIE_FACTURE"
ROLE_VALIDATION = "VALIDATION_PAIEMENT"

roles_par_user = df.groupby("user_id")["role"].apply(list).reset_index()
roles_par_user.columns = ["user_id", "liste_roles"]

print("\n=== Rôles par utilisateur ===")
print(roles_par_user)

def est_violation_sod(liste_roles):
    a_saisie     = ROLE_SAISIE in liste_roles
    a_validation = ROLE_VALIDATION in liste_roles
    return a_saisie and a_validation

roles_par_user["est_violation"] = roles_par_user["liste_roles"].apply(est_violation_sod)

violations = roles_par_user[roles_par_user["est_violation"] == True]

print("\n=== VIOLATIONS SOD DÉTECTÉES ===")
print(f"Nombre de violations : {len(violations)}")
print(violations[["user_id", "liste_roles"]])

# ----------------------------------------------------------
# ÉTAPE C : Enrichir avec les infos utilisateurs
# ----------------------------------------------------------
infos_users = df.drop_duplicates(subset="user_id")[
    ["user_id", "user_name", "department", "status", "last_login"]
]

rapport_sod = violations.merge(infos_users, on="user_id")

def niveau_criticite(row):
    if row["status"] == "ACTIF":
        return "🔴 CRITIQUE"
    else:
        return "🟡 MOYEN"

rapport_sod["criticite"] = rapport_sod.apply(niveau_criticite, axis=1)
rapport_sod["controle"]  = "SOD - Séparation des tâches"
rapport_sod["regle"]     = "SAISIE_FACTURE + VALIDATION_PAIEMENT interdits"

print("\n=== RAPPORT FINAL SOD ===")
print(rapport_sod[["user_id", "user_name", "department", "status", "criticite"]])

# ----------------------------------------------------------
# ÉTAPE D : Export Excel
# ----------------------------------------------------------
colonnes_rapport = [
    "controle", "regle", "user_id", "user_name",
    "department", "status", "last_login",
    "liste_roles", "criticite"
]

rapport_final = rapport_sod[colonnes_rapport].copy()

rapport_final["liste_roles"] = rapport_final["liste_roles"].apply(
    lambda roles: " | ".join(roles)
)

rapport_final.to_excel(FICHIER_RAPPORT, index=False)

print(f"\n✅ Rapport exporté : {FICHIER_RAPPORT}")
print(f"📋 {len(rapport_final)} violation(s) documentée(s)")