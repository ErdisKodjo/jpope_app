/**
 * Communauté — forum, messagerie, mentorat, sessions collectives.
 */
import React from 'react';
import { View, Text, ScrollView, TouchableOpacity, StyleSheet } from 'react-native';
import { AVENSU_COLORS, SPACING, TYPOGRAPHY } from '../../theme';

export function CommunityScreen() {
  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Communauté</Text>
        <Text style={styles.subtitle}>Forum · Messagerie · Mentorat · Sessions</Text>
      </View>

      <View style={styles.grid}>
        <TouchableOpacity style={styles.card}>
          <Text style={styles.cardIcon}>💬</Text>
          <Text style={styles.cardTitle}>Forum d'entraide</Text>
          <Text style={styles.cardDesc}>Échangez avec la communauté</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.card}>
          <Text style={styles.cardIcon}>✉️</Text>
          <Text style={styles.cardTitle}>Messagerie</Text>
          <Text style={styles.cardDesc}>Vos conversations privées</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.card}>
          <Text style={styles.cardIcon}>🤝</Text>
          <Text style={styles.cardTitle}>Mentorat alumni</Text>
          <Text style={styles.cardDesc}>Trouvez un mentor</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.card}>
          <Text style={styles.cardIcon}>📅</Text>
          <Text style={styles.cardTitle}>Sessions collectives</Text>
          <Text style={styles.cardDesc}>Ateliers et webinaires</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.card}>
          <Text style={styles.cardIcon}>⭐</Text>
          <Text style={styles.cardTitle}>Avis alumni</Text>
          <Text style={styles.cardDesc}>Témoignages certifiés</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F8FAFC' },
  header: { padding: SPACING.lg, backgroundColor: AVENSU_COLORS.primary },
  title: { ...TYPOGRAPHY.h1, color: '#FFFFFF' },
  subtitle: { color: '#FFFFFF', opacity: 0.85, marginTop: SPACING.xs },
  grid: { padding: SPACING.md, gap: SPACING.md },
  card: { backgroundColor: '#FFFFFF', borderRadius: 12, padding: SPACING.lg, elevation: 1 },
  cardIcon: { fontSize: 32 },
  cardTitle: { ...TYPOGRAPHY.h3, marginTop: SPACING.sm, color: AVENSU_COLORS.textPrimary },
  cardDesc: { color: AVENSU_COLORS.textSecondary, marginTop: SPACING.xs },
});
