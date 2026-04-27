# Coaching Agent

A full-stack coaching agent monorepo featuring a Python FastAPI backend powered by LangGraph and Anthropic, with a React + TypeScript frontend chatbot interface.

## Description

This monorepo implements an intelligent coaching agent that leverages LangGraph and Anthropic's Claude API to provide personalized coaching experiences. The project is organized into two main directories:

- **Backend** (`src/`): Python FastAPI coaching agent with LangGraph, clean layered architecture, dependency injection, and session management
- **Frontend** (`frontend/`): React + TypeScript chatbot interface with Tailwind CSS, real-time messaging, and session history

## Installation

### Prerequisites

- Python 3.13+ (for backend)
- Node.js 16+ (for frontend)

### Backend Setup

```bash
# Install Python dependencies
uv sync
```

### Frontend Setup

```bash
cd frontend
npm install
```

## Running the Application

### Backend Development Server

```bash
cd src
python -m uvicorn server:app --reload
```

The API will be available at `http://localhost:8000` with:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Frontend Development Server

```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Running Both

Open two terminals:

1. Terminal 1: `cd src && python -m uvicorn server:app --reload`
2. Terminal 2: `cd frontend && npm run dev`

Then visit `http://localhost:3000`

## Project Structure

This monorepo is organized as follows:

```
.
├── src/                           # Backend - Python FastAPI application
│   ├── setup/
│   │   ├── __init__.py
│   │   └── dependencies.py        # Dependency injection configuration
│   ├── models/
│   │   ├── __init__.py
│   │   ├── coaching.py
│   │   └── sessions.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── coaching_agent_service.py
│   │   └── session_service.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── coaching.py
│   │   └── sessions.py
│   ├── coaching_agent.py
│   ├── server.py
│   └── assets/
│       └── strava_auth.json
├── frontend/                      # Frontend - React + TypeScript application
│   ├── src/
│   │   ├── components/           # Reusable React components
│   │   │   ├── ChatContainer.tsx
│   │   │   ├── MessageInput.tsx
│   │   │   ├── MessageList.tsx
│   │   │   └── Sidebar.tsx
│   │   ├── services/
│   │   │   └── api.ts            # API communication layer
│   │   ├── types/
│   │   │   ├── api.ts
│   │   │   └── index.ts
│   │   ├── styles/
│   │   │   └── index.css
│   │   ├── App.tsx
│   │   ├── config.ts
│   │   └── main.tsx
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── tsconfig.json
├── pyproject.toml
└── README.md
```

## Backend Architecture

### Overview

The backend follows a clean layered architecture with proper separation of concerns:

```
User Request
    ↓
Route Layer (FastAPI Endpoint)
    ↓
Dependency Injection (get_coaching_agent_service, get_session_service)
    ↓
Service Layer (CoachingAgentService, SessionService)
    ↓
Agent/Business Logic (CoachingAgent, Session Management)
    ↓
Response → Back through Service → Route → User
```

## Frontend

The frontend is a React + TypeScript application providing a modern chatbot interface:

- **Components**: Modular React components for chat interface, messages, sidebar, and input
- **Styling**: Tailwind CSS for responsive, utility-first styling
- **Build Tool**: Vite for fast development and optimized production builds
- **API Integration**: Centralized API service layer for backend communication
- **Real-time Messaging**: Live chat with conversation history and session management

### Getting Started

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000` in your browser.

## Backend Components

Handles centralized service initialization and dependency injection.

**Key Features:**

- Singleton pattern for service instances
- `init_services()` - Initializes all services at app startup
- `get_coaching_agent_service()` - FastAPI dependency for CoachingAgentService
- `get_session_service()` - FastAPI dependency for SessionService

**Usage in Endpoints:**

```python
@router.post("/ask")
async def ask_coaching_agent(
    request: CoachingRequestModel,
    coaching_service: CoachingAgentService = Depends(get_coaching_agent_service),
):
    # Service is automatically injected
```

### Session Service (`services/session_service.py`)

Manages user sessions and conversation history independently.

**Key Methods:**

- `create_session()` - Create a new session with UUID
- `get_session(session_id)` - Retrieve session data
- `add_message(session_id, query, response)` - Store conversation messages
- `add_analysis(session_id, analysis)` - Store analysis data
- `get_session_history(session_id)` - Get full session history
- `clear_session(session_id)` - Delete session
- `list_sessions()` - List all active sessions
- `get_session_context(session_id)` - Get context for coaching requests

### Coaching Agent Service (`services/coaching_agent_service.py`)

Orchestrates agent invocation and integrates with SessionService.

**Key Methods:**

- `__init__(session_service)` - Accepts SessionService for dependency injection
- `process_coaching_request()` - Main flow for handling coaching requests
- `_invoke_agent()` - Call the CoachingAgent
- `_generate_analysis()` - Generate additional analysis if requested
- `_build_context_aware_query()` - Enhance queries with conversation history

### Coaching Routes (`routes/coaching.py`)

RESTful API for coaching agent interactions.

**Endpoints:**

- `POST /api/coaching/ask` - Ask coaching agent
- `POST /api/coaching/health` - Health check

### Session Routes (`routes/sessions.py`)

RESTful API for session management.

**Endpoints:**

- `POST /api/sessions/create` - Create new session
- `GET /api/sessions/{session_id}` - Get session details
- `DELETE /api/sessions/{session_id}` - Delete session
- `GET /api/sessions` - List all sessions

### Pydantic Models (`models/coaching_models.py`)

Type-safe request/response definitions.

**Models:**

- `CoachingRequestModel` - Input with query, optional session_id, include_analysis flag
- `CoachingResponseModel` - Output with response, session_id, analysis, metadata
- `ErrorResponseModel` - Standardized error responses

## API Usage Examples

### Create New Session

```bash
curl -X POST http://localhost:8000/api/sessions/create
```

### Ask Coaching Question (without session)

```bash
curl -X POST http://localhost:8000/api/coaching/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "How should I train?", "include_analysis": true}'
```

### Continue Conversation (with session)

```bash
curl -X POST http://localhost:8000/api/coaching/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What about nutrition?", "session_id": "your-session-id"}'
```

### Get Session History

```bash
curl -X GET http://localhost:8000/api/sessions/your-session-id
```

### List All Sessions

```bash
curl -X GET http://localhost:8000/api/sessions
```

### Delete Session

```bash
curl -X DELETE http://localhost:8000/api/sessions/your-session-id
```

## Architecture Benefits

1. **Separation of Concerns**: Each layer has a single responsibility
2. **Dependency Injection**: Services are loosely coupled and testable
3. **Session Management**: Decoupled from coaching logic
4. **Scalability**: Easy to add new services or endpoints
5. **Maintainability**: Clear data flow and responsibilities
6. **Type Safety**: Pydantic models ensure input/output validation
7. **Documentation**: FastAPI auto-generates API docs
8. **Flexibility**: Services can be replaced or extended without affecting routes

## Requirements

- Python 3.13+
- Node.js 16+
- See `pyproject.toml` for backend dependencies
- See `frontend/package.json` for frontend dependencies

## License

MIT
