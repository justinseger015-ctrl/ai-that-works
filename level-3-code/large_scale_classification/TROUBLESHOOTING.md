# Troubleshooting Guide

## OpenAI API Timeout Errors

### The Problem
You're seeing errors like:
- `httpcore.ConnectTimeout: _ssl.c:1011: The handshake operation timed out`
- `openai.APITimeoutError: Request timed out`

### Common Causes
1. **Network connectivity issues** - Unstable internet connection
2. **OpenAI API service problems** - Temporary API outages
3. **Firewall/proxy blocking** - Corporate networks blocking OpenAI
4. **DNS resolution issues** - Can't resolve api.openai.com
5. **SSL/TLS handshake problems** - Certificate or encryption issues

### Solutions

#### 1. Quick Diagnostics
```bash
# Test basic connectivity
ping api.openai.com

# Test HTTPS connectivity
curl -I https://api.openai.com/v1/models

# Check OpenAI service status
curl -s https://status.openai.com/api/v2/status.json | grep "indicator"
```

#### 2. Network Troubleshooting
- **Check internet connection**: Try browsing other websites
- **Try different network**: Switch to mobile hotspot or different WiFi
- **Restart router/modem**: Sometimes helps with DNS issues
- **Use different DNS**: Try Google DNS (8.8.8.8) or Cloudflare (1.1.1.1)

#### 3. Firewall/Proxy Issues
If you're on a corporate network:
- **Contact IT**: Ask them to whitelist `*.openai.com`
- **Use VPN**: Try connecting through a personal VPN
- **Configure proxy**: Set HTTP_PROXY and HTTPS_PROXY environment variables

#### 4. API Key Issues
```bash
# Check if your API key is valid
curl -H "Authorization: Bearer YOUR_API_KEY" https://api.openai.com/v1/models
```

#### 5. Temporary Workarounds

##### Use Existing Results
The GUI can analyze existing test results without making API calls:
1. Look for existing results in `tests/results/`
2. Click "📂 Load Latest Results" in the GUI
3. Analyze previous test runs while troubleshooting API issues

##### Run Sample Tests First
Use the "🔬 Run Sample" button instead of full test suite:
- Tests only 5 cases instead of 25
- Faster timeout detection
- Confirms API connectivity before running full suite

##### Increase Timeout Settings
Edit the OpenAI client configuration to use longer timeouts:
```python
# In src/classification/embeddings.py or similar
client = OpenAI(
    timeout=httpx.Timeout(60.0, connect=10.0)  # 60s total, 10s connect
)
```

### Environment Setup

#### Required .env File
Create a `.env` file in the project root:
```
OPENAI_API_KEY=sk-your-key-here
```

#### Test Your Setup
```bash
# Navigate to project directory
cd level-3-code/large_scale_classification

# Load environment
source .env  # or use `export OPENAI_API_KEY=your-key`

# Test a single classification
python -c "
from src.classification.pipeline import ClassificationPipeline
pipeline = ClassificationPipeline()
result = pipeline.classify('Samsung refrigerator')
print(f'Classification: {result.category.path}')
"
```

### GUI-Specific Solutions

#### 1. Use Sample Tests
- Click "🔬 Run Sample" instead of "🚀 Run Full Suite"
- This runs only a few test cases to check connectivity
- Faster failure detection

#### 2. Analyze Existing Results
- The GUI automatically looks for existing test results
- Click "📂 Load Latest Results" to load previous runs
- You can analyze past results while troubleshooting API issues

#### 3. Custom Testing Fallback
- Custom testing in the GUI uses the same API
- If it fails, you'll get user-friendly error messages
- Try again after resolving connectivity issues

### Advanced Debugging

#### Enable Debug Logging
Add this to your code to see detailed HTTP requests:
```python
import logging
import httpx

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.DEBUG)
```

#### Check System Resources
```bash
# Check if system is under heavy load
top
htop  # if available

# Check network interface
ifconfig  # or ip addr on Linux
```

#### Test with Different Models
Try switching to a different embedding model in `src/config/settings.py`:
```python
embedding_model: str = "text-embedding-ada-002"  # Older, might be more stable
```

### Getting Help

#### Check Service Status
- OpenAI Status: https://status.openai.com/
- Your network status: https://fast.com/ (speed test)

#### Contact Support
If issues persist:
1. **Document the error**: Copy the full error message
2. **Note timing**: When did it start happening?
3. **Test environment**: Try from different networks/devices
4. **Check billing**: Ensure your OpenAI account has available credits

### Prevention

#### Best Practices
1. **Use existing results** when possible for analysis
2. **Run sample tests** before full test suites
3. **Monitor API usage** to avoid rate limits
4. **Keep backups** of successful test results
5. **Set up monitoring** for API connectivity

#### Robust Configuration
```python
# Example robust OpenAI client setup
import httpx
from openai import OpenAI

client = OpenAI(
    timeout=httpx.Timeout(
        timeout=60.0,      # Total timeout
        connect=10.0,      # Connection timeout
        read=45.0,         # Read timeout
        write=10.0         # Write timeout
    ),
    max_retries=3          # Retry failed requests
)
```
