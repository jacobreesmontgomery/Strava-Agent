/**
 * Domain models for the coaching agent frontend
 */

export interface Conversation {
    sessionId: string;
    messages: ConversationMessage[];
    createdAt: Date;
    lastAccessedAt: Date;
}

export interface ConversationMessage {
    id: string;
    query: string;
    response?: string;
    timestamp: Date;
}

export interface ChatState {
    sessionId: string | null;
    messages: ConversationMessage[];
    isLoading: boolean;
    error: string | null;
}
