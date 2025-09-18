# Large Scale Classification System GUI - Product Requirements Document

## Project Context

This document specifies a graphical user interface for a large-scale text classification system that handles 1000+ hierarchical categories. The system uses a two-stage approach:

1. **Narrowing Stage**: Reduces categories from 1000+ to ~3-10 candidates using embedding similarity, LLM reasoning, or hybrid approaches
2. **Selection Stage**: Uses LLM to select the final category from narrowed candidates

The system supports multiple narrowing strategies:
- **Embedding**: Pure vector similarity search
- **Hybrid**: Embedding narrowing (1000→10) followed by LLM refinement (10→3)
- **LLM**: Pure language model-based narrowing

Categories are hierarchical (e.g., `/Appliances/Refrigerators/French Door Refrigerators`) and the system is evaluated on 25 test cases with known ground truth labels.

## Overview

This GUI application provides engineers with an interactive tool to configure, test, and analyze the large-scale classification system. The primary goal is to help engineers understand how different strategies and hyperparameters affect classification accuracy and identify failure patterns in the multi-stage narrowing process.

**Current State**: Engineers analyze results by manually examining JSON files output from `tests/run_tests.py`
**Desired State**: Interactive visual tool for configuration, testing, and failure analysis

## Target Users

- **Primary**: ML Engineers tuning classification system parameters
- **Secondary**: Data Scientists analyzing system performance
- **Use Cases**: 
  - Hyperparameter optimization
  - Failure analysis and debugging
  - Strategy comparison and selection
  - Custom test case validation

## Application Structure

The application consists of three main sections:

### 1. Configuration Panel (Left Sidebar)
### 2. Test Case Analysis (Main Content Area)  
### 3. Custom Testing (Bottom Panel)

---

## Section 1: Configuration Panel

**Location**: Left sidebar, always visible
**Purpose**: Allow engineers to configure system parameters and trigger test runs

### Layout

```
┌─────────────────────────────────┐
│ ⚙️ CLASSIFICATION CONFIG        │
├─────────────────────────────────┤
│                                 │
│ Strategy                        │
│ [Dropdown: Embedding ▼]         │
│   • Embedding                   │
│   • Hybrid                      │
│                                 │
│ Max Narrowed Categories         │
│ [Slider: ●────────] 5           │
│ Range: 3-10                     │
│                                 │
│ ┌─ Hybrid Strategy Settings ──┐ │
│ │ Max Embedding Candidates    │ │
│ │ [Slider: ●────────] 10      │ │
│ │ Range: 5-20                 │ │
│ │                             │ │
│ │ Max Final Categories        │ │
│ │ [Slider: ●──────] 3         │ │
│ │ Range: 2-5                  │ │
│ └─────────────────────────────┘ │
│                                 │
│ Embedding Model                 │
│ [Dropdown: text-embedding... ▼] │
│                                 │
│ ┌─────────────────────────────┐ │
│ │ [🚀 Run Test Suite]         │ │
│ └─────────────────────────────┘ │
│                                 │
│ Last Run: 2025-09-17 21:45      │
│ Status: ✅ Complete (25/25)      │
└─────────────────────────────────┘
```

### Component Specifications

#### Strategy Dropdown
- **Options**: Embedding, Hybrid
- **Default**: Hybrid
- **Behavior**: When changed, dynamically show/hide relevant hyperparameter controls

#### Hyperparameter Controls
- **Max Narrowed Categories**: 
  - Range: 3-10, Default: 5
  - Tooltip: "Number of final candidates passed to selection stage"
- **Max Embedding Candidates** (Hybrid only):
  - Range: 5-20, Default: 10  
  - Tooltip: "Categories returned by embedding stage before LLM refinement"
- **Max Final Categories** (Hybrid only):
  - Range: 2-5, Default: 3
  - Tooltip: "Categories returned by LLM stage for final selection"

#### Run Test Suite Button
- **Behavior**: Executes test suite with current configuration
- **States**: Idle, Running (with progress), Complete, Error
- **Output**: Updates test results and enables analysis section

