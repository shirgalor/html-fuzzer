# In run_agent.py (or agent_task.py)

import time
import sys
from launch import main as launch_comet 

from browser_use import Agent, Browser, ChatBrowserUse 

cdp_connect_url = "http://127.0.0.1:9222"


def run_agent_on_comet(task_description: str):
    print("--- Step 1: Launching Comet with remote debugging... ---")
    
    # Call your launcher script's main function to get the DevTools URL
    devtools_websocket_url = launch_comet() 
    
    if not devtools_websocket_url:
        print("Failed to get DevTools URL. Exiting.")
        sys.exit(1)

    print(f"Comet is running. DevTools URL: {devtools_websocket_url}")

    # --- Step 2: Initialize browser-use to connect to the running Comet ---
    
    try:
        browser = Browser(
            use_cloud=False, 
            cdp_url=cdp_connect_url   
        )
        print("im in")

        agent = Agent(
            task=task_description,
            llm=ChatBrowserUse(), # Use the default LLM (requires API key)
            browser=browser       # Pass the connected browser instance
        )
        
        print("\n--- Step 3: Running AI Agent Task on Comet ---")
        result = agent.run_sync()
        
        print("\n🎉 Agent Task Complete!")
        print("Output:", result.output)
        
    except Exception as e:
        print(f"\n[!] Error during browser-use execution: {e}")
        # Add cleanup here to close the Comet process if needed
        # ...

if __name__ == "__main__":
    task = "Go to the Perplexity search bar, type 'What is the capital of France?', and return the final answer provided by Perplexity."
    run_agent_on_comet(task)