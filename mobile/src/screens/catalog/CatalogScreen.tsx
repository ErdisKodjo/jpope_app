/**
 * Catalogue — liste établissements avec recherche + filtres.
 */
import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, TextInput, TouchableOpacity, FlatList, StyleSheet, RefreshControl, ActivityIndicator } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { CatalogService } from '../../services/catalog';
import { AVENSU_COLORS, SPACING, TYPOGRAPHY } from '../../theme';
import type { Etablissement } from '../../types';

type Nav = NativeStackNavigationProp<any>;

export function CatalogScreen() {
  const navigation = useNavigation<Nav>();
  const [etablissements, setEtablissements] = useState<Etablissement[]>([]);
  const [search, setSearch] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadData = useCallback(async () => {
    try {
      const result = await CatalogService.listEtablissements({ search });
      setEtablissements(result.results);
    } catch (e) {
      // ignore
    } finally {
      setIsLoading(false);
      setRefreshing(false);
    }
  }, [search]);

  useEffect(() => { loadData(); }, [loadData]);

  const renderItem = ({ item }: { item: Etablissement }) => (
    <TouchableOpacity
      style={styles.card}
      onPress={() => navigation.navigate('EtablissementDetail', { id: item.id })}
    >
      <View style={styles.cardHeader}>
        <Text style={styles.cardTitle}>{item.sigle || item.nom}</Text>
        {item.is_verified && <Text style={styles.verifiedBadge}>✓ Vérifié</Text>}
      </View>
      <Text style={styles.cardDescription} numberOfLines={2}>{item.description}</Text>
      <View style={styles.cardFooter}>
        <Text style={styles.cardMeta}>📍 {item.ville}, {item.pays}</Text>
        <Text style={styles.cardRating}>⭐ {item.note_globale.toFixed(1)} ({item.nombre_avis})</Text>
      </View>
      <View style={styles.cardStats}>
        <Text style={styles.cardStat}>Réussite : {item.taux_reussite.toFixed(0)}%</Text>
        <Text style={styles.cardStat}>Insertion : {item.taux_insertion_professionnelle.toFixed(0)}%</Text>
        {item.visite_virtuelle_url && <Text style={styles.card3D}>🌐 Visite 3D</Text>}
      </View>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <View style={styles.searchContainer}>
        <TextInput
          style={styles.searchInput}
          placeholder="🔍 Rechercher une école, formation..."
          value={search}
          onChangeText={setSearch}
          onSubmitEditing={loadData}
        />
      </View>

      {isLoading ? (
        <ActivityIndicator color={AVENSU_COLORS.primary} size="large" style={{ marginTop: SPACING.xl }} />
      ) : (
        <FlatList
          data={etablissements}
          keyExtractor={item => item.id}
          renderItem={renderItem}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); loadData(); }} />}
          contentContainerStyle={{ padding: SPACING.md }}
          ItemSeparatorComponent={() => <View style={{ height: SPACING.md }} />}
          ListEmptyComponent={<Text style={styles.empty}>Aucun établissement trouvé.</Text>}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F8FAFC' },
  searchContainer: { padding: SPACING.md, backgroundColor: '#FFFFFF' },
  searchInput: {
    borderWidth: 1, borderColor: AVENSU_COLORS.outline, borderRadius: 12,
    padding: SPACING.md, fontSize: 16, backgroundColor: '#F8FAFC',
  },
  card: { backgroundColor: '#FFFFFF', borderRadius: 12, padding: SPACING.lg, elevation: 1 },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  cardTitle: { ...TYPOGRAPHY.h3, color: AVENSU_COLORS.textPrimary, flex: 1 },
  verifiedBadge: { backgroundColor: '#D1FAE5', color: '#065F46', paddingHorizontal: SPACING.sm, paddingVertical: 2, borderRadius: 4, fontSize: 12 },
  cardDescription: { color: AVENSU_COLORS.textSecondary, marginTop: SPACING.xs, fontSize: 14 },
  cardFooter: { flexDirection: 'row', justifyContent: 'space-between', marginTop: SPACING.md },
  cardMeta: { color: AVENSU_COLORS.textTertiary, fontSize: 14 },
  cardRating: { color: AVENSU_COLORS.accent, fontSize: 14 },
  cardStats: { flexDirection: 'row', gap: SPACING.md, marginTop: SPACING.sm, flexWrap: 'wrap' },
  cardStat: { backgroundColor: '#F1F5F9', paddingHorizontal: SPACING.sm, paddingVertical: 4, borderRadius: 6, fontSize: 12, color: AVENSU_COLORS.textSecondary },
  card3D: { backgroundColor: '#E0F2FE', color: AVENSU_COLORS.primaryDark, paddingHorizontal: SPACING.sm, paddingVertical: 4, borderRadius: 6, fontSize: 12 },
  empty: { textAlign: 'center', padding: SPACING.xl, color: AVENSU_COLORS.textTertiary },
});
