"""
Browser Factory
===============
Factory for creating complete browser instances.

Each browser bundles together:
- Launcher (how to launch)
- Navigator (how to navigate)
- Pipeline (complete workflow)
- Attack names (browser-specific tests)
"""

from enum import Enum
from typing import Dict, Type
from .base import BaseBrowser
from .comet import CometBrowser


class BrowserType(Enum):
    """Supported browser types."""
    COMET = "comet"



# Registry mapping browser types to their classes
_BROWSER_CLASSES: Dict[BrowserType, Type[BaseBrowser]] = {
    BrowserType.COMET: CometBrowser,
}


class BrowserFactory:
    """
    Factory for creating complete browser instances.
    
    This is the highest-level factory that creates a complete Browser object
    which internally composes:
    - BrowserLauncher (from browser_launcher module)
    - Navigator (from navigator module)
    - Pipeline (from pipeline module)
    - Attack names (browser-specific)

    """
    
    @staticmethod
    def create(browser_type: BrowserType) -> BaseBrowser:
        """
        Create a complete browser instance.
        
        Args:
            browser_type: Type of browser to create (from BrowserType enum)
            
        Returns:
            Instance of the appropriate browser class
            
        Raises:
            ValueError: If browser_type is not supported
        """
        if browser_type not in _BROWSER_CLASSES:
            supported = ", ".join(bt.value for bt in _BROWSER_CLASSES.keys())
            raise ValueError(
                f"Unsupported browser type: {browser_type.value}. "
                f"Supported types: {supported}"
            )
        
        browser_class = _BROWSER_CLASSES[browser_type]
        return browser_class()
    
    @staticmethod
    def register_browser(
        browser_type: BrowserType,
        browser_class: Type[BaseBrowser]
    ):
        """
        Register a new browser type.
        
        This allows external code to add support for new browsers
        without modifying this module.
        
        Args:
            browser_type: Browser type enum value
            browser_class: Class implementing BaseBrowser
        """
        if not issubclass(browser_class, BaseBrowser):
            raise TypeError(
                f"{browser_class.__name__} must inherit from BaseBrowser"
            )
        
        _BROWSER_CLASSES[browser_type] = browser_class
        print(f"[INFO] Registered browser: {browser_type.value} -> {browser_class.__name__}")
    
    @staticmethod
    def get_supported_types() -> list[BrowserType]:
        """
        Get list of all supported browser types.
        
        Returns:
            List of BrowserType enum values that can be created
        """
        return list(_BROWSER_CLASSES.keys())
    
    @staticmethod
    def list_browsers():
        """
        Print information about all supported browsers.
        """
        print("Supported Browsers:")
        print("=" * 60)
        
        for browser_type in _BROWSER_CLASSES.keys():
            browser = BrowserFactory.create(browser_type)
            info = browser.get_browser_info()
            attacks_count = len(browser.get_attack_names())
            
            print(f"\n{info.name}")
            print(f"  Type: {browser_type.value}")
            print(f"  DevTools: {info.supports_devtools}")
            print(f"  Extensions: {info.supports_extensions}")
            print(f"  Attack vectors: {attacks_count}")
        
        print("\n" + "=" * 60)


# Convenience function for simpler imports
def create_browser(browser_type: BrowserType) -> BaseBrowser:
    """
    Convenience function to create a browser.
    
    Equivalent to BrowserFactory.create() but shorter to type.
    
    Args:
        browser_type: Type of browser to create
        
    Returns:
        Browser instance

    """
    return BrowserFactory.create(browser_type)
