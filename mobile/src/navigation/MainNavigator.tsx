/**
 * Main Navigator — Bottom Tabs (Dashboard, Catalog, Orientation, Biblio, Profile)
 * + Root stack pour écrans modaux (Simulateur, Visite 3D, CRM, RGPD, etc.)
 */
import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { MaterialCommunityIcons } from '@expo/vector-icons';

import { DashboardScreen } from '../screens/dashboard/DashboardScreen';
import { CatalogScreen } from '../screens/catalog/CatalogScreen';
import { OrientationHomeScreen } from '../screens/orientation/OrientationHomeScreen';
import { LibraryScreen } from '../screens/library/LibraryScreen';
import { ProfileScreen } from '../screens/profile/ProfileScreen';

import { EtablissementDetailScreen } from '../screens/catalog/EtablissementDetailScreen';
import { FormationDetailScreen } from '../screens/catalog/FormationDetailScreen';
import { SimulateurAdmissionScreen } from '../screens/catalog/SimulateurAdmissionScreen';
import { Visite3DScreen } from '../screens/catalog/Visite3DScreen';
import { TakeTestScreen } from '../screens/orientation/TakeTestScreen';
import { ResultatTestScreen } from '../screens/orientation/ResultatTestScreen';
import { RapportCombineScreen } from '../screens/orientation/RapportCombineScreen';
import { RoadmapScreen } from '../screens/roadmap/RoadmapScreen';
import { ChatbotScreen } from '../screens/chatbot/ChatbotScreen';
import { CommunityScreen } from '../screens/community/CommunityScreen';
import { CRMScreen } from '../screens/crm/CRMScreen';
import { CampagnesScreen } from '../screens/crm/CampagnesScreen';
import { RGPDScreen } from '../screens/rgpd/RGPDScreen';
import { TwoFASettingsScreen } from '../screens/profile/TwoFASettingsScreen';

const Tab = createBottomTabNavigator();
const Stack = createNativeStackNavigator();

function DashboardStack() {
  return (
    <Stack.Navigator>
      <Stack.Screen name="DashboardHome" component={DashboardScreen} options={{ title: 'Tableau de bord' }} />
      <Stack.Screen name="Roadmap" component={RoadmapScreen} options={{ title: 'Ma roadmap' }} />
      <Stack.Screen name="Chatbot" component={ChatbotScreen} options={{ title: 'AvenBot' }} />
      <Stack.Screen name="Community" component={CommunityScreen} options={{ title: 'Communauté' }} />
    </Stack.Navigator>
  );
}

function CatalogStack() {
  return (
    <Stack.Navigator>
      <Stack.Screen name="CatalogHome" component={CatalogScreen} options={{ title: 'Catalogue' }} />
      <Stack.Screen name="EtablissementDetail" component={EtablissementDetailScreen} options={{ title: 'Établissement' }} />
      <Stack.Screen name="FormationDetail" component={FormationDetailScreen} options={{ title: 'Formation' }} />
      <Stack.Screen name="SimulateurAdmission" component={SimulateurAdmissionScreen} options={{ title: 'Simulateur d\'admission' }} />
      <Stack.Screen name="Visite3D" component={Visite3DScreen} options={{ title: 'Visite virtuelle 3D' }} />
    </Stack.Navigator>
  );
}

function OrientationStack() {
  return (
    <Stack.Navigator>
      <Stack.Screen name="OrientationHome" component={OrientationHomeScreen} options={{ title: 'Orientation' }} />
      <Stack.Screen name="TakeTest" component={TakeTestScreen} options={{ title: 'Test en cours' }} />
      <Stack.Screen name="ResultatTest" component={ResultatTestScreen} options={{ title: 'Résultat' }} />
      <Stack.Screen name="RapportCombine" component={RapportCombineScreen} options={{ title: 'Rapport combiné' }} />
    </Stack.Navigator>
  );
}

function LibraryStack() {
  return (
    <Stack.Navigator>
      <Stack.Screen name="LibraryHome" component={LibraryScreen} options={{ title: 'Bibliothèque' }} />
    </Stack.Navigator>
  );
}

function ProfileStack() {
  return (
    <Stack.Navigator>
      <Stack.Screen name="ProfileHome" component={ProfileScreen} options={{ title: 'Profil' }} />
      <Stack.Screen name="TwoFASettings" component={TwoFASettingsScreen} options={{ title: 'Sécurité 2FA' }} />
      <Stack.Screen name="CRM" component={CRMScreen} options={{ title: 'CRM Établissement' }} />
      <Stack.Screen name="Campagnes" component={CampagnesScreen} options={{ title: 'Campagnes marketing' }} />
      <Stack.Screen name="RGPD" component={RGPDScreen} options={{ title: 'Mes données RGPD' }} />
    </Stack.Navigator>
  );
}

export function MainNavigator() {
  return (
    <Tab.Navigator
      screenOptions={{
        tabBarActiveTintColor: '#0EA5E9',
        tabBarInactiveTintColor: '#94A3B8',
        tabBarStyle: { backgroundColor: '#FFFFFF', borderTopColor: '#E2E8F0' },
        headerShown: false,
      }}
    >
      <Tab.Screen
        name="DashboardTab"
        component={DashboardStack}
        options={{
          tabBarLabel: 'Accueil',
          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="home" color={color} size={size} />
          ),
        }}
      />
      <Tab.Screen
        name="CatalogTab"
        component={CatalogStack}
        options={{
          tabBarLabel: 'Catalogue',
          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="school" color={color} size={size} />
          ),
        }}
      />
      <Tab.Screen
        name="OrientationTab"
        component={OrientationStack}
        options={{
          tabBarLabel: 'Tests',
          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="compass-outline" color={color} size={size} />
          ),
        }}
      />
      <Tab.Screen
        name="LibraryTab"
        component={LibraryStack}
        options={{
          tabBarLabel: 'Biblio',
          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="book-open-variant" color={color} size={size} />
          ),
        }}
      />
      <Tab.Screen
        name="ProfileTab"
        component={ProfileStack}
        options={{
          tabBarLabel: 'Profil',
          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="account" color={color} size={size} />
          ),
        }}
      />
    </Tab.Navigator>
  );
}
