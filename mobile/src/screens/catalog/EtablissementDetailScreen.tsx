/**
 * Détail établissement — infos + visite 3D + formations + simulateur.
 */
import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, TouchableOpacity, StyleSheet, ActivityIndicator, Image } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { CatalogService } from '../../services/catalog';
import { AVENSU_COLORS, SPACING, TYPOGRAPHY } from '../../theme';
import type { Etablissement } from '../../types';

type Nav = NativeStackNavigationProp<any>;

export function EtablissementDetailScreen() {
  const route = useRoute<any>();
  const navigation = useNavigation<Nav>();
  const [etab, setEtab] = useState<Etablissement | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const result = await CatalogService.getEtablissement(route.params.id);
        setEtab(result);
      } finally {
        setIsLoading(false);
      }
    })();
  }, [route.params.id]);

  if (isLoading || !etab) {
    return <View style={styles.center}><ActivityIndicator color={AVENSU_COLORS.primary} size="large" /></View>;
  }

  return (
    <ScrollView style={styles.container}>
      {etab.banniere && (
        <Image source={{ uri: etab.banniere }} style={styles.banniere} resizeMode="cover" />
      )}
      <View style={styles.content}>
        <Text style={styles.title}>{etab.nom}</Text>
        <Text style={styles.location}>📍 {etab.ville}, {etab.pays}</Text>
        <Text style={styles.description}>{etab.description}</Text>

        {/* Indicateurs */}
        <View style={styles.statsGrid}>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>{etab.taux_reussite.toFixed(0)}%</Text>
            <Text style={styles.statLabel}>Réussite</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>{etab.taux_insertion_professionnelle.toFixed(0)}%</Text>
            <Text style={styles.statLabel}>Insertion pro</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>{etab.note_globale.toFixed(1)}⭐</Text>
            <Text style={styles.statLabel}>{etab.nombre_avis} avis</Text>
          </View>
          {etab.classement_national && (
            <View style={styles.statCard}>
              <Text style={styles.statValue}>#{etab.classement_national}</Text>
              <Text style={styles.statLabel}>National</Text>
            </View>
          )}
        </View>

        {/* Frais scolarité */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Frais de scolarité</Text>
          <Text style={styles.sectionContent}>
            {etab.frais_scolarite_annuel_min.toLocaleString()} - {etab.frais_scolarite_annuel_max.toLocaleString()} FCFA / an
          </Text>
        </View>

        {/* Visite 3D */}
        {(etab.visite_virtuelle_url || etab.galerie_3d?.length || etab.video_presentation_url) ? (
          <TouchableOpacity
            style={styles.cta3D}
            onPress={() => navigation.navigate('Visite3D', { id: etab.id })}
          >
            <Text style={styles.cta3DIcon}>🌐</Text>
            <View style={{ flex: 1 }}>
              <Text style={styles.cta3DTitle}>Visite virtuelle 3D</Text>
              <Text style={styles.cta3DSub}>Explorez le campus en immersion</Text>
            </View>
            <Text style={styles.cta3DArrow}>→</Text>
          </TouchableOpacity>
        ) : null}

        {/* Contact */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Contact</Text>
          {etab.site_web && <Text style={styles.sectionContent}>🌐 {etab.site_web}</Text>}
          {etab.email && <Text style={styles.sectionContent}>✉️ {etab.email}</Text>}
          {etab.telephone && <Text style={styles.sectionContent}>📞 {etab.telephone}</Text>}
        </View>

        {/* CTA Simulateur admission */}
        <TouchableOpacity
          style={styles.ctaButton}
          onPress={() => navigation.navigate('SimulateurAdmission', { etablissement_id: etab.id })}
        >
          <Text style={styles.ctaButtonText}>🎯 Simuler mes chances d'admission</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FFFFFF' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  banniere: { width: '100%', height: 200 },
  content: { padding: SPACING.lg },
  title: { ...TYPOGRAPHY.h1, color: AVENSU_COLORS.textPrimary },
  location: { color: AVENSU_COLORS.textSecondary, marginTop: SPACING.xs },
  description: { color: AVENSU_COLORS.textSecondary, marginTop: SPACING.md, lineHeight: 22 },
  statsGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: SPACING.sm, marginTop: SPACING.lg },
  statCard: { flex: 1, minWidth: '47%', backgroundColor: '#F8FAFC', padding: SPACING.md, borderRadius: 12, alignItems: 'center' },
  statValue: { ...TYPOGRAPHY.h3, color: AVENSU_COLORS.primary },
  statLabel: { color: AVENSU_COLORS.textSecondary, fontSize: 12, marginTop: 2 },
  section: { marginTop: SPACING.lg },
  sectionTitle: { ...TYPOGRAPHY.h3, marginBottom: SPACING.sm },
  sectionContent: { color: AVENSU_COLORS.textSecondary, fontSize: 14, marginBottom: 4 },
  cta3D: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#E0F2FE', padding: SPACING.lg, borderRadius: 12, marginTop: SPACING.lg },
  cta3DIcon: { fontSize: 32, marginRight: SPACING.md },
  cta3DTitle: { ...TYPOGRAPHY.h3, color: AVENSU_COLORS.primaryDark },
  cta3DSub: { color: AVENSU_COLORS.textSecondary, fontSize: 14 },
  cta3DArrow: { fontSize: 24, color: AVENSU_COLORS.primary },
  ctaButton: { backgroundColor: AVENSU_COLORS.primary, padding: SPACING.lg, borderRadius: 12, alignItems: 'center', marginTop: SPACING.xl },
  ctaButtonText: { color: '#FFFFFF', ...TYPOGRAPHY.button },
});
