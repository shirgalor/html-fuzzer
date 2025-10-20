# Architecture Decision: Browser as Facade

## Question
Should Browser be:
1. **Browser → Pipeline → Navigator/Launcher** (hierarchy)?
2. **Browser → All components** (facade)?

## Answer: Option 2 - Browser as Facade ✅

## Why Facade Pattern?

### Browser owns all 3 components as SIBLINGS, not in hierarchy

```
                    Browser (Facade)
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
    Launcher         Navigator        Pipeline
    (Layer 1)        (Layer 2)        (Layer 3)
        ↑                ↑                │
        └────────────────┴────────────────┘
              Pipeline USES Launcher + Navigator
```

## Benefits of Facade Pattern

### 1. Flexibility
```python
# Can use any component independently
browser.launch()              # Just launcher
browser.navigate_to(url)      # Just navigator
browser.run_pipeline(config)  # Complete workflow
```

### 2. No Mandatory Hierarchy
```python
# Pipeline is OPTIONAL, not required
browser = BrowserFactory.create(BrowserType.COMET)

# Option A: Skip pipeline, use components directly
browser.launch()
browser.navigate_to("https://example.com")

# Option B: Use pipeline for complete workflow
config = PipelineConfig(target_url="https://example.com")
browser.run_pipeline(config)
```

### 3. Clear Responsibilities

```python
class BaseBrowser:
    # Owns all components as siblings
    _launcher: BrowserLauncher    # Independent
    _navigator: Navigator         # Independent
    _pipeline: Pipeline           # Uses launcher + navigator
    
    # Provides access to each
    def launch(self):
        """Direct access to launcher."""
        self._launcher.launch_and_attach()
    
    def navigate_to(self, url):
        """Direct access to navigator."""
        self._navigator.navigate_to_url(url)
    
    def run_pipeline(self, config):
        """Orchestrated workflow using all components."""
        self._pipeline.run()  # Pipeline uses launcher + navigator internally
```

## Component Relationships

### Independent Components (Siblings)
- **Launcher**: Can work alone - just launches browser
- **Navigator**: Can work alone - just navigates (needs existing driver)

### Composite Component
- **Pipeline**: Orchestrates Launcher + Navigator for complete workflows

### Browser Role
- **Facade**: Provides simple interface to all components
- **Factory**: Creates appropriate components for browser type
- **Owner**: Manages lifecycle of all components

## Visual Comparison

### ❌ Wrong: Hierarchy (Browser → Pipeline → Others)
```
Browser
  ↓
Pipeline (required)
  ↓
Navigator + Launcher
```
Problems:
- Can't use Navigator without Pipeline
- Can't use Launcher without Pipeline
- Pipeline becomes mandatory
- Less flexible

### ✅ Correct: Facade (Browser → All as siblings)
```
Browser
  ├─→ Launcher
  ├─→ Navigator
  └─→ Pipeline → uses Launcher + Navigator
```
Benefits:
- Can use any component independently
- Pipeline is optional
- More flexible
- Clear separation of concerns

## Real-World Usage

### Use Case 1: Just Launch
```python
browser = BrowserFactory.create(BrowserType.COMET)
browser.launch()
# Direct launcher access, no pipeline needed
```

### Use Case 2: Launch + Navigate
```python
browser = BrowserFactory.create(BrowserType.COMET)
browser.launch()
browser.navigate_to("https://example.com")
# Direct launcher + navigator access, no pipeline needed
```

### Use Case 3: Complete Workflow
```python
browser = BrowserFactory.create(BrowserType.COMET)
config = PipelineConfig(target_url="https://example.com")
browser.run_pipeline(config)
# Pipeline orchestrates launcher + navigator + browser-specific steps
```

## Code Structure

```python
class CometBrowser(BaseBrowser):
    """
    Facade that provides access to all Comet components.
    All components are siblings, not hierarchical.
    """
    
    def __init__(self):
        self._launcher = None    # Layer 1 - Independent
        self._navigator = None   # Layer 2 - Independent
        self._pipeline = None    # Layer 3 - Uses L1 + L2
    
    # Factory methods create independent components
    def create_launcher(self):
        return BrowserFactory.create(BrowserType.COMET)
    
    def create_navigator(self, driver):
        return NavigatorFactory.create(NavigatorType.COMET, driver)
    
    def create_pipeline(self, config):
        # Pipeline uses launcher + navigator
        launcher = self.create_launcher()
        nav_factory = lambda d: self.create_navigator(d)
        return PipelineFactory.create(
            PipelineType.COMET,
            browser_launcher=launcher,
            navigator_factory=nav_factory,
            config=config
        )
    
    # Direct access methods (no pipeline needed)
    def launch(self):
        """Use launcher directly."""
        if not self._launcher:
            self._launcher = self.create_launcher()
        self._driver = self._launcher.launch_and_attach()
        self._navigator = self.create_navigator(self._driver)
    
    def navigate_to(self, url):
        """Use navigator directly."""
        return self._navigator.navigate_to_url(url)
    
    # Orchestrated access (uses pipeline)
    def run_pipeline(self, config):
        """Use pipeline which orchestrates launcher + navigator."""
        self._pipeline = self.create_pipeline(config)
        return self._pipeline.run()
```

## Summary

**Browser is a FACADE, not a hierarchy:**
- ✅ Owns Launcher, Navigator, Pipeline as **siblings**
- ✅ Provides **direct access** to each component
- ✅ Pipeline is **optional** - uses Launcher + Navigator when needed
- ✅ Maximum **flexibility** - use any combination of components
- ✅ Clear **separation of concerns**

**The Pattern:**
```
Application
    ↓
Browser (FACADE)
    ↓
├── Launcher  ──┐
├── Navigator ──┼── Used independently OR
└── Pipeline ───┘   Used together via Pipeline
```

This is the **correct architecture** and what the code currently implements! 🎉
