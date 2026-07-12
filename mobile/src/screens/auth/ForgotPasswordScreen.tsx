/**
 * Écran ForgotPassword — demande de reset par email.
 */
import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, ActivityIndicator } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { AuthService } from '../../services/auth';
import { AVENSU_COLORS, SPACING, TYPOGRAPHY } from '../../theme';
import { AuthStackParamList } from '../../navigation/AuthNavigator';

type Nav = NativeStackNavigationProp<AuthStackParamList, 'ForgotPassword'>;

export function ForgotPasswordScreen() {
  const navigation = useNavigation<Nav>();
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sent, setSent] = useState(false);

  const handleSubmit = async () => {
    if (!email) return Alert.alert('Erreur', 'Saisissez votre email.');
    setIsLoading(true);
    try {
      await AuthService.requestPasswordReset(email);
      setSent(true);
    } catch (e: any) {
      Alert.alert('Erreur', e.message);
    } finally {
      setIsLoading(false);
    }
  };

  if (sent) {
    return (
      <View style={styles.container}>
        <View style={styles.card}>
          <Text style={styles.icon}>✉️</Text>
          <Text style={styles.title}>Email envoyé</Text>
          <Text style={styles.text}>
            Si un compte existe avec l'adresse {email}, vous recevrez un email avec les instructions
            de réinitialisation.
          </Text>
          <TouchableOpacity style={styles.button} onPress={() => navigation.navigate('Login')}>
            <Text style={styles.buttonText}>Retour à la connexion</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.title}>Mot de passe oublié</Text>
        <Text style={styles.text}>Saisissez votre email. Vous recevrez un lien de réinitialisation.</Text>
        <TextInput
          style={styles.input}
          value={email}
          onChangeText={setEmail}
          placeholder="vous@exemple.com"
          keyboardType="email-address"
          autoCapitalize="none"
        />
        <TouchableOpacity style={styles.button} onPress={handleSubmit} disabled={isLoading}>
          {isLoading ? <ActivityIndicator color="#FFFFFF" /> : <Text style={styles.buttonText}>Envoyer</Text>}
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: AVENSU_COLORS.primary, justifyContent: 'center', padding: SPACING.lg },
  card: { backgroundColor: '#FFFFFF', borderRadius: 16, padding: SPACING.xl },
  icon: { fontSize: 48, textAlign: 'center' },
  title: { ...TYPOGRAPHY.h2, textAlign: 'center', marginBottom: SPACING.md, color: AVENSU_COLORS.textPrimary },
  text: { color: AVENSU_COLORS.textSecondary, textAlign: 'center', marginBottom: SPACING.lg },
  input: {
    borderWidth: 1, borderColor: AVENSU_COLORS.outline, borderRadius: 12,
    padding: SPACING.md, fontSize: 16, backgroundColor: '#F8FAFC', marginBottom: SPACING.md,
  },
  button: { backgroundColor: AVENSU_COLORS.primary, padding: SPACING.md, borderRadius: 12, alignItems: 'center' },
  buttonText: { color: '#FFFFFF', ...TYPOGRAPHY.button },
});