---

## Section 2: Test Case Analysis (Main Content)

**Location**: Main content area (center-right of screen)
**Purpose**: Detailed analysis of individual test case results

### Layout

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ 📊 TEST CASE ANALYSIS                                                           │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│ Test Case: [Dropdown: 1/25 - Samsung Counter-Depth Refrigerator... ▼]         │
│                                                                                 │
│ ┌─ Product Description ─────────────────────────────────────────────────────┐   │
│ │ "Samsung Counter-Depth 17.5-cu ft 3-Door Smart Compatible French Door    │   │
│ │  Refrigerator with Ice Maker (Fingerprint Resistant Matte Black Steel)"  │   │
│ └───────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│ 🎯 Ground Truth: /Appliances/Refrigerators/French Door Refrigerators           │
│                                                                                 │
│ ┌─ CLASSIFICATION FLOW ────────────────────────────────────────────────────┐   │
│ │                                                                          │   │
│ │     All Categories                 Narrowed Results           Final      │   │
│ │         (1000+)                      (Stage 1)            Selection     │   │
│ │                                                                          │   │
│ │    ┌─────────────┐                ┌─────────────┐        ┌───────────┐  │   │
│ │    │     ⚪⚪⚪     │   Embedding    │     🟢      │  LLM   │     🟢    │  │   │
│ │    │   ⚪⚪⚪⚪⚪   │ ───────────▶   │     🔵      │ ─────▶ │     🔵    │  │   │
│ │    │  ⚪⚪⚪⚪⚪⚪  │   Similarity   │     🟡      │ Select │     🟡    │  │   │
│ │    │   ⚪⚪⚪⚪⚪   │                │     🟡      │        │           │  │   │
│ │    │     ⚪⚪⚪     │                │     🟡      │        │           │  │   │
│ │    └─────────────┘                │     ...     │        │           │  │   │
│ │                                   └─────────────┘        └───────────┘  │   │
│ │                                                                          │   │
│ │    Legend:                                                               │   │
│ │    🟢 Correct Category (Ground Truth)                                    │   │
│ │    🔵 System Selected (Correct)                                          │   │
│ │    🟡 System Selected (Incorrect)                                        │   │
│ │    🔴 Correct Category (System Missed)                                   │   │
│ │    ⚪ Not Selected                                                        │   │
│ └──────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│ ┌─ STAGE BREAKDOWN ────────────────────────────────────────────────────────┐   │
│ │                                                                          │   │
│ │ Stage 1: Embedding Narrowing (1000+ → 10)                              │   │
│ │ ├─ 🟢 French Door Refrigerators    (similarity: 0.94) ✓                │   │
│ │ ├─ 🔵 Refrigerators                (similarity: 0.89)                   │   │
│ │ ├─ 🟡 Refrigerator Parts           (similarity: 0.76)                   │   │
│ │ ├─ 🟡 Freezer Parts                (similarity: 0.72)                   │   │
│ │ ├─ 🟡 Refrigerator Water Filters   (similarity: 0.68)                   │   │
│ │ └─ ... 5 more categories                                                 │   │
│ │                                                                          │   │
│ │ Stage 2: LLM Refinement (10 → 3)                                       │   │
│ │ ├─ 🟢 French Door Refrigerators    ← FINAL SELECTION ✅                │   │
│ │ ├─ 🔵 Refrigerators                                                     │   │
│ │ └─ 🟡 Ice Maker Kits                                                    │   │
│ │                                                                          │   │
│ │ ✅ Result: CORRECT                                                       │   │
│ │ ⏱️ Processing Time: 1,545ms (Embedding: 624ms, LLM: 921ms)             │   │
│ └──────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Hierarchical Tree View (Alternative/Additional Display)

