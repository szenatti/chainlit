"""
Configuration Validator

This module provides validation utilities for YAML configuration files.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import os

from .config_loader import ConfigLoader, ProfileConfig, AuthConfig, PromptflowConfig

logger = logging.getLogger(__name__)

class ConfigValidator:
    """Configuration validator for YAML files"""
    
    def __init__(self, config_loader: ConfigLoader):
        self.config_loader = config_loader
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_all(self) -> Tuple[bool, List[str], List[str]]:
        """
        Validate all configurations
        
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors.clear()
        self.warnings.clear()
        
        try:
            self.validate_profiles()
            self.validate_auth()
            self.validate_promptflows()
            self.validate_cross_references()
            
            is_valid = len(self.errors) == 0
            return is_valid, self.errors.copy(), self.warnings.copy()
            
        except Exception as e:
            self.errors.append(f"Validation error: {str(e)}")
            return False, self.errors.copy(), self.warnings.copy()
    
    def validate_profiles(self):
        """Validate profile configurations"""
        profiles = self.config_loader.get_all_profiles()
        
        if not profiles:
            self.errors.append("No profiles configured")
            return
        
        # Check for default profile
        default_profile = self.config_loader.settings.get("default_profile")
        if default_profile and default_profile not in profiles:
            self.errors.append(f"Default profile '{default_profile}' not found in profiles")
        
        # Validate each profile
        for profile_name, profile_config in profiles.items():
            self._validate_profile(profile_name, profile_config)
    
    def _validate_profile(self, profile_name: str, profile_config: ProfileConfig):
        """Validate a single profile"""
        # Required fields
        if not profile_config.name:
            self.errors.append(f"Profile '{profile_name}': name is required")
        
        if not profile_config.markdown_description:
            self.errors.append(f"Profile '{profile_name}': markdown_description is required")
        
        if not profile_config.system_prompt:
            self.errors.append(f"Profile '{profile_name}': system_prompt is required")
        
        # Validate temperature
        if not (0.0 <= profile_config.temperature <= 2.0):
            self.errors.append(f"Profile '{profile_name}': temperature must be between 0.0 and 2.0")
        
        # Validate icon path
        if profile_config.icon:
            if profile_config.icon.startswith("/public/"):
                icon_path = profile_config.icon[8:]  # Remove /public/
                full_path = Path("public") / icon_path
                if not full_path.exists():
                    self.warnings.append(f"Profile '{profile_name}': icon file not found: {full_path}")
        
        # Validate role requirements
        if profile_config.requires_role:
            auth_config = self.config_loader.get_auth_config()
            if auth_config and profile_config.requires_role not in auth_config.roles:
                self.errors.append(f"Profile '{profile_name}': required role '{profile_config.requires_role}' not defined in auth config")
        
        # Validate promptflow configuration
        if profile_config.requires_promptflow:
            if not profile_config.flow_config:
                self.errors.append(f"Profile '{profile_name}': requires_promptflow is true but no flow_config provided")
            else:
                self._validate_profile_flow_config(profile_name, profile_config.flow_config)
        
        # Validate model settings
        if profile_config.model_settings:
            self._validate_model_settings(profile_name, profile_config.model_settings)
    
    def _validate_profile_flow_config(self, profile_name: str, flow_config: Dict[str, Any]):
        """Validate flow configuration for a profile"""
        if "flow_path" not in flow_config:
            self.errors.append(f"Profile '{profile_name}': flow_config missing flow_path")
            return
        
        flow_path = flow_config["flow_path"]
        if not Path(flow_path).exists():
            self.errors.append(f"Profile '{profile_name}': flow_path does not exist: {flow_path}")
        
        if "flow_type" not in flow_config:
            self.warnings.append(f"Profile '{profile_name}': flow_config missing flow_type")
    
    def _validate_model_settings(self, profile_name: str, model_settings: Dict[str, Any]):
        """Validate model settings for a profile"""
        if "max_tokens" in model_settings:
            max_tokens = model_settings["max_tokens"]
            if not isinstance(max_tokens, int) or max_tokens <= 0:
                self.errors.append(f"Profile '{profile_name}': max_tokens must be a positive integer")
        
        if "top_p" in model_settings:
            top_p = model_settings["top_p"]
            if not isinstance(top_p, (int, float)) or not (0.0 <= top_p <= 1.0):
                self.errors.append(f"Profile '{profile_name}': top_p must be between 0.0 and 1.0")
    
    def validate_auth(self):
        """Validate authentication configuration"""
        auth_config = self.config_loader.get_auth_config()
        
        if not auth_config:
            self.warnings.append("No authentication configuration found")
            return
        
        # Validate auth type
        valid_auth_types = ["password", "oauth", "ldap", "custom"]
        if auth_config.auth_type not in valid_auth_types:
            self.errors.append(f"Invalid auth_type: {auth_config.auth_type}. Must be one of: {valid_auth_types}")
        
        # Validate session timeout
        if auth_config.session_timeout <= 0:
            self.errors.append("session_timeout must be positive")
        
        # Validate users
        if auth_config.enabled and auth_config.auth_type == "password":
            if not auth_config.users:
                self.errors.append("Password authentication enabled but no users configured")
            else:
                self._validate_users(auth_config.users)
        
        # Validate roles
        if auth_config.roles:
            self._validate_roles(auth_config.roles)
    
    def _validate_users(self, users: Dict[str, Any]):
        """Validate user configurations"""
        for username, user_config in users.items():
            if not isinstance(user_config, dict):
                self.errors.append(f"User '{username}': configuration must be a dictionary")
                continue
            
            if "password" not in user_config:
                self.errors.append(f"User '{username}': password is required")
            
            if "role" not in user_config:
                self.errors.append(f"User '{username}': role is required")
            
            # Check if role exists
            auth_config = self.config_loader.get_auth_config()
            if auth_config and user_config.get("role") not in auth_config.roles:
                self.errors.append(f"User '{username}': role '{user_config.get('role')}' not defined")
    
    def _validate_roles(self, roles: Dict[str, Any]):
        """Validate role configurations"""
        for role_name, role_config in roles.items():
            if not isinstance(role_config, dict):
                self.errors.append(f"Role '{role_name}': configuration must be a dictionary")
                continue
            
            if "description" not in role_config:
                self.warnings.append(f"Role '{role_name}': description is recommended")
            
            if "permissions" not in role_config:
                self.warnings.append(f"Role '{role_name}': permissions not defined")
            
            if "profile_access" not in role_config:
                self.warnings.append(f"Role '{role_name}': profile_access not defined")
    
    def validate_promptflows(self):
        """Validate promptflow configurations"""
        promptflow_config = self.config_loader.get_promptflow_config()
        
        if not promptflow_config:
            self.warnings.append("No promptflow configuration found")
            return
        
        # Validate flows
        for flow_name, flow_config in promptflow_config.promptflows.items():
            self._validate_flow(flow_name, flow_config)
        
        # Validate connections
        for conn_name, conn_config in promptflow_config.connections.items():
            self._validate_connection(conn_name, conn_config)
        
        # Validate execution settings
        if promptflow_config.execution:
            self._validate_execution_settings(promptflow_config.execution)
    
    def _validate_flow(self, flow_name: str, flow_config: Dict[str, Any]):
        """Validate a promptflow configuration"""
        required_fields = ["name", "description", "flow_path"]
        for field in required_fields:
            if field not in flow_config:
                self.errors.append(f"Flow '{flow_name}': {field} is required")
        
        # Check if flow path exists
        if "flow_path" in flow_config:
            flow_path = Path(flow_config["flow_path"])
            if not flow_path.exists():
                self.errors.append(f"Flow '{flow_name}': flow_path does not exist: {flow_path}")
            
            # Check for flow.dag.yaml
            flow_file = flow_config.get("flow_file", "flow.dag.yaml")
            if not (flow_path / flow_file).exists():
                self.errors.append(f"Flow '{flow_name}': flow file not found: {flow_path / flow_file}")
        
        # Validate inputs and outputs
        if "inputs" in flow_config:
            self._validate_flow_inputs(flow_name, flow_config["inputs"])
        
        if "outputs" in flow_config:
            self._validate_flow_outputs(flow_name, flow_config["outputs"])
    
    def _validate_flow_inputs(self, flow_name: str, inputs: List[Dict[str, Any]]):
        """Validate flow inputs"""
        for i, input_config in enumerate(inputs):
            if "name" not in input_config:
                self.errors.append(f"Flow '{flow_name}': input {i} missing name")
            
            if "type" not in input_config:
                self.errors.append(f"Flow '{flow_name}': input {i} missing type")
    
    def _validate_flow_outputs(self, flow_name: str, outputs: List[Dict[str, Any]]):
        """Validate flow outputs"""
        for i, output_config in enumerate(outputs):
            if "name" not in output_config:
                self.errors.append(f"Flow '{flow_name}': output {i} missing name")
            
            if "type" not in output_config:
                self.errors.append(f"Flow '{flow_name}': output {i} missing type")
    
    def _validate_connection(self, conn_name: str, conn_config: Dict[str, Any]):
        """Validate a connection configuration"""
        if "type" not in conn_config:
            self.errors.append(f"Connection '{conn_name}': type is required")
        
        # Validate Azure OpenAI connections
        if conn_config.get("type") == "AzureOpenAI":
            required_fields = ["api_base", "api_key", "api_version"]
            for field in required_fields:
                if field not in conn_config:
                    self.errors.append(f"Connection '{conn_name}': {field} is required for AzureOpenAI")
    
    def _validate_execution_settings(self, execution_config: Dict[str, Any]):
        """Validate execution settings"""
        if "max_parallel_runs" in execution_config:
            max_runs = execution_config["max_parallel_runs"]
            if not isinstance(max_runs, int) or max_runs <= 0:
                self.errors.append("max_parallel_runs must be a positive integer")
        
        if "timeout_seconds" in execution_config:
            timeout = execution_config["timeout_seconds"]
            if not isinstance(timeout, int) or timeout <= 0:
                self.errors.append("timeout_seconds must be a positive integer")
    
    def validate_cross_references(self):
        """Validate cross-references between configurations"""
        # Check if promptflow profiles reference valid flows
        profiles = self.config_loader.get_all_profiles()
        promptflow_config = self.config_loader.get_promptflow_config()
        
        if not promptflow_config:
            return
        
        available_flows = set(promptflow_config.promptflows.keys())
        
        for profile_name, profile_config in profiles.items():
            if profile_config.requires_promptflow and profile_config.flow_config:
                flow_type = profile_config.flow_config.get("flow_type")
                if flow_type and flow_type not in available_flows:
                    self.errors.append(f"Profile '{profile_name}': references unknown flow type '{flow_type}'")
    
    def validate_environment_variables(self) -> List[str]:
        """Validate required environment variables"""
        missing_vars = []
        
        # Check for Azure OpenAI variables
        required_vars = [
            "AZURE_OPENAI_API_KEY",
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_DEPLOYMENT_NAME"
        ]
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        return missing_vars

def validate_configuration(config_dir: str = "config") -> Tuple[bool, List[str], List[str]]:
    """
    Validate configuration files
    
    Args:
        config_dir: Directory containing configuration files
        
    Returns:
        Tuple of (is_valid, errors, warnings)
    """
    try:
        config_loader = ConfigLoader(config_dir)
        validator = ConfigValidator(config_loader)
        return validator.validate_all()
    except Exception as e:
        return False, [f"Configuration loading failed: {str(e)}"], []

if __name__ == "__main__":
    # Command-line validation
    import sys
    
    config_dir = sys.argv[1] if len(sys.argv) > 1 else "config"
    
    is_valid, errors, warnings = validate_configuration(config_dir)
    
    print(f"Configuration validation: {'✅ PASSED' if is_valid else '❌ FAILED'}")
    
    if warnings:
        print(f"\n⚠️  Warnings ({len(warnings)}):")
        for warning in warnings:
            print(f"  - {warning}")
    
    if errors:
        print(f"\n❌ Errors ({len(errors)}):")
        for error in errors:
            print(f"  - {error}")
    
    sys.exit(0 if is_valid else 1) 