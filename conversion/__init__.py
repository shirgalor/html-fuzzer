"""
Conversion Package
==================
Factory and base classes for browser conversion operations.

Conversion handles communication with AI assistants:
- Sending queries
- Capturing responses
"""

from .factory import ConversionFactory, ConversionType
from .base import BaseConversion, ConversionResult

__all__ = ['ConversionFactory', 'ConversionType', 'BaseConversion', 'ConversionResult']
