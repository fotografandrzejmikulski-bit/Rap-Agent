"""Compatibility notice.

The production runtime is src.omega. This file is retained as a migration marker only.
New code must import from src.omega and never from the legacy root module.
"""
raise RuntimeError("omega_core.py is legacy. Use the canonical src.omega runtime.")
