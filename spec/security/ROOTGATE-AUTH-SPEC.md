# ROOT-GATE AUTHENTICATION BOUNDARY SPECIFICATION
## Enforcing the Law of Stewardship in the Nebula Mesh

### 1. The Sovereign Identity Key
`ROOTGATE_SECRET` is the supreme sovereign identity key. It guards the core boundary of the mesh. It must never be exposed to the client.

### 2. /api/mcp (Master Control Program)
- Must require `Authorization: Bearer <ROOTGATE_SECRET>`.
- Aliases `MCP_BEARER_TOKEN` as a legacy fallback.
- No execution commands can be issued to the mesh without this key.

### 3. /api/public/heartbeat (Telemetry Gateway)
- Must check `process.env.HEARTBEAT_HMAC_SECRET || process.env.ROOTGATE_SECRET`.
- Mesh nodes sign telemetry using `HMAC-SHA256(secret, "${nodeId}.${payload}")`.
- This prevents spoofed nodes from injecting fake state into the Nebula Mesh.

### 4. /admin/nodes (Nebula Mesh Control Boundary)
- Client Gate: Displays a cryptographic challenge prompt.
- Server Handler: Uses `crypto.timingSafeEqual` to verify the key against `ROOTGATE_SECRET`.
- Manifest inspection and node modification are locked behind this gate.

### 5. Required Environment Variables
- `ROOTGATE_SECRET` (Primary)
- `HEARTBEAT_HMAC_SECRET` (Optional, falls back to Root-Gate)
- `MCP_BEARER_TOKEN` (Legacy fallback)
