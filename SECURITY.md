# Security Notes

## Object Authorization Policy
- All object access must pass one of: owner, public, or admin/system role.
- Not Found returns 404; Forbidden returns 403 (existence not leaked beyond 403 for lists).
- Service-layer checks are mandatory for Model API keys and MCP servers.

## Secret Handling
- Do not store or return secrets in API responses.
- Do not embed secrets in code or frontend assets.
- Use environment variables or a secret manager for runtime injection.

## Audit Logging (Recommended)
- Log access to Model API keys and MCP servers with user ID and object ID.
- Log authorization failures (403) with request metadata.
