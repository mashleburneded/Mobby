# src/input_validator.py
"""
Enhanced input validation and smart suggestions for Möbius AI Assistant.
Provides intelligent input validation with helpful suggestions and auto-correction.
"""
import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ValidationResult(Enum):
    VALID = "valid"
    INVALID = "invalid"
    CORRECTABLE = "correctable"

@dataclass
class ValidationResponse:
    result: ValidationResult
    message: str
    suggestions: List[str]
    corrected_input: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class InputValidator:
    """
    Intelligent input validation with auto-correction and helpful suggestions.
    Improves user experience without compromising security or performance.
    """
    
    def __init__(self):
        self.validation_rules = self._load_validation_rules()
        self.common_corrections = self._load_common_corrections()
        self.command_patterns = self._load_command_patterns()
        
    def _load_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load validation rules for different input types"""
        return {
            "ethereum_address": {
                "pattern": r"^0x[a-fA-F0-9]{40}$",
                "description": "Ethereum address (42 characters starting with 0x)",
                "example": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"
            },
            "amount_usd": {
                "pattern": r"^\d+(\.\d{1,2})?$",
                "min_value": 0.01,
                "max_value": 1000000000,
                "description": "USD amount (positive number with up to 2 decimal places)",
                "example": "1000.50"
            },
            "protocol_slug": {
                "pattern": r"^[a-z0-9\-_]+$",
                "min_length": 2,
                "max_length": 50,
                "description": "Protocol identifier (lowercase letters, numbers, hyphens, underscores)",
                "example": "uniswap-v3"
            },
            "calendly_url": {
                "pattern": r"^https://calendly\.com/[a-zA-Z0-9\-_/]+$",
                "description": "Calendly scheduling URL",
                "example": "https://calendly.com/username/meeting"
            },
            "username": {
                "pattern": r"^@?[a-zA-Z0-9_]{5,32}$",
                "description": "Telegram username (5-32 characters, letters, numbers, underscores)",
                "example": "@username or username"
            },
            "timezone": {
                "valid_values": [
                    "UTC", "US/Eastern", "US/Central", "US/Mountain", "US/Pacific",
                    "Europe/London", "Europe/Paris", "Europe/Berlin", "Europe/Rome",
                    "Asia/Tokyo", "Asia/Shanghai", "Asia/Singapore", "Australia/Sydney"
                ],
                "description": "Valid timezone identifier",
                "example": "UTC or US/Eastern"
            },
            "time_24h": {
                "pattern": r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$",
                "description": "24-hour time format",
                "example": "14:30 or 09:00"
            }
        }
    
    def _load_common_corrections(self) -> Dict[str, List[Tuple[str, str]]]:
        """Load common input corrections and suggestions"""
        return {
            "ethereum_address": [
                (r"^0X", "0x"),  # Fix uppercase 0X
                (r"^[a-fA-F0-9]{40}$", "0x{input}"),  # Add missing 0x prefix
                (r"^0x[a-fA-F0-9]{39}$", None),  # Too short, suggest checking
                (r"^0x[a-fA-F0-9]{41,}$", None),  # Too long, suggest checking
            ],
            "protocol_slug": [
                (r"[A-Z]", lambda m: m.group().lower()),  # Convert to lowercase
                (r"\s+", "-"),  # Replace spaces with hyphens
                (r"[^a-z0-9\-_]", ""),  # Remove invalid characters
            ],
            "username": [
                (r"^([a-zA-Z0-9_]{5,32})$", "@{input}"),  # Add missing @
                (r"^@+", "@"),  # Fix multiple @ symbols
            ],
            "amount_usd": [
                (r"^\$", ""),  # Remove $ symbol
                (r",", ""),  # Remove commas
                (r"^(\d+)$", "{input}.00"),  # Add decimal places for whole numbers
            ]
        }
    
    def _load_command_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load command-specific validation patterns"""
        return {
            "llama": {
                "args_count": 2,
                "arg_types": ["data_type", "protocol_slug"],
                "valid_data_types": ["tvl", "revenue", "raises"],
                "description": "Usage: /llama <type> <protocol>\nTypes: tvl, revenue, raises"
            },
            "arkham": {
                "args_count": 1,
                "arg_types": ["ethereum_address_or_query"],
                "description": "Usage: /arkham <wallet_address_or_entity_name>"
            },
            "nansen": {
                "args_count": 1,
                "arg_types": ["ethereum_address"],
                "description": "Usage: /nansen <wallet_address>"
            },
            "alert": {
                "args_count": 2,
                "arg_types": ["ethereum_address", "amount_usd"],
                "description": "Usage: /alert <wallet_address> <amount_usd>"
            },
            "set_calendly": {
                "args_count": 1,
                "arg_types": ["calendly_url"],
                "description": "Usage: /set_calendly <calendly_url>"
            },
            "schedule": {
                "args_count": 1,
                "arg_types": ["username"],
                "description": "Usage: /schedule @username"
            },
            "set_timezone": {
                "args_count": 1,
                "arg_types": ["timezone"],
                "description": "Usage: /set_timezone <timezone>"
            },
            "set_summary_time": {
                "args_count": 1,
                "arg_types": ["time_24h"],
                "description": "Usage: /set_summary_time <HH:MM>"
            }
        }
    
    def validate_command_input(self, command: str, args: List[str]) -> ValidationResponse:
        """Validate command input with intelligent suggestions"""
        command_clean = command.lower().replace("/", "")
        
        # Check if command exists
        if command_clean not in self.command_patterns:
            return self._suggest_similar_commands(command_clean)
        
        command_config = self.command_patterns[command_clean]
        expected_args = command_config.get("args_count", 0)
        
        # Check argument count
        if len(args) != expected_args:
            return ValidationResponse(
                result=ValidationResult.INVALID,
                message=f"❌ **Incorrect number of arguments**\n\nExpected {expected_args}, got {len(args)}",
                suggestions=[
                    command_config.get("description", f"Use `/help {command_clean}` for usage"),
                    f"Example: {self._get_command_example(command_clean)}"
                ]
            )
        
        # Validate each argument
        arg_types = command_config.get("arg_types", [])
        for i, (arg, arg_type) in enumerate(zip(args, arg_types)):
            validation = self.validate_input(arg, arg_type)
            
            if validation.result == ValidationResult.INVALID:
                return ValidationResponse(
                    result=ValidationResult.INVALID,
                    message=f"❌ **Invalid argument {i+1}**\n\n{validation.message}",
                    suggestions=validation.suggestions + [command_config.get("description", "")]
                )
            elif validation.result == ValidationResult.CORRECTABLE:
                return ValidationResponse(
                    result=ValidationResult.CORRECTABLE,
                    message=f"🔧 **Argument {i+1} can be corrected**\n\n{validation.message}",
                    suggestions=validation.suggestions,
                    corrected_input=validation.corrected_input
                )
        
        # Special validation for specific commands
        if command_clean == "llama":
            return self._validate_llama_command(args)
        
        return ValidationResponse(
            result=ValidationResult.VALID,
            message="✅ Input is valid",
            suggestions=[]
        )
    
    def validate_input(self, input_value: str, input_type: str) -> ValidationResponse:
        """Validate individual input value"""
        if input_type not in self.validation_rules:
            return ValidationResponse(
                result=ValidationResult.VALID,
                message="No validation rules for this input type",
                suggestions=[]
            )
        
        rules = self.validation_rules[input_type]
        
        # Check pattern if exists
        if "pattern" in rules:
            pattern = rules["pattern"]
            if not re.match(pattern, input_value):
                # Try to correct the input
                corrected = self._try_correct_input(input_value, input_type)
                if corrected:
                    return ValidationResponse(
                        result=ValidationResult.CORRECTABLE,
                        message=f"Input doesn't match expected format",
                        suggestions=[
                            f"Did you mean: `{corrected}`?",
                            f"Expected format: {rules.get('description', 'See example')}",
                            f"Example: `{rules.get('example', 'N/A')}`"
                        ],
                        corrected_input=corrected
                    )
                else:
                    return ValidationResponse(
                        result=ValidationResult.INVALID,
                        message=f"Invalid format for {input_type}",
                        suggestions=[
                            f"Expected format: {rules.get('description', 'See example')}",
                            f"Example: `{rules.get('example', 'N/A')}`"
                        ]
                    )
        
        # Check valid values if exists
        if "valid_values" in rules:
            if input_value not in rules["valid_values"]:
                # Find similar values
                similar = self._find_similar_values(input_value, rules["valid_values"])
                suggestions = [f"Did you mean: `{val}`?" for val in similar[:3]]
                suggestions.append(f"Valid values: {', '.join(rules['valid_values'][:5])}")
                if len(rules["valid_values"]) > 5:
                    suggestions.append("...and more")
                
                return ValidationResponse(
                    result=ValidationResult.INVALID,
                    message=f"Invalid value for {input_type}",
                    suggestions=suggestions
                )
        
        # Check numeric ranges
        if "min_value" in rules or "max_value" in rules:
            try:
                numeric_value = float(input_value)
                min_val = rules.get("min_value", float('-inf'))
                max_val = rules.get("max_value", float('inf'))
                
                if numeric_value < min_val or numeric_value > max_val:
                    return ValidationResponse(
                        result=ValidationResult.INVALID,
                        message=f"Value out of range",
                        suggestions=[
                            f"Must be between {min_val} and {max_val}",
                            f"You entered: {numeric_value}"
                        ]
                    )
            except ValueError:
                return ValidationResponse(
                    result=ValidationResult.INVALID,
                    message=f"Expected numeric value",
                    suggestions=[f"Example: {rules.get('example', '100')}"]
                )
        
        # Check length constraints
        if "min_length" in rules or "max_length" in rules:
            min_len = rules.get("min_length", 0)
            max_len = rules.get("max_length", float('inf'))
            
            if len(input_value) < min_len or len(input_value) > max_len:
                return ValidationResponse(
                    result=ValidationResult.INVALID,
                    message=f"Length must be between {min_len} and {max_len} characters",
                    suggestions=[f"Current length: {len(input_value)}"]
                )
        
        return ValidationResponse(
            result=ValidationResult.VALID,
            message="Input is valid",
            suggestions=[]
        )
    
    def _try_correct_input(self, input_value: str, input_type: str) -> Optional[str]:
        """Try to automatically correct common input errors"""
        if input_type not in self.common_corrections:
            return None
        
        corrections = self.common_corrections[input_type]
        corrected = input_value
        
        for pattern, replacement in corrections:
            if replacement is None:
                continue
            
            if callable(replacement):
                corrected = re.sub(pattern, replacement, corrected)
            elif "{input}" in replacement:
                if re.match(pattern, corrected):
                    corrected = replacement.format(input=corrected)
            else:
                corrected = re.sub(pattern, replacement, corrected)
        
        # Validate the corrected input
        validation = self.validate_input(corrected, input_type)
        return corrected if validation.result == ValidationResult.VALID else None
    
    def _suggest_similar_commands(self, command: str) -> ValidationResponse:
        """Suggest similar commands for typos"""
        available_commands = list(self.command_patterns.keys())
        similar = self._find_similar_values(command, available_commands)
        
        suggestions = []
        if similar:
            suggestions.extend([f"Did you mean `/{cmd}`?" for cmd in similar[:3]])
        
        suggestions.extend([
            "Use `/help` to see all available commands",
            "Check your spelling and try again"
        ])
        
        return ValidationResponse(
            result=ValidationResult.INVALID,
            message=f"❓ **Unknown command: `/{command}`**",
            suggestions=suggestions
        )
    
    def _validate_llama_command(self, args: List[str]) -> ValidationResponse:
        """Special validation for llama command"""
        data_type, protocol_slug = args
        
        valid_types = ["tvl", "revenue", "raises"]
        if data_type.lower() not in valid_types:
            similar_types = self._find_similar_values(data_type.lower(), valid_types)
            suggestions = []
            if similar_types:
                suggestions.append(f"Did you mean `{similar_types[0]}`?")
            suggestions.extend([
                f"Valid types: {', '.join(valid_types)}",
                "Example: `/llama tvl uniswap`"
            ])
            
            return ValidationResponse(
                result=ValidationResult.INVALID,
                message=f"❌ **Invalid data type: `{data_type}`**",
                suggestions=suggestions
            )
        
        return ValidationResponse(
            result=ValidationResult.VALID,
            message="✅ Command is valid",
            suggestions=[]
        )
    
    def _find_similar_values(self, input_value: str, valid_values: List[str], max_distance: int = 2) -> List[str]:
        """Find similar values using simple string distance"""
        def levenshtein_distance(s1: str, s2: str) -> int:
            if len(s1) < len(s2):
                return levenshtein_distance(s2, s1)
            
            if len(s2) == 0:
                return len(s1)
            
            previous_row = list(range(len(s2) + 1))
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            
            return previous_row[-1]
        
        similar = []
        input_lower = input_value.lower()
        
        for value in valid_values:
            value_lower = value.lower()
            distance = levenshtein_distance(input_lower, value_lower)
            
            # Also check if input is a substring or starts with the value
            if (distance <= max_distance or 
                input_lower in value_lower or 
                value_lower.startswith(input_lower)):
                similar.append((value, distance))
        
        # Sort by distance and return values
        similar.sort(key=lambda x: x[1])
        return [value for value, _ in similar[:5]]
    
    def _get_command_example(self, command: str) -> str:
        """Get example usage for a command"""
        examples = {
            "llama": "/llama tvl uniswap",
            "arkham": "/arkham 0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            "nansen": "/nansen 0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            "alert": "/alert 0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6 1000",
            "set_calendly": "/set_calendly https://calendly.com/username/meeting",
            "schedule": "/schedule @username",
            "set_timezone": "/set_timezone UTC",
            "set_summary_time": "/set_summary_time 14:30"
        }
        return examples.get(command, f"/{command} <arguments>")

# Global input validator instance
input_validator = InputValidator()