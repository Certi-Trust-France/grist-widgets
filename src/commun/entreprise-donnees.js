// Données et alertes « entreprise », partagées par les widgets fiche-entreprise et alertes-entreprises.
// Chargé en script classique : les déclarations ci-dessous sont visibles des scripts de la page.
// Lecture seule ; aucune donnée ni adresse de document ici (dépôt public).

const T = {
  ent: 'Entreprises', cyc: 'Cycles_services', tem: 'TEM_404', rev: 'Revues_de_dossier',
  pl: 'Propositions_commerciales', ch: 'Propositions_prestation', ev: 'Evaluations',
  ecr: 'Examens_ecrits', ora: 'Examens_oraux', cand: 'Candidats', qi: 'Qualification_individuelle',
  ctc: 'Contacts', site: 'Sites', prog: 'Programmes', evr: 'Evaluateurs', ql: 'Qualifications_List',
  dde: 'Demandes_devis_examens',
};
// Liens « ouvrir dans Grist » : page, section et première colonne affichée.
const LIENS = {
  ev: [48, 378, 148], ch: [75, 348, 911], tem: [77, 354, 962], rev: [68, 326, 1134], cyc: [58, 273, 932],
  pl: [82, 366, 1039], qi: [79, 363, 969], ctc: [65, 320, 108],
  fiche: [95, 409, 51],   // page « Fiche entreprise », ligne de l'entreprise
};
const ALERTE_JOURS = 183;   // échéances à moins de 6 mois

let D = null;   // tables chargées (lignes, index par id, évaluations par CH)

const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const rowsOf = t => t ? t.id.map((id, i) => Object.fromEntries(Object.keys(t).map(k => [k, t[k][i]]))) : [];
const ids = raw => Array.isArray(raw) ? raw.slice(1).filter(x => x != null && x !== '') : [];   // RefList / ChoiceList : ['L', …]
const EUR = new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 });
const NB = new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 2 });
const eur = v => (v === null || v === undefined || v === '') ? '' : EUR.format(v);
const nb = v => (v === null || v === undefined || v === '') ? '' : NB.format(v);
const DAY = 86400;
const now = () => Math.floor(Date.now() / 1000);
const fdate = s => s ? new Intl.DateTimeFormat('fr-FR', { timeZone: 'UTC' }).format(new Date(s * 1000)) : '';
const num = v => (typeof v === 'number' && isFinite(v)) ? v : 0;

async function chargerDonnees() {
  const cles = Object.keys(T);
  const tabs = await Promise.all(cles.map(k => grist.docApi.fetchTable(T[k]).catch(() => null)));
  const d = Object.fromEntries(cles.map((k, i) => [k, rowsOf(tabs[i])]));
  d.byId = Object.fromEntries(cles.map(k => [k, new Map(d[k].map(r => [r.id, r]))]));
  d.evalsParCh = new Map();
  for (const e of d.ev) if (e.PO) (d.evalsParCh.get(e.PO) || d.evalsParCh.set(e.PO, []).get(e.PO)).push(e);
  return d;
}

// ── Calculs ────────────────────────────────────────────────────────────────

const nomProg = id => D.byId.prog.get(id)?.Nom_du_programme || '';
const codeQual = id => D.byId.ql.get(id)?.Qualification_code || '';
const trig = id => D.byId.evr.get(id)?.Evaluateur_Trigramme || '';
const nomCand = c => c ? `${c.First_Name || ''} ${c.Last_Name || ''}`.trim() : '';
const typesOf = r => ids(r.Type_d_evaluation).join(', ');
const evalTerminee = e => e.Terminee === true || e.Statut === 'Terminé';
const evalActive = e => !evalTerminee(e) && e.Statut !== 'Annulé';
const chAnnulee = c => c.Statut === 'Annulée';
// Signature : rarement saisie sur les anciennes CH. Une CH facturée, présente au carnet de commandes
// (reste à facturer renseigné) ou rattachée à une évaluation est considérée comme signée.
const chSigneeExplicite = c => c.devis_signe === true || !!c.Date_de_signature || c.Statut === 'Signée';
const chSignee = c => chSigneeExplicite(c) || num(c.Facture) > 0 || typeof c.Reste_a_facturer === 'number' || !!D.evalsParCh.get(c.id)?.length;

function donnees(eid) {
  const by = (k, col) => D[k].filter(r => r[col] === eid);
  const d = {
    ent: D.byId.ent.get(eid),
    cycles: by('cyc', 'Denomination'),
    tems: by('tem', 'Entreprise'),
    pls: by('pl', 'Entreprise'),
    chs: by('ch', 'Denomination'),
    evals: by('ev', 'Entreprise'),
    cands: by('cand', 'Entreprise'),
    ecrits: by('ecr', 'Denomination'),
    oraux: by('ora', 'Denomination'),
    qis: by('qi', 'Denomination'),
    contacts: by('ctc', 'Entreprise'),
    sites: by('site', 'Entreprise'),
    ddes: by('dde', 'Entreprise'),
  };
  d.evalsParCh = D.evalsParCh;
  d.revParTem = new Map(D.rev.filter(r => r.Demande).map(r => [r.Demande, r]));
  return d;
}

