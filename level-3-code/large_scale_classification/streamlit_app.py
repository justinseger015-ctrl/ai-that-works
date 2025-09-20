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
import plotly.figure_factory as ff
import streamlit as st
from plotly.subplots import make_subplots
import networkx as nx
import numpy as np

# Add the src directory to Python path
import sys
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Ensure environment variables are loaded before importing settings
import os
from dotenv import load_dotenv
env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(env_file)

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
    
    # Get results - prioritize Hybrid strategy if available and configured
    current_strategy = settings.narrowing_strategy.value
    strategy_key = None
    
    if current_strategy == "hybrid" and "Hybrid" in narrowing_data['strategies']:
        strategy_key = "Hybrid"
    elif current_strategy == "embedding" and "Embedding" in narrowing_data['strategies']:
        strategy_key = "Embedding"
    else:
        # Fallback to first available strategy
        strategy_key = list(narrowing_data['strategies'].keys())[0]
    
    narrowing_results = narrowing_data['strategies'][strategy_key]['results']
    selection_results = selection_data['results']['individual_results']
    
    for i, (narrow_result, select_result) in enumerate(zip(narrowing_results, selection_results)):
        # Check if this is a hybrid result with stage breakdown
        is_hybrid_result = narrow_result.get('is_hybrid_result', False)
        
        if is_hybrid_result and 'stage1_categories' in narrow_result:
            # Use Stage 1 (embedding) results as the "narrowed" candidates
            narrowed_candidates = narrow_result['stage1_categories']
            narrowing_time = narrow_result['stage1_processing_time_ms']
            
            # Add stage breakdown information
            stage_breakdown = {
                'stage1_candidates': narrow_result['stage1_categories'],
                'stage1_time': narrow_result['stage1_processing_time_ms'],
                'stage2_candidates': narrow_result['narrowed_categories'],  # LLM refined results
                'stage2_time': narrow_result['stage2_processing_time_ms'],
                'is_hybrid': True
            }
        else:
            # Regular embedding strategy results
            narrowed_candidates = narrow_result['narrowed_categories']
            narrowing_time = narrow_result['processing_time_ms']
            stage_breakdown = {'is_hybrid': False}
        
        test_case_data = {
            'id': i,
            'description': narrow_result['test_case']['text'],
            'ground_truth': narrow_result['test_case']['category'],
            'stages': {
                'narrowing': {
                    'candidates': narrowed_candidates,
                    'correct_found': narrow_result['correct_category_found'],
                    'processing_time': narrowing_time
                },
                'selection': {
                    'candidates': select_result['candidate_categories'],
                    'final_choice': select_result['selected_category'],
                    'correct_selection': select_result['correct_selection'],
                    'processing_time': select_result['processing_time_ms']
                }
            },
            'stage_breakdown': stage_breakdown
        }
        ui_data.append(test_case_data)
    
    return ui_data




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
    
    # Strategy-specific settings
    max_narrowed = settings.max_narrowed_categories
    max_embedding = settings.max_embedding_candidates
    max_final = settings.max_final_categories
    
    if strategy == "embedding":
        # Embedding strategy only needs max_narrowed_categories
        max_narrowed = st.sidebar.number_input(
            "Max Narrowed Categories",
            min_value=3,
            max_value=20,
            value=settings.max_narrowed_categories,
            step=1,
            help="Number of final candidates passed to selection stage"
        )
    elif strategy == "hybrid":
        # Hybrid strategy uses two-stage narrowing
        st.sidebar.markdown("**Hybrid Strategy Settings**")
        max_embedding = st.sidebar.number_input(
            "Max Embedding Candidates",
            min_value=5,
            max_value=50,
            value=settings.max_embedding_candidates,
            step=1,
            help="Categories returned by embedding stage before LLM refinement"
        )
        max_final = st.sidebar.number_input(
            "Max LLM Candidates",
            min_value=2,
            max_value=10,
            value=settings.max_final_categories,
            step=1,
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
    
    # Show current vs selected config
    current_settings_different = (
        strategy != settings.narrowing_strategy.value or
        max_narrowed != settings.max_narrowed_categories or
        (strategy == "hybrid" and (
            max_embedding != settings.max_embedding_candidates or
            max_final != settings.max_final_categories
        ))
    )
    
    if current_settings_different:
        st.sidebar.warning("⚠️ Configuration changed! Run tests to see updated results.")
    
    # Run test suite button
    if st.sidebar.button("🚀 Run Full Suite", type="primary"):
        run_test_suite(strategy, max_narrowed, max_embedding, max_final)
    
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
        # Use uv run to ensure fresh Python process with updated settings
        result = subprocess.run(
            ['uv', 'run', 'python', 'tests/run_tests.py', '--all'],
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout for API calls
            cwd=project_root
        )
        
        progress_bar.progress(75)
        
        if result.returncode == 0:
            progress_bar.progress(100)
            status_text.text("✅ Test suite completed!")
            
            # Reload results with a longer wait to ensure files are written
            time.sleep(2)  # Give files time to be written
            st.session_state.test_results = load_latest_results()
            
            # Force a complete refresh to ensure tree diagram updates
            if st.session_state.test_results:
                st.sidebar.success("🔄 Results loaded! Tree diagram will update.")
            else:
                st.sidebar.warning("⚠️ No results loaded, check test execution")
            
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
            elif "OPENAI_API_KEY" in error_msg or "Incorrect API key provided" in error_msg:
                st.sidebar.error("🔑 **API Key Missing**")
                st.sidebar.markdown("""
                **Create a `.env` file with:**
                ```
                OPENAI_API_KEY=sk-your-key-here
                ```
                See TROUBLESHOOTING.md for details.
                """)
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
    import tempfile
    import shutil
    
    settings_file = project_root / "src" / "config" / "settings.py"
    
    try:
        # Read the current settings file
        with open(settings_file, 'r') as f:
            content = f.read()
        
        # Update the strategy
        if strategy == "embedding":
            content = content.replace(
                "narrowing_strategy: NarrowingStrategy = NarrowingStrategy.HYBRID",
                "narrowing_strategy: NarrowingStrategy = NarrowingStrategy.EMBEDDING"
            )
            content = content.replace(
                "narrowing_strategy: NarrowingStrategy = NarrowingStrategy.EMBEDDING",
                "narrowing_strategy: NarrowingStrategy = NarrowingStrategy.EMBEDDING"
            )  # Ensure it stays EMBEDDING if already set
        else:  # hybrid
            content = content.replace(
                "narrowing_strategy: NarrowingStrategy = NarrowingStrategy.EMBEDDING",
                "narrowing_strategy: NarrowingStrategy = NarrowingStrategy.HYBRID"
            )
            content = content.replace(
                "narrowing_strategy: NarrowingStrategy = NarrowingStrategy.HYBRID",
                "narrowing_strategy: NarrowingStrategy = NarrowingStrategy.HYBRID"
            )  # Ensure it stays HYBRID if already set
        
        # Update max_narrowed_categories
        import re
        content = re.sub(
            r'max_narrowed_categories: int = \d+',
            f'max_narrowed_categories: int = {max_narrowed}',
            content
        )
        
        # Update hybrid-specific settings
        if strategy == "hybrid":
            content = re.sub(
                r'max_embedding_candidates: int = \d+',
                f'max_embedding_candidates: int = {max_embedding}',
                content
            )
            content = re.sub(
                r'max_final_categories: int = \d+',
                f'max_final_categories: int = {max_final}',
                content
            )
        
        # Write the updated content to a temporary file first
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Replace the original file
        shutil.move(temp_file_path, settings_file)
        
        # Add more detailed success message
        if strategy == "hybrid":
            st.sidebar.success(f"✅ Updated config: {strategy} strategy")
            st.sidebar.info(f"📊 Max Embedding Candidates: {max_embedding}")
            st.sidebar.info(f"📊 Max LLM Candidates: {max_final}")
        else:
            st.sidebar.success(f"✅ Updated config: {strategy} strategy, max_narrowed={max_narrowed}")
        
        st.sidebar.warning("🔄 Settings updated - test results should reflect new config")
        
    except Exception as e:
        st.sidebar.error(f"❌ Failed to update config: {e}")
        st.sidebar.info("💡 Tests will run with previous configuration")


def build_category_tree():
    """Build a hierarchical tree structure from the flat category list."""
    try:
        category_loader = CategoryLoader()
        all_categories = category_loader.load_categories()
        
        # Build tree structure
        tree = {}
        
        for category in all_categories:
            parts = category.path.strip('/').split('/')
            current = tree
            path_so_far = ""
            
            for i, part in enumerate(parts):
                path_so_far += "/" + part
                
                if part not in current:
                    current[part] = {
                        'children': {},
                        'full_path': path_so_far,
                        'name': part,
                        'category': category if i == len(parts) - 1 else None,
                        'level': i
                    }
                current = current[part]['children']
        
        return tree
    except Exception as e:
        st.error(f"Error building category tree: {e}")
        return {}


def organize_categories_by_hierarchy(categories: List[Dict], ground_truth: str, narrowed_cats: List[Dict], 
                                   final_selection: Dict, stage1_cats: List[Dict] = None, stage_name: str = "Stage 1") -> Dict:
    """Organize categories into hierarchical structure for better display."""
    hierarchy = {}
    
    for cat in categories:
        path_parts = cat['path'].split('/')
        if len(path_parts) < 2:  # Skip if not properly formatted
            continue
            
        # Get top-level category (e.g., "Appliances")
        top_level = path_parts[1] if len(path_parts) > 1 else path_parts[0]
        
        # Get second-level category if exists (e.g., "Refrigerators", "Appliance Parts")
        second_level = path_parts[2] if len(path_parts) > 2 else None
        
        # Get status for this category
        status, color, icon = get_category_status(cat['path'], ground_truth, narrowed_cats, final_selection, stage1_cats, stage_name)
        
        # Initialize top-level if not exists
        if top_level not in hierarchy:
            hierarchy[top_level] = {}
            
        # Add to appropriate level
        if second_level:
            if second_level not in hierarchy[top_level]:
                hierarchy[top_level][second_level] = []
            hierarchy[top_level][second_level].append({
                'name': cat['name'],
                'path': cat['path'],
                'icon': icon,
                'status': status
            })
        else:
            # Direct top-level category
            if '_direct' not in hierarchy[top_level]:
                hierarchy[top_level]['_direct'] = []
            hierarchy[top_level]['_direct'].append({
                'name': cat['name'],
                'path': cat['path'],
                'icon': icon,
                'status': status
            })
    
    return hierarchy


def get_category_status(category_path: str, ground_truth: str, narrowed_cats: List[Dict], 
                       final_selection: Dict, stage1_cats: List[Dict] = None, stage_name: str = "Stage 1") -> tuple[str, str, str]:
    """Get status, color, and icon for a category in the classification flow."""
    narrowed_paths = [cat['path'] for cat in narrowed_cats]
    final_path = final_selection.get('path', '') if final_selection else ''
    
    # Special handling for Final Selection view
    if stage_name == "Final Selection":
        if category_path == final_path:
            if category_path == ground_truth:
                return "correct_selected", "#22C55E", "✅"  # Green - correct final selection
            else:
                return "incorrect_selected", "#EAB308", "🟡"  # Yellow - incorrect final selection
        else:
            # Everything else is gray in final selection view
            return "not_considered", "#9CA3AF", "⚪"  # Gray - not the final selection
    
    # Check if this category was in stage 1 but filtered out in stage 2
    was_in_stage1 = stage1_cats and any(cat['path'] == category_path for cat in stage1_cats)
    is_filtered_out = was_in_stage1 and category_path not in narrowed_paths and "Stage 2" in stage_name
    
    if category_path == ground_truth:
        if category_path == final_path:
            return "correct_selected", "#22C55E", "✅"  # Green - correct and selected
        elif category_path in narrowed_paths:
            return "correct_narrowed", "#3B82F6", "🔵"  # Blue - correct and narrowed
        elif is_filtered_out:
            return "correct_missed", "#EF4444", "🔴"  # Red - correct but filtered out
        else:
            return "correct_missed", "#EF4444", "🔴"  # Red - correct but missed
    else:
        if category_path == final_path:
            return "incorrect_selected", "#EAB308", "🟡"  # Yellow - incorrect but selected
        elif category_path in narrowed_paths:
            return "incorrect_narrowed", "#F59E0B", "🟠"  # Orange - incorrect but narrowed
        elif is_filtered_out:
            return "filtered_out", "#E5E7EB", "⭕"  # Light gray - filtered out in this stage
        else:
            return "not_considered", "#9CA3AF", "⚪"  # Gray - not considered




def render_visual_tree_diagram(tree: Dict, ground_truth: str, narrowed_cats: List[Dict], final_selection: Dict, 
                              stage_name: str = "Stage 1", stage1_cats: List[Dict] = None):
    """Render an interactive visual tree diagram using Plotly."""
    st.markdown(f"**🌳 Interactive Tree Diagram - {stage_name}:**")
    
    # Build a graph structure for visualization
    G = nx.DiGraph()
    
    # Colors for different statuses
    color_map = {
        'correct_selected': '#22C55E',      # Green
        'correct_narrowed': '#3B82F6',      # Blue  
        'incorrect_selected': '#8B5CF6',    # Purple
        'incorrect_narrowed': '#F59E0B',    # Orange
        'correct_missed': '#EF4444',        # Red
        'not_considered': '#9CA3AF',        # Gray
        'filtered_out': '#E5E7EB'           # Light gray for filtered categories
    }
    
    # Icon map
    icon_map = {
        'correct_selected': '✅',
        'correct_narrowed': '🔵', 
        'incorrect_selected': '🟣',
        'incorrect_narrowed': '🟠',
        'correct_missed': '🔴',
        'not_considered': '⚪',
        'filtered_out': '⭕'                # Filtered out in current stage
    }
    
    # Helper function to add nodes recursively
    def add_tree_nodes(tree_nodes, parent_id=None, level=0, max_level=3):
        if level > max_level:
            return
            
        for name, node_data in tree_nodes.items():
            node_id = node_data.get('full_path', name)
            
            # Get status for coloring
            status, color, icon = get_category_status(node_id, ground_truth, narrowed_cats, final_selection, stage1_cats, stage_name)
            
            # Include all Stage 1 categories plus structural nodes needed for tree
            # Use stage1_cats to determine which nodes to include (for stable structure)
            # But use narrowed_cats for coloring logic
            is_stage1_category = stage1_cats and any(cat['path'] == node_id for cat in stage1_cats)
            is_narrowed_category = any(cat['path'] == node_id for cat in narrowed_cats)
            
            # Always include Stage 1 categories to maintain consistent tree structure
            if status == 'not_considered' and level > 1 and not is_stage1_category:
                if not has_relevant_children_in_tree(node_data.get('children', {}), ground_truth, stage1_cats or narrowed_cats, final_selection):
                    continue
            
            # Add node to graph
            G.add_node(node_id, 
                      name=name,
                      level=level,
                      status=status,
                      color=color_map[status],
                      icon=icon_map[status],
                      full_path=node_id)
            
            # Add edge from parent
            if parent_id:
                G.add_edge(parent_id, node_id)
            
            # Add children
            children = node_data.get('children', {})
            if children:
                add_tree_nodes(children, node_id, level + 1, max_level)
    
    # Build the graph
    add_tree_nodes(tree)
    
    if len(G.nodes()) == 0:
        st.warning("No relevant nodes found for tree visualization")
        return
    
    # Create hierarchical layout
    pos = create_hierarchical_layout(G)
    
    # Extract node and edge information
    node_x = []
    node_y = []
    node_colors = []
    node_text = []
    node_hover = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        node_data = G.nodes[node]
        node_colors.append(node_data['color'])
        
        # Create display text
        display_name = node_data['name']
        if len(display_name) > 15:
            display_name = display_name[:12] + "..."
        
        node_text.append(f"{node_data['icon']}<br>{display_name}")
        
        # Create hover text
        hover_text = f"<b>{node_data['name']}</b><br>"
        hover_text += f"Path: {node_data['full_path']}<br>"
        hover_text += f"Status: {node_data['status'].replace('_', ' ').title()}<br>"
        hover_text += f"Level: {node_data['level']}"
        node_hover.append(hover_text)
    
    # Extract edge information
    edge_x = []
    edge_y = []
    
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    # Create the plot
    fig = go.Figure()
    
    # Add edges
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        mode='lines',
        line=dict(color='#E5E7EB', width=3),
        hoverinfo='none',
        showlegend=False,
        name='connections'
    ))
    
    # Add nodes
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        marker=dict(
            size=50,
            color=node_colors,
            line=dict(width=3, color='white'),
            opacity=0.9
        ),
        text=node_text,
        textposition="middle center",
        textfont=dict(size=14, color='black', family='Arial Black'),
        hovertemplate='%{hovertext}<extra></extra>',
        hovertext=node_hover,
        showlegend=False,
        name='categories'
    ))
    
    # Update layout
    fig.update_layout(
        title="Classification Tree Flow",
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20,l=5,r=5,t=40),
        annotations=[ 
            dict(
                text="Hover over nodes for details. Tree shows hierarchical relationships and classification flow.",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.005, y=-0.002,
                xanchor='left', yanchor='bottom',
                font=dict(color='gray', size=10)
            )
        ],
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=600,
        plot_bgcolor='white'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def create_hierarchical_layout(G):
    """Create a hierarchical layout for the tree."""
    pos = {}
    
    # Group nodes by level
    levels = {}
    for node in G.nodes():
        level = G.nodes[node]['level']
        if level not in levels:
            levels[level] = []
        levels[level].append(node)
    
    # Position nodes
    max_level = max(levels.keys()) if levels else 0
    
    for level, nodes in levels.items():
        y = max_level - level  # Higher levels at top
        num_nodes = len(nodes)
        
        if num_nodes == 1:
            pos[nodes[0]] = (0, y)
        else:
            # Spread nodes horizontally
            x_positions = np.linspace(-2, 2, num_nodes)
            for i, node in enumerate(nodes):
                pos[node] = (x_positions[i], y)
    
    return pos


