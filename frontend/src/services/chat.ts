import { api } from './api';
import type { AnalysisData } from '../types/analysis';
import type { ChatMessage } from '../types/chat';

export async function sendChatMessage(
  messages: ChatMessage[],
  context: AnalysisData,
): Promise<string> {
  const { data } = await api.post<{ reply: string }>('/chat', { messages, context });
  return data.reply;
}
