/**
 * Service Orientation — tests RIASEC, Ikigai, rapport combiné.
 */
import { api } from './api';
import type { ResultatTest, RapportCombine } from '../types';

export class OrientationService {
  static async listTests(): Promise<any[]> {
    const result = await api.get('/tests/');
    return result.results || result;
  }

  static async startTest(testId: string): Promise<{ reponse_id: string; test: any }> {
    return api.post('/test/start/', { test_id: testId });
  }

  static async saveAnswer(reponseId: string, data: { question_id: string; choice_id?: string; valeur_echelle?: number; texte?: string }): Promise<void> {
    await api.post('/test/save-answer/', { reponse_id: reponseId, ...data });
  }

  static async submitTest(reponseId: string): Promise<ResultatTest> {
    return api.post('/test/submit/', { reponse_id: reponseId });
  }

  static async getResultats(): Promise<ResultatTest[]> {
    const result = await api.get('/resultats/');
    return result.results || result;
  }

  static async getRapportCombine(): Promise<RapportCombine> {
    return api.get('/rapport-combine/');
  }

  static async listTestsIkigai(): Promise<any[]> {
    const result = await api.get('/ikigai/tests/');
    return result.tests;
  }

  static async getResultatIkigai(): Promise<ResultatTest> {
    return api.get('/ikigai/resultat/');
  }

  static async getRecommandations(): Promise<any[]> {
    const result = await api.get('/recommandations/');
    return result.results || result;
  }
}
