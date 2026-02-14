def shorten_filename(filename, max_len=40):
    """Shortens a filename to a maximum length, adding ellipsis."""
    return filename if len(filename) <= max_len else filename[:max_len-3] + "..."

def format_seconds(seconds):
    """Formats seconds into MM:SS Min string."""
    m, s = divmod(max(0, seconds), 60)
    return f"{int(m):02d}:{int(s):02d} Min"
