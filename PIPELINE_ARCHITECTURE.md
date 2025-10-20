# Pipeline Architecture

## Overview

The pipeline module provides browser-specific automation workflows using abstract base classes and factory pattern. Each browser type can have its own customized pipeline with different pre/post navigation steps.

## Architecture

```
pipeline/
├── __init__.py           # Public API exports
├── base.py              # BasePipeline abstract class
├── comet_pipeline.py    # CometPipeline implementation
└── factory.py           # PipelineFactory for creating pipelines
```

## Design Pattern

### 1. Abstract Base Class (BasePipeline)

Defines the workflow template:
```python
class BasePipeline(ABC):
    def run() -> PipelineResult:
        1. setup_browser()
        2. pre_navigation_steps()    # Browser-specific
        3. navigate_to_target()
        4. post_navigation_steps()   # Browser-specific
        5. cleanup()
```

### 2. Concrete Implementation (CometPipeline)

```python
class CometPipeline(BasePipeline):
    def pre_navigation_steps():
        # Open Perplexity Sidecar
        
    def post_navigation_steps():
        # Activate Assistant button
```

### 3. Factory Pattern

```python
PipelineFactory.create(
    PipelineType.COMET,
    browser_launcher=launcher,
    navigator_factory=nav_factory,
    config=config
)
```

## Why This Architecture?

### Problem with Old Design
```python
# Old pipeline.py had scattered if/else logic:
if browser_type == BrowserType.COMET:
    # Open Sidecar
    ...
if browser_type == BrowserType.COMET:
    # Activate Assistant
    ...
```

**Issues:**
- Violates Open/Closed Principle
- Every new browser adds more `if/elif` statements
- Browser-specific logic mixed with general pipeline
- Hard to test individual browsers
- Difficult to customize workflows per browser

### New Design Benefits

✅ **Separation of Concerns**: Each browser has its own pipeline class
✅ **Open/Closed Principle**: Add new browsers without modifying existing code
✅ **Clear Responsibilities**: Browser-specific logic stays in browser-specific classes
✅ **Easy Testing**: Test each pipeline independently
✅ **Consistent Pattern**: Follows same architecture as `browser_launcher` and `navigator`

## Usage

### Basic Usage

```python
from pipeline import PipelineFactory, PipelineType, PipelineConfig
from browser_launcher import BrowserFactory, BrowserType
from navigator import NavigatorFactory, NavigatorType

# Create dependencies
browser_launcher = BrowserFactory.create(BrowserType.COMET)
navigator_factory = lambda driver: NavigatorFactory.create(NavigatorType.COMET, driver)

# Configure pipeline
config = PipelineConfig(
    target_url="https://example.com",
    load_wait_time=5,
    stability_wait_time=2,
    keep_open=True,
    activate_features=True
)

# Create and run pipeline
pipeline = PipelineFactory.create(
    PipelineType.COMET,
    browser_launcher=browser_launcher,
    navigator_factory=navigator_factory,
    config=config
)

result = pipeline.run()

if result.success:
    print("Pipeline completed!")
    print(f"Steps: {result.steps_completed}")
```

### Advanced Usage - Multiple HTML Files

```python
# Use pipeline for first file
config = PipelineConfig(
    target_url=first_html.as_uri(),
    keep_open=True
)

pipeline = PipelineFactory.create(PipelineType.COMET, launcher, nav_factory, config)
result = pipeline.run()

# Get driver from result and open more files
driver = result.driver
navigator = NavigatorFactory.create(NavigatorType.COMET, driver)

for html_file in remaining_files:
    navigator.navigate_to_url(html_file.as_uri())
```

## Adding New Browsers

To add support for a new browser (e.g., Chrome):

### Step 1: Add to PipelineType Enum

```python
# pipeline/factory.py
class PipelineType(Enum):
    COMET = "comet"
    CHROME = "chrome"  # New!
```

### Step 2: Create Pipeline Class

