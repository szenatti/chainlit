"""
Configuration Loader for Dynamic Chainlit Application

This module provides configuration loading and management for the dynamic
Chainlit application with YAML-based configuration.
"""

import os
import yaml
import logging
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass, field
import copy

logger = logging.getLogger(__name__)

@dataclass
class ProfileConfig:
    """Configuration for a chat profile"""
    name: str
    markdown_description: str
    icon: str
    temperature: float
    system_prompt: str
    enabled: bool = True
    requires_role: Optional[str] = None
    requires_promptflow: bool = False
    supports_file_upload: bool = False
    flow_config: Optional[Dict[str, Any]] = None
    model_settings: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AuthConfig:
    """Configuration for authentication"""
    enabled: bool = True
    auth_type: str = "password"
    session_timeout: int = 3600
    require_auth_for_all_profiles: bool = False
    users: Dict[str, Any] = field(default_factory=dict)
    roles: Dict[str, Any] = field(default_factory=dict)
    security: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PromptflowConfig:
    """Configuration for promptflows"""
    promptflows: Dict[str, Any] = field(default_factory=dict)
    connections: Dict[str, Any] = field(default_factory=dict)
    execution: Dict[str, Any] = field(default_factory=dict)
    file_upload: Dict[str, Any] = field(default_factory=dict)

