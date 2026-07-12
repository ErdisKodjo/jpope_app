/**
 * Écran TwoFAVerify — saisie du code TOTP après login (étape 2 du 2FA).
 */
import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, ActivityIndicator } from 'react-native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useAuth } from '../../store/authStore';
import { AVENSU_COLORS, SPACING, TYPOGRAPHY } from '../../theme';
import { AuthStackParamList } from '../../navigation/AuthNavigator';

type Nav = NativeStackNavigationProp<AuthStackParamList, 'TwoFAVerify'>;

export function TwoFAVerifyScreen({ route }: { route: any }) {
  const { challenge_token } = route.params;
  const { complete2FA } = useAuth();
  const [code, setCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleVerify = async () => {
    if (code.length !== 6) {
      Alert.alert('Erreur', 'Veuillez saisir le code à 6 chiffres.');
      return;
    }
    setIsLoading(true);
    try {
      await complete2FA(code);
    } catch (e: any) {
      Alert.alert('Code invalide', e?.response?.data?.error || 'Vérifiez votre code TOTP.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.icon}>🔐</Text>
        <Text style={styles.title}>Vérification 2FA</Text>
        <Text style={styles.subtitle}>
          Saisissez le code à 6 chiffres généré par votre application d'authentification
          (Google Authenticator, Authy, etc.).
        </Text>

        <TextInput
          style={styles.codeInput}
          value={code}
          onChangeText={setCode}
          placeholder="000000"
          keyboardType="numeric"
          maxLength={6}
          autoFocus
        />

        <TouchableOpacity style={styles.button} onPress={handleVerify} disabled={isLoading}>
          {isLoading ? <ActivityIndicator color="#FFFFFF" /> : <Text style={styles.buttonText}>Vérifier</Text>}
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: AVENSU_COLORS.primary, justifyContent: 'center', padding: SPACING.lg },
  card: { backgroundColor: '#FFFFFF', borderRadius: 16, padding: SPACING.xl },
  icon: { fontSize: 48, textAlign: 'center', marginBottom: SPACING.md },
  title: { ...TYPOGRAPHY.h2, textAlign: 'center', color: AVENSU_COLORS.textPrimary },
  subtitle: { color: AVENSU_COLORS.textSecondary, textAlign: 'center', marginTop: SPACING.sm, marginBottom: SPACING.lg },
  codeInput: {
    borderWidth: 2, borderColor: AVENSU_COLORS.primary, borderRadius: 12,
    padding: SPACING.lg, fontSize: 32, textAlign: 'center', letterSpacing: 8,
    backgroundColor: '#F8FAFC',
  },
  button: {
    backgroundColor: AVENSU_COLORS.primary, padding: SPACING.md, borderRadius: 12,
    alignItems: 'center', marginTop: SPACING.lg,
  },
  buttonText: { color: '#FFFFFF', ...TYPOGRAPHY.button },
});
