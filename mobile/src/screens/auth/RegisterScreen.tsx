/**
 * Écran Register — inscription avec choix de rôle + rattachement parental pour mineurs.
 */
import React, { useState } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, ScrollView, ActivityIndicator, Modal
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useAuth } from '../../store/authStore';
import { AVENSU_COLORS, SPACING, TYPOGRAPHY } from '../../theme';
import { AuthStackParamList } from '../../navigation/AuthNavigator';
import { AuthService } from '../../services/auth';

type Nav = NativeStackNavigationProp<AuthStackParamList, 'Register'>;

const ROLES = [
  { value: 'STUDENT', label: 'Étudiant / Élève', icon: '🎓' },
  { value: 'PARENT', label: 'Parent / Tuteur', icon: '👨‍👩‍👧' },
  { value: 'COUNSELOR', label: 'Conseiller d\'orientation', icon: '🧭' },
  { value: 'SCHOOL_REP', label: 'Établissement', icon: '🏫' },
];

export function RegisterScreen() {
  const navigation = useNavigation<Nav>();
  const { register } = useAuth();
  const [step, setStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password: '',
    phone: '',
    role: 'STUDENT',
    date_naissance: '',
  });
  const [parentalModal, setParentalModal] = useState(false);
  const [parentEmail, setParentEmail] = useState('');

  const updateForm = (key: string, value: string) => setForm(f => ({ ...f, [key]: value }));

  const handleSubmit = async () => {
    if (!form.first_name || !form.last_name || !form.email || !form.password) {
      Alert.alert('Erreur', 'Veuillez remplir tous les champs obligatoires.');
      return;
    }
    if (form.password.length < 10) {
      Alert.alert('Erreur', 'Le mot de passe doit faire au moins 10 caractères.');
      return;
    }

    setIsLoading(true);
    try {
      await register(form);
      // Si mineur (né après 2008) → proposer le consentement parental
      const birthYear = parseInt(form.date_naissance.split('-')[0] || '2000', 10);
      if (form.role === 'STUDENT' && birthYear > new Date().getFullYear() - 18) {
        setParentalModal(true);
      }
    } catch (e: any) {
      Alert.alert('Inscription échouée', e?.response?.data?.error || e.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleParentalConsent = async () => {
    if (!parentEmail) {
      Alert.alert('Erreur', 'Veuillez saisir l\'email de votre parent/tuteur.');
      return;
    }
    try {
      await AuthService.requestParentalConsent({
        email_parent: parentEmail,
        relation: 'PERE',
      });
      Alert.alert(
        'Demande envoyée',
        'Un email a été envoyé à votre parent. Il disposera de 14 jours pour valider votre inscription.',
        [{ text: 'OK', onPress: () => setParentalModal(false) }]
      );
    } catch (e: any) {
      Alert.alert('Erreur', e?.response?.data?.error || e.message);
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <TouchableOpacity style={styles.backButton} onPress={() => navigation.navigate('Login')}>
        <Text style={styles.backText}>← Retour</Text>
      </TouchableOpacity>

      <View style={styles.header}>
        <Text style={styles.title}>Créer un compte</Text>
        <Text style={styles.subtitle}>Étape {step} / 2</Text>
      </View>

      {step === 1 && (
        <View style={styles.form}>
          <Text style={styles.label}>Je suis...</Text>
          <View style={styles.roleGrid}>
            {ROLES.map(r => (
              <TouchableOpacity
                key={r.value}
                style={[
                  styles.roleCard,
                  form.role === r.value && styles.roleCardSelected,
                ]}
                onPress={() => updateForm('role', r.value)}
              >
                <Text style={styles.roleIcon}>{r.icon}</Text>
                <Text style={[
                  styles.roleLabel,
                  form.role === r.value && styles.roleLabelSelected,
                ]}>{r.label}</Text>
              </TouchableOpacity>
            ))}
          </View>

          <TouchableOpacity style={styles.button} onPress={() => setStep(2)}>
            <Text style={styles.buttonText}>Continuer</Text>
          </TouchableOpacity>
        </View>
      )}

      {step === 2 && (
        <View style={styles.form}>
          <Text style={styles.label}>Prénom *</Text>
          <TextInput style={styles.input} value={form.first_name} onChangeText={v => updateForm('first_name', v)} />

          <Text style={styles.label}>Nom *</Text>
          <TextInput style={styles.input} value={form.last_name} onChangeText={v => updateForm('last_name', v)} />

          <Text style={styles.label}>Adresse e-mail *</Text>
          <TextInput
            style={styles.input}
            value={form.email}
            onChangeText={v => updateForm('email', v)}
            keyboardType="email-address"
            autoCapitalize="none"
          />

          <Text style={styles.label}>Téléphone</Text>
          <TextInput
            style={styles.input}
            value={form.phone}
            onChangeText={v => updateForm('phone', v)}
            placeholder="+228 90 00 00 00"
            keyboardType="phone-pad"
          />

          <Text style={styles.label}>Date de naissance (AAAA-MM-JJ)</Text>
          <TextInput
            style={styles.input}
            value={form.date_naissance}
            onChangeText={v => updateForm('date_naissance', v)}
            placeholder="2008-05-15"
          />

          <Text style={styles.label}>Mot de passe (min. 10 caractères) *</Text>
          <TextInput
            style={styles.input}
            value={form.password}
            onChangeText={v => updateForm('password', v)}
            secureTextEntry
          />

          <View style={styles.stepActions}>
            <TouchableOpacity style={[styles.button, styles.secondaryButton]} onPress={() => setStep(1)}>
              <Text style={[styles.buttonText, styles.secondaryButtonText]}>Retour</Text>
            </TouchableOpacity>
            <TouchableOpacity style={[styles.button, { flex: 2 }]} onPress={handleSubmit} disabled={isLoading}>
              {isLoading ? <ActivityIndicator color="#FFFFFF" /> : <Text style={styles.buttonText}>S'inscrire</Text>}
            </TouchableOpacity>
          </View>

          {form.role === 'COUNSELOR' && (
            <Text style={styles.notice}>
              ℹ️ Les conseillers doivent soumettre leurs diplômes et activer le 2FA après inscription.
            </Text>
          )}
          {form.role === 'SCHOOL_REP' && (
            <Text style={styles.notice}>
              ℹ️ Les établissements doivent soumettre leurs documents juridiques et activer le 2FA.
            </Text>
          )}
        </View>
      )}

      {/* Modal consentement parental */}
      <Modal visible={parentalModal} animationType="slide" transparent>
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Consentement parental requis</Text>
            <Text style={styles.modalText}>
              Vous êtes mineur(e). Pour finaliser votre inscription, veuillez saisir l'email
              de votre parent ou tuteur légal. Il recevra un email pour valider votre compte.
            </Text>
            <TextInput
              style={styles.input}
              value={parentEmail}
              onChangeText={setParentEmail}
              placeholder="email@parent.com"
              keyboardType="email-address"
              autoCapitalize="none"
            />
            <View style={styles.modalActions}>
              <TouchableOpacity onPress={() => setParentalModal(false)}>
                <Text style={styles.skipText}>Plus tard</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.button} onPress={handleParentalConsent}>
                <Text style={styles.buttonText}>Envoyer la demande</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flexGrow: 1, backgroundColor: '#F8FAFC', padding: SPACING.lg },
  backButton: { marginBottom: SPACING.md },
  backText: { color: AVENSU_COLORS.primary, fontSize: 16 },
  header: { marginBottom: SPACING.lg },
  title: { ...TYPOGRAPHY.h1, color: AVENSU_COLORS.textPrimary },
  subtitle: { color: AVENSU_COLORS.textSecondary, marginTop: SPACING.xs },
  form: { backgroundColor: '#FFFFFF', borderRadius: 16, padding: SPACING.lg },
  label: { color: AVENSU_COLORS.textSecondary, marginBottom: SPACING.xs, marginTop: SPACING.md, ...TYPOGRAPHY.body },
  input: {
    borderWidth: 1, borderColor: AVENSU_COLORS.outline, borderRadius: 12,
    padding: SPACING.md, fontSize: 16, backgroundColor: '#F8FAFC',
  },
  roleGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: SPACING.sm, marginTop: SPACING.sm },
  roleCard: {
    borderWidth: 2, borderColor: AVENSU_COLORS.outline, borderRadius: 12, padding: SPACING.md,
    width: '48%', alignItems: 'center', backgroundColor: '#FFFFFF',
  },
  roleCardSelected: { borderColor: AVENSU_COLORS.primary, backgroundColor: '#E0F2FE' },
  roleIcon: { fontSize: 32, marginBottom: SPACING.xs },
  roleLabel: { textAlign: 'center', color: AVENSU_COLORS.textPrimary, fontSize: 14 },
  roleLabelSelected: { color: AVENSU_COLORS.primary, fontWeight: '600' },
  button: {
    backgroundColor: AVENSU_COLORS.primary, padding: SPACING.md, borderRadius: 12,
    alignItems: 'center', marginTop: SPACING.lg,
  },
  buttonText: { color: '#FFFFFF', ...TYPOGRAPHY.button },
  secondaryButton: { backgroundColor: '#FFFFFF', borderWidth: 1, borderColor: AVENSU_COLORS.outline, flex: 1, marginRight: SPACING.sm },
  secondaryButtonText: { color: AVENSU_COLORS.textPrimary },
  stepActions: { flexDirection: 'row', alignItems: 'center' },
  notice: {
    backgroundColor: '#FEF3C7', padding: SPACING.md, borderRadius: 8,
    marginTop: SPACING.md, color: AVENSU_COLORS.accentDark, fontSize: 14,
  },
  modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'center', padding: SPACING.lg },
  modalContent: { backgroundColor: '#FFFFFF', borderRadius: 16, padding: SPACING.lg },
  modalTitle: { ...TYPOGRAPHY.h3, marginBottom: SPACING.md, color: AVENSU_COLORS.textPrimary },
  modalText: { color: AVENSU_COLORS.textSecondary, marginBottom: SPACING.md },
  modalActions: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginTop: SPACING.md },
  skipText: { color: AVENSU_COLORS.textSecondary, padding: SPACING.md },
});
