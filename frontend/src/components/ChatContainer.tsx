import React from "react";
import { MessageList } from "./MessageList";
import { MessageInput } from "./MessageInput";
import { ConversationMessage, ChatState } from "../types";
import { CoachingRequest } from "../types/api";
import { apiService } from "../services/api";

interface ChatContainerProps {
    chatState: ChatState;
    onStateChange: (state: Partial<ChatState>) => void;
}

export const ChatContainer: React.FC<ChatContainerProps> = ({
    chatState,
    onStateChange,
}) => {
    const handleSendMessage = async (query: string) => {
        // Show user's question immediately
        const messageId = `${Date.now()}-${Math.random()}`;
        const userMessage: ConversationMessage = {
            id: messageId,
            query,
            response: undefined,
            timestamp: new Date(),
        };

        const messagesWithUserQuery = [...chatState.messages, userMessage];

        onStateChange({
            messages: messagesWithUserQuery,
            isLoading: true,
            error: null,
        });

        try {
            const request: CoachingRequest = {
                query,
                session_id: chatState.sessionId || undefined,
            };

            const response = await apiService.askCoachingAgent(request);

            // Update message with response
            const updatedMessages = messagesWithUserQuery.map((msg) =>
                msg.id === messageId
                    ? { ...msg, response: response.response }
                    : msg,
            );

            // Update session ID if this was the first message (created a new session)
            if (!chatState.sessionId && response.session_id) {
                onStateChange({
                    sessionId: response.session_id,
                    messages: updatedMessages,
                    isLoading: false,
                });
            } else {
                onStateChange({
                    messages: updatedMessages,
                    isLoading: false,
                });
            }
        } catch (err) {
            const errorMessage =
                err instanceof Error ? err.message : "Failed to send message";
            onStateChange({
                error: errorMessage,
                isLoading: false,
            });
        }
    };

    return (
        <div className="flex flex-col h-full bg-white">
            <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
                {chatState.sessionId ? (
                    <span className="text-sm text-gray-600 font-medium">
                        Session: {chatState.sessionId.substring(0, 8)}...
                    </span>
                ) : (
                    <span className="text-sm text-gray-600 font-medium">
                        New Conversation
                    </span>
                )}
            </div>

            <MessageList
                messages={chatState.messages}
                isLoading={chatState.isLoading}
            />

            {chatState.error && (
                <div className="px-6 py-3 bg-red-50 border-t border-red-200">
                    <p className="text-sm text-red-700">{chatState.error}</p>
                </div>
            )}

            <MessageInput
                onSendMessage={handleSendMessage}
                isLoading={chatState.isLoading}
            />
        </div>
    );
};
