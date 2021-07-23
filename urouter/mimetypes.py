# TODO: local-file database
MAP: dict = {
    ".txt": "text/plain",
    ".htm": "text/html",
    ".html": "text/html",
    ".css": "text/css",
    ".csv": "text/csv",
    ".js": "application/javascript",
    ".xml": "application/xml",
    ".xhtml": "application/xhtml+xml",
    ".json": "application/json",
    ".zip": "application/zip",
    ".pdf": "application/pdf",
    ".ts": "application/typescript",
    ".woff": "font/woff",
    ".woff2": "font/woff2",
    ".ttf": "font/ttf",
    ".otf": "font/otf",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon"
    # others : "application/octet-stream"
}


def get(suf: str, default: str = "application/octet-stream") -> str:
    """
    Pass in a file suffix, return its immetype
    """
    return MAP.get(suf, default)
