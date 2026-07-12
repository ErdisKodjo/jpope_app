/**
 * Navigation racine — Auth stack vs Main stack selon statut d'auth.
 */
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { ActivityIndicator, View } from 'react-native';
import { useAuth } from '../store/authStore';
import { AuthNavigator } from './AuthNavigator';
import { MainNavigator } from './MainNavigator';
import { AVENSU_COLORS } from '../theme';

export function RootNavigator() {
  const { isLoading, isAuthenticated, requires2FA } = useAuth();

  if (isLoading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: AVENSU_COLORS.primary }}>
        <ActivityIndicator size="large" color="#FFFFFF" />
      </View>
    );
  }

  return (
    <NavigationContainer>
      {/* requires2FA ou non-authentifié → AuthNavigator */}
      {/* authentifié → MainNavigator */}
      {isAuthenticated && !requires2FA ? <MainNavigator /> : <AuthNavigator />}
    </NavigationContainer>
  );
}
