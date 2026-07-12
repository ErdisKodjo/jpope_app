/**
 * Orientation home — liste des tests + rapport combiné.
 */
import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, ActivityIndicator } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { OrientationService } from '../../services/orientation';
import { AVENSU_COLORS, SPACING, TYPOGRAPHY } from '../../theme';

type Nav = NativeStackNavigationProp<any>;

export function OrientationHomeScreen() {
  const navigation = useNavigation<Nav>();
  const [tests, setTests] = useState<any[]>([]);
  const [rapport, setRapport] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const [t, r] = await Promise.allSettled([
          OrientationService.listTests(),
          OrientationService.getRapportCombine(),
        ]);
        if (t.status === 'fulfilled') setTests(t.value);
        if (r.status === 'fulfilled') setRapport(r.value);
      } finally {
        setIsLoading(false);
      }
    })();
  }, []);

  if (isLoading) {
    return <View style={styles.center}><ActivityIndicator color={AVENSU_COLORS.primary} size="large" /></View>;
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>🧭 Orientation</Text>
        <Text style={styles.subtitle}>Tests + rapport combiné RIASEC × Ikigai</Text>
      </View>

      {rapport && (
        <TouchableOpacity
          style={styles.rapportCard}
          onPress={() => navigation.navigate('RapportCombine')}
        >
          <Text style={styles.rapportTitle}>📄 Rapport combiné</Text>
          <Text style={styles.rapportSynthese} numberOfLines={3}>{rapport.synthese}</Text>
          <Text style={styles.rapportArrow}>→</Text>
        </TouchableOpacity>
      )}

      <Text style={styles.sectionTitle}>Tests disponibles</Text>
      {tests.map(t => (
        <TouchableOpacity
          key={t.id}
          style={styles.testCard}
          onPress={() => navigation.navigate('TakeTest', { test_id: t.id, test_nom: t.nom })}
        >
          <View style={styles.testIcon}>
            <Text style={styles.testIconText}>
              {t.type === 'IKIGAI' ? '🎯' : t.type === 'INTERETS' ? '🧬' : '📋'}
            </Text>
          </View>
          <View style={{ flex: 1 }}>
            <Text style={styles.testTitle}>{t.nom}</Text>
            <Text style={styles.testMeta}>{t.duree_estimee_minutes} min · {t.nombre_questions} questions</Text>
          </View>
          <Text style={styles.testArrow}>→</Text>
        </TouchableOpacity>
      ))}

      {tests.length === 0 && (
        <Text style={styles.empty}>Aucun test disponible pour le moment.</Text>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F8FAFC' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  header: { padding: SPACING.lg, backgroundColor: AVENSU_COLORS.primary },
  title: { ...TYPOGRAPHY.h1, color: '#FFFFFF' },
  subtitle: { color: '#FFFFFF', opacity: 0.85, marginTop: SPACING.xs },
  rapportCard: {
    backgroundColor: '#FFFFFF', margin: SPACING.md, padding: SPACING.lg, borderRadius: 12,
    flexDirection: 'row', alignItems: 'center', elevation: 2,
  },
  rapportTitle: { ...TYPOGRAPHY.h3, color: AVENSU_COLORS.textPrimary, marginBottom: SPACING.xs },
  rapportSynthese: { color: AVENSU_COLORS.textSecondary, fontSize: 14, flex: 1 },
  rapportArrow: { fontSize: 24, color: AVENSU_COLORS.primary, marginLeft: SPACING.md },
  sectionTitle: { ...TYPOGRAPHY.h3, marginHorizontal: SPACING.md, marginTop: SPACING.lg },
  testCard: {
    backgroundColor: '#FFFFFF', marginHorizontal: SPACING.md, marginVertical: SPACING.sm,
    padding: SPACING.md, borderRadius: 12, flexDirection: 'row', alignItems: 'center', elevation: 1,
  },
  testIcon: { width: 50, height: 50, borderRadius: 25, backgroundColor: '#E0F2FE', justifyContent: 'center', alignItems: 'center', marginRight: SPACING.md },
  testIconText: { fontSize: 24 },
  testTitle: { color: AVENSU_COLORS.textPrimary, fontSize: 16, fontWeight: '600' },
  testMeta: { color: AVENSU_COLORS.textTertiary, fontSize: 12, marginTop: 2 },
  testArrow: { fontSize: 24, color: AVENSU_COLORS.primary },
  empty: { textAlign: 'center', padding: SPACING.xl, color: AVENSU_COLORS.textTertiary },
});