def render_tree_node_with_flow(tree_nodes: Dict, ground_truth: str, narrowed_cats: List[Dict], 
                               final_selection: Dict, level: int = 0, max_display_level: int = 3):
    """Render tree nodes with classification flow information."""
    if level > max_display_level:
        return
    
    if level == 0:
        st.markdown("**🌳 Classification Path Through Category Tree:**")
    
    # Sort nodes to show relevant ones first
    def sort_key(item):
        name, node_data = item
        path = node_data.get('full_path', '')
        status, _, _ = get_category_status(path, ground_truth, narrowed_cats, final_selection)
        
        # Priority order: correct_selected > correct_narrowed > incorrect_selected > incorrect_narrowed > correct_missed > not_considered
        priority = {
            'correct_selected': 0,
            'correct_narrowed': 1,
            'incorrect_selected': 2,
            'incorrect_narrowed': 3,
            'correct_missed': 4,
            'not_considered': 5
        }
        return priority.get(status, 6)
    
    sorted_nodes = sorted(tree_nodes.items(), key=sort_key)
    
    for name, node_data in sorted_nodes:
        full_path = node_data.get('full_path', '')
        children = node_data.get('children', {})
        
        # Get status for this node
        status, color, icon = get_category_status(full_path, ground_truth, narrowed_cats, final_selection)
        
        # Skip nodes that aren't relevant unless they're on the path to something relevant
        # But be more permissive at higher levels to show context
        if level > 2 and status == 'not_considered' and not has_relevant_children_in_tree(children, ground_truth, narrowed_cats, final_selection):
            continue
        
        # Create indentation
        indent = "  " * level
        
        # Get additional information
        stage_info = ""
        if status in ['correct_narrowed', 'incorrect_narrowed']:
            stage_info = " (Stage 1)"
        elif status in ['correct_selected', 'incorrect_selected']:
            stage_info = " (Stage 2 - Final)"
        
        # Special formatting for different statuses
        if status == 'correct_selected':
            st.markdown(f"{indent}{icon} **{name}** ← GROUND TRUTH & FINAL SELECTION{stage_info}")
        elif status == 'correct_narrowed':
            st.markdown(f"{indent}{icon} **{name}** ← GROUND TRUTH{stage_info}")
        elif status == 'incorrect_selected':
            st.markdown(f"{indent}{icon} **{name}** ← INCORRECT FINAL SELECTION{stage_info}")
        elif status == 'incorrect_narrowed':
            st.markdown(f"{indent}{icon} {name}{stage_info}")
        elif status == 'correct_missed':
            st.markdown(f"{indent}{icon} **{name}** ← GROUND TRUTH (MISSED)")
        else:
            # Only show if it has relevant children or is at a low level
            if level < 2 or has_relevant_children_in_tree(children, ground_truth, narrowed_cats, final_selection):
                st.markdown(f"{indent}{icon} {name}")
        
        # Show path for leaf nodes or important nodes
        if level > 0 and (not children or status != 'not_considered'):
            st.markdown(f"{indent}   `{full_path}`")
        
        # Add similarity score if available and relevant
        if status in ['correct_narrowed', 'incorrect_narrowed', 'correct_selected', 'incorrect_selected']:
            # Try to find similarity score from narrowed categories
            for cat in narrowed_cats:
                if cat['path'] == full_path:
                    # Note: Similarity scores aren't in the current data structure, 
                    # but we can add this when they become available
                    break
        
        # Recursively render children
        if children and (level < 2 or has_relevant_children_in_tree(children, ground_truth, narrowed_cats, final_selection)):
            render_tree_node_with_flow(children, ground_truth, narrowed_cats, final_selection, level + 1, max_display_level)


