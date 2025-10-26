"""
Browser Module
==============
High-level browser abstraction that composes all browser-specific components.

A Browser is a complete package that includes:
- Launcher: How to launch and attach to the browser
- Navigator: How to navigate pages and manage tabs
- Pipeline: Complete automation workflows
- Attack names: Browser-specific vulnerability test cases

This is the highest level of abstraction - use this when you want
to work with a complete browser without worrying about individual components.

Usage:
    # Simple usage
    from browser import BrowserFactory, BrowserType
    
    browser = BrowserFactory.create(BrowserType.COMET)
    browser.launch()
    browser.navigate_to("https://example.com")
    browser.quit()
    
    # Context manager (recommended)
    with BrowserFactory.create(BrowserType.COMET) as browser:
        browser.navigate_to("https://test.com")
        attacks = browser.get_attack_names()
        print(f"Testing {len(attacks)} attack vectors")
    
    # Using pipeline for complete workflow
    from pipeline import PipelineConfig
    
    browser = BrowserFactory.create(BrowserType.COMET)
    config = PipelineConfig(
        target_url="https://example.com",
        keep_open=True
    )
    result = browser.run_pipeline(config)
    
    # Fuzzing with attack names
    browser = BrowserFactory.create(BrowserType.COMET)
    browser.launch()
    
    for attack in browser.get_attack_names():
        print(f"Testing {attack}...")
        # Run fuzzing tests

Available Browsers:
    - CometBrowser: Perplexity Comet with AI Assistant
    - (Future) ChromeBrowser: Google Chrome
    - (Future) FirefoxBrowser: Mozilla Firefox
    - (Future) EdgeBrowser: Microsoft Edge
"""

from .base import BaseBrowser, BrowserInfo
from .comet import CometBrowser
from .factory import BrowserFactory, BrowserType, create_browser

__all__ = [
    # Base classes
    "BaseBrowser",
    "BrowserInfo",
    
    # Concrete implementations
    "CometBrowser",
    
    # Factory
    "BrowserFactory",
    "BrowserType",
    "create_browser",
]
