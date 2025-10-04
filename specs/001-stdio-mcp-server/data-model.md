# Data Model: STDIO MCP Server

**Feature**: 001-stdio-mcp-server
**Date**: 2025-10-04

## Overview

This document defines the key entities and their relationships for the STDIO MCP Server. All entities are runtime-only (no persistence) and exist in memory during server execution.

---

## Entities

### 1. MCP Server

**Type**: Runtime singleton (one instance per process)

**Purpose**: Represents the server process that implements the MCP protocol

**Attributes**:
- `server_name` (string): Identifier for this server instance (e.g., "stdio-mcp-server")
- `version` (string): Server version following semver (e.g., "0.1.0")
- `protocol_version` (string): MCP protocol version supported (e.g., "2024-11-05")
- `capabilities` (ServerCapabilities): Features this server supports
- `state` (ServerState enum): Current lifecycle state

**States** (ServerState enum):
- `UNINITIALIZED`: Server object created but not started
- `INITIALIZING`: Processing initialization request
- `READY`: Ready to accept protocol messages
- `SHUTTING_DOWN`: Graceful shutdown in progress
- `STOPPED`: Server has exited

**State Transitions**:
```
UNINITIALIZED → (initialize) → INITIALIZING → (handshake complete) → READY
READY → (SIGINT/SIGTERM) → SHUTTING_DOWN → (cleanup complete) → STOPPED
```

**Validation Rules**:
- `server_name` must be non-empty string
- `version` must follow semantic versioning (MAJOR.MINOR.PATCH)
- `protocol_version` must match MCP SDK supported versions
- Cannot transition from STOPPED to any other state (terminal state)

---

### 2. Protocol Session

**Type**: Runtime entity (one per server lifetime)

**Purpose**: Represents the active communication session between client and server

**Attributes**:
- `session_id` (UUID): Unique identifier for this session
- `client_info` (dict): Client name and version from initialization
- `initialized_at` (datetime): Timestamp when session became active
- `state` (SessionState enum): Current session state

**States** (SessionState enum):
- `NOT_STARTED`: No initialization request received yet
- `HANDSHAKE`: Processing initialize request
- `ACTIVE`: Initialization complete, ready for requests
- `CLOSED`: Session terminated

**State Transitions**:
```
NOT_STARTED → (initialize request) → HANDSHAKE → (initialize response) → ACTIVE
ACTIVE → (shutdown) → CLOSED
```

**Validation Rules**:
- `session_id` must be valid UUID v4
- `client_info` must contain "name" and "version" keys (strings)
- `initialized_at` must be UTC datetime
- Can only receive one initialize request per session (NOT_STARTED → ACTIVE only)

---

### 3. Message

**Type**: Transient data structure (exists only during request/response cycle)

**Purpose**: Represents a single JSON-RPC 2.0 message exchanged between client and server

**Attributes**:
- `jsonrpc` (string, always "2.0"): JSON-RPC protocol version
- `id` (int | string | null): Request identifier for correlation
- `method` (string, optional): RPC method name (requests only)
- `params` (dict, optional): Method parameters (requests only)
- `result` (any, optional): Success result (responses only)
- `error` (ErrorObject, optional): Error details (error responses only)

**Message Types**:
1. **Request**: Has `method` and `params`, sent by client
2. **Response**: Has `result`, sent by server (correlates via `id`)
3. **Error**: Has `error` object, sent by server when request fails

**Validation Rules**:
- `jsonrpc` field MUST be exactly "2.0"
- Requests MUST have `method` (non-empty string)
- Responses MUST have either `result` OR `error`, never both
- `id` must match between request and response
- Notification (id == null) not supported in v1

**Example Structures**:
```python
# Request
{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": { ... }
}

# Success Response
{
    "jsonrpc": "2.0",
    "id": 1,
    "result": { ... }
}

# Error Response
{
    "jsonrpc": "2.0",
    "id": 1,
    "error": {
        "code": -32700,
        "message": "Parse error"
    }
}
```

---

### 4. Server Capabilities

**Type**: Configuration object (immutable after server initialization)

**Purpose**: Advertises what features this server supports to clients