def has_relevant_children_in_tree(children: Dict, ground_truth: str, narrowed_cats: List[Dict], 
                                 final_selection: Dict) -> bool:
    """Check if any children are relevant to the current test case."""
    if not children:
        return False
    
    for child_data in children.values():
        child_path = child_data.get('full_path', '')
        status, _, _ = get_category_status(child_path, ground_truth, narrowed_cats, final_selection)
        
        if status != 'not_considered':
            return True
        
        # Check recursively
        if has_relevant_children_in_tree(child_data.get('children', {}), ground_truth, narrowed_cats, final_selection):
            return True
    
    return False


def render_flow_diagram(case_data: Dict[str, Any]):
    """Render the classification flow diagram - now using tree-based visualization."""
    st.markdown("### 🌳 Classification Tree Flow")
    
    ground_truth = case_data['ground_truth']
    narrowed_cats = case_data['stages']['narrowing']['candidates']
    final_selection = case_data['stages']['selection']['final_choice']
    
    # Legend
    st.markdown("**Legend:**")
    stage_breakdown = case_data.get('stage_breakdown', {'is_hybrid': False})
    
    if stage_breakdown.get('is_hybrid', False):
        # Extended legend for hybrid strategies
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            st.markdown("✅ **Correct & Selected**")
        with col2:
            st.markdown("🔵 **Correct & Narrowed**")
        with col3:
            st.markdown("🟣 **Incorrect & Selected**")
        with col4:
            st.markdown("🟠 **Incorrect & Narrowed**")
        with col5:
            st.markdown("🔴 **Correct but Missed**")
        with col6:
            st.markdown("⭕ **Filtered Out**")
    else:
        # Standard legend for embedding strategies
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.markdown("✅ **Correct & Selected**")
        with col2:
            st.markdown("🔵 **Correct & Narrowed**")
        with col3:
            st.markdown("🟣 **Incorrect & Selected**")
        with col4:
            st.markdown("🟠 **Incorrect & Narrowed**")
        with col5:
            st.markdown("🔴 **Correct but Missed**")
    
    st.markdown("---")
    
    # Render the visual tree diagram FIRST - most prominent position
    stage_breakdown = case_data.get('stage_breakdown', {'is_hybrid': False})
    
    if stage_breakdown.get('is_hybrid', False):
        # Hybrid strategy: show stage toggle with enhanced UI
        st.markdown("### 🔄 **Narrowing Stage Visualization**")
        st.markdown("*Choose which stage of the hybrid narrowing process to visualize:*")
        
        # Create stage options with better visual hierarchy
        stage1_count = len(stage_breakdown['stage1_candidates'])
        stage2_count = len(stage_breakdown['stage2_candidates'])
        
        # Use columns for better layout and prominence
        col1, col2, col3 = st.columns(3)
        
        # Create custom button-style selection using columns and styling
        with col1:
            stage1_selected = st.button(
                f"🔍 **Stage 1: Embedding**\n{stage1_count} categories",
                key="stage1_btn",
                help="View the initial embedding-based narrowing results",
                use_container_width=True
            )
            
        with col2:
            stage2_selected = st.button(
                f"🧠 **Stage 2: LLM Refinement**\n{stage2_count} categories", 
                key="stage2_btn",
                help="View the LLM-refined narrowing results",
                use_container_width=True
            )
            
        with col3:
            final_selected = st.button(
                f"✅ **Final Selection**\n1 category",
                key="final_btn", 
                help="View only the final selected category",
                use_container_width=True
            )
        
        # Determine selected stage with session state persistence
        if 'selected_stage' not in st.session_state:
            st.session_state.selected_stage = 'stage1'
            
        if stage1_selected:
            st.session_state.selected_stage = 'stage1'
        elif stage2_selected:
            st.session_state.selected_stage = 'stage2'
        elif final_selected:
            st.session_state.selected_stage = 'final'
        
        # Show current selection with visual feedback
        st.markdown("---")
        if st.session_state.selected_stage == 'stage1':
            st.success(f"📊 **Currently Viewing**: Stage 1 - Embedding ({stage1_count} categories)")
            stage_option = f"🔍 Stage 1: Embedding ({stage1_count} categories)"
        elif st.session_state.selected_stage == 'stage2':
            st.info(f"📊 **Currently Viewing**: Stage 2 - LLM Refinement ({stage2_count} categories)")
            stage_option = f"🧠 Stage 2: LLM Refinement ({stage2_count} categories)"
        else:
            st.warning(f"📊 **Currently Viewing**: Final Selection (1 category)")
            stage_option = f"✅ Final Selection (1 category)"
        
        # Always use Stage 1 candidates for tree structure to keep layout stable
        # But pass different narrowed_cats for coloring based on selected stage
        tree_structure_candidates = stage_breakdown['stage1_candidates']  # Keep tree structure constant
        
        if "Stage 1" in stage_option:
            tree_coloring_candidates = stage_breakdown['stage1_candidates']
            stage_name = f"Stage 1: Embedding ({stage1_count} categories)"
        elif "Stage 2" in stage_option:
            tree_coloring_candidates = stage_breakdown['stage2_candidates']
            stage_name = f"Stage 2: LLM Refinement ({stage2_count} categories)"
        else:  # Final Selection
            tree_coloring_candidates = [final_selection] if final_selection else []
            stage_name = "Final Selection"
            
        # Show stage-specific metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            if "Stage 1" in stage_option:
                st.metric("Stage 1 Time", f"{stage_breakdown['stage1_time']:.1f}ms")
            elif "Stage 2" in stage_option:
                st.metric("Stage 2 Time", f"{stage_breakdown['stage2_time']:.1f}ms")
            else:
                total_time = stage_breakdown['stage1_time'] + stage_breakdown['stage2_time']
                st.metric("Total Time", f"{total_time:.1f}ms")
        
        with col2:
            if "Stage 1" in stage_option:
                st.metric("Candidates", f"{stage1_count}")
            elif "Stage 2" in stage_option:
                filtered_out = stage1_count - stage2_count
                st.metric("Filtered Out", f"{filtered_out}")
            else:
                st.metric("Final Choice", "1")
                
        with col3:
            if "Stage 1" in stage_option:
                st.metric("Strategy", "Embedding")
            elif "Stage 2" in stage_option:
                st.metric("Strategy", "LLM")
            else:
                st.metric("Strategy", "Selection")
        
    else:
        # Embedding strategy: single stage
        tree_candidates = narrowed_cats
        stage_name = f"Embedding Strategy ({len(narrowed_cats)} categories)"
    
    # Render the visual tree diagram
    if stage_breakdown.get('is_hybrid', False):
        # For hybrid: use structure candidates for tree, coloring candidates for colors
        stage1_for_tree = stage_breakdown.get('stage1_candidates')
        render_visual_tree_diagram(build_category_tree(), ground_truth, tree_coloring_candidates, final_selection, stage_name, stage1_for_tree)
    else:
        # For embedding: use narrowed_cats for both structure and coloring
        render_visual_tree_diagram(build_category_tree(), ground_truth, narrowed_cats, final_selection, stage_name)
    
    st.markdown("---")
    
    # Show processing summary
    narrowing_time = case_data['stages']['narrowing']['processing_time']
    selection_time = case_data['stages']['selection']['processing_time']
    total_time = narrowing_time + selection_time
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Narrowing Time", f"{narrowing_time:.1f}ms")
    with col2:
        st.metric("Selection Time", f"{selection_time:.1f}ms")
    with col3:
        st.metric("Total Time", f"{total_time:.1f}ms")
    
    st.markdown("---")
    


