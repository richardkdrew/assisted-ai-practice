"""
File I/O operations for span storage.

This module provides functionality for storing and retrieving spans from files,
handling file path validation, append operations, and error handling.
"""

import json
import os
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional, TextIO, Union

from .models import StoredSpan


class FileStorage:
    """
    Handles file I/O operations for span storage.

    This class provides thread-safe operations for storing spans to a file
    and loading spans from a file, with proper error handling and file
    path validation.
    """

    def __init__(self, file_path: str):
        """
        Initialize the file storage with a file path.

        Args:
            file_path: Path to the trace storage file

        Raises:
            ValueError: If file_path is empty
            IOError: If the file cannot be created or accessed
        """
        if not file_path:
            raise ValueError("File path cannot be empty")

        self.file_path = Path(file_path)
        self._file_lock = threading.Lock()
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """
        Ensure that the storage file exists and is accessible.

        Creates the parent directories if they don't exist.

        Raises:
            IOError: If the file cannot be created or accessed
        """
        try:
            # Create parent directories if they don't exist
            self.file_path.parent.mkdir(parents=True, exist_ok=True)

            # Touch the file if it doesn't exist
            if not self.file_path.exists():
                self.file_path.touch()
        except (IOError, PermissionError) as e:
            raise IOError(f"Failed to create or access file: {self.file_path}") from e

    def _validate_span(self, span: Union[StoredSpan, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate and convert span to dictionary for storage.

        Args:
            span: The span to validate (StoredSpan object or dict)

        Returns:
            Dictionary representation of the span

        Raises:
            ValueError: If the span is invalid
        """
        if isinstance(span, StoredSpan):
            return span.to_dict()
        elif isinstance(span, dict):
            # Validate by converting to StoredSpan and back to dict
            return StoredSpan.from_dict(span).to_dict()
        else:
            raise ValueError(f"Invalid span type: {type(span)}. Must be StoredSpan or dict.")

    def append_span(self, span: Union[StoredSpan, Dict[str, Any]]) -> None:
        """
        Append a span to the storage file.

        This operation is atomic and thread-safe. It validates the span
        before writing it to the file.

        Args:
            span: The span to append (StoredSpan object or dict)

        Raises:
            ValueError: If the span is invalid
            IOError: If the file cannot be written to
        """
        span_dict = self._validate_span(span)

        try:
            with self._file_lock:
                with open(self.file_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(span_dict) + "\n")
        except (IOError, PermissionError) as e:
            raise IOError(f"Failed to write span to file: {self.file_path}") from e

    def append_spans(self, spans: List[Union[StoredSpan, Dict[str, Any]]]) -> None:
        """
        Append multiple spans to the storage file in a single operation.

        This operation is atomic and thread-safe. It validates each span
        before writing it to the file.

        Args:
            spans: List of spans to append (StoredSpan objects or dicts)

        Raises:
            ValueError: If any span is invalid
            IOError: If the file cannot be written to
        """
        if not spans:
            return

        try:
            with self._file_lock:
                with open(self.file_path, "a", encoding="utf-8") as f:
                    for span in spans:
                        span_dict = self._validate_span(span)
                        f.write(json.dumps(span_dict) + "\n")
        except (IOError, PermissionError) as e:
            raise IOError(f"Failed to write spans to file: {self.file_path}") from e

    def read_spans(self, max_spans: Optional[int] = None) -> List[StoredSpan]:
        """
        Read spans from the storage file.

        Args:
            max_spans: Maximum number of spans to read (reads all if None)

        Returns:
            List of StoredSpan objects read from the file

        Raises:
            IOError: If the file cannot be read
            ValueError: If any span in the file is invalid
        """
        spans = []

        try:
            with self._file_lock:
                # Check if file exists and has content
                if not self.file_path.exists() or self.file_path.stat().st_size == 0:
                    return spans

                with open(self.file_path, "r", encoding="utf-8") as f:
                    for i, line in enumerate(f):
                        if max_spans is not None and i >= max_spans:
                            break

                        if not line.strip():
                            continue

                        try:
                            span_dict = json.loads(line)
                            spans.append(StoredSpan.from_dict(span_dict))
                        except json.JSONDecodeError as e:
                            raise ValueError(f"Invalid JSON on line {i+1}: {line}") from e
                        except ValueError as e:
                            raise ValueError(f"Invalid span on line {i+1}: {e}") from e
        except (IOError, PermissionError) as e:
            raise IOError(f"Failed to read spans from file: {self.file_path}") from e

        return spans

    def get_file_size(self) -> int:
        """
        Get the size of the storage file in bytes.

        Returns:
            Size of the file in bytes (0 if the file doesn't exist)

        Raises:
            IOError: If the file cannot be accessed
        """
        try:
            with self._file_lock:
                if not self.file_path.exists():
                    return 0
                return self.file_path.stat().st_size
        except (IOError, PermissionError) as e:
            raise IOError(f"Failed to get file size: {self.file_path}") from e

    def get_span_count(self) -> int:
        """
        Get the number of spans in the storage file.

        This is an estimate based on the number of non-empty lines in the file.

        Returns:
            Number of spans in the file

        Raises:
            IOError: If the file cannot be read
        """
        try:
            with self._file_lock:
                if not self.file_path.exists() or self.file_path.stat().st_size == 0:
                    return 0

                with open(self.file_path, "r", encoding="utf-8") as f:
                    return sum(1 for line in f if line.strip())
        except (IOError, PermissionError) as e:
            raise IOError(f"Failed to count spans in file: {self.file_path}") from e

    def clear(self) -> None:
        """
        Clear the storage file.

        This operation is atomic and thread-safe.

        Raises:
            IOError: If the file cannot be cleared
        """
        try:
            with self._file_lock:
                with open(self.file_path, "w", encoding="utf-8") as f:
                    pass  # Truncate the file
        except (IOError, PermissionError) as e:
            raise IOError(f"Failed to clear file: {self.file_path}") from e

    def truncate_to_last_n_spans(self, n: int) -> None:
        """
        Truncate the storage file to keep only the last N spans.

        This operation is atomic and thread-safe.

        Args:
            n: Number of spans to keep

        Raises:
            ValueError: If n is not positive
            IOError: If the file cannot be truncated
        """
        if n <= 0:
            raise ValueError(f"Invalid n: {n}. Must be positive.")

        try:
            spans = self.read_spans()
            if len(spans) <= n:
                return  # No need to truncate

            # Keep only the last n spans
            spans_to_keep = spans[-n:]
            self.clear()
            self.append_spans(spans_to_keep)
        except (IOError, ValueError) as e:
            raise IOError(f"Failed to truncate file to last {n} spans: {e}") from e