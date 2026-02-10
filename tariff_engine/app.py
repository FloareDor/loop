from pathlib import Path

from tariff_engine.domain.ast_schema import Contract
from tariff_engine.domain.result import PricingResult
from tariff_engine.domain.shipment import Shipment
from tariff_engine.engine.evaluator import price
from tariff_engine.infrastructure.edi_parser import parse_edi
from tariff_engine.infrastructure.llm_parser import parse_to_contract
from tariff_engine.infrastructure.pdf_parser import extract_tables, extract_text


def price_shipment(contract: Contract, shipment: Shipment) -> PricingResult:
    return price(contract, shipment)


def price_from_json(json_path: Path, shipment: Shipment) -> PricingResult:
    contract = Contract.model_validate_json(json_path.read_text())
    return price(contract, shipment)


def price_from_edi(edi_path: Path, shipment: Shipment) -> PricingResult:
    contract = parse_edi(edi_path.read_text())
    return price(contract, shipment)


def price_from_pdf(pdf_path: Path, shipment: Shipment) -> PricingResult:
    text = extract_text(str(pdf_path))
    tables = extract_tables(str(pdf_path))
    contract = parse_to_contract(text, tables)
    return price(contract, shipment)