def render_strategy_results(case_data: Dict[str, Any]):
    """Render detailed strategy results with clear organization and visual hierarchy."""
    ground_truth = case_data['ground_truth']
    narrowed_cats = case_data['stages']['narrowing']['candidates']
    final_selection = case_data['stages']['selection']['final_choice']
    stage_breakdown = case_data.get('stage_breakdown', {'is_hybrid': False})
    
    # === COLOR LEGEND SECTION ===
    st.markdown("## 🎨 Color Legend")
    st.markdown("**Understanding the category status indicators:**")
    
    if stage_breakdown.get('is_hybrid', False):
        # Extended legend for hybrid strategies with better organization
        legend_col1, legend_col2, legend_col3 = st.columns(3)
        with legend_col1:
            st.markdown("### ✅ Positive Results")
            st.markdown("✅ **Correct & Selected** - Perfect match!")
            st.markdown("🔵 **Correct & Narrowed** - Found but not selected")
        with legend_col2:
            st.markdown("### ⚠️ Partial Results")
            st.markdown("🟣 **Incorrect & Selected** - Wrong final choice")
            st.markdown("🟠 **Incorrect & Narrowed** - Wrong but considered")
        with legend_col3:
            st.markdown("### ❌ Negative Results")
            st.markdown("🔴 **Correct but Missed** - Should have been found")
            st.markdown("⭕ **Filtered Out** - Removed in Stage 2")
    else:
        # Standard legend for embedding strategies
        legend_col1, legend_col2, legend_col3 = st.columns(3)
        with legend_col1:
            st.markdown("### ✅ Positive Results")
            st.markdown("✅ **Correct & Selected** - Perfect match!")
            st.markdown("🔵 **Correct & Narrowed** - Found but not selected")
        with legend_col2:
            st.markdown("### ⚠️ Partial Results")
            st.markdown("🟣 **Incorrect & Selected** - Wrong final choice")
            st.markdown("🟠 **Incorrect & Narrowed** - Wrong but considered")
        with legend_col3:
            st.markdown("### ❌ Negative Results")
            st.markdown("🔴 **Correct but Missed** - Should have been found")
    
    st.markdown("---")
    
    # === STRATEGY RESULTS SECTION ===
    if stage_breakdown.get('is_hybrid', False):
        # Hybrid strategy: show both stages with enhanced organization
        st.markdown("## 📋 Hybrid Strategy Results")
        st.markdown("**Two-stage classification process with embedding narrowing followed by LLM refinement.**")
        
        stage1_cats = stage_breakdown['stage1_candidates']
        stage2_cats = stage_breakdown['stage2_candidates']
        
        # Performance summary at the top
        total_time = stage_breakdown['stage1_time'] + stage_breakdown['stage2_time']
        perf_col1, perf_col2, perf_col3 = st.columns(3)
        with perf_col1:
            st.metric("Stage 1 Time", f"{stage_breakdown['stage1_time']:.1f}ms", help="Embedding similarity search time")
        with perf_col2:
            st.metric("Stage 2 Time", f"{stage_breakdown['stage2_time']:.1f}ms", help="LLM refinement time")
        with perf_col3:
            st.metric("Total Time", f"{total_time:.1f}ms", help="Combined processing time")
        
        st.markdown("---")
        
        # === STAGE 1 RESULTS ===
        st.markdown(f"## 🔍 Stage 1: Embedding Similarity")
        st.markdown(f"### Found {len(stage1_cats)} candidate categories using embedding similarity")
        
        stage1_hierarchy = organize_categories_by_hierarchy(stage1_cats, ground_truth, stage1_cats, final_selection, stage1_cats, "Stage 1")
        
        # Create expandable sections for better organization
        with st.expander(f"📂 View all {len(stage1_cats)} Stage 1 categories", expanded=True):
            for top_level, subcategories in sorted(stage1_hierarchy.items()):
                if top_level == '_direct':
                    continue
                    
                # Show top-level category header
                st.markdown(f"### 📁 {top_level}")
                
                # Show direct top-level categories first
                if '_direct' in subcategories:
                    for cat in subcategories['_direct']:
                        st.markdown(f"#### {cat['icon']} {cat['name']}")
                        st.code(cat['path'], language=None)
                
                # Show subcategories
                for subcat_name, items in sorted(subcategories.items()):
                    if subcat_name == '_direct':
                        continue
                    st.markdown(f"#### 📂 {subcat_name}")
                    for cat in items:
                        st.markdown(f"##### {cat['icon']} {cat['name']}")
                        st.code(cat['path'], language=None)
        
        st.markdown("---")
        
        # === STAGE 2 RESULTS ===
        st.markdown(f"## 🤖 Stage 2: LLM Refinement")
        st.markdown(f"### Refined to {len(stage2_cats)} categories using language model analysis")
        
        stage2_hierarchy = organize_categories_by_hierarchy(stage2_cats, ground_truth, stage2_cats, final_selection, stage1_cats, "Stage 2")
        
        with st.expander(f"📂 View all {len(stage2_cats)} Stage 2 categories", expanded=True):
            for top_level, subcategories in sorted(stage2_hierarchy.items()):
                if top_level == '_direct':
                    continue
                    
                # Show top-level category header
                st.markdown(f"### 📁 {top_level}")
                
                # Show direct top-level categories first
                if '_direct' in subcategories:
                    for cat in subcategories['_direct']:
                        stage_info = " 🎯 **FINAL SELECTION**" if cat['path'] == final_selection.get('path', '') else ""
                        st.markdown(f"#### {cat['icon']} {cat['name']}{stage_info}")
                        st.code(cat['path'], language=None)
                
                # Show subcategories
                for subcat_name, items in sorted(subcategories.items()):
                    if subcat_name == '_direct':
                        continue
                    st.markdown(f"#### 📂 {subcat_name}")
                    for cat in items:
                        stage_info = " 🎯 **FINAL SELECTION**" if cat['path'] == final_selection.get('path', '') else ""
                        st.markdown(f"##### {cat['icon']} {cat['name']}{stage_info}")
                        st.code(cat['path'], language=None)
                        
    else:
        # === EMBEDDING STRATEGY RESULTS ===
        st.markdown("## 📋 Embedding Strategy Results")
        st.markdown(f"### Single-stage classification using embedding similarity")
        st.markdown(f"**Found {len(narrowed_cats)} candidate categories**")
        
        # Performance metrics
        narrowing_time = case_data['stages']['narrowing']['processing_time']
        selection_time = case_data['stages']['selection']['processing_time']
        total_time = narrowing_time + selection_time
        
        perf_col1, perf_col2, perf_col3 = st.columns(3)
        with perf_col1:
            st.metric("Narrowing Time", f"{narrowing_time:.1f}ms", help="Embedding similarity search time")
        with perf_col2:
            st.metric("Selection Time", f"{selection_time:.1f}ms", help="Final category selection time")
        with perf_col3:
            st.metric("Total Time", f"{total_time:.1f}ms", help="Combined processing time")
        
        st.markdown("---")
        
        # Organize embedding results hierarchically
        embedding_hierarchy = organize_categories_by_hierarchy(narrowed_cats, ground_truth, narrowed_cats, final_selection, narrowed_cats, "Embedding")
        
        with st.expander(f"📂 View all {len(narrowed_cats)} embedding results", expanded=True):
            for top_level, subcategories in sorted(embedding_hierarchy.items()):
                if top_level == '_direct':
                    continue
                    
                # Show top-level category header
                st.markdown(f"### 📁 {top_level}")
                
                # Show direct top-level categories first
                if '_direct' in subcategories:
                    for cat in subcategories['_direct']:
                        stage_info = " 🎯 **FINAL SELECTION**" if cat['path'] == final_selection.get('path', '') else ""
                        st.markdown(f"#### {cat['icon']} {cat['name']}{stage_info}")
                        st.code(cat['path'], language=None)
                
                # Show subcategories
                for subcat_name, items in sorted(subcategories.items()):
                    if subcat_name == '_direct':
                        continue
                    st.markdown(f"#### 📂 {subcat_name}")
                    for cat in items:
                        stage_info = " 🎯 **FINAL SELECTION**" if cat['path'] == final_selection.get('path', '') else ""
                        st.markdown(f"##### {cat['icon']} {cat['name']}{stage_info}")
                        st.code(cat['path'], language=None)


