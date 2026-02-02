# 🏗️ AI Chatbot - Architecture & Flow Diagrams

## System Architecture Diagram

```mermaid
graph TB
    User["👤 User Browser"]
    Frontend["🎨 Streamlit Frontend<br/>streamlit_frontend_database.py"]
    SessionMgr["🔐 Session Manager<br/>UUID-based isolation"]
    
    Backend["⚙️ LangGraph Backend<br/>langgraph_database_backend.py"]
    StateGraph["📊 State Graph<br/>ChatState Management"]
    ChatNode["💬 Chat Node<br/>Message Processing"]
    
    Groq["🚀 Groq API<br/>Llama 3.3 70B"]
    
    SQLite["💾 SQLite Database<br/>chatbot.db"]
    Checkpointer["📝 Checkpointer<br/>State Persistence"]
    
    User -->|enters message| Frontend
    Frontend -->|unique session ID| SessionMgr
    SessionMgr -->|send message| Backend
    Backend -->|invoke| StateGraph
    StateGraph -->|execute| ChatNode
    ChatNode -->|inference| Groq
    Groq -->|response| ChatNode
    ChatNode -->|state update| StateGraph
    StateGraph -->|save checkpoint| Checkpointer
    Checkpointer -->|persist| SQLite
    SQLite -->|retrieve history| Frontend
    Frontend -->|stream response| User
    
    style User fill:#e1f5ff
    style Frontend fill:#fff3e0
    style SessionMgr fill:#f3e5f5
    style Backend fill:#e8f5e9
    style StateGraph fill:#fce4ec
    style ChatNode fill:#e0f2f1
    style Groq fill:#fff9c4
    style SQLite fill:#f1f8e9
    style Checkpointer fill:#ede7f6
```

## Data Flow - Complete Message Processing

```mermaid
sequenceDiagram
    actor User
    participant Frontend as Streamlit UI
    participant Session as Session Manager
    participant Backend as LangGraph Backend
    participant LLM as Groq API
    participant DB as SQLite DB

    User->>Frontend: 1. Type & send message
    Frontend->>Session: 2. Get/create session ID
    Session-->>Frontend: Return unique session_id
    
    Frontend->>Backend: 3. Send message + thread_id + session_id
    Backend->>Backend: 4. Create ChatState
    Backend->>LLM: 5. Call LLM with message history
    LLM-->>Backend: 6. Stream response tokens
    Backend->>Backend: 7. Accumulate response
    Backend->>DB: 8. Save to checkpointer (SQLite)
    DB-->>Backend: Confirmation
    Backend-->>Frontend: 9. Complete response
    
    Frontend->>Frontend: 10. Display response
    Frontend->>Frontend: 11. Update message_history
    Frontend->>DB: 12. Retrieve chat summary
    DB-->>Frontend: Chat summary
    Frontend-->>User: 13. Show updated UI
```

## Session Isolation Architecture

```mermaid
graph LR
    Browser1["🌐 Browser 1<br/>Session A"]
    Browser2["🌐 Browser 2<br/>Session B"]
    Browser3["🌐 Browser 3<br/>Session C"]
    
    App["Streamlit App<br/>Single Instance"]
    
    SessionA["Session State A<br/>thread_id: UUID1<br/>messages: [...]"]
    SessionB["Session State B<br/>thread_id: UUID2<br/>messages: [...]"]
    SessionC["Session State C<br/>thread_id: UUID3<br/>messages: [...]"]
    
    DB["SQLite Database<br/>All threads stored"]
    
    Browser1 -->|creates| SessionA
    Browser2 -->|creates| SessionB
    Browser3 -->|creates| SessionC
    
    SessionA -->|persists via| DB
    SessionB -->|persists via| DB
    SessionC -->|persists via| DB
    
    SessionA -.->|NO ACCESS| SessionB
    SessionB -.->|NO ACCESS| SessionC
    SessionA -.->|NO ACCESS| SessionC
    
    style SessionA fill:#c8e6c9
    style SessionB fill:#bbdefb
    style SessionC fill:#ffe0b2
    style DB fill:#f0f4c3
```

## LangGraph State Management Flow

```mermaid
stateDiagram-v2
    [*] --> InitState
    
    InitState: Initial ChatState
    UserInputState: User Message Added
    ProcessState: Chat Node Execution
    ResponseState: LLM Response Received
    UpdateState: ChatState Updated
    SaveState: Checkpoint Saved
    OutputState: Response Streamed
    
    InitState --> UserInputState: message received
    UserInputState --> ProcessState: invoke chat_node
    ProcessState --> ResponseState: call llm.invoke()
    ResponseState --> UpdateState: add AIMessage
    UpdateState --> SaveState: persist to SQLite
    SaveState --> OutputState: stream to user
    OutputState --> [*]
    
    note right of ProcessState
        StateGraph compiles with:
        START → chat_node → END
        Checkpointer: SqliteSaver
    end note
```

## Database Schema & Relationships

```mermaid
erDiagram
    CHAT_METADATA ||--o{ MESSAGES : stores
    
    CHAT_METADATA {
        string thread_id PK "UUID of conversation"
        string user_id FK "Session/User identifier"
        string summary "First message truncated"
        timestamp created_at "Creation timestamp"
    }
    
    MESSAGES {
        string thread_id FK "Reference to chat"
        int sequence "Message order"
        string role "user or assistant"
        text content "Message text"
        timestamp timestamp "When sent"
    }
    
    CHECKPOINTS {
        string thread_id FK "Conversation ID"
        int checkpoint_id PK "State snapshot"
        blob state_data "Serialized ChatState"
        timestamp created_at "Snapshot time"
    }
```

