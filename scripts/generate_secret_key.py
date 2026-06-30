#!/usr/bin/env python3
"""
Script para generar una clave secreta segura para Django.
Ejecutar: python scripts/generate_secret_key.py
"""

import secrets
import string

def generate_secret_key(length=50):
    """Genera una clave secreta segura para Django"""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    # Remover caracteres problemáticos
    alphabet = alphabet.replace("'", "").replace('"', "").replace("\\", "")
    
    return ''.join(secrets.choice(alphabet) for _ in range(length))

if __name__ == "__main__":
    secret_key = generate_secret_key()
    print("\n" + "="*60)
    print("CLAVE SECRETA GENERADA PARA DJANGO")
    print("="*60)
    print(f"\n{secret_key}\n")
    print("="*60)
    print("\nInstrucciones:")
    print("1. Copia esta clave en tu archivo .env:")
    print(f"   SECRET_KEY={secret_key}")
    print("2. Para Docker, establece la variable de entorno:")
    print(f"   export SECRET_KEY={secret_key}")
    print("   o en .env de Docker: SECRET_KEY={secret_key}")
    print("="*60 + "\n")