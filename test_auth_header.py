#!/usr/bin/env python
"""Test if Authorization header is received by Django"""
import requests
import json

url = "http://localhost:8000/api/v1/ocupacion/debug-header/"
headers = {
    "Authorization": "Api-Key QPbDter3.qK0iLwBYH1eYG1RZDKmz82CWKD0kLJvk",
    "Content-Type": "application/json"
}

try:
    response = requests.post(url, json={"test": "123"}, headers=headers, timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    data = response.json()
    print(f"\nHeaders received by Django:")
    for k, v in data.get('headers', {}).items():
        print(f"  {k}: {v}")
    print(f"\nAuth header: {data.get('auth_header')}")
except Exception as e:
    print(f"Error: {e}")
