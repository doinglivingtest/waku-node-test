# Waku Node Test Automation Framework

Test automation framework for testing Waku nodes using Python, Pytest, Docker, and Allure reporting.

## 🏗️ Architecture

This framework follows industry best practices with a clean, maintainable architecture:

```
waku-test-automation/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── pytest.ini                        # Pytest configuration
├── conftest.py                       # Pytest fixtures and setup
├── config/
│   ├── __init__.py
│   └── settings.py                   # Configuration management
├── framework/
│   ├── __init__.py
│   ├── docker_manager.py            # Docker container management
│   ├── waku_client.py               # Waku REST API client
│   └── utils.py                     # Utility functions
├── tests/
│   ├── __init__.py
│   ├── test_basic_node_operation.py      # Test Suite 1
│   └── test_inter_node_communication.py  # Test Suite 2
└── reports/                         # Test reports directory
```

## 🎯 Features

- **Clean Architecture**: Separation of concerns with dedicated modules
- **Configuration Management**: Centralized settings with environment variable support
- **Docker Integration**: Automated container and network management
- **Retry Mechanisms**: Robust error handling with exponential backoff
- **Comprehensive Logging**: Detailed logging for debugging and monitoring
- **Allure Reporting**: Rich HTML reports with step-by-step execution details
- **Parallel Execution**: Support for parallel test execution
- **Fixture Management**: Proper setup/teardown with pytest fixtures

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Docker Desktop
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd waku-node-test
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Allure (for reporting):**

   **macOS:**
   ```bash
   brew install allure
   ```

   **Windows (using Scoop):**
   ```bash
   scoop install allure
   ```

   **Linux:**
   ```bash
   curl -o allure-2.13.2.tgz -Ls https://repo.maven.apache.org/maven2/io/qameta/allure/allure-commandline/2.13.2/allure-commandline-2.13.2.tgz
   sudo tar -zxf allure-2.13.2.tgz -C /opt/
   sudo ln -s /opt/allure-2.13.2/bin/allure /usr/bin/allure
   ```

## 🧪 Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test Suite
```bash
# Basic node operations (Test Suite 1)
pytest tests/test_basic_node_operation.py -v

# Inter-node communication (Test Suite 2)
pytest tests/test_inter_node_communication.py -v
```

### Run Tests by Markers
```bash
# Run only smoke tests
pytest -m smoke

# Run only basic functionality tests
pytest -m basic

# Run advanced tests
pytest -m advanced

# Skip slow tests
pytest -m "not slow"
```

### Parallel Execution
```bash
# Run tests in parallel (4 workers)
pytest -n 4
```

### Generate Reports
```bash
# Run tests with Allure reporting
pytest --alluredir=reports/allure-results

# Generate and serve Allure report
allure serve reports/allure-results
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root to override default settings:

```bash
# Docker settings
DOCKER_IMAGE=wakuorg/nwaku:v0.24.0
DOCKER_NETWORK_NAME=waku
DOCKER_NETWORK_SUBNET=172.18.0.0/16

# Node IPs
NODE1_IP=172.18.111.225
NODE2_IP=172.18.111.226

# Timeouts (seconds)