# AGENT CONTEXT: The Tariff-to-Code Engine

## 1. Project Mission & Identity
**Project Name:** Tariff-to-Code (Concept: "The GitAsk for Logistics")
**User Context:** I am a CMU Masters student specializing in Scalable Systems. I have significant experience with ASTs (Abstract Syntax Trees), parsing, and systems programming (from my "GitAsk" project).
**Target Audience:** Engineering interviewers at **Loop** (a logistics payments platform).
**Core Philosophy:** * **Determinism > Probability:** Financial audits cannot be "mostly right." We do not use RAG to *answer* questions. We use LLMs only to *parse* unstructured data into strict, executable logic.
* **Contract as Code:** A PDF rate sheet is just source code written in a messy language (English). We are building the compiler.

## 2. The Problem Space (Domain Knowledge)
**The Pain Point:** Carriers (FedEx, DHL, private trucking fleets) send "Rate Sheets" as complex PDFs. These contain conditional logic:
* "Base rate $500."
* "IF weight > 2000 lbs, add $0.50/lb."
* "IF delivery is to zip code starting with 152, add surcharge."

**Current Industry Solution:** Humans manually reading PDFs or basic OCR that fails on complex table layouts.
**Our Solution:** A pipeline that converts PDF logic into a **JSON AST (Abstract Syntax Tree)**, which is then compiled into a Python executable function.

## 3. Technical Architecture

### Layer 1: Ingestion (The Lexer)
* **Goal:** Extract text while preserving spatial hierarchy (identifying that "Fuel Surcharge" is a subsection of "Accessorials").
* **Tooling:** `pdfplumber` (for raw text/tables) or a layout-aware model.
* **Agent Instruction:** Prioritize identifying *tables* and *conditional clauses* over raw text dumping.

### Layer 2: The Intermediate Representation (The "GitAsk" Core)
* **Concept:** Instead of vector embeddings, we map the PDF rules to a **Strict JSON Schema**.
* **Mechanism:** Use an LLM (GPT-4o/Claude 3.5) strictly as a *parser* to extract data into a Pydantic model.
* **The Schema (Draft):**
    ```json
    {
      "contract_id": "DHL_2026_NE",
      "rules": [
        {
          "rule_type": "base_rate",
          "conditions": [
            { "field": "zone", "operator": "==", "value": 5 }
          ],
          "action": { "type": "set_price", "value": 450.00, "currency": "USD" }
        },
        {
          "rule_type": "surcharge",
          "conditions": [
            { "field": "weight", "operator": ">", "value": 2000 }
          ],
          "action": { "type": "add_rate", "formula": "0.15 * (weight - 2000)" }
        }
      ]
    }
    ```

### Layer 3: The Execution Engine (The Compiler)
* **Goal:** A Python engine that traverses the JSON AST and calculates the final price for a given shipment.
* **Implementation:** A simple Visitor Pattern or Rule Engine.
* **Input:** A `Shipment` object (e.g., `{ "weight": 2500, "zone": 5 }`).
* **Output:** `Final Price` (Float) + `Audit Trace` (List of rules applied).

## 4. Implementation Guidelines for the Agent
1.  **Code Style:** Pythonic, typed (TypeHints), clean, and modular. 
2.  **No Comments:** As per user preference, keep code direct. Do not add expository comments unless explaining a complex algorithm.
3.  **Focus on "The Twist":** * Do not suggest a vector DB. 
    * Do not suggest a Chatbot interface.
    * **DO** suggest Pydantic validators and AST traversal logic.
4.  **MVP Scope:** * Do not try to parse an entire 50-page contract. 
    * **Focus:** Parse *one single pricing table* with *one specific exception rule* (e.g., "Overweight Surcharge") to demonstrate the end-to-end pipeline.

## 5. Key Differentiators to Highlight in Code
* **Auditability:** The system must return *why* a price was calculated (e.g., "Rule #4 (Overweight) applied: +$75.00").
* **Safety:** The LLM never does the math. Python does the math.

## 6. Next Step
Start by creating the **Pydantic Models** (The AST Schema) that define what a "Rule" looks like. This is the foundation of the system.