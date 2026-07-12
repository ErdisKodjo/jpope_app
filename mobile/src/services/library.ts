/**
 * Service Bibliothèque — catalogue, recommandations, favoris, votes.
 */
import { api } from './api';
import type { RessourceBiblio } from '../types';

export class LibraryService {
  static async listRessources(params?: {
    type?: string;
    matiere?: string;
    niveau?: string;
    premium?: 'true' | 'false';
    q?: string;
    ordering?: string;
    page?: number;
  }): Promise<{ results: RessourceBiblio[]; count: number; next?: string }> {
    return api.get('/', { params });
  }

  static async getRessource(slug: string): Promise<RessourceBiblio> {
    return api.get(`/${slug}/`);
  }

  static async getDownloadURL(slug: string): Promise<{ url: string }> {
    const token = await api.getAccessToken();
    const url = `${api.baseURL}/${slug}/download/`;
    return { url: token ? `${url}?token=${token}` : url };
  }

  static async vote(slug: string, note: number, commentaire?: string): Promise<void> {
    await api.post(`/${slug}/vote/`, { note, commentaire });
  }

  static async addFavori(slug: string, note_personnelle?: string): Promise<void> {
    await api.post(`/${slug}/favori/`, { note_personnelle });
  }

  static async removeFavori(slug: string): Promise<void> {
    await api.delete(`/${slug}/favori/`);
  }

  static async getRecommandations(): Promise<{ recommandations: RessourceBiblio[] }> {
    return api.get('/recommandations/');
  }

  static async getCategories(): Promise<any[]> {
    const result = await api.get('/categories/');
    return result.results || result;
  }

  static async getStats(): Promise<any> {
    return api.get('/stats/');
  }
}
