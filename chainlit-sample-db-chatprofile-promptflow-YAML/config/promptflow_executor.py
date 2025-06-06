"""
Dynamic Promptflow Executor

This module provides dynamic execution of promptflows based on YAML configuration.
"""

import os
import sys
import importlib
import logging
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import asyncio
from openai import AsyncAzureOpenAI

from .config_loader import get_config_loader, PromptflowConfig

logger = logging.getLogger(__name__)

class PromptflowExecutor:
    """Dynamic promptflow executor"""
    
    def __init__(self):
        self.config_loader = get_config_loader()
        self.client: Optional[AsyncAzureOpenAI] = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Azure OpenAI client"""
        try:
            # Get connection configuration
            connection_config = self.config_loader.get_connection_config("Default_AzureOpenAI")
            if not connection_config:
                logger.warning("No Azure OpenAI connection configuration found")
                return
            
            # Expand environment variables
            expanded_config = self.config_loader.expand_environment_variables(connection_config)
            
            self.client = AsyncAzureOpenAI(
                api_key=expanded_config.get("api_key"),
                api_version=expanded_config.get("api_version", "2023-05-15"),
                azure_endpoint=expanded_config.get("api_base")
            )
            logger.info("Azure OpenAI client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI client: {e}")
    
    async def execute_flow(self, flow_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a promptflow dynamically"""
        try:
            flow_config = self.config_loader.get_flow_config(flow_name)
            if not flow_config:
                raise ValueError(f"Flow configuration not found: {flow_name}")
            
            if not flow_config.get("enabled", True):
                raise ValueError(f"Flow is disabled: {flow_name}")
            
            logger.info(f"Executing flow: {flow_name}")
            
            # Execute the flow based on type
            if flow_name == "chat_assistant":
                return await self._execute_chat_assistant_flow(flow_config, inputs)
            elif flow_name == "document_qa":
                return await self._execute_document_qa_flow(flow_config, inputs)
            else:
                # Generic flow execution
                return await self._execute_generic_flow(flow_config, inputs)
                
        except Exception as e:
            logger.error(f"Error executing flow {flow_name}: {e}")
            raise
    
    async def _execute_chat_assistant_flow(self, flow_config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute chat assistant flow"""
        try:
            flow_path = flow_config["flow_path"]
            
            # Step 1: Prepare prompt
            prepare_prompt_result = await self._execute_python_node(
                flow_path, "prepare_prompt", "prepare_prompt", {
                    "chat_history": inputs.get("chat_history", []),
                    "question": inputs.get("question", ""),
                    "profile_name": inputs.get("profile_name", "Assistant")
                }
            )
            
            # Step 2: LLM Response
            llm_settings = flow_config["nodes"]["llm_response"]["settings"]
            llm_response = await self._execute_llm_node(
                messages=[
                    {"role": "system", "content": prepare_prompt_result["system_prompt"]},
                    {"role": "user", "content": prepare_prompt_result["user_message"]}
                ],
                settings=llm_settings
            )
            
            # Step 3: Format response
            format_response_result = await self._execute_python_node(
                flow_path, "format_response", "format_response", {
                    "llm_output": llm_response,
                    "profile_name": inputs.get("profile_name", "Assistant")
                }
            )
            
            return {
                "answer": llm_response,
                "citations": format_response_result
            }
            
        except Exception as e:
            logger.error(f"Error in chat assistant flow: {e}")
            raise
    
    async def _execute_document_qa_flow(self, flow_config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute document Q&A flow"""
        try:
            flow_path = flow_config["flow_path"]
            
            # Step 1: Preprocess document
            preprocess_result = await self._execute_python_node(
                flow_path, "preprocess_document", "preprocess_document", {
                    "document_content": inputs.get("document_content", ""),
                    "question": inputs.get("question", "")
                }
            )
            
            # Step 2: Extract context
            extract_context_result = await self._execute_python_node(
                flow_path, "extract_context", "extract_context", {
                    "processed_doc": preprocess_result,
                    "question": inputs.get("question", ""),
                    "chat_history": inputs.get("chat_history", [])
                }
            )
            
            # Step 3: Generate answer using LLM
            llm_settings = flow_config["nodes"]["generate_answer"]["settings"]
            
            # Build prompt for Q&A
            qa_prompt = f"""You are an expert document analyst. Your task is to answer questions based solely on the provided document context.

Context: {extract_context_result.get('context', '')}

Question: {inputs.get('question', '')}

Please provide a detailed answer based only on the information in the context. If the context doesn't contain enough information to answer the question, say so clearly."""
            
            answer = await self._execute_llm_node(
                messages=[
                    {"role": "system", "content": "You are an expert document analyst."},
                    {"role": "user", "content": qa_prompt}
                ],
                settings=llm_settings
            )
            
            # Step 4: Calculate relevance
            relevance_result = await self._execute_python_node(
                flow_path, "calculate_relevance", "calculate_relevance", {
                    "question": inputs.get("question", ""),
                    "answer": answer,
                    "context": extract_context_result.get("context", "")
                }
            )
            
            # Step 5: Extract sources
            sources_result = await self._execute_python_node(
                flow_path, "extract_sources", "extract_sources", {
                    "processed_doc": preprocess_result,
                    "context": extract_context_result.get("context", ""),
                    "answer": answer
                }
            )
            
            return {
                "answer": answer,
                "relevance_score": relevance_result,
                "sources": sources_result
            }
            
        except Exception as e:
            logger.error(f"Error in document Q&A flow: {e}")
            raise
    
    async def _execute_generic_flow(self, flow_config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a generic flow based on configuration"""
        # This would implement a generic flow executor based on the node configuration
        # For now, return a simple response
        return {"message": "Generic flow execution not yet implemented"}
    
    async def _execute_python_node(self, flow_path: str, node_name: str, function_name: str, inputs: Dict[str, Any]) -> Any:
        """Execute a Python node dynamically"""
        try:
            # Import the module dynamically
            module_path = f"{flow_path.replace('/', '.')}.{node_name}"
            
            # Add the current directory to Python path if needed
            current_dir = os.getcwd()
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)
            
            module = importlib.import_module(module_path)
            function = getattr(module, function_name)
            
            # Execute the function
            if asyncio.iscoroutinefunction(function):
                result = await function(**inputs)
            else:
                result = function(**inputs)
            
            logger.debug(f"Executed Python node: {node_name} -> {type(result)}")
            return result
            
        except Exception as e:
            logger.error(f"Error executing Python node {node_name}: {e}")
            raise
    
    async def _execute_llm_node(self, messages: List[Dict[str, str]], settings: Dict[str, Any]) -> str:
        """Execute an LLM node"""
        try:
            if not self.client:
                raise ValueError("Azure OpenAI client not initialized")
            
            # Get deployment name from environment or config
            deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
            if not deployment_name:
                connection_config = self.config_loader.get_connection_config("Default_AzureOpenAI")
                if connection_config:
                    expanded_config = self.config_loader.expand_environment_variables(connection_config)
                    deployment_name = expanded_config.get("deployment_name")
            
            if not deployment_name:
                raise ValueError("Azure OpenAI deployment name not configured")
            
            response = await self.client.chat.completions.create(
                model=deployment_name,
                messages=messages,
                temperature=settings.get("temperature", 0.7),
                max_tokens=settings.get("max_tokens", 1000),
                top_p=settings.get("top_p", 1.0)
            )
            
            result = response.choices[0].message.content
            logger.debug(f"LLM response length: {len(result) if result else 0}")
            return result or ""
            
        except Exception as e:
            logger.error(f"Error executing LLM node: {e}")
            raise
    
    def validate_flow_inputs(self, flow_name: str, inputs: Dict[str, Any]) -> bool:
        """Validate inputs for a flow"""
        try:
            flow_config = self.config_loader.get_flow_config(flow_name)
            if not flow_config:
                return False
            
            required_inputs = [
                input_config["name"] 
                for input_config in flow_config.get("inputs", [])
                if input_config.get("required", False)
            ]
            
            for required_input in required_inputs:
                if required_input not in inputs:
                    logger.warning(f"Missing required input: {required_input}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating inputs for flow {flow_name}: {e}")
            return False
    
    def get_flow_info(self, flow_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a flow"""
        flow_config = self.config_loader.get_flow_config(flow_name)
        if not flow_config:
            return None
        
        return {
            "name": flow_config.get("name"),
            "description": flow_config.get("description"),
            "enabled": flow_config.get("enabled", True),
            "inputs": flow_config.get("inputs", []),
            "outputs": flow_config.get("outputs", [])
        }
    
    def list_available_flows(self) -> List[str]:
        """List all available flows"""
        promptflow_config = self.config_loader.get_promptflow_config()
        if not promptflow_config:
            return []
        
        return [
            name for name, config in promptflow_config.promptflows.items()
            if config.get("enabled", True)
        ]

# Global executor instance
_executor: Optional[PromptflowExecutor] = None

def get_promptflow_executor() -> PromptflowExecutor:
    """Get the global promptflow executor instance"""
    global _executor
    if _executor is None:
        _executor = PromptflowExecutor()
    return _executor 