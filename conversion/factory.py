"""
Conversion Factory
==================
Factory for creating conversion instances based on browser type.

NOTE: Conversion implementations live in browser/<browser_type>/conversion.py
"""

from typing import Any
from enum import Enum


class ConversionType(Enum):
    """Supported conversion types."""
    COMET = "comet"


class ConversionFactory:
    """
    Factory for creating browser-specific conversion handlers.
    """
    
    @staticmethod
    def create(conversion_type: ConversionType, driver: Any, navigator: Any = None):
        """
        Create a conversion handler for the specified browser type.
        
        Args:
            conversion_type: Type of conversion to create
            driver: Selenium WebDriver instance
            navigator: Navigator instance (optional)
            
        Returns:
            Conversion instance for the specified browser
            
        Raises:
            ValueError: If conversion type is not supported
        """
        if conversion_type == ConversionType.COMET:
            # Import from browser/comet/ folder (not from conversion/comet/)
            from browser.comet.conversion import CometConversion
            return CometConversion(driver, navigator)
        else:
            raise ValueError(f"Unsupported conversion type: {conversion_type}")
