/**
 * Service Roadmap — progression, étapes, jalons.
 */
import { api } from './api';
import type { EtapeRoadmap } from '../types';

export class RoadmapService {
  static async getProgression(): Promise<{
    progression: Record<string, { total: number; completes: number; en_cours: number; bloques: number; pourcentage: number }>;
    phase_actuelle: string;
  }> {
    return api.get('/progression/');
  }

  static async initRoadmap(phase?: string): Promise<{ message: string; etape_ids: string[] }> {
    return api.post('/init/', phase ? { phase } : {});
  }

  static async getEtapes(params?: { phase?: string; statut?: string }): Promise<EtapeRoadmap[]> {
    const result = await api.get('/etapes/', { params });
    return result.results || result;
  }

  static async createEtape(data: Partial<EtapeRoadmap>): Promise<EtapeRoadmap> {
    return api.post('/etapes/', data);
  }

  static async updateEtape(id: string, data: Partial<EtapeRoadmap>): Promise<EtapeRoadmap> {
    return api.patch(`/etapes/${id}/`, data);
  }

  static async deleteEtape(id: string): Promise<void> {
    await api.delete(`/etapes/${id}/`);
  }

  static async actionEtape(id: string, action: 'complete' | 'start' | 'block' | 'reset'): Promise<EtapeRoadmap> {
    return api.post(`/etapes/${id}/${action}/`);
  }

  static async getEtapesAVenir(limit?: number): Promise<{ etapes: EtapeRoadmap[] }> {
    return api.get('/etapes-a-venir/', { params: limit ? { limit } : undefined });
  }

  static async getJalons(days?: number): Promise<any[]> {
    const result = await api.get('/jalons/', { params: days ? { days } : undefined });
    return result.results || result;
  }
}
