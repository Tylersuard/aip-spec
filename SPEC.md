# Agentic Internet Protocol (AIP) v0.2 (Draft)

> Agent-native websites as navigable graphs.

## 1. Abstract

The Agentic Internet Protocol (AIP) defines a compact, text-first page format and a small set of client/server rules for publishing **agent-only websites**.
An AIP website is a directed graph:

- **nodes** are pages (AIP documents)
- **edges** are allowed next steps (navigation, queries, actions)

AIP is built for incremental disclosure: a client reads **one node at a time**, chooses a small next action, and fetches the next node.

## 2. Goals

- **Agent-first**: pages are designed to be consumed by agents directly
- **Small nodes**: pages SHOULD be short and human-readable (recommended: well under 8,000 words)
- **Small action space**: nodes SHOULD expose a small set of edges (recommended: ~6)
- **Graph navigation**: explicit, bounded next steps
- **Transport-friendly**: works over HTTP(S), cacheable, predictable parsing
- **Interoperable**: versioning + unknown-field tolerance

## 3. Non-goals

- Replacing HTTP or defining a new transport
- Defining auth standards (AIP declares requirements but does not invent OAuth)
- Encoding large policies or long docs in a single node

## 4. Transport

AIP is transport-agnostic, but HTTP(S) is the default.

Servers SHOULD return:

- `Content-Type: text/aip; charset=utf-8`

Clients MAY send:

- `Accept: text/aip, text/plain`

## 5. Node addressing

Each node MUST include a stable identifier and a canonical fetch URL.

- `Node:` a stable identifier (recommended scheme: `aip://`)
- `Fetch:` the canonical URL for the current transport (typically `https://…`)

Example:

```
Node: aip://acornmart.example/product/12345
Fetch: https://acornmart.example/product/12345
```

## 6. Document format

### 6.1 Required fields

An AIP document is UTF-8 plain text and MUST contain:

1) version line `AIP/<major>.<minor>`
2) `Node:`
3) `Fetch:`
4) `Title:`
5) `Description:`
6) `Content:`
7) `Edges:`

### 6.2 Unknown fields

Clients MUST ignore unknown top-level fields.
This enables forward-compatible extensions.

### 6.3 Syntax (normative, line-oriented)

```
AIP/0.2
Node: <aip://...>
Fetch: <https://...>
Title: <single line>
Description: <single line>

Content:
  <one or more lines of page content>

Edges:
  <EDGE_ID> <KIND> <METHOD> <TARGET> - <summary>
    <optional indented metadata lines>
```

- `Content:` and `Edges:` MUST appear exactly once.
- Indented content lines MUST begin with two spaces.
- Edge metadata lines MUST begin with four spaces.

## 7. Edge types

Edges MUST be one of:

- `NAV` — navigate to a known node (“go to that page”)
- `QRY` — compute a node from parameters (search/filter/sort/paginate)
- `ACT` — change server state (cart/checkout/payment/account updates)

### 7.1 Edge line

```
<EDGE_ID> <KIND> <METHOD> <TARGET> - <summary>
```

- `EDGE_ID` is unique within the node (e.g. `search`, `open`, `add`)
- `METHOD` is typically `GET` or `POST`
- `TARGET` is one of:
  - a node id: `aip://…`
  - an absolute path: `/…` (resolved against the authority of `Fetch:`)
  - `self` (operate on the current node URL)

### 7.2 Metadata (optional)

Edges MAY include metadata blocks. Common keys:

- `Input:` parameters (name, type, location, constraints)
- `Output:` result (status, media type, next node)
- `Auth:` requirement (`none|api_key|bearer|oauth2`) and notes
- `Retry-Key:` a required header name for deduplicating retries (recommended for money/irreversible actions)
- `Notes:` freeform notes

Example:

```
add ACT POST /cart/add - add to cart
    Input:
      sku: string required (body) - "12345"
      qty: integer required (body) - min=1 max=10
      retry_key: string required (header) - unique token for this intended add
    Output:
      200: text/aip - cart node
    Retry-Key: X-Request-Key
```

## 8. Client behavior

### 8.1 One node at a time

Clients SHOULD operate as:

1) fetch node
2) read `Title`, `Description`, and `Content`
3) choose one edge from `Edges`
4) provide required inputs
5) follow edge to next node

### 8.2 Bounded expansion

Clients MUST NOT recursively fetch the whole site.
Recommended defaults:

- evaluate at most **6–12** edges per node (sites SHOULD keep edges small anyway)
- prefetch depth default = **0** (no automatic traversal)
- max follow depth when enabled = **1**
- cycle detection on `Node:` ids

### 8.3 Errors

Clients SHOULD treat:

- `404` missing node/edge target: pick another edge or navigate upward
- `401/403` auth needed/forbidden: authenticate or choose alternate path
- `409` conflict: re-fetch current state node
- `429` rate limited: backoff and retry
- `5xx` server error: retry with exponential backoff

## 9. Caching

Servers SHOULD include `ETag` and/or `Last-Modified`.
Clients SHOULD cache immutable nodes and revalidate mutable nodes.

## 10. Security considerations (brief)

- Keep nodes short to reduce the ability to hide prompt-injection content.
- Prefer small edge menus to reduce unintended actions.
- For actions that can charge money or create irreversible changes, require a retry-dedup header (e.g. `X-Request-Key`).
- Do not include secrets in nodes.

## 11. Examples

See `examples/` in this repo.
