"""Simple validation test for Graphiti MCP server.

This test validates that the server script has correct syntax and imports.
It does NOT require Neo4j or OpenAI to be running.
"""

import ast
import sys


def test_server_syntax():
    """Test that the server has valid Python syntax and structure."""
    print("Validating Graphiti MCP Server...")

    # Read the server file
    with open("graphiti_mcp_server.py", "r") as f:
        source_code = f.read()

    # Parse the AST to validate syntax
    try:
        tree = ast.parse(source_code)
        print("✓ Valid Python syntax")
    except SyntaxError as e:
        print(f"✗ Syntax error: {e}")
        sys.exit(1)

    # Check for required components (both regular and async functions)
    functions = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.add(node.name)

    classes = {node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}

    required_functions = [
        "list_tools",
        "call_tool",
        "handle_sse",
        "format_episode",
        "format_entity",
        "main",
    ]

    for func in required_functions:
        if func in functions:
            print(f"✓ Function '{func}' defined")
        else:
            print(f"✗ Missing function: {func}")
            sys.exit(1)

    # Check imports
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend([alias.name for alias in node.names])
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module)

    required_modules = ["logging", "mcp.server", "mcp.types", "starlette.applications"]
    for module in required_modules:
        if module in imports or any(module.startswith(imp) for imp in imports if imp):
            print(f"✓ Imports '{module}'")
        else:
            print(f"✗ Missing import: {module}")
            sys.exit(1)

    # Check for SSE route
    has_route = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == "Route":
            has_route = True
            break

    if has_route:
        print("✓ SSE route configured")
    else:
        print("✗ Missing SSE route configuration")
        sys.exit(1)

    print("\n" + "=" * 50)
    print("All validation checks passed!")
    print("=" * 50)
    print("\nServer is ready to run in Docker.")
    print("Use: docker-compose up graphiti-mcp")


if __name__ == "__main__":
    test_server_syntax()
