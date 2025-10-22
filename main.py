"""
Main Entry Point
================
Launches Comet browser and opens Perplexity Sidecar with optional query.

Workflow:
1. Browser facade launches Comet
2. Browser facade navigates to Sidecar URL
3. Pipeline sends query to Sidecar (if provided)
"""

import time
from pathlib import Path
from browser import BrowserFactory, BrowserType
from pipeline import PipelineConfig

# ==================== Configuration ====================
BROWSER_TYPE = BrowserType.COMET
SIDECAR_URL = "https://www.perplexity.ai/sidecar?copilot=true"

# Query configuration - Choose ONE mode:

# MODE 1: Single Query (simple mode - just type or send one question)
QUERY = None  # "What is Python?"  # Set to None to skip single query mode
SUBMIT_QUERY = True  # True to submit, False to just type
READ_RESPONSE = True  # True to read the assistant's response

# MODE 2: Conversation (multi-turn mode - full conversation with assistant)
CONVERSATION = [
    "What is Python?",
    "Can you give me a simple code example?",
    "How do I install it on Windows?"
]  # Set to None to disable conversation mode
# CONVERSATION = None  # Uncomment to disable conversation mode


def main():
    """
    Main function: Launch Comet, open Sidecar, and interact with assistant.
    
    Supports two modes:
    1. Single query: Send one question (with optional response reading)
    2. Conversation: Multi-turn conversation with the assistant
    """
    print("=" * 60)
    print("COMET BROWSER - PERPLEXITY SIDECAR ASSISTANT")
    print("=" * 60)
    print(f"Browser: {BROWSER_TYPE.value}")
    print(f"Target: {SIDECAR_URL}")
    
    if CONVERSATION:
        print(f"\n🔄 MODE: Conversation")
        print(f"Messages: {len(CONVERSATION)}")
        for i, msg in enumerate(CONVERSATION, 1):
            print(f"  {i}. {msg}")
    elif QUERY:
        print(f"\n💬 MODE: Single Query")
        print(f"Query: '{QUERY}'")
        print(f"Submit: {SUBMIT_QUERY}")
        print(f"Read Response: {READ_RESPONSE}")
    else:
        print(f"\n👁 MODE: Just open Sidecar (no interaction)")
    
    print("=" * 60)
    
    try:
        # Create browser facade (bundles launcher, navigator, pipeline)
        browser = BrowserFactory.create(BROWSER_TYPE)
        
        # Configure pipeline
        config = PipelineConfig(
            target_url=SIDECAR_URL,  # Browser will navigate here
            load_wait_time=5,
            keep_open=True,
            activate_features=False
        )
        
        # Run pipeline (Browser facade orchestrates everything)
        print(f"\n[INFO] Running Comet pipeline...")
        
        # Build pipeline kwargs based on mode
        pipeline_kwargs = {}
        
        if CONVERSATION:
            # Conversation mode
            pipeline_kwargs['conversation'] = CONVERSATION
            pipeline_kwargs['read_responses'] = True
        elif QUERY:
            # Single query mode
            pipeline_kwargs['query'] = QUERY
            pipeline_kwargs['submit'] = SUBMIT_QUERY
            pipeline_kwargs['read_responses'] = READ_RESPONSE
        
        # Run the pipeline
        result = browser.run_pipeline(config, **pipeline_kwargs)
        
        if not result.success:
            print(f"[ERROR] Pipeline failed: {result.message}")
            return False
        
        print(f"\n[SUCCESS] Pipeline completed!")
        print(f"[INFO] Steps: {', '.join(result.steps_completed)}")
        
        # Display conversation or response if available
        if 'conversation' in result.metadata:
            print(f"\n" + "=" * 60)
            print("CONVERSATION LOG")
            print("=" * 60)
            for turn in result.metadata['conversation']:
                role = "🧑 USER" if turn['role'] == 'user' else "🤖 ASSISTANT"
                content = turn['content']
                print(f"\n{role}:")
                print(f"{content[:500]}..." if len(content) > 500 else content)
        elif 'response' in result.metadata:
            print(f"\n" + "=" * 60)
            print("ASSISTANT RESPONSE")
            print("=" * 60)
            print(result.metadata['response'])
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Main execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
