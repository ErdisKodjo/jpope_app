/**
 * Profil — infos utilisateur + actions (2FA, abonnement, CRM, RGPD, déconnexion).
 */
import React from 'react';
import { View, Text, TouchableOpacity, ScrollView, StyleSheet, Alert } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useAuth } from '../../store/authStore';
import { AVENSU_COLORS, SPACING, TYPOGRAPHY } from '../../theme';

type Nav = NativeStackNavigationProp<any>;

export function ProfileScreen() {
  const { user, logout } = useAuth();
  const navigation = useNavigation<Nav>();

  const menuItems = [
    { icon: '🔐', label: 'Sécurité 2FA', screen: 'TwoFASettings', color: '#0EA5E9' },
    { icon: '💼', label: 'CRM Établissement', screen: 'CRM', color: '#10B981', role: 'SCHOOL_REP' },
    { icon: '📣', label: 'Campagnes marketing', screen: 'Campagnes', color: '#F59E0B', role: 'SCHOOL_REP' },
    { icon: '🔒', label: 'Mes données RGPD', screen: 'RGPD', color: '#A855F7' },
    { icon: '👨‍👩‍👧', label: 'Mes enfants', screen: 'Children', color: '#EC4899', role: 'PARENT' },
  ];

  const handleLogout = () => {
    Alert.alert('Déconnexion', 'Voulez-vous vraiment vous déconnecter ?', [
      { text: 'Annuler' },
      { text: 'Déconnexion', style: 'destructive', onPress: logout },
    ]);
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <View style={styles.avatar}>
          <Text style={styles.avatarText}>
            {user?.first_name?.[0]?.toUpperCase()}{user?.last_name?.[0]?.toUpperCase()}
          </Text>
        </View>
        <Text style={styles.userName}>{user?.first_name} {user?.last_name}</Text>
        <Text style={styles.userEmail}>{user?.email}</Text>
        <View style={styles.roleBadge}>
          <Text style={styles.roleText}>{user?.role}</Text>
        </View>
      </View>

      <View style={styles.menu}>
        {menuItems
          .filter(item => !item.role || item.role === user?.role)
          .map(item => (
            <TouchableOpacity
              key={item.screen}
              style={styles.menuItem}
              onPress={() => navigation.navigate(item.screen)}
            >
              <View style={[styles.menuIcon, { backgroundColor: item.color + '20' }]}>
                <Text style={styles.menuIconText}>{item.icon}</Text>
              </View>
              <Text style={styles.menuLabel}>{item.label}</Text>
              <Text style={styles.menuArrow}>→</Text>
            </TouchableOpacity>
          ))}
      </View>

      <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
        <Text style={styles.logoutText}>🚪 Déconnexion</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F8FAFC' },
  header: { padding: SPACING.xl, backgroundColor: AVENSU_COLORS.primary, alignItems: 'center' },
  avatar: { width: 80, height: 80, borderRadius: 40, backgroundColor: '#FFFFFF', justifyContent: 'center', alignItems: 'center' },
  avatarText: { fontSize: 32, fontWeight: 'bold', color: AVENSU_COLORS.primary },
  userName: { ...TYPOGRAPHY.h2, color: '#FFFFFF', marginTop: SPACING.md },
  userEmail: { color: '#FFFFFF', opacity: 0.85, marginTop: SPACING.xs },
  roleBadge: { backgroundColor: 'rgba(255,255,255,0.2)', paddingHorizontal: SPACING.md, paddingVertical: SPACING.xs, borderRadius: 12, marginTop: SPACING.sm },
  roleText: { color: '#FFFFFF', fontSize: 12, fontWeight: '600' },
  menu: { padding: SPACING.md },
  menuItem: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#FFFFFF', borderRadius: 12, padding: SPACING.md, marginBottom: SPACING.sm },
  menuIcon: { width: 44, height: 44, borderRadius: 22, justifyContent: 'center', alignItems: 'center', marginRight: SPACING.md },
  menuIconText: { fontSize: 22 },
  menuLabel: { flex: 1, color: AVENSU_COLORS.textPrimary, fontSize: 16, fontWeight: '500' },
  menuArrow: { color: AVENSU_COLORS.textTertiary, fontSize: 20 },
  logoutButton: { margin: SPACING.md, padding: SPACING.lg, backgroundColor: '#FEE2E2', borderRadius: 12, alignItems: 'center' },
  logoutText: { color: '#991B1B', fontWeight: '600', fontSize: 16 },
});