function indicateurs(d) {
  const vivantes = d.chs.filter(c => !chAnnulee(c));
  const signees = vivantes.filter(chSignee);
  const t = now();
  const qualifsValides = d.qis.filter(q => q.Valide !== false && (!q.Fin_validite || q.Fin_validite >= t));
  const exAFact = [...d.ecrits.filter(x => x.a_facturer && !x.Facture), ...d.oraux.filter(x => x.a_facturer && !x.Facture2)];
  return {
    signe: signees.reduce((s, c) => s + num(c.Montant_PO), 0),
    propose: vivantes.filter(c => !chSignee(c)).reduce((s, c) => s + num(c.Montant_PO), 0),
    facture: vivantes.reduce((s, c) => s + num(c.Facture), 0),
    reste: vivantes.reduce((s, c) => s + num(c.Reste_a_facturer), 0),
    jours: signees.reduce((s, c) => s + num(c.JH_vendus), 0),
    evalsEnCours: d.evals.filter(evalActive).length,
    auditeurs: new Set(qualifsValides.map(q => q.Candidat)).size,
    exAFact: exAFact.length,
    exAFactMontant: exAFact.reduce((s, x) => s + num(x.Montant), 0),
  };
}

function alertes(d) {
  const A = [], t = now(), lim = t + ALERTE_JOURS * DAY;
  const add = (niv, cat, q, txt, date, l) => A.push({ niv, cat, q, txt, date: date || null, l: l || null, entId: d.ent?.id, ent: d.ent?.Denomination || '' });
  for (const c of d.cycles) {
    const p = nomProg(c.Programme);
    if (c.Prochaine_echeance && c.Prochaine_echeance <= lim)
      add(c.Prochaine_echeance < t ? 'ko' : 'enc', 'Cycle', p, `Prochaine échéance du cycle le ${fdate(c.Prochaine_echeance)}${c.Prochaine_echeance < t ? ' (dépassée)' : ''}`, c.Prochaine_echeance, { cle: 'cyc', id: c.id, texte: 'cycle' });
    if (c.date_fin_certification && c.date_fin_certification <= lim)
      add(c.date_fin_certification < t ? 'ko' : 'enc', 'Cycle', p, `Fin de certification le ${fdate(c.date_fin_certification)}`, c.date_fin_certification, { cle: 'cyc', id: c.id, texte: 'cycle' });
  }
  for (const c of d.chs) {
    if (chAnnulee(c) || !chSignee(c)) continue;
    const ref = (c.Propale || c.Libelle_CH || '').trim();
    // Signée sans évaluation : seulement si tout n'est pas déjà facturé (sinon cycle terminé hors Grist)
    const soldee = num(c.Facture) > 0 && !(num(c.Reste_a_facturer) > 0);
    if (!d.evalsParCh.get(c.id)?.length && !soldee)
      add('enc', 'Proposition', nomProg(c.Programme), `Proposition signée sans évaluation : ${ref} (${typesOf(c) || 'type ?'})`, c.Date_de_signature || c.Date, { cle: 'ch', id: c.id, texte: 'CH' });
    const evs = d.evalsParCh.get(c.id) || [];
    if (num(c.Reste_a_facturer) > 0 && evs.length && evs.every(evalTerminee))
      add('ko', 'Facturation', nomProg(c.Programme), `Évaluation terminée, reste à facturer ${eur(c.Reste_a_facturer)} : ${ref}`, c.date_facturation, { cle: 'ch', id: c.id, texte: 'CH' });
  }
  if (d.ent?.Examens_sans_devis) add('enc', 'Examens', 'Examens', 'Des examens n’ont ni devis ni code devis.', null, null);
  const exp = d.qis.filter(q => q.Valide !== false && q.Fin_validite && q.Fin_validite >= t && q.Fin_validite <= lim)
    .sort((a, b) => a.Fin_validite - b.Fin_validite);
  if (exp.length) add('enc', 'Auditeurs', 'Auditeurs', `${exp.length} qualification(s) expirent d’ici 6 mois : ${exp.slice(0, 6).map(q => `${nomCand(D.byId.cand.get(q.Candidat))} ${codeQual(q.Qualification)} (${fdate(q.Fin_validite)})`).join(', ')}${exp.length > 6 ? '…' : ''}`, exp[0].Fin_validite, null);
  for (const tm of d.tems) if (!d.revParTem.has(tm.id))
    add('enc', 'Demande', 'TEM-404', `Demande ${tm.NumTEM404 || tm.id} sans revue de dossier`, tm.Date_Reception, { cle: 'tem', id: tm.id, texte: 'TEM-404' });
  return A;
}

// Toutes les alertes de toutes les entreprises
function toutesAlertes() {
  return D.ent.flatMap(e => alertes(donnees(e.id)));
}
