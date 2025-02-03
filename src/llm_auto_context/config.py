"""Configuration handling for code snapshot generation."""

from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

class SnapshotConfig(BaseModel):
    """Configuration model for code snapshot generation."""
    
    directories: List[str] = Field(
        default=["src"],
        description="List of directories to scan for code files"
    )
    output_file: str = Field(
        default="code_snapshot.txt",
        description="Path to output file"
    )
    include_extensions: List[str] = Field(
        default=[".swift", ".py", ".js"],
        description="File extensions to include"
    )
    exclude_dirs: List[str] = Field(
        default=["node_modules", ".git", "build"],
        description="Directories to exclude"
    )
    exclude_files: List[str] = Field(
        default=[],
        description="Specific files to exclude"
    )

    @field_validator("output_file")
    def validate_output_file(cls, v: str) -> str:
        """Validate output file path."""
        if not v:
            raise ValueError("Output file path cannot be empty")
        return v

    @field_validator("directories")
    def validate_directories(cls, v: List[str]) -> List[str]:
        """Validate directories list."""
        if not v:
            raise ValueError("At least one directory must be specified")
        return v

    def get_output_path(self, base_dir: Optional[Path] = None) -> Path:
        """Get absolute output path, optionally relative to base_dir."""
        path = Path(self.output_file)
        if base_dir and not path.is_absolute():
            path = base_dir / path
        return path.resolve()

    class Config:
        json_schema_extra = {
            "example": {
                "directories": ["src", "lib"],
                "output_file": "snapshot.md",
                "include_extensions": [".py", ".js", ".ts"],
                "exclude_dirs": ["node_modules", ".git"],
                "exclude_files": ["secrets.env"]
            }
        } 