/**
 * Écran Login — email + mot de passe + boutons OAuth Google/Apple.
 */
import React, { useState } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, ScrollView, ActivityIndicator
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import * as WebBrowser from 'expo-web-browser';
import * as Linking from 'expo-linking';
import { useAuth } from '../../store/authStore';
import { AuthService } from '../../services/auth';
import { AVENSU_COLORS, SPACING, TYPOGRAPHY } from '../../theme';
import { AuthStackParamList } from '../../navigation/AuthNavigator';

type Nav = NativeStackNavigationProp<AuthStackParamList, 'Login'>;

export function LoginScreen() {
  const navigation = useNavigation<Nav>();
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert('Erreur', 'Veuillez saisir votre email et mot de passe.');
      return;
    }
    setIsLoading(true);
    try {
      await login(email, password);
      // AuthProvider va déclencher la navigation automatiquement
    } catch (e: any) {
      const data = e?.response?.data;
      if (data?.error === 'TWO_FACTOR_REQUIRED_BUT_NOT_SETUP') {
        Alert.alert(
          '2FA requis',
          'Vous devez activer le 2FA pour vous connecter. Voulez-vous le configurer maintenant ?',
          [
            { text: 'Annuler' },
            { text: 'Configurer', onPress: () => navigation.navigate('TwoFASetup') },
          ]
        );
      } else if (data?.challenge_token) {
        navigation.navigate('TwoFAVerify', { challenge_token: data.challenge_token });
      } else {
        Alert.alert('Connexion échouée', data?.error || 'Email ou mot de passe incorrect.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleSocialLogin = async (provider: 'google' | 'apple') => {
    try {
      const { auth_url } = await AuthService.getSocialLoginURL(provider);
      const result = await WebBrowser.openAuthSessionAsync(
        auth_url,
        Linking.createURL(`/auth/${provider}/callback`)
      );
      if (result.type === 'success' && result.url) {
        const params = Linking.parse(result.url).queryParams;
        if (params.code) {
          await AuthService.socialCallback(provider, params.code as string);
        }
      }
    } catch (e: any) {
      Alert.alert('Erreur', `Connexion ${provider} échouée : ${e.message}`);
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <View style={styles.header}>
        <Text style={styles.brandName}>AvenSU-Orienta</Text>
        <Text style={styles.tagline}>Votre orientation, notre mission</Text>
      </View>

      <View style={styles.form}>
        <Text style={styles.label}>Adresse e-mail</Text>
        <TextInput
          style={styles.input}
          value={email}
          onChangeText={setEmail}
          placeholder="vous@exemple.com"
          keyboardType="email-address"
          autoCapitalize="none"
          autoComplete="email"
        />

        <Text style={styles.label}>Mot de passe</Text>
        <TextInput
          style={styles.input}
          value={password}
          onChangeText={setPassword}
          placeholder="••••••••"
          secureTextEntry
          autoComplete="password"
        />

        <TouchableOpacity onPress={() => navigation.navigate('ForgotPassword')}>
          <Text style={styles.forgotLink}>Mot de passe oublié ?</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.button} onPress={handleLogin} disabled={isLoading}>
          {isLoading ? (
            <ActivityIndicator color="#FFFFFF" />
          ) : (
            <Text style={styles.buttonText}>Se connecter</Text>
          )}
        </TouchableOpacity>

        <View style={styles.divider}>
          <View style={styles.dividerLine} />
          <Text style={styles.dividerText}>OU</Text>
          <View style={styles.dividerLine} />
        </View>

        <TouchableOpacity
          style={[styles.socialButton, { backgroundColor: '#FFFFFF', borderColor: '#E2E8F0' }]}
          onPress={() => handleSocialLogin('google')}
        >
          <Text style={styles.socialButtonText}>🔗 Continuer avec Google</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.socialButton, { backgroundColor: '#000000' }]}
          onPress={() => handleSocialLogin('apple')}
        >
          <Text style={[styles.socialButtonText, { color: '#FFFFFF' }]}> Continuer avec Apple</Text>
        </TouchableOpacity>

        <View style={styles.footer}>
          <Text style={styles.footerText}>Pas encore de compte ? </Text>
          <TouchableOpacity onPress={() => navigation.navigate('Register')}>
            <Text style={styles.footerLink}>S'inscrire</Text>
          </TouchableOpacity>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    backgroundColor: AVENSU_COLORS.primary,
    padding: SPACING.lg,
    justifyContent: 'center',
  },
  header: {
    alignItems: 'center',
    marginBottom: SPACING.xl,
  },
  brandName: {
    ...TYPOGRAPHY.h1,
    color: '#FFFFFF',
    fontSize: 32,
  },
  tagline: {
    color: '#FFFFFF',
    opacity: 0.85,
    marginTop: SPACING.xs,
  },
  form: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: SPACING.lg,
  },
  label: {
    ...TYPOGRAPHY.body,
    color: AVENSU_COLORS.textSecondary,
    marginBottom: SPACING.xs,
    marginTop: SPACING.md,
  },
  input: {
    borderWidth: 1,
    borderColor: AVENSU_COLORS.outline,
    borderRadius: 12,
    padding: SPACING.md,
    fontSize: 16,
    backgroundColor: '#F8FAFC',
  },
  forgotLink: {
    color: AVENSU_COLORS.primary,
    textAlign: 'right',
    marginTop: SPACING.xs,
  },
  button: {
    backgroundColor: AVENSU_COLORS.primary,
    padding: SPACING.md,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: SPACING.lg,
  },
  buttonText: {
    color: '#FFFFFF',
    ...TYPOGRAPHY.button,
  },
  divider: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: SPACING.lg,
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: AVENSU_COLORS.outlineVariant,
  },
  dividerText: {
    color: AVENSU_COLORS.textTertiary,
    marginHorizontal: SPACING.md,
  },
  socialButton: {
    padding: SPACING.md,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: SPACING.sm,
    borderWidth: 1,
  },
  socialButtonText: {
    ...TYPOGRAPHY.body,
    color: AVENSU_COLORS.textPrimary,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: SPACING.lg,
  },
  footerText: {
    color: AVENSU_COLORS.textSecondary,
  },
  footerLink: {
    color: AVENSU_COLORS.primary,
    fontWeight: '600',
  },
});
