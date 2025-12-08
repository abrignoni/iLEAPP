# Cross-platform iLEAPP Makefile
.PHONY: env install run run-cli test-parser lint format clean help

PYTHON ?= python
VENV_DIR := .venv
REQUIREMENTS := requirements.txt

# ==========================================
# Platform-specific Paths (Hanya untuk lokasi file)
# ==========================================
ifeq ($(OS),Windows_NT)
    # Windows Paths
    VENV_BIN := $(VENV_DIR)/Scripts
    PIP := $(VENV_BIN)/pip.exe
    PYTHON_VENV := $(VENV_BIN)/python.exe
else
    # Unix/Linux Paths
    VENV_BIN := $(VENV_DIR)/bin
    PIP := $(VENV_BIN)/pip
    PYTHON_VENV := $(VENV_BIN)/python
endif

# Development Tools
BLACK := $(VENV_BIN)/black
ISORT := $(VENV_BIN)/isort
FLAKE8 := $(VENV_BIN)/flake8

# ==========================================
# Targets
# ==========================================

# 1. Create virtual environment (Menggunakan Python agar cross-shell aman)
env:
	@echo "🔍 Checking virtual environment..."
	@$(PYTHON) -c "import os, venv; venv.create('$(VENV_DIR)', with_pip=True) if not os.path.exists('$(VENV_DIR)') else print('✅ Virtual environment already exists.')"

# 2. Install dependencies
install:
	@echo "📦 Checking pip..."
	@$(PYTHON_VENV) -m pip install --upgrade pip
	@echo "📦 Installing iLEAPP dependencies..."
	@$(PIP) install -r $(REQUIREMENTS)
	@echo "🛠️  Installing dev tools..."
	@$(PIP) install black isort flake8

# 3. Run iLEAPP GUI
run:
	@echo "🚀 Running iLEAPP GUI..."
	@$(PYTHON_VENV) ileappGUI.py

# 4. Run iLEAPP CLI Help
run-cli:
	@echo "🚀 Running iLEAPP CLI Help..."
	@$(PYTHON_VENV) ileapp.py --help

# 5. Test Specific Parser
# Usage: make test-parser IN=./input OUT=./output ART=Name
IN ?= ./input_data
OUT ?= ./output_report
ART ?= *
test-parser:
	@echo "🧪 Testing Artifact: $(ART)"
	@echo "📂 Input: $(IN)"
	@echo "📄 Output: $(OUT)"
	@$(PYTHON) -c "import os; os.makedirs('$(OUT)', exist_ok=True)"
	@$(PYTHON_VENV) ileapp.py --input_path "$(IN)" --output_path "$(OUT)" --artifact "$(ART)" --t

# 6. Formatting Code
format:
	@echo "✨ Formatting code..."
	@$(ISORT) scripts/artifacts/
	@$(BLACK) scripts/artifacts/

# 7. Linting
lint:
	@echo "🔍 Linting..."
	@$(FLAKE8) scripts/artifacts/ --count --select=E9,F63,F7,F82 --show-source --statistics
	@$(FLAKE8) scripts/artifacts/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

# 8. Clean up (Menggunakan Python agar aman di CMD maupun Bash)
clean:
	@echo "🧹 Cleaning up..."
	@$(PYTHON) -c "import shutil, os; shutil.rmtree('$(VENV_DIR)', ignore_errors=True); shutil.rmtree('__pycache__', ignore_errors=True); shutil.rmtree('.pytest_cache', ignore_errors=True)"
	@echo "✨ Clean."

# Help message
help:
	@echo "iLEAPP Helper Makefile"
	@echo "----------------------"
	@echo " make env          : Create python virtual environment"
	@echo " make install      : Install requirements inside venv"
	@echo " make run          : Run iLEAPP GUI"
	@echo " make test-parser  : Run CLI test (Usage: make test-parser IN=... OUT=... ART=...)"
	@echo " make format       : Auto-format code"
	@echo " make clean        : Remove venv and caches"

.DEFAULT_GOAL := help