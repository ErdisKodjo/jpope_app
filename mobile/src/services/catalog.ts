/**
 * Service Catalog — établissements, formations, simulateur admission, visites 3D.
 */
import { api } from './api';
import type { Etablissement, Formation, SimulationAdmission } from '../types';

export class CatalogService {
  static async listEtablissements(params?: {
    ville?: string;
    type?: string;
    search?: string;
    page?: number;
  }): Promise<{ results: Etablissement[]; count: number; next?: string }> {
    return api.get('/etablissements/', { params });
  }

  static async getEtablissement(id: string): Promise<Etablissement> {
    return api.get(`/etablissements/${id}/`);
  }

  static async getVisite3D(etablissementId: string): Promise<{
    etablissement: { id: string; nom: string };
    visite_virtuelle_url: string;
    galerie_3d: any[];
    video_presentation_url: string;
    ateliers_virtuels_disponibles: boolean;
  }> {
    return api.get(`/etablissements/${etablissementId}/visite-3d/`);
  }

  static async listFormations(params?: {
    etablissement?: string;
    niveau?: string;
    domaine?: string;
    search?: string;
    page?: number;
  }): Promise<{ results: Formation[]; count: number }> {
    return api.get('/formations/', { params });
  }

  static async getFormation(id: string): Promise<Formation> {
    return api.get(`/formations/${id}/`);
  }

  static async simulerAdmission(data: {
    formation_id: string;
    moyenne: number;
    serie_bac?: string;
  }): Promise<SimulationAdmission> {
    return api.post('/simulateur/admission/', data);
  }

  static async getHistoriqueSimulations(): Promise<{ simulations: SimulationAdmission[] }> {
    return api.get('/simulateur/historique/');
  }
}
