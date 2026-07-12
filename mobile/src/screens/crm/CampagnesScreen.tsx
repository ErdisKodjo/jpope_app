/**
 * Campagnes Marketing — liste + création + activation + stats.
 */
import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, TouchableOpacity, FlatList, StyleSheet, RefreshControl, ActivityIndicator, Alert } from 'react-native';
import { CRMService } from '../../services/crm';
import { AVENSU_COLORS, SPACING, TYPOGRAPHY } from '../../theme';
import type { CampagneMarketing } from '../../types';

export function CampagnesScreen() {
  const [campagnes, setCampagnes] = useState<CampagneMarketing[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadData = useCallback(async () => {
    try {
      const result = await CRMService.listCampagnes();
      setCampagnes(result);
    } catch (e) {
      // silent
    } finally {
      setIsLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  const handleActivate = (id: string) => {
    Alert.alert('Activer la campagne ?', 'Cela générera les leads qualifiés automatiquement.', [
      { text: 'Annuler' },
      {
        text: 'Activer',
        onPress: async () => {
          try {
            const result = await CRMService.activerCampagne(id);
            Alert.alert('✅', result.message);
            loadData();
          } catch (e: any) {
            Alert.alert('Erreur', e?.response?.data?.error || e.message);
          }
        },
      },
    ]);
  };

  const renderItem = ({ item }: { item: CampagneMarketing }) => (
    <View style={styles.card}>
      <View style={styles.cardHeader}>
        <Text style={styles.cardTitle}>{item.nom}</Text>
        <View style={[styles.statutBadge, { backgroundColor: item.is_active_now ? '#D1FAE5' : '#F1F5F9' }]}>
          <Text style={[styles.statutText, { color: item.is_active_now ? '#065F46' : AVENSU_COLORS.textSecondary }]}>
            {item.statut}
          </Text>
        </View>
      </View>
      <Text style={styles.cardEtab}>{item.etablissement_nom}</Text>
      <Text style={styles.cardDates}>
        📅 {new Date(item.date_debut).toLocaleDateString('fr-FR')} → {new Date(item.date_fin).toLocaleDateString('fr-FR')}
      </Text>
      <View style={styles.statsRow}>
        <View style={styles.stat}>
          <Text style={styles.statValue}>{item.vues}</Text>
          <Text style={styles.statLabel}>Vues</Text>
        </View>
        <View style={styles.stat}>
          <Text style={styles.statValue}>{item.clics}</Text>
          <Text style={styles.statLabel}>Clics</Text>
        </View>
        <View style={styles.stat}>
          <Text style={styles.statValue}>{item.leads_generes}</Text>
          <Text style={styles.statLabel}>Leads</Text>
        </View>
        <View style={styles.stat}>
          <Text style={styles.statValue}>{item.conversions}</Text>
          <Text style={styles.statLabel}>Conv.</Text>
        </View>
      </View>
      {item.statut === 'BROUILLON' && (
        <TouchableOpacity style={styles.activateButton} onPress={() => handleActivate(item.id)}>
          <Text style={styles.activateText}>🚀 Activer la campagne</Text>
        </TouchableOpacity>
      )}
    </View>
  );

  if (isLoading) {
    return <View style={styles.center}><ActivityIndicator color={AVENSU_COLORS.primary} size="large" /></View>;
  }

  return (
    <FlatList
      data={campagnes}
      keyExtractor={item => item.id}
      renderItem={renderItem}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); loadData(); }} />}
      contentContainerStyle={{ padding: SPACING.md }}
      ItemSeparatorComponent={() => <View style={{ height: SPACING.md }} />}
      ListEmptyComponent={<Text style={styles.empty}>Aucune campagne. Créez-en une depuis le dashboard établissement.</Text>}
    />
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  card: { backgroundColor: '#FFFFFF', borderRadius: 12, padding: SPACING.lg, elevation: 1 },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  cardTitle: { ...TYPOGRAPHY.h3, color: AVENSU_COLORS.textPrimary, flex: 1 },
  statutBadge: { paddingHorizontal: SPACING.sm, paddingVertical: 2, borderRadius: 4 },
  statutText: { fontSize: 11, fontWeight: '600' },
  cardEtab: { color: AVENSU_COLORS.textSecondary, fontSize: 14, marginTop: SPACING.xs },
  cardDates: { color: AVENSU_COLORS.textTertiary, fontSize: 12, marginTop: SPACING.xs },
  statsRow: { flexDirection: 'row', gap: SPACING.sm, marginTop: SPACING.md },
  stat: { flex: 1, backgroundColor: '#F8FAFC', borderRadius: 8, padding: SPACING.sm, alignItems: 'center' },
  statValue: { fontSize: 18, fontWeight: 'bold', color: AVENSU_COLORS.textPrimary },
  statLabel: { fontSize: 11, color: AVENSU_COLORS.textTertiary, marginTop: 2 },
  activateButton: { backgroundColor: AVENSU_COLORS.primary, padding: SPACING.md, borderRadius: 8, alignItems: 'center', marginTop: SPACING.md },
  activateText: { color: '#FFFFFF', fontWeight: '600' },
  empty: { textAlign: 'center', padding: SPACING.xl, color: AVENSU_COLORS.textTertiary },
});
