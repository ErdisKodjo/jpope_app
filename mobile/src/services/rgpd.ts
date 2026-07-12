/**
 * Service RGPD — consentements, export, droit à l'oubli, journal.
 */
import { api } from './api';
import * as FileSystem from 'expo-file-system';
import * as Sharing from 'expo-sharing';
import type { ConsentementRGPD } from '../types';

export class RGPDService {
  static async listConsentements(): Promise<ConsentementRGPD[]> {
    const result = await api.get('/consentements/');
    return result.results || result;
  }

  static async donnerConsentement(type: string, texte: string, version_politique?: string): Promise<ConsentementRGPD> {
    return api.post('/consentements/', { type, texte_consentement: texte, version_politique });
  }

  static async retirerConsentement(type: string): Promise<{ retires: number }> {
    return api.delete(`/consentements/${type}/`);
  }

  static async listDemandes(): Promise<any[]> {
    const result = await api.get('/demandes/');
    return result.results || result;
  }

  static async creerDemande(type: string, motif?: string): Promise<any> {
    return api.post('/demandes/', { type, motif });
  }

  static async exportDonnees(): Promise<void> {
    const token = await api.getAccessToken();
    const url = `${api.baseURL}/rgpd/export/`;
    const downloadRes = await FileSystem.downloadAsync(
      url,
      `${FileSystem.documentDirectory}export-rgpd.zip`,
      { headers: { Authorization: `Bearer ${token}` } }
    );
    if (downloadRes.status === 200) {
      await Sharing.shareAsync(downloadRes.uri, { mimeType: 'application/zip', dialogTitle: 'Export RGPD' });
    } else {
      throw new Error('Échec du téléchargement');
    }
  }

  static async droitOubli(): Promise<{ message: string; reference: string }> {
    return api.post('/rgpd/droit-oubli/', { confirm: 'JE_CONFIRME_EFFACEMENT_IRREVERSIBLE' });
  }

  static async getJournal(): Promise<any[]> {
    const result = await api.get('/rgpd/journal/');
    return result.results || result;
  }

  static async getPolitiques(): Promise<any[]> {
    const result = await api.get('/rgpd/politiques/');
    return result.results || result;
  }
}
