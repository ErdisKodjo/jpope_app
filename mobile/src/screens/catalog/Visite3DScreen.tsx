/**
 * Visite 3D — WebView Matterport/Sketchfab/360° + galerie.
 */
import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ActivityIndicator, FlatList, Image } from 'react-native';
import { WebView } from 'react-native-webview';
import { CatalogService } from '../../services/catalog';
import { AVENSU_COLORS, SPACING, TYPOGRAPHY } from '../../theme';

export function Visite3DScreen({ route }: { route: any }) {
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [currentScene, setCurrentScene] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const result = await CatalogService.getVisite3D(route.params.id);
        setData(result);
        if (result.visite_virtuelle_url) {
          setCurrentScene(result.visite_virtuelle_url);
        } else if (result.galerie_3d?.length > 0) {
          setCurrentScene(result.galerie_3d[0].url);
        }
      } finally {
        setIsLoading(false);
      }
    })();
  }, [route.params.id]);

  if (isLoading) {
    return <View style={styles.center}><ActivityIndicator color={AVENSU_COLORS.primary} size="large" /></View>;
  }

  if (!currentScene) {
    return (
      <View style={styles.center}>
        <Text style={styles.emptyIcon}>🌐</Text>
        <Text style={styles.emptyText}>Aucune visite virtuelle disponible pour cet établissement.</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.webviewContainer}>
        <WebView
          source={{ uri: currentScene }}
          allowsInlineMediaPlayback
          mediaPlaybackRequiresUserAction={false}
          startInLoadingState
          renderLoading={() => <ActivityIndicator color={AVENSU_COLORS.primary} size="large" style={{ marginTop: 50 }} />}
        />
      </View>

      {data?.galerie_3d?.length > 1 && (
        <View style={styles.galerieContainer}>
          <Text style={styles.galerieTitle}>Galerie 3D</Text>
          <FlatList
            horizontal
            data={data.galerie_3d}
            keyExtractor={(item, idx) => idx.toString()}
            renderItem={({ item }) => (
              <TouchableOpacity
                style={[styles.sceneCard, currentScene === item.url && styles.sceneCardActive]}
                onPress={() => setCurrentScene(item.url)}
              >
                {item.vignette && <Image source={{ uri: item.vignette }} style={styles.sceneVignette} />}
                <Text style={styles.sceneTitre} numberOfLines={1}>{item.titre}</Text>
                <Text style={styles.sceneType}>{item.type}</Text>
              </TouchableOpacity>
            )}
          />
        </View>
      )}

      {data?.video_presentation_url && !data.galerie_3d?.length && (
        <TouchableOpacity
          style={styles.videoButton}
          onPress={() => setCurrentScene(data.video_presentation_url)}
        >
          <Text style={styles.videoButtonText}>▶ Vidéo de présentation</Text>
        </TouchableOpacity>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000000' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: SPACING.lg },
  emptyIcon: { fontSize: 64, marginBottom: SPACING.md },
  emptyText: { color: AVENSU_COLORS.textSecondary, textAlign: 'center' },
  webviewContainer: { flex: 1 },
  galerieContainer: { backgroundColor: '#FFFFFF', padding: SPACING.md, maxHeight: 180 },
  galerieTitle: { ...TYPOGRAPHY.h3, marginBottom: SPACING.sm },
  sceneCard: { width: 140, marginRight: SPACING.md, borderWidth: 2, borderColor: 'transparent', borderRadius: 8, padding: SPACING.xs },
  sceneCardActive: { borderColor: AVENSU_COLORS.primary },
  sceneVignette: { width: '100%', height: 80, borderRadius: 6 },
  sceneTitre: { fontSize: 12, marginTop: SPACING.xs, color: AVENSU_COLORS.textPrimary },
  sceneType: { fontSize: 10, color: AVENSU_COLORS.textTertiary },
  videoButton: { backgroundColor: AVENSU_COLORS.primary, padding: SPACING.md, margin: SPACING.md, borderRadius: 12, alignItems: 'center' },
  videoButtonText: { color: '#FFFFFF', ...TYPOGRAPHY.button },
});
