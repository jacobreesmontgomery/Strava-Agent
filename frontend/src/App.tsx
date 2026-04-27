import React, { useState, useEffect } from "react";
import { Sidebar } from "./components/Sidebar";
import { ChatContainer } from "./components/ChatContainer";
import { ChatState } from "./types";
import { apiService } from "./services/api";

export const App: React.FC = () => {
    const [chatState, setChatState] = useState<ChatState>({
        sessionId: null,
        messages: [],
        isLoading: false,
        error: null,
    });

    const [isInitializing, setIsInitializing] = useState(true);
    const [connectionError, setConnectionError] = useState<string | null>(null);

    useEffect(() => {
        // Check connection to backend on mount
        checkBackendConnection();
    }, []);

    const checkBackendConnection = async () => {
        try {
            const isHealthy = await apiService.healthCheck();
            if (!isHealthy) {
                setConnectionError(
                    "Backend service is not responding. Please ensure the server is running on http://localhost:8000",
                );
            }
        } catch (error) {
            setConnectionError(
                "Cannot connect to backend. Please ensure the server is running on http://localhost:8000",
            );
        } finally {
            setIsInitializing(false);
        }
    };

    const handleNewChat = async () => {
        try {
            const response = await apiService.createSession();
            setChatState({
                sessionId: response.session_id,
                messages: [],
                isLoading: false,
                error: null,
            });
        } catch (error) {
            const errorMessage =
                error instanceof Error
                    ? error.message
                    : "Failed to create new chat";
            setChatState((prev) => ({
                ...prev,
                error: errorMessage,
            }));
        }
    };

    const handleSelectSession = async (sessionId: string) => {
        try {
            const history = await apiService.getSessionHistory(sessionId);
            const messages = (history.messages || []).map((msg, index) => ({
                id: `${sessionId}-${index}`,
                query: msg.query,
                response: msg.response,
                timestamp: new Date(msg.timestamp),
            }));

            setChatState({
                sessionId: history.session_id,
                messages,
                isLoading: false,
                error: null,
            });
        } catch (error) {
            const errorMessage =
                error instanceof Error
                    ? error.message
                    : "Failed to load session";
            setChatState((prev) => ({
                ...prev,
                error: errorMessage,
            }));
        }
    };

    const handleStateChange = (newState: Partial<ChatState>) => {
        setChatState((prev) => ({
            ...prev,
            ...newState,
        }));
    };

    if (isInitializing) {
        return (
            <div className="flex flex-col items-center justify-center h-screen gap-5 bg-gradient-to-br from-primary-500 to-secondary-500 text-white">
                <div className="border-4 border-white/30 rounded-full border-t-white w-10 h-10 animate-spin"></div>
                <p className="text-lg">Initializing...</p>
            </div>
        );
    }

    return (
        <div className="flex h-screen w-screen bg-white">
            <Sidebar
                currentSessionId={chatState.sessionId}
                onSelectSession={handleSelectSession}
                onNewChat={handleNewChat}
            />
            <main className="flex-1 flex flex-col overflow-hidden">
                {connectionError && (
                    <div className="flex flex-col items-center justify-center h-full gap-5 bg-gradient-to-br from-primary-500 to-secondary-500 text-white p-10">
                        <h3 className="text-2xl font-semibold">
                            Connection Error
                        </h3>
                        <p className="text-center max-w-lg text-base">
                            {connectionError}
                        </p>
                        <button
                            className="mt-4 px-6 py-2 bg-white text-primary-500 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
                            onClick={checkBackendConnection}
                        >
                            Retry
                        </button>
                    </div>
                )}
                {!connectionError && (
                    <ChatContainer
                        chatState={chatState}
                        onStateChange={handleStateChange}
                    />
                )}
            </main>
        </div>
    );
};

export default App;