def render_hierarchy_tree(case_data: Dict[str, Any]):
    """Render comprehensive classification analysis with clear visual hierarchy."""
    
    ground_truth = case_data['ground_truth']
    narrowed_cats = case_data['stages']['narrowing']['candidates']
    final_selection = case_data['stages']['selection']['final_choice']
    
    # Analysis insights
    narrowed_paths = [cat['path'] for cat in narrowed_cats]
    final_path = final_selection.get('path', '') if final_selection else ''
    
    # Check if ground truth was found in narrowing
    ground_truth_found = ground_truth in narrowed_paths
    correct_selection = final_path == ground_truth
    
    # Path analysis
    gt_parts = ground_truth.strip('/').split('/')
    final_parts = final_path.strip('/').split('/') if final_path else []
    
    # Find common path prefix
    common_depth = 0
    for i, (gt_part, final_part) in enumerate(zip(gt_parts, final_parts)):
        if gt_part == final_part:
            common_depth = i + 1
        else:
            break
    
    # === SECTION 1: CLASSIFICATION OUTCOME ===
    st.markdown("## 🎯 Classification Outcome")
    
    if correct_selection:
        st.success("### ✅ Perfect Classification", icon="🎯")
        st.markdown("**The model correctly identified the exact category!**")
    elif ground_truth_found:
        st.warning("### ⚠️ Partial Success", icon="⚠️")
        st.markdown("**The correct category was found during narrowing but not selected as the final answer.**")
        st.info(f"**Model's Final Choice:** `{final_path}`")
    else:
        st.error("### ❌ Classification Failed", icon="❌")
        st.markdown("**The correct category was not even included in the narrowed candidates.**")
        if final_path:
            st.info(f"**Model's Final Choice:** `{final_path}`")
    
    st.markdown("---")
    
    # === SECTION 2: CATEGORY HIERARCHY ANALYSIS ===
    st.markdown("## 📊 Category Hierarchy Analysis")
    
    # Create three columns for better organization
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📏 Path Depths")
        st.metric("Ground Truth", f"{len(gt_parts)} levels", help="How deep the correct category is in the hierarchy")
        if final_path:
            st.metric("Model Selection", f"{len(final_parts)} levels", help="How deep the selected category is in the hierarchy")
    
    with col2:
        st.markdown("### 🔗 Shared Hierarchy")
        if common_depth > 0:
            st.metric("Common Levels", f"{common_depth} levels", help="How many hierarchy levels the paths share")
            common_path = "/" + "/".join(gt_parts[:common_depth])
            st.markdown(f"**Shared Path:**")
            st.code(common_path, language=None)
        else:
            st.metric("Common Levels", "0 levels", help="The categories are in completely different branches")
            st.markdown("**Different root categories**")
    
    with col3:
        st.markdown("### 🎭 Classification Type")
        if not correct_selection and final_path:
            # Check if it's a parent/child relationship
            if final_path in ground_truth or ground_truth in final_path:
                if len(final_parts) < len(gt_parts):
                    st.error("**Too General**")
                    st.markdown("Selected parent instead of specific subcategory")
                else:
                    st.error("**Too Specific**")
                    st.markdown("Selected subcategory when parent was correct")
            elif common_depth > 0:
                st.warning("**Sibling Confusion**")
                st.markdown(f"Categories share {common_depth} hierarchy level(s)")
            else:
                st.error("**Complete Mismatch**")
                st.markdown("Selected from different category tree")
        else:
            st.success("**Exact Match**")
            st.markdown("Perfect category identification")
    
    st.markdown("---")
    
    # === SECTION 3: RELATED CATEGORIES ===
    st.markdown("## 🔗 Related Categories Analysis")
    
    # Find sibling categories (same parent)
    if len(gt_parts) > 1:
        parent_path = "/" + "/".join(gt_parts[:-1])
        siblings_in_narrowed = [cat for cat in narrowed_cats if cat['path'].startswith(parent_path) and cat['path'] != ground_truth]
        
        if siblings_in_narrowed:
            st.markdown(f"### 👥 Sibling Categories Considered ({len(siblings_in_narrowed)} found)")
            st.markdown("**Categories that share the same parent as the ground truth:**")
            
            # Show siblings in a more organized way
            for i, sibling in enumerate(siblings_in_narrowed[:5], 1):  # Show first 5
                sibling_name = sibling['path'].split('/')[-1]  # Get just the category name
                st.markdown(f"**{i}.** `{sibling_name}`")
                st.markdown(f"   Full path: `{sibling['path']}`")
            
            if len(siblings_in_narrowed) > 5:
                with st.expander(f"Show {len(siblings_in_narrowed) - 5} more sibling categories"):
                    for i, sibling in enumerate(siblings_in_narrowed[5:], 6):
                        sibling_name = sibling['path'].split('/')[-1]
                        st.markdown(f"**{i}.** `{sibling_name}` - `{sibling['path']}`")
        else:
            st.info("### 👥 No Sibling Categories Found")
            st.markdown("No other categories from the same parent were included in narrowing.")
    else:
        st.info("### 👥 Root Level Category")
        st.markdown("The ground truth is a root-level category with no siblings.")
    
    st.markdown("---")
    
    # === SECTION 4: PERFORMANCE ANALYSIS ===
    st.markdown("## ⚡ Performance Analysis")
    
    narrowing_time = case_data['stages']['narrowing']['processing_time']
    selection_time = case_data['stages']['selection']['processing_time']
    total_time = narrowing_time + selection_time
    
    # Create performance metrics
    perf_col1, perf_col2, perf_col3 = st.columns(3)
    
    with perf_col1:
        st.metric(
            "Narrowing Time", 
            f"{narrowing_time:.1f}ms",
            help="Time spent finding candidate categories"
        )
    
    with perf_col2:
        st.metric(
            "Selection Time", 
            f"{selection_time:.1f}ms",
            help="Time spent choosing final category from candidates"
        )
    
    with perf_col3:
        st.metric(
            "Total Time", 
            f"{total_time:.1f}ms",
            help="Total classification time"
        )
    
    # Performance insights with better visual presentation
    st.markdown("### 🔍 Performance Insights")
    
    if narrowing_time > selection_time * 2:
        st.warning("**⏱️ Narrowing Bottleneck Detected**")
        st.markdown("Most processing time is spent in the narrowing stage. Consider optimizing embedding similarity search or reducing the candidate pool.")
        
        # Show percentage breakdown
        narrowing_pct = (narrowing_time / total_time) * 100
        st.progress(narrowing_pct / 100, text=f"Narrowing: {narrowing_pct:.1f}% of total time")
        
    elif selection_time > narrowing_time * 2:
        st.warning("**🤖 Selection Bottleneck Detected**")
        st.markdown("Most processing time is spent in the final selection stage. The LLM is taking longer to choose from the candidates.")
        
        # Show percentage breakdown
        selection_pct = (selection_time / total_time) * 100
        st.progress(selection_pct / 100, text=f"Selection: {selection_pct:.1f}% of total time")
        
    else:
        st.success("**⚖️ Balanced Performance**")
        st.markdown("Processing time is well-distributed between narrowing and selection stages.")
        
        # Show balanced breakdown
        narrowing_pct = (narrowing_time / total_time) * 100
        selection_pct = (selection_time / total_time) * 100
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.progress(narrowing_pct / 100, text=f"Narrowing: {narrowing_pct:.1f}%")
        with col_b:
            st.progress(selection_pct / 100, text=f"Selection: {selection_pct:.1f}%")



