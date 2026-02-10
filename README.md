# Tariff-to-Code

Turns carrier rate sheets into executable pricing logic.

Rate sheets (PDFs, EDI files) contain rules like "base rate $450, add $0.15/lb over 2000 lbs." This simple engine parses those rules into a strict JSON AST, then runs them against shipments to get exact prices with a full audit trail.

The LLM parses. Python computes. Not probabilistic.

## How it works

```
PDF / EDI / JSON  -->  Contract AST (Pydantic)  -->  Pricing Engine  -->  Price + Audit Trail
     input               intermediate repr              evaluator              output
```

Three ingestion paths, one execution engine. The AST is the universal contract between layers.

## Quick start

```bash
pip install -e ".[dev]"
pytest
```

## Usage

```bash
# from a JSON contract
python cli.py sample_data/dhl_2026_ne.json --weight 2500 --zone 5

# from an EDI file (no LLM needed)
python cli.py sample_data/dhl_2026_ne.edi --weight 2500 --zone 5

# JSON output
python cli.py sample_data/dhl_2026_ne.json --weight 2500 --zone 5 --json-output
```

Output:

```
Contract: DHL_2026_NE
  [APPLIED] base_rate: set base 450 (+450)
  [APPLIED] surcharge: formula: 0.15 * (weight - 2000) = 75.0 (+75.0)
  [SKIPPED] discount: multiply x1.25 (+0)
  [APPLIED] min_charge: flat +15 (+15)
  TOTAL: USD 540.00
```

Every rule is logged. Applied or skipped, with the dollar impact. The deltas sum to the total.

## Project structure

```
tariff_engine/
  domain/          pure models, no I/O
    ast_schema.py    Contract, Rule, Condition, Action (discriminated union)
    shipment.py      input value object
    result.py        PricingResult + AuditEntry
    exceptions.py    domain errors
  engine/          pure computation
    evaluator.py     price() function — traverses AST, returns audited result
    safe_math.py     formula validator using Python's ast module (whitelist-only)
  infrastructure/  all I/O lives here
    pdf_parser.py    pdfplumber wrapper
    llm_parser.py    LLM structured output -> Contract
    edi_parser.py    X12-style EDI -> Contract (deterministic, no LLM)
  app.py           wires it all together
```

## Key ideas

- **Formulas are validated at parse time.** The safe_math module walks the Python AST and rejects anything not on a whitelist. An unsafe formula cannot become a domain object.
- **Decimal, not float.** `0.1 + 0.2 != 0.3` in floating point. We use `Decimal` for all money.
- **Discriminated unions.** Pydantic routes `{"type": "set_price"}` to `SetPrice` and `{"type": "add_formula"}` to `AddFormula` automatically. Adding a new action type is one model + one match branch.
- **The domain has zero I/O dependencies.** The entire engine is testable without API keys, PDFs, or network calls.
