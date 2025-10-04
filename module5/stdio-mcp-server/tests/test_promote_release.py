"""Integration tests for promote_release tool."""

import asyncio
import pytest
from unittest.mock import AsyncMock, patch
from src.server import CLIExecutionResult
import src.server as server_module


# Get the unwrapped function for testing
promote_release = server_module.promote_release.fn


@pytest.mark.asyncio
class TestPromoteReleaseIntegration:
    """Integration tests for promote_release tool."""

    @patch("src.server.execute_cli_command")
    async def test_success_non_production(self, mock_exec):
        """Successful non-production promotion returns success response."""
        mock_exec.return_value = CLIExecutionResult(
            stdout="Deployment successful: web-api v1.2.3 promoted to staging",
            stderr="",
            returncode=0,
        )

        result = await promote_release(
            app="web-api",
            version="1.2.3",
            from_env="dev",
            to_env="staging",
        )

        assert result["status"] == "success"
        assert result["promotion"]["app"] == "web-api"
        assert result["promotion"]["version"] == "1.2.3"
        assert result["promotion"]["from_env"] == "dev"
        assert result["promotion"]["to_env"] == "staging"
        assert result["production_deployment"] is False
        assert "timestamp" in result

        mock_exec.assert_called_once_with(
            ["promote", "web-api", "1.2.3", "dev", "staging"],
            timeout=300.0,
        )

    @patch("src.server.execute_cli_command")
    async def test_success_production_deployment(self, mock_exec):
        """Production deployment sets production_deployment flag."""
        mock_exec.return_value = CLIExecutionResult(
            stdout="Production deployment complete",
            stderr="",
            returncode=0,
        )

        result = await promote_release(
            app="mobile-app",
            version="2.0.1",
            from_env="uat",
            to_env="prod",
        )

        assert result["status"] == "success"
        assert result["production_deployment"] is True

    @pytest.mark.parametrize("app,expected_error", [
        ("", "app cannot be empty"),
        ("   ", "app cannot be empty"),
    ])
    async def test_validation_error_empty_app(self, app, expected_error):
        """Empty app parameter fails validation."""
        with pytest.raises(ValueError, match=expected_error):
            await promote_release(
                app=app,
                version="1.0.0",
                from_env="dev",
                to_env="staging",
            )

    async def test_validation_error_invalid_path(self):
        """Invalid promotion path fails validation."""
        with pytest.raises(ValueError, match="invalid promotion path"):
            await promote_release(
                app="web-api",
                version="1.0.0",
                from_env="dev",
                to_env="prod",  # Skipping staging and uat
            )

    @patch("src.server.execute_cli_command")
    async def test_cli_execution_failure(self, mock_exec):
        """CLI execution failure raises RuntimeError."""
        mock_exec.return_value = CLIExecutionResult(
            stdout="",
            stderr="Error: Version not found",
            returncode=1,
        )

        with pytest.raises(RuntimeError, match="Promotion failed"):
            await promote_release(
                app="web-api",
                version="9.9.9",
                from_env="dev",
                to_env="staging",
            )

    @patch("src.server.execute_cli_command")
    async def test_cli_timeout(self, mock_exec):
        """CLI timeout raises RuntimeError with helpful message."""
        mock_exec.side_effect = asyncio.TimeoutError()

        with pytest.raises(RuntimeError, match="timed out after 300 seconds"):
            await promote_release(
                app="slow-app",
                version="1.0.0",
                from_env="dev",
                to_env="staging",
            )

    @patch("src.server.execute_cli_command")
    async def test_case_insensitive_normalization(self, mock_exec):
        """Environment names normalized to lowercase."""
        mock_exec.return_value = CLIExecutionResult(
            stdout="Success",
            stderr="",
            returncode=0,
        )

        result = await promote_release(
            app="web-api",
            version="1.0.0",
            from_env="DEV",
            to_env="STAGING",
        )

        assert result["promotion"]["from_env"] == "dev"
        assert result["promotion"]["to_env"] == "staging"

        mock_exec.assert_called_once_with(
            ["promote", "web-api", "1.0.0", "dev", "staging"],
            timeout=300.0,
        )
