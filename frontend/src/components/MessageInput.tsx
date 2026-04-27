import React, { useState } from "react";

interface MessageInputProps {
    onSendMessage: (message: string) => Promise<void>;
    isLoading: boolean;
    disabled?: boolean;
}

export const MessageInput: React.FC<MessageInputProps> = ({
    onSendMessage,
    isLoading,
    disabled = false,
}) => {
    const [input, setInput] = useState("");
    const textareaRef = React.useRef<HTMLTextAreaElement>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isLoading || disabled) return;

        const message = input.trim();
        setInput("");
        // Reset textarea height
        if (textareaRef.current) {
            textareaRef.current.style.height = "auto";
        }

        try {
            await onSendMessage(message);
        } catch (error) {
            // Error is handled in parent component
            setInput(message); // Restore input on error
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e as unknown as React.FormEvent);
        }
    };

    const handleTextareaChange = (
        e: React.ChangeEvent<HTMLTextAreaElement>,
    ) => {
        setInput(e.target.value);
        // Auto-resize textarea
        if (textareaRef.current) {
            textareaRef.current.style.height = "auto";
            textareaRef.current.style.height =
                Math.min(textareaRef.current.scrollHeight, 120) + "px";
        }
    };

    return (
        <form
            className="px-6 py-4 border-t border-gray-200 bg-white flex gap-3 items-end"
            onSubmit={handleSubmit}
        >
            <textarea
                ref={textareaRef}
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg text-sm focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 disabled:bg-gray-100 disabled:text-gray-500 resize-none"
                placeholder="Ask your coaching question... (Shift+Enter for new line)"
                value={input}
                onChange={handleTextareaChange}
                onKeyDown={handleKeyDown}
                disabled={isLoading || disabled}
                rows={1}
            />
            <button
                className="py-3 px-6 bg-gradient-to-r from-primary-500 to-secondary-500 hover:from-primary-600 hover:to-secondary-600 text-white rounded-lg font-semibold text-sm disabled:opacity-60 disabled:cursor-not-allowed whitespace-nowrap transition-all"
                type="submit"
                disabled={isLoading || !input.trim() || disabled}
                title="Send message (Enter)"
            >
                {isLoading ? "..." : "Send"}
            </button>
        </form>
    );
};
