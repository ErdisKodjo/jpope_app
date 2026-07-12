/**
 * Roadmap — progression 3 phases + étapes + actions.
 */
import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, RefreshControl, ActivityIndicator, Alert } from 'react-native';
import { RoadmapService } from '../../services/roadmap';
import { AVENSU_COLORS, SPACING, TYPOGRAPHY } from '../../theme';
import type { EtapeRoadmap } from '../../types';

const PHASES = [
  { value: 'COLLEGE', label: 'Collège', icon: '🎒', color: '#10B981' },
  { value: 'LYCEE', label: 'Lycée', icon: '📘', color: '#0EA5E9' },
  { value: 'POST_BAC', label: 'Post-Bac', icon: '🎓', color: '#F59E0B' },
];

const STATUT_COLORS: Record<string, string> = {
  NON_COMMENCE: '#94A3B8',
  EN_COURS: '#F59E0B',
  COMPLETE: '#10B981',
  BLOQUE: '#EF4444',
  ANNULE: '#6B7280',
};

export function RoadmapScreen() {
  const [phase, setPhase] = useState('LYCEE');
  const [etapes, setEtapes] = useState<EtapeRoadmap[]>([]);
  const [progression, setProgression] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadData = useCallback(async () => {
    try {
      const [p, e] = await Promise.all([
        RoadmapService.getProgression(),
        RoadmapService.getEtapes({ phase }),
      ]);
      setProgression(p);
      setEtapes(e);
    } catch (err) {
      // Init roadmap if empty
      try {
        await RoadmapService.initRoadmap(phase);
        const [p, e] = await Promise.all([
          RoadmapService.getProgression(),
          RoadmapService.getEtapes({ phase }),
        ]);
        setProgression(p);
        setEtapes(e);
      } catch (e) {
        // silent
      }
    } finally {
      setIsLoading(false);
      setRefreshing(false);
    }
  }, [phase]);

  useEffect(() => { loadData(); }, [loadData]);

  const onRefresh = () => { setRefreshing(true); loadData(); };

  const handleAction = async (etape: EtapeRoadmap, action: 'complete' | 'start' | 'block' | 'reset') => {
    try {
      await RoadmapService.actionEtape(etape.id, action);
      loadData();
    } catch (e: any) {
      Alert.alert('Erreur', e?.response?.data?.error || e.message);
    }
  };

  const phaseProg = progression?.progression?.[phase] || { pourcentage: 0, completes: 0, total: 0 };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      {/* Tabs phases */}
      <View style={styles.phaseTabs}>
        {PHASES.map(p => (
          <TouchableOpacity
            key={p.value}
            style={[styles.phaseTab, phase === p.value && { backgroundColor: p.color }]}
            onPress={() => setPhase(p.value)}
          >
            <Text style={styles.phaseIcon}>{p.icon}</Text>
            <Text style={[styles.phaseLabel, phase === p.value && styles.phaseLabelActive]}>{p.label}</Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Progression */}
      <View style={styles.progressCard}>
        <Text style={styles.progressLabel}>Progression {phase}</Text>
        <View style={styles.progressBar}>
          <View style={[styles.progressFill, { width: `${phaseProg.pourcentage}%`, backgroundColor: PHASES.find(p => p.value === phase)?.color }]} />
        </View>
        <Text style={styles.progressText}>{phaseProg.completes} / {phaseProg.total} ({phaseProg.pourcentage}%)</Text>
      </View>

      {/* Étapes */}
      {isLoading ? (
        <ActivityIndicator color={AVENSU_COLORS.primary} size="large" style={{ marginTop: SPACING.xl }} />
      ) : (
        etapes.map(e => (
          <View key={e.id} style={styles.etapeCard}>
            <View style={styles.etapeHeader}>
              <View style={[styles.etapeStatus, { backgroundColor: STATUT_COLORS[e.statut] }]} />
              <Text style={styles.etapeTitle}>{e.titre}</Text>
            </View>
            <Text style={styles.etapeDesc}>{e.description}</Text>
            <View style={styles.etapeMeta}>
              <Text style={styles.etapeCategory}>📌 {e.categorie}</Text>
              {e.date_objectif && (
                <Text style={styles.etapeDate}>🎯 {new Date(e.date_objectif).toLocaleDateString('fr-FR')}</Text>
              )}
            </View>
            <View style={styles.etapeActions}>
              {e.statut !== 'COMPLETE' && (
                <TouchableOpacity
                  style={[styles.actionButton, { backgroundColor: '#D1FAE5' }]}
                  onPress={() => handleAction(e, 'complete')}
                >
                  <Text style={[styles.actionText, { color: '#065F46' }]}>✓ Compléter</Text>
                </TouchableOpacity>
              )}
              {e.statut === 'NON_COMMENCE' && (
                <TouchableOpacity
                  style={[styles.actionButton, { backgroundColor: '#FEF3C7' }]}
                  onPress={() => handleAction(e, 'start')}
                >
                  <Text style={[styles.actionText, { color: '#92400E' }]}>▶ Commencer</Text>
                </TouchableOpacity>
              )}
              {e.statut !== 'NON_COMMENCE' && e.statut !== 'COMPLETE' && (
                <TouchableOpacity
                  style={[styles.actionButton, { backgroundColor: '#F1F5F9' }]}
                  onPress={() => handleAction(e, 'reset')}
                >
                  <Text style={[styles.actionText, { color: AVENSU_COLORS.textSecondary }]}>↻ Reset</Text>
                </TouchableOpacity>
              )}
            </View>
          </View>
        ))
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F8FAFC' },
  phaseTabs: { flexDirection: 'row', backgroundColor: '#FFFFFF', padding: SPACING.sm, gap: SPACING.sm },
  phaseTab: { flex: 1, padding: SPACING.md, borderRadius: 12, alignItems: 'center', backgroundColor: '#F1F5F9' },
  phaseIcon: { fontSize: 24 },
  phaseLabel: { color: AVENSU_COLORS.textSecondary, fontSize: 12, marginTop: 2 },
  phaseLabelActive: { color: '#FFFFFF', fontWeight: '600' },
  progressCard: { backgroundColor: '#FFFFFF', margin: SPACING.md, padding: SPACING.lg, borderRadius: 12 },
  progressLabel: { ...TYPOGRAPHY.h3, marginBottom: SPACING.md },
  progressBar: { height: 10, backgroundColor: '#E2E8F0', borderRadius: 5, overflow: 'hidden' },
  progressFill: { height: '100%' },
  progressText: { color: AVENSU_COLORS.textSecondary, marginTop: SPACING.xs, fontSize: 14, textAlign: 'center' },
  etapeCard: { backgroundColor: '#FFFFFF', margin: SPACING.md, marginTop: 0, padding: SPACING.lg, borderRadius: 12 },
  etapeHeader: { flexDirection: 'row', alignItems: 'center' },
  etapeStatus: { width: 12, height: 12, borderRadius: 6, marginRight: SPACING.sm },
  etapeTitle: { ...TYPOGRAPHY.h3, color: AVENSU_COLORS.textPrimary, flex: 1 },
  etapeDesc: { color: AVENSU_COLORS.textSecondary, fontSize: 14, marginTop: SPACING.xs, lineHeight: 20 },
  etapeMeta: { flexDirection: 'row', justifyContent: 'space-between', marginTop: SPACING.sm },
  etapeCategory: { color: AVENSU_COLORS.textTertiary, fontSize: 12 },
  etapeDate: { color: AVENSU_COLORS.textTertiary, fontSize: 12 },
  etapeActions: { flexDirection: 'row', gap: SPACING.sm, marginTop: SPACING.md, flexWrap: 'wrap' },
  actionButton: { paddingHorizontal: SPACING.md, paddingVertical: SPACING.sm, borderRadius: 8 },
  actionText: { fontSize: 13, fontWeight: '600' },
});
