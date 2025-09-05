"""
Configuration Manager Module

This module handles configuration management including
loading, validation, and access to bot settings.
"""

import os
import yaml
import json
import logging
from typing import Dict, Any, Optional, Union
from pathlib import Path


class ConfigManager:
    """
    Manages configuration settings for the trading bot.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to configuration file
        """
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path or "config/config.yaml"
        self.config = {}
        self.default_config = self._get_default_config()
        
        # Load configuration
        self.load_config()
    
    def load_config(self) -> bool:
        """
        Load configuration from file.
        
        Returns:
            True if loading successful
        """
        try:
            config_file = Path(self.config_path)
            
            if not config_file.exists():
                self.logger.warning(f"Config file {self.config_path} not found, using defaults")
                self.config = self.default_config.copy()
                return True
            
            # Load YAML config
            with open(config_file, 'r', encoding='utf-8') as f:
                file_config = yaml.safe_load(f)
            
            # Merge with defaults
            self.config = self._merge_configs(self.default_config, file_config or {})
            
            # Validate configuration
            if self._validate_config():
                self.logger.info(f"Configuration loaded from {self.config_path}")
                return True
            else:
                self.logger.error("Configuration validation failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            self.config = self.default_config.copy()
            return False
    
    def save_config(self, config_path: str = None) -> bool:
        """
        Save current configuration to file.
        
        Args:
            config_path: Path to save configuration
            
        Returns:
            True if saving successful
        """
        try:
            save_path = config_path or self.config_path
            config_dir = Path(save_path).parent
            
            # Create directory if it doesn't exist
            config_dir.mkdir(parents=True, exist_ok=True)
            
            # Save as YAML
            with open(save_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, indent=2)
            
            self.logger.info(f"Configuration saved to {save_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        try:
            keys = key.split('.')
            value = self.config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
            
        except Exception as e:
            self.logger.error(f"Error getting config key {key}: {e}")
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """
        Set configuration value by key.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
            
        Returns:
            True if setting successful
        """
        try:
            keys = key.split('.')
            config = self.config
            
            # Navigate to parent level
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            # Set value at leaf level
            config[keys[-1]] = value
            
            self.logger.debug(f"Set config key {key} = {value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting config key {key}: {e}")
            return False
    
    def has(self, key: str) -> bool:
        """
        Check if configuration key exists.
        
        Args:
            key: Configuration key (supports dot notation)
            
        Returns:
            True if key exists
        """
        try:
            keys = key.split('.')
            value = self.config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get entire configuration section.
        
        Args:
            section: Section name
            
        Returns:
            Configuration section dictionary
        """
        return self.get(section, {})
    
    def update_section(self, section: str, updates: Dict[str, Any]) -> bool:
        """
        Update configuration section.
        
        Args:
            section: Section name
            updates: Updates to apply
            
        Returns:
            True if update successful
        """
        try:
            current_section = self.get_section(section)
            current_section.update(updates)
            return self.set(section, current_section)
            
        except Exception as e:
            self.logger.error(f"Error updating config section {section}: {e}")
            return False
    
    def reload(self) -> bool:
        """
        Reload configuration from file.
        
        Returns:
            True if reload successful
        """
        return self.load_config()
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get entire configuration.
        
        Returns:
            Complete configuration dictionary
        """
        return self.config.copy()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            'bot': {
                'name': 'Claude Code Trading Bot',
                'version': '2.0.0',
                'environment': 'development',
                'debug': True,
                'log_level': 'INFO'
            },
            'ai': {
                'claude_api_key': '',
                'openai_api_key': '',
                'max_concurrent_strategies': 5,
                'strategy_generation_enabled': True,
                'optimization_enabled': True
            },
            'trading': {
                'enabled': False,
                'paper_trading': True,
                'max_positions': 10,
                'default_risk_per_trade': 0.01,
                'max_portfolio_risk': 0.05
            },
            'data': {
                'sources': ['binance', 'coinbase'],
                'update_interval': 60,
                'cache_duration': 300,
                'max_data_points': 10000
            },
            'database': {
                'type': 'sqlite',
                'path': 'data/trading_bot.db',
                'backup_enabled': True,
                'backup_interval': 86400
            },
            'logging': {
                'file_enabled': True,
                'file_path': 'logs/trading_bot.log',
                'max_file_size': 10485760,
                'backup_count': 5
            },
            'api': {
                'enabled': True,
                'host': 'localhost',
                'port': 8000,
                'debug': True
            }
        }
    
    def _merge_configs(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Merge user configuration with defaults."""
        merged = default.copy()
        
        def merge_dict(base: Dict[str, Any], override: Dict[str, Any]):
            for key, value in override.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dict(base[key], value)
                else:
                    base[key] = value
        
        merge_dict(merged, user)
        return merged
    
    def _validate_config(self) -> bool:
        """Validate configuration values."""
        try:
            # Check required fields
            required_fields = [
                'bot.name',
                'bot.version',
                'ai.claude_api_key'
            ]
            
            for field in required_fields:
                if not self.has(field) or not self.get(field):
                    self.logger.error(f"Required config field missing: {field}")
                    return False
            
            # Validate numeric fields
            numeric_fields = [
                ('trading.max_positions', 1, 100),
                ('trading.default_risk_per_trade', 0.001, 0.1),
                ('trading.max_portfolio_risk', 0.01, 0.5),
                ('data.update_interval', 1, 3600)
            ]
            
            for field, min_val, max_val in numeric_fields:
                value = self.get(field)
                if value is not None and (value < min_val or value > max_val):
                    self.logger.error(f"Config field {field} value {value} out of range [{min_val}, {max_val}]")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Configuration validation error: {e}")
            return False
    
    def export_json(self, file_path: str) -> bool:
        """
        Export configuration to JSON file.
        
        Args:
            file_path: Path to export file
            
        Returns:
            True if export successful
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, default=str)
            
            self.logger.info(f"Configuration exported to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting configuration: {e}")
            return False