```
┌─ CATEGORY HIERARCHY VIEW ──────────────────────────────────────────────────┐
│                                                                            │
│ 🌳 /Appliances                                                             │
│    ├─ 🟢 /Refrigerators ✓ (found by system)                               │
│    │  ├─ 🟢 /French Door Refrigerators ✅ TARGET (final selection)         │
│    │  ├─ ⚪ /Side-by-Side Refrigerators                                     │
│    │  └─ ⚪ /Top-Freezer Refrigerators                                      │
│    ├─ ⚪ /Dishwashers                                                       │
│    │  ├─ ⚪ /Built-In Dishwashers                                           │
│    │  └─ ⚪ /Portable Dishwashers                                           │
│    ├─ ⚪ /Garbage Disposals                                                 │
│    └─ 🟡 /Appliance Parts ⚠️ (incorrectly considered)                      │
│       ├─ 🟡 /Refrigerator Parts (stage 1)                                 │
│       ├─ 🟡 /Ice Maker Kits (stage 2)                                     │
│       ├─ 🟡 /Refrigerator Water Filters (stage 1)                         │
│       └─ 🟡 /Freezer Parts (stage 1)                                      │
│                                                                            │
│ 📊 Analysis:                                                               │
│ • System correctly identified product level (Appliances)                  │
│ • System correctly identified category level (Refrigerators)              │
│ • System correctly identified subcategory (French Door Refrigerators)     │
│ • False positives primarily from related parts categories                  │
└────────────────────────────────────────────────────────────────────────────┘
```

### Component Specifications

#### Test Case Selector
- **Type**: Dropdown with search
- **Format**: "1/25 - [First 50 chars of product description]..."
- **Behavior**: Auto-updates analysis when changed

#### Flow Diagram
- **Visual Style**: Sankey-like flow or fan-out diagram
- **Color Coding**: Consistent throughout application
- **Interactive**: Hover to see category details, click to highlight path

#### Stage Breakdown
- **Expandable sections** for each stage
- **Similarity scores** for embedding stage
- **Confidence scores** for LLM stage (if available)
- **Processing time breakdown**

---

## Section 3: Custom Testing Panel

**Location**: Bottom panel, collapsible
**Purpose**: Allow engineers to test arbitrary product descriptions

### Layout

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ 🧪 CUSTOM TEST CASE                                           [Collapse ▲]     │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│ Product Description:                                                            │
│ ┌─────────────────────────────────────────────────────────────────────────────┐ │
│ │ Enter a product description to classify...                                  │ │
│ │                                                                             │ │
│ │                                                                             │ │
│ └─────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│ Expected Category (Ground Truth):                                               │
│ [Hierarchical Dropdown: Select category... ▼]                                  │
│   Appliances >                                                                  │
│     Refrigerators >                                                             │
│       French Door Refrigerators                                                │
│                                                                                 │
│ ┌─────────────────────────────────────────────────────────────────────────────┐ │
│ │                    [🚀 Classify & Analyze]                                  │ │
│ └─────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│ [Results would display using the same visualization as Section 2]              │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Component Specifications

#### Product Description Input
- **Type**: Multi-line text area
- **Placeholder**: "Enter a product description to classify..."
- **Validation**: Minimum 10 characters

#### Category Selector
- **Type**: Hierarchical dropdown/tree selector
- **Behavior**: Expandable tree structure matching category hierarchy
- **Search**: Type-ahead search within categories

#### Classify Button
- **Behavior**: Runs classification with current config, displays results in same format as Section 2
- **States**: Enabled only when both fields have valid input

---

## Data Flow & Integration

### System Architecture Context

The GUI integrates with an existing Python classification system with the following structure:

```
src/
├── classification/
│   ├── pipeline.py           # Main ClassificationPipeline class
│   ├── narrowing.py          # Strategy implementations
│   └── selection.py          # Final LLM selection
├── config/settings.py        # Configuration parameters
└── data/models.py           # Category and result data models

tests/
├── run_tests.py             # Test execution script
└── results/                 # JSON output files
    ├── narrowing/           # Narrowing stage results
    └── selection/           # Selection stage results
```

