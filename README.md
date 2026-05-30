# 🔍 ITGC Audit Tool

Outil Python d'automatisation des contrôles IT Généraux (ITGC)  
**Framework : COBIT 2019 | SOX Section 404 | COSO**

---

##  Objectif

Automatiser la détection de violations ITGC sur les systèmes d'information,  
généralement effectuée manuellement par les auditeurs IT.  
Ce pipeline remplace des heures de travail Excel par une exécution en quelques secondes.

---

##  Contrôles implémentés

| # | Test | Framework | Règle métier |
|---|------|-----------|--------------|
| 1 | **Séparation des tâches (SOD)** | COBIT DSS05.04 | Un utilisateur ne peut pas cumuler SAISIE + VALIDATION |
| 2 | **Accès Inactifs** | COBIT DSS05.04 / APO09 | Compte désactivé ou sans connexion >90j avec rôle sensible |
| 3 | **Change Management** | COBIT BAI06 / BAI07 | Modification PROD sans approbation ou hors heures ouvrées |

---

##  Résultats sur données de test

| Test | Violations | Critiques |
|------|-----------|-----------|
| SOD | 2 | 1 |
| Accès Inactifs | 2 | 2 |
| Change Management | 4 | 3 |
| **TOTAL** | **8** | **6** |

---

##  Structure du projet
itgc-audit-tool/
├── data/
│   ├── user_access.csv        # Droits d'accès utilisateurs
│   └── change_log.csv         # Journal des modifications système
├── controls/
│   ├── test_sod.py            # Test SOD
│   ├── test_access_inactif.py # Test accès inactifs
│   └── test_change_mgmt.py    # Test change management
├── utils/
│   └── format_rapport.py      # Mise en forme Excel
├── reports/                   # Rapports générés (gitignore)
├── main.py                    # Pipeline principal
└── README.md

---

##  Lancement rapide

**1. Cloner le projet**
```bash
git clone https://github.com/chanamohcine/itgc-audit-tool.git
cd itgc-audit-tool
```

**2. Installer les dépendances**
```bash
pip install pandas openpyxl
```

**3. Lancer le pipeline complet**
```bash
python main.py
```

Les rapports sont générés dans `reports/RAPPORT_AUDIT_ITGC_FINAL.xlsx`

---

##  Stack technique

| Outil | Usage |
|-------|-------|
| **Python 3.x** | Pipeline principal |
| **pandas** | Manipulation et analyse des données |
| **openpyxl** | Génération et mise en forme Excel |

---

##  Format des données d'entrée

### user_access.csv
| Colonne | Description |
|---------|-------------|
| user_id | Identifiant unique utilisateur |
| user_name | Nom complet |
| department | Département |
| role | Rôle / droit d'accès |
| status | ACTIF ou INACTIF |
| last_login | Date dernière connexion (YYYY-MM-DD) |

### change_log.csv
| Colonne | Description |
|---------|-------------|
| change_id | Identifiant du changement |
| user_id | Auteur du changement |
| type_changement | MODIFICATION_CODE / DEPLOIEMENT / MODIFICATION_CONFIG |
| environnement | PRODUCTION ou TEST |
| statut_ticket | APPROUVE / NON_APPROUVE / EN_ATTENTE |
| date_changement | Date (YYYY-MM-DD) |
| heure_changement | Heure (HH:MM) |

---

##  Évolutions prévues

- [ ] Test n°4 : Audit Log — connexions hors heures ouvrées
- [ ] Connexion directe base de données MySQL
- [ ] Dashboard Power BI connecté aux rapports
- [ ] Scoring de risque global par utilisateur

---

##  Auteur

**Mohcine Chana**  
MSc2 Contrôle de Gestion & Audit — INSEEC Bordeaux  
[LinkedIn](https://linkedin.com/in/mohcine-chana)