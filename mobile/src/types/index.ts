/**
 * Types TypeScript globaux.
 */

export type UserRole = 'STUDENT' | 'COUNSELOR' | 'SCHOOL_REP' | 'PARENT' | 'ADMIN';

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  phone?: string;
  avatar?: string;
  role: UserRole;
  statut_compte: 'ACTIF' | 'INACTIF' | 'SUSPENDU' | 'EN_ATTENTE';
  is_email_verified: boolean;
  date_naissance?: string;
  profile_complete: boolean;
  created_at: string;
}

export interface AuthTokens { access: string; refresh: string; }
export interface TwoFAStatus { required: boolean; enabled: boolean; }

export interface Etablissement {
  id: string;
  nom: string;
  slug: string;
  sigle?: string;
  description: string;
  type: string;
  statut: string;
  ville: string;
  pays: string;
  logo?: string;
  banniere?: string;
  site_web?: string;
  email?: string;
  telephone?: string;
  frais_scolarite_annuel_min: number;
  frais_scolarite_annuel_max: number;
  taux_reussite: number;
  taux_insertion_professionnelle: number;
  note_globale: number;
  nombre_avis: number;
  classement_national?: number;
  is_verified: boolean;
  visite_virtuelle_url?: string;
  galerie_3d?: Array<{ titre: string; type: string; url: string; vignette?: string }>;
  video_presentation_url?: string;
  ateliers_virtuels_disponibles: boolean;
}

export interface Formation {
  id: string;
  nom: string;
  slug: string;
  description: string;
  etablissement_nom: string;
  niveau: string;
  duree_annees: number;
  modalite: string;
  cout_annuel: number;
  frais_inscription: number;
  taux_reussite: number;
  taux_insertion_6mois: number;
  places_disponibles: number;
  nombre_inscrits_annee: number;
  serie_bac_admises: string[];
  prerequis: string[];
  is_featured: boolean;
}

export interface ResultatTest {
  id: string;
  score_global: number;
  scores_par_dimension: Record<string, number>;
  code_holland?: string;
  profil_dominant: string;
  interpretation: string;
  forces: string[];
  axes_amelioration: string[];
}

export interface RapportCombine {
  etudiant: string;
  date_rapport: string;
  riasec?: {
    code_holland: string;
    score_global: number;
    scores_par_dimension: Record<string, number>;
    forces: string[];
  };
  ikigai?: {
    score_global: number;
    scores_par_dimension: Record<string, number>;
    forces: string[];
  };
  synthese: string;
  metiers_prioritaires: string[];
}

export interface SimulationAdmission {
  id: string;
  formation: { id: string; nom: string; etablissement: string };
  moyenne_saisie: number;
  serie_bac_saisie: string;
  pourcentage_chances: number;
  niveau_confiance: 'FAIBLE' | 'MOYEN' | 'ELEVE';
  explication: Record<string, any>;
  recommandations: string[];
  date_simulation: string;
}

export interface EtapeRoadmap {
  id: string;
  phase: 'COLLEGE' | 'LYCEE' | 'POST_BAC';
  categorie: string;
  titre: string;
  description: string;
  ordre: number;
  statut: 'NON_COMMENCE' | 'EN_COURS' | 'COMPLETE' | 'BLOQUE' | 'ANNULE';
  date_objectif?: string;
  date_completion?: string;
}

export interface RessourceBiblio {
  id: string;
  titre: string;
  slug: string;
  description_courte: string;
  type: string;
  matiere: string;
  niveaux: string[];
  auteur?: string;
  editeur?: string;
  annee_publication?: number;
  fichier_taille_mo: number;
  is_premium: boolean;
  is_free: boolean;
  note_moyenne: number;
  nombre_votes: number;
  nombre_telechargements: number;
  est_accessible: boolean;
}

export interface CampagneMarketing {
  id: string;
  etablissement_nom: string;
  nom: string;
  description: string;
  statut: 'BROUILLON' | 'ACTIVE' | 'PAUSE' | 'TERMINEE' | 'ANNULEE';
  date_debut: string;
  date_fin: string;
  vues: number;
  clics: number;
  leads_generes: number;
  conversions: number;
  is_active_now: boolean;
}

export interface CandidatureCRM {
  id: string;
  candidat_email: string;
  candidat_nom: string;
  etablissement_nom: string;
  formation_nom?: string;
  statut: 'RECUE' | 'EN_REVUE' | 'ACCEPTEE' | 'REFUSEE' | 'EN_ATTENTE' | 'INSCRIT' | 'DESISTE';
  date_reception: string;
  date_decision?: string;
  commentaire_etablissement?: string;
  motif_refus?: string;
}

export interface ConsentementRGPD {
  id: string;
  type: string;
  statut: 'ACTIVE' | 'RETIRE' | 'EXPIRE';
  texte_consentement: string;
  version_politique: string;
  date_consentement: string;
  date_retrait?: string;
}