def render_custom_testing():
    """Render the custom testing panel."""
    
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
                        'candidates': [{'path': cat.path, 'name': cat.name, 'description': cat.llm_description} 
                                     for cat in result.candidates],
                        'correct_found': expected_category in [cat.path for cat in result.candidates],
                        'processing_time': result.metadata.get('narrowing_time_ms', 0)
                    },
                    'selection': {
                        'candidates': [{'path': cat.path, 'name': cat.name, 'description': cat.llm_description} 
                                     for cat in result.candidates],
                        'final_choice': {'path': result.category.path, 'name': result.category.name, 
                                       'description': result.category.llm_description},
                        'correct_selection': result.category.path == expected_category,
                        'processing_time': result.metadata.get('selection_time_ms', 0)
                    }
                }
            }
        
        st.success("Classification completed!")
        
        # Display results using the same components
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["🎯 Classification Results", "📈 Classification Analysis", "📋 Detailed Strategy Results"])
        
        with tab1:
            render_flow_diagram(case_data)
        
        with tab2:
            render_hierarchy_tree(case_data)
        
        with tab3:
            render_strategy_results(case_data)
            
    except Exception as e:
        error_str = str(e)
        if "ConnectTimeout" in error_str or "APITimeoutError" in error_str:
            st.error("🌐 **API Timeout Error**\n\n"
                    "The classification failed due to OpenAI API timeout. "
                    "Please check your network connection and try again.")
        elif "OPENAI_API_KEY" in error_str or "Incorrect API key provided" in error_str:
            st.error("🔑 **API Key Configuration Error**")
            st.markdown("""
            **The `.env` file is missing or incorrectly configured.**
            
            **To fix this:**
            1. Create a file named `.env` in the project root directory
            2. Add your OpenAI API key:
            ```
            OPENAI_API_KEY=sk-your-actual-api-key-here
            ```
            3. Replace `sk-your-actual-api-key-here` with your real API key from https://platform.openai.com/account/api-keys
            
            **Important:** 
            - Do NOT include quotes around the API key
            - The API key should start with `sk-`
            - Make sure the `.env` file is in the same directory as `streamlit_app.py`
            """)
        else:
            st.error(f"**Classification Error:** {error_str}")


