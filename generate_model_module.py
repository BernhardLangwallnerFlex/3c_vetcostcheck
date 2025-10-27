import argparse
import json
from pathlib import Path

def generate_pydantic_model_file(config_path: str, output_path: str, class_name: str = "Invoice") -> None:
    with open(config_path, "r") as f:
        config = json.load(f)

    fields = config["extraction_fields"]

    lines = [
        "# This file is auto-generated from config.json. Do not edit manually.",
        "from pydantic import BaseModel, Field\n",
        f"class {class_name}(BaseModel):"
    ]

    for field_name, props in fields.items():
        field_type = props.get("type", "str")
        description = props.get("description", "").replace('"', '\\"')  # Escape double quotes
        lines.append(f'    {field_name}: {field_type} = Field(description="{description}")')

    content = "\n".join(lines) + "\n"

    Path(output_path).write_text(content)
    print(f"✅ Pydantic model '{class_name}' written to: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Generate a Pydantic model from config.json")
    parser.add_argument(
        "--config",
        type=str,
        default="configs/extraction_config.json",
        help="Path to the config.json file"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="models/invoice_model.py",
        help="Path to the output Python module"
    )
    parser.add_argument(
        "--class_name",
        type=str,
        default="Invoice",
        help="Name of the generated Pydantic class"
    )

    args = parser.parse_args()
    generate_pydantic_model_file(args.config, args.output, args.class_name)

if __name__ == "__main__":
    main()