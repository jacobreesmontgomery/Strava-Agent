import React, { useEffect, useState } from "react";
import { SessionContext } from "../types/api";
import { apiService } from "../services/api";

interface SidebarProps {
    currentSessionId: string | null;
    onSelectSession: (sessionId: string) => void;
    onNewChat: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
    currentSessionId,
    onSelectSession,
    onNewChat,
}) => {
    const [sessions, setSessions] = useState<SessionContext[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        loadSessions();
    }, []);

    const loadSessions = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const response = await apiService.listSessions();
            setSessions(response.sessions || []);
        } catch (err) {
            setError(
                err instanceof Error ? err.message : "Failed to load sessions",
            );
        } finally {
            setIsLoading(false);
        }
    };

    const handleDeleteSession = async (
        e: React.MouseEvent,
        sessionId: string,
    ) => {
        e.stopPropagation();
        try {
            await apiService.deleteSession(sessionId);
            setSessions(sessions.filter((s) => s.session_id !== sessionId));
        } catch (err) {
            setError(
                err instanceof Error ? err.message : "Failed to delete session",
            );
        }
    };

    const formatDate = (dateString: string | undefined): string => {
        if (!dateString) return "Unknown date";
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString("en-US", {
                month: "short",
                day: "numeric",
                hour: "2-digit",
                minute: "2-digit",
            });
        } catch {
            return "Invalid date";
        }
    };

    const getPreview = (session: SessionContext): string => {
        if (session.messages && session.messages.length > 0) {
            const lastMessage = session.messages[session.messages.length - 1];
            return lastMessage.query.substring(0, 50) + "...";
        }
        return "New conversation";
    };

    return (
        <aside className="w-80 bg-gray-900 border-r border-gray-800 flex flex-col h-screen overflow-hidden">
            <div className="p-4 border-b border-gray-800">
                <h2 className="text-white text-lg font-semibold mb-3">
                    Conversations
                </h2>
                <button
                    className="w-full py-2 px-4 bg-primary-500 hover:bg-primary-600 text-white rounded-lg font-semibold text-sm transition-colors"
                    onClick={onNewChat}
                >
                    + New Chat
                </button>
            </div>

            {error && (
                <div className="px-4 py-2 bg-red-500 text-white text-sm border-b border-red-700">
                    {error}
                </div>
            )}

            {isLoading && (
                <div className="px-4 py-4 text-center text-gray-400 text-sm">
                    Loading sessions...
                </div>
            )}

            <div className="flex-1 overflow-y-auto px-2 py-2">
                {sessions.length === 0 ? (
                    <div className="px-4 py-6 text-center text-gray-500 text-sm">
                        No conversations yet
                    </div>
                ) : (
                    sessions.map((session) => (
                        <div
                            key={session.session_id}
                            className={`p-3 mb-1 rounded-lg cursor-pointer flex justify-between items-start transition-colors ${
                                currentSessionId === session.session_id
                                    ? "bg-primary-500 text-white"
                                    : "bg-transparent text-gray-300 hover:bg-gray-800"
                            }`}
                            onClick={() => onSelectSession(session.session_id)}
                        >
                            <div className="flex-1 min-w-0 mr-2">
                                <div className="text-sm font-medium truncate">
                                    {getPreview(session)}
                                </div>
                                <div className="text-xs opacity-70 mt-1">
                                    {formatDate(session.created_at)}
                                </div>
                            </div>
                            <button
                                className="text-xl leading-none opacity-50 hover:opacity-100 w-6 h-6 flex items-center justify-center rounded hover:bg-black/20 transition-all"
                                onClick={(e) =>
                                    handleDeleteSession(e, session.session_id)
                                }
                                title="Delete session"
                            >
                                ×
                            </button>
                        </div>
                    ))
                )}
            </div>
        </aside>
    );
};
