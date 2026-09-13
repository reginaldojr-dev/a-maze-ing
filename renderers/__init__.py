"""Initialization module for the renderers package,
        exporting terminal and graphical display engines."""

from .ascii_renderer import ASCIIRenderer

__all__ = ["ASCIIRenderer", "MLXRenderer"]
