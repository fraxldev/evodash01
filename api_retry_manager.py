#!/usr/bin/env python3
"""
🛡️ API RETRY MANAGER - DEFENSIVE SECURITY
==========================================
Sistema robusto per gestione retry con exponential backoff e rate limiting.
Previene infinite loops e rispetta limiti API Gate.io.

Principi implementati:
- SOLID: Single Responsibility, Interface Segregation
- Defensive Programming: Limiti rigidi, fallback sicuri
- Security by Design: Rate limiting, circuit breaker
"""

import time
import random
import logging
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum


class RetryableErrorType(Enum):
    """Tipologie errori gestibili"""
    NETWORK_ERROR = "network"
    RATE_LIMIT = "rate_limit"
    SERVER_ERROR = "server_error"
    TIMEOUT = "timeout"
    API_ERROR = "api_error"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class RetryConfig:
    """Configurazione immutabile retry policy"""
    max_attempts: int = 5
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    backoff_multiplier: float = 1.5
    
    def __post_init__(self):
        if self.max_attempts <= 0:
            raise ValueError("max_attempts must be positive")
        if self.base_delay <= 0:
            raise ValueError("base_delay must be positive")


@dataclass
class RetryAttempt:
    """Informazioni tentativo retry"""
    attempt_number: int
    error_type: RetryableErrorType
    delay_seconds: float
    timestamp: float
    error_message: str = ""


class IRateLimitHandler:
    """Interface per gestione rate limiting"""
    def handle_rate_limit(self, retry_after: Optional[int] = None) -> float:
        raise NotImplementedError
    
    def can_make_request(self) -> bool:
        raise NotImplementedError


class GateIORateLimitHandler(IRateLimitHandler):
    """Gestore rate limiting specifico Gate.io"""
    
    def __init__(self):
        self.last_request_time = 0.0
        self.min_interval = 0.1  # 100ms minimo tra requests
        self.rate_limit_until = 0.0
        
    def handle_rate_limit(self, retry_after: Optional[int] = None) -> float:
        """Calcola delay per rate limiting con safety margin"""
        if retry_after:
            # Usa header Retry-After + 20% margin
            delay = retry_after * 1.2
        else:
            # Fallback: 60s + jitter per sicurezza
            delay = 60.0 + random.uniform(0, 30.0)
            
        self.rate_limit_until = time.time() + delay
        logging.warning(f"🚨 Rate limit hit - waiting {delay:.1f}s")
        return delay
    
    def can_make_request(self) -> bool:
        """Verifica se possiamo fare richiesta"""
        now = time.time()
        
        # Check rate limit timeout
        if now < self.rate_limit_until:
            return False
            
        # Check minimum interval
        if now - self.last_request_time < self.min_interval:
            return False
            
        self.last_request_time = now
        return True


class ExponentialBackoffCalculator:
    """Calcolatore backoff con jitter (Single Responsibility)"""
    
    @staticmethod
    def calculate_delay(attempt: int, config: RetryConfig, error_type: RetryableErrorType) -> float:
        """Calcola delay con exponential backoff e jitter"""
        if attempt <= 0:
            return 0.0
            
        # Base delay con exponential backoff
        delay = config.base_delay * (config.exponential_base ** (attempt - 1))
        
        # Rate limiting ha priorità
        if error_type == RetryableErrorType.RATE_LIMIT:
            delay = max(delay, 60.0)  # Min 60s per rate limit
            
        # Apply multiplier
        delay *= config.backoff_multiplier
        
        # Cap al massimo
        delay = min(delay, config.max_delay)
        
        # Add jitter per evitare thundering herd
        if config.jitter:
            jitter_range = delay * 0.2  # ±20%
            jitter = random.uniform(-jitter_range, jitter_range)
            delay += jitter
            
        return max(0.1, delay)  # Min 100ms


class CircuitBreaker:
    """Circuit breaker per prevenire cascading failures"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 300):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        
    def record_failure(self):
        """Registra fallimento"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logging.error(f"🔴 Circuit breaker OPEN - {self.failure_count} failures")
    
    def record_success(self):
        """Registra successo"""
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"
            self.failure_count = 0
            logging.info("✅ Circuit breaker CLOSED - recovered")
    
    def can_proceed(self) -> bool:
        """Verifica se possiamo procedere"""
        if self.state == "CLOSED":
            return True
            
        if self.state == "OPEN":
            # Check recovery timeout
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = "HALF_OPEN"
                logging.info("🟡 Circuit breaker HALF_OPEN - testing")
                return True
            return False
            
        # HALF_OPEN: allow single attempt
        return True


