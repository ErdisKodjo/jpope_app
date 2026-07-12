/**
 * Service d'authentification — login, register, 2FA, OAuth, consent parental.
 */
import { api } from './api';
import type { User } from '../types';

export class AuthService {
  static async login(email: string, password: string): Promise<{
    access: string;
    refresh: string;
    user: User;
    requires_2fa?: boolean;
    challenge_token?: string;
  }> {
    const result = await api.post('/auth/login/', { email, password });
    if (result.access) {
      await api.storeTokens(result.access, result.refresh);
    }
    return result;
  }

  static async register(data: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    role: string;
    date_naissance?: string;
    phone?: string;
  }): Promise<{ user: User; access: string; refresh: string }> {
    const result = await api.post('/auth/register/', data);
    if (result.access) {
      await api.storeTokens(result.access, result.refresh);
    }
    return result;
  }

  static async logout(): Promise<void> {
    try {
      const refresh = await (await import('expo-secure-store')).getItemAsync('avensu_refresh_token');
      if (refresh) {
        await api.post('/auth/logout/', { refresh });
      }
    } finally {
      await api.clearTokens();
    }
  }

  static async getCurrentUser(): Promise<User> {
    return api.get('/me/');
  }

  static async get2FAStatus(): Promise<{ required: boolean; enabled: boolean }> {
    return api.get('/auth/2fa/status/');
  }

  static async setup2FA(): Promise<{ secret: string; uri: string; qr_svg_base64: string }> {
    return api.post('/auth/2fa/setup/');
  }

  static async confirm2FA(code: string): Promise<{ is_enabled: boolean; backup_codes: string[] }> {
    return api.post('/auth/2fa/confirm/', { code });
  }

  static async create2FAChallenge(): Promise<{ challenge_token: string; expires_at: string }> {
    return api.post('/auth/2fa/challenge/');
  }

  static async verify2FA(challenge_token: string, code: string): Promise<{ access: string; refresh: string }> {
    const result = await api.post('/auth/2fa/verify/', { challenge_token, code });
    if (result.access) {
      await api.storeTokens(result.access, result.refresh);
    }
    return result;
  }

  static async disable2FA(code: string): Promise<void> {
    await api.post('/auth/2fa/disable/', { code });
  }

  static async getSocialProviders(): Promise<Array<{ id: string; name: string; configured: boolean; login_url: string }>> {
    const result = await api.get('/auth/social/providers/');
    return result.providers;
  }

  static async getSocialLoginURL(provider: string): Promise<{ auth_url: string; callback_url: string }> {
    return api.get(`/auth/social/${provider}/login/`);
  }

  static async socialCallback(provider: string, code: string): Promise<{ access: string; refresh: string; user: any }> {
    const result = await api.post(`/auth/social/${provider}/callback/`, { code });
    if (result.access) {
      await api.storeTokens(result.access, result.refresh);
    }
    return result;
  }

  static async requestParentalConsent(data: {
    email_parent: string;
    nom_parent?: string;
    relation: string;
  }): Promise<{ id: string; statut: string; date_expiration: string }> {
    return api.post('/auth/parental-consent/request/', data);
  }

  static async validateParentalConsent(token: string, data: {
    parent_email: string;
    parent_first_name: string;
    parent_last_name: string;
    parent_password: string;
  }): Promise<{ message: string; parent_email: string; etudiant_nom: string }> {
    return api.post(`/auth/parental-consent/${token}/validate/`, data);
  }

  static async getMyChildren(): Promise<{ enfants: Array<{ etudiant_id: string; etudiant_nom: string; etudiant_email: string; relation: string; date_validation: string }> }> {
    return api.get('/auth/parental-consent/my-children/');
  }

  static async requestPasswordReset(email: string): Promise<void> {
    await api.post('/auth/password/reset/', { email });
  }

  static async changePassword(old_password: string, new_password: string): Promise<void> {
    await api.post('/me/password/', { old_password, new_password });
  }
}
