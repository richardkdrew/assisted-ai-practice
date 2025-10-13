"""API routes for trace querying and observability.

This module provides FastAPI route handlers for trace queries.
"""

from typing import Optional
from fastapi import FastAPI
from fastapi.responses import JSONResponse

def register_trace_routes(app: FastAPI):
    """Register trace API routes with the FastAPI application.

    Args:
        app: FastAPI application instance
    """

    @app.get("/api/v1/traces/{trace_id}")
    async def get_trace_endpoint(trace_id: str):
        """
        Retrieve all spans for a specific trace ID.

        Args:
            trace_id: 32-character hex trace identifier

        Returns:
            JSON response with spans
        """
        from observability.trace_query.query import get_trace
        try:
            spans = get_trace(trace_id)
            return {"trace_id": trace_id, "spans": [span.__dict__ for span in spans]}
        except ValueError as e:
            return JSONResponse(status_code=400, content={"error": str(e)})
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})

    @app.get("/api/v1/traces/recent/failures")
    async def recent_failures_endpoint(hours: float = 1, max_results: int = 100):
        """
        Retrieve recent spans with ERROR status.

        Args:
            hours: Number of hours to look back (default: 1)
            max_results: Maximum number of results (default: 100)

        Returns:
            JSON response with spans
        """
        from observability.trace_query.query import recent_failures
        try:
            spans = recent_failures(hours=hours, max_results=max_results)
            return {"count": len(spans), "spans": [span.__dict__ for span in spans]}
        except ValueError as e:
            return JSONResponse(status_code=400, content={"error": str(e)})
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})

    @app.get("/api/v1/traces/filter/status/{status}")
    async def filter_by_status_endpoint(status: str, duration: str = "1h", max_results: int = 100):
        """
        Filter spans by status.

        Args:
            status: Status to filter by ("OK" or "ERROR")
            duration: Time duration to look back (e.g., "1h", "30m", "2d")
            max_results: Maximum number of results (default: 100)

        Returns:
            JSON response with spans
        """
        from observability.trace_query.query import filter_by_status
        try:
            spans = filter_by_status(status=status, time_range=duration, max_results=max_results)
            return {"count": len(spans), "spans": [span.__dict__ for span in spans]}
        except ValueError as e:
            return JSONResponse(status_code=400, content={"error": str(e)})
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})

    @app.get("/api/v1/traces/filter/time")
    async def filter_by_time_endpoint(
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        duration: Optional[str] = None,
        status: Optional[str] = None,
        max_results: int = 100
    ):
        """
        Filter spans by time range.

        Args:
            start_time: Start time (ISO format or relative time)
            end_time: End time (ISO format or relative time)
            duration: Alternative to start_time (e.g., "1h", "30m")
            status: Optional status filter ("OK" or "ERROR")
            max_results: Maximum number of results (default: 100)

        Returns:
            JSON response with spans
        """
        from observability.trace_query.query import filter_by_time
        try:
            spans = filter_by_time(
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                status=status,
                max_results=max_results
            )
            return {"count": len(spans), "spans": [span.__dict__ for span in spans]}
        except ValueError as e:
            return JSONResponse(status_code=400, content={"error": str(e)})
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})

    @app.get("/api/v1/traces/filter/error-type/{error_type}")
    async def filter_by_error_type_endpoint(error_type: str, max_results: int = 100):
        """
        Filter spans by error type.

        Args:
            error_type: Error type to filter by
            max_results: Maximum number of results (default: 100)

        Returns:
            JSON response with spans
        """
        from observability.trace_query.query import filter_by_error_type
        try:
            spans = filter_by_error_type(error_type=error_type, max_results=max_results)
            return {"count": len(spans), "spans": [span.__dict__ for span in spans]}
        except ValueError as e:
            return JSONResponse(status_code=400, content={"error": str(e)})
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})