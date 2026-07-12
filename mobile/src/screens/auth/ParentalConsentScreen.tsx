/**
 * Écran ParentalConsent — validation du consentement parental par le parent.
 * Le parent arrive ici via le lien email (deep link).
 */
import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, ActivityIndicator, ScrollView } from 'react-native';
import { AuthService } from '../../services/auth';
import { AVENSU_COLORS, SPACING, TYPOGRAPHY } from '../../theme';

export function ParentalConsentScreen({ route }: { route: any }) {
  const token = route?.params?.token || '';
  const [isLoading, setIsLoading] = useState(false);
  const [demande, setDemande] = useState<any>(null);
  const [form, setForm] = useState({
    parent_email: '', parent_first_name: '', parent_last_name: '', parent_password: '',
  });

  const handleFetchDemande = async () => {
    if (!token) return;
    try {
      const result = await AuthService.validateParentalConsent(token, form as any);
      Alert.alert('Succès', result.message);
    } catch (e: any) {
      Alert.alert('Erreur', e?.response?.data?.error || e.message);
    }
  };

  const handleSubmit = async () => {
    if (!form.parent_email || !form.parent_first_name || !form.parent_last_name || !form.parent_password) {
      Alert.alert('Erreur', 'Tous les champs sont obligatoires.');
      return;
    }
    if (form.parent_password.length < 10) {
      Alert.alert('Erreur', 'Le mot de passe doit faire au moins 10 caractères.');
      return;
    }
    setIsLoading(true);
    try {
      const result = await AuthService.validateParentalConsent(token, form);
      Alert.alert(
        '✅ Consentement validé',
        result.message,
        [{ text: 'OK' }]
      );
    } catch (e: any) {
      Alert.alert('Erreur', e?.response?.data?.error || e.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <View style={styles.card}>
        <Text style={styles.icon}>👨‍👩‍👧</Text>
        <Text style={styles.title}>Consentement parental</Text>
        <Text style={styles.text}>
          En validant ce formulaire, vous confirmez être le parent ou tuteur légal de l'étudiant
          qui a demandé à utiliser AvenSU-Orienta. Votre compte parent sera créé et vous permettra
          de suivre son parcours d'orientation.
        </Text>

        <Text style={styles.label}>Email (doit correspondre à celui saisi par l'étudiant) *</Text>
        <TextInput
          style={styles.input}
          value={form.parent_email}
          onChangeText={v => setForm(f => ({ ...f, parent_email: v }))}
          keyboardType="email-address"
          autoCapitalize="none"
        />

        <Text style={styles.label}>Prénom *</Text>
        <TextInput
          style={styles.input}
          value={form.parent_first_name}
          onChangeText={v => setForm(f => ({ ...f, parent_first_name: v }))}
        />

        <Text style={styles.label}>Nom *</Text>
        <TextInput
          style={styles.input}
          value={form.parent_last_name}
          onChangeText={v => setForm(f => ({ ...f, parent_last_name: v }))}
        />

        <Text style={styles.label}>Mot de passe (min. 10 caractères) *</Text>
        <TextInput
          style={styles.input}
          value={form.parent_password}
          onChangeText={v => setForm(f => ({ ...f, parent_password: v }))}
          secureTextEntry
        />

        <TouchableOpacity style={styles.button} onPress={handleSubmit} disabled={isLoading}>
          {isLoading ? <ActivityIndicator color="#FFFFFF" /> : <Text style={styles.buttonText}>Valider le consentement</Text>}
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flexGrow: 1, backgroundColor: '#F8FAFC', padding: SPACING.lg, justifyContent: 'center' },
  card: { backgroundColor: '#FFFFFF', borderRadius: 16, padding: SPACING.xl },
  icon: { fontSize: 48, textAlign: 'center' },
  title: { ...TYPOGRAPHY.h2, textAlign: 'center', marginBottom: SPACING.md, color: AVENSU_COLORS.textPrimary },
  text: { color: AVENSU_COLORS.textSecondary, textAlign: 'center', marginBottom: SPACING.lg, lineHeight: 22 },
  label: { color: AVENSU_COLORS.textSecondary, marginBottom: SPACING.xs, marginTop: SPACING.md },
  input: {
    borderWidth: 1, borderColor: AVENSU_COLORS.outline, borderRadius: 12,
    padding: SPACING.md, fontSize: 16, backgroundColor: '#F8FAFC',
  },
  button: { backgroundColor: AVENSU_COLORS.primary, padding: SPACING.md, borderRadius: 12, alignItems: 'center', marginTop: SPACING.lg },
  buttonText: { color: '#FFFFFF', ...TYPOGRAPHY.button },
});
