/**
 * Simulateur d'admission — saisie moyenne + bac → % chances.
 */
import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, ActivityIndicator, ScrollView } from 'react-native';
import { CatalogService } from '../../services/catalog';
import { AVENSU_COLORS, SPACING, TYPOGRAPHY } from '../../theme';
import type { SimulationAdmission } from '../../types';

const SERIES_BAC = ['C', 'D', 'G2', 'L', 'S', 'STMG', 'STI2D'];

export function SimulateurAdmissionScreen({ route }: { route: any }) {
  const { etablissement_id } = route.params;
  const [formationId, setFormationId] = useState('');
  const [moyenne, setMoyenne] = useState('');
  const [serie, setSerie] = useState('C');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<SimulationAdmission | null>(null);

  const handleSimulate = async () => {
    const m = parseFloat(moyenne);
    if (isNaN(m) || m < 0 || m > 20) {
      Alert.alert('Erreur', 'Veuillez saisir une moyenne entre 0 et 20.');
      return;
    }
    if (!formationId) {
      Alert.alert('Erreur', 'Veuillez saisir l\'ID de la formation.');
      return;
    }
    setIsLoading(true);
    try {
      const r = await CatalogService.simulerAdmission({
        formation_id: formationId,
        moyenne: m,
        serie_bac: serie,
      });
      setResult(r);
    } catch (e: any) {
      Alert.alert('Erreur', e?.response?.data?.error || e.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.title}>🎯 Simulateur d'admission</Text>
        <Text style={styles.subtitle}>
          Estimez vos chances d'intégrer une formation en croisant votre moyenne et
          les critères historiques de l'établissement.
        </Text>

        <Text style={styles.label}>ID de la formation *</Text>
        <TextInput
          style={styles.input}
          value={formationId}
          onChangeText={setFormationId}
          placeholder="UUID de la formation"
        />

        <Text style={styles.label}>Moyenne au bac (/20) *</Text>
        <TextInput
          style={styles.input}
          value={moyenne}
          onChangeText={setMoyenne}
          placeholder="14.5"
          keyboardType="decimal-pad"
        />

        <Text style={styles.label}>Série de bac</Text>
        <View style={styles.seriesGrid}>
          {SERIES_BAC.map(s => (
            <TouchableOpacity
              key={s}
              style={[styles.serieButton, serie === s && styles.serieButtonSelected]}
              onPress={() => setSerie(s)}
            >
              <Text style={[styles.serieText, serie === s && styles.serieTextSelected]}>{s}</Text>
            </TouchableOpacity>
          ))}
        </View>

        <TouchableOpacity style={styles.button} onPress={handleSimulate} disabled={isLoading}>
          {isLoading ? <ActivityIndicator color="#FFFFFF" /> : <Text style={styles.buttonText}>Simuler</Text>}
        </TouchableOpacity>
      </View>

      {result && (
        <View style={[styles.card, { marginTop: SPACING.md }]}>
          <Text style={styles.resultTitle}>Résultat</Text>
          <View style={[styles.scoreCircle, {
            backgroundColor: result.pourcentage_chances >= 60 ? '#D1FAE5'
              : result.pourcentage_chances >= 30 ? '#FEF3C7' : '#FEE2E2'
          }]}>
            <Text style={[styles.scoreValue, {
              color: result.pourcentage_chances >= 60 ? '#065F46'
                : result.pourcentage_chances >= 30 ? '#92400E' : '#991B1B'
            }]}>
              {result.pourcentage_chances.toFixed(1)}%
            </Text>
          </View>

          <Text style={styles.confidenceLabel}>
            Confiance : <Text style={styles.confidenceValue}>{result.niveau_confiance}</Text>
          </Text>

          {result.explication && (
            <View style={styles.explicationBox}>
              <Text style={styles.explicationTitle}>📊 Détails du calcul</Text>
              {Object.entries(result.explication).map(([k, v]) => (
                <Text key={k} style={styles.explicationRow}>• {k}: {String(v)}</Text>
              ))}
            </View>
          )}

          {result.recommandations?.length > 0 && (
            <View style={styles.recommandationsBox}>
              <Text style={styles.explicationTitle}>💡 Recommandations</Text>
              {result.recommandations.map((r, i) => (
                <Text key={i} style={styles.recommandationRow}>{r}</Text>
              ))}
            </View>
          )}
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F8FAFC', padding: SPACING.md },
  card: { backgroundColor: '#FFFFFF', borderRadius: 12, padding: SPACING.lg },
  title: { ...TYPOGRAPHY.h2, color: AVENSU_COLORS.textPrimary, marginBottom: SPACING.sm },
  subtitle: { color: AVENSU_COLORS.textSecondary, marginBottom: SPACING.lg, lineHeight: 22 },
  label: { color: AVENSU_COLORS.textSecondary, marginBottom: SPACING.xs, marginTop: SPACING.md },
  input: {
    borderWidth: 1, borderColor: AVENSU_COLORS.outline, borderRadius: 12,
    padding: SPACING.md, fontSize: 16, backgroundColor: '#F8FAFC',
  },
  seriesGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: SPACING.sm, marginTop: SPACING.sm },
  serieButton: { paddingHorizontal: SPACING.md, paddingVertical: SPACING.sm, borderWidth: 1, borderColor: AVENSU_COLORS.outline, borderRadius: 8 },
  serieButtonSelected: { backgroundColor: AVENSU_COLORS.primary, borderColor: AVENSU_COLORS.primary },
  serieText: { color: AVENSU_COLORS.textPrimary, fontSize: 14 },
  serieTextSelected: { color: '#FFFFFF', fontWeight: '600' },
  button: { backgroundColor: AVENSU_COLORS.primary, padding: SPACING.md, borderRadius: 12, alignItems: 'center', marginTop: SPACING.lg },
  buttonText: { color: '#FFFFFF', ...TYPOGRAPHY.button },
  resultTitle: { ...TYPOGRAPHY.h2, color: AVENSU_COLORS.textPrimary, textAlign: 'center', marginBottom: SPACING.lg },
  scoreCircle: { width: 180, height: 180, borderRadius: 90, justifyContent: 'center', alignItems: 'center', alignSelf: 'center', marginVertical: SPACING.lg },
  scoreValue: { fontSize: 36, fontWeight: 'bold' },
  confidenceLabel: { textAlign: 'center', color: AVENSU_COLORS.textSecondary, marginBottom: SPACING.md },
  confidenceValue: { fontWeight: '600', color: AVENSU_COLORS.textPrimary },
  explicationBox: { backgroundColor: '#F1F5F9', padding: SPACING.md, borderRadius: 8, marginTop: SPACING.md },
  explicationTitle: { ...TYPOGRAPHY.h3, fontSize: 14, marginBottom: SPACING.xs },
  explicationRow: { color: AVENSU_COLORS.textSecondary, fontSize: 12, marginVertical: 2 },
  recommandationsBox: { backgroundColor: '#FEF3C7', padding: SPACING.md, borderRadius: 8, marginTop: SPACING.md },
  recommandationRow: { color: AVENSU_COLORS.textPrimary, fontSize: 12, marginVertical: 4, lineHeight: 18 },
});
