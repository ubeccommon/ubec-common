# /services/api/api_gateway_auth.py
"""
API Gateway Authentication Middleware
======================================

Security middleware to ensure only the API Gateway can access the backend.

This module implements:
    - API Key verification for all incoming requests
    - IP whitelist verification (optional, defense in depth)
    - Logging of rejected requests with timestamps

Installation:
    Add to your FastAPI application in api_service.py:
    
    from services.api.api_gateway_auth import APIGatewayAuthMiddleware
    
    # In BackendAPIService.__init__():
    self.app.add_middleware(APIGatewayAuthMiddleware)

Environment Variables:
    API_GATEWAY_KEY: Secret key shared between gateway and backend
    API_GATEWAY_IPS: Comma-separated list of allowed IPs (optional)

Design Principles Compliance:
    - Principle #5: All operations are async
    - Principle #9: Integrated rate limiting works alongside this middleware
    - Principle #10: Security concern separated from business logic
    - Principle #11: Comprehensive documentation

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform 
    our decisions and recommendations. This project was made possible with 
    the assistance of Claude and Anthropic PBC.
"""

import os
import logging
from datetime import datetime, timezone
from typing import List

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


# ============================================================================
# Configuration (Environment-based for security credentials)
# ============================================================================

def _get_gateway_key() -> str:
    """Get API gateway key from environment."""
    return os.getenv("API_GATEWAY_KEY", "")


def _get_allowed_ips() -> List[str]:
    """Get allowed IP addresses from environment."""
    ips = os.getenv("API_GATEWAY_IPS", "92.205.28.58,127.0.0.1")
    return [ip.strip() for ip in ips.split(",") if ip.strip()]


# Paths that don't require authentication
PUBLIC_PATHS = ["/health", "/healthz", "/", "/api/docs", "/api/redoc", "/openapi.json"]


# ============================================================================
# Middleware Class
# ============================================================================

class APIGatewayAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to authenticate requests from the API Gateway.
    
    Verifies:
        1. X-API-Gateway-Key header matches configured secret
        2. Request IP is in whitelist (if configured)
    
    Allows:
        - Health check endpoints without authentication
        - API documentation endpoints without authentication
        - Requests with valid API key from whitelisted IPs
    
    Example:
        >>> from services.api.api_gateway_auth import APIGatewayAuthMiddleware
        >>> app.add_middleware(APIGatewayAuthMiddleware)
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        Process incoming request through authentication checks.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain
            
        Returns:
            Response from next handler or 403 JSONResponse if unauthorized
        """
        client_ip = self._get_client_ip(request)
        path = request.url.path
        
        # Allow public paths without authentication
        if self._is_public_path(path):
            return await call_next(request)
        
        # Get current configuration
        gateway_key = _get_gateway_key()
        
        # Check if authentication is configured
        if not gateway_key:
            logger.warning(
                "API_GATEWAY_KEY not configured - allowing request (INSECURE)"
            )
            return await call_next(request)
        
        # Verify API key
        provided_key = request.headers.get("X-API-Gateway-Key", "")
        if provided_key != gateway_key:
            logger.warning(f"Invalid API key from {client_ip} for {path}")
            return self._forbidden_response(
                "Invalid API Gateway Key",
                "authentication_failed"
            )
        
        # Verify IP whitelist (defense in depth)
        if not self._is_allowed_ip(client_ip):
            logger.warning(f"Non-whitelisted IP: {client_ip} for {path}")
            return self._forbidden_response(
                "IP not authorized",
                "ip_not_allowed"
            )
        
        # Request authenticated - proceed
        logger.debug(f"Authenticated request from {client_ip} for {path}")
        return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP from request, considering reverse proxies.
        
        Args:
            request: HTTP request object
            
        Returns:
            Client IP address as string
        """
        # Check X-Forwarded-For header (set by reverse proxies)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        # Check X-Real-IP header (nginx convention)
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        # Fall back to direct connection IP
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _is_public_path(self, path: str) -> bool:
        """
        Check if path is public (no authentication required).
        
        Args:
            path: URL path to check
            
        Returns:
            True if path is public, False otherwise
        """
        for public_path in PUBLIC_PATHS:
            if path == public_path or path.startswith(public_path + "/"):
                return True
        return False
    
    def _is_allowed_ip(self, ip: str) -> bool:
        """
        Check if IP is in the whitelist.
        
        Args:
            ip: IP address to check
            
        Returns:
            True if IP is allowed, False otherwise
        """
        allowed_ips = _get_allowed_ips()
        if not allowed_ips:
            # No whitelist configured - rely on API key only
            return True
        return ip in allowed_ips
    
    def _forbidden_response(self, message: str, error_code: str) -> JSONResponse:
        """
        Create standardized 403 forbidden response.
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            
        Returns:
            JSONResponse with 403 status
        """
        return JSONResponse(
            status_code=403,
            content={
                "error": error_code,
                "message": f"Forbidden - {message}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )


# ============================================================================
# FastAPI Dependency (Alternative to Middleware)
# ============================================================================

async def verify_api_gateway_request(request: Request) -> bool:
    """
    Verify that a request came from the authorized API Gateway.
    
    Use as a FastAPI dependency for selective endpoint protection:
    
        from fastapi import Depends
        from services.api.api_gateway_auth import verify_api_gateway_request
        
        @app.get("/api/v1/admin/sensitive")
        async def sensitive_endpoint(
            request: Request,
            authorized: bool = Depends(verify_api_gateway_request)
        ):
            # Only reaches here if authorized
            return {"status": "authorized"}
    
    Args:
        request: FastAPI request object
    
    Returns:
        True if authorized
    
    Raises:
        HTTPException: 403 if not authorized
    """
    gateway_key = _get_gateway_key()
    
    if not gateway_key:
        # No key configured - allow (but log warning)
        logger.warning("API_GATEWAY_KEY not configured in dependency check")
        return True
    
    provided_key = request.headers.get("X-API-Gateway-Key", "")
    
    if provided_key != gateway_key:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "authentication_failed",
                "message": "Forbidden - Invalid API Gateway Key",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
    
    return True


# ============================================================================
# Integration Instructions
# ============================================================================

"""
INTEGRATION WITH api_service.py
===============================

Add the following to BackendAPIService.__init__() AFTER CORSMiddleware:

    # Import at top of file:
    from services.api.api_gateway_auth import APIGatewayAuthMiddleware
    
    # In __init__, after CORS middleware:
    self.app.add_middleware(APIGatewayAuthMiddleware)

Middleware order matters! The order should be:
    1. CORSMiddleware (outermost - handles preflight)
    2. APIGatewayAuthMiddleware (security check)
    3. Rate limiting (already handled via decorator)

DEPLOYMENT CHECKLIST
====================

Backend Server (92.205.230.245):

    1. Generate secure API key:
       $ python3 -c "import secrets; print(secrets.token_urlsafe(32))"
    
    2. Add to .env file:
       API_GATEWAY_KEY=<generated_key>
       API_GATEWAY_IPS=92.205.28.58,127.0.0.1
    
    3. Restart backend service:
       $ sudo systemctl restart ubec-backend

API Gateway Server (92.205.28.58):

    1. Add same API key to gateway .env:
       API_GATEWAY_KEY=<same_generated_key>
    
    2. Update gateway code to include header in requests:
       headers = {"X-API-Gateway-Key": os.getenv("API_GATEWAY_KEY")}
    
    3. Restart gateway service:
       $ sudo systemctl restart ubec-api

Firewall Configuration (Backend):

    $ sudo ufw allow from 92.205.28.58 to any port 8000 comment 'UBEC API Gateway'
    $ sudo ufw deny 8000 comment 'Block direct backend access'
    $ sudo ufw reload

TESTING
=======

    # Should return 403 (direct access without key):
    $ curl http://92.205.230.245:8000/api/v1/tokens
    
    # Should work (with valid key):
    $ curl -H "X-API-Gateway-Key: <your_key>" http://92.205.230.245:8000/api/v1/tokens
    
    # Should work (via gateway):
    $ curl https://api.ubec.network/v1/tokens
    
    # Health check should always work:
    $ curl http://92.205.230.245:8000/health
"""
