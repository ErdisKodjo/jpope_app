/**
 * Détail formation — placeholder (consultation d'une formation spécifique).
 */
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { AVENSU_COLORS, SPACING, TYPOGRAPHY } from '../../theme';

export function FormationDetailScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Détail formation</Text>
      <Text style={styles.text}>Écran à compléter avec les informations de la formation.</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: SPACING.lg, backgroundColor: '#FFFFFF' },
  title: { ...TYPOGRAPHY.h2, color: AVENSU_COLORS.textPrimary, marginBottom: SPACING.md },
  text: { color: AVENSU_COLORS.textSecondary },
});
