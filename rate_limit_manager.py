#!/usr/bin/env python3
"""
🚦 RATE LIMIT MANAGER - GATE.IO VIP 0 COMPLIANCE
===============================================
Sistema enterprise-grade per gestione rate limiting Gate.io API.
Implementa principi SOLID, Strategy Pattern e Thread Safety.

VIP 0 Rate Limits (2024 Official):
- Public Endpoints: 200r/10s per endpoint (IP-based)
- Spot Order Placement: 10r/1s (UID Market-based)
- Spot Order Cancellation: 200r/1s (UID-based)
- Other Private Endpoints: 200r/10s per endpoint (UID-based)
- Wallet Transfers: 80r/10s (UID-based)
- Wallet Withdrawals: 1r/3s (UID-based)
"""

import time
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Protocol
from collections import deque
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class EndpointCategory(Enum):
    """📊 Categorie endpoint Gate.io per rate limiting"""
    PUBLIC = "public"
    SPOT_ORDER = "spot_order"
    SPOT_CANCEL = "spot_cancel"  
    SPOT_OTHER = "spot_other"
    WALLET_TRANSFER = "wallet_transfer"
    WALLET_WITHDRAWAL = "wallet_withdrawal"
    WALLET_OTHER = "wallet_other"
    FUTURES_ORDER = "futures_order"
    FUTURES_CANCEL = "futures_cancel"
    FUTURES_OTHER = "futures_other"

@dataclass(frozen=True)
class RateLimitConfig:
    """⚙️ Configurazione immutable per rate limiting (Value Object Pattern)"""
    max_requests: int
    window_seconds: int
    burst_allowance: float = 0.8  # Usa solo 80% del limit per sicurezza
    
    @property
    def safe_max_requests(self) -> int:
        """Limite sicuro con burst allowance"""
        return max(1, int(self.max_requests * self.burst_allowance))
    
    @property
    def min_interval_ms(self) -> float:
        """Intervallo minimo tra richieste (ms)"""
        safe_requests = self.safe_max_requests
        if safe_requests <= 0:
            return 1000.0  # Default 1s se configurazione invalida
        return (self.window_seconds * 1000) / safe_requests

class IRateLimitStrategy(Protocol):
    """🎯 Strategy Interface per algoritmi rate limiting (Strategy Pattern)"""
    
    def can_make_request(self) -> bool:
        """Verifica se è possibile effettuare una richiesta"""
        ...
    
    def record_request(self) -> None:
        """Registra una richiesta effettuata"""
        ...
    
    def time_until_next_request(self) -> float:
        """Tempo di attesa prima della prossima richiesta (secondi)"""
        ...

class SlidingWindowRateLimiter:
    """🪟 Implementazione Sliding Window Rate Limiting (Concrete Strategy)"""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.requests: deque[float] = deque()
        self._lock = threading.Lock()
    
    def can_make_request(self) -> bool:
        """Thread-safe check per richiesta"""
        with self._lock:
            self._cleanup_old_requests()
            return len(self.requests) < self.config.safe_max_requests
    
    def record_request(self) -> None:
        """Registra richiesta con timestamp"""
        with self._lock:
            self.requests.append(time.time())
            self._cleanup_old_requests()
    
    def time_until_next_request(self) -> float:
        """Calcola tempo di attesa ottimale"""
        with self._lock:
            self._cleanup_old_requests()
            
            if len(self.requests) < self.config.safe_max_requests:
                return 0.0
            
            oldest_request = self.requests[0]
            window_reset_time = oldest_request + self.config.window_seconds
            return max(0.0, window_reset_time - time.time())
    
    def _cleanup_old_requests(self) -> None:
        """Rimuove richieste fuori dalla finestra temporale"""
        current_time = time.time()
        cutoff_time = current_time - self.config.window_seconds
        
        while self.requests and self.requests[0] <= cutoff_time:
            self.requests.popleft()

class TokenBucketRateLimiter:
    """🪣 Implementazione Token Bucket per burst control (Alternative Strategy)"""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.tokens = float(config.safe_max_requests)
        self.last_refill = time.time()
        self._lock = threading.Lock()
        self.refill_rate = config.safe_max_requests / config.window_seconds
    
    def can_make_request(self) -> bool:
        """Verifica disponibilità token"""
        with self._lock:
            self._refill_tokens()
            return self.tokens >= 1.0
    
    def record_request(self) -> None:
        """Consuma un token"""
        with self._lock:
            self._refill_tokens()
            if self.tokens >= 1.0:
                self.tokens -= 1.0
    
    def time_until_next_request(self) -> float:
        """Tempo per il prossimo token"""
        with self._lock:
            self._refill_tokens()
            if self.tokens >= 1.0:
                return 0.0
            return (1.0 - self.tokens) / self.refill_rate
    
    def _refill_tokens(self) -> None:
        """Riempie bucket con nuovi token"""
        current_time = time.time()
        time_passed = current_time - self.last_refill
        tokens_to_add = time_passed * self.refill_rate
        
        self.tokens = min(
            self.config.safe_max_requests,
            self.tokens + tokens_to_add
        )
        self.last_refill = current_time

