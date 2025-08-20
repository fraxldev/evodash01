#!/usr/bin/env python3
"""
🛡️ SAFE SLEEP MANAGER - DEFENSIVE SECURITY
==========================================
Sistema sicuro per sleep e wait operations che previene busy-wait e 
rispetta limiti temporali per evitare infinite loops.

Principi implementati:
- SOLID: Single Responsibility per sleep management
- Defensive Programming: Limiti rigidi, timeouts
- Performance: Adaptive sleep basato su condizioni
"""

import time
import random
import logging
from typing import Optional, Callable
from dataclasses import dataclass
from enum import Enum


class SleepContext(Enum):
    """Contesti di sleep per adaptive timing"""
    API_RETRY = "api_retry"
    TRADING_CYCLE = "trading_cycle"
    ERROR_RECOVERY = "error_recovery"
    CIRCUIT_BREAKER = "circuit_breaker"
    DATA_POLLING = "data_polling"
    BALANCE_CHECK = "balance_check"


@dataclass(frozen=True)
class SleepLimits:
    """Limiti sicuri per sleep operations"""
    min_sleep: float = 0.1  # Min 100ms
    max_sleep: float = 300.0  # Max 5 minuti
    default_sleep: float = 0.5  # Default 500ms
    max_total_wait: float = 3600.0  # Max 1 ora di wait totale
    
    def __post_init__(self):
        if self.min_sleep <= 0:
            raise ValueError("min_sleep must be positive")
        if self.max_sleep < self.min_sleep:
            raise ValueError("max_sleep must be >= min_sleep")


class SafeSleepManager:
    """🛡️ Manager sicuro per operations di sleep e wait"""
    
    def __init__(self, limits: SleepLimits = None):
        self.limits = limits or SleepLimits()
        self.total_sleep_time = 0.0
        self.session_start_time = time.time()
        self.sleep_history = []
        
    def safe_sleep(self, 
                   duration: float, 
                   context: SleepContext = SleepContext.TRADING_CYCLE,
                   jitter: bool = True) -> bool:
        """
        Sleep sicuro con limiti e validazione
        
        Args:
            duration: Durata sleep richiesta
            context: Contesto per ottimizzazioni
            jitter: Aggiunge randomizzazione per evitare thundering herd
            
        Returns:
            True se sleep completato, False se interrotto per limiti
        """
        # 🛡️ Validation e sanitization
        safe_duration = self._sanitize_duration(duration, context)
        
        # 🚨 Check total wait limit
        if self.total_sleep_time + safe_duration > self.limits.max_total_wait:
            logging.warning(f"🚨 Sleep blocked - would exceed max total wait time ({self.limits.max_total_wait}s)")
            return False
        
        # Add jitter per evitare thundering herd
        if jitter and context != SleepContext.CIRCUIT_BREAKER:
            jitter_factor = random.uniform(0.9, 1.1)  # ±10%
            safe_duration *= jitter_factor
            safe_duration = max(self.limits.min_sleep, safe_duration)
        
        # Record sleep
        self.sleep_history.append({
            'duration': safe_duration,
            'context': context.value,
            'timestamp': time.time()
        })
        
        # Execute sleep
        start_time = time.time()
        time.sleep(safe_duration)
        actual_duration = time.time() - start_time
        
        self.total_sleep_time += actual_duration
        
        logging.debug(f"💤 Safe sleep: {safe_duration:.2f}s (context: {context.value})")
        return True
    
    def adaptive_sleep(self, 
                       base_duration: float, 
                       failure_count: int = 0,
                       context: SleepContext = SleepContext.TRADING_CYCLE) -> bool:
        """Sleep adattivo basato su contesto e numero fallimenti"""
        
        if context == SleepContext.API_RETRY:
            # Exponential backoff per API retry
            duration = base_duration * (2 ** min(failure_count, 5))  # Cap a 2^5
            
        elif context == SleepContext.ERROR_RECOVERY:
            # Sleep più lungo per error recovery
            duration = base_duration * (1 + failure_count * 0.5)
            
        elif context == SleepContext.DATA_POLLING:
            # Adaptive polling basato su volatilità (simulata)
            volatility_factor = 1.0  # Placeholder per future integration
            duration = base_duration * (2.0 - volatility_factor)
            
        else:
            duration = base_duration
        
        return self.safe_sleep(duration, context)
    
    def conditional_sleep(self, 
                          duration: float,
                          condition_func: Optional[Callable[[], bool]] = None,
                          max_wait_time: float = 60.0,
                          context: SleepContext = SleepContext.TRADING_CYCLE) -> bool:
        """
        Sleep condizionale che si ferma se condizione diventa False
        
        Args:
            duration: Durata sleep per iterazione
            condition_func: Funzione che ritorna True se continuare sleep
            max_wait_time: Tempo massimo di wait totale
            context: Contesto sleep
            
        Returns:
            True se condizione ancora valida, False se interrotto
        """
        if not condition_func:
            return self.safe_sleep(duration, context)
        
        start_wait = time.time()
        sleep_iterations = 0
        max_iterations = int(max_wait_time / max(duration, self.limits.min_sleep)) + 1
        
        while condition_func() and sleep_iterations < max_iterations:
            elapsed = time.time() - start_wait
            if elapsed >= max_wait_time:
                logging.warning(f"🚨 Conditional sleep timeout after {elapsed:.1f}s")
                return False
            
            # Sleep per iterazione più corta
            iteration_sleep = min(duration, max_wait_time - elapsed)
            if not self.safe_sleep(iteration_sleep, context, jitter=False):
                return False
            
            sleep_iterations += 1
        
        return condition_func() if condition_func else True
    
    def circuit_breaker_sleep(self, failure_count: int, max_delay: float = 300.0) -> bool:
        """Sleep specifico per circuit breaker con exponential backoff"""
        base_delay = 10.0  # 10 secondi base
        delay = min(base_delay * (1.5 ** failure_count), max_delay)
        
        logging.info(f"🔴 Circuit breaker sleep: {delay:.1f}s (failures: {failure_count})")
        return self.safe_sleep(delay, SleepContext.CIRCUIT_BREAKER, jitter=True)
    
    def rate_limit_sleep(self, retry_after: Optional[str] = None) -> bool:
        """Sleep specifico per rate limiting con safety margin"""
        if retry_after:
            try:
                delay = float(retry_after) * 1.2  # 20% safety margin
            except ValueError:
                delay = 60.0  # Fallback
        else:
            delay = 60.0  # Default 1 minuto
        
        logging.warning(f"🚨 Rate limit sleep: {delay:.1f}s")
        return self.safe_sleep(delay, SleepContext.API_RETRY, jitter=False)
    
    def _sanitize_duration(self, duration: float, context: SleepContext) -> float:
        """🛡️ Sanitizza durata sleep per sicurezza"""
        # Validation base
        if duration <= 0:
            logging.warning(f"⚠️ Invalid sleep duration {duration}, using min")
            return self.limits.min_sleep
        
        # Context-specific limits
        if context == SleepContext.CIRCUIT_BREAKER:
            # Circuit breaker può avere sleep più lunghi
            max_allowed = min(duration, 600.0)  # Max 10 minuti
        elif context == SleepContext.API_RETRY:
            # API retry ha limiti intermedi
            max_allowed = min(duration, self.limits.max_sleep)
        else:
            # Trading cycle ha limiti più stretti
            max_allowed = min(duration, min(self.limits.max_sleep, 30.0))
        
        # Apply limits
        sanitized = max(self.limits.min_sleep, min(max_allowed, duration))
        
        if sanitized != duration:
            logging.debug(f"Sleep sanitized: {duration:.2f}s -> {sanitized:.2f}s")
        
        return sanitized
    
    def get_sleep_stats(self) -> dict:
        """Statistiche sleep per monitoring"""
        session_duration = time.time() - self.session_start_time
        
        return {
            'total_sleep_time': self.total_sleep_time,
            'session_duration': session_duration,
            'sleep_ratio': self.total_sleep_time / session_duration if session_duration > 0 else 0,
            'sleep_count': len(self.sleep_history),
            'avg_sleep_duration': sum(s['duration'] for s in self.sleep_history) / len(self.sleep_history) if self.sleep_history else 0,
            'remaining_sleep_budget': max(0, self.limits.max_total_wait - self.total_sleep_time)
        }
    
    def reset_session(self):
        """Reset session per nuovo ciclo trading"""
        self.total_sleep_time = 0.0
        self.session_start_time = time.time()
        self.sleep_history = []
        logging.info("🔄 Sleep manager session reset")


