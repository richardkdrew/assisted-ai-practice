"""Documentation tools for feature investigation."""

from datetime import datetime
from pathlib import Path
from typing import Any

from investigator_agent.tools.jira import get_folder_by_feature_id


async def list_docs(feature_id: str) -> list[dict[str, Any]]:
    """
    List all documentation files for a specific feature.

    This tool scans the planning directory for a feature and returns
    metadata about available documentation files. Use this before
    read_doc to see what documentation is available.

    Args:
        feature_id: Feature identifier (e.g., 'FEAT-MS-001')

    Returns:
        List of dictionaries containing file metadata:
        - path: Relative path to the file
        - name: File name
        - size: File size in bytes
        - modified: Last modified timestamp (ISO format)

    Raises:
        ValueError: If feature_id is invalid
        FileNotFoundError: If planning directory doesn't exist
    """
    # Get folder for feature
    folder = get_folder_by_feature_id(feature_id)

    # Build path to planning directory
    planning_dir = Path(f"incoming_data/{folder}/planning")

    # Check if directory exists
    if not planning_dir.exists():
        raise FileNotFoundError(
            f"Planning directory not found: {planning_dir}. "
            f"Feature '{feature_id}' may not have documentation available."
        )

    # Scan for markdown files
    docs = []
    for file_path in sorted(planning_dir.glob("*.md")):
        stat = file_path.stat()
        docs.append(
            {
                "path": str(file_path),
                "name": file_path.name,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            }
        )

    return docs


# Tool schema for list_docs
LIST_DOCS_SCHEMA = {
    "type": "object",
    "properties": {
        "feature_id": {
            "type": "string",
            "description": "Feature identifier (e.g., 'FEAT-MS-001')",
        }
    },
    "required": ["feature_id"],
}


async def read_doc(path: str) -> str:
    """
    Read the contents of a documentation file.

    Use this tool after list_docs to read specific documentation files.
    Large files may trigger sub-conversation creation for analysis.

    Args:
        path: Path to the documentation file (from list_docs)

    Returns:
        String containing the full file contents

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If path is not in incoming_data/ (security check)
    """
    file_path = Path(path)

    # Security check: ensure path is within incoming_data/
    try:
        file_path.resolve().relative_to(Path("incoming_data").resolve())
    except ValueError:
        raise ValueError(
            f"Invalid path '{path}'. Path must be within incoming_data/ directory."
        )

    # Check if file exists
    if not file_path.exists():
        raise FileNotFoundError(
            f"Documentation file not found: {path}. "
            "Use list_docs to see available files."
        )

    # Read and return contents
    with open(file_path, "r", encoding="utf-8") as f:
        contents = f.read()

    return contents


# Tool schema for read_doc
READ_DOC_SCHEMA = {
    "type": "object",
    "properties": {
        "path": {
            "type": "string",
            "description": (
                "Path to the documentation file. "
                "Get this from list_docs output (use the 'path' field)."
            ),
        }
    },
    "required": ["path"],
}
