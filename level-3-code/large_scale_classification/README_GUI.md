# Classification System GUI

This Streamlit application provides an interactive interface for testing and analyzing different narrowing strategies and settings for the large-scale classification system.

## Features

### 1. Configuration Panel (Left Sidebar)
- **Strategy Selection**: Choose between Embedding and Hybrid narrowing strategies
- **Hyperparameter Controls**: Adjust max narrowed categories, embedding candidates, and final categories
- **Test Suite Execution**: Run the full test suite with current configuration
- **Status Display**: View last run timestamp and accuracy metrics

### 2. Test Case Analysis (Main Content)
- **Test Case Selector**: Browse through all 25 test cases with searchable descriptions
- **Product Description Display**: View the full product description being classified
- **Ground Truth**: See the expected correct category
- **Flow Diagram**: Visual representation of the classification pipeline
- **Stage Breakdown**: Detailed analysis of narrowing and selection stages with timing
- **Hierarchy Tree**: Interactive category tree showing the classification path

### 3. Custom Testing Panel (Bottom Expandable)
- **Custom Input**: Test arbitrary product descriptions
- **Expected Category Selection**: Choose the ground truth for comparison
- **Real-time Classification**: Run the pipeline on custom input
- **Same Visualizations**: View results using the same analysis tools

## Quick Start

1. **Install Dependencies**:
   ```bash
   uv add streamlit plotly pandas
   ```

2. **Set up Environment**:
   - Ensure you have a `.env` file with your `OPENAI_API_KEY`
   - Make sure the vector store is built (run the classification system once)

3. **Run the Application**:
   ```bash
   streamlit run streamlit_app.py
   ```

4. **Access the Interface**:
   - Open your browser to the URL shown in the terminal (typically `http://localhost:8501`)

## Usage Workflow

### Testing Different Strategies

1. **Configure Parameters**: Use the left sidebar to select strategy and adjust hyperparameters
2. **Run Test Suite**: Click "🚀 Run Test Suite" to execute tests with current settings
3. **Analyze Results**: Browse test cases to understand how different settings affect performance
4. **Compare Strategies**: Run tests with different configurations to compare results

### Analyzing Individual Test Cases

1. **Select Test Case**: Use the dropdown to choose a specific test case
2. **Review Flow**: Examine the classification flow diagram to see the pipeline stages
3. **Study Breakdown**: Look at the detailed stage breakdown for timing and accuracy
4. **Explore Hierarchy**: Use the category tree to understand the classification path

### Testing Custom Input

1. **Enter Description**: Type or paste a product description in the custom testing panel
2. **Select Expected Category**: Choose what you think the correct category should be
3. **Run Classification**: Click "🚀 Classify & Analyze" to see results
4. **Compare Results**: See how well the system performs on your custom input

## Color Coding Legend

- 🟢 **Green**: Correct category (ground truth)
- 🔵 **Blue**: System selected (correct)
- 🟡 **Yellow**: System selected (incorrect)
- 🔴 **Red**: Correct category (system missed)
- ⚪ **Gray**: Not considered

## Understanding the Results

### Narrowing Stage
- Shows which categories were selected by the narrowing strategy
- Displays similarity scores or reasoning for selection
- Indicates whether the ground truth category was included

### Selection Stage
- Shows the final category chosen by the LLM
- Indicates whether the selection was correct
- Provides confidence scores when available

### Performance Metrics
- **Processing Time**: Time taken for each stage and total
- **Accuracy**: Percentage of correct classifications
- **Strategy Comparison**: Side-by-side performance of different approaches

## Troubleshooting

### Common Issues

1. **"No test results available"**: Run the test suite first using the sidebar
2. **Import errors**: Make sure all dependencies are installed with `uv add`
3. **API errors**: Check that your OpenAI API key is set in the `.env` file
4. **Vector store errors**: Run the classification system once to build the vector store

### Performance Tips

- The vector store significantly speeds up embedding-based narrowing
- Hybrid strategy typically provides the best accuracy/speed tradeoff
- Custom testing runs in real-time but may be slower than batch tests

## Technical Details

### Architecture
- Built with Streamlit for the web interface
- Uses Plotly for interactive visualizations
- Integrates with the existing classification pipeline
- Loads test results from JSON files in `tests/results/`

### Data Flow
1. Configuration changes update the settings
2. Test suite execution runs the existing test runner
3. Results are loaded from JSON files and transformed for UI display
4. Visualizations are generated from the processed data

### File Structure
- `streamlit_app.py`: Main application file
- `tests/results/`: JSON result files from test runs
- `src/`: Original classification system code
- `data/categories.txt`: Category hierarchy definition