class RateLimitRegistry:
    """📚 Registry per configurazioni rate limit (Registry Pattern)"""
    
    # VIP 0 Rate Limits ufficiali Gate.io 2024
    VIP_0_LIMITS = {
        EndpointCategory.PUBLIC: RateLimitConfig(200, 10),
        EndpointCategory.SPOT_ORDER: RateLimitConfig(10, 1),
        EndpointCategory.SPOT_CANCEL: RateLimitConfig(200, 1),
        EndpointCategory.SPOT_OTHER: RateLimitConfig(200, 10),
        EndpointCategory.WALLET_TRANSFER: RateLimitConfig(80, 10),
        EndpointCategory.WALLET_WITHDRAWAL: RateLimitConfig(1, 3),
        EndpointCategory.WALLET_OTHER: RateLimitConfig(200, 10),
        EndpointCategory.FUTURES_ORDER: RateLimitConfig(100, 1),
        EndpointCategory.FUTURES_CANCEL: RateLimitConfig(200, 1),
        EndpointCategory.FUTURES_OTHER: RateLimitConfig(200, 10),
    }
    
    @classmethod
    def get_config(cls, category: EndpointCategory) -> RateLimitConfig:
        """Factory method per ottenere configurazione"""
        return cls.VIP_0_LIMITS[category]
    
    @classmethod
    def get_all_configs(cls) -> Dict[EndpointCategory, RateLimitConfig]:
        """Ottiene tutte le configurazioni"""
        return cls.VIP_0_LIMITS.copy()

class RateLimitManager:
    """🎯 Manager principale per rate limiting (Facade Pattern)"""
    
    def __init__(self, 
                 strategy_type: str = "sliding_window",
                 custom_configs: Optional[Dict[EndpointCategory, RateLimitConfig]] = None):
        """
        Inizializza manager con strategia specifica
        
        Args:
            strategy_type: "sliding_window" o "token_bucket"
            custom_configs: Configurazioni personalizzate (opzionale)
        """
        self.strategy_type = strategy_type
        self.configs = custom_configs or RateLimitRegistry.get_all_configs()
        self.limiters: Dict[EndpointCategory, IRateLimitStrategy] = {}
        self._lock = threading.Lock()
        
        # Inizializza limiters per ogni categoria
        self._initialize_limiters()
        
        logger.info(f"RateLimitManager initialized with {strategy_type} strategy")
    
    def _initialize_limiters(self) -> None:
        """Inizializza limiters con strategy pattern (Factory Method)"""
        for category, config in self.configs.items():
            if self.strategy_type == "token_bucket":
                limiter = TokenBucketRateLimiter(config)
            else:  # default to sliding_window
                limiter = SlidingWindowRateLimiter(config)
            
            self.limiters[category] = limiter
    
    def can_make_request(self, category: EndpointCategory) -> bool:
        """
        Verifica se è possibile effettuare una richiesta
        
        Args:
            category: Categoria endpoint
            
        Returns:
            bool: True se la richiesta è permessa
        """
        if category not in self.limiters:
            logger.warning(f"Unknown category {category}, allowing request")
            return True
        
        return self.limiters[category].can_make_request()
    
    def record_request(self, category: EndpointCategory) -> None:
        """
        Registra una richiesta effettuata
        
        Args:
            category: Categoria endpoint
        """
        if category not in self.limiters:
            return
        
        self.limiters[category].record_request()
        logger.debug(f"Request recorded for {category.value}")
    
    def wait_if_needed(self, category: EndpointCategory) -> float:
        """
        Attende se necessario prima della richiesta
        
        Args:
            category: Categoria endpoint
            
        Returns:
            float: Tempo di attesa effettivo (secondi)
        """
        if category not in self.limiters:
            return 0.0
        
        wait_time = self.limiters[category].time_until_next_request()
        if wait_time > 0:
            logger.info(f"Rate limit wait: {wait_time:.3f}s for {category.value}")
            time.sleep(wait_time)
        
        return wait_time
    
    def get_stats(self) -> Dict[str, any]:
        """
        Ottiene statistiche rate limiting
        
        Returns:
            Dict con statistiche per categoria
        """
        stats = {
            "strategy": self.strategy_type,
            "categories": {}
        }
        
        for category, limiter in self.limiters.items():
            if hasattr(limiter, 'requests'):
                # SlidingWindowRateLimiter
                current_requests = len(limiter.requests)
                max_requests = self.configs[category].safe_max_requests
            elif hasattr(limiter, 'tokens'):
                # TokenBucketRateLimiter  
                current_requests = self.configs[category].safe_max_requests - int(limiter.tokens)
                max_requests = self.configs[category].safe_max_requests
            else:
                current_requests = 0
                max_requests = self.configs[category].safe_max_requests
            
            stats["categories"][category.value] = {
                "current_requests": current_requests,
                "max_requests": max_requests,
                "utilization_percent": (current_requests / max_requests) * 100,
                "can_request": limiter.can_make_request(),
                "wait_time": limiter.time_until_next_request()
            }
        
        return stats

