import json

# build_prompt_from_config("configs/extraction_config.json", use_ocr=True, use_vision=True, ocr_text=ocr_text)

def build_prompt_from_config(config_path="configs/extraction_config.json", use_ocr=False, use_vision=False, ocr_text=""):
    with open(config_path, "r") as f:
        config = json.load(f)   

    if use_vision:
        header = config["prompt_template"]["header_with_image"]
    else:
        header = config["prompt_template"]["header"]

    if use_ocr:
        ocr_text = config["prompt_template"]["ocr_text"].format(ocr_text=ocr_text)
        header = header + "\n\n" + ocr_text

    footer = config["prompt_template"]["footer"]
    fmt = config["prompt_template"]["field_format"]

    body = "\n".join(
        fmt.format(readable_name=key, description=field["description"])
        for key, field in config["extraction_fields"].items()
    )

    return f"{header}\n\n{body}\n\n{footer}"