**Attributes**:
- `tools` (dict): Tool capabilities (empty in v1)
- `resources` (dict): Resource capabilities (empty in v1)
- `prompts` (dict): Prompt template capabilities (empty in v1)

**Validation Rules**:
- All fields are dictionaries (may be empty)
- Immutable after initialization handshake
- Must be serializable to JSON

**V1 Implementation**:
```python
{
    "tools": {},
    "resources": {},
    "prompts": {}
}
```

**Future Expansion**:
Later versions will populate these dictionaries with actual tool/resource/prompt definitions.

---

### 5. ErrorObject

**Type**: Data structure (embedded in error responses)

**Purpose**: Provides structured error information per JSON-RPC 2.0 spec

**Attributes**:
- `code` (int): Numeric error code (JSON-RPC defined or application-specific)
- `message` (string): Human-readable error description
- `data` (any, optional): Additional error context

**Standard Error Codes**:
- `-32700`: Parse error (invalid JSON)
- `-32600`: Invalid request (not valid JSON-RPC)
- `-32601`: Method not found
- `-32602`: Invalid params
- `-32603`: Internal error
- `-32000 to -32099`: Application-defined errors (reserved for MCP)

**Validation Rules**:
- `code` must be integer
- `message` must be non-empty string
- `data` is optional and free-form

---

## Entity Relationships

```
┌─────────────┐
│ MCP Server  │
│             │
│ - state     │──┬───────────────────┐
│ - caps      │  │                   │
└─────────────┘  │                   │
                 │                   │
                 │ 1:1               │ 1:1
                 ▼                   ▼
        ┌─────────────────┐   ┌──────────────────┐
        │ Protocol Session│   │ ServerCapabilities│
        │                 │   │                  │
        │ - client_info   │   │ - tools          │
        │ - state         │   │ - resources      │
        └─────────────────┘   │ - prompts        │
                 │            └──────────────────┘
                 │ 1:N
                 ▼
        ┌─────────────────┐
        │ Message         │
        │                 │
        │ - jsonrpc       │──┬─ contains ─▶ ┌──────────────┐
        │ - id            │  │               │ ErrorObject  │
        │ - method/result │  └──────────────▶│              │
        └─────────────────┘                  └──────────────┘
```

**Relationship Descriptions**:
- **MCP Server ↔ Protocol Session**: 1:1 - Each server has exactly one session
- **MCP Server ↔ ServerCapabilities**: 1:1 - Each server advertises one capability set
- **Protocol Session ↔ Message**: 1:N - One session handles many messages sequentially
- **Message ↔ ErrorObject**: 1:0..1 - Error responses contain one error object

---

## Implementation Notes

### Type Hints

All entities should have Python type hints defined:

```python
from typing import Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass
from uuid import UUID
from datetime import datetime

class ServerState(Enum):
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    SHUTTING_DOWN = "shutting_down"
    STOPPED = "stopped"

class SessionState(Enum):
    NOT_STARTED = "not_started"
    HANDSHAKE = "handshake"
    ACTIVE = "active"
    CLOSED = "closed"

@dataclass
class ServerCapabilities:
    tools: Dict[str, Any]
    resources: Dict[str, Any]
    prompts: Dict[str, Any]
```

### Validation

Validation should occur at:
1. **Message receipt**: Validate JSON-RPC structure before processing
2. **State transitions**: Validate legal state changes before updating
3. **Initialization**: Validate client_info structure during handshake

### Error Handling

Per Constitution Principle II (Explicit Over Implicit):
- All validation failures must raise explicit exceptions
- All exceptions must be logged to stderr
- Protocol errors must return proper ErrorObject responses
- Server must never crash on invalid input

---

## Summary

The data model is minimal and focused on protocol compliance:
- **4 core entities** (Server, Session, Message, Capabilities)
- **2 supporting types** (ErrorObject, Enums for states)
- **No persistence** (all runtime-only)
- **Clear state machines** (explicit transitions, validation)
- **JSON-RPC 2.0 compliant** (standard message structure)

This model supports the FR requirements while adhering to Constitution Principle I (Simplicity First).
