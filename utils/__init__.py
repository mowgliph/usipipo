"""
Utils module for uSipipo bot.

Note: submodules (e.g. `utils.spinner`) should be imported explicitly to avoid heavy package-level imports
that pull optional dependencies (like `telegram`) during early bootstrap.
"""

# Keep the package import lightweight to avoid importing optional dependencies.
# Import submodules explicitly where needed, e.g. `from utils.spinner import SpinnerManager`.

__all__ = []