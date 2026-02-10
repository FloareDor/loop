import argparse
import json
import sys
from pathlib import Path

from tariff_engine.app import price_from_edi, price_from_json, price_from_pdf
from tariff_engine.domain.shipment import Shipment


def main():
    parser = argparse.ArgumentParser(description="Tariff-to-Code Engine")
    parser.add_argument("contract", help="Path to contract JSON or PDF")
    parser.add_argument("--weight", type=float, required=True)
    parser.add_argument("--zone", type=int, required=True)
    parser.add_argument("--origin-zip", default="")
    parser.add_argument("--dest-zip", default="")
    parser.add_argument("--service-type", default="ground")
    parser.add_argument("--json-output", action="store_true")
    args = parser.parse_args()

    shipment = Shipment(
        weight=args.weight,
        zone=args.zone,
        origin_zip=args.origin_zip,
        dest_zip=args.dest_zip,
        service_type=args.service_type,
    )

    path = Path(args.contract)
    if path.suffix == ".json":
        result = price_from_json(path, shipment)
    elif path.suffix == ".edi":
        result = price_from_edi(path, shipment)
    elif path.suffix == ".pdf":
        result = price_from_pdf(path, shipment)
    else:
        print(f"Unsupported file type: {path.suffix}", file=sys.stderr)
        sys.exit(1)

    if args.json_output:
        print(result.model_dump_json(indent=2))
    else:
        print(result.breakdown)


if __name__ == "__main__":
    main()
