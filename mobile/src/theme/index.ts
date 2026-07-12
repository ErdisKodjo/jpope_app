/**
 * Thème Material Design 3 — palette AvenSU-Orienta (lagune + sable).
 */
import { MD3LightTheme } from 'react-native-paper';

export const AVENSU_COLORS = {
  primary: '#0EA5E9',
  primaryDark: '#0369A1',
  primaryLight: '#7DD3FC',
  accent: '#F59E0B',
  accentDark: '#B45309',
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444',
  info: '#3B82F6',
  background: '#F8FAFC',
  surface: '#FFFFFF',
  surfaceVariant: '#F1F5F9',
  outline: '#CBD5E1',
  outlineVariant: '#E2E8F0',
  textPrimary: '#0F172A',
  textSecondary: '#475569',
  textTertiary: '#94A3B8',
  textInverse: '#FFFFFF',
};

export const theme = {
  ...MD3LightTheme,
  colors: {
    ...MD3LightTheme.colors,
    primary: AVENSU_COLORS.primary,
    primaryContainer: AVENSU_COLORS.primaryLight,
    secondary: AVENSU_COLORS.accent,
    secondaryContainer: '#FEF3C7',
    tertiary: AVENSU_COLORS.success,
    error: AVENSU_COLORS.error,
    errorContainer: '#FEE2E2',
    background: AVENSU_COLORS.background,
    surface: AVENSU_COLORS.surface,
    surfaceVariant: AVENSU_COLORS.surfaceVariant,
    outline: AVENSU_COLORS.outline,
    outlineVariant: AVENSU_COLORS.outlineVariant,
    onPrimary: '#FFFFFF',
    onPrimaryContainer: AVENSU_COLORS.primaryDark,
    onSecondary: '#FFFFFF',
    onBackground: AVENSU_COLORS.textPrimary,
    onSurface: AVENSU_COLORS.textPrimary,
    onSurfaceVariant: AVENSU_COLORS.textSecondary,
  },
  roundness: 12,
};

export const SPACING = { xs: 4, sm: 8, md: 16, lg: 24, xl: 32, xxl: 48 };
export const TYPOGRAPHY = {
  h1: { fontSize: 32, fontWeight: 'bold' as const },
  h2: { fontSize: 24, fontWeight: 'bold' as const },
  h3: { fontSize: 20, fontWeight: '600' as const },
  body: { fontSize: 16, fontWeight: '400' as const },
  caption: { fontSize: 12, fontWeight: '400' as const },
  button: { fontSize: 16, fontWeight: '600' as const },
};
