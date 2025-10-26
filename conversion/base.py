"""
Base Conversion Class
=====================
Abstract base class for browser conversion operations.

Conversion handles the communication layer with AI assistants.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class ConversionResult:
    """
    Result of a conversion operation.
    
    Attributes:
        success: Whether the operation succeeded
        query: The query that was sent
        response: The assistant's response text (if captured)
        response_html: The assistant's response HTML (if captured)
        html_filepath: Path to saved HTML file (if saved)
        text_filepath: Path to saved text file (if saved)
        error: Error message if failed
    """
    success: bool
    query: str
    response: Optional[str] = None
    response_html: Optional[str] = None
    html_filepath: Optional[str] = None
    text_filepath: Optional[str] = None
    error: Optional[str] = None


class BaseConversion(ABC):
    """
    Abstract base class for browser conversion operations.
    
    Each browser type implements its own conversion logic for:
    - Sending queries to AI assistants
    - Capturing responses from assistants
    """
    
    def __init__(self, driver: Any, navigator: Any = None):
        """
        Initialize conversion handler.
        
        Args:
            driver: Selenium WebDriver instance
            navigator: Navigator instance (optional, for navigation helpers)
        """
        self.driver = driver
        self.navigator = navigator
    
    @abstractmethod
    def send_query(self, query: str, submit: bool = True) -> bool:
        """
        Send a query to the AI assistant.
        
        Args:
            query: The question/prompt to send
            submit: Whether to submit (True) or just type (False)
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def capture_response(self, wait_for_completion: bool = True, 
                        max_wait: float = 60.0) -> Optional[str]:
        """
        Capture the assistant's response.
        
        Args:
            wait_for_completion: Wait for response to finish streaming
            max_wait: Maximum time to wait (seconds)
            
        Returns:
            The response text, or None if failed
        """
        pass
    
    def capture_response_html(self, wait_for_completion: bool = True,
                             max_wait: float = 60.0) -> Optional[str]:
        """
        Capture the assistant's response as HTML (optional - can be overridden).
        
        Args:
            wait_for_completion: Wait for response to finish streaming
            max_wait: Maximum time to wait (seconds)
            
        Returns:
            The response HTML, or None if not implemented/failed
        """
        # Default implementation: not supported
        return None
    
    def save_response_html(self, filepath: str, wait_for_completion: bool = True,
                          max_wait: float = 60.0) -> bool:
        """
        Save the assistant's response as an HTML file (optional - can be overridden).
        
        Args:
            filepath: Path where to save the HTML file
            wait_for_completion: Wait for response to finish streaming
            max_wait: Maximum time to wait (seconds)
            
        Returns:
            True if saved successfully, False otherwise
        """
        # Default implementation: not supported
        return False
    
    def save_response_text(self, filepath: str, wait_for_completion: bool = True,
                          max_wait: float = 60.0) -> bool:
        """
        Save the assistant's response as a plain text file (optional - can be overridden).
        
        Args:
            filepath: Path where to save the text file
            wait_for_completion: Wait for response to finish streaming
            max_wait: Maximum time to wait (seconds)
            
        Returns:
            True if saved successfully, False otherwise
        """
        # Default implementation: not supported
        return False
    
    def execute(self, query: str, capture: bool = True, 
               save_html: Optional[str] = None, save_text: Optional[str] = None,
               max_wait: float = 60.0) -> ConversionResult:
        """
        Execute a complete conversion: send query and capture response.
        
        Args:
            query: The question/prompt to send
            capture: Whether to capture the response
            save_html: Optional filepath to save HTML response
            save_text: Optional filepath to save text response
            max_wait: Maximum wait time for response (seconds)
            
        Returns:
            ConversionResult with query and response
        """
        print(f"[CONVERSION] Executing query...")
        print(f"[CONVERSION] Query: '{query}'")
        print(f"[CONVERSION] Capture response: {capture}")
        if save_html:
            print(f"[CONVERSION] Save HTML to: {save_html}")
        if save_text:
            print(f"[CONVERSION] Save text to: {save_text}")
        
        try:
            # Send the query
            send_success = self.send_query(query, submit=True)
            
            if not send_success:
                return ConversionResult(
                    success=False,
                    query=query,
                    error="Failed to send query"
                )
            
            print(f"[CONVERSION] ✓ Query sent successfully")
            
            # Capture response if requested
            response_text = None
            response_html = None
            html_filepath = None
            text_filepath = None
            
            if capture:
                print(f"[CONVERSION] Capturing response...")
                response_text = self.capture_response(
                    wait_for_completion=True,
                    max_wait=max_wait
                )
                
                if response_text:
                    print(f"[CONVERSION] ✓ Response captured ({len(response_text)} characters)")
                else:
                    print(f"[CONVERSION] ⚠ No response text captured")
            
            # Save HTML if requested
            if save_html:
                print(f"[CONVERSION] Saving HTML...")
                html_saved = self.save_response_html(
                    filepath=save_html,
                    wait_for_completion=True,
                    max_wait=max_wait
                )
                
                if html_saved:
                    html_filepath = save_html
                    print(f"[CONVERSION] ✓ HTML saved successfully")
                    
                    # Also capture the HTML content
                    response_html = self.capture_response_html(
                        wait_for_completion=False,  # Already waited
                        max_wait=5.0
                    )
                else:
                    print(f"[CONVERSION] ⚠ Failed to save HTML")
            
            # Save text if requested
            if save_text:
                print(f"[CONVERSION] Saving text...")
                text_saved = self.save_response_text(
                    filepath=save_text,
                    wait_for_completion=False if response_text else True,  # Skip wait if already captured
                    max_wait=max_wait
                )
                
                if text_saved:
                    text_filepath = save_text
                    print(f"[CONVERSION] ✓ Text saved successfully")
                else:
                    print(f"[CONVERSION] ⚠ Failed to save text")
            
            # Determine success
            success = send_success and (not capture or response_text is not None)
            
            return ConversionResult(
                success=success,
                query=query,
                response=response_text,
                response_html=response_html,
                html_filepath=html_filepath,
                text_filepath=text_filepath,
                error=None if success else "Failed to capture response"
            )
        
        except Exception as e:
            print(f"[CONVERSION ERROR] {e}")
            import traceback
            traceback.print_exc()
            return ConversionResult(
                success=False,
                query=query,
                error=str(e)
            )
