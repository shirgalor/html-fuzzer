"""
Comet Pipeline
==============
Pipeline implementation for Perplexity Comet browser.

Workflow (after Browser facade has launched and navigated to Sidecar):
1. Pre-workflow: Verify Sidecar loaded correctly
2. Execute workflow: Send query to Sidecar input (if query provided)
3. Post-workflow: Wait for response (if query submitted)
"""

import time
from typing import Optional

# Import from parent package's pipeline
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from pipeline.base import BasePipeline, PipelineConfig, PipelineResult


class CometPipeline(BasePipeline):
    """
    Pipeline implementation for Comet browser.
    
    Browser facade has already:
    - Launched Comet
    - Navigated to Perplexity Sidecar
    
    Pipeline workflow:
    - Verify Sidecar loaded
    - Optionally send query to Sidecar input field
    """
    
    def __init__(self, driver, navigator, config, **kwargs):
        """
        Initialize Comet pipeline.
        
        Args:
            driver: Selenium WebDriver (already attached to Comet)
            navigator: CometNavigator instance (already created)
            config: Pipeline configuration
            **kwargs: Optional parameters (query, submit, conversation, read_responses)
        """
        super().__init__(driver, navigator, config, **kwargs)
        
        # Extract optional query parameters
        self.query: Optional[str] = kwargs.get('query', None)
        self.submit_query: bool = kwargs.get('submit', False)
        
        # New conversation mode parameters
        self.conversation: Optional[list] = kwargs.get('conversation', None)
        self.read_responses: bool = kwargs.get('read_responses', True)
    
    def get_browser_name(self) -> str:
        """Return the browser name."""
        return "Comet"
    
    def pre_workflow_steps(self) -> bool:
        """
        Pre-workflow: Navigate to Sidecar and verify it loaded.
        
        Returns:
            True if successful
        """
        print(f"[COMET] Navigating to Sidecar...")
        
        # Navigate to Sidecar URL
        SIDECAR_URL = "https://www.perplexity.ai/sidecar?copilot=true"
        nav_result = self.navigator.navigate_to_url(SIDECAR_URL, wait_time=3)
        
        if not nav_result.success:
            print(f"[COMET] ✗ Failed to navigate to Sidecar: {nav_result.message}")
            return False
        
        print(f"[COMET] Verifying Sidecar loaded...")
        current_url = self.navigator.get_current_url()
        print(f"[COMET] Current URL: {current_url}")
        
        if "sidecar" in current_url.lower():
            print(f"[COMET] ✓ Sidecar page confirmed")
            return True
        else:
            print(f"[COMET] ⚠ Warning: Not on Sidecar page, continuing anyway...")
            return True
    
    def execute_workflow(self) -> bool:
        """
        Execute workflow: Send query/conversation to Sidecar if provided.
        
        Supports two modes:
        1. Single query mode: Send one query (with optional response reading)
        2. Conversation mode: Multi-turn conversation with the assistant
        
        Returns:
            True if successful (or no query provided)
        """
        # Mode 1: Conversation mode (takes priority)
        if self.conversation:
            print(f"[COMET] === CONVERSATION MODE ===")
            print(f"[COMET] Messages to send: {len(self.conversation)}")
            print(f"[COMET] Read responses: {self.read_responses}")
            
            conversation_log = self.navigator.have_conversation(
                messages=self.conversation,
                read_responses=self.read_responses,
                wait_between_messages=2.0
            )
            
            # Store conversation in result for later retrieval
            self.result.metadata['conversation'] = conversation_log
            
            print(f"[COMET] ✓ Conversation completed")
            print(f"[COMET] Total turns: {len(conversation_log)}")
            return True
        
        # Mode 2: Single query mode
        if not self.query:
            print(f"[COMET] No query or conversation provided, skipping")
            return True
        
        print(f"[COMET] === SINGLE QUERY MODE ===")
        print(f"[COMET] Query: '{self.query}'")
        print(f"[COMET] Submit: {self.submit_query}")
        print(f"[COMET] Read response: {self.read_responses}")
        
        # Send query
        success = self.navigator.send_query_to_sidecar(
            query=self.query,
            submit=self.submit_query
        )
        
        if not success:
            print(f"[COMET] ✗ Failed to send query")
            return False
        
        print(f"[COMET] ✓ Query sent successfully")
        
        # Read response if requested and query was submitted
        if self.submit_query and self.read_responses:
            print(f"[COMET] Reading assistant response...")
            
            # Wait for streaming to complete
            self.navigator.wait_for_response_streaming(timeout=60.0)
            
            # Read the response
            response = self.navigator.read_assistant_response(
                wait_for_completion=True,
                max_wait=60.0
            )
            
            if response:
                print(f"[COMET] ✓ Got response")
                # Store in result metadata
                self.result.metadata['response'] = response
            else:
                print(f"[COMET] ⚠ Could not read response")
        
        return True
    
    def post_workflow_steps(self) -> bool:
        """
        Post-workflow: Wait for response if query was submitted.
        
        Returns:
            True (always succeeds)
        """
        print(f"[COMET] Workflow complete!")
        
        if self.query and self.submit_query:
            print(f"[COMET] Waiting for Perplexity response...")
            time.sleep(3)  # Wait for response to start loading
        
        return True