### Data Flow Pseudocode

#### Configuration Changes
```python
def on_config_change(strategy, hyperparams):
    # Update settings.py with new parameters
    settings.narrowing_strategy = strategy
    settings.max_narrowed_categories = hyperparams.max_narrowed
    settings.max_embedding_candidates = hyperparams.max_embedding
    settings.max_final_categories = hyperparams.max_final
    
    # Enable run button
    ui.enable_run_button()

def on_run_test_suite():
    # Execute existing test runner
    subprocess.run(['python', 'tests/run_tests.py'])
    
    # Load new results
    results = load_latest_test_results()
    
    # Update UI
    ui.update_test_case_dropdown(results.test_cases)
    ui.show_run_complete_status()
```

#### Test Case Analysis
```python
def on_test_case_selected(test_case_id):
    # Load results for selected test case
    narrowing_result = load_narrowing_result(test_case_id)
    selection_result = load_selection_result(test_case_id)
    
    # Extract visualization data
    viz_data = {
        'ground_truth': test_case.category,
        'narrowed_categories': narrowing_result.narrowed_categories,
        'final_selection': selection_result.selected_category,
        'processing_times': {
            'narrowing': narrowing_result.processing_time_ms,
            'selection': selection_result.processing_time_ms
        }
    }
    
    # Render visualizations
    render_flow_diagram(viz_data)
    render_hierarchy_tree(viz_data)
    render_stage_breakdown(viz_data)

def categorize_for_visualization(category, ground_truth, narrowed_cats, final_selection):
    """Assign color coding for visualization"""
    if category == ground_truth:
        if category == final_selection:
            return "correct_selected"      # 🟢 Green
        elif category in narrowed_cats:
            return "correct_narrowed"      # 🔵 Blue  
        else:
            return "correct_missed"        # 🔴 Red
    else:
        if category == final_selection:
            return "incorrect_selected"    # 🟡 Yellow
        elif category in narrowed_cats:
            return "incorrect_narrowed"    # 🟡 Yellow
        else:
            return "not_considered"        # ⚪ Gray
```

#### Custom Testing
```python
def on_classify_custom():
    # Get user input
    text = ui.get_product_description()
    expected_category = ui.get_selected_category()
    
    # Run classification pipeline
    pipeline = ClassificationPipeline()
    result = pipeline.classify(text)
    
    # Create visualization data
    viz_data = {
        'ground_truth': expected_category,
        'narrowed_categories': result.candidates,
        'final_selection': result.category,
        'processing_times': {
            'total': result.processing_time_ms
        }
    }
    
    # Display results using same components
    render_flow_diagram(viz_data)
    render_hierarchy_tree(viz_data)
```

### Data Models

#### Expected JSON Structure (from existing test results)
```python
# narrowing_accuracy_YYYYMMDD_HHMMSS.json
{
    "test_info": {
        "test_type": "narrowing_accuracy",
        "timestamp": "2025-09-17T21:45:24.073582",
        "total_categories": 30,
        "max_narrowed_categories": 5,
        "total_test_cases": 25
    },
    "strategies": {
        "Embedding": {
            "strategy_name": "Embedding",
            "total_tests": 25,
            "correct_found": 24,
            "accuracy_percent": 96.0,
            "results": [
                {
                    "test_case": {
                        "text": "Samsung Counter-Depth 17.5-cu ft...",
                        "category": "/Appliances/Refrigerators/French Door Refrigerators"
                    },
                    "narrowed_categories": [...],
                    "correct_category_found": true,
                    "processing_time_ms": 624.64
                }
            ]
        }
    }
}

# selection_accuracy_YYYYMMDD_HHMMSS.json  
{
    "results": {
        "individual_results": [
            {
                "test_case": {...},
                "candidate_categories": [...],
                "selected_category": {...},
                "correct_selection": true,
                "processing_time_ms": 558.54
            }
        ]
    }
}
```

