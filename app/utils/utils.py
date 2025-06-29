# app/utils.py
import csv
import os


def save_output_csv(output: dict, file="outputs/alt_texts.csv"):
    headers = ["image_path", "caption_en", "caption_fr", "caption_es",
               "caption_de", "safe_en", "safe_fr", "safe_es", "safe_de"]
    os.makedirs(os.path.dirname(file), exist_ok=True)

    if not os.path.exists(file):
        with open(file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)

    with open(file, "a", newline="") as f:
        writer = csv.writer(f)
        row = [
            output["image_path"],
            output["captions"].get("en", ""),
            output["captions"].get("fr", ""),
            output["captions"].get("es", ""),
            output["captions"].get("de", ""),
            output["safety"]["en"]["is_safe"],
            output["safety"]["fr"]["is_safe"],
            output["safety"]["es"]["is_safe"],
            output["safety"]["de"]["is_safe"],
        ]
        writer.writerow(row)
