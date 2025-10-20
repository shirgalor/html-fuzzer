"""
Abstract Navigator Base Classes
================================
Defines the interface for browser navigation operations.

All navigator implementations must inherit from the Navigator base class
and implement browser-specific navigation strategies.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, List, Optional, Dict
import time


class NavigationResult:
    """Result of a navigation operation"""
    
    def __init__(self, success: bool, url: str, message: str = "", error: Optional[Exception] = None):
        self.success = success
        self.url = url
        self.message = message
        self.error = error
    
    def __bool__(self):
        return self.success
    
    def __repr__(self):
        status = "✓" if self.success else "✗"
        return f"NavigationResult({status} {self.url}: {self.message})"


class Navigator(ABC):
    """
    Abstract base class for browser navigation.
    
    All browser-specific navigator implementations must inherit from this class
    and implement the abstract methods.
    """
    
    def __init__(self, driver: Any):
        """
        Initialize navigator with a Selenium WebDriver instance.
        
        Args:
            driver: Selenium WebDriver instance (already attached to browser)
        """
        self.driver = driver
    
    @abstractmethod
    def navigate_to_url(self, url: str, wait_time: float = 2.0) -> NavigationResult:
        """
        Navigate to a specific URL.
        
        Args:
            url: Target URL (http://, https://, or file://)
            wait_time: Seconds to wait after navigation
        
        Returns:
            NavigationResult indicating success/failure
        """
        pass
    
    @abstractmethod
    def open_local_html_files(
        self,
        folder_path: Path,
        pattern: str = "*.html",
        new_tabs: bool = True,
        wait_per_page: float = 0.5
    ) -> List[str]:
        """
        Open multiple local HTML files.
        
        Args:
            folder_path: Directory containing HTML files
            pattern: Glob pattern for file matching
            new_tabs: Open in new tabs (True) or replace current page (False)
            wait_per_page: Seconds to wait between opening files
        
        Returns:
            List of file:// URLs that were opened
        """
        pass
    
    def get_current_url(self) -> str:
        """Get the current page URL"""
        try:
            return self.driver.current_url
        except Exception:
            return ""
    
    def get_page_title(self) -> str:
        """Get the current page title"""
        try:
            return self.driver.title
        except Exception:
            return ""
    
    def get_window_handles(self) -> List[str]:
        """Get all window/tab handles"""
        try:
            return self.driver.window_handles
        except Exception:
            return []
    
    def switch_to_window(self, handle: str) -> bool:
        """
        Switch to a specific window/tab.
        
        Args:
            handle: Window handle to switch to
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.driver.switch_to.window(handle)
            return True
        except Exception:
            return False
    
    def switch_to_window_by_index(self, index: int) -> bool:
        """
        Switch to window/tab by index.
        
        Args:
            index: Zero-based index of window
        
        Returns:
            True if successful, False otherwise
        """
        try:
            handles = self.get_window_handles()
            if 0 <= index < len(handles):
                return self.switch_to_window(handles[index])
            return False
        except Exception:
            return False
    
    def close_current_tab(self) -> bool:
        """
        Close the current tab.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.driver.close()
            return True
        except Exception:
            return False
    
    def get_page_info(self) -> Dict[str, Any]:
        """
        Get comprehensive information about the current page.
        
        Returns:
            Dictionary with page metadata
        """
        return {
            'url': self.get_current_url(),
            'title': self.get_page_title(),
            'window_count': len(self.get_window_handles()),
        }
    
    def wait(self, seconds: float):
        """Convenience method for waiting"""
        time.sleep(seconds)
