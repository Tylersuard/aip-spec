# Agentic Internet Protocol (AIP)

The Web for Machines.

AIP is a minimalist, text-only protocol designed for AI Agents. It replaces heavy, chaotic HTML with clean, predictable "Nodes."

📄 What is a Node?
An AIP Node is a simple .txt file divided into four clear parts. This structure ensures an AI always knows exactly where it is and what it can do.

<img width="1024" height="1024" alt="Gemini_Generated_Image_s47465s47465s474" src="https://github.com/user-attachments/assets/6ec2c8b3-f3de-4b6e-a418-2e3b79d09812" />

    Title: The name of the current location.
    Description: High-level context (The "System Prompt" for the page).
    Content: The actual data (Markdown tables, lists, or text).
    Actions: The "Edges", exactly where the agent can move next.

🚀 Why Use It?  
 - Token Efficiency: 150 tokens vs. 5,000+ for standard HTML.
 - Reduced Hallucination: Agents don't have to "guess" which button to click.
 - Speed: No Javascript, no CSS, no ads. Just pure logic.

🛠 Navigation Types (The Edges)

AIP limits choices to three simple actions to prevent model confusion:
    NAV: Move to a static page (e.g., View Cart).
    QRY: A dynamic search or filter (e.g., Find by ID).
    ACT: A state-changing action (e.g., Pay Now).
    
This repo contains:

- **`SPEC.md`** — the AIP v0.2 draft (format + discovery + client behavior)
- **`examples/`** — two “hero sites” (ecommerce + billing) implemented as AIP nodes
- **`reference/python/`** — a minimal parser/validator + a tiny interactive node browser CLI

Key ideas:

- **Agent-first sites** (not “human sites + a helper file”)
- Websites as **graphs**: nodes (pages) + edges (routes)
- **Short pages** (recommended: well under 8,000 words) to reduce cost/latency and make prompt-injection harder to hide
- **Small action space** (recommended: ~6 edges per node) so simpler models don’t get confused
- Explicit edge types:
  - `NAV` = go to a known node
  - `QRY` = generate a node from parameters (search/filter/paginate)
  - `ACT` = change state (cart/checkout/payment)
 
Here is a sample AIP node representing a product page in a fictional store:

### Sample AIP Node: `product_123.aip.txt`

```text
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

```

### How an AI "sees" this

Instead of scanning 5,000 lines of HTML code to find a "Buy" button, the AI looks at this text file and immediately understands:

* **What this is:** An industrial gear (from the `TITLE`).
* **The Details:** It costs $89 and 14 are left (from the `CONTENT`).
* **What it can do next:** It has exactly 4 options. It doesn't have to "guess" where to click; it just picks Action #2 to buy it.

### Why this is better for your AI agents:

1. **Lower Cost:** It uses about 150 tokens. A standard web page can easily use 5,000+ tokens.
2. **Higher Accuracy:** There are no "pop-ups" or "sidebar links" to distract the model.
3. **Speed:** The AI can "read" and "decide" in a fraction of a second.

**Would you like me to show you how the `aip_browser.py` script would process this specific node?**

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
