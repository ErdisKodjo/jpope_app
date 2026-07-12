/**
 * Auth Navigator — Login, Register, 2FA Verify, Forgot Password, Consent Parental.
 */
import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { LoginScreen } from '../screens/auth/LoginScreen';
import { RegisterScreen } from '../screens/auth/RegisterScreen';
import { TwoFAVerifyScreen } from '../screens/auth/TwoFAVerifyScreen';
import { TwoFASetupScreen } from '../screens/auth/TwoFASetupScreen';
import { ForgotPasswordScreen } from '../screens/auth/ForgotPasswordScreen';
import { ParentalConsentScreen } from '../screens/auth/ParentalConsentScreen';

export type AuthStackParamList = {
  Login: undefined;
  Register: undefined;
  TwoFAVerify: { challenge_token: string };
  TwoFASetup: undefined;
  ForgotPassword: undefined;
  ParentalConsent: undefined;
};

const Stack = createNativeStackNavigator<AuthStackParamList>();

export function AuthNavigator() {
  return (
    <Stack.Navigator
      initialRouteName="Login"
      screenOptions={{ headerShown: false }}
    >
      <Stack.Screen name="Login" component={LoginScreen} />
      <Stack.Screen name="Register" component={RegisterScreen} />
      <Stack.Screen name="TwoFAVerify" component={TwoFAVerifyScreen} options={{ title: 'Vérification 2FA' }} />
      <Stack.Screen name="TwoFASetup" component={TwoFASetupScreen} options={{ title: 'Configuration 2FA' }} />
      <Stack.Screen name="ForgotPassword" component={ForgotPasswordScreen} options={{ title: 'Mot de passe oublié' }} />
      <Stack.Screen name="ParentalConsent" component={ParentalConsentScreen} options={{ title: 'Consentement parental' }} />
    </Stack.Navigator>
  );
}
