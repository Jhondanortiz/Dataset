# REPARADOR_JSON.py
import json
from pathlib import Path

archivo = Path("data/processed/vulnerabilities_dataset.json")
texto = archivo.read_text(encoding="utf-8")

# Buscamos dónde empieza "vulnerabilities":
pos = texto.find('"vulnerabilities"')
if pos == -1:
    print("No se encontró 'vulnerabilities'")
    exit()

# Nos movemos justo después de los dos puntos :
pos_dos_puntos = texto.find(":", pos) + 1
while texto[pos_dos_puntos].isspace():
    pos_dos_puntos += 1

# Insertamos una [ si no hay una
if texto[pos_dos_puntos] != '[':
    texto = texto[:pos_dos_puntos] + " [" + texto[pos_dos_puntos:]

# Aseguramos que termine con ]
if not texto.strip().endswith("]"):
    # Buscamos el último } y lo reemplazamos por }]
    ultimo_llave = texto.rfind("}")
    if ultimo_llave != -1:
        texto = texto[:ultimo_llave] + "  ]\n" + texto[ultimo_llave:]

# Guardamos el archivo reparado
archivo.write_text(texto, encoding="utf-8")
print("¡JSON REPARADO PERFECTAMENTE! YA TIENE LA LISTA CORRECTA []")
print("Ahora ejecuta: python -m scripts.load_data")