```python
# pipeline/chrome_pipeline.py
from .base import BasePipeline

class ChromePipeline(BasePipeline):
    def get_browser_name(self) -> str:
        return "Chrome"
    
    def pre_navigation_steps(self) -> bool:
        # Chrome-specific pre-navigation
        # E.g., load extensions
        print("[INFO] Loading Chrome extensions...")
        return True
    
    def post_navigation_steps(self) -> bool:
        # Chrome-specific post-navigation
        # E.g., inject scripts
        print("[INFO] Injecting content scripts...")
        return True
    
    def print_success_summary(self):
        print("CHROME PIPELINE COMPLETED!")
        for step in self._steps_completed:
            print(f"✓ {step}")
```

### Step 3: Register in Factory

```python
# pipeline/factory.py
from .chrome_pipeline import ChromePipeline

_PIPELINE_CLASSES = {
    PipelineType.COMET: CometPipeline,
    PipelineType.CHROME: ChromePipeline,  # New!
}
```

### Step 4: Update Exports

```python
# pipeline/__init__.py
from .chrome_pipeline import ChromePipeline

__all__ = [
    "BasePipeline",
    "CometPipeline",
    "ChromePipeline",  # New!
    "PipelineFactory",
    "PipelineType",
]
```

That's it! No need to modify existing code.

## Pipeline Workflow Details

### Comet Pipeline Workflow

```
1. Setup Browser
   - Launch Comet browser
   - Create navigator

2. Pre-Navigation (Comet-specific)
   - Navigate to https://www.perplexity.ai/sidecar?copilot=true
   - Wait 3 seconds for Sidecar to load
   - Additional 2 second stability wait

3. Navigate to Target
   - Navigate to user-specified URL
   - Wait configured load_wait_time
   - Verify navigation success

4. Post-Navigation (Comet-specific)
   - Wait stability_wait_time for UI
   - Click Assistant button using PyAutoGUI
   - Report success/failure

5. Cleanup (optional)
   - Close browser if not keep_open
   - Handle user input
```

### Future Browser Examples

**Chrome Pipeline** might:
- Pre-navigation: Load extensions, set preferences
- Post-navigation: Inject content scripts, run automation

**Firefox Pipeline** might:
- Pre-navigation: Configure DevTools, enable features
- Post-navigation: Attach debugger, run Marionette commands

## Configuration Options

```python
@dataclass
class PipelineConfig:
    target_url: str                  # URL to navigate to
    load_wait_time: int = 5          # Wait after navigation
    stability_wait_time: int = 2     # Wait before post-nav steps
    keep_open: bool = False          # Keep browser open after completion
    activate_features: bool = True   # Run post-navigation features
```

## Error Handling

Pipelines return structured results:

```python
@dataclass
class PipelineResult:
    success: bool
    message: str
    driver: Optional[WebDriver]
    steps_completed: list[str]
```

**Graceful Degradation:**
- Pre-navigation failures don't stop the pipeline (e.g., Sidecar load failure)
- Post-navigation failures are warnings (e.g., Assistant activation failure)
- Critical failures (browser launch, main navigation) stop the pipeline

## Comparison with Other Modules

All three modules follow the same pattern:

| Module | Abstract Base | Concrete Impl | Factory | Enum |
|--------|--------------|---------------|---------|------|
| `browser_launcher` | BrowserLauncher | CometBrowserLauncher | BrowserFactory | BrowserType |
| `navigator` | Navigator | CometNavigator | NavigatorFactory | NavigatorType |
| `pipeline` | BasePipeline | CometPipeline | PipelineFactory | PipelineType |

**Consistent 3-Step Extension Pattern:**
1. Add to enum
2. Create class implementing abstract base
3. Register in factory

This makes the codebase easy to understand and extend!

## Testing

Each pipeline can be tested independently:

```python
def test_comet_pipeline():
    # Mock dependencies
    mock_launcher = Mock(spec=BrowserLauncher)
    mock_nav_factory = Mock()
    
    config = PipelineConfig(target_url="https://test.com")
    
    pipeline = CometPipeline(mock_launcher, mock_nav_factory, config)
    result = pipeline.run()
    
    assert result.success
    assert "Sidecar" in str(result.steps_completed)
```

## Future Enhancements

Potential additions:
- **Pipeline chaining**: Run multiple pipelines in sequence
- **Pipeline hooks**: Add custom callbacks at any step
- **Pipeline templates**: Pre-configured pipelines for common tasks
- **Parallel pipelines**: Run multiple browsers simultaneously
- **Pipeline recording**: Save and replay workflows
