"""Top-level package for the repository documentation generator service.

Data flow:
	API routes accept repository requests, an orchestration pipeline analyzes
	repository structure through GitHub APIs, and generated documentation is
	persisted in an in-memory/snapshot-backed job store for polling clients.
"""

