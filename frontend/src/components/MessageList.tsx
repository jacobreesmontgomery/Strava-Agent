import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ConversationMessage } from "../types";

interface MessageListProps {
    messages: ConversationMessage[];
    isLoading: boolean;
}

export const MessageList: React.FC<MessageListProps> = ({
    messages,
    isLoading,
}) => {
    const containerRef = React.useRef<HTMLDivElement>(null);

    React.useEffect(() => {
        // Auto-scroll to bottom when new messages arrive
        if (containerRef.current) {
            containerRef.current.scrollTop = containerRef.current.scrollHeight;
        }
    }, [messages]);

    const formatTime = (date: Date): string => {
        return date.toLocaleTimeString("en-US", {
            hour: "2-digit",
            minute: "2-digit",
        });
    };

    return (
        <div
            className="flex-1 overflow-y-auto p-6 flex flex-col gap-4 bg-white"
            ref={containerRef}
        >
            {messages.length === 0 ? (
                <div className="flex-1 flex items-center justify-center">
                    <p className="text-gray-400 text-center">
                        No messages yet. Start a conversation!
                    </p>
                </div>
            ) : (
                messages.map((msg) => (
                    <div
                        key={msg.id}
                        className="flex flex-col gap-2 animate-fadeIn"
                    >
                        {/* User Message */}
                        <div className="flex justify-end">
                            <div className="flex items-end gap-2 max-w-xs lg:max-w-md">
                                <div className="bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-xl rounded-br-sm px-4 py-3 text-sm leading-relaxed">
                                    {msg.query}
                                </div>
                                <span className="text-xs text-gray-400 opacity-60 whitespace-nowrap mb-1">
                                    {formatTime(msg.timestamp)}
                                </span>
                            </div>
                        </div>

                        {/* Agent Message */}
                        {msg.response && (
                            <div className="flex justify-start">
                                <div className="flex items-end gap-2 max-w-xs lg:max-w-md">
                                    <div className="bg-gray-100 text-gray-800 rounded-xl rounded-bl-sm px-4 py-3 text-sm leading-relaxed prose prose-sm max-w-none">
                                        <ReactMarkdown
                                            remarkPlugins={[remarkGfm]}
                                        >
                                            {msg.response}
                                        </ReactMarkdown>
                                    </div>
                                    <span className="text-xs text-gray-400 opacity-60 whitespace-nowrap mb-1">
                                        {formatTime(msg.timestamp)}
                                    </span>
                                </div>
                            </div>
                        )}
                    </div>
                ))
            )}
            {isLoading && (
                <div className="flex justify-start">
                    <div className="bg-gray-100 rounded-xl rounded-bl-sm px-4 py-3">
                        <div className="flex gap-1">
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse"></div>
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse animation-delay-200"></div>
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse animation-delay-400"></div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};