#### GUI Data Transformation
```python
def transform_test_results_for_ui(narrowing_results, selection_results):
    """Transform JSON results into UI-friendly format"""
    ui_data = []
    
    for i, (narrow_result, select_result) in enumerate(zip(narrowing_results, selection_results)):
        test_case_data = {
            'id': i,
            'description': narrow_result['test_case']['text'],
            'ground_truth': narrow_result['test_case']['category'],
            'stages': {
                'narrowing': {
                    'candidates': narrow_result['narrowed_categories'],
                    'correct_found': narrow_result['correct_category_found'],
                    'processing_time': narrow_result['processing_time_ms']
                },
                'selection': {
                    'final_choice': select_result['selected_category'],
                    'correct_selection': select_result['correct_selection'],
                    'processing_time': select_result['processing_time_ms']
                }
            }
        }
        ui_data.append(test_case_data)
    
    return ui_data
```

---

## Technical Requirements

### Framework
- **Primary Option**: Streamlit (faster development, good enough interactivity)
- **Advanced Option**: Solara (better animations, more interactive)

### Data Integration
- Load existing test results from `tests/results/` JSON files
- Interface with existing classification pipeline code
- Support real-time configuration changes and test execution

### Performance
- Lazy loading of test results
- Efficient rendering for large category sets
- Responsive design for different screen sizes

### Key Libraries
- **Visualization**: Plotly for interactive charts, graphviz for tree diagrams
- **UI Components**: Native framework components with custom styling
- **Data Processing**: Existing pandas/python data pipeline

### Implementation Pseudocode

#### Main Application Structure (Streamlit)
```python
import streamlit as st
import json
import subprocess
from pathlib import Path

def main():
    st.set_page_config(page_title="Classification System GUI", layout="wide")
    
    # Initialize session state
    if 'test_results' not in st.session_state:
        st.session_state.test_results = load_latest_results()
    
    # Layout
    with st.sidebar:
        render_config_panel()
    
    col1, col2 = st.columns([3, 1])
    with col1:
        render_analysis_section()
    
    with st.expander("🧪 Custom Test Case", expanded=False):
        render_custom_testing()

def render_config_panel():
    st.header("⚙️ Configuration")
    
    # Strategy selection
    strategy = st.selectbox("Strategy", ["embedding", "hybrid"])
    
    # Hyperparameters
    max_narrowed = st.slider("Max Narrowed Categories", 3, 10, 5)
    
    if strategy == "hybrid":
        max_embedding = st.slider("Max Embedding Candidates", 5, 20, 10)
        max_final = st.slider("Max Final Categories", 2, 5, 3)
    
    # Run button
    if st.button("🚀 Run Test Suite"):
        run_test_suite(strategy, max_narrowed, max_embedding, max_final)

def render_analysis_section():
    if not st.session_state.test_results:
        st.warning("No test results available. Run test suite first.")
        return
    
    # Test case selector
    test_cases = get_test_case_options()
    selected_case = st.selectbox("Test Case", test_cases)
    
    # Load and display results
    case_data = get_case_data(selected_case)
    
    # Flow visualization
    render_flow_diagram(case_data)
    
    # Stage breakdown
    render_stage_breakdown(case_data)
    
    # Hierarchy tree
    render_hierarchy_tree(case_data)

def render_flow_diagram(case_data):
    """Create Sankey-style flow diagram using Plotly"""
    import plotly.graph_objects as go
    
    # Create nodes and links for flow
    nodes = ["All Categories", "Narrowed", "Final Selection"]
    
    # Color code based on correctness
    colors = get_flow_colors(case_data)
    
    fig = go.Figure(data=[go.Sankey(
        node=dict(label=nodes, color=colors['nodes']),
        link=dict(source=[0,1], target=[1,2], color=colors['links'])
    )])
    
    st.plotly_chart(fig, use_container_width=True)

def render_hierarchy_tree(case_data):
    """Render expandable tree using Streamlit components"""
    ground_truth = case_data['ground_truth']
    narrowed_cats = case_data['narrowed_categories']
    final_selection = case_data['final_selection']
    
    # Parse hierarchy
    hierarchy = build_category_hierarchy()
    
    # Render tree with color coding
    for root_category in hierarchy:
        render_tree_node(root_category, ground_truth, narrowed_cats, final_selection)

def render_tree_node(node, ground_truth, narrowed_cats, final_selection, level=0):
    """Recursively render tree nodes with proper color coding"""
    color = categorize_for_visualization(node.path, ground_truth, narrowed_cats, final_selection)
    icon = get_status_icon(color)
    
    with st.expander(f"{icon} {node.name}", expanded=(level < 2)):
        if node.children:
            for child in node.children:
                render_tree_node(child, ground_truth, narrowed_cats, final_selection, level+1)
        else:
            st.write(f"Path: {node.path}")

def run_test_suite(strategy, max_narrowed, max_embedding=None, max_final=None):
    """Execute test suite with given configuration"""
    # Update configuration file
    update_config_file(strategy, max_narrowed, max_embedding, max_final)
    
    # Run tests
    with st.spinner("Running test suite..."):
        result = subprocess.run(['python', 'tests/run_tests.py'], 
                              capture_output=True, text=True)
    
    if result.returncode == 0:
        st.success("Test suite completed successfully!")
        # Reload results
        st.session_state.test_results = load_latest_results()
        st.experimental_rerun()
    else:
        st.error(f"Test suite failed: {result.stderr}")

def load_latest_results():
    """Load most recent test results from JSON files"""
    results_dir = Path("tests/results")
    
    # Find latest narrowing results
    narrowing_files = list((results_dir / "narrowing").glob("*.json"))
    selection_files = list((results_dir / "selection").glob("*.json"))
    
    if not narrowing_files or not selection_files:
        return None
    
    latest_narrowing = max(narrowing_files, key=lambda x: x.stat().st_mtime)
    latest_selection = max(selection_files, key=lambda x: x.stat().st_mtime)
    
    with open(latest_narrowing) as f:
        narrowing_data = json.load(f)
    
    with open(latest_selection) as f:
        selection_data = json.load(f)
    
    return transform_test_results_for_ui(narrowing_data, selection_data)

if __name__ == "__main__":
    main()
```

