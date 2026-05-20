"""Version information for biovalid package."""

try:
    from importlib.metadata import version

    __version__ = version("biovalid")
except ImportError:
    # Fallback if running from source without installation
    __version__ = "0.4.0"
