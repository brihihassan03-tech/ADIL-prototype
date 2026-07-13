"""
ADIL — Prototype de démonstration (Module 3 : Calcul + Module 6 : Comparateur)
Design inspiré de l'identité visuelle actuelle de TAMWILCOM (bleu clair + bleu marine).
Lancer avec :  python -m streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from moteur_calcul import construire_montage, comparer_scenarios, cout_total_interets

st.set_page_config(page_title="ADIL — TAMWILCOM", page_icon="◆", layout="wide")

# ── Charte inspirée du site TAMWILCOM ──
BLEU = "#3B82C4"        # bleu clair dominant TAMWILCOM
BLEU_FONCE = "#1E2A44"  # bleu marine (barre de navigation)
BLEU_MOYEN = "#2E6DB4"
GRIS = "#4A4F54"
BLEU_CLAIR_BG = "#EEF4FA"
BLANC = "#FFFFFF"

# Logo stylisé (motif en losange de TAMWILCOM) recréé en SVG
LOGO_SVG = '<span style="font-size:34px;color:white;">&#9670;</span>'

st.markdown(f"""
<style>
  .stApp {{ background-color: {BLANC}; }}
  .stApp, .stApp p, .stApp label, .stApp span, .stApp div {{ color: {BLEU_FONCE}; }}
  h1, h2, h3 {{ color: {BLEU_FONCE} !important; font-weight: 700 !important; }}
  label, .stSelectbox label, .stNumberInput label, .stTextInput label, .stSlider label {{
     color: {GRIS} !important; font-weight: 600 !important; }}
  .stTabs [data-baseweb="tab-list"] {{ gap: 6px; background: {BLEU_CLAIR_BG}; padding: 6px; border-radius: 8px; }}
  .stTabs [data-baseweb="tab"] {{ font-weight: 600; }}
  .stTabs [aria-selected="true"] {{ color: {BLEU} !important; border-bottom-color: {BLEU} !important; }}
  div[data-testid="stMetricValue"] {{ color: {BLEU} !important; font-weight: 700 !important; }}
  div[data-testid="stMetricLabel"] {{ color: {GRIS} !important; }}
  section[data-testid="stSidebar"] {{ background-color: {BLEU_CLAIR_BG}; }}
  /* Menus déroulants et champs : fond clair + texte foncé lisible */
  div[data-baseweb="select"] > div {{ background-color: {BLANC} !important; color: {BLEU_FONCE} !important; border: 1px solid #C5D3E2 !important; }}
  div[data-baseweb="select"] * {{ color: {BLEU_FONCE} !important; }}
  .stNumberInput input, .stTextInput input {{ background-color: {BLANC} !important; color: {BLEU_FONCE} !important; }}
  ul[role="listbox"], ul[role="listbox"] * {{ background-color: {BLANC} !important; color: {BLEU_FONCE} !important; }}
  [data-testid="stWidgetLabel"] * {{ color: {GRIS} !important; }}
</style>

<!-- Barre de navigation façon TAMWILCOM -->
<div style="background:{BLEU_FONCE};padding:14px 26px;border-radius:8px 8px 0 0;
            display:flex;align-items:center;justify-content:space-between;">
  <div style="display:flex;align-items:center;gap:14px;">
    {LOGO_SVG}
    <div>
      <div style="color:white;font-size:22px;font-weight:bold;letter-spacing:1px;">ADIL</div>
      <div style="color:#A9C4E4;font-size:11px;letter-spacing:2px;">TAMWILCOM · AIDE À LA DÉCISION</div>
    </div>
  </div>
  <div style="color:#C9D8EC;font-size:13px;font-weight:600;">
    ACCUEIL &nbsp;·&nbsp; ANALYSE &nbsp;·&nbsp; SCÉNARIOS &nbsp;·&nbsp; RAPPORT
  </div>
</div>

<!-- Bandeau bleu façon "TAMWILCOM en chiffres" -->
<div style="background:{BLEU};padding:22px 26px;border-radius:0 0 8px 8px;margin-bottom:24px;">
  <div style="color:white;font-size:15px;font-weight:600;letter-spacing:1px;margin-bottom:4px;">
     ◆ ASSISTANT DE DÉCISION ET D'INSTRUCTION POUR LE FINANCEMENT DES PME
  </div>
  <div style="color:#E4F0FB;font-size:12px;">
     Prototype de démonstration · le calcul est déterministe (aucun chiffre n'est produit par l'IA)
  </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📊 Module 3 — Calcul financier", "⚖️ Module 6 — Comparateur de scénarios"])

# ════════════════════════════════════════════════════════════════
# MODULE 3
# ════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("Paramètres du dossier")
    c1, c2, c3 = st.columns(3)
    with c1:
        dossier = st.selectbox("Dossier", ["ALPHA (Green Invest)", "BETA (Ilayki + Damane)", "Personnalisé"])
    with c2:
        annee_depart = st.number_input("Année de départ", value=2026, step=1)
    with c3:
        periodicite = st.selectbox("Périodicité", ["Semestrielle", "Mensuelle", "Annuelle"], index=0)
    periodes_par_an = {"Semestrielle": 2, "Mensuelle": 12, "Annuelle": 1}[periodicite]

    if dossier == "ALPHA (Green Invest)":
        defaults = [
            {"nom": "Banque", "principal": 20_000_000, "taux": 6.0, "differe_mois": 12, "duree_totale_ans": 6},
            {"nom": "Green Invest", "principal": 10_000_000, "taux": 2.5, "differe_mois": 12, "duree_totale_ans": 6},
        ]
    elif dossier == "BETA (Ilayki + Damane)":
        defaults = [
            {"nom": "Banque", "principal": 4_000_000, "taux": 6.0, "differe_mois": 24, "duree_totale_ans": 7},
            {"nom": "Ilayki Invest", "principal": 4_000_000, "taux": 2.0, "differe_mois": 24, "duree_totale_ans": 7},
        ]
    else:
        defaults = [{"nom": "Tranche 1", "principal": 10_000_000, "taux": 6.0, "differe_mois": 12, "duree_totale_ans": 5}]

    st.markdown("---")
    st.subheader("Tranches du crédit conjoint")
    nb = st.number_input("Nombre de tranches", 1, 4, len(defaults))
    tranches = []
    cols = st.columns(nb)
    for i in range(nb):
        d = defaults[i] if i < len(defaults) else {"nom": f"Tranche {i+1}", "principal": 5_000_000, "taux": 6.0, "differe_mois": 12, "duree_totale_ans": 5}
        with cols[i]:
            st.markdown(f"**{d['nom']}**")
            nom = st.text_input("Nom", d["nom"], key=f"n{i}")
            principal = st.number_input("Montant (DH)", value=d["principal"], step=100_000, key=f"p{i}")
            taux = st.number_input("Taux annuel HT (%)", value=d["taux"], step=0.1, key=f"t{i}")
            differe = st.number_input("Différé (mois)", value=d["differe_mois"], step=1, key=f"g{i}")
            duree = st.number_input("Durée totale (ans)", value=d["duree_totale_ans"], step=1, key=f"d{i}")
            tranches.append({"nom": nom, "principal": principal, "taux": taux, "differe_mois": differe, "duree_totale_ans": duree})

    def to_moteur(t):
        dp = round(t["differe_mois"] / 12 * periodes_par_an)
        tp = t["duree_totale_ans"] * periodes_par_an
        return {"nom": t["nom"], "principal": t["principal"], "taux_annuel_ht": t["taux"] / 100,
                "nb_periodes_differe": dp, "nb_periodes_amort": tp - dp}

    tm = [to_moteur(t) for t in tranches]
    df = construire_montage(tm, periodes_par_an, annee_depart)
    df["annee"] = df["annee"].astype(int)

    st.markdown("---")
    st.subheader("Résultats — tableau d'amortissement annuel")
    disp = {"annee": "Année"}
    for t in tm:
        disp[f"interet_{t['nom']}"] = f"Intérêts {t['nom']}"
    disp["total_interet"] = "Total intérêts"
    disp["total_principal"] = "Principal remboursé"
    disp["encours_total_fin"] = "Encours fin"
    dd = df.rename(columns=disp)[list(disp.values())]
    st.dataframe(dd.style.format({c: "{:,.0f} DH" for c in dd.columns if c != "Année"}), use_container_width=True)

    tot = df["total_interet"].sum()
    a, b, c = st.columns(3)
    a.metric("Total intérêts sur la durée", f"{tot:,.0f} DH")
    b.metric("Principal total", f"{sum(t['principal'] for t in tranches):,.0f} DH")
    c.metric("Durée", f"{tranches[0]['duree_totale_ans']} ans")

    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["annee"], y=df["total_interet"], name="Intérêts annuels", marker_color=BLEU))
    fig.add_trace(go.Scatter(x=df["annee"], y=df["encours_total_fin"], name="Encours restant dû",
                             yaxis="y2", line=dict(color=BLEU_FONCE, width=3)))
    fig.update_layout(title="Évolution des intérêts et de l'encours",
                      yaxis=dict(title="Intérêts (DH)"),
                      yaxis2=dict(title="Encours (DH)", overlaying="y", side="right"),
                      legend=dict(orientation="h", y=1.12), height=420, plot_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("✅ Moteur validé : sur le cas réel ALPHA, il reproduit le tableau de l'Annexe 1 à 0,00 % d'écart.")

# ════════════════════════════════════════════════════════════════
# MODULE 6 — 4 SCÉNARIOS
# ════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("Comparaison des 4 scénarios de financement")
    st.caption("Reproduit la logique des scénarios S1 à S4 du mémoire (Tableau 7).")

    c1, c2 = st.columns(2)
    with c1:
        montant_total = st.number_input("Montant total du programme (DH)", value=30_000_000, step=1_000_000)
        taux_banque = st.number_input("Taux bancaire classique HT (%)", value=6.0, step=0.1)
        taux_cofi = st.number_input("Taux cofinancement TAMWILCOM HT (%)", value=2.5, step=0.1)
    with c2:
        part_cofi = st.slider("Part cofinancée par TAMWILCOM (%)", 0, 100, 33)
        differe_mois = st.number_input("Différé (mois)", value=12, step=1, key="dm_s")
        duree_ans = st.number_input("Durée totale (ans)", value=6, step=1, key="da_s")
        taux_commission = st.number_input("Commission de garantie Damane (%/an du montant garanti)", value=0.5, step=0.1,
                                          help="Laisse 0.5 % si tu ne connais pas la valeur exacte ; tu l'ajusteras.")

    quotite = 0.70
    dp = round(differe_mois / 12 * periodes_par_an)
    tp = duree_ans * periodes_par_an
    amort = tp - dp
    m_cofi = montant_total * part_cofi / 100
    m_banque_mixte = montant_total - m_cofi

    def tr(nom, principal, taux):
        return {"nom": nom, "principal": principal, "taux_annuel_ht": taux / 100,
                "nb_periodes_differe": dp, "nb_periodes_amort": amort}

    commission_s2 = (montant_total * quotite) * (taux_commission / 100) * duree_ans
    commission_s4 = (m_banque_mixte * quotite) * (taux_commission / 100) * duree_ans

    scenarios = {
        "S1 — Bancaire classique seul": [tr("banque", montant_total, taux_banque)],
        "S2 — Bancaire + garantie Damane": [tr("banque", montant_total, taux_banque)],
        f"S3 — Cofinancement ({part_cofi}%)": [tr("banque", m_banque_mixte, taux_banque), tr("cofi", m_cofi, taux_cofi)],
        "S4 — Cofinancement + garantie (combiné)": [tr("banque", m_banque_mixte, taux_banque), tr("cofi", m_cofi, taux_cofi)],
    }
    commissions = {"S1 — Bancaire classique seul": 0, "S2 — Bancaire + garantie Damane": commission_s2,
                   f"S3 — Cofinancement ({part_cofi}%)": 0, "S4 — Cofinancement + garantie (combiné)": commission_s4}

    cout_ref = cout_total_interets(scenarios["S1 — Bancaire classique seul"], periodes_par_an, annee_depart)
    rows = []
    for nom, trs in scenarios.items():
        interets = cout_total_interets(trs, periodes_par_an, annee_depart)
        commission = commissions[nom]
        cout_total = interets + commission
        ecart = (cout_total - cout_ref) / cout_ref * 100
        rows.append({"Scénario": nom, "Intérêts (DH)": round(interets), "Commission (DH)": round(commission),
                     "Coût total (DH)": round(cout_total), "Écart vs S1 (%)": round(ecart, 1)})
    comp = pd.DataFrame(rows)

    st.markdown("### Tableau comparatif des 4 scénarios")
    st.dataframe(comp.style.format({"Intérêts (DH)": "{:,.0f}", "Commission (DH)": "{:,.0f}",
                                    "Coût total (DH)": "{:,.0f}", "Écart vs S1 (%)": "{:+.1f}%"}),
                 use_container_width=True)

    couleurs = [GRIS, BLEU_MOYEN, BLEU, "#1A6B3C"]
    fig2 = go.Figure(go.Bar(x=comp["Scénario"], y=comp["Coût total (DH)"], marker_color=couleurs,
                            text=comp["Coût total (DH)"].apply(lambda v: f"{v:,.0f}"), textposition="outside"))
    fig2.update_layout(title="Coût total par scénario (intérêts + commission)", height=440,
                       yaxis_title="DH", plot_bgcolor="white", xaxis_tickangle=-12)
    st.plotly_chart(fig2, use_container_width=True)

    best = comp.loc[comp["Coût total (DH)"].idxmin()]
    st.success(f"★ Recommandation : le scénario le plus économique est « {best['Scénario']} » — "
               f"coût total {best['Coût total (DH)']:,.0f} DH ({best['Écart vs S1 (%)']:+.1f}% vs S1).")
    st.caption("⚠ La commission de garantie est estimée avec le taux paramétrable ci-dessus — remplace-le par ton taux réel.")

# ── Pied de page ──
st.markdown(f"""
<div style="margin-top:40px;padding:16px;background:{BLEU_FONCE};border-radius:8px;text-align:center;">
  <span style="color:#A9C4E4;font-size:12px;">
    ADIL — Prototype académique · Mémoire de Master · Design inspiré de l'identité TAMWILCOM ·
    Le calcul financier est déterministe, l'IA n'intervient pas sur les chiffres.
  </span>
</div>
""", unsafe_allow_html=True)