class ConfigLoader:
    """Configuration loader and manager"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.profiles_config: Dict[str, ProfileConfig] = {}
        self.auth_config: Optional[AuthConfig] = None
        self.promptflow_config: Optional[PromptflowConfig] = None
        self.settings: Dict[str, Any] = {}
        
        # Load all configurations
        self.load_all_configs()
    
    def load_all_configs(self):
        """Load all configuration files"""
        try:
            self.load_profiles_config()
            self.load_auth_config()
            self.load_promptflow_config()
            logger.info("All configurations loaded successfully")
        except Exception as e:
            logger.error(f"Error loading configurations: {e}")
            raise
    
    def load_yaml_file(self, filename: str) -> Dict[str, Any]:
        """Load a YAML configuration file"""
        file_path = self.config_dir / filename
        if not file_path.exists():
            logger.warning(f"Configuration file not found: {file_path}")
            return {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = yaml.safe_load(file)
                return content or {}
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML file {filename}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error reading file {filename}: {e}")
            raise
    
    def load_profiles_config(self):
        """Load chat profiles configuration"""
        config = self.load_yaml_file("profiles.yaml")
        
        # Load regular profiles
        profiles = config.get("profiles", {})
        for profile_name, profile_data in profiles.items():
            self.profiles_config[profile_name] = ProfileConfig(**profile_data)
        
        # Load promptflow profiles
        promptflow_profiles = config.get("promptflow_profiles", {})
        for profile_name, profile_data in promptflow_profiles.items():
            profile_data["requires_promptflow"] = True
            self.profiles_config[profile_name] = ProfileConfig(**profile_data)
        
        # Store global settings
        self.settings.update(config.get("settings", {}))
        
        logger.info(f"Loaded {len(self.profiles_config)} profiles")
    
    def load_auth_config(self):
        """Load authentication configuration"""
        config = self.load_yaml_file("auth.yaml")
        
        auth_settings = config.get("auth", {})
        users = config.get("users", {})
        roles = config.get("roles", {})
        security = config.get("security", {})
        
        self.auth_config = AuthConfig(
            enabled=auth_settings.get("enabled", True),
            auth_type=auth_settings.get("auth_type", "password"),
            session_timeout=auth_settings.get("session_timeout", 3600),
            require_auth_for_all_profiles=auth_settings.get("require_auth_for_all_profiles", False),
            users=users,
            roles=roles,
            security=security
        )
        
        logger.info(f"Loaded authentication config with {len(users)} users and {len(roles)} roles")
    
    def load_promptflow_config(self):
        """Load promptflow configuration"""
        config = self.load_yaml_file("promptflows.yaml")
        
        self.promptflow_config = PromptflowConfig(
            promptflows=config.get("promptflows", {}),
            connections=config.get("connections", {}),
            execution=config.get("execution", {}),
            file_upload=config.get("file_upload", {})
        )
        
        logger.info(f"Loaded promptflow config with {len(self.promptflow_config.promptflows)} flows")
    
    def get_profile_config(self, profile_name: str) -> Optional[ProfileConfig]:
        """Get configuration for a specific profile"""
        return self.profiles_config.get(profile_name)
    
    def get_all_profiles(self) -> Dict[str, ProfileConfig]:
        """Get all profile configurations"""
        return self.profiles_config.copy()
    
    def get_enabled_profiles(self) -> Dict[str, ProfileConfig]:
        """Get only enabled profile configurations"""
        return {name: config for name, config in self.profiles_config.items() if config.enabled}
    
    def get_profiles_for_user(self, user_role: Optional[str] = None, has_promptflow: bool = False) -> Dict[str, ProfileConfig]:
        """Get profiles available for a specific user role"""
        available_profiles = {}
        
        for name, config in self.profiles_config.items():
            # Skip disabled profiles
            if not config.enabled:
                continue
            
            # Check role requirements
            if config.requires_role and user_role != config.requires_role:
                continue
            
            # Check promptflow requirements
            if config.requires_promptflow and not has_promptflow:
                continue
            
            available_profiles[name] = config
        
        return available_profiles
    
    def get_auth_config(self) -> Optional[AuthConfig]:
        """Get authentication configuration"""
        return self.auth_config
    
    def get_promptflow_config(self) -> Optional[PromptflowConfig]:
        """Get promptflow configuration"""
        return self.promptflow_config
    
    def get_user_config(self, username: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific user"""
        if not self.auth_config:
            return None
        return self.auth_config.users.get(username)
    
    def get_role_config(self, role: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific role"""
        if not self.auth_config:
            return None
        return self.auth_config.roles.get(role)
    
    def validate_user_credentials(self, username: str, password: str) -> bool:
        """Validate user credentials"""
        if not self.auth_config or not self.auth_config.enabled:
            return True
        
        user_config = self.get_user_config(username)
        if not user_config:
            return False
        
        if not user_config.get("enabled", True):
            return False
        
        return user_config.get("password") == password
    
    def get_user_role(self, username: str) -> Optional[str]:
        """Get role for a specific user"""
        user_config = self.get_user_config(username)
        if user_config:
            return user_config.get("role")
        return None
    
    def get_user_metadata(self, username: str) -> Dict[str, Any]:
        """Get metadata for a specific user"""
        user_config = self.get_user_config(username)
        if user_config:
            return user_config.get("metadata", {})
        return {}
    
    def get_flow_config(self, flow_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific promptflow"""
        if not self.promptflow_config:
            return None
        return self.promptflow_config.promptflows.get(flow_name)
    
    def get_connection_config(self, connection_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific connection"""
        if not self.promptflow_config:
            return None
        return self.promptflow_config.connections.get(connection_name)
    
    def expand_environment_variables(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Expand environment variables in configuration values"""
        expanded_config = copy.deepcopy(config)
        
        def expand_value(value):
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                return os.getenv(env_var, value)
            elif isinstance(value, dict):
                return {k: expand_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [expand_value(item) for item in value]
            return value
        
        return expand_value(expanded_config)
    
    def reload_configs(self):
        """Reload all configuration files"""
        logger.info("Reloading all configurations")
        self.profiles_config.clear()
        self.auth_config = None
        self.promptflow_config = None
        self.settings.clear()
        self.load_all_configs()

# Global configuration instance
_config_loader: Optional[ConfigLoader] = None

def get_config_loader() -> ConfigLoader:
    """Get the global configuration loader instance"""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader

def reload_config():
    """Reload the global configuration"""
    global _config_loader
    if _config_loader:
        _config_loader.reload_configs()
    else:
        _config_loader = ConfigLoader() 