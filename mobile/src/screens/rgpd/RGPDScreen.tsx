/**
 * RGPD — consentements, export, droit à l'oubli, journal.
 */
import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert, ActivityIndicator, FlatList } from 'react-native';
import { RGPDService } from '../../services/rgpd';
import { AVENSU_COLORS, SPACING, TYPOGRAPHY } from '../../theme';
import type { ConsentementRGPD } from '../../types';

export function RGPDScreen() {
  const [consentements, setConsentements] = useState<ConsentementRGPD[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const result = await RGPDService.listConsentements();
        setConsentements(result);
      } finally {
        setIsLoading(false);
      }
    })();
  }, []);

  const handleExport = async () => {
    Alert.alert('Exporter mes données ?', 'Un fichier ZIP sera téléchargé.', [
      { text: 'Annuler' },
      {
        text: 'Exporter',
        onPress: async () => {
          try {
            await RGPDService.exportDonnees();
          } catch (e: any) {
            Alert.alert('Erreur', e.message);
          }
        },
      },
    ]);
  };

  const handleDroitOubli = () => {
    Alert.alert(
      '⚠️ Droit à l\'oubli',
      'Cette action est IRRÉVERSIBLE. Toutes vos données personnelles seront anonymisées définitivement. Continuer ?',
      [
        { text: 'Annuler' },
        {
          text: 'Je confirme',
          style: 'destructive',
          onPress: async () => {
            Alert.alert('Confirmation finale', 'Saisissez "EFFACER" pour confirmer', [
              { text: 'Annuler' },
              {
                text: 'Effacer',
                style: 'destructive',
                onPress: async () => {
                  try {
                    const result = await RGPDService.droitOubli();
                    Alert.alert('✅ Compte anonymisé', result.message);
                  } catch (e: any) {
                    Alert.alert('Erreur', e?.response?.data?.error || e.message);
                  }
                },
              },
            ]);
          },
        },
      ]
    );
  };

  if (isLoading) {
    return <View style={styles.center}><ActivityIndicator color={AVENSU_COLORS.primary} size="large" /></View>;
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>🔒 Mes données RGPD</Text>
        <Text style={styles.subtitle}>Gérez vos consentements et vos droits</Text>
      </View>

      <View style={styles.actions}>
        <TouchableOpacity style={styles.actionCard} onPress={handleExport}>
          <Text style={styles.actionIcon}>📥</Text>
          <Text style={styles.actionTitle}>Exporter mes données</Text>
          <Text style={styles.actionDesc}>Télécharger un ZIP (art. 15 + 20)</Text>
        </TouchableOpacity>

        <TouchableOpacity style={[styles.actionCard, { borderColor: AVENSU_COLORS.error }]} onPress={handleDroitOubli}>
          <Text style={styles.actionIcon}>🗑️</Text>
          <Text style={[styles.actionTitle, { color: AVENSU_COLORS.error }]}>Droit à l'oubli</Text>
          <Text style={styles.actionDesc}>Anonymiser mon compte (art. 17)</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Mes consentements</Text>
        {consentements.length === 0 ? (
          <Text style={styles.empty}>Aucun consentement enregistré.</Text>
        ) : (
          consentements.map(c => (
            <View key={c.id} style={styles.consentCard}>
              <View style={styles.consentHeader}>
                <Text style={styles.consentType}>{c.type}</Text>
                <View style={[styles.consentBadge, { backgroundColor: c.statut === 'ACTIVE' ? '#D1FAE5' : '#FEE2E2' }]}>
                  <Text style={[styles.consentBadgeText, { color: c.statut === 'ACTIVE' ? '#065F46' : '#991B1B' }]}>
                    {c.statut}
                  </Text>
                </View>
              </View>
              <Text style={styles.consentDate}>
                Donné le {new Date(c.date_consentement).toLocaleDateString('fr-FR')}
              </Text>
              {c.date_retrait && (
                <Text style={styles.consentDate}>
                  Retiré le {new Date(c.date_retrait).toLocaleDateString('fr-FR')}
                </Text>
              )}
              <Text style={styles.consentVersion}>Version politique : {c.version_politique}</Text>
            </View>
          ))
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F8FAFC' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  header: { padding: SPACING.lg, backgroundColor: AVENSU_COLORS.primary },
  title: { ...TYPOGRAPHY.h2, color: '#FFFFFF' },
  subtitle: { color: '#FFFFFF', opacity: 0.85, marginTop: SPACING.xs },
  actions: { padding: SPACING.md, gap: SPACING.md },
  actionCard: { backgroundColor: '#FFFFFF', borderRadius: 12, padding: SPACING.lg, borderWidth: 1, borderColor: AVENSU_COLORS.outline },
  actionIcon: { fontSize: 36 },
  actionTitle: { ...TYPOGRAPHY.h3, marginTop: SPACING.sm, color: AVENSU_COLORS.textPrimary },
  actionDesc: { color: AVENSU_COLORS.textSecondary, fontSize: 14, marginTop: SPACING.xs },
  section: { padding: SPACING.md },
  sectionTitle: { ...TYPOGRAPHY.h3, marginBottom: SPACING.md },
  empty: { color: AVENSU_COLORS.textTertiary, textAlign: 'center', padding: SPACING.lg },
  consentCard: { backgroundColor: '#FFFFFF', borderRadius: 8, padding: SPACING.md, marginBottom: SPACING.sm },
  consentHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  consentType: { ...TYPOGRAPHY.h3, fontSize: 14, color: AVENSU_COLORS.textPrimary },
  consentBadge: { paddingHorizontal: SPACING.sm, paddingVertical: 2, borderRadius: 4 },
  consentBadgeText: { fontSize: 11, fontWeight: '600' },
  consentDate: { color: AVENSU_COLORS.textSecondary, fontSize: 12, marginTop: 4 },
  consentVersion: { color: AVENSU_COLORS.textTertiary, fontSize: 11, marginTop: 4 },
});
