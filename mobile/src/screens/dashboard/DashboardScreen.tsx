/**
 * Dashboard étudiant — roadmap, étapes à venir, jalons, recommandations.
 */
import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, ScrollView, StyleSheet, RefreshControl, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useAuth } from '../../store/authStore';
import { RoadmapService } from '../../services/roadmap';
import { AVENSU_COLORS, SPACING, TYPOGRAPHY } from '../../theme';

type Nav = NativeStackNavigationProp<any>;

export function DashboardScreen() {
  const { user } = useAuth();
  const navigation = useNavigation<Nav>();
  const [progression, setProgression] = useState<any>(null);
  const [etapesAVenir, setEtapesAVenir] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadData = useCallback(async () => {
    try {
      const [prog, avenirs] = await Promise.all([
        RoadmapService.getProgression(),
        RoadmapService.getEtapesAVenir(5),
      ]);
      setProgression(prog);
      setEtapesAVenir(avenirs.etapes);
    } catch (e) {
      // ignore — offline
    } finally {
      setIsLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  const onRefresh = () => { setRefreshing(true); loadData(); };

  if (isLoading) {
    return <View style={styles.center}><ActivityIndicator color={AVENSU_COLORS.primary} size="large" /></View>;
  }

  const phase = progression?.phase_actuelle || 'LYCEE';
  const phaseProg = progression?.progression?.[phase] || { pourcentage: 0, completes: 0, total: 0 };

  return (
    <ScrollView style={styles.container} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}>
      <View style={styles.header}>
        <Text style={styles.greeting}>Bonjour {user?.first_name} 👋</Text>
        <Text style={styles.subtitle}>Voici votre parcours d'orientation</Text>
      </View>

      {/* Carte progression roadmap */}
      <TouchableOpacity
        style={styles.card}
        onPress={() => navigation.navigate('Roadmap')}
      >
        <Text style={styles.cardTitle}>📊 Progression roadmap</Text>
        <Text style={styles.cardPhase}>Phase actuelle : {phase}</Text>
        <View style={styles.progressBar}>
          <View style={[styles.progressFill, { width: `${phaseProg.pourcentage}%` }]} />
        </View>
        <Text style={styles.progressText}>
          {phaseProg.completes} / {phaseProg.total} étapes ({phaseProg.pourcentage}%)
        </Text>
      </TouchableOpacity>

      {/* Raccourcis */}
      <View style={styles.shortcutGrid}>
        <TouchableOpacity
          style={styles.shortcut}
          onPress={() => navigation.navigate('OrientationHome' as any)}
        >
          <Text style={styles.shortcutIcon}>🧭</Text>
          <Text style={styles.shortcutLabel}>Tests d'orientation</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={styles.shortcut}
          onPress={() => navigation.navigate('CatalogHome' as any)}
        >
          <Text style={styles.shortcutIcon}>🏫</Text>
          <Text style={styles.shortcutLabel}>Catalogue écoles</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={styles.shortcut}
          onPress={() => navigation.navigate('LibraryHome' as any)}
        >
          <Text style={styles.shortcutIcon}>📚</Text>
          <Text style={styles.shortcutLabel}>Bibliothèque</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={styles.shortcut}
          onPress={() => navigation.navigate('Chatbot' as any)}
        >
          <Text style={styles.shortcutIcon}>🤖</Text>
          <Text style={styles.shortcutLabel}>AvenBot IA</Text>
        </TouchableOpacity>
      </View>

      {/* Étapes à venir */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Étapes à venir</Text>
        {etapesAVenir.length === 0 ? (
          <Text style={styles.emptyText}>Aucune étape en attente. 🎉</Text>
        ) : (
          etapesAVenir.map(e => (
            <View key={e.id} style={styles.etapeItem}>
              <View style={[styles.etapeBadge, { backgroundColor: e.statut === 'EN_COURS' ? '#FEF3C7' : '#E0F2FE' }]}>
                <Text style={styles.etapeOrder}>{e.ordre}</Text>
              </View>
              <View style={{ flex: 1 }}>
                <Text style={styles.etapeTitle}>{e.titre}</Text>
                <Text style={styles.etapeCategory}>{e.categorie}</Text>
              </View>
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
  greeting: { ...TYPOGRAPHY.h2, color: '#FFFFFF' },
  subtitle: { color: '#FFFFFF', opacity: 0.85, marginTop: SPACING.xs },
  card: { backgroundColor: '#FFFFFF', margin: SPACING.md, padding: SPACING.lg, borderRadius: 12, elevation: 2 },
  cardTitle: { ...TYPOGRAPHY.h3, marginBottom: SPACING.sm },
  cardPhase: { color: AVENSU_COLORS.textSecondary, marginBottom: SPACING.md },
  progressBar: { height: 8, backgroundColor: '#E2E8F0', borderRadius: 4, overflow: 'hidden' },
  progressFill: { height: '100%', backgroundColor: AVENSU_COLORS.primary },
  progressText: { color: AVENSU_COLORS.textSecondary, marginTop: SPACING.xs, fontSize: 14 },
  shortcutGrid: { flexDirection: 'row', flexWrap: 'wrap', padding: SPACING.md, gap: SPACING.md },
  shortcut: { width: '47%', backgroundColor: '#FFFFFF', borderRadius: 12, padding: SPACING.lg, alignItems: 'center', elevation: 1 },
  shortcutIcon: { fontSize: 36, marginBottom: SPACING.xs },
  shortcutLabel: { color: AVENSU_COLORS.textPrimary, textAlign: 'center', fontSize: 14 },
  section: { padding: SPACING.md },
  sectionTitle: { ...TYPOGRAPHY.h3, marginBottom: SPACING.md },
  emptyText: { color: AVENSU_COLORS.textTertiary, textAlign: 'center', padding: SPACING.lg },
  etapeItem: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#FFFFFF', padding: SPACING.md, borderRadius: 8, marginBottom: SPACING.sm },
  etapeBadge: { width: 40, height: 40, borderRadius: 20, justifyContent: 'center', alignItems: 'center', marginRight: SPACING.md },
  etapeOrder: { fontSize: 18, fontWeight: 'bold', color: AVENSU_COLORS.textPrimary },
  etapeTitle: { color: AVENSU_COLORS.textPrimary, fontSize: 16, fontWeight: '500' },
  etapeCategory: { color: AVENSU_COLORS.textTertiary, fontSize: 12, marginTop: 2 },
});
