/**
 * Chatbot AvenBot — chat IA avec historique.
 */
import React, { useState, useRef, useEffect } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, FlatList, KeyboardAvoidingView, Platform } from 'react-native';
import { AVENSU_COLORS, SPACING, TYPOGRAPHY } from '../../theme';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export function ChatbotScreen() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Bonjour 👋 Je suis AvenBot, votre assistant IA d\'orientation. Posez-moi une question sur les filières, métiers, écoles ou préparation d\'examens !',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const flatlistRef = useRef<FlatList>(null);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };
    setMessages(m => [...m, userMsg]);
    setInput('');
    setIsTyping(true);

    // TODO: brancher WebSocket Django Channels ou API REST
    // Pour démo : réponse simulée
    setTimeout(() => {
      const botMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Je suis en mode démo. Connectez le WebSocket pour activer l\'IA. Voici quelques suggestions :\n\n• "Quelles filières pour un profil RIA ?"\n• "Compare les écoles d\'ingénieur à Lomé"\n• "Comment préparer le concours ESGIS ?"',
        timestamp: new Date(),
      };
      setMessages(m => [...m, botMsg]);
      setIsTyping(false);
    }, 1500);
  };

  useEffect(() => {
    flatlistRef.current?.scrollToEnd({ animated: true });
  }, [messages]);

  const renderItem = ({ item }: { item: Message }) => (
    <View style={[styles.message, item.role === 'user' ? styles.userMessage : styles.botMessage]}>
      <Text style={styles.messageText}>{item.content}</Text>
      <Text style={styles.timestamp}>{item.timestamp.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}</Text>
    </View>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>🤖 AvenBot</Text>
        <Text style={styles.headerSub}>Assistant IA 24/7</Text>
      </View>

      <FlatList
        ref={flatlistRef}
        data={messages}
        keyExtractor={item => item.id}
        renderItem={renderItem}
        contentContainerStyle={{ padding: SPACING.md }}
        ItemSeparatorComponent={() => <View style={{ height: SPACING.sm }} />}
      />

      {isTyping && (
        <View style={styles.typingIndicator}>
          <Text style={styles.typingText}>AvenBot écrit...</Text>
        </View>
      )}

      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        style={styles.inputContainer}
      >
        <TextInput
          style={styles.input}
          value={input}
          onChangeText={setInput}
          placeholder="Posez votre question..."
          multiline
          maxLength={500}
        />
        <TouchableOpacity style={styles.sendButton} onPress={sendMessage} disabled={!input.trim()}>
          <Text style={styles.sendText}>↑</Text>
        </TouchableOpacity>
      </KeyboardAvoidingView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F8FAFC' },
  header: { padding: SPACING.md, backgroundColor: AVENSU_COLORS.primary },
  headerTitle: { ...TYPOGRAPHY.h3, color: '#FFFFFF' },
  headerSub: { color: '#FFFFFF', opacity: 0.85, fontSize: 12 },
  message: { maxWidth: '80%', padding: SPACING.md, borderRadius: 12 },
  userMessage: { alignSelf: 'flex-end', backgroundColor: AVENSU_COLORS.primary },
  botMessage: { alignSelf: 'flex-start', backgroundColor: '#FFFFFF' },
  messageText: { color: '#FFFFFF', fontSize: 14, lineHeight: 20 },
  timestamp: { color: 'rgba(255,255,255,0.7)', fontSize: 10, marginTop: 4, textAlign: 'right' },
  typingIndicator: { padding: SPACING.sm, alignItems: 'center' },
  typingText: { color: AVENSU_COLORS.textTertiary, fontStyle: 'italic' },
  inputContainer: { flexDirection: 'row', padding: SPACING.md, backgroundColor: '#FFFFFF', borderTopWidth: 1, borderTopColor: '#E2E8F0', gap: SPACING.sm },
  input: { flex: 1, borderWidth: 1, borderColor: AVENSU_COLORS.outline, borderRadius: 24, paddingHorizontal: SPACING.lg, paddingVertical: SPACING.sm, fontSize: 16, maxHeight: 100 },
  sendButton: { width: 48, height: 48, borderRadius: 24, backgroundColor: AVENSU_COLORS.primary, justifyContent: 'center', alignItems: 'center' },
  sendText: { color: '#FFFFFF', fontSize: 24 },
});