#### Alternative Implementation (Solara)
```python
import solara
import solara.lab
from typing import Dict, List, Optional

# Global state
config = solara.reactive({"strategy": "hybrid", "max_narrowed": 5})
test_results = solara.reactive(None)
selected_test_case = solara.reactive(0)

@solara.component
def App():
    with solara.AppLayout():
        with solara.Sidebar():
            ConfigPanel()
        
        MainContent()
        
        CustomTestingPanel()

@solara.component  
def ConfigPanel():
    strategy, set_strategy = solara.use_state("hybrid")
    max_narrowed, set_max_narrowed = solara.use_state(5)
    
    solara.Select("Strategy", values=["embedding", "hybrid"], 
                  value=strategy, on_value=set_strategy)
    
    solara.SliderInt("Max Narrowed Categories", value=max_narrowed, 
                     min=3, max=10, on_value=set_max_narrowed)
    
    if strategy == "hybrid":
        max_embedding, set_max_embedding = solara.use_state(10)
        max_final, set_max_final = solara.use_state(3)
        
        solara.SliderInt("Max Embedding Candidates", value=max_embedding,
                         min=5, max=20, on_value=set_max_embedding)
        
        solara.SliderInt("Max Final Categories", value=max_final,
                         min=2, max=5, on_value=set_max_final)
    
    def run_tests():
        # Execute test suite with current config
        execute_test_suite(strategy, max_narrowed)
        # Update results
        test_results.value = load_latest_results()
    
    solara.Button("🚀 Run Test Suite", on_click=run_tests)

@solara.component
def MainContent():
    if test_results.value is None:
        solara.Warning("No test results available. Run test suite first.")
        return
    
    # Test case selector
    test_case_options = [f"{i}: {case['description'][:50]}..." 
                        for i, case in enumerate(test_results.value)]
    
    solara.Select("Test Case", values=test_case_options, 
                  value=selected_test_case.value, 
                  on_value=selected_test_case.set)
    
    # Get current case data
    case_data = test_results.value[selected_test_case.value]
    
    # Visualizations
    FlowDiagram(case_data)
    StageBreakdown(case_data)  
    HierarchyTree(case_data)

@solara.component
def FlowDiagram(case_data: Dict):
    # Interactive flow visualization with animations
    # Could use custom Vue.js component for advanced interactions
    solara.HTML(f"""
    <div id="flow-diagram">
        <svg width="800" height="400">
            <!-- SVG flow diagram with color-coded paths -->
        </svg>
    </div>
    """)

@solara.component
def HierarchyTree(case_data: Dict):
    # Interactive tree component
    expanded_nodes, set_expanded = solara.use_state(set())
    
    hierarchy = build_category_hierarchy()
    
    for root in hierarchy:
        TreeNode(root, case_data, expanded_nodes, set_expanded)

@solara.component
def TreeNode(node, case_data, expanded_nodes, set_expanded):
    is_expanded = node.path in expanded_nodes
    color = categorize_for_visualization(node.path, case_data['ground_truth'], 
                                       case_data['narrowed_categories'], 
                                       case_data['final_selection'])
    icon = get_status_icon(color)
    
    def toggle_expand():
        new_expanded = expanded_nodes.copy()
        if is_expanded:
            new_expanded.discard(node.path)
        else:
            new_expanded.add(node.path)
        set_expanded(new_expanded)
    
    solara.Button(f"{icon} {node.name}", on_click=toggle_expand)
    
    if is_expanded and node.children:
        with solara.Column():
            for child in node.children:
                TreeNode(child, case_data, expanded_nodes, set_expanded)
```

