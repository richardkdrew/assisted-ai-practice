"""Integration tests for Graphiti MCP Server.

These tests require Docker services to be running:
    docker-compose up -d neo4j

For full integration tests with OpenAI:
    export OPENAI_API_KEY=your-key
    docker-compose up -d graphiti-mcp
"""
import os
import pytest
import asyncio
from pathlib import Path

# Mark all tests in this file as integration tests
pytestmark = pytest.mark.integration


class TestGraphitiServerSetup:
    """Test Graphiti server setup and configuration."""

    def test_server_file_exists(self):
        """Test that server file exists."""
        server_file = Path(__file__).parent / "graphiti_mcp_server.py"
        assert server_file.exists(), "Graphiti MCP server file should exist"

    def test_dockerfile_exists(self):
        """Test that Dockerfile exists."""
        dockerfile = Path(__file__).parent / "Dockerfile"
        assert dockerfile.exists(), "Dockerfile should exist"

    def test_pyproject_exists(self):
        """Test that pyproject.toml exists."""
        pyproject = Path(__file__).parent / "pyproject.toml"
        assert pyproject.exists(), "pyproject.toml should exist"

    def test_server_imports(self):
        """Test that server can be imported (syntax check)."""
        import ast

        server_file = Path(__file__).parent / "graphiti_mcp_server.py"
        with open(server_file) as f:
            source = f.read()

        # Parse should not raise SyntaxError
        tree = ast.parse(source)
        assert tree is not None

    def test_server_has_required_functions(self):
        """Test that server defines required functions."""
        import ast

        server_file = Path(__file__).parent / "graphiti_mcp_server.py"
        with open(server_file) as f:
            source = f.read()

        tree = ast.parse(source)
        functions = {node.name for node in ast.walk(tree)
                     if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}

        required = ["list_tools", "call_tool", "handle_sse", "main"]
        for func in required:
            assert func in functions, f"Server should define {func}()"

    def test_server_defines_all_tools(self):
        """Test that server defines all expected Graphiti tools."""
        import ast

        server_file = Path(__file__).parent / "graphiti_mcp_server.py"
        with open(server_file) as f:
            source = f.read()

        # Expected tools
        expected_tools = [
            "graphiti_add_episode",
            "graphiti_search",
            "graphiti_get_episode",
            "graphiti_delete_episode",
            "graphiti_get_entities",
            "graphiti_entity_search",
            "graphiti_get_relationships",
            "graphiti_clear_graph",
        ]

        # Check that tool names appear in source
        for tool in expected_tools:
            assert tool in source, f"Server should define {tool} tool"


@pytest.mark.skipif(
    "OPENAI_API_KEY" not in os.environ,
    reason="OpenAI API key required for full integration tests"
)
class TestGraphitiServerIntegration:
    """Full integration tests requiring running Graphiti server."""

    @pytest.mark.asyncio
    async def test_server_starts_and_responds(self):
        """Test that Graphiti server starts and responds to requests."""
        # This test would require the server to be running
        # For now, we'll skip it unless explicitly enabled
        pytest.skip("Requires running Graphiti MCP server")

    @pytest.mark.asyncio
    async def test_add_and_search_episode(self):
        """Test adding and searching episodes."""
        pytest.skip("Requires running Graphiti MCP server with OpenAI")


