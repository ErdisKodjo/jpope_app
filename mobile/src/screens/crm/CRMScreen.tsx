/**
 * CRM Établissement — pipeline candidatures Kanban.
 */
import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, ScrollView, TouchableOpacity, StyleSheet, RefreshControl, ActivityIndicator, Alert } from 'react-native';
import { CRMService } from '../../services/crm';
import { AVENSU_COLORS, SPACING, TYPOGRAPHY } from '../../theme';
import type { CandidatureCRM } from '../../types';

const STATUTS = [
  { value: 'RECUE', label: 'Reçues', color: '#3B82F6' },
  { value: 'EN_REVUE', label: 'En revue', color: '#F59E0B' },
  { value: 'EN_ATTENTE', label: 'En attente', color: '#A855F7' },
  { value: 'ACCEPTEE', label: 'Acceptées', color: '#10B981' },
  { value: 'REFUSEE', label: 'Refusées', color: '#EF4444' },
  { value: 'INSCRIT', label: 'Inscrites', color: '#059669' },
];

export function CRMScreen() {
  const [candidatures, setCandidatures] = useState<CandidatureCRM[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [stats, setStats] = useState<any>(null);

  const loadData = useCallback(async () => {
    try {
      const [cs, st] = await Promise.all([
        CRMService.listCandidatures(),
        CRMService.getPipelineStats('me'), // temp
      ]);
      setCandidatures(cs);
      setStats(st);
    } catch (e) {
      // silent
    } finally {
      setIsLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  const onRefresh = () => { setRefreshing(true); loadData(); };

  const handleAction = (c: CandidatureCRM, action: string) => {
    Alert.alert(
      `Confirmer — ${action}`,
      `${c.candidat_nom} → ${action} ?`,
      [
        { text: 'Annuler' },
        {
          text: 'Confirmer',
          onPress: async () => {
            try {
              await CRMService.actionCandidature(c.id, action);
              loadData();
            } catch (e: any) {
              Alert.alert('Erreur', e?.response?.data?.error || e.message);
            }
          },
        },
      ]
    );
  };

  if (isLoading) {
    return <View style={styles.center}><ActivityIndicator color={AVENSU_COLORS.primary} size="large" /></View>;
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      <View style={styles.header}>
        <Text style={styles.title}>CRM Candidatures</Text>
        {stats && (
          <Text style={styles.subtitle}>
            Total : {stats.total} · Inscriptions : {stats.inscrites} ({stats.taux_conversion}%)
          </Text>
        )}
      </View>

      {STATUTS.map(statut => {
        const items = candidatures.filter(c => c.statut === statut.value);
        if (items.length === 0) return null;
        return (
          <View key={statut.value} style={styles.column}>
            <View style={[styles.columnHeader, { backgroundColor: statut.color }]}>
              <Text style={styles.columnTitle}>{statut.label}</Text>
              <Text style={styles.columnCount}>{items.length}</Text>
            </View>
            {items.map(c => (
              <View key={c.id} style={styles.card}>
                <Text style={styles.cardName}>{c.candidat_nom}</Text>
                <Text style={styles.cardEmail}>{c.candidat_email}</Text>
                {c.formation_nom && <Text style={styles.cardFormation}>📚 {c.formation_nom}</Text>}
                <Text style={styles.cardDate}>📅 {new Date(c.date_reception).toLocaleDateString('fr-FR')}</Text>
                <View style={styles.cardActions}>
                  {c.statut === 'RECUE' && (
                    <TouchableOpacity style={[styles.btn, { backgroundColor: '#FEF3C7' }]} onPress={() => handleAction(c, 'revue')}>
                      <Text style={[styles.btnText, { color: '#92400E' }]}>Revoir</Text>
                    </TouchableOpacity>
                  )}
                  {(c.statut === 'RECUE' || c.statut === 'EN_REVUE') && (
                    <>
                      <TouchableOpacity style={[styles.btn, { backgroundColor: '#D1FAE5' }]} onPress={() => handleAction(c, 'accepter')}>
                        <Text style={[styles.btnText, { color: '#065F46' }]}>✓</Text>
                      </TouchableOpacity>
                      <TouchableOpacity style={[styles.btn, { backgroundColor: '#FEE2E2' }]} onPress={() => handleAction(c, 'refuser')}>
                        <Text style={[styles.btnText, { color: '#991B1B' }]}>✗</Text>
                      </TouchableOpacity>
                    </>
                  )}
                  {c.statut === 'ACCEPTEE' && (
                    <TouchableOpacity style={[styles.btn, { backgroundColor: '#D1FAE5' }]} onPress={() => handleAction(c, 'inscrire')}>
                      <Text style={[styles.btnText, { color: '#065F46' }]}>Inscrire</Text>
                    </TouchableOpacity>
                  )}
                </View>
              </View>
            ))}
          </View>
        );
      })}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F8FAFC' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  header: { padding: SPACING.lg, backgroundColor: AVENSU_COLORS.primary },
  title: { ...TYPOGRAPHY.h2, color: '#FFFFFF' },
  subtitle: { color: '#FFFFFF', opacity: 0.85, marginTop: SPACING.xs, fontSize: 14 },
  column: { margin: SPACING.md, marginTop: 0 },
  columnHeader: { flexDirection: 'row', justifyContent: 'space-between', padding: SPACING.md, borderRadius: 8 },
  columnTitle: { color: '#FFFFFF', fontWeight: '600' },
  columnCount: { color: '#FFFFFF', fontWeight: 'bold' },
  card: { backgroundColor: '#FFFFFF', borderRadius: 8, padding: SPACING.md, marginTop: SPACING.sm, elevation: 1 },
  cardName: { ...TYPOGRAPHY.h3, color: AVENSU_COLORS.textPrimary },
  cardEmail: { color: AVENSU_COLORS.textTertiary, fontSize: 12, marginTop: 2 },
  cardFormation: { color: AVENSU_COLORS.textSecondary, fontSize: 13, marginTop: SPACING.xs },
  cardDate: { color: AVENSU_COLORS.textTertiary, fontSize: 12, marginTop: SPACING.xs },
  cardActions: { flexDirection: 'row', gap: SPACING.sm, marginTop: SPACING.sm },
  btn: { paddingHorizontal: SPACING.md, paddingVertical: SPACING.xs, borderRadius: 6 },
  btnText: { fontSize: 13, fontWeight: '600' },
});
