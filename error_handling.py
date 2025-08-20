"""
Error Handling Module - Robust Exception Management
Following SOLID principles for defensive programming
"""
from enum import Enum
from typing import Dict, Any, Optional, Callable, Type, List
import logging
from dataclasses import dataclass
from abc import ABC, abstractmethod

class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ErrorContext:
    operation: str
    parameters: Dict[str, Any]
    timestamp: float
    retry_count: int = 0

class ErrorRecoveryStrategy(ABC):
    @abstractmethod
    def can_recover(self, error: Exception, context: ErrorContext) -> bool:
        pass
    
    @abstractmethod
    def recover(self, error: Exception, context: ErrorContext) -> Any:
        pass

class NetworkErrorRecovery(ErrorRecoveryStrategy):
    def can_recover(self, error: Exception, context: ErrorContext) -> bool:
        return (
            isinstance(error, (ConnectionError, TimeoutError)) and
            context.retry_count < 3
        )
    
    def recover(self, error: Exception, context: ErrorContext) -> Any:
        logging.warning(f"Network error in {context.operation}, attempt {context.retry_count + 1}/3")
        context.retry_count += 1
        return "retry_with_backoff"

class DataValidationErrorRecovery(ErrorRecoveryStrategy):
    def can_recover(self, error: Exception, context: ErrorContext) -> bool:
        return isinstance(error, (ValueError, KeyError, TypeError))
    
    def recover(self, error: Exception, context: ErrorContext) -> Any:
        logging.error(f"Data validation error in {context.operation}: {str(error)}")
        return "use_fallback_values"

class ErrorHandler:
    def __init__(self):
        self._recovery_strategies: List[ErrorRecoveryStrategy] = [
            NetworkErrorRecovery(),
            DataValidationErrorRecovery()
        ]
        self._logger = logging.getLogger(__name__)
    
    def handle_error(self, 
                    error: Exception, 
                    context: ErrorContext,
                    fallback: Optional[Callable] = None) -> Any:
        
        # Prova strategie di recovery specifiche
        for strategy in self._recovery_strategies:
            if strategy.can_recover(error, context):
                try:
                    return strategy.recover(error, context)
                except Exception as recovery_error:
                    self._logger.error(f"Recovery failed: {recovery_error}")
        
        # Se nessuna recovery è possibile, usa fallback
        if fallback:
            try:
                return fallback()
            except Exception as fallback_error:
                self._logger.critical(f"Fallback failed: {fallback_error}")
        
        # Log errore e re-raise se non gestibile
        self._log_error(error, context)
        raise error
    
    def _log_error(self, error: Exception, context: ErrorContext):
        severity = self._determine_severity(error)
        log_level = {
            ErrorSeverity.LOW: logging.INFO,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }[severity]
        
        self._logger.log(
            log_level,
            f"[{severity.value.upper()}] {context.operation}: {str(error)}"
        )
    
    def _determine_severity(self, error: Exception) -> ErrorSeverity:
        if isinstance(error, (SystemExit, KeyboardInterrupt)):
            return ErrorSeverity.CRITICAL
        elif isinstance(error, (ConnectionError, TimeoutError)):
            return ErrorSeverity.HIGH
        elif isinstance(error, (ValueError, KeyError)):
            return ErrorSeverity.MEDIUM
        else:
            return ErrorSeverity.LOW

# Singleton instance
error_handler = ErrorHandler()

def safe_execute(operation_name: str, 
                func: Callable, 
                *args, 
                fallback: Optional[Callable] = None,
                **kwargs) -> Any:
    """
    Decorator per esecuzione sicura con error handling robusto
    """
    import time
    
    context = ErrorContext(
        operation=operation_name,
        parameters={"args": args, "kwargs": kwargs},
        timestamp=time.time()
    )
    
    try:
        return func(*args, **kwargs)
    except Exception as e:
        return error_handler.handle_error(e, context, fallback)