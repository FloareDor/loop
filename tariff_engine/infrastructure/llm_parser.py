import json

from tariff_engine.domain.ast_schema import Contract


def build_system_prompt() -> str:
    schema = json.dumps(Contract.model_json_schema(), indent=2)
    return (
        "You are a logistics rate sheet parser. "
        "Extract pricing rules from the provided text into the JSON schema below. "
        "Return ONLY valid JSON matching this schema.\n\n"
        f"```json\n{schema}\n```"
    )


def parse_to_contract(text: str, tables: list | None = None) -> Contract:
    try:
        from anthropic import Anthropic
        return _parse_anthropic(text, tables)
    except ImportError:
        pass

    try:
        from openai import OpenAI
        return _parse_openai(text, tables)
    except ImportError:
        pass

    raise RuntimeError("Install 'anthropic' or 'openai' package: pip install tariff-engine[llm]")


def _user_content(text: str, tables: list | None) -> str:
    parts = [f"Rate sheet text:\n{text}"]
    if tables:
        parts.append(f"Extracted tables:\n{json.dumps(tables, indent=2)}")
    return "\n\n".join(parts)


def _parse_anthropic(text: str, tables: list | None) -> Contract:
    from anthropic import Anthropic
    client = Anthropic()
    msg = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        system=build_system_prompt(),
        messages=[{"role": "user", "content": _user_content(text, tables)}],
    )
    raw = msg.content[0].text
    return Contract.model_validate_json(raw)


def _parse_openai(text: str, tables: list | None) -> Contract:
    from openai import OpenAI
    client = OpenAI()
    resp = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": _user_content(text, tables)},
        ],
    )
    raw = resp.choices[0].message.content
    return Contract.model_validate_json(raw)
