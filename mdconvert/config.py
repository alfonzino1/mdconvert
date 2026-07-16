"""
Configuration management.
"""

import os
import yaml
from pathlib import Path
from typing import Optional


DEFAULT_CONFIG = {
    'format': 'claude',
    'smart': True,
    'copy': False,
    'stats': True,
    'output_dir': None,
    'template_dir': None,
}


class Config:
    """Configuration handler."""
    
    def __init__(self):
        self.config = DEFAULT_CONFIG.copy()
        self.config_path = self._find_config()
        
        if self.config_path:
            self._load()
    
    def _find_config(self) -> Optional[Path]:
        """Find config file."""
        paths = [
            Path.cwd() / '.mdconvert.yaml',
            Path.cwd() / '.mdconvert.yml',
            Path.home() / '.config' / 'mdconvert' / 'config.yaml',
            Path.home() / '.mdconvert.yaml',
        ]
        
        for path in paths:
            if path.exists():
                return path
        
        return None
    
    def _load(self):
        """Load config from file."""
        try:
            with open(self.config_path) as f:
                user_config = yaml.safe_load(f)
                if user_config:
                    self.config.update(user_config)
        except Exception:
            pass
    
    def get(self, key: str, default=None):
        """Get config value."""
        return self.config.get(key, default)
    
    def save(self, path: Optional[Path] = None):
        """Save config to file."""
        target = path or Path.cwd() / '.mdconvert.yaml'
        with open(target, 'w') as f:
            yaml.dump(self.config, f)