def check_api_connectivity():
    """Quick check if API is accessible."""
    try:
        # Check if .env file exists and has API key
        env_file = project_root / ".env"
        if not env_file.exists():
            return False, f"No .env file found at {env_file}"
        
        with open(env_file) as f:
            content = f.read()
            if "OPENAI_API_KEY" not in content or not content.strip():
                return False, f"No OpenAI API key found in {env_file}"
        
        # Also check if the settings object can access the API key
        try:
            from src.config.settings import settings
            api_key = settings.openai_api_key
            if not api_key or api_key.startswith('$'):
                return False, f"Settings not loading API key properly (got: {api_key[:20]}...)"
        except Exception as settings_error:
            return False, f"Settings loading error: {settings_error}"
        
        return True, "Configuration looks good"
    except Exception as e:
        return False, f"Configuration check failed: {e}"


def main():
    """Main application function."""
    st.title("🔍 Large Scale Classification System")
    st.markdown("Interactive tool for testing and analyzing classification strategies")
    
    # Custom CSS to make tab fonts larger
    st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 20px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Quick API connectivity check
    api_ok, api_msg = check_api_connectivity()
    if not api_ok:
        st.warning(f"⚠️ **Configuration Issue:** {api_msg}")
        st.info("💡 You can still analyze existing test results, but won't be able to run new tests until this is fixed.")
        
        # Add debug information
        with st.expander("🔍 Debug Information", expanded=False):
            st.markdown("**Environment File Path:**")
            st.code(str(project_root / ".env"))
            
            st.markdown("**Environment Variables:**")
            openai_key = os.getenv('OPENAI_API_KEY', 'Not found')
            if openai_key and openai_key != 'Not found':
                st.code(f"OPENAI_API_KEY = {openai_key[:10]}...{openai_key[-4:] if len(openai_key) > 14 else openai_key}")
            else:
                st.code("OPENAI_API_KEY = Not found")
            
            st.markdown("**Settings Object:**")
            try:
                from src.config.settings import settings
                st.code(f"settings.openai_api_key = {settings.openai_api_key[:10] if settings.openai_api_key else 'None'}...")
            except Exception as e:
                st.code(f"Settings error: {e}")
            
            st.markdown("**Current Working Directory:**")
            st.code(f"os.getcwd() = {os.getcwd()}")
            st.code(f"project_root = {project_root}")
    
    # Initialize session state
    if 'test_results' not in st.session_state:
        st.session_state.test_results = load_latest_results()
    
    # Render sidebar configuration
    render_config_panel()
    
    # Main content - check if we have test results to show the analysis tabs
    if 'test_results' not in st.session_state or not st.session_state.test_results:
        st.warning("🚫 No test results available.")
        
        # Show helpful info about existing results
        results_dir = Path("tests/results")
        if results_dir.exists():
            narrowing_files = list((results_dir / "narrowing").glob("*.json"))
            selection_files = list((results_dir / "selection").glob("*.json"))
            
            if narrowing_files and selection_files:
                st.info(f"📁 Found {len(narrowing_files)} narrowing and {len(selection_files)} selection result files.")
                st.info("🔄 Click 'Run Full Suite' in the sidebar to generate fresh results, or the app will use the latest existing results.")
            else:
                st.info("🚀 Click 'Run Full Suite' in the sidebar to generate test results.")
        else:
            st.info("🚀 Click 'Run Full Suite' in the sidebar to generate test results.")
        
        # Show only custom test case when no results available
        st.markdown("---")
        st.header("🧪 Custom Test Case")
        render_custom_testing()
        return

    # Transform results for UI display
    ui_data = transform_results_for_ui(st.session_state.test_results)
    
    if not ui_data:
        st.error("Failed to process test results.")
        return
    
    # Test case selector with status indicators and full text display
    test_case_options = []
    for i, case in enumerate(ui_data):
        # Check if model was correct for this case
        model_guess = case['stages']['selection']['final_choice']
        model_path = model_guess.get('path', 'Unknown') if model_guess else 'Unknown'
        is_correct = model_path == case['ground_truth']
        
        # Add appropriate status indicator
        status_emoji = "✅" if is_correct else "❌"
        option_text = f"{status_emoji} {i+1}/{len(ui_data)} - {case['description']}"
        test_case_options.append(option_text)
    selected_index = st.selectbox(
        "Test Case:",
        range(len(test_case_options)),
        format_func=lambda x: test_case_options[x],
        key="test_case_selector"
    )
    
    selected_case = ui_data[selected_index]
    
    # Create 4-tab structure with Custom Test Case as the 4th tab
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Classification Results", "📈 Classification Analysis", "📋 Detailed Strategy Results", "🧪 Custom Test Case"])
    
    with tab1:
        # Display product description
        st.markdown("#### Product Description")
        st.info(selected_case['description'])
        
        # Display ground truth and model guess prominently
        st.markdown(f"#### 🎯 **Ground Truth:** `{selected_case['ground_truth']}`")
        
        # Get model's final selection
        model_guess = selected_case['stages']['selection']['final_choice']
        model_path = model_guess.get('path', 'Unknown') if model_guess else 'Unknown'
        
        # Check if model was correct and choose appropriate status
        is_correct = model_path == selected_case['ground_truth']
        if is_correct:
            guess_status = "✅"
        else:
            guess_status = "❌"
        
        st.markdown(f"#### 🔮 **Model Guess:** `{model_path}` {guess_status}")
        
        # Show the tree diagram prominently right after product description
        render_flow_diagram(selected_case)
    
    with tab2:
        # Classification Analysis tab
        render_hierarchy_tree(selected_case)
    
    with tab3:
        # Strategy results tab
        render_strategy_results(selected_case)
    
    with tab4:
        # Custom Test Case tab
        render_custom_testing()


if __name__ == "__main__":
    main()