---

## Success Metrics

### Engineer Productivity
- **Time to identify optimal hyperparameters**: Reduced from manual JSON analysis
- **Failure pattern recognition**: Visual patterns easier to spot than text logs
- **Configuration iteration speed**: Real-time feedback vs batch testing

### System Understanding
- **Strategy selection confidence**: Clear visual comparison of approaches
- **Failure root cause analysis**: Stage-by-stage breakdown shows where system fails
- **Category confusion patterns**: Hierarchical view reveals related-category mistakes

---

## Future Enhancements

### Phase 2 Features
- **Batch test comparison**: Compare results across multiple test runs
- **Performance trending**: Track accuracy/speed over time
- **Category confusion matrix**: Heatmap of commonly confused categories
- **Export functionality**: Save configurations and results

### Advanced Analytics
- **Embedding visualization**: 2D/3D plots of category embedding space
- **Similarity analysis**: Show why certain categories are confused
- **A/B testing framework**: Systematic comparison of configurations

### Helper Function Pseudocode

#### Utility Functions
```python
def build_category_hierarchy():
    """Build tree structure from flat category list"""
    hierarchy = {}
    
    # Load categories from data/categories.txt
    with open("data/categories.txt") as f:
        categories = [line.strip() for line in f if line.strip()]
    
    for category_path in categories:
        parts = category_path.strip('/').split('/')
        current = hierarchy
        
        for part in parts:
            if part not in current:
                current[part] = {'children': {}, 'path': category_path}
            current = current[part]['children']
    
    return hierarchy

def get_status_icon(color_category):
    """Return appropriate icon for visualization"""
    icons = {
        "correct_selected": "✅",      # Green - correct and selected
        "correct_narrowed": "🔵",      # Blue - correct and in narrowed set
        "correct_missed": "🔴",        # Red - correct but missed
        "incorrect_selected": "🟡",    # Yellow - incorrect but selected  
        "incorrect_narrowed": "🟡",    # Yellow - incorrect but in narrowed set
        "not_considered": "⚪"         # Gray - not considered
    }
    return icons.get(color_category, "⚪")

def update_config_file(strategy, max_narrowed, max_embedding=None, max_final=None):
    """Update settings.py with new configuration"""
    config_updates = {
        'narrowing_strategy': f'NarrowingStrategy.{strategy.upper()}',
        'max_narrowed_categories': max_narrowed,
    }
    
    if strategy == "hybrid" and max_embedding and max_final:
        config_updates.update({
            'max_embedding_candidates': max_embedding,
            'max_final_categories': max_final
        })
    
    # Read current settings file
    with open("src/config/settings.py", "r") as f:
        content = f.read()
    
    # Update relevant lines (simplified - would need proper parsing)
    for key, value in config_updates.items():
        # Replace lines matching pattern: key: type = old_value
        pattern = rf'({key}:\s*\w+\s*=\s*)[^#\n]+'
        replacement = rf'\g<1>{value}'
        content = re.sub(pattern, replacement, content)
    
    # Write updated settings
    with open("src/config/settings.py", "w") as f:
        f.write(content)

def get_flow_colors(case_data):
    """Generate colors for flow diagram based on results"""
    ground_truth = case_data['ground_truth']
    narrowed_cats = case_data['narrowed_categories']
    final_selection = case_data['final_selection']
    
    # Node colors
    node_colors = ["lightgray", "lightblue", "lightgreen"]
    
    # Link colors based on correctness
    link_colors = []
    
    # All categories -> Narrowed (green if correct category included)
    if ground_truth in [cat['path'] for cat in narrowed_cats]:
        link_colors.append("rgba(34, 197, 94, 0.6)")  # Green
    else:
        link_colors.append("rgba(239, 68, 68, 0.6)")  # Red
    
    # Narrowed -> Final (green if final selection is correct)
    if final_selection['path'] == ground_truth:
        link_colors.append("rgba(34, 197, 94, 0.6)")  # Green
    else:
        link_colors.append("rgba(234, 179, 8, 0.6)")  # Yellow
    
    return {
        'nodes': node_colors,
        'links': link_colors
    }

def execute_test_suite(strategy, max_narrowed, max_embedding=None, max_final=None):
    """Execute the test suite with given parameters"""
    # Update configuration
    update_config_file(strategy, max_narrowed, max_embedding, max_final)
    
    # Run the test suite
    import subprocess
    import os
    
    # Change to project directory
    os.chdir("level-3-code/large_scale_classification")
    
    # Execute test runner
    result = subprocess.run(
        ['python', 'tests/run_tests.py', '--narrowing-accuracy', '--selection-accuracy'],
        capture_output=True,
        text=True,
        timeout=300  # 5 minute timeout
    )
    
    return result.returncode == 0, result.stdout, result.stderr

class CategoryNode:
    """Data structure for category hierarchy"""
    def __init__(self, name: str, path: str, parent=None):
        self.name = name
        self.path = path
        self.parent = parent
        self.children = []
    
    def add_child(self, child_node):
        child_node.parent = self
        self.children.append(child_node)
    
    def is_leaf(self):
        return len(self.children) == 0
    
    def get_level(self):
        level = 0
        current = self.parent
        while current:
            level += 1
            current = current.parent
        return level
```

---

## Implementation Notes

### Color Coding Standard
- 🟢 **Green (#22C55E)**: Correct/Ground truth
- 🔵 **Blue (#3B82F6)**: System selected (correct)
- 🟡 **Yellow (#EAB308)**: System selected (incorrect)
- 🔴 **Red (#EF4444)**: System missed (should have selected)
- ⚪ **Gray (#9CA3AF)**: Not considered/neutral

### Responsive Design
- **Minimum width**: 1200px (complex data visualization)
- **Sidebar**: Fixed 300px width
- **Main content**: Flexible width
- **Custom panel**: Collapsible to maximize analysis space

### Error Handling
- **Invalid configurations**: Prevent impossible parameter combinations
- **Test execution failures**: Clear error messages and fallback behavior
- **Missing data**: Graceful degradation when results incomplete
