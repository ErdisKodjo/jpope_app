/**
 * Rapport combiné RIASEC × Ikigai.
 */
import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, StyleSheet, ActivityIndicator } from 'react-native';
import { OrientationService } from '../../services/orientation';
import { AVENSU_COLORS, SPACING, TYPOGRAPHY } from '../../theme';

export function RapportCombineScreen() {
  const [rapport, setRapport] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const r = await OrientationService.getRapportCombine();
        setRapport(r);
      } finally {
        setIsLoading(false);
      }
    })();
  }, []);

  if (isLoading) {
    return <View style={styles.center}><ActivityIndicator color={AVENSU_COLORS.primary} size="large" /></View>;
  }

  if (!rapport) {
    return <View style={styles.center}><Text>Aucun rapport disponible.</Text></View>;
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Rapport d'orientation combiné</Text>
        <Text style={styles.date}>{new Date(rapport.date_rapport).toLocaleDateString('fr-FR')}</Text>
      </View>

      {rapport.riasec && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>🧬 Profil RIASEC</Text>
          <Text style={styles.codeHolland}>{rapport.riasec.code_holland}</Text>
          <Text style={styles.score}>Score global : {rapport.riasec.score_global}/100</Text>
          {rapport.riasec.forces?.length > 0 && (
            <>
              <Text style={styles.subTitle}>Forces :</Text>
              {rapport.riasec.forces.map((f: string, i: number) => (
                <Text key={i} style={styles.listItem}>• {f}</Text>
              ))}
            </>
          )}
        </View>
      )}

      {rapport.ikigai && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>🎯 Profil Ikigai</Text>
          <Text style={styles.score}>Score global : {rapport.ikigai.score_global}/100</Text>
          {rapport.ikigai.scores_par_dimension && (
            <View style={{ marginTop: SPACING.sm }}>
              {Object.entries(rapport.ikigai.scores_par_dimension).map(([dim, score]: [string, any]) => (
                <View key={dim} style={styles.dimRow}>
                  <Text style={styles.dimLabel}>{dim}</Text>
                  <View style={styles.dimBar}>
                    <View style={[styles.dimFill, { width: `${score}%` }]} />
                  </View>
                  <Text style={styles.dimScore}>{score.toFixed(0)}</Text>
                </View>
              ))}
            </View>
          )}
        </View>
      )}

      <View style={styles.card}>
        <Text style={styles.cardTitle}>📊 Synthèse combinée</Text>
        <Text style={styles.synthese}>{rapport.synthese}</Text>
      </View>

      {rapport.metiers_prioritaires?.length > 0 && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>💼 Métiers prioritaires</Text>
          {rapport.metiers_prioritaires.map((m: string, i: number) => (
            <View key={i} style={styles.metierRow}>
              <Text style={styles.metierIcon}>→</Text>
              <Text style={styles.metierName}>{m}</Text>
            </View>
          ))}
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F8FAFC' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  header: { padding: SPACING.lg, backgroundColor: AVENSU_COLORS.primary },
  title: { ...TYPOGRAPHY.h2, color: '#FFFFFF' },
  date: { color: '#FFFFFF', opacity: 0.85, marginTop: SPACING.xs },
  card: { backgroundColor: '#FFFFFF', margin: SPACING.md, padding: SPACING.lg, borderRadius: 12 },
  cardTitle: { ...TYPOGRAPHY.h3, color: AVENSU_COLORS.textPrimary, marginBottom: SPACING.md },
  codeHolland: { fontSize: 36, fontWeight: 'bold', color: AVENSU_COLORS.primary, textAlign: 'center', marginVertical: SPACING.sm },
  score: { color: AVENSU_COLORS.textSecondary, textAlign: 'center' },
  subTitle: { ...TYPOGRAPHY.body, marginTop: SPACING.md, marginBottom: SPACING.xs, fontWeight: '600' },
  listItem: { color: AVENSU_COLORS.textSecondary, marginVertical: 2 },
  synthese: { color: AVENSU_COLORS.textSecondary, lineHeight: 22 },
  dimRow: { flexDirection: 'row', alignItems: 'center', marginVertical: 4 },
  dimLabel: { width: 100, fontSize: 12, color: AVENSU_COLORS.textPrimary, fontWeight: '500' },
  dimBar: { flex: 1, height: 10, backgroundColor: '#E2E8F0', borderRadius: 5, marginHorizontal: SPACING.sm, overflow: 'hidden' },
  dimFill: { height: '100%', backgroundColor: AVENSU_COLORS.accent },
  dimScore: { width: 30, fontSize: 12, color: AVENSU_COLORS.textSecondary, textAlign: 'right' },
  metierRow: { flexDirection: 'row', alignItems: 'center', marginVertical: 6 },
  metierIcon: { color: AVENSU_COLORS.primary, marginRight: SPACING.sm, fontSize: 16 },
  metierName: { color: AVENSU_COLORS.textPrimary, fontSize: 16, flex: 1 },
});
