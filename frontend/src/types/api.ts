/**
 * API request and response contracts for the coaching agent backend
 */

export interface CoachingRequest {
    query: string;
    session_id?: string;
}

export interface CoachingResponse {
    response: string;
    session_id?: string;
    metadata?: Record<string, unknown>;
}

export interface Message {
    query: string;
    response: string;
    timestamp: string;
}

export interface SessionContext {
    session_id: string;
    messages: Message[];
    created_at?: string;
    last_accessed?: string;
}

export interface CreateSessionResponse {
    session_id: string;
    message: string;
}

export interface SessionHistoryResponse {
    session_id: string;
    messages: Message[];
    created_at?: string;
    last_accessed?: string;
}

export interface ListSessionsResponse {
    sessions: SessionContext[];
    count: number;
}

export interface ErrorResponse {
    detail: string;
    error_code?: string;
}

export interface HealthCheckResponse {
    status: "healthy" | "unhealthy";
    message: string;
}
