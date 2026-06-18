"""
Utility Components Module
Abstracts mathematical, cryptographic, and security verification processes.
"""
import hashlib
import urllib.parse
from urllib.parse import urlparse, urljoin
from flask import request

def is_safe_url(target):
    """
    Evaluates absolute location properties to stop unauthorized third-party redirects.
    Validates redirect metrics exclusively within the safe host platform boundary.
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

def gravatar_url(email, size=100, default='identicon', rating='g'):
    """
    Converts individual identifiers into low-profile secure MD5 string structures.
    Connects anonymously to online avatar systems without exposing raw text addresses.
    """
    if not email:
        email = 'default@example.com'
    clean_email = email.strip().lower()
    hash_value = hashlib.md5(clean_email.encode('utf-8')).hexdigest()
    query_string = urllib.parse.urlencode({'d': default, 's': str(size), 'r': rating})
    return f"https://www.gravatar.com/avatar/{hash_value}?{query_string}"