# Factory functions per configurazioni predefinite
def create_trading_sleep_manager() -> SafeSleepManager:
    """Sleep manager ottimizzato per trading loop"""
    limits = SleepLimits(
        min_sleep=0.1,
        max_sleep=30.0,
        default_sleep=0.5,
        max_total_wait=1800.0  # 30 minuti max
    )
    return SafeSleepManager(limits)


def create_api_sleep_manager() -> SafeSleepManager:
    """Sleep manager per operazioni API intensive"""
    limits = SleepLimits(
        min_sleep=0.2,
        max_sleep=300.0,
        default_sleep=1.0,
        max_total_wait=3600.0  # 1 ora max
    )
    return SafeSleepManager(limits)


# Global instance per backward compatibility
_global_sleep_manager = create_trading_sleep_manager()


def safe_sleep(duration: float, 
               context: SleepContext = SleepContext.TRADING_CYCLE,
               jitter: bool = True) -> bool:
    """Funzione globale per sleep sicuro"""
    return _global_sleep_manager.safe_sleep(duration, context, jitter)


if __name__ == "__main__":
    # Test example
    manager = create_trading_sleep_manager()
    
    print("Testing safe sleep manager...")
    
    # Test normal sleep
    print("Normal sleep...")
    manager.safe_sleep(0.5, SleepContext.TRADING_CYCLE)
    
    # Test adaptive sleep with failures
    print("Adaptive sleep with failures...")
    manager.adaptive_sleep(0.2, failure_count=3, context=SleepContext.API_RETRY)
    
    # Test conditional sleep
    print("Conditional sleep...")
    counter = [0]  # Use list for mutable reference
    def condition():
        counter[0] += 1
        return counter[0] < 3
    
    manager.conditional_sleep(0.2, condition, max_wait_time=2.0)
    
    # Show stats
    print(f"Sleep stats: {manager.get_sleep_stats()}")