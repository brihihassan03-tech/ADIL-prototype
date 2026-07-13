"""
ADIL — Module 3 : Moteur de calcul financier (déterministe, sans IA)
======================================================================
Reconstruit un tableau d'amortissement (méthode PMT / annuités constantes)
et le compare entre scénarios de financement.

Aucune ligne de ce fichier n'appelle un modèle de langage : tout est
calculé par des formules financières standard (cf. principe directeur
d'ADIL : "l'IA ne calcule jamais").
"""

import pandas as pd


def generer_echeancier(principal, taux_annuel_ht, periodes_par_an, nb_periodes_differe, nb_periodes_amort):
    """
    Génère un échéancier période par période pour UNE tranche de crédit.

    principal            : montant emprunté (DH)
    taux_annuel_ht       : taux nominal annuel HT (ex. 0.06 pour 6%)
    periodes_par_an      : périodicité (12=mensuel, 2=semestriel, 1=annuel)
    nb_periodes_differe   : nombre de périodes de différé (intérêts seuls, principal=0)
    nb_periodes_amort     : nombre de périodes d'amortissement (après le différé)

    Retourne une liste de dicts : période, intérêt, principal, encours_fin, phase
    """
    r = taux_annuel_ht / periodes_par_an
    n = nb_periodes_amort

    # Annuité constante (PMT) sur la phase d'amortissement
    if r == 0:
        pmt = principal / n
    else:
        pmt = principal * r / (1 - (1 + r) ** (-n))

    echeancier = []
    encours = principal

    # Phase de différé : intérêts seuls, le principal ne bouge pas
    for p in range(1, nb_periodes_differe + 1):
        interet = encours * r
        echeancier.append({
            "periode": p, "interet": interet, "principal": 0.0,
            "encours_fin": encours, "phase": "différé"
        })

    # Phase d'amortissement : annuité constante
    for p in range(1, n + 1):
        interet = encours * r
        principal_rembourse = pmt - interet
        encours -= principal_rembourse
        if abs(encours) < 1e-6:
            encours = 0.0
        echeancier.append({
            "periode": nb_periodes_differe + p, "interet": interet,
            "principal": principal_rembourse, "encours_fin": encours, "phase": "amortissement"
        })

    return echeancier


def agreger_par_annee(echeancier, periodes_par_an, annee_depart):
    """Agrège un échéancier périodique (mensuel/semestriel) en synthèse annuelle."""
    df = pd.DataFrame(echeancier)
    df["annee"] = annee_depart + (df["periode"] - 1) // periodes_par_an
    annuel = df.groupby("annee").agg(
        interet=("interet", "sum"),
        principal=("principal", "sum"),
        encours_fin=("encours_fin", "last"),
    ).reset_index()
    return annuel


def construire_montage(tranches, periodes_par_an, annee_depart):
    """
    tranches : liste de dicts {nom, principal, taux_annuel_ht, nb_periodes_differe, nb_periodes_amort}
    Combine plusieurs tranches (ex. banque + cofinancement) en un tableau annuel joint,
    au même format que l'Annexe 1 / Annexe 2 du mémoire.
    """
    tables_annuelles = {}
    for tr in tranches:
        ech = generer_echeancier(
            tr["principal"], tr["taux_annuel_ht"], periodes_par_an,
            tr["nb_periodes_differe"], tr["nb_periodes_amort"]
        )
        tables_annuelles[tr["nom"]] = agreger_par_annee(ech, periodes_par_an, annee_depart)

    # Fusion sur l'année
    annees = sorted(set(a for t in tables_annuelles.values() for a in t["annee"]))
    lignes = []
    for an in annees:
        ligne = {"annee": an}
        total_interet, total_principal, total_encours = 0.0, 0.0, 0.0
        for nom, tbl in tables_annuelles.items():
            row = tbl[tbl["annee"] == an]
            interet = float(row["interet"].iloc[0]) if len(row) else 0.0
            principal = float(row["principal"].iloc[0]) if len(row) else 0.0
            encours = float(row["encours_fin"].iloc[0]) if len(row) else 0.0
            ligne[f"interet_{nom}"] = interet
            total_interet += interet
            total_principal += principal
            total_encours += encours
        ligne["total_interet"] = total_interet
        ligne["total_principal"] = total_principal
        ligne["encours_total_fin"] = total_encours
        lignes.append(ligne)

    return pd.DataFrame(lignes)


def cout_total_interets(tranches, periodes_par_an, annee_depart):
    """Raccourci : renvoie uniquement le total des intérêts sur toute la durée."""
    df = construire_montage(tranches, periodes_par_an, annee_depart)
    return df["total_interet"].sum()


def comparer_scenarios(scenarios, periodes_par_an, annee_depart):
    """
    scenarios : dict {nom_scenario: liste_de_tranches}
    Retourne un tableau comparatif : coût total, écart en valeur et en % vs le premier scénario (référence S1).
    """
    resultats = []
    cout_reference = None
    for nom, tranches in scenarios.items():
        cout = cout_total_interets(tranches, periodes_par_an, annee_depart)
        if cout_reference is None:
            cout_reference = cout
        ecart_pct = (cout - cout_reference) / cout_reference * 100 if cout_reference else 0.0
        resultats.append({
            "scenario": nom,
            "cout_total_interets": round(cout, 0),
            "ecart_vs_S1_DH": round(cout - cout_reference, 0),
            "ecart_vs_S1_pct": round(ecart_pct, 2),
        })
    return pd.DataFrame(resultats)
