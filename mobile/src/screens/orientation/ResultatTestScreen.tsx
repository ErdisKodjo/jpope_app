/**
 * Résultat test — affiche scores, dimensions, interprétation, forces.
 */
import React from 'react';
import { View, Text, ScrollView, StyleSheet } from 'react-native';
import { useRoute } from '@react-navigation/native';
import { AVENSU_COLORS, SPACING, TYPOGRAPHY } from '../../theme';

export function ResultatTestScreen() {
  const route = useRoute<any>();
  const r = route.params?.resultat;

  if (!r) {
    return <View style={styles.center}><Text>Aucun résultat</Text></View>;
  }

  const dimensions = r.scores_par_dimension || {};

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.scoreLabel}>Score global</Text>
        <Text style={styles.scoreValue}>{r.score_global}/100</Text>
      </View>

      {r.code_holland && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Code Holland</Text>
          <Text style={styles.codeHolland}>{r.code_holland}</Text>
        </View>
      )}

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Scores par dimension</Text>
        {Object.entries(dimensions).map(([dim, score]: [string, any]) => (
          <View key={dim} style={styles.dimensionRow}>
            <Text style={styles.dimensionLabel}>{dim}</Text>
            <View style={styles.dimensionBar}>
              <View style={[styles.dimensionFill, { width: `${score}%` }]} />
            </View>
            <Text style={styles.dimensionScore}>{score.toFixed(1)}</Text>
          </View>
        ))}
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Interprétation</Text>
        <Text style={styles.interpretation}>{r.interpretation}</Text>
      </View>

      {r.forces?.length > 0 && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>✓ Forces</Text>
          {r.forces.map((f: string, i: number) => (
            <Text key={i} style={styles.listItem}>• {f}</Text>
          ))}
        </View>
      )}

      {r.axes_amelioration?.length > 0 && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>↑ Axes d'amélioration</Text>
          {r.axes_amelioration.map((a: string, i: number) => (
            <Text key={i} style={styles.listItem}>• {a}</Text>
          ))}
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F8FAFC' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  header: { backgroundColor: AVENSU_COLORS.primary, padding: SPACING.xl, alignItems: 'center' },
  scoreLabel: { color: '#FFFFFF', opacity: 0.85, fontSize: 16 },
  scoreValue: { fontSize: 48, fontWeight: 'bold', color: '#FFFFFF', marginTop: SPACING.xs },
  card: { backgroundColor: '#FFFFFF', margin: SPACING.md, padding: SPACING.lg, borderRadius: 12 },
  cardTitle: { ...TYPOGRAPHY.h3, color: AVENSU_COLORS.textPrimary, marginBottom: SPACING.md },
  codeHolland: { fontSize: 36, fontWeight: 'bold', color: AVENSU_COLORS.primary, textAlign: 'center' },
  dimensionRow: { flexDirection: 'row', alignItems: 'center', marginVertical: 6 },
  dimensionLabel: { width: 60, fontSize: 16, fontWeight: '600', color: AVENSU_COLORS.textPrimary },
  dimensionBar: { flex: 1, height: 12, backgroundColor: '#E2E8F0', borderRadius: 6, marginHorizontal: SPACING.md, overflow: 'hidden' },
  dimensionFill: { height: '100%', backgroundColor: AVENSU_COLORS.primary },
  dimensionScore: { width: 40, fontSize: 12, color: AVENSU_COLORS.textSecondary, textAlign: 'right' },
  interpretation: { color: AVENSU_COLORS.textSecondary, lineHeight: 22 },
  listItem: { color: AVENSU_COLORS.textSecondary, marginVertical: 4 },
});
