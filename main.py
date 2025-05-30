from mcp.server.fastmcp import FastMCP
import json

# In-memory AI VC database
ai_vcs = {
    "a16z": {"name": "Andreessen Horowitz", "focus": "AI/ML", "notable": ["OpenAI", "Databricks"]},
    "sequoia": {"name": "Sequoia Capital", "focus": "AI/Enterprise", "notable": ["OpenAI", "Stripe"]},
    "gv": {"name": "GV (Google Ventures)", "focus": "AI/Infrastructure", "notable": ["Anthropic", "DeepMind"]},
    "nea": {"name": "NEA", "focus": "Enterprise AI", "notable": ["Salesforce", "DataRobot"]},
    "kleiner": {"name": "Kleiner Perkins", "focus": "AI/Consumer", "notable": ["Google", "Amazon"]}
}

# Create MCP server
mcp = FastMCP("AIVCResearch")

@mcp.tool()
def get_ai_vcs() -> str:
    """Get list of top AI venture capital firms"""
    result = []
    for key, vc in ai_vcs.items():
        result.append(f"{vc['name']}: {vc['focus']} - Notable: {', '.join(vc['notable'])}")
    
    return "\n".join(result)

@mcp.tool()
def get_vc_info(vc_key: str) -> str:
    """Get detailed info about a specific VC firm (use keys: a16z, sequoia, gv, nea, kleiner)"""
    vc = ai_vcs.get(vc_key.lower())
    if vc:
        return f"{vc['name']}\nFocus: {vc['focus']}\nNotable investments: {', '.join(vc['notable'])}"
    return f"VC '{vc_key}' not found. Available: {', '.join(ai_vcs.keys())}"

if __name__ == "__main__":
    mcp.run()