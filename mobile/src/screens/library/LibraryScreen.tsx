/**
 * Bibliothèque — liste ressources avec filtres + recommandations.
 */
import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, TextInput, TouchableOpacity, FlatList, StyleSheet, RefreshControl, ActivityIndicator } from 'react-native';
import { LibraryService } from '../../services/library';
import { AVENSU_COLORS, SPACING, TYPOGRAPHY } from '../../theme';
import type { RessourceBiblio } from '../../types';

const TYPES = [
  { value: '', label: 'Tous', icon: '📚' },
  { value: 'MANUEL', label: 'Manuels', icon: '📖' },
  { value: 'ANNALE', label: 'Annales', icon: '📝' },
  { value: 'COURS_PREP', label: 'Cours prep', icon: '🎓' },
  { value: 'FICHE_REVISION', label: 'Fiches', icon: '📋' },
  { value: 'VIDEO', label: 'Vidéos', icon: '🎬' },
];

export function LibraryScreen() {
  const [ressources, setRessources] = useState<RessourceBiblio[]>([]);
  const [type, setType] = useState('');
  const [search, setSearch] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadData = useCallback(async () => {
    try {
      const result = await LibraryService.listRessources({
        type: type || undefined,
        q: search || undefined,
      });
      setRessources(result.results);
    } catch (e) {
      // silent
    } finally {
      setIsLoading(false);
      setRefreshing(false);
    }
  }, [type, search]);

  useEffect(() => { loadData(); }, [loadData]);

  const renderItem = ({ item }: { item: RessourceBiblio }) => (
    <View style={styles.card}>
      <View style={styles.cardHeader}>
        <Text style={styles.cardType}>{TYPES.find(t => t.value === item.type)?.icon} {item.type}</Text>
        {item.is_premium && <Text style={styles.premiumBadge}>PREMIUM</Text>}
      </View>
      <Text style={styles.cardTitle}>{item.titre}</Text>
      <Text style={styles.cardDesc} numberOfLines={2}>{item.description_courte}</Text>
      <View style={styles.cardMeta}>
        <Text style={styles.metaText}>📚 {item.matiere}</Text>
        <Text style={styles.metaText}>⭐ {item.note_moyenne.toFixed(1)} ({item.nombre_votes})</Text>
        <Text style={styles.metaText}>⬇ {item.nombre_telechargements}</Text>
      </View>
    </View>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Bibliothèque numérique</Text>
        <TextInput
          style={styles.search}
          placeholder="🔍 Rechercher..."
          value={search}
          onChangeText={setSearch}
        />
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.typesContainer}>
          {TYPES.map(t => (
            <TouchableOpacity
              key={t.value}
              style={[styles.typeChip, type === t.value && styles.typeChipActive]}
              onPress={() => setType(t.value)}
            >
              <Text style={[styles.typeText, type === t.value && styles.typeTextActive]}>
                {t.icon} {t.label}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      {isLoading ? (
        <ActivityIndicator color={AVENSU_COLORS.primary} size="large" style={{ marginTop: SPACING.xl }} />
      ) : (
        <FlatList
          data={ressources}
          keyExtractor={item => item.id}
          renderItem={renderItem}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); loadData(); }} />}
          contentContainerStyle={{ padding: SPACING.md }}
          ItemSeparatorComponent={() => <View style={{ height: SPACING.md }} />}
          ListEmptyComponent={<Text style={styles.empty}>Aucune ressource trouvée.</Text>}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F8FAFC' },
  header: { padding: SPACING.md, backgroundColor: '#FFFFFF' },
  title: { ...TYPOGRAPHY.h2, color: AVENSU_COLORS.textPrimary, marginBottom: SPACING.md },
  search: {
    borderWidth: 1, borderColor: AVENSU_COLORS.outline, borderRadius: 12,
    padding: SPACING.md, fontSize: 16, backgroundColor: '#F8FAFC',
  },
  typesContainer: { marginTop: SPACING.md },
  typeChip: { paddingHorizontal: SPACING.md, paddingVertical: SPACING.sm, backgroundColor: '#F1F5F9', borderRadius: 20, marginRight: SPACING.sm },
  typeChipActive: { backgroundColor: AVENSU_COLORS.primary },
  typeText: { color: AVENSU_COLORS.textPrimary, fontSize: 14 },
  typeTextActive: { color: '#FFFFFF', fontWeight: '600' },
  card: { backgroundColor: '#FFFFFF', borderRadius: 12, padding: SPACING.lg, elevation: 1 },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: SPACING.xs },
  cardType: { color: AVENSU_COLORS.textTertiary, fontSize: 12 },
  premiumBadge: { backgroundColor: '#FEF3C7', color: '#92400E', paddingHorizontal: SPACING.sm, paddingVertical: 2, borderRadius: 4, fontSize: 10, fontWeight: 'bold' },
  cardTitle: { ...TYPOGRAPHY.h3, color: AVENSU_COLORS.textPrimary, marginBottom: SPACING.xs },
  cardDesc: { color: AVENSU_COLORS.textSecondary, fontSize: 14, lineHeight: 20 },
  cardMeta: { flexDirection: 'row', gap: SPACING.md, marginTop: SPACING.sm },
  metaText: { color: AVENSU_COLORS.textTertiary, fontSize: 12 },
  empty: { textAlign: 'center', padding: SPACING.xl, color: AVENSU_COLORS.textTertiary },
});
