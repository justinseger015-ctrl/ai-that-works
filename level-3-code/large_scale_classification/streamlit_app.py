"""Streamlit GUI for Large Scale Classification System.

This application provides an interactive interface for testing and analyzing
different narrowing strategies and settings for the classification system.
"""

import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

# Add the src directory to Python path
import sys
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from src.classification.pipeline import ClassificationPipeline
from src.config.settings import settings
from src.data.category_loader import CategoryLoader
from src.shared.enums import NarrowingStrategy


# Page configuration
st.set_page_config(
    page_title="Classification System GUI",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-metric {
        border-left-color: #2ca02c;
    }
    .error-metric {
        border-left-color: #d62728;
    }
    .warning-metric {
        border-left-color: #ff7f0e;
    }
    .stage-header {
        font-size: 1.2em;
        font-weight: bold;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .category-item {
        padding: 0.25rem;
        margin: 0.1rem 0;
        border-radius: 0.25rem;
    }
    .correct-selected {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
    }
    .correct-narrowed {
        background-color: #cce5ff;
        border: 1px solid #99d6ff;
    }
    .incorrect-selected {
        background-color: #fff3cd;
        border: 1px solid #ffecb3;
    }
    .correct-missed {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)


def load_latest_results() -> Optional[Dict[str, Any]]:
    """Load the most recent test results from JSON files."""
    results_dir = Path("tests/results")
    
    if not results_dir.exists():
        return None
    
    # Find latest narrowing and selection results
    narrowing_files = list((results_dir / "narrowing").glob("*.json"))
    selection_files = list((results_dir / "selection").glob("*.json"))
    
    if not narrowing_files or not selection_files:
        return None
    
    latest_narrowing = max(narrowing_files, key=lambda x: x.stat().st_mtime)
    latest_selection = max(selection_files, key=lambda x: x.stat().st_mtime)
    
    try:
        with open(latest_narrowing) as f:
            narrowing_data = json.load(f)
        
        with open(latest_selection) as f:
            selection_data = json.load(f)
        
        return {
            'narrowing': narrowing_data,
            'selection': selection_data,
            'timestamp': narrowing_data['test_info']['timestamp']
        }
    except Exception as e:
        st.error(f"Error loading test results: {e}")
        return None


def transform_results_for_ui(results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Transform JSON results into UI-friendly format."""
    if not results:
        return []
    
    narrowing_data = results['narrowing']
    selection_data = results['selection']
    
    ui_data = []
    
    # Get results from the first strategy (assuming only one strategy per test run)
    strategy_key = list(narrowing_data['strategies'].keys())[0]
    narrowing_results = narrowing_data['strategies'][strategy_key]['results']
    selection_results = selection_data['results']['individual_results']
    
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
                    'candidates': select_result['candidate_categories'],
                    'final_choice': select_result['selected_category'],
                    'correct_selection': select_result['correct_selection'],
                    'processing_time': select_result['processing_time_ms']
                }
            }
        }
        ui_data.append(test_case_data)
    
    return ui_data


def get_status_icon(category_path: str, ground_truth: str, narrowed_cats: List[Dict], final_selection: Dict) -> str:
    """Get appropriate status icon for a category."""
    narrowed_paths = [cat['path'] for cat in narrowed_cats]
    final_path = final_selection['path'] if final_selection else None
    
    if category_path == ground_truth:
        if category_path == final_path:
            return "✅"  # Correct and selected
        elif category_path in narrowed_paths:
            return "🔵"  # Correct and narrowed
        else:
            return "🔴"  # Correct but missed
    else:
        if category_path == final_path:
            return "🟡"  # Incorrect but selected
        elif category_path in narrowed_paths:
            return "🟡"  # Incorrect but narrowed
        else:
            return "⚪"  # Not considered


def render_config_panel():
    """Render the configuration panel in the sidebar."""
    st.sidebar.header("⚙️ Classification Config")
    
    # Strategy selection
    strategy_options = ["embedding", "hybrid"]
    current_strategy = settings.narrowing_strategy.value
    strategy = st.sidebar.selectbox(
        "Strategy",
        strategy_options,
        index=strategy_options.index(current_strategy),
        help="Choose the narrowing strategy for classification"
    )
    
    # Max narrowed categories
    max_narrowed = st.sidebar.slider(
        "Max Narrowed Categories",
        min_value=3,
        max_value=10,
        value=settings.max_narrowed_categories,
        help="Number of final candidates passed to selection stage"
    )
    
    # Hybrid-specific settings
    max_embedding = settings.max_embedding_candidates
    max_final = settings.max_final_categories
    
    if strategy == "hybrid":
        st.sidebar.markdown("**Hybrid Strategy Settings**")
        max_embedding = st.sidebar.slider(
            "Max Embedding Candidates",
            min_value=5,
            max_value=20,
            value=settings.max_embedding_candidates,
            help="Categories returned by embedding stage before LLM refinement"
        )
        max_final = st.sidebar.slider(
            "Max Final Categories",
            min_value=2,
            max_value=5,
            value=settings.max_final_categories,
            help="Categories returned by LLM stage for final selection"
        )
    
    # Embedding model
    st.sidebar.selectbox(
        "Embedding Model",
        ["text-embedding-3-small"],
        disabled=True,
        help="Embedding model (currently fixed)"
    )
    
    st.sidebar.markdown("---")
    
    # Run test suite button
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("🚀 Run Full Suite", type="primary"):
            run_test_suite(strategy, max_narrowed, max_embedding, max_final)
    with col2:
        if st.button("🔬 Run Sample", help="Run just 5 test cases to check API connectivity"):
            run_sample_tests(strategy, max_narrowed, max_embedding, max_final)
    
    # Display last run info
    if 'test_results' in st.session_state and st.session_state.test_results:
        timestamp = st.session_state.test_results.get('timestamp', 'Unknown')
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            formatted_time = dt.strftime("%Y-%m-%d %H:%M")
        except:
            formatted_time = timestamp
        
        st.sidebar.markdown(f"**Last Run:** {formatted_time}")
        
        # Show basic stats
        narrowing_data = st.session_state.test_results.get('narrowing', {})
        selection_data = st.session_state.test_results.get('selection', {})
        
        if narrowing_data and selection_data:
            strategy_key = list(narrowing_data['strategies'].keys())[0]
            narrowing_accuracy = narrowing_data['strategies'][strategy_key]['accuracy_percent']
            selection_accuracy = selection_data['results']['accuracy_percent']
            
            st.sidebar.markdown(f"**Status:** ✅ Complete")
            st.sidebar.markdown(f"**Narrowing Accuracy:** {narrowing_accuracy:.1f}%")
            st.sidebar.markdown(f"**Selection Accuracy:** {selection_accuracy:.1f}%")


def run_test_suite(strategy: str, max_narrowed: int, max_embedding: int, max_final: int):
    """Execute the test suite with given configuration."""
    # Update configuration
    update_config_file(strategy, max_narrowed, max_embedding, max_final)
    
    # Show progress
    progress_bar = st.sidebar.progress(0)
    status_text = st.sidebar.empty()
    
    try:
        status_text.text("Running test suite...")
        progress_bar.progress(25)
        
        # Run the test suite with extended timeout
        result = subprocess.run(
            ['python', 'tests/run_tests.py', '--all'],
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout for API calls
            cwd=project_root
        )
        
        progress_bar.progress(75)
        
        if result.returncode == 0:
            progress_bar.progress(100)
            status_text.text("✅ Test suite completed!")
            
            # Reload results
            time.sleep(1)  # Give files time to be written
            st.session_state.test_results = load_latest_results()
            st.rerun()
        else:
            status_text.text("❌ Test suite failed")
            error_msg = result.stderr
            
            # Check for common API issues and provide helpful messages
            if "ConnectTimeout" in error_msg or "APITimeoutError" in error_msg:
                st.sidebar.error("🌐 **Network/API Timeout Error**\n\n"
                               "The OpenAI API is not responding. This could be due to:\n"
                               "- Network connectivity issues\n"
                               "- OpenAI API service problems\n"
                               "- Firewall/proxy blocking requests\n\n"
                               "**Solutions:**\n"
                               "1. Check your internet connection\n"
                               "2. Try again in a few minutes\n"
                               "3. Use existing test results below\n"
                               "4. Check OpenAI status at status.openai.com")
            elif "OPENAI_API_KEY" in error_msg:
                st.sidebar.error("🔑 **API Key Error**\n\n"
                               "Please check your OpenAI API key in the .env file")
            else:
                # Show first 500 chars of error for other issues
                short_error = error_msg[:500] + "..." if len(error_msg) > 500 else error_msg
                st.sidebar.error(f"**Error Details:**\n```\n{short_error}\n```")
            
            # Suggest using existing results
            if load_latest_results():
                st.sidebar.info("💡 **Tip:** You can still analyze existing test results below while troubleshooting the API issue.")
            
    except subprocess.TimeoutExpired:
        status_text.text("❌ Test suite timed out")
        st.sidebar.error("⏰ **Timeout Error**\n\n"
                        "Test suite timed out after 10 minutes. This usually indicates:\n"
                        "- Slow API responses\n"
                        "- Network connectivity issues\n\n"
                        "Try running with a smaller test set or check your connection.")
    except Exception as e:
        status_text.text("❌ Test suite error")
        st.sidebar.error(f"**Unexpected Error:** {str(e)}")
    finally:
        progress_bar.empty()
        time.sleep(2)
        status_text.empty()


def update_config_file(strategy: str, max_narrowed: int, max_embedding: int, max_final: int):
    """Update the settings file with new configuration."""
    # For now, we'll just update the session state
    # In a production system, you might want to update the actual settings file
    pass


def render_flow_diagram(case_data: Dict[str, Any]):
    """Render the classification flow diagram."""
    st.markdown("### 🔄 Classification Flow")
    
    ground_truth = case_data['ground_truth']
    narrowed_cats = case_data['stages']['narrowing']['candidates']
    final_selection = case_data['stages']['selection']['final_choice']
    
    # Create a simple flow visualization
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=("All Categories<br>(1000+)", "Narrowed Results<br>(Stage 1)", "Final Selection<br>(Stage 2)"),
        specs=[[{"type": "scatter"}, {"type": "scatter"}, {"type": "scatter"}]]
    )
    
    # Stage 1: All categories (represented as a cloud)
    fig.add_trace(
        go.Scatter(
            x=[0.5], y=[0.5],
            mode='markers+text',
            marker=dict(size=100, color='lightgray', symbol='circle'),
            text="All<br>Categories",
            textposition="middle center",
            showlegend=False,
            name="All Categories"
        ),
        row=1, col=1
    )
    
    # Stage 2: Narrowed categories
    narrowed_y = [0.8, 0.6, 0.4, 0.2, 0.1][:len(narrowed_cats)]
    narrowed_colors = []
    narrowed_text = []
    
    for i, cat in enumerate(narrowed_cats):
        if cat['path'] == ground_truth:
            color = 'green'
            symbol = 'circle'
        else:
            color = 'orange'
            symbol = 'circle'
        
        narrowed_colors.append(color)
        narrowed_text.append(cat['name'][:20] + "...")
    
    if narrowed_cats:
        fig.add_trace(
            go.Scatter(
                x=[0.5] * len(narrowed_cats),
                y=narrowed_y,
                mode='markers+text',
                marker=dict(size=30, color=narrowed_colors),
                text=narrowed_text,
                textposition="middle right",
                showlegend=False,
                name="Narrowed"
            ),
            row=1, col=2
        )
    
    # Stage 3: Final selection
    if final_selection:
        final_color = 'green' if final_selection['path'] == ground_truth else 'red'
        fig.add_trace(
            go.Scatter(
                x=[0.5], y=[0.5],
                mode='markers+text',
                marker=dict(size=50, color=final_color, symbol='star'),
                text=final_selection['name'][:15] + "...",
                textposition="middle center",
                showlegend=False,
                name="Final"
            ),
            row=1, col=3
        )
    
    fig.update_layout(
        height=300,
        showlegend=False,
        xaxis=dict(showgrid=False, showticklabels=False, range=[0, 1]),
        yaxis=dict(showgrid=False, showticklabels=False, range=[0, 1]),
        xaxis2=dict(showgrid=False, showticklabels=False, range=[0, 1]),
        yaxis2=dict(showgrid=False, showticklabels=False, range=[0, 1]),
        xaxis3=dict(showgrid=False, showticklabels=False, range=[0, 1]),
        yaxis3=dict(showgrid=False, showticklabels=False, range=[0, 1])
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_stage_breakdown(case_data: Dict[str, Any]):
    """Render detailed stage breakdown."""
    st.markdown("### 📊 Stage Breakdown")
    
    ground_truth = case_data['ground_truth']
    narrowed_cats = case_data['stages']['narrowing']['candidates']
    final_selection = case_data['stages']['selection']['final_choice']
    narrowing_time = case_data['stages']['narrowing']['processing_time']
    selection_time = case_data['stages']['selection']['processing_time']
    
    # Stage 1: Narrowing
    st.markdown(f"**Stage 1: Narrowing** ({len(narrowed_cats)} candidates, {narrowing_time:.1f}ms)")
    
    for cat in narrowed_cats:
        icon = get_status_icon(cat['path'], ground_truth, narrowed_cats, final_selection)
        st.markdown(f"{icon} {cat['name']} - `{cat['path']}`")
    
    st.markdown("---")
    
    # Stage 2: Selection
    st.markdown(f"**Stage 2: Selection** ({selection_time:.1f}ms)")
    
    if final_selection:
        icon = get_status_icon(final_selection['path'], ground_truth, narrowed_cats, final_selection)
        is_correct = final_selection['path'] == ground_truth
        result_text = "✅ CORRECT" if is_correct else "❌ INCORRECT"
        
        st.markdown(f"{icon} **{final_selection['name']}** ← FINAL SELECTION {result_text}")
        st.markdown(f"Path: `{final_selection['path']}`")
    
    # Summary
    total_time = narrowing_time + selection_time
    st.markdown(f"**⏱️ Total Processing Time:** {total_time:.1f}ms")


def render_hierarchy_tree(case_data: Dict[str, Any]):
    """Render category hierarchy tree view."""
    st.markdown("### 🌳 Category Hierarchy")
    
    ground_truth = case_data['ground_truth']
    narrowed_cats = case_data['stages']['narrowing']['candidates']
    final_selection = case_data['stages']['selection']['final_choice']
    
    # Load all categories to build hierarchy
    try:
        category_loader = CategoryLoader()
        all_categories = category_loader.load_categories()
        
        # Build hierarchy tree
        hierarchy = {}
        for cat in all_categories:
            parts = cat.path.strip('/').split('/')
            current = hierarchy
            for part in parts:
                if part not in current:
                    current[part] = {'children': {}, 'full_path': cat.path, 'category': cat}
                current = current[part]['children']
        
        # Render tree starting from root
        for root_name, root_data in hierarchy.items():
            render_tree_node(root_name, root_data, ground_truth, narrowed_cats, final_selection, level=0)
            
    except Exception as e:
        st.error(f"Error loading category hierarchy: {e}")


def render_tree_node(name: str, node_data: Dict, ground_truth: str, narrowed_cats: List[Dict], 
                    final_selection: Dict, level: int = 0):
    """Recursively render tree nodes."""
    full_path = node_data.get('full_path', '')
    children = node_data.get('children', {})
    
    # Get status icon
    icon = get_status_icon(full_path, ground_truth, narrowed_cats, final_selection)
    
    # Indent based on level
    indent = "  " * level
    
    # Special formatting for different statuses
    if full_path == ground_truth:
        if full_path == final_selection.get('path', ''):
            st.markdown(f"{indent}{icon} **{name}** ← TARGET (final selection)")
        else:
            st.markdown(f"{indent}{icon} **{name}** ← TARGET")
    elif full_path == final_selection.get('path', ''):
        st.markdown(f"{indent}{icon} **{name}** ← SELECTED")
    elif any(cat['path'] == full_path for cat in narrowed_cats):
        st.markdown(f"{indent}{icon} {name} (narrowed)")
    else:
        # Only show if it's relevant to the path or has relevant children
        if level < 2 or has_relevant_children(children, ground_truth, narrowed_cats, final_selection):
            st.markdown(f"{indent}{icon} {name}")
    
    # Render children if this node is on the path to ground truth or has relevant categories
    if children and (level < 2 or is_on_relevant_path(full_path, ground_truth, narrowed_cats, final_selection)):
        for child_name, child_data in children.items():
            render_tree_node(child_name, child_data, ground_truth, narrowed_cats, final_selection, level + 1)


def has_relevant_children(children: Dict, ground_truth: str, narrowed_cats: List[Dict], 
                         final_selection: Dict) -> bool:
    """Check if any children are relevant to the current test case."""
    for child_data in children.values():
        child_path = child_data.get('full_path', '')
        if (child_path == ground_truth or 
            child_path == final_selection.get('path', '') or
            any(cat['path'] == child_path for cat in narrowed_cats)):
            return True
        if has_relevant_children(child_data.get('children', {}), ground_truth, narrowed_cats, final_selection):
            return True
    return False


def is_on_relevant_path(path: str, ground_truth: str, narrowed_cats: List[Dict], 
                       final_selection: Dict) -> bool:
    """Check if a path is on the way to any relevant categories."""
    relevant_paths = [ground_truth, final_selection.get('path', '')] + [cat['path'] for cat in narrowed_cats]
    return any(relevant_path.startswith(path) for relevant_path in relevant_paths if relevant_path)


def render_analysis_section():
    """Render the main test case analysis section."""
    if 'test_results' not in st.session_state or not st.session_state.test_results:
        st.warning("🚫 No test results available.")
        
        # Show helpful info about existing results
        results_dir = Path("tests/results")
        if results_dir.exists():
            narrowing_files = list((results_dir / "narrowing").glob("*.json"))
            selection_files = list((results_dir / "selection").glob("*.json"))
            
            if narrowing_files and selection_files:
                st.info("💡 **Found existing test results!**\n\n"
                       f"- {len(narrowing_files)} narrowing result files\n"
                       f"- {len(selection_files)} selection result files\n\n"
                       "Click the button below to load the most recent results, "
                       "or run new tests using the configuration panel.")
                
                if st.button("📂 Load Latest Results", type="secondary"):
                    st.session_state.test_results = load_latest_results()
                    st.rerun()
            else:
                st.info("ℹ️ **No existing results found.**\n\n"
                       "Run the test suite using the configuration panel to generate results for analysis.")
        else:
            st.info("ℹ️ **No results directory found.**\n\n"
                   "Run the test suite using the configuration panel to generate results for analysis.")
        return
    
    # Transform results for UI
    ui_data = transform_results_for_ui(st.session_state.test_results)
    
    if not ui_data:
        st.error("Failed to process test results.")
        return
    
    st.header("📊 Test Case Analysis")
    
    # Test case selector
    test_case_options = [f"{i+1}/25 - {case['description'][:50]}..." for i, case in enumerate(ui_data)]
    selected_index = st.selectbox(
        "Test Case:",
        range(len(test_case_options)),
        format_func=lambda x: test_case_options[x],
        key="test_case_selector"
    )
    
    selected_case = ui_data[selected_index]
    
    # Display product description
    st.markdown("#### Product Description")
    st.info(selected_case['description'])
    
    # Display ground truth
    st.markdown(f"**🎯 Ground Truth:** `{selected_case['ground_truth']}`")
    
    # Create three columns for different visualizations
    col1, col2 = st.columns([2, 1])
    
    with col1:
        render_flow_diagram(selected_case)
        render_stage_breakdown(selected_case)
    
    with col2:
        render_hierarchy_tree(selected_case)


def render_custom_testing():
    """Render the custom testing panel."""
    st.header("🧪 Custom Test Case")
    
    # Product description input
    product_description = st.text_area(
        "Product Description:",
        placeholder="Enter a product description to classify...",
        height=100
    )
    
    # Load categories for selection
    try:
        category_loader = CategoryLoader()
        categories = category_loader.load_categories()
        category_paths = [cat.path for cat in categories]
        
        expected_category = st.selectbox(
            "Expected Category (Ground Truth):",
            category_paths,
            help="Select the expected category for comparison"
        )
        
        if st.button("🚀 Classify & Analyze", type="primary"):
            if len(product_description.strip()) < 10:
                st.error("Please enter a product description with at least 10 characters.")
            else:
                run_custom_classification(product_description, expected_category)
                
    except Exception as e:
        st.error(f"Error loading categories: {e}")


def run_sample_tests(strategy: str, max_narrowed: int, max_embedding: int, max_final: int):
    """Run a small sample of tests to check API connectivity."""
    # Update configuration
    update_config_file(strategy, max_narrowed, max_embedding, max_final)
    
    # Show progress
    progress_bar = st.sidebar.progress(0)
    status_text = st.sidebar.empty()
    
    try:
        status_text.text("Running sample tests (5 cases)...")
        progress_bar.progress(25)
        
        # Run just narrowing accuracy test with limited cases
        result = subprocess.run(
            ['python', 'tests/run_tests.py', '--narrowing-accuracy'],
            capture_output=True,
            text=True,
            timeout=180,  # 3 minute timeout for sample
            cwd=project_root
        )
        
        progress_bar.progress(75)
        
        if result.returncode == 0:
            progress_bar.progress(100)
            status_text.text("✅ Sample test completed!")
            st.sidebar.success("🎉 API connectivity confirmed! You can now run the full test suite.")
            
            # Reload results
            time.sleep(1)
            st.session_state.test_results = load_latest_results()
            st.rerun()
        else:
            status_text.text("❌ Sample test failed")
            error_msg = result.stderr
            
            if "ConnectTimeout" in error_msg or "APITimeoutError" in error_msg:
                st.sidebar.error("🌐 **API Connection Issue**\n\n"
                               "Even the sample test failed due to API timeout. "
                               "Please check your network connection and try again later.")
            else:
                short_error = error_msg[:300] + "..." if len(error_msg) > 300 else error_msg
                st.sidebar.error(f"**Sample Test Error:**\n```\n{short_error}\n```")
                
    except subprocess.TimeoutExpired:
        status_text.text("❌ Sample test timed out")
        st.sidebar.error("⏰ Sample test timed out. There may be network connectivity issues.")
    except Exception as e:
        status_text.text("❌ Sample test error")
        st.sidebar.error(f"**Sample Test Error:** {str(e)}")
    finally:
        progress_bar.empty()
        time.sleep(2)
        status_text.empty()


def run_custom_classification(text: str, expected_category: str):
    """Run classification on custom input."""
    try:
        with st.spinner("Running classification..."):
            pipeline = ClassificationPipeline()
            result = pipeline.classify(text)
        
        # Create case data structure similar to test results
        case_data = {
            'description': text,
            'ground_truth': expected_category,
            'stages': {
                'narrowing': {
                    'candidates': [{'path': cat.path, 'name': cat.name, 'description': cat.description} 
                                 for cat in result.candidates],
                    'correct_found': expected_category in [cat.path for cat in result.candidates],
                    'processing_time': result.metadata.get('narrowing_time_ms', 0)
                },
                'selection': {
                    'candidates': [{'path': cat.path, 'name': cat.name, 'description': cat.description} 
                                 for cat in result.candidates],
                    'final_choice': {'path': result.category.path, 'name': result.category.name, 
                                   'description': result.category.description},
                    'correct_selection': result.category.path == expected_category,
                    'processing_time': result.metadata.get('selection_time_ms', 0)
                }
            }
        }
        
        st.success("Classification completed!")
        
        # Display results using the same components
        col1, col2 = st.columns([2, 1])
        
        with col1:
            render_flow_diagram(case_data)
            render_stage_breakdown(case_data)
        
        with col2:
            render_hierarchy_tree(case_data)
            
    except Exception as e:
        error_str = str(e)
        if "ConnectTimeout" in error_str or "APITimeoutError" in error_str:
            st.error("🌐 **API Timeout Error**\n\n"
                    "The classification failed due to OpenAI API timeout. "
                    "Please check your network connection and try again.")
        elif "OPENAI_API_KEY" in error_str:
            st.error("🔑 **API Key Error**\n\n"
                    "Please check your OpenAI API key configuration.")
        else:
            st.error(f"**Classification Error:** {error_str}")


def check_api_connectivity():
    """Quick check if API is accessible."""
    try:
        # Check if .env file exists and has API key
        env_file = project_root / ".env"
        if not env_file.exists():
            return False, "No .env file found"
        
        with open(env_file) as f:
            content = f.read()
            if "OPENAI_API_KEY" not in content or not content.strip():
                return False, "No OpenAI API key configured"
        
        return True, "Configuration looks good"
    except Exception as e:
        return False, f"Configuration check failed: {e}"


def main():
    """Main application function."""
    st.title("🔍 Large Scale Classification System")
    st.markdown("Interactive tool for testing and analyzing classification strategies")
    
    # Quick API connectivity check
    api_ok, api_msg = check_api_connectivity()
    if not api_ok:
        st.warning(f"⚠️ **Configuration Issue:** {api_msg}")
        st.info("💡 You can still analyze existing test results, but won't be able to run new tests until this is fixed.")
    
    # Initialize session state
    if 'test_results' not in st.session_state:
        st.session_state.test_results = load_latest_results()
    
    # Render sidebar configuration
    render_config_panel()
    
    # Main content area
    render_analysis_section()
    
    # Custom testing panel (expandable)
    with st.expander("🧪 Custom Test Case", expanded=False):
        render_custom_testing()


if __name__ == "__main__":
    main()
