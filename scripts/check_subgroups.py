import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE = os.path.join(BASE, "data", "processed", "vulnerabilities_dataset_subgroups.json")

with open(FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

# Detectar si es lista o dict
if isinstance(data, list):
    subgroups = data
elif isinstance(data, dict) and "subgroups" in data:
    subgroups = data["subgroups"]
else:
    raise Exception("ERROR: El JSON no contiene una lista válida de subgrupos.")

errores = []

for s in subgroups:
    if "group" not in s:
        errores.append(s)

print("SUBGRUPOS SIN 'group':\n")
for e in errores:
    print(e)

print(f"\nTOTAL SUBGRUPOS CON ERROR: {len(errores)}")