class ApiRetryManager:
    """Manager principale per retry con security focus"""
    
    def __init__(self, config: RetryConfig = None, rate_handler: IRateLimitHandler = None):
        self.config = config or RetryConfig()
        self.rate_handler = rate_handler or GateIORateLimitHandler()
        self.circuit_breaker = CircuitBreaker()
        self.calculator = ExponentialBackoffCalculator()
        self.retry_stats: Dict[str, int] = {}
        
    def execute_with_retry(self, 
                          operation: Callable[[], Any],
                          operation_name: str = "api_call",
                          error_classifier: Optional[Callable[[Exception], RetryableErrorType]] = None) -> Any:
        """
        Esegue operazione con retry robusto e sicuro
        
        Args:
            operation: Funzione da eseguire
            operation_name: Nome per logging/stats
            error_classifier: Funzione per classificare errori
            
        Returns:
            Risultato operazione
            
        Raises:
            Exception: Dopo max tentativi falliti
        """
        if not self.circuit_breaker.can_proceed():
            raise RuntimeError("Circuit breaker is OPEN - operation blocked")
        
        attempts = []
        last_exception = None
        
        for attempt in range(1, self.config.max_attempts + 1):
            try:
                # Check rate limiting
                if not self.rate_handler.can_make_request():
                    logging.debug(f"Rate limit active - skipping attempt {attempt}")
                    time.sleep(0.1)
                    continue
                
                # Execute operation
                logging.debug(f"🔄 {operation_name} - attempt {attempt}/{self.config.max_attempts}")
                result = operation()
                
                # Success!
                self.circuit_breaker.record_success()
                self._record_success(operation_name, attempt, attempts)
                return result
                
            except Exception as e:
                last_exception = e
                
                # Classify error type
                error_type = self._classify_error(e, error_classifier)
                
                # Handle rate limiting specifically
                if error_type == RetryableErrorType.RATE_LIMIT:
                    retry_after = self._extract_retry_after(e)
                    delay = self.rate_handler.handle_rate_limit(retry_after)
                else:
                    delay = self.calculator.calculate_delay(attempt, self.config, error_type)
                
                # Record attempt
                retry_attempt = RetryAttempt(
                    attempt_number=attempt,
                    error_type=error_type,
                    delay_seconds=delay,
                    timestamp=time.time(),
                    error_message=str(e)
                )
                attempts.append(retry_attempt)
                
                # Check if should retry
                if attempt >= self.config.max_attempts:
                    self.circuit_breaker.record_failure()
                    self._record_failure(operation_name, attempts)
                    break
                
                # Wait before retry
                logging.warning(f"⚠️ {operation_name} failed (attempt {attempt}) - retrying in {delay:.1f}s: {e}")
                time.sleep(delay)
        
        # All attempts failed
        self._record_failure(operation_name, attempts)
        raise RuntimeError(f"Operation '{operation_name}' failed after {self.config.max_attempts} attempts") from last_exception
    
    def _classify_error(self, error: Exception, classifier: Optional[Callable] = None) -> RetryableErrorType:
        """Classifica tipo errore per strategia retry"""
        if classifier:
            return classifier(error)
            
        error_str = str(error).lower()
        
        # HTTP status codes
        if hasattr(error, 'response') and error.response:
            status = error.response.status_code
            if status == 429:
                return RetryableErrorType.RATE_LIMIT
            elif status >= 500:
                return RetryableErrorType.SERVER_ERROR
            elif status in [408, 504]:
                return RetryableErrorType.TIMEOUT
        
        # Network/connection errors
        if any(keyword in error_str for keyword in ['connection', 'network', 'timeout', 'dns']):
            return RetryableErrorType.NETWORK_ERROR
            
        return RetryableErrorType.UNKNOWN
    
    def _extract_retry_after(self, error: Exception) -> Optional[int]:
        """Estrae Retry-After header se disponibile"""
        if hasattr(error, 'response') and error.response:
            retry_after = error.response.headers.get('Retry-After')
            if retry_after:
                try:
                    return int(retry_after)
                except ValueError:
                    pass
        return None
    
    def _record_success(self, operation: str, attempts: int, retry_history: list):
        """Registra successo per statistiche"""
        self.retry_stats[f"{operation}_success"] = self.retry_stats.get(f"{operation}_success", 0) + 1
        if attempts > 1:
            logging.info(f"✅ {operation} succeeded after {attempts} attempts")
    
    def _record_failure(self, operation: str, retry_history: list):
        """Registra fallimento permanente"""
        self.retry_stats[f"{operation}_failure"] = self.retry_stats.get(f"{operation}_failure", 0) + 1
        logging.error(f"❌ {operation} failed permanently after {len(retry_history)} attempts")
        
        # Log retry timeline for debugging
        for attempt in retry_history:
            logging.debug(f"  Attempt {attempt.attempt_number}: {attempt.error_type.value} -> {attempt.delay_seconds:.1f}s delay")
    
    def get_stats(self) -> Dict[str, Any]:
        """Statistiche retry per monitoring"""
        return {
            "retry_stats": self.retry_stats.copy(),
            "circuit_breaker_state": self.circuit_breaker.state,
            "circuit_breaker_failures": self.circuit_breaker.failure_count,
            "rate_limit_active": time.time() < self.rate_handler.rate_limit_until if hasattr(self.rate_handler, 'rate_limit_until') else False
        }


# Factory per configurazioni predefinite
def create_gate_io_retry_manager() -> ApiRetryManager:
    """Crea retry manager ottimizzato per Gate.io"""
    config = RetryConfig(
        max_attempts=5,
        base_delay=1.0,
        max_delay=300.0,
        exponential_base=2.0,
        jitter=True,
        backoff_multiplier=1.5
    )
    
    rate_handler = GateIORateLimitHandler()
    return ApiRetryManager(config, rate_handler)


def create_aggressive_retry_manager() -> ApiRetryManager:
    """Crea manager con retry più aggressivo per sistemi interni"""
    config = RetryConfig(
        max_attempts=10,
        base_delay=0.5,
        max_delay=60.0,
        exponential_base=1.5,
        jitter=True,
        backoff_multiplier=1.2
    )
    
    return ApiRetryManager(config)


if __name__ == "__main__":
    # Test example
    import requests
    
    def test_operation():
        response = requests.get("https://httpstat.us/500", timeout=5)
        response.raise_for_status()
        return response.json()
    
    manager = create_gate_io_retry_manager()
    
    try:
        result = manager.execute_with_retry(test_operation, "test_api_call")
        print(f"Success: {result}")
    except Exception as e:
        print(f"Final failure: {e}")
        print(f"Stats: {manager.get_stats()}")