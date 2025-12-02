import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
PATH = os.path.join(PROCESSED_DIR, "vulnerabilities_dataset_groups.json")

with open(PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

print("\n=== TIPO DE ESTRUCTURA ===")
print(type(data))

if isinstance(data, list):
    print("\nPrimer elemento:")
    print(data[0])

elif isinstance(data, dict):
    print("\nClaves disponibles:")
    print(list(data.keys()))

    # Intentar detectar automáticamente una lista
    for key in data:
        if isinstance(data[key], list):
            print(f"\nDetectada lista en la clave: {key}")
            print("Primer elemento:")
            print(data[key][0])
            break
