/**
 * TwoFA Settings — activer/désactiver le 2FA.
 */
import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert, ActivityIndicator } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { AuthService } from '../../services/auth';
import { AVENSU_COLORS, SPACING, TYPOGRAPHY } from '../../theme';

type Nav = NativeStackNavigationProp<any>;

export function TwoFASettingsScreen() {
  const navigation = useNavigation<Nav>();
  const [status, setStatus] = useState<{ required: boolean; enabled: boolean } | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const s = await AuthService.get2FAStatus();
        setStatus(s);
      } finally {
        setIsLoading(false);
      }
    })();
  }, []);

  if (isLoading) {
    return <View style={styles.center}><ActivityIndicator color={AVENSU_COLORS.primary} size="large" /></View>;
  }

  return (
    <View style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.icon}>🔐</Text>
        <Text style={styles.title}>Authentification à 2 facteurs</Text>
        <Text style={styles.status}>
          Statut : <Text style={{ fontWeight: 'bold', color: status?.enabled ? AVENSU_COLORS.success : AVENSU_COLORS.warning }}>
            {status?.enabled ? 'Activé' : 'Désactivé'}
          </Text>
        </Text>
        {status?.required && !status?.enabled && (
          <Text style={styles.warning}>
            ⚠️ Le 2FA est obligatoire pour votre compte. Activez-le pour accéder à toutes les fonctionnalités.
          </Text>
        )}
        <TouchableOpacity
          style={[styles.button, { backgroundColor: status?.enabled ? AVENSU_COLORS.error : AVENSU_COLORS.primary }]}
          onPress={() => {
            if (status?.enabled) {
              Alert.prompt('Désactiver le 2FA', 'Saisissez un code TOTP pour confirmer :', async (code) => {
                try {
                  await AuthService.disable2FA(code);
                  Alert.alert('✅ 2FA désactivé');
                  navigation.goBack();
                } catch (e: any) {
                  Alert.alert('Erreur', e?.response?.data?.error || e.message);
                }
              });
            } else {
              navigation.navigate('TwoFASetup' as any);
            }
          }}
        >
          <Text style={styles.buttonText}>
            {status?.enabled ? 'Désactiver le 2FA' : 'Configurer le 2FA'}
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F8FAFC', padding: SPACING.lg, justifyContent: 'center' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  card: { backgroundColor: '#FFFFFF', borderRadius: 16, padding: SPACING.xl, alignItems: 'center' },
  icon: { fontSize: 64 },
  title: { ...TYPOGRAPHY.h2, color: AVENSU_COLORS.textPrimary, marginTop: SPACING.md, textAlign: 'center' },
  status: { color: AVENSU_COLORS.textSecondary, marginTop: SPACING.sm },
  warning: { color: AVENSU_COLORS.warning, textAlign: 'center', marginTop: SPACING.md, lineHeight: 20 },
  button: { padding: SPACING.md, borderRadius: 12, alignItems: 'center', marginTop: SPACING.lg, width: '100%' },
  buttonText: { color: '#FFFFFF', ...TYPOGRAPHY.button },
});
