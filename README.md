# Agentic Internet Protocol (AIP)

AIP is a tiny, agent-native “web” format: each page is a **small, human-readable text node** containing (1) a title, (2) a description, (3) the page **content**, and (4) a **small menu of next actions**.

This repo contains:

- **`SPEC.md`** — the AIP v0.2 draft (format + discovery + client behavior)
- **`examples/`** — two “hero sites” (ecommerce + billing) implemented as AIP nodes
- **`reference/python/`** — a minimal parser/validator + a tiny interactive node browser CLI

## Why AIP

Modern models can handle huge context windows, but that can get expensive and slow if you just want to read one page and take one step.
AIP is designed for **incremental disclosure**: show the model only what it needs *right now*.

Key ideas:

- **Agent-first sites** (not “human sites + a helper file”)
- Websites as **graphs**: nodes (pages) + edges (routes)
- **Short pages** (recommended: well under 8,000 words) to reduce cost/latency and make prompt-injection harder to hide
- **Small action space** (recommended: ~6 edges per node) so simpler models don’t get confused
- Explicit edge types:
  - `NAV` = go to a known node
  - `QRY` = generate a node from parameters (search/filter/paginate)
  - `ACT` = change state (cart/checkout/payment)
 
## Example Node:

TITLE: Heavy-Duty Industrial Gear
DESCRIPTION: Technical specifications and purchase options for the HG-9000 model.
---
CONTENT:
The HG-9000 is a steel-reinforced industrial gear designed for high-torque 
applications. 
- Material: Grade 8 Carbon Steel
- Weight: 4.5kg
- Compatibility: Universal 40mm shafts
- Status: In Stock (14 units)
- Price: $89.00
---
ACTIONS:
1. [NAV] Back to Catalog | url: /catalog/gears
2. [ACT] Add to Cart | url: /cart/add?id=123&qty=1
3. [QRY] Check Shipping Estimates | url: /shipping/calc{zip_code}
4. [NAV] View Technical Manual | url: /docs/hg9000-manual

## Quick start (local)

```bash
python -m venv .venv && source .venv/bin/activate
python reference/python/aip_browser.py examples/acornmart/root.aip.txt
```

Then pick an edge by id, and the browser will open the next node (local file demo).

## Hosting

These examples are plain text. Any static host works.
You can also build a tiny HTTP server that serves `text/aip; charset=utf-8` and returns AIP nodes at their `Fetch:` URLs.

## License

MIT. See `LICENSE`.
