# ============================================================
# ITGC AUDIT TOOL — Pipeline Principal
# Lance les 3 tests et consolide les résultats en un rapport
# Framework : COBIT 2019
# Auteur    : Mohcine Chana
# ============================================================

import pandas as pd
import os
from datetime import datetime

# ----------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------
BASE_DIR        = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR     = os.path.join(BASE_DIR, "reports")
RAPPORT_FINAL   = os.path.join(REPORTS_DIR, "RAPPORT_AUDIT_ITGC_FINAL.xlsx")

DATE_AUDIT      = datetime.today().strftime("%Y-%m-%d")

print("=" * 60)
print("   ITGC AUDIT TOOL — Démarrage du pipeline")
print(f"   Date d'audit : {DATE_AUDIT}")
print("=" * 60)

# ----------------------------------------------------------
# ÉTAPE A : Lancer les 3 tests via import
# ----------------------------------------------------------
# On importe chaque script comme un module Python
# Ça exécute le code de chaque fichier et génère les rapports Excel

print("\n[1/3] Test SOD — Séparation des tâches...")
import controls.test_sod

print("\n[2/3] Test Accès Inactifs...")
import controls.test_access_inactif

print("\n[3/3] Test Change Management...")
import controls.test_change_mgmt

# ----------------------------------------------------------
# ÉTAPE B : Lire les 3 rapports générés
# ----------------------------------------------------------
print("\n" + "=" * 60)
print("   Consolidation des résultats...")
print("=" * 60)

sod       = pd.read_excel(os.path.join(REPORTS_DIR, "rapport_SOD.xlsx"))
inactifs  = pd.read_excel(os.path.join(REPORTS_DIR, "rapport_acces_inactifs.xlsx"))
changes   = pd.read_excel(os.path.join(REPORTS_DIR, "rapport_change_mgmt.xlsx"))

# Harmoniser les colonnes pour pouvoir tout empiler
# Chaque rapport a ses colonnes propres — on garde le minimum commun
colonnes_communes = ["controle", "user_id", "user_name", "criticite"]

# Ajouter les colonnes manquantes avec une valeur vide
for df in [sod, inactifs, changes]:
    for col in colonnes_communes:
        if col not in df.columns:
            df[col] = ""

# ----------------------------------------------------------
# ÉTAPE C : Tableau de synthèse par test
# ----------------------------------------------------------
synthese = pd.DataFrame({
    "test"              : ["SOD", "Accès Inactifs", "Change Management"],
    "fichier_source"    : ["rapport_SOD.xlsx",
                           "rapport_acces_inactifs.xlsx",
                           "rapport_change_mgmt.xlsx"],
    "nb_violations"     : [len(sod), len(inactifs), len(changes)],
    "nb_critiques"      : [
        len(sod[sod["criticite"].str.contains("CRITIQUE", na=False)]),
        len(inactifs[inactifs["criticite"].str.contains("CRITIQUE", na=False)]),
        len(changes[changes["criticite"].str.contains("CRITIQUE", na=False)])
    ],
    "framework_cobit"   : ["DSS05.04", "DSS05.04 / APO09", "BAI06 / BAI07"],
    "date_audit"        : DATE_AUDIT
})

total_violations = synthese["nb_violations"].sum()
total_critiques  = synthese["nb_critiques"].sum()

print("\n=== SYNTHÈSE PAR TEST ===")
print(synthese.to_string(index=False))
print(f"\n{'='*40}")
print(f"  TOTAL VIOLATIONS : {total_violations}")
print(f"  DONT CRITIQUES   : {total_critiques}")
print(f"{'='*40}")

# ----------------------------------------------------------
# ÉTAPE D : Export rapport final multi-onglets
# ----------------------------------------------------------
# ExcelWriter permet d'écrire plusieurs onglets dans un seul fichier
with pd.ExcelWriter(RAPPORT_FINAL, engine="openpyxl") as writer:

    # Onglet 1 : Synthèse exécutive
    synthese.to_excel(writer, sheet_name="Synthèse", index=False)

    # Onglet 2 : Détail SOD
    sod.to_excel(writer, sheet_name="SOD", index=False)

    # Onglet 3 : Détail Accès Inactifs
    inactifs.to_excel(writer, sheet_name="Accès Inactifs", index=False)

    # Onglet 4 : Détail Change Management
    changes.to_excel(writer, sheet_name="Change Management", index=False)

print(f"\n✅ Rapport final exporté : {RAPPORT_FINAL}")
print(f"📋 {total_violations} violation(s) — {total_critiques} critique(s)")
print("\n" + "=" * 60)
print("   Pipeline terminé avec succès")
print("=" * 60)
# ----------------------------------------------------------
# ÉTAPE E : Mise en forme professionnelle du rapport final
# ----------------------------------------------------------
from utils.format_rapport import formater_rapport
formater_rapport(RAPPORT_FINAL)