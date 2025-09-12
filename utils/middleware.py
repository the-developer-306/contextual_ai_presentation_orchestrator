# utils/middleware.py
import json
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from utils.audit import write_audit
from utils.masking import mask_all_sensitive

BANNED_KEYWORDS = {"classified", "secret", "ssn", "pan"}  # example — tune as needed

class AuditAndFilterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        body = None
        
        # Skip content filtering for file uploads and other binary content
        content_type = request.headers.get("content-type", "")
        
        # Skip processing for multipart/form-data (file uploads)
        if content_type.startswith("multipart/form-data"):
            # Still audit the request, but skip content filtering
            response = await call_next(request)
            
            # Audit log for file uploads (no body content)
            log = {
                "path": request.url.path,
                "method": request.method,
                "status_code": response.status_code,
                "duration_sec": time.time() - start_time,
                "content_type": "file_upload",
                "body_preview": "[FILE_UPLOAD_SKIPPED]"
            }
            write_audit(log)
            return response
        
        # Skip processing for other binary content types
        binary_types = [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument",
            "application/msword",
            "image/",
            "video/",
            "audio/"
        ]
        
        if any(content_type.startswith(bt) for bt in binary_types):
            response = await call_next(request)
            
            log = {
                "path": request.url.path,
                "method": request.method,
                "status_code": response.status_code,
                "duration_sec": time.time() - start_time,
                "content_type": content_type,
                "body_preview": "[BINARY_CONTENT_SKIPPED]"
            }
            write_audit(log)
            return response

        # Process only JSON and text content for filtering
        try:
            body_bytes = await request.body()
            if body_bytes:
                try:
                    # Try to parse as JSON first
                    if content_type.startswith("application/json"):
                        body = json.loads(body_bytes.decode("utf-8"))
                    # Handle form data and text content
                    elif content_type.startswith(("application/x-www-form-urlencoded", "text/")):
                        body = body_bytes.decode("utf-8", errors="ignore")
                    else:
                        # For other content types, try to decode as text but don't fail
                        try:
                            body = body_bytes.decode("utf-8")
                        except UnicodeDecodeError:
                            body = None  # Skip processing for non-text content
                except (json.JSONDecodeError, UnicodeDecodeError):
                    body = None
        except Exception:
            body = None

        # Content filtering: only check if we have processable content
        if body is not None:
            str_body = json.dumps(body) if isinstance(body, dict) else str(body)
            lower = str_body.lower()
            blocked = any(word in lower for word in BANNED_KEYWORDS)

            if blocked:
                audit_entry = {
                    "path": request.url.path,
                    "method": request.method,
                    "user": "unknown",
                    "action": "blocked_content",
                    "reason": "banned_keyword_detected",
                    "body_preview": mask_all_sensitive(str_body)[:800]
                }
                write_audit(audit_entry)
                return JSONResponse(
                    status_code=403, 
                    content={"detail": "Content not allowed"}
                )

        # Proceed with request
        response = await call_next(request)

        # Audit log: record request/response summary (mask sensitive)
        str_body_for_log = ""
        if body is not None:
            str_body_for_log = json.dumps(body) if isinstance(body, dict) else str(body)
        
        log = {
            "path": request.url.path,
            "method": request.method,
            "status_code": response.status_code,
            "duration_sec": time.time() - start_time,
            "content_type": content_type,
            "body_preview": mask_all_sensitive(str_body_for_log)[:800] if str_body_for_log else "[NO_BODY]"
        }
        write_audit(log)
        return response
