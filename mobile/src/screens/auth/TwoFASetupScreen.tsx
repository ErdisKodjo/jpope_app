/**
 * Écran TwoFASetup — génère QR code + secret, puis confirmation.
 */
import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, ActivityIndicator, ScrollView, Image } from 'react-native';
import { AuthService } from '../../services/auth';
import { AVENSU_COLORS, SPACING, TYPOGRAPHY } from '../../theme';

export function TwoFASetupScreen() {
  const [setup, setSetup] = useState<{ secret: string; uri: string; qr_svg_base64: string } | null>(null);
  const [code, setCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [backupCodes, setBackupCodes] = useState<string[]>([]);
  const [showBackupCodes, setShowBackupCodes] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const result = await AuthService.setup2FA();
        setSetup(result);
      } catch (e: any) {
        Alert.alert('Erreur', e?.response?.data?.error || e.message);
      }
    })();
  }, []);

  const handleConfirm = async () => {
    if (code.length !== 6) {
      Alert.alert('Erreur', 'Veuillez saisir le code à 6 chiffres.');
      return;
    }
    setIsLoading(true);
    try {
      const result = await AuthService.confirm2FA(code);
      setBackupCodes(result.backup_codes);
      setShowBackupCodes(true);
    } catch (e: any) {
      Alert.alert('Code invalide', e?.response?.data?.error || 'Vérifiez votre code TOTP.');
    } finally {
      setIsLoading(false);
    }
  };

  if (showBackupCodes) {
    return (
      <ScrollView contentContainerStyle={styles.container}>
        <View style={styles.card}>
          <Text style={styles.icon}>✅</Text>
          <Text style={styles.title}>2FA activé !</Text>
          <Text style={styles.subtitle}>
            Conservez ces codes de secours en lieu sûr. Ils vous permettront de récupérer
            l'accès à votre compte en cas de perte de votre téléphone.
          </Text>
          <View style={styles.codesGrid}>
            {backupCodes.map((c, i) => (
              <Text key={i} style={styles.code}>{c}</Text>
            ))}
          </View>
          <Text style={styles.warning}>
            ⚠️ Ces codes ne seront plus jamais affichés.
          </Text>
        </View>
      </ScrollView>
    );
  }

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <View style={styles.card}>
        <Text style={styles.icon}>🔐</Text>
        <Text style={styles.title}>Configurer le 2FA</Text>
        <Text style={styles.subtitle}>
          1. Installez Google Authenticator ou Authy{'\n'}
          2. Scannez ce QR code ou saisissez le secret manuellement{'\n'}
          3. Saisissez le code à 6 chiffres généré
        </Text>

        {setup ? (
          <>
            <View style={styles.qrContainer}>
              <Image
                source={{ uri: `data:image/svg;base64,${setup.qr_svg_base64}` }}
                style={styles.qr}
                resizeMode="contain"
              />
            </View>
            <Text style={styles.secretLabel}>Secret (à saisir manuellement si besoin) :</Text>
            <Text style={styles.secret}>{setup.secret}</Text>

            <Text style={styles.label}>Code TOTP</Text>
            <TextInput
              style={styles.codeInput}
              value={code}
              onChangeText={setCode}
              placeholder="000000"
              keyboardType="numeric"
              maxLength={6}
            />

            <TouchableOpacity style={styles.button} onPress={handleConfirm} disabled={isLoading}>
              {isLoading ? <ActivityIndicator color="#FFFFFF" /> : <Text style={styles.buttonText}>Activer le 2FA</Text>}
            </TouchableOpacity>
          </>
        ) : (
          <ActivityIndicator color={AVENSU_COLORS.primary} />
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flexGrow: 1, backgroundColor: '#F8FAFC', padding: SPACING.lg, justifyContent: 'center' },
  card: { backgroundColor: '#FFFFFF', borderRadius: 16, padding: SPACING.xl },
  icon: { fontSize: 48, textAlign: 'center', marginBottom: SPACING.md },
  title: { ...TYPOGRAPHY.h2, textAlign: 'center', color: AVENSU_COLORS.textPrimary },
  subtitle: { color: AVENSU_COLORS.textSecondary, textAlign: 'center', marginVertical: SPACING.md, lineHeight: 22 },
  qrContainer: { alignItems: 'center', marginVertical: SPACING.lg },
  qr: { width: 240, height: 240 },
  secretLabel: { color: AVENSU_COLORS.textSecondary, textAlign: 'center', marginTop: SPACING.md },
  secret: { fontFamily: 'monospace', textAlign: 'center', fontSize: 16, color: AVENSU_COLORS.textPrimary, marginTop: SPACING.xs },
  label: { color: AVENSU_COLORS.textSecondary, marginTop: SPACING.lg, marginBottom: SPACING.xs },
  codeInput: {
    borderWidth: 2, borderColor: AVENSU_COLORS.primary, borderRadius: 12,
    padding: SPACING.md, fontSize: 28, textAlign: 'center', letterSpacing: 8,
    backgroundColor: '#F8FAFC',
  },
  button: { backgroundColor: AVENSU_COLORS.primary, padding: SPACING.md, borderRadius: 12, alignItems: 'center', marginTop: SPACING.lg },
  buttonText: { color: '#FFFFFF', ...TYPOGRAPHY.button },
  codesGrid: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'center', marginVertical: SPACING.md, gap: SPACING.sm },
  code: { fontFamily: 'monospace', fontSize: 18, backgroundColor: '#F1F5F9', padding: SPACING.sm, borderRadius: 6, margin: 4 },
  warning: { color: AVENSU_COLORS.error, textAlign: 'center', marginTop: SPACING.md, fontWeight: '600' },
});
