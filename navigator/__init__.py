"""
Navigator Module
================
Modular navigation architecture for different browsers.

Currently supports:
- Comet (Perplexity browser)

Easy to extend for future browsers (Chrome, Edge, Firefox, etc.)

Usage:
    from navigator import NavigatorFactory, NavigatorType, create_navigator
    
    # Simple usage
    driver = launch_browser()
    navigator = create_navigator(driver=driver)
    navigator.navigate_to_url("https://example.com")
    
    # Factory pattern
    navigator = NavigatorFactory.create(NavigatorType.COMET, driver)
    result = navigator.navigate_to_url("https://example.com")
    if result.success:
        print(f"Navigated to: {result.url}")
    
    # Open local HTML files
    urls = navigator.open_local_html_files(
        Path("htmls"),
        pattern="*.html",
        new_tabs=True
    )
"""

from .base import Navigator, NavigationResult
from .comet_navigator import CometNavigator
from .factory import NavigatorFactory, NavigatorType, create_navigator

__all__ = [
    'Navigator',
    'NavigationResult',
    'CometNavigator',
    'NavigatorFactory',
    'NavigatorType',
    'create_navigator',
]
