/**
 * Passation d'un test — questions + save answer + submit.
 */
import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, ActivityIndicator, ScrollView } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { OrientationService } from '../../services/orientation';
import { AVENSU_COLORS, SPACING, TYPOGRAPHY } from '../../theme';

type Nav = NativeStackNavigationProp<any>;

export function TakeTestScreen() {
  const route = useRoute<any>();
  const navigation = useNavigation<Nav>();
  const [session, setSession] = useState<any>(null);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [answers, setAnswers] = useState<Record<string, any>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const result = await OrientationService.startTest(route.params.test_id);
        setSession(result);
      } catch (e: any) {
        Alert.alert('Erreur', e?.response?.data?.error || e.message);
      } finally {
        setIsLoading(false);
      }
    })();
  }, [route.params.test_id]);

  const handleAnswer = async (questionId: string, value: any) => {
    setAnswers(a => ({ ...a, [questionId]: value }));
    try {
      await OrientationService.saveAnswer(session.reponse_id, { question_id: questionId, ...value });
    } catch (e) {
      // silent — will retry on submit
    }
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      const result = await OrientationService.submitTest(session.reponse_id);
      navigation.replace('ResultatTest', { resultat: result });
    } catch (e: any) {
      Alert.alert('Erreur', e?.response?.data?.error || e.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading || !session) {
    return <View style={styles.center}><ActivityIndicator color={AVENSU_COLORS.primary} size="large" /></View>;
  }

  const questions = session.test?.questions_actives || session.test?.questions || [];
  const question = questions[currentIdx];
  const isLast = currentIdx === questions.length - 1;
  const progress = ((currentIdx + 1) / questions.length) * 100;

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>{session.test.nom}</Text>
        <View style={styles.progressBar}>
          <View style={[styles.progressFill, { width: `${progress}%` }]} />
        </View>
        <Text style={styles.progressText}>Question {currentIdx + 1} / {questions.length}</Text>
      </View>

      <ScrollView style={styles.content}>
        <Text style={styles.questionText}>{question?.texte || question?.enonce}</Text>

        {question?.type === 'ECHELLE_LIKERT' && (
          <View style={styles.likertScale}>
            {[1, 2, 3, 4, 5].map(n => (
              <TouchableOpacity
                key={n}
                style={[styles.likertButton, answers[question.id]?.valeur_echelle === n && styles.likertSelected]}
                onPress={() => handleAnswer(question.id, { valeur_echelle: n })}
              >
                <Text style={[styles.likertText, answers[question.id]?.valeur_echelle === n && styles.likertTextSelected]}>{n}</Text>
              </TouchableOpacity>
            ))}
          </View>
        )}

        {question?.type === 'OUVERTE' && (
          <TextInput
            style={styles.textInput}
            multiline
            placeholder="Saisissez votre réponse..."
            value={answers[question.id]?.texte || ''}
            onChangeText={t => handleAnswer(question.id, { texte: t })}
          />
        )}

        {(question?.type === 'CHOIX_UNIQUE' || question?.type === 'CHOIX_MULTIPLE') && (
          <View>
            {question.choices?.map((c: any) => (
              <TouchableOpacity
                key={c.id}
                style={[
                  styles.choiceButton,
                  answers[question.id]?.choice_id === c.id && styles.choiceSelected,
                ]}
                onPress={() => handleAnswer(question.id, { choice_id: c.id })}
              >
                <Text style={[
                  styles.choiceText,
                  answers[question.id]?.choice_id === c.id && styles.choiceTextSelected,
                ]}>{c.texte || c.libelle}</Text>
              </TouchableOpacity>
            ))}
          </View>
        )}
      </ScrollView>

      <View style={styles.footer}>
        {currentIdx > 0 && (
          <TouchableOpacity
            style={[styles.navButton, styles.secondaryButton]}
            onPress={() => setCurrentIdx(i => i - 1)}
          >
            <Text style={styles.secondaryText}>← Précédent</Text>
          </TouchableOpacity>
        )}
        {!isLast ? (
          <TouchableOpacity
            style={[styles.navButton, { flex: 2 }]}
            onPress={() => setCurrentIdx(i => i + 1)}
            disabled={!answers[question.id]}
          >
            <Text style={styles.navText}>Suivant →</Text>
          </TouchableOpacity>
        ) : (
          <TouchableOpacity
            style={[styles.navButton, { flex: 2, backgroundColor: AVENSU_COLORS.success }]}
            onPress={handleSubmit}
            disabled={isSubmitting}
          >
            {isSubmitting ? <ActivityIndicator color="#FFFFFF" /> : <Text style={styles.navText}>✓ Terminer</Text>}
          </TouchableOpacity>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F8FAFC' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  header: { padding: SPACING.lg, backgroundColor: AVENSU_COLORS.primary },
  title: { ...TYPOGRAPHY.h3, color: '#FFFFFF', marginBottom: SPACING.sm },
  progressBar: { height: 6, backgroundColor: 'rgba(255,255,255,0.3)', borderRadius: 3, overflow: 'hidden' },
  progressFill: { height: '100%', backgroundColor: '#FFFFFF' },
  progressText: { color: '#FFFFFF', opacity: 0.85, fontSize: 12, marginTop: SPACING.xs },
  content: { padding: SPACING.lg },
  questionText: { ...TYPOGRAPHY.h3, color: AVENSU_COLORS.textPrimary, marginBottom: SPACING.lg, lineHeight: 26 },
  likertScale: { flexDirection: 'row', justifyContent: 'space-between', marginVertical: SPACING.lg },
  likertButton: { width: 50, height: 50, borderRadius: 25, borderWidth: 2, borderColor: AVENSU_COLORS.outline, justifyContent: 'center', alignItems: 'center' },
  likertSelected: { backgroundColor: AVENSU_COLORS.primary, borderColor: AVENSU_COLORS.primary },
  likertText: { fontSize: 18, fontWeight: 'bold', color: AVENSU_COLORS.textPrimary },
  likertTextSelected: { color: '#FFFFFF' },
  textInput: {
    borderWidth: 1, borderColor: AVENSU_COLORS.outline, borderRadius: 12,
    padding: SPACING.md, fontSize: 16, backgroundColor: '#FFFFFF',
    minHeight: 150, textAlignVertical: 'top',
  },
  choiceButton: { backgroundColor: '#FFFFFF', padding: SPACING.lg, borderRadius: 12, marginBottom: SPACING.sm, borderWidth: 1, borderColor: AVENSU_COLORS.outline },
  choiceSelected: { backgroundColor: '#E0F2FE', borderColor: AVENSU_COLORS.primary },
  choiceText: { color: AVENSU_COLORS.textPrimary, fontSize: 16 },
  choiceTextSelected: { color: AVENSU_COLORS.primaryDark, fontWeight: '600' },
  footer: { flexDirection: 'row', padding: SPACING.md, backgroundColor: '#FFFFFF', gap: SPACING.sm },
  navButton: { backgroundColor: AVENSU_COLORS.primary, padding: SPACING.md, borderRadius: 12, alignItems: 'center', flex: 1 },
  secondaryButton: { backgroundColor: 'transparent', borderWidth: 1, borderColor: AVENSU_COLORS.outline },
  navText: { color: '#FFFFFF', ...TYPOGRAPHY.button },
  secondaryText: { color: AVENSU_COLORS.textPrimary },
});
