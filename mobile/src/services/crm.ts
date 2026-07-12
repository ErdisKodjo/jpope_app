/**
 * Service CRM/Marketing — campagnes, leads, candidatures, pipeline.
 */
import { api } from './api';
import type { CampagneMarketing, CandidatureCRM } from '../types';

export class CRMService {
  static async listCampagnes(etablissementId?: string): Promise<CampagneMarketing[]> {
    const params = etablissementId ? { etablissement: etablissementId } : undefined;
    const result = await api.get('/campagnes/', { params });
    return result.results || result;
  }

  static async createCampagne(data: Partial<CampagneMarketing>): Promise<CampagneMarketing> {
    return api.post('/campagnes/', data);
  }

  static async activerCampagne(id: string): Promise<{ message: string; leads_generes: number }> {
    return api.post(`/campagnes/${id}/activer/`);
  }

  static async getCampagneStats(id: string): Promise<any> {
    return api.get(`/campagnes/${id}/stats/`);
  }

  static async listLeads(campagneId?: string): Promise<any[]> {
    const params = campagneId ? { campagne: campagneId } : undefined;
    const result = await api.get('/leads/', { params });
    return result.results || result;
  }

  static async facturerLead(id: string): Promise<{ message: string; montant: number }> {
    return api.post(`/leads/${id}/facturer/`);
  }

  static async listCandidatures(params?: { etablissement?: string; statut?: string }): Promise<CandidatureCRM[]> {
    const result = await api.get('/candidatures/', { params });
    return result.results || result;
  }

  static async actionCandidature(id: string, action: string, data?: { commentaire?: string; motif_refus?: string }): Promise<CandidatureCRM> {
    return api.post(`/candidatures/${id}/${action}/`, data || {});
  }

  static async syncExterne(id: string): Promise<{ synced: boolean; last_sync_at: string }> {
    return api.post(`/candidatures/${id}/sync/`);
  }

  static async getPipelineStats(etablissementId: string): Promise<any> {
    return api.get('/pipeline/stats/', { params: { etablissement: etablissementId } });
  }
}
