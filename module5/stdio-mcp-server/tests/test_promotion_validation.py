"""Tests for promotion-specific validation functions."""

import pytest
from src.validation import (
    validate_non_empty,
    validate_promotion_path,
    VALID_PROMOTION_PATHS,
)


class TestValidateNonEmpty:
    """Tests for validate_non_empty function."""

    def test_valid_non_empty_string(self):
        """Standard non-empty string should pass validation."""
        result = validate_non_empty("app", "web-api")
        assert result == "web-api"

    def test_valid_with_whitespace(self):
        """Whitespace should be trimmed."""
        result = validate_non_empty("version", "  1.2.3  ")
        assert result == "1.2.3"

    def test_empty_string_raises_error(self):
        """Empty string should raise ValueError."""
        with pytest.raises(ValueError, match="app cannot be empty"):
            validate_non_empty("app", "")

    def test_whitespace_only_raises_error(self):
        """Whitespace-only string should raise ValueError."""
        with pytest.raises(ValueError, match="version cannot be empty"):
            validate_non_empty("version", "   ")

    def test_tab_newline_whitespace_raises_error(self):
        """All types of whitespace should be stripped."""
        with pytest.raises(ValueError, match="app cannot be empty"):
            validate_non_empty("app", "\t\n\r")


class TestValidatePromotionPath:
    """Tests for validate_promotion_path function."""

    def test_valid_dev_to_staging(self):
        """dev→staging is valid forward path."""
        validate_promotion_path("dev", "staging")  # Should not raise

    def test_valid_staging_to_uat(self):
        """staging→uat is valid forward path."""
        validate_promotion_path("staging", "uat")  # Should not raise

    def test_valid_uat_to_prod(self):
        """uat→prod is valid forward path (production deployment)."""
        validate_promotion_path("uat", "prod")  # Should not raise

    def test_invalid_same_environment(self):
        """Promoting to same environment should be rejected."""
        with pytest.raises(ValueError, match="cannot promote to same environment"):
            validate_promotion_path("dev", "dev")

    def test_invalid_skipping_staging(self):
        """Cannot skip staging from dev."""
        with pytest.raises(ValueError) as exc_info:
            validate_promotion_path("dev", "uat")

        error_msg = str(exc_info.value)
        assert "invalid promotion path" in error_msg
        assert "dev→uat" in error_msg or "dev->uat" in error_msg
        assert "staging" in error_msg

    def test_invalid_skipping_uat(self):
        """Cannot skip uat from staging."""
        with pytest.raises(ValueError) as exc_info:
            validate_promotion_path("staging", "prod")

        error_msg = str(exc_info.value)
        assert "invalid promotion path" in error_msg
        assert "staging→prod" in error_msg or "staging->prod" in error_msg
        assert "uat" in error_msg

    def test_invalid_backward_prod_to_uat(self):
        """Backward promotion from prod should be rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_promotion_path("prod", "uat")

        error_msg = str(exc_info.value)
        assert "invalid promotion path" in error_msg
        assert "prod→uat" in error_msg or "prod->uat" in error_msg
        assert "backward" in error_msg

    def test_invalid_backward_staging_to_dev(self):
        """Backward promotion from staging should be rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_promotion_path("staging", "dev")

        error_msg = str(exc_info.value)
        assert "invalid promotion path" in error_msg
        assert "staging→dev" in error_msg or "staging->dev" in error_msg
        assert "backward" in error_msg


class TestPromotionPathsConstant:
    """Tests for VALID_PROMOTION_PATHS constant."""

    def test_promotion_paths_structure(self):
        """Verify promotion paths are correctly defined."""
        assert ("dev", "staging") in VALID_PROMOTION_PATHS
        assert ("staging", "uat") in VALID_PROMOTION_PATHS
        assert ("uat", "prod") in VALID_PROMOTION_PATHS
        assert len(VALID_PROMOTION_PATHS) == 3

    def test_promotion_paths_immutable(self):
        """VALID_PROMOTION_PATHS should be immutable frozenset."""
        assert isinstance(VALID_PROMOTION_PATHS, frozenset)
