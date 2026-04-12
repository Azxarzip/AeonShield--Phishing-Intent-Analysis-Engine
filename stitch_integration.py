"""
Optional Google Stitch (Labs) helpers for the dashboard.

The official client is the Node package @google/stitch-sdk, which speaks MCP over
Streamable HTTP at https://stitch.googleapis.com/mcp with header X-Goog-Api-Key.

Set STITCH_API_KEY in the environment — never commit real keys to the repository.
"""

import os

STITCH_MCP_BASE = os.environ.get("STITCH_HOST", "https://stitch.googleapis.com/mcp")
STITCH_WEB_APP = "https://stitch.withgoogle.com"


def stitch_api_key_configured() -> bool:
    return bool(os.environ.get("STITCH_API_KEY", "").strip())


def aeonshield_stitch_prompt() -> str:
    return (
        "Design a dark, wide desktop security dashboard called AeonShield for BEC and "
        "phishing detection: neon cyan (#00d4ff) accents on black, monospace data panels, "
        "KPI cards for threat pulse and spoofing counts, a Sankey for intent flow, and a "
        "forensic log table. Cyber-forensic terminal aesthetic, high contrast, no clutter."
    )


def stitch_setup_instructions() -> str:
    return (
        "Google Stitch uses MCP Streamable HTTP. From Python, use the official "
        "`@google/stitch-sdk` (Node.js) or connect Stitch in Cursor MCP settings:\n\n"
        f"- URL: `{STITCH_MCP_BASE}`\n"
        "- Header: `X-Goog-Api-Key: <your key>`\n\n"
        "Paste the design prompt from the sidebar into Stitch, generate a screen, then "
        "export HTML or refine in the canvas."
    )
