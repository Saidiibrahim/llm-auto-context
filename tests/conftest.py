"""Shared test fixtures."""

import json
from pathlib import Path

import pytest

@pytest.fixture
def test_files(tmp_path):
    """Create test files and directories for testing."""
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    
    # Create test files
    (src_dir / "test.py").write_text("print('test')")
    (src_dir / "test2.py").write_text("print('test2')")
    (src_dir / "test.txt").write_text("not included")
    
    # Create excluded directory
    excluded_dir = src_dir / "__pycache__"
    excluded_dir.mkdir()
    (excluded_dir / "cache.py").write_text("print('cache')")
    
    return tmp_path

@pytest.fixture
def config_file(tmp_path):
    """Create a sample config file."""
    config = {
        "directories": ["src"],
        "output_file": "snapshot.md",
        "include_extensions": [".py"],
        "exclude_dirs": ["__pycache__"],
        "exclude_files": []
    }
    config_path = tmp_path / ".codesnapshot.json"
    config_path.write_text(json.dumps(config))
    return config_path 