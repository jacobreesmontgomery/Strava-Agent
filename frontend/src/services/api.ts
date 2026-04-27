/**
 * API service for communicating with the coaching agent backend
 */

import axios, { AxiosInstance } from "axios";
import config from "../config";
import {
    CoachingRequest,
    CoachingResponse,
    CreateSessionResponse,
    SessionHistoryResponse,
    ListSessionsResponse,
} from "../types/api";

class CoachingAgentService {
    private axiosInstance: AxiosInstance;
    private baseURL: string;

    constructor(baseURL = config.API_URL) {
        this.baseURL = baseURL;
        this.axiosInstance = axios.create({
            baseURL: this.baseURL,
            headers: {
                "Content-Type": "application/json",
            },
        });
    }

    /**
     * Send a coaching query to the agent
     */
    async askCoachingAgent(
        request: CoachingRequest,
    ): Promise<CoachingResponse> {
        try {
            const response = await this.axiosInstance.post<CoachingResponse>(
                "/api/coaching/ask",
                request,
            );
            return response.data;
        } catch (error) {
            throw this.handleError(error);
        }
    }

    /**
     * Check the health status of the coaching agent
     */
    async healthCheck(): Promise<boolean> {
        try {
            await this.axiosInstance.post("/api/coaching/health");
            return true;
        } catch {
            return false;
        }
    }

    /**
     * Create a new session
     */
    async createSession(): Promise<CreateSessionResponse> {
        try {
            const response =
                await this.axiosInstance.post<CreateSessionResponse>(
                    "/api/sessions/create",
                );
            return response.data;
        } catch (error) {
            throw this.handleError(error);
        }
    }

    /**
     * Get session history by session ID
     */
    async getSessionHistory(
        sessionId: string,
    ): Promise<SessionHistoryResponse> {
        try {
            const response =
                await this.axiosInstance.get<SessionHistoryResponse>(
                    `/api/sessions/${sessionId}`,
                );
            return response.data;
        } catch (error) {
            throw this.handleError(error);
        }
    }

    /**
     * Delete a session
     */
    async deleteSession(sessionId: string): Promise<void> {
        try {
            await this.axiosInstance.delete(`/api/sessions/${sessionId}`);
        } catch (error) {
            throw this.handleError(error);
        }
    }

    /**
     * List all active sessions
     */
    async listSessions(): Promise<ListSessionsResponse> {
        try {
            const response =
                await this.axiosInstance.get<ListSessionsResponse>(
                    "/api/sessions",
                );
            return response.data;
        } catch (error) {
            throw this.handleError(error);
        }
    }

    private handleError(error: unknown): Error {
        if (axios.isAxiosError(error)) {
            const message =
                (error.response?.data as Record<string, unknown>)?.detail ||
                error.message;
            return new Error(`API Error: ${message}`);
        }
        return new Error("An unexpected error occurred");
    }
}

export const apiService = new CoachingAgentService();
export default CoachingAgentService;
