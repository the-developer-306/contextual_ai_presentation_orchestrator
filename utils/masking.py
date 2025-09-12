# utils/masking.py
import re

def mask_all_sensitive(text: str) -> str:
    """
    Mask sensitive information in text content.
    Add more patterns as needed for your use case.
    """
    if not isinstance(text, str):
        return str(text)
    
    # Email masking
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '***@***.***', text)
    
    # Phone number masking (basic patterns)
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '***-***-****', text)
    
    # SSN masking
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '***-**-****', text)
    
    # Credit card masking (basic)
    text = re.sub(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', '****-****-****-****', text)
    
    # Password field masking
    text = re.sub(r'("password"\s*:\s*")[^"]*(")', r'\1****\2', text, flags=re.IGNORECASE)
    
    # Token masking
    text = re.sub(r'("token"\s*:\s*")[^"]*(")', r'\1****\2', text, flags=re.IGNORECASE)
    
    return text