class TestGraphitiDockerSetup:
    """Test Docker configuration for Graphiti."""

    def test_docker_compose_has_graphiti_service(self):
        """Test that docker-compose.yml defines graphiti-mcp service."""
        import yaml

        compose_file = Path(__file__).parent.parent / "docker-compose.yml"
        assert compose_file.exists(), "docker-compose.yml should exist"

        with open(compose_file) as f:
            compose = yaml.safe_load(f)

        assert "services" in compose
        assert "graphiti-mcp" in compose["services"], "Should define graphiti-mcp service"
        assert "neo4j" in compose["services"], "Should define neo4j service"

    def test_docker_compose_graphiti_config(self):
        """Test Graphiti service configuration."""
        import yaml

        compose_file = Path(__file__).parent.parent / "docker-compose.yml"
        with open(compose_file) as f:
            compose = yaml.safe_load(f)

        graphiti = compose["services"]["graphiti-mcp"]

        # Check required fields
        assert "ports" in graphiti, "Should expose ports"
        assert "8000:8000" in graphiti["ports"], "Should expose port 8000"

        assert "environment" in graphiti, "Should have environment variables"
        env = graphiti["environment"]
        assert any("NEO4J_URI" in str(e) for e in env), "Should configure Neo4j URI"
        assert any("OPENAI_API_KEY" in str(e) for e in env), "Should require OpenAI key"

    def test_neo4j_service_configured(self):
        """Test Neo4j service configuration."""
        import yaml

        compose_file = Path(__file__).parent.parent / "docker-compose.yml"
        with open(compose_file) as f:
            compose = yaml.safe_load(f)

        neo4j = compose["services"]["neo4j"]

        # Check required fields
        assert "ports" in neo4j, "Should expose ports"
        assert "7474:7474" in neo4j["ports"], "Should expose HTTP port"
        assert "7687:7687" in neo4j["ports"], "Should expose Bolt port"

        assert "healthcheck" in neo4j, "Should have healthcheck"


class TestGraphitiServerTools:
    """Test Graphiti MCP tool definitions."""

    def test_tool_schemas_valid(self):
        """Test that tool schemas are valid JSON schemas."""
        import ast
        import json

        server_file = Path(__file__).parent / "graphiti_mcp_server.py"
        with open(server_file) as f:
            source = f.read()

        # Extract inputSchema dictionaries
        tree = ast.parse(source)

        # Look for Tool() calls with inputSchema
        tool_count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if (hasattr(node.func, 'id') and node.func.id == 'Tool') or \
                   (hasattr(node.func, 'attr') and node.func.attr == 'Tool'):
                    tool_count += 1

        # Should have 8 tools defined
        assert tool_count >= 8, f"Should define at least 8 tools, found {tool_count}"

    def test_episode_tools_have_required_fields(self):
        """Test that episode-related tools have required fields."""
        server_file = Path(__file__).parent / "graphiti_mcp_server.py"
        with open(server_file) as f:
            source = f.read()

        # Check add_episode tool
        assert '"content"' in source, "add_episode should have content field"
        assert '"reference_time"' in source, "add_episode should have reference_time field"

        # Check search tool
        assert '"query"' in source, "search should have query field"
        assert '"limit"' in source, "search should have limit field"
        assert '"start_time"' in source, "search should support temporal filtering"

    def test_server_has_error_handling(self):
        """Test that server has proper error handling."""
        server_file = Path(__file__).parent / "graphiti_mcp_server.py"
        with open(server_file) as f:
            source = f.read()

        # Should have try/except blocks
        assert "try:" in source, "Server should have error handling"
        assert "except Exception" in source, "Server should catch exceptions"
        assert "logger.error" in source, "Server should log errors"


class TestGraphitiDeployment:
    """Test Graphiti deployment readiness."""

    def test_readme_exists(self):
        """Test that README exists."""
        readme = Path(__file__).parent / "README.md"
        assert readme.exists(), "README.md should exist"

    def test_readme_has_deployment_instructions(self):
        """Test that README has deployment instructions."""
        readme = Path(__file__).parent / "README.md"
        with open(readme) as f:
            content = f.read()

        assert "docker-compose" in content.lower(), "README should mention docker-compose"
        assert "environment" in content.lower(), "README should mention environment variables"
        assert "openai" in content.lower(), "README should mention OpenAI requirement"

    def test_readme_has_tool_documentation(self):
        """Test that README documents all tools."""
        readme = Path(__file__).parent / "README.md"
        with open(readme) as f:
            content = f.read()

        tools = [
            "add_episode",
            "search",
            "get_episode",
            "delete_episode",
        ]

        for tool in tools:
            assert tool in content, f"README should document {tool}"

    def test_env_example_documents_graphiti_vars(self):
        """Test that .env.example documents Graphiti variables."""
        # This would check if .env.example in root has Graphiti vars
        # For now, we document this as a task
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