class EndpointClassifier:
    """🏷️ Classificatore per endpoints Gate.io (Classifier Pattern)"""
    
    ENDPOINT_MAPPINGS = {
        # Public endpoints
        '/spot/currencies': EndpointCategory.PUBLIC,
        '/spot/currency_pairs': EndpointCategory.PUBLIC,
        '/spot/tickers': EndpointCategory.PUBLIC,
        '/spot/order_book': EndpointCategory.PUBLIC,
        '/spot/trades': EndpointCategory.PUBLIC,
        '/spot/candlesticks': EndpointCategory.PUBLIC,
        
        # Spot trading
        '/spot/orders': EndpointCategory.SPOT_ORDER,  # POST/PUT
        '/spot/batch_orders': EndpointCategory.SPOT_ORDER,  # POST
        '/spot/cancel_batch_orders': EndpointCategory.SPOT_CANCEL,  # DELETE
        '/spot/accounts': EndpointCategory.SPOT_OTHER,
        '/spot/my_trades': EndpointCategory.SPOT_OTHER,
        
        # Wallet endpoints
        '/wallet/transfers': EndpointCategory.WALLET_TRANSFER,
        '/wallet/sub_account_transfers': EndpointCategory.WALLET_TRANSFER,
        '/withdrawals': EndpointCategory.WALLET_WITHDRAWAL,
        '/wallet/deposits': EndpointCategory.WALLET_OTHER,
        '/wallet/balances': EndpointCategory.WALLET_OTHER,
        
        # Futures endpoints
        '/futures/orders': EndpointCategory.FUTURES_ORDER,
        '/futures/batch_orders': EndpointCategory.FUTURES_ORDER,
        '/futures/cancel_orders': EndpointCategory.FUTURES_CANCEL,
        '/futures/positions': EndpointCategory.FUTURES_OTHER,
    }
    
    @classmethod
    def classify_endpoint(cls, endpoint: str, method: str = "GET") -> EndpointCategory:
        """
        Classifica endpoint in categoria rate limit
        
        Args:
            endpoint: Path dell'endpoint
            method: Metodo HTTP
            
        Returns:
            EndpointCategory appropriata
        """
        # Normalizzo endpoint rimuovendo parametri
        clean_endpoint = endpoint.split('?')[0]
        
        # Mappatura diretta
        if clean_endpoint in cls.ENDPOINT_MAPPINGS:
            category = cls.ENDPOINT_MAPPINGS[clean_endpoint]
            
            # Distinzioni specifiche per metodo HTTP
            if clean_endpoint == '/spot/orders':
                if method in ['POST', 'PUT']:
                    return EndpointCategory.SPOT_ORDER
                elif method == 'DELETE':
                    return EndpointCategory.SPOT_CANCEL
                else:
                    return EndpointCategory.SPOT_OTHER
            
            return category
        
        # Classificazione pattern-based
        if clean_endpoint.startswith('/spot/'):
            if method in ['POST', 'PUT'] and 'orders' in clean_endpoint:
                return EndpointCategory.SPOT_ORDER
            elif method == 'DELETE' and 'orders' in clean_endpoint:
                return EndpointCategory.SPOT_CANCEL
            else:
                return EndpointCategory.SPOT_OTHER
        
        if clean_endpoint.startswith('/wallet/') or clean_endpoint.startswith('/withdrawals'):
            return EndpointCategory.WALLET_OTHER
        
        if clean_endpoint.startswith('/futures/'):
            if method in ['POST', 'PUT'] and 'orders' in clean_endpoint:
                return EndpointCategory.FUTURES_ORDER
            elif method == 'DELETE' and 'orders' in clean_endpoint:
                return EndpointCategory.FUTURES_CANCEL
            else:
                return EndpointCategory.FUTURES_OTHER
        
        # Default to public per endpoint non classificati
        return EndpointCategory.PUBLIC

# Singleton instance per uso globale
_global_rate_limit_manager: Optional[RateLimitManager] = None
_manager_lock = threading.Lock()

def get_global_rate_limit_manager(**kwargs) -> RateLimitManager:
    """
    Factory function per ottenere singleton manager
    
    Returns:
        RateLimitManager: Istanza singleton
    """
    global _global_rate_limit_manager
    
    if _global_rate_limit_manager is None:
        with _manager_lock:
            if _global_rate_limit_manager is None:
                _global_rate_limit_manager = RateLimitManager(**kwargs)
    
    return _global_rate_limit_manager

def reset_global_rate_limit_manager() -> None:
    """Reset singleton per testing"""
    global _global_rate_limit_manager
    with _manager_lock:
        _global_rate_limit_manager = None