## Request/Response Lifecycle

```mermaid
graph TD
    A["User types message<br/>in chat input"] 
    B["Frontend detects<br/>Enter key / Send click"]
    C["Get session_id from<br/>st.session_state"]
    D["Create CONFIG dict:<br/>thread_id, session_id"]
    E["Call chatbot.stream<br/>with HumanMessage"]
    F["Backend processes<br/>through StateGraph"]
    G["Chat node invokes<br/>LLM via Groq API"]
    H["Groq returns<br/>streamed tokens"]
    I["Frontend uses<br/>st.write_stream"]
    J["Display tokens<br/>in real-time"]
    K["Append to<br/>message_history"]
    L["Save checkpoint<br/>to SQLite"]
    M["Update sidebar<br/>conversation list"]
    
    A --> B --> C --> D --> E --> F --> G --> H
    H --> I --> J --> K --> L --> M
    
    style A fill:#e1f5ff
    style B fill:#e1f5ff
    style C fill:#f3e5f5
    style D fill:#f3e5f5
    style E fill:#e8f5e9
    style F fill:#e8f5e9
    style G fill:#fff9c4
    style H fill:#fff9c4
    style I fill:#fff3e0
    style J fill:#fff3e0
    style K fill:#f1f8e9
    style L fill:#f1f8e9
    style M fill:#fce4ec
```

## Component Interaction Matrix

```mermaid
graph TB
    subgraph Frontend["🎨 Frontend Layer"]
        SF["Streamlit App"]
        UI["Chat UI"]
        SB["Sidebar"]
        CSS["Custom CSS"]
    end
    
    subgraph Application["⚙️ Application Layer"]
        LG["LangGraph"]
        CS["ChatState"]
        SG["StateGraph"]
        CN["ChatNode"]
    end
    
    subgraph LLMLayer["🚀 LLM Layer"]
        GA["Groq API"]
        MODEL["Llama 3.3 70B"]
    end
    
    subgraph Persistence["💾 Persistence Layer"]
        CP["Checkpointer"]
        DB[(SQLite DB)]
        FILES["chatbot.db file"]
    end
    
    SF --> UI
    SF --> SB
    UI --> CSS
    SB --> CSS
    
    SF --> LG
    LG --> CS
    LG --> SG
    SG --> CN
    
    CN --> GA
    GA --> MODEL
    MODEL --> GA
    
    CN --> CP
    CP --> DB
    DB --> FILES
    
    SG --> CP
    CP --> SF
    
    style Frontend fill:#fff3e0
    style Application fill:#e8f5e9
    style LLMLayer fill:#fff9c4
    style Persistence fill:#f1f8e9
```

## Deployment Architecture (Render)

```mermaid
graph TB
    Client["🌐 Users<br/>Web Browser"]
    CDN["⚡ Render CDN"]
    RenderWeb["☁️ Render Web Service<br/>Python 3.13"]
    
    RenderApp["📦 Application Container<br/>Streamlit + Dependencies"]
    
    GroqAPI["🚀 Groq API<br/>(External)"]
    
    RenderFS["📁 File System<br/>chatbot.db"]
    
    Client -->|HTTPS| CDN
    CDN -->|routes to| RenderWeb
    RenderWeb --> RenderApp
    RenderApp -->|load code| RenderFS
    RenderApp -->|API call| GroqAPI
    GroqAPI -->|inference| RenderApp
    RenderApp -->|save state| RenderFS
    RenderApp -->|stream response| RenderWeb
    RenderWeb -->|HTTP| CDN
    CDN -->|display| Client
    
    style Client fill:#e1f5ff
    style CDN fill:#f3e5f5
    style RenderWeb fill:#e8f5e9
    style RenderApp fill:#fff3e0
    style GroqAPI fill:#fff9c4
    style RenderFS fill:#f1f8e9
```

## Error Handling & Recovery Flow

```mermaid
graph TD
    A["Message Received"]
    B{Session<br/>Exists?}
    C["Create New<br/>Session"]
    D{LLM<br/>Available?}
    E["Return Error<br/>Retry Later"]
    F{DB<br/>Writable?}
    G["Cache in<br/>Memory"]
    H["Process & Stream<br/>Response"]
    I{Save<br/>Success?}
    J["Log & Monitor"]
    K["Success"]
    
    A --> B
    B -->|No| C --> D
    B -->|Yes| D
    D -->|No| E
    D -->|Yes| F
    F -->|No| G
    F -->|Yes| H
    H --> I
    I -->|No| G --> J
    I -->|Yes| K
    J --> K
    
    style K fill:#c8e6c9
    style E fill:#ffccbc
```

## Authentication & Session Flow (Future v1.5+)

```mermaid
graph LR
    User["👤 User"]
    LoginPage["🔐 Login Page"]
    Auth["Auth Service"]
    ValidSess["Valid Session?"]
    Dashboard["📊 Dashboard"]
    ChatApp["💬 Chat App"]
    Logout["Logout"]
    
    User -->|visit| LoginPage
    LoginPage -->|credentials| Auth
    Auth -->|verify| ValidSess
    ValidSess -->|invalid| LoginPage
    ValidSess -->|valid| Dashboard
    Dashboard -->|navigate| ChatApp
    ChatApp -->|click| Logout
    Logout -->|clear session| LoginPage
    
    style Auth fill:#fff3e0
    style ValidSess fill:#e8f5e9
```

---

**Note:** These diagrams illustrate the current architecture (v1.0). See README.md for future enhancement plans.
