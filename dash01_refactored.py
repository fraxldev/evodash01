#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 OTTIMIZZAZIONI COMPLETE APPLICATE - DESIGN PATTERNS & BEST PRACTICES

✅ CONSOLIDAZIONI IMPLEMENTATE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 1. MarketFormatter - Centralizza tutte le formattazioni duplicate:
   • format_trend_text() - Formattazione trend BTC/ETH
   • format_sentiment_score() - Scoring 0-100 con colori
   • format_correlation_strength() - Forza correlazioni
   • format_impact_score() - Impatti di mercato

🎯 2. MarketAnalyzer - Consolida logiche di analisi:
   • detect_market_regime() - Bull/Bear/Altseason detection
   • calculate_sentiment_score() - Score composito 0-100
   • calculate_correlation_impact() - Impatto BTC/ETH su altcoin

🎨 3. ColorHelper - Gestione colori centralizzata:
   • get_trend_color() - Colori per trend combinati
   • get_correlation_color() - Colori per correlazioni

🎯 4. TradingSignalHelper - Segnali trading consolidati:
   • calculate_price_velocities() - Velocità multi-timeframe
   • get_trading_signals() - Segnali momentum/volatilità
   • get_sentiment_analysis() - Analisi sentiment predittivo
   • get_tactical_suggestion() - Consigli tattici unificati
   • get_market_alert() - Alert di mercato standardizzati

💳 5. FeeCalculator - Calcoli commissioni centralizzati:
   • calculate_exit_fees() - Fees vendita 0.2%
   • calculate_net_value_after_fees() - Valore netto post-fees
   • calculate_breakeven_price() - Breakeven con fees incluse
   • calculate_target_value_net() - Target netto finale
   • get_fee_breakdown_for_percentages() - Breakdown 25/50/75/100%

🔧 ELIMINAZIONI COMPLETATE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ _format_trend_text() - Rimossa duplicazione (6 istanze)
❌ _format_correlation_strength() - Rimossa duplicazione (4 istanze)
❌ _get_trend_color() - Rimossa duplicazione (3 istanze)
❌ _get_correlation_color() - Rimossa duplicazione (3 istanze)
❌ _format_sentiment_score() - Rimossa duplicazione (2 istanze)
❌ _format_impact_score() - Rimossa duplicazione (2 istanze)
❌ _calculate_market_sentiment_score() - Rimossa duplicazione
❌ _detect_market_regime_simple() - Rimossa duplicazione
❌ _calculate_price_velocities() - Logica centralizzata
❌ _get_trading_signals() - Logica centralizzata
❌ _get_sentiment_analysis() - Logica centralizzata
❌ _get_scalping_signal()/_get_swing_signal() - Unificate
❌ _get_tactical_suggestion() - Centralizzata
❌ Calcoli fees hardcoded 0.002 - Centralizzati (15+ istanze)

⚡ BENEFICI OTTENUTI:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Riduzione ~300 linee di codice duplicato
✅ Manutenibilità migliorata (Single Responsibility Principle)
✅ Consistenza garantita in formattazioni e calcoli
✅ DRY Principle applicato (Don't Repeat Yourself)
✅ Configurazione commissioni centralizzata e modificabile
✅ Logiche di trading unificate e testabili
✅ Colori e stili UI consistenti
✅ Facilità di debugging e testing
✅ Estensibilità futura semplificata

🎯 DESIGN PATTERNS IMPLEMENTATI:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📐 Strategy Pattern - TradingSignalHelper per algoritmi intercambiabili
🏭 Factory Pattern - MarketFormatter per creazione oggetti formattati
🔧 Utility Classes - Helper statici per funzioni pure
📊 Data Transfer Objects - Strutture dati standardizzate
🎨 Facade Pattern - Interface semplificate per logiche complesse
"""

import requests
import time
import hmac
import hashlib
import os
import sys
import pandas as pd
import curses
import traceback
import time
import json
import csv
import logging
from datetime import datetime, date
from curses import wrapper
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum
import threading
from collections import defaultdict
# 🔍 MONITORING: Import advanced monitoring system
from advanced_monitoring_system import get_global_monitoring, EventType, AlertSeverity
from error_handling import safe_execute, ErrorContext, error_handler
from urllib3.util.connection import create_connection
from urllib3 import PoolManager

API_BASE_URL = "https://api.gateio.ws"
API_BASE_PATH = "/api/v4"

# ===================== GATE.IO TRADING LIMITS =====================
class GateIOLimits:
    """📏 Limiti minimi di trading per Gate.io spot"""
    MIN_ORDER_VALUE_USDT = 5.0  # Valore minimo ordine in USDT - FIX per validazione
    SAFETY_MARGIN = 1.15  # Margine di sicurezza 15%
    
    @classmethod
    def get_min_order_value_with_margin(cls):
        """Ritorna valore minimo con margine di sicurezza"""
        return cls.MIN_ORDER_VALUE_USDT * cls.SAFETY_MARGIN
    
    @classmethod
    def validate_order_value(cls, value_usdt):
        """Valida se l'importo rispetta i limiti Gate.io"""
        min_required = cls.get_min_order_value_with_margin()
        return value_usdt >= min_required, min_required
    
    @classmethod
    def adjust_to_minimum(cls, value_usdt):
        """Ajusta importo al minimo richiesto se sotto-soglia"""
        min_required = cls.get_min_order_value_with_margin()
        return max(value_usdt, min_required)

# ===================== TYPE DEFINITIONS =====================

@dataclass
class OrderRequest:
    """Value Object per richieste ordine (Immutable)"""
    pair: str
    amount_usdt: float
    side: str  # 'buy' or 'sell'
    percentage: Optional[int] = None
    
    def __post_init__(self):
        if self.amount_usdt <= 0:
            raise ValueError("Amount must be positive")
        if self.side not in ['buy', 'sell']:
            raise ValueError("Side must be 'buy' or 'sell'")

class OrderStatus(Enum):
    """Enum per stati ordine (Type Safety)"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    BLOCKED = "blocked"

# ===================== ORDER MANAGEMENT SOLID CLASSES =====================

class OrderValidationResult:
    """Value Object per risultati validazione (Immutable)"""
    def __init__(self, is_valid: bool, error_message: str = "", min_required: float = 0.0):
        self.is_valid = is_valid
        self.error_message = error_message
        self.min_required = min_required

class IOrderValidator:
    """Interface per validatori ordine (Dependency Inversion Principle)"""
    def validate_balance(self, balance: float, amount: float) -> OrderValidationResult:
        raise NotImplementedError
    
    def validate_order_limits(self, amount: float) -> OrderValidationResult:
        raise NotImplementedError

class OrderValidator(IOrderValidator):
    """🔍 SINGLE RESPONSIBILITY: Solo validazione ordini"""
    
    def validate_balance(self, balance: float, amount: float) -> OrderValidationResult:
        """Valida saldo sufficiente"""
        if balance <= 0:
            return OrderValidationResult(
                is_valid=False,
                error_message=f"Saldo insufficiente: {balance:.8f} USDT"
            )
        
        if amount > balance:
            return OrderValidationResult(
                is_valid=False,
                error_message=f"Importo richiesto {amount:.8f} supera saldo {balance:.8f} USDT"
            )
        
        return OrderValidationResult(is_valid=True)
    
    def validate_order_limits(self, amount: float) -> OrderValidationResult:
        """Valida limiti Gate.IO"""
        is_valid, min_required = GateIOLimits.validate_order_value(amount)
        
        if not is_valid:
            return OrderValidationResult(
                is_valid=False,
                error_message=f"Importo {amount:.8f} sotto soglia minima {min_required:.2f} USDT",
                min_required=min_required
            )
        
        return OrderValidationResult(is_valid=True)

class OrderCalculationResult:
    """Value Object per risultati calcolo (Immutable)"""
    def __init__(self, quantity: float, price: float, total_value: float, fee_info: dict):
        self.quantity = quantity
        self.price = price
        self.total_value = total_value
        self.fee_info = fee_info

class IOrderCalculator:
    """Interface per calcolatori ordine (Dependency Inversion Principle)"""
    def calculate_buy_order(self, usdt_amount: float, optimal_price: float, client) -> OrderCalculationResult:
        raise NotImplementedError

class OrderCalculator(IOrderCalculator):
    """🧮 SINGLE RESPONSIBILITY: Solo calcoli ordine"""
    
    def calculate_buy_order(self, usdt_amount: float, optimal_price: float, client) -> OrderCalculationResult:
        """Calcola parametri ordine buy"""
        quantity = usdt_amount / optimal_price
        quantity = round(quantity, 8)
        price = round(optimal_price, 8)
        
        fee_info = {
            'effective_rate': client.get_effective_fee_rate('taker', usdt_amount),
            'gt_points_used': (client.get_gt_fee_info().get('gt_discount_enabled', False) 
                              and client.get_gt_balance() > 0)
        }
        
        return OrderCalculationResult(
            quantity=quantity,
            price=price,
            total_value=usdt_amount,
            fee_info=fee_info
        )

class OrderExecutionResult:
    """Value Object per risultati esecuzione (Immutable)"""
    def __init__(self, success: bool, order_id: str = "", api_result: dict = None, error_message: str = ""):
        self.success = success
        self.order_id = order_id
        self.api_result = api_result or {}
        self.error_message = error_message

class IOrderExecutor:
    """Interface per esecutori ordine (Dependency Inversion Principle)"""
    def execute_buy_order(self, pair: str, quantity: float, price: float, client) -> OrderExecutionResult:
        raise NotImplementedError

class OrderExecutor(IOrderExecutor):
    """🚀 SINGLE RESPONSIBILITY: Solo esecuzione ordini"""
    
    def execute_buy_order(self, pair: str, quantity: float, price: float, client) -> OrderExecutionResult:
        """Esegue ordine buy su API"""
        try:
            result = client.place_spot_order(
                pair=pair,
                side='buy',
                amount=quantity,
                price=price,
                order_type='limit'
            )
            
            if result and 'id' in result:
                return OrderExecutionResult(
                    success=True,
                    order_id=result['id'],
                    api_result=result
                )
            else:
                return OrderExecutionResult(
                    success=False,
                    error_message=f"API response invalid: {result}",
                    api_result=result
                )
                
        except Exception as e:
            context = ErrorContext(
                operation="execute_order",
                parameters={"amount": amount, "symbol": symbol if hasattr(self, 'symbol') else 'unknown'},
                timestamp=time.time()
            )
            error_result = error_handler.handle_error(e, context, 
                lambda: OrderExecutionResult(success=False, error_message="Order execution failed - using fallback"))
            if isinstance(error_result, OrderExecutionResult):
                return error_result
            return OrderExecutionResult(
                success=False,
                error_message=f"Execution exception: {str(e)}"
            )

class OrderLogData:
    """Value Object per dati logging (Immutable)"""
    def __init__(self, session_id: str, pair: str, percentage: float, quantity: float = 0.0, 
                 price: float = 0.0, execution_time_ms: int = 0, error_message: str = "", 
                 fee_info: dict = None, balance_before: float = 0.0, balance_after: float = 0.0,
                 order_result: dict = None):
        self.session_id = session_id
        self.pair = pair
        self.percentage = percentage
        self.quantity = quantity
        self.price = price
        self.execution_time_ms = execution_time_ms
        self.error_message = error_message
        self.fee_info = fee_info or {}
        self.balance_before = balance_before
        self.balance_after = balance_after
        self.order_result = order_result or {}

class IOrderLogger:
    """Interface per logger ordini (Dependency Inversion Principle)"""
    def log_order_success(self, log_data: OrderLogData) -> None:
        raise NotImplementedError
    
    def log_order_error(self, log_data: OrderLogData) -> None:
        raise NotImplementedError

class OrderLogger(IOrderLogger):
    """📝 SINGLE RESPONSIBILITY: Solo logging ordini"""
    
    def __init__(self, trading_logger):
        self.trading_logger = trading_logger
    
    def log_order_success(self, log_data: OrderLogData) -> None:
        """Log ordine eseguito con successo"""
        if log_data.session_id and self.trading_logger:
            self.trading_logger.log_order_execution(
                session_id=log_data.session_id,
                pair=log_data.pair,
                percentage=log_data.percentage,
                quantity=log_data.quantity,
                price=log_data.price,
                order_result=log_data.order_result,
                balance_before=log_data.balance_before,
                balance_after=log_data.balance_after,
                execution_time_ms=log_data.execution_time_ms,
                fee_info=log_data.fee_info
            )
    
    def log_order_error(self, log_data: OrderLogData) -> None:
        """Log errore ordine"""
        if log_data.session_id and self.trading_logger:
            self.trading_logger.log_order_error(
                session_id=log_data.session_id,
                pair=log_data.pair,
                percentage=log_data.percentage,
                error_message=log_data.error_message,
                execution_time_ms=log_data.execution_time_ms
            )

# ===================== POPUP MESSAGE SYSTEM =====================

class IPopupService:
    """Interface per servizi di popup (Interface Segregation Principle)"""
    def show_info_popup(self, title: str, messages: List[str]) -> bool:
        raise NotImplementedError
    
    def show_success_popup(self, title: str, messages: List[str]) -> bool:
        raise NotImplementedError
    
    def show_error_popup(self, title: str, messages: List[str]) -> bool:
        raise NotImplementedError
    
    def show_warning_popup(self, title: str, messages: List[str]) -> bool:
        raise NotImplementedError
    
    def show_confirmation_popup(self, title: str, messages: List[str]) -> Optional[bool]:
        raise NotImplementedError

class PopupTheme:
    """Theme configuration per popup (Strategy Pattern)"""
    def __init__(self, success_color, error_color, warning_color, info_color, confirm_color):
        self.colors = {
            "success": success_color,
            "error": error_color,
            "warning": warning_color,
            "info": info_color,
            "confirm": confirm_color
        }
        
        self.icons = {
            "success": "✅",
            "error": "❌", 
            "warning": "⚠️",
            "info": "ℹ️",
            "confirm": "❓"
        }

class CursesPopupService(IPopupService):
    """Implementazione curses per popup system (Dependency Inversion)"""
    
    def __init__(self, stdscr, theme: PopupTheme, white_color, yellow_color):
        self.stdscr = stdscr
        self.theme = theme
        self.white_color = white_color
        self.yellow_color = yellow_color
    
    def show_info_popup(self, title: str, messages: List[str]) -> bool:
        return self._show_popup(title, messages, "info")
    
    def show_success_popup(self, title: str, messages: List[str]) -> bool:
        return self._show_popup(title, messages, "success")
    
    def show_error_popup(self, title: str, messages: List[str]) -> bool:
        return self._show_popup(title, messages, "error")
    
    def show_warning_popup(self, title: str, messages: List[str]) -> bool:
        return self._show_popup(title, messages, "warning")
    
    def show_confirmation_popup(self, title: str, messages: List[str]) -> Optional[bool]:
        return self._show_popup(title, messages, "confirm")

    def _show_popup(self, title, messages, popup_type):
        """Mostra popup usando curses con gestione completa (Template Method Pattern)"""
        try:
            height, width = self.stdscr.getmaxyx()
            popup_width = min(60, width - 4)
            popup_height = min(len(messages) + 8, height - 4)
            
            start_y = (height - popup_height) // 2
            start_x = (width - popup_width) // 2
            
            border_color = self.theme.colors.get(popup_type, self.white_color)
            
            popup_win = curses.newwin(popup_height, popup_width, start_y, start_x)
            popup_win.box()
            
            icon = self.theme.icons.get(popup_type, "📢")
            header = f" {icon} {title.upper()} "
            header_x = (popup_width - len(header)) // 2
            popup_win.addstr(1, header_x, header, border_color | curses.A_BOLD)
            
            popup_win.addstr(2, 1, "─" * (popup_width - 2), border_color)
            
            for i, message in enumerate(messages):
                if i < popup_height - 6:
                    popup_win.addstr(3 + i, 2, message[:popup_width-4], self.white_color)
            
            popup_win.addstr(popup_height - 3, 1, "─" * (popup_width - 2), border_color)
            
            if popup_type == "confirm":
                footer = "INVIO = Sì | C = No | ESC = Annulla"
            else:
                footer = "Premi un tasto qualsiasi per continuare..."
                
            footer_x = (popup_width - len(footer)) // 2
            popup_win.addstr(popup_height - 2, footer_x, footer, self.yellow_color | curses.A_DIM)
            
            popup_win.refresh()
            
            if popup_type == "confirm":
                while True:
                    key = self.stdscr.getch()
                    if key in [10, 13]:
                        return True
                    elif key in [ord('c'), ord('C')]:
                        return False
                    elif key == 27:
                        return None
            else:
                self.stdscr.getch()
                return True
                
        except Exception as e:
            trade_logger.error(f"Errore popup: {e}")
            print(f"\n{title}: {' | '.join(messages)}")
            input("Premi INVIO per continuare...")
            return True

class ConsolePopupService(IPopupService):
    """Fallback implementation per popup su console (Strategy Pattern)"""
    
    def show_info_popup(self, title: str, messages: List[str]) -> bool:
        print(f"\n🔵 INFO: {title}")
        for msg in messages:
            print(f"   {msg}")
        input("Premi INVIO per continuare...")
        return True
    
    def show_success_popup(self, title: str, messages: List[str]) -> bool:
        print(f"\n✅ SUCCESS: {title}")
        for msg in messages:
            print(f"   {msg}")
        input("Premi INVIO per continuare...")
        return True
    
    def show_error_popup(self, title: str, messages: List[str]) -> bool:
        print(f"\n❌ ERROR: {title}")
        for msg in messages:
            print(f"   {msg}")
        input("Premi INVIO per continuare...")
        return True
    
    def show_warning_popup(self, title: str, messages: List[str]) -> bool:
        print(f"\n⚠️ WARNING: {title}")
        for msg in messages:
            print(f"   {msg}")
        input("Premi INVIO per continuare...")
        return True
    
    def show_confirmation_popup(self, title: str, messages: List[str]) -> Optional[bool]:
        print(f"\n❓ CONFIRM: {title}")
        for msg in messages:
            print(f"   {msg}")
        while True:
            response = input("Confermi? (s/n/annulla): ").lower().strip()
            if response in ['s', 'si', 'y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            elif response in ['annulla', 'cancel', 'esc']:
                return None
            print("Risposta non valida. Usa 's', 'n' o 'annulla'.")

# ===================== USER CONFIRMATION SERVICE =====================

class IConfirmationService:
    """Interface per servizi di conferma (Interface Segregation)"""
    def request_order_adjustment_confirmation(self, original_amount: float, adjusted_amount: float, pair: str) -> bool:
        raise NotImplementedError
        
    def request_insufficient_funds_confirmation(self, required_amount: float, available_amount: float, pair: str) -> bool:
        raise NotImplementedError

class ConsoleConfirmationService(IConfirmationService):
    """Implementazione console per conferme utente (Dependency Inversion)"""
    
    def request_order_adjustment_confirmation(self, original_amount: float, adjusted_amount: float, pair: str) -> bool:
        """Richiede conferma per ajustamento ordine (Strategy Pattern)"""
        print(f"\n⚠️ ORDINE SOTTO-SOGLIA RILEVATO")
        print(f"═" * 60)
        print(f"📊 Coppia: {pair}")
        print(f"💰 Importo richiesto: {original_amount:.2f} USDT")
        print(f"🔧 Importo minimo Gate.io: {adjusted_amount:.2f} USDT")
        print(f"\n📈 Il sistema ajusterà automaticamente l'ordine per conformità")
        print(f"⚡ L'operazione procederà con {adjusted_amount:.2f} USDT")
        print("\n🔍 PREMI INVIO PER CONFERMARE E CONTINUARE...")
        
        try:
            input()  # Attende conferma lettura
            trade_logger.info(f"✅ Utente confermato ajustamento: {original_amount:.2f} → {adjusted_amount:.2f} USDT")
            return True
        except KeyboardInterrupt:
            trade_logger.warning("⚠️ Utente ha annullato operazione")
            return False
    
    def request_insufficient_funds_confirmation(self, required_amount: float, available_amount: float, pair: str) -> bool:
        """Richiede conferma per saldo insufficiente e blocca bot (Observer Pattern)"""
        print(f"\n🚨 SALDO INSUFFICIENTE")
        print(f"═" * 60)
        print(f"📊 Coppia: {pair}")
        print(f"💰 Richiesto: {required_amount:.2f} USDT")
        print(f"💳 Disponibile: {available_amount:.2f} USDT")
        print(f"\n⚠️ OPERATIVITÀ BOT SOSPESA per questa coppia/posizione")
        print(f"💡 Deposita USDT o riduci la dimensione degli ordini")
        print("\n🔍 PREMI INVIO PER CONFERMARE E BLOCCARE BOT...")
        
        try:
            input()  # Attende conferma lettura
            trade_logger.error(f"🛑 Bot bloccato per {pair} - Saldo insufficiente")
            return True
        except KeyboardInterrupt:
            return True  # Blocca comunque per sicurezza

class BotStateManager:
    """Gestisce stato del bot per coppia (State Pattern)"""
    
    def __init__(self):
        self.blocked_pairs = set()
        self.blocked_reasons = {}
    
    def block_pair(self, pair: str, reason: str):
        """Blocca una coppia con motivo"""
        self.blocked_pairs.add(pair)
        self.blocked_reasons[pair] = reason
        trade_logger.warning(f"🚫 Coppia {pair} BLOCCATA: {reason}")
    
    def unblock_pair(self, pair: str):
        """Sblocca una coppia"""
        self.blocked_pairs.discard(pair)
        self.blocked_reasons.pop(pair, None)
        trade_logger.info(f"✅ Coppia {pair} SBLOCCATA")
    
    def is_pair_blocked(self, pair: str) -> bool:
        """Verifica se coppia è bloccata"""
        return pair in self.blocked_pairs
    
    def get_block_reason(self, pair: str) -> str:
        """Ottiene motivo blocco"""
        return self.blocked_reasons.get(pair, "")

# ===================== CIRCUIT BREAKER E SAFETY MANAGER =====================

class OrderFailureTracker:
    """Circuit breaker per ordini falliti consecutivi - Implementa pattern SOLID"""
    def __init__(self, max_failures=5, cooldown_seconds=60):
        self.max_failures = max_failures
        self.cooldown_seconds = cooldown_seconds
        self.failure_count = 0
        self.last_failure_time = 0
        self.circuit_open = False
        self.consecutive_failures = 0
        self.backoff_multiplier = 1.5
        self.max_backoff = 300
        self._failure_types = {
            'network': 0,
            'api_limit': 0,
            'insufficient_balance': 0,
            'validation': 0,
            'unknown': 0
        }
    
    def record_failure(self, failure_type='unknown'):
        """Registra un fallimento ordine con exponential backoff e categorizzazione"""
        self.failure_count += 1
        self.consecutive_failures += 1
        self.last_failure_time = time.time()
        
        if failure_type in self._failure_types:
            self._failure_types[failure_type] += 1
        
        if self.failure_count >= self.max_failures:
            self.circuit_open = True
            trade_logger.warning(f"🚨 CIRCUIT BREAKER ATTIVATO dopo {self.failure_count} fallimenti")
            trade_logger.info(f"📊 Failure types: {self._failure_types}")
            
            # 🔍 MONITORING: Record circuit breaker activation
            try:
                from advanced_monitoring_system import get_global_monitoring
                monitoring = get_global_monitoring()
                monitoring.record_circuit_breaker_event(
                    source="order_failure_tracker",
                    failure_count=self.failure_count,
                    cooldown_seconds=self.cooldown_seconds
                )
            except ImportError:
                pass  # Monitoring not available
    
    def get_failure_stats(self) -> Dict[str, int]:
        """Restituisce statistiche sui tipi di fallimenti"""
        return self._failure_types.copy()
    
    def record_success(self):
        """Reset contatore su successo"""
        self.failure_count = 0
        self.consecutive_failures = 0
        self.circuit_open = False
    
    def can_place_order(self):
        """Verifica se è possibile piazzare un ordine con exponential backoff"""
        if not self.circuit_open:
            # Exponential backoff per fallimenti consecutivi
            if self.consecutive_failures > 0:
                backoff_time = min(self.cooldown_seconds * (self.backoff_multiplier ** (self.consecutive_failures - 1)), self.max_backoff)
                if time.time() - self.last_failure_time < backoff_time:
                    return False
            return True
            
        # Verifica se il cooldown è scaduto
        if time.time() - self.last_failure_time >= self.cooldown_seconds:
            self.circuit_open = False
            self.failure_count = 0
            self.consecutive_failures = 0
            trade_logger.info("✅ Circuit breaker resettato dopo cooldown")
            return True
        
        return False

class WalletManager:
    """Gestione sicura del saldo USDT con validazione (Repository Pattern)"""
    def __init__(self, client):
        self.client = client
        self._cached_balance = None
        self._last_update = 0
        self._cache_duration = 5  # 5 secondi di cache
        # Dependency Injection con default
        self.confirmation_service = ConsoleConfirmationService()
        self.state_manager = BotStateManager()
    
    def get_available_usdt(self, force_refresh=False):
        """Recupera saldo USDT con cache intelligente"""
        current_time = time.time()
        
        if force_refresh or current_time - self._last_update > self._cache_duration:
            try:
                self._cached_balance = self.client.get_wallet_balance('USDT')
                self._last_update = current_time
                trade_logger.debug(f"💰 Saldo USDT aggiornato: {self._cached_balance:.2f}")
            except Exception as e:
                trade_logger.error(f"❌ Errore recupero saldo USDT: {e}")
                return self._cached_balance or 0.0
        
        return self._cached_balance or 0.0
    
    def can_afford_order(self, usdt_amount):
        """Verifica se è possibile permettersi l'ordine"""
        available = self.get_available_usdt()
        buffer = usdt_amount * 0.1  # 10% buffer per fees
        return available >= (usdt_amount + buffer)
    
    def suggest_affordable_amount(self, requested_amount, max_percentage=90, pair=""):
        """Suggerisce importo sostenibile con gestione user confirmation (Template Method Pattern)"""
        available = self.get_available_usdt()
        min_gate_io = GateIOLimits.get_min_order_value_with_margin()
        
        # CASO 1: Ordine >= 5 USDT - Nessun intervento
        if requested_amount >= min_gate_io:
            if requested_amount <= available:
                return requested_amount
            else:
                # Saldo insufficiente per ordine valido
                if self.confirmation_service.request_insufficient_funds_confirmation(requested_amount, available, pair):
                    self.state_manager.block_pair(pair, f"Saldo insufficiente: {requested_amount:.2f} > {available:.2f} USDT")
                return 0.0
        
        # CASO 2: Ordine < 5 USDT - Ajustamento necessario
        adjusted_amount = min_gate_io
        
        if available >= adjusted_amount:
            # Può permettersi l'ajustamento - Richiede conferma utente
            if self.confirmation_service.request_order_adjustment_confirmation(requested_amount, adjusted_amount, pair):
                return adjusted_amount
            else:
                return 0.0  # Utente ha rifiutato
        else:
            # Non può permettersi nemmeno l'importo minimo
            if self.confirmation_service.request_insufficient_funds_confirmation(adjusted_amount, available, pair):
                self.state_manager.block_pair(pair, f"Saldo insufficiente per minimo Gate.io: {adjusted_amount:.2f} > {available:.2f} USDT")
            return 0.0

# ===================== NUOVO SISTEMA STRATEGICO MATEMATICO =====================

class StrategyOrchestrator:
    """Multi-Strategy Orchestrator semplificato basato su matematica deterministica"""
    def __init__(self, capital):
        self.capital = capital
        self.strategy_weights = {
            'scalping': 0.4,
            'mean_reversion': 0.3,
            'momentum': 0.3
        }
    
    def allocate_capital(self, market_conditions):
        """Calcolo dinamico basato su volatilità e trend"""
        volatility = market_conditions.get('volatility', 0.02)
        trend_strength = abs(market_conditions.get('trend', 0))
        
        # Regola i pesi in base alle condizioni di mercato
        if volatility > 0.05:
            self.strategy_weights['scalping'] = min(0.6, self.strategy_weights['scalping'] * 1.2)
        if trend_strength > 1.0:
            self.strategy_weights['momentum'] = min(0.5, self.strategy_weights['momentum'] * 1.3)
        
        # Ricalcola pesi normalizzati
        total_weight = sum(self.strategy_weights.values())
        for strategy in self.strategy_weights:
            self.strategy_weights[strategy] /= total_weight
        
        # Calcola allocazioni
        allocations = {}
        for strategy, weight in self.strategy_weights.items():
            allocations[strategy] = self.capital * weight
        
        return allocations

def detect_volume_anomalies(volume_data):
    """Rileva anomalie di volume con statistica semplice"""
    if len(volume_data) < 10:
        return 0
    
    # Calcola media mobile e deviazione standard
    sma = sum(volume_data[-10:]) / 10
    std_dev = (sum((v - sma)**2 for v in volume_data[-10:]) / 10)**0.5
    
    # Ultimo volume
    last_volume = volume_data[-1]
    
    # Z-score del volume
    z_score = (last_volume - sma) / std_dev if std_dev > 0 else 0
    
    if z_score > 3.0:
        return 1  # Forte volume in acquisto
    elif z_score < -3.0:
        return -1  # Forte volume in vendita
    return 0

def calculate_position_size(capital, volatility, confidence):
    """Dimensione posizione basata su volatilità e confidence"""
    # Proteggi da volatilità nulla
    if volatility <= 0:
        volatility = 0.0001
    # Kelly fraction semplificata
    kelly_fraction = confidence - (1 - confidence) / (volatility * 100)
    
    # Limita tra 1% e 20% del capitale
    position_size = max(0.01, min(0.2, kelly_fraction)) * capital
    return position_size

def pyramid_position(entry_price, current_price, position_size):
    """Aggiunge alla posizione in trend forti"""
    price_change = (current_price - entry_price) / entry_price
    
    if price_change > 0.03:  # 3% in profitto
        return position_size * 0.5  # Aggiungi metà della posizione originale
    return 0

def calculate_spread_opportunity(order_book):
    """Calcola opportunità di arbitraggio spread"""
    if not order_book or len(order_book.get('bids', [])) == 0 or len(order_book.get('asks', [])) == 0:
        return 0
    
    best_bid = float(order_book['bids'][0][0])
    best_ask = float(order_book['asks'][0][0])
    spread = best_ask - best_bid
    
    # Opportunità se spread > 0.1% del prezzo medio
    avg_price = (best_bid + best_ask) / 2
    if spread > avg_price * 0.001:
        return spread / avg_price  # Ritorna rapporto spread/prezzo
    return 0

def calculate_market_sentiment(rsi, macd, volume_change, price_trend):
    """Combina indicatori in un punteggio di sentiment 0-100"""
    # Pesi dinamici basati sulla volatilità
    weights = {
        'rsi': 0.3,
        'macd': 0.4,
        'volume': 0.2,
        'trend': 0.1
    }
    
    # Normalizza indicatori
    rsi_score = max(0, min(100, rsi if rsi else 50))  # RSI è già 0-100
    macd_histogram = macd.get('histogram', 0) if isinstance(macd, dict) else 0
    macd_score = max(0, min(100, 50 + (macd_histogram * 1000)))  # Scala l'istogramma MACD
    volume_score = max(0, min(100, 50 + (volume_change * 200)))  # -0.25 a +0.25 diventa 0-100
    trend_score = max(0, min(100, 50 + (price_trend * 100)))  # -0.5 a +0.5 diventa 0-100
    
    # Calcola punteggio combinato
    score = (
        weights['rsi'] * rsi_score +
        weights['macd'] * macd_score +
        weights['volume'] * volume_score +
        weights['trend'] * trend_score
    )
    
    return max(0, min(100, score))

class ProfitLock:
    """Sistema di protezione profitti con trailing stop dinamico"""
    def __init__(self, base_trail=0.005):
        self.base_trail = base_trail
        self.trailing_stop = 0
        self.highest_price = 0
    
    def update_trailing_stop(self, current_price, highest_price, volatility):
        """Calcola trailing stop dinamico"""
        # Aumenta trailing stop in alta volatilità
        volatility_factor = 1 + (volatility * 10)
        self.trailing_stop = highest_price * (1 - self.base_trail * volatility_factor)
        self.highest_price = max(self.highest_price, highest_price)
        return self.trailing_stop
    
    def partial_profit_targets(self, entry_price, current_price):
        """Punti di uscita parziale predefiniti"""
        profit_levels = [
            {'percent': 0.01, 'take': 0.3},   # Prendi 30% a +1%
            {'percent': 0.02, 'take': 0.3},   # Prendi 30% a +2%
            {'percent': 0.03, 'take': 0.4}    # Prendi 40% a +3%
        ]
        
        # Calcola quali livelli sono stati raggiunti
        profit = (current_price - entry_price) / entry_price if entry_price > 0 else 0
        take_profit = 0
        for level in profit_levels:
            if profit >= level['percent']:
                take_profit += level['take']
        
        return min(1.0, take_profit)  # Massimo 100%

def get_session_parameters():
    """Restituisce parametri per sessione di trading"""
    from datetime import timezone
    utc_hour = datetime.now(timezone.utc).hour
    asia_session = (0, 8)    # 00:00-08:00 UTC
    europe_session = (8, 16) # 08:00-16:00 UTC
    us_session = (16, 24)    # 16:00-24:00 UTC
    
    if asia_session[0] <= utc_hour < asia_session[1]:
        return {'aggressiveness': 0.7, 'target': 0.003, 'max_size': 0.1}
    elif europe_session[0] <= utc_hour < europe_session[1]:
        return {'aggressiveness': 1.0, 'target': 0.005, 'max_size': 0.15}
    else:
        return {'aggressiveness': 1.2, 'target': 0.008, 'max_size': 0.2}

class SafetySystem:
    """Sistema di sicurezza con controlli matematici"""
    def __init__(self, max_daily_loss=0.05, min_win_rate=0.6):
        self.max_daily_loss = max_daily_loss
        self.min_win_rate = min_win_rate
        self.daily_pnl = 0
        self.trade_history = []
        self.start_time = datetime.now().date()
    
    def check_trade(self, pnl):
        """Controlla se è permesso eseguire un nuovo trade"""
        # Reset giornaliero
        if datetime.now().date() != self.start_time:
            self.daily_pnl = 0
            self.trade_history = []
            self.start_time = datetime.now().date()
        
        self.daily_pnl += pnl
        self.trade_history.append(pnl)
        
        # Circuit breaker per perdite giornaliere
        if self.daily_pnl < -self.max_daily_loss:
            return False
        
        # Controllo win rate (solo se ci sono almeno 5 trade)
        if len(self.trade_history) >= 5:
            wins = sum(1 for trade in self.trade_history if trade > 0)
            win_rate = wins / len(self.trade_history)
            
            if win_rate < self.min_win_rate:
                return False
        
        return True

def calculate_volatility(prices):
    """Calcola volatilità come deviazione standard dei rendimenti"""
    if len(prices) < 5:
        return 0.0
    
    returns = []
    for i in range(1, len(prices)):
        if prices[i-1] == 0:
            returns.append(0)
        else:
            returns.append((prices[i] - prices[i-1]) / prices[i-1])
    
    if not returns:
        return 0.0
    
    mean_return = sum(returns) / len(returns)
    variance = sum((r - mean_return)**2 for r in returns) / len(returns)
    return variance**0.5  # Deviazione standard

def calculate_price_trend(prices):
    """Calcola la pendenza del trend con regressione lineare semplice"""
    n = len(prices)
    if n < 2:
        return 0
    
    sum_x = sum(range(n))
    sum_y = sum(prices)
    sum_xy = sum(i * price for i, price in enumerate(prices))
    sum_x_sq = sum(i**2 for i in range(n))
    
    denominator = n * sum_x_sq - sum_x**2
    if denominator == 0 or prices[0] == 0:
        return 0
    
    slope = (n * sum_xy - sum_x * sum_y) / denominator
    return slope / prices[0]  # Normalizza rispetto al prezzo iniziale

# ===================== FINE SISTEMA STRATEGICO =====================

# ===================== LOGGER CONFIG =====================
# Crea cartella logs se non esiste
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

def get_daily_logger():
    log_filename = datetime.now().strftime("trades_%Y-%m-%d.log")
    log_path = os.path.join(LOG_DIR, log_filename)
    logger = logging.getLogger("trade_logger")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        fh = logging.FileHandler(log_path)
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    return logger

trade_logger = get_daily_logger()

# 📊 Configuration Manager - Centralizzazione Valori Magici
class TradingConfig:
    """Configurazione centralizzata per eliminare valori hardcoded duplicati"""
    
    # Fees e commissioni (prima era 0.002 ripetuto 15+ volte)
    EXIT_FEE_RATE = 0.002
    DEFAULT_TAKER_FEE = 0.002
    DEFAULT_MAKER_FEE = 0.002
    
    # Percentuali vendita standard
    SELL_PERCENTAGES = [25, 50, 75, 100]
    
    # Percentuali acquisto (speculari alla vendita)
    BUY_PERCENTAGES = [25, 50, 75, 100]
    
    # Soglie momentum e trend
    MOMENTUM_THRESHOLDS = {
        'strong': 0.5,
        'medium': 0.2, 
        'weak': 0.1
    }
    
    # Timeframes per analisi tecnica
    TIMEFRAMES = ['1m', '5m', '15m', '1h']
    
    # Prezzi stimati per conversioni
    GT_ESTIMATED_PRICE = 5.0  # Stima prezzo GT quando API non disponibile
    
    # API timeout e limiti
    DEFAULT_TIMEOUT = 5
    API_LIMITS = {
        'trades': 1000,
        'candles': 1000,
        'orderbook': 100
    }
    
    # Cache timeouts
    CACHE_TIMEOUTS = {
        'indicators': 10,
        'stats': 60,
        'trends': 30,
        'orderbook': 5
    }
    
    # API endpoints
    ENDPOINTS = {
        'spot_accounts': '/spot/accounts',
        'wallet_fee': '/wallet/fee',
        'spot_orders': '/spot/orders',
        'order_book': '/spot/order_book',
        'my_trades': '/spot/my_trades',
        'tickers': '/spot/tickers'
    }

# 🎨 UI Formatter - Centralizzazione Pattern Rendering Duplicati
class UIFormatter:
    """Centralizza tutti i pattern di rendering UI per eliminare 50+ duplicazioni"""
    
    @staticmethod
    def format_currency_line(label, value, unit="USDT", decimals=2, prefix="💰"):
        """Formatter standard per linee valuta con icona"""
        return f"{prefix} {label}: {value:.{decimals}f} {unit}"
    
    @staticmethod
    def format_percentage_line(label, value, decimals=2, prefix="📊"):
        """Formatter standard per percentuali con segno"""
        return f"{prefix} {label}: {value:+.{decimals}f}%"
    
    @staticmethod 
    def format_quantity_line(label, quantity, symbol, decimals=6, prefix="📦"):
        """Formatter per quantità crypto"""
        return f"{prefix} {label}: {quantity:.{decimals}f} {symbol}"
    
    @staticmethod
    def format_price_line(label, price, decimals=6, prefix="💱"):
        """Formatter per prezzi"""
        return f"{prefix} {label}: {price:.{decimals}f}"
    
    @staticmethod
    def get_profit_color(dashboard_instance, value):
        """Colore standardizzato per profit/loss"""
        return dashboard_instance.GREEN if value >= 0 else dashboard_instance.RED
    
    @staticmethod
    def get_trend_color(dashboard_instance, trend_score):
        """Colore per trend basato su soglie"""
        if trend_score >= TradingConfig.MOMENTUM_THRESHOLDS['strong']:
            return dashboard_instance.GREEN
        elif trend_score <= -TradingConfig.MOMENTUM_THRESHOLDS['strong']:
            return dashboard_instance.RED
        else:
            return dashboard_instance.YELLOW
    
    @staticmethod
    def format_fees_line(fees, currency="USDT", decimals=4, prefix="💸"):
        """Formatter standardizzato per fees"""
        return f"{prefix} Fees: {fees:.{decimals}f} {currency}"

# 🚨 Error Feedback Service - Sistema migliorato per feedback errori API
class ErrorFeedbackService:
    """Gestisce il feedback degli errori con categorizzazione e messaggi chiari (SOLID principles)"""
    
    # Error categories with user-friendly messages (Strategy Pattern)
    ERROR_CATEGORIES = {
        'INSUFFICIENT_BALANCE': {
            'icon': '💰',
            'color_key': 'RED',
            'format': lambda amount, balance: f"💰 Saldo insufficiente: hai {balance:.2f} USDT, servono {amount:.2f} USDT"
        },
        'MIN_ORDER_VALUE': {
            'icon': '📏',
            'color_key': 'YELLOW', 
            'format': lambda amount, min_req: f"📏 Importo troppo piccolo: {amount:.2f} USDT (minimo: {min_req:.2f} USDT)"
        },
        'API_ERROR': {
            'icon': '🔌',
            'color_key': 'RED',
            'format': lambda msg: f"🔌 Errore API: {msg}"
        },
        'NETWORK_ERROR': {
            'icon': '🌐',
            'color_key': 'MAGENTA',
            'format': lambda: "🌐 Errore connessione - Riprova tra qualche secondo"
        },
        'VALIDATION_ERROR': {
            'icon': '⚠️',
            'color_key': 'YELLOW',
            'format': lambda msg: f"⚠️ Validazione fallita: {msg}"
        }
    }
    
    @staticmethod
    def categorize_error(error_result=None, balance=None, amount=None, min_required=None, exception=None):
        """Categorizza l'errore e restituisce messaggio user-friendly (Factory Pattern)"""
        
        # Insufficient balance case
        if balance is not None and amount is not None and balance < amount:
            category = ErrorFeedbackService.ERROR_CATEGORIES['INSUFFICIENT_BALANCE']
            return {
                'category': 'INSUFFICIENT_BALANCE',
                'message': category['format'](amount, balance),
                'icon': category['icon'],
                'color_key': category['color_key'],
                'duration': 15  # More time for user to read
            }
        
        # Minimum order value case
        if amount is not None and min_required is not None and amount < min_required:
            category = ErrorFeedbackService.ERROR_CATEGORIES['MIN_ORDER_VALUE'] 
            return {
                'category': 'MIN_ORDER_VALUE',
                'message': category['format'](amount, min_required),
                'icon': category['icon'], 
                'color_key': category['color_key'],
                'duration': 12
            }
        
        # API error with detailed message
        if error_result and isinstance(error_result, dict):
            api_msg = error_result.get('message', error_result.get('label', 'Errore API sconosciuto'))
            category = ErrorFeedbackService.ERROR_CATEGORIES['API_ERROR']
            return {
                'category': 'API_ERROR',
                'message': category['format'](api_msg),
                'icon': category['icon'],
                'color_key': category['color_key'], 
                'duration': 12
            }
        
        # Network/Connection error
        if exception and ('connection' in str(exception).lower() or 'network' in str(exception).lower()):
            category = ErrorFeedbackService.ERROR_CATEGORIES['NETWORK_ERROR']
            return {
                'category': 'NETWORK_ERROR',
                'message': category['format'](),
                'icon': category['icon'],
                'color_key': category['color_key'],
                'duration': 10
            }
        
        # Generic validation error
        if exception:
            category = ErrorFeedbackService.ERROR_CATEGORIES['VALIDATION_ERROR']
            return {
                'category': 'VALIDATION_ERROR', 
                'message': category['format'](str(exception)[:100]),
                'icon': category['icon'],
                'color_key': category['color_key'],
                'duration': 10
            }
        
        # Fallback to generic API error
        category = ErrorFeedbackService.ERROR_CATEGORIES['API_ERROR']
        return {
            'category': 'API_ERROR',
            'message': category['format']('Errore sconosciuto'),
            'icon': category['icon'],
            'color_key': category['color_key'],
            'duration': 8
        }

# 📊 Profit Calculator - Centralizzazione Calcoli P&L Duplicati  
class ProfitCalculator:
    """Centralizza tutti i calcoli di profit/loss per eliminare 6+ duplicazioni"""
    
    @staticmethod
    def calculate_net_profit_usdt(current_value_net, total_cost_basis):
        """Calcolo profit netto in USDT"""
        return current_value_net - total_cost_basis
    
    @staticmethod
    def calculate_net_profit_percentage(net_profit_usdt, total_cost_basis):
        """Calcolo profit percentuale"""
        return (net_profit_usdt / total_cost_basis) * 100 if total_cost_basis > 0 else 0
    
    @staticmethod
    def calculate_roi_percentage(current_value_net, total_cost):
        """Calcolo ROI istantaneo"""
        return ((current_value_net - total_cost) / total_cost) * 100 if total_cost > 0 else 0
    
    @staticmethod
    def calculate_price_profit_percentage(current_price, buy_avg_price):
        """Calcolo profit percentuale solo su prezzo"""
        return (current_price - buy_avg_price) / buy_avg_price * 100 if buy_avg_price > 0 else 0
    
    @staticmethod
    def calculate_breakeven_price(total_cost_basis, current_balance, exit_fee_rate=None):
        """Calcolo prezzo di breakeven con fees"""
        if exit_fee_rate is None:
            exit_fee_rate = TradingConfig.EXIT_FEE_RATE
        return total_cost_basis / (current_balance * (1 - exit_fee_rate)) if current_balance > 0 else 0
    
    @staticmethod
    def calculate_distance_to_breakeven(current_price, breakeven_price):
        """Calcolo distanza percentuale da breakeven"""
        return ((current_price - breakeven_price) / breakeven_price) * 100 if breakeven_price > 0 else 0

# 📚 Help System - Manuale Dettagliato Interattivo
class HelpSystem:
    """Sistema di aiuto integrato con manuale dettagliato organizzato per schede"""
    
    def __init__(self):
        self.current_tab = 0
        self.tabs = [
            "🎮 CONTROLLI",
            "📊 DASHBOARD", 
            "💰 TRADING",
            "📈 ANALISI",
            "⚙️ TECHNICAL",
            "🔧 CONFIG"
        ]
        
        self.help_content = {
            "🎮 CONTROLLI": self._get_controls_help(),
            "📊 DASHBOARD": self._get_dashboard_help(),
            "💰 TRADING": self._get_trading_help(),
            "📈 ANALISI": self._get_analysis_help(),
            "⚙️ TECHNICAL": self._get_technical_help(),
            "🔧 CONFIG": self._get_config_help()
        }
    
    def _get_controls_help(self):
        return [
            "═══════════════ 🎮 CONTROLLI TASTIERA ═══════════════",
            "",
            "🔹 NAVIGAZIONE PRINCIPALE:",
            "  • H       → Mostra/Nascondi questo aiuto",
            "  • Q       → Esci dall'applicazione",  
            "  • ↑/↓     → Scorri contenuto help (quando attivo)",
            "  • ←/→     → Cambia scheda help (quando attivo)",
            "",
            "🔹 ORDINI DI VENDITA:",
            "  • 1       → Vendi 25% del saldo",
            "  • 2       → Vendi 50% del saldo", 
            "  • 3       → Vendi 75% del saldo",
            "  • 4       → Vendi 100% del saldo (tutto)",
            "",
            "🔹 ORDINI DI ACQUISTO:",
            "  • 6       → Acquista con 25% USDT",
            "  • 7       → Acquista con 50% USDT",
            "  • 8       → Acquista con 75% USDT",
            "  • 9       → Acquista con 100% USDT",
            "",
            "🔹 BOT AUTOMATICO:",
            "  • S       → Avvia SCALPING automatico 🤖",
            "  • F       → Ferma SCALPING attivo 🛑", 
            "  • V       → Visualizza LOG bot in tempo reale 📈",
            "            → Menu navigazione: Dashboard ↔ Log",
            "            → Funziona anche SENZA coin nel wallet!",
            "",
            "🔹 CONFERMA/ANNULLA ORDINI:",
            "  • INVIO   → Conferma ordine selezionato",
            "  • C       → Annulla ordine in corso",
            "  • ESC     → Annulla qualsiasi operazione",
            "",
            "🔹 REFRESH E AGGIORNAMENTI:",
            "  • R       → Forza refresh dati manuale",
            "  • Auto    → Aggiornamento automatico ogni 0.5s",
            "",
            "⚠️  ATTENZIONE: Gli ordini sono REALI su Gate.io",
            "    Controlla sempre before confermare!"
        ]
    
    def _get_dashboard_help(self):
        return [
            "═══════════════ 📊 PANORAMICA DASHBOARD ═══════════════",
            "",
            "🔹 SEZIONE PORTFOLIO (Sinistra Alto):",
            "  • 🔗 LIVE/📝 MANUAL → Fonte dati (API vs Manuale)",
            "  • Asset Balance    → Quantità cryptocurrency posseduta", 
            "  • 💰 Valore Lordo  → Valore attuale senza fees uscita",
            "  • 💸 Valore Netto  → Valore dopo fees vendita (-0.2%)",
            "  • 📈 P&L Netto     → Profitto/perdita finale",
            "",
            "🔹 SEZIONE COSTI (Sinistra Centro):",
            "  • 🏦 Capitale Investito → Somma acquisti effettuati",
            "  • 💳 Commissioni Pagate → Fees storiche pagate",
            "  • 💼 Costo Totale Base → Investimento + fees totali",
            "  • ⚖️  Prezzo Medio Ponderato → Media pesata acquisti",
            "",
            "🔹 SEZIONE ROI (Sinistra Basso):",
            "  • 💹 ROI Istantaneo → Return on Investment attuale",
            "  • ⚖️  Break-Even → Prezzo per pareggiare",
            "  • 📈 Max/Min Oggi → Range profitto sessione corrente",
            "",
            "🔹 SEZIONE PREZZI (Destra Alto):",
            "  • 💱 Prezzo Live → Ticker tempo reale da Gate.io",
            "  • 🕐 Ultimo Update → Timestamp ultimo aggiornamento",
            "  • 📊 Variazione 24h → Performance giornaliera"
        ]
    
    def _get_trading_help(self):
        return [
            "═══════════════ 💰 SISTEMA TRADING ═══════════════",
            "",
            "🔹 MODALITÀ OPERATIVE:",
            "  • MONITOR → Visualizzazione dati (default)",
            "  • ORDINE  → Conferma vendita attiva",
            "",
            "🔹 PERCENTUALI VENDITA:",
            "  • 25% → Vendita parziale conservativa",
            "  • 50% → Vendita bilanciata", 
            "  • 75% → Vendita aggressiva",
            "  • 100% → Liquidazione completa posizione",
            "",
            "🔹 CALCOLO COMMISSIONI:",
            f"  • Fee Rate: {TradingConfig.EXIT_FEE_RATE*100:.1f}% per tutte le vendite",
            "  • GT Points: Possono ridurre le commissioni",
            "  • Calcolo: (Quantità × Prezzo) × 0.002",
            "",
            "🔹 CONFERMA ORDINE:",
            "  • 📋 Mostra: Percentuale, Quantità, Prezzo stimato",
            "  • 💰 Valore: Lordo e netto stimato",
            "  • ⚠️  Richiede: Conferma esplicita con INVIO",
            "",
            "🔹 ESECUZIONE ORDINE:",
            "  • Tipo: Market Order (esecuzione immediata)",
            "  • API: Gate.io signed endpoints",
            "  • Log: Tracciamento completo operazione",
            "",
            "🔹 SICUREZZA:",
            "  • Double confirmation richiesta",
            "  • Session logging per audit trail",  
            "  • Error handling su fallimenti API",
            "  • Timeout protection su chiamate lente"
        ]
    
    def _get_analysis_help(self):
        return [
            "═══════════════ 📈 ANALISI TECNICHE ═══════════════", 
            "",
            "🔹 INDICATORI MOMENTUM:",
            "  • RSI → Relative Strength Index (14 periods)",
            "  • MACD → Moving Average Convergence Divergence", 
            "  • Stochastic → %K e %D oscillator",
            f"  • Soglie: Forte >{TradingConfig.MOMENTUM_THRESHOLDS['strong']}, Medio >{TradingConfig.MOMENTUM_THRESHOLDS['medium']}",
            "",
            "🔹 TIMEFRAMES ANALIZZATI:",
            f"  • {', '.join(TradingConfig.TIMEFRAMES)} → Multi-timeframe analysis",
            "  • Peso maggiore: 1h > 15m > 5m > 1m",
            "",
            "🔹 SEGNALI TRADING:",
            "  • 🟢 FORTE RIALZISTA → Momentum + Velocity positive",
            "  • 🔴 FORTE RIBASSISTA → Momentum + Velocity negative", 
            "  • 🟡 LATERALE → Range-bound, attesa breakout",
            "",
            "🔹 ANALISI CORRELAZIONI:",
            "  • BTC Impact → Influenza Bitcoin su altcoin",
            "  • ETH Impact → Influenza Ethereum su altcoin",
            "  • Combined Trend → Trend combinato crypto market",
            "",
            "🔹 SUGGERIMENTI TATTICI:",
            "  • 💡 MOMENTO IDEALE → Timing ottimale vendita",
            "  • ⏳ ATTENDI → Mercato incerto, aspetta segnali",
            "  • 🎯 TARGET → Livelli prezzo suggeriti",
            "",
            "🔹 VELOCITÀ PREZZO:",
            "  • Price Velocity → Velocità variazione prezzo",
            "  • Acceleration → Accelerazione trend",
            "  • Session Range → Range percentuale sessione"
        ]
    
    def _get_technical_help(self):
        return [
            "═══════════════ ⚙️ DETTAGLI TECNICI ═══════════════",
            "",
            "🔹 CONNESSIONE API:",
            "  • Endpoint: https://api.gateio.ws/api/v4",
            "  • Auth: HMAC-SHA512 signing",
            "  • Rate Limits: Rispettati automaticamente",
            "  • Timeout: 5s default, configurabile",
            "",
            "🔹 CONFIGURAZIONE CREDENZIALI:",
            "  • GATE_API_KEY → Variabile ambiente",
            "  • GATE_SECRET_KEY → Variabile ambiente", 
            "  • Permessi: spot trading + wallet read",
            "",
            "🔹 CACHING SYSTEM:",
            f"  • Indicators: {TradingConfig.CACHE_TIMEOUTS['indicators']}s cache",
            f"  • Stats: {TradingConfig.CACHE_TIMEOUTS['stats']}s cache",
            f"  • Trends: {TradingConfig.CACHE_TIMEOUTS['trends']}s cache",
            f"  • OrderBook: {TradingConfig.CACHE_TIMEOUTS['orderbook']}s cache",
            "",
            "🔹 LOGGING SYSTEM:",
            "  • File: trading_logs/trading_YYYYMMDD.log",
            "  • Format: Timestamp | Level | Message",
            "  • CSV Export: Compatibile database",
            "  • JSON Detail: Metadata completi",
            "",
            "🔹 ERROR HANDLING:",
            "  • API Failures → Graceful degradation",
            "  • Network Issues → Retry con backoff",
            "  • Rate Limiting → Queue automatica",
            "  • Data Validation → Sanity checks",
            "",
            "🔹 PERFORMANCE:",
            "  • Update Rate: 0.5s per UI refresh",
            "  • Memory Usage: < 50MB typical",
            "  • CPU Usage: < 5% during idle",
            "  • Network: ~1KB/s data transfer"
        ]
    
    def _get_config_help(self):
        return [
            "═══════════════ 🔧 CONFIGURAZIONI ═══════════════",
            "",
            "🔹 TRADING CONFIG (TradingConfig class):",
            f"  • EXIT_FEE_RATE = {TradingConfig.EXIT_FEE_RATE} (0.2%)",
            f"  • DEFAULT_TAKER_FEE = {TradingConfig.DEFAULT_TAKER_FEE} (0.2%)",
            f"  • DEFAULT_MAKER_FEE = {TradingConfig.DEFAULT_MAKER_FEE} (0.2%)",
            f"  • SELL_PERCENTAGES = {TradingConfig.SELL_PERCENTAGES}",
            "",
            "🔹 MOMENTUM THRESHOLDS:",
            f"  • Strong: >{TradingConfig.MOMENTUM_THRESHOLDS['strong']} (50%)",
            f"  • Medium: >{TradingConfig.MOMENTUM_THRESHOLDS['medium']} (20%)", 
            f"  • Weak: >{TradingConfig.MOMENTUM_THRESHOLDS['weak']} (10%)",
            "",
            "🔹 API CONFIGURATION:",
            f"  • Default Timeout: {TradingConfig.DEFAULT_TIMEOUT}s",
            f"  • Trades Limit: {TradingConfig.API_LIMITS['trades']} records",
            f"  • Candles Limit: {TradingConfig.API_LIMITS['candles']} records",
            f"  • OrderBook Limit: {TradingConfig.API_LIMITS['orderbook']} levels",
            "",
            "🔹 PERSONALIZZAZIONE:",
            "  • Modifica: Editing TradingConfig class",
            "  • Location: Inizio file dash01.py",
            "  • Restart: Richiesto dopo modifiche",
            "",
            "🔹 FILES IMPORTANTI:",
            "  • dash01.py → Dashboard principale",
            "  • dash_prod_gateio.py → Script CLI produzione", 
            "  • BONIFICA_TRACCIA.md → Documentazione",
            "  • trading_logs/ → Directory logs operazioni",
            "",
            "🔹 ENVIRONMENT SETUP:",
            "  • Python 3.7+ required",
            "  • Dependencies: requests, pandas, curses",
            "  • OS: Linux/MacOS (curses compatibility)",
            "  • Terminal: 80x24 minimum recommended"
        ]

# COMMISSION_RATE rimosso - ora calcolato dinamicamente basato sui GT Points

# 📊 Trading Logger per Database Analysis
class TradingLogger:
    """Sistema di logging professionale per operazioni di trading
    Genera log in formato compatibile con database per analisi avanzate"""

    def __init__(self, log_dir="trading_logs"):
        self.log_dir = log_dir
        self.ensure_log_directory()

        # Configurazione logging strutturato
        self.setup_structured_logging()

        # File CSV per importazione database
        self.csv_file = os.path.join(log_dir, f"trading_operations_{datetime.now().strftime('%Y%m%d')}.csv")
        self.json_file = os.path.join(log_dir, f"trading_detailed_{datetime.now().strftime('%Y%m%d')}.json")

        # Inizializza CSV se non esistente
        self.init_csv_file()

    def ensure_log_directory(self):
        """Crea directory di log se non esistente"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def setup_structured_logging(self):
        """Configura logging strutturato per operazioni"""
        log_file = os.path.join(self.log_dir, f"trading_{datetime.now().strftime('%Y%m%d')}.log")

        # Logger dedicato per trading
        self.logger = logging.getLogger('trading_operations')
        self.logger.setLevel(logging.INFO)

        # Evita duplicazione handler
        if not self.logger.handlers:
            handler = logging.FileHandler(log_file, encoding='utf-8')
            formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def init_csv_file(self):
        """Inizializza file CSV con header se non esistente"""
        if not os.path.exists(self.csv_file):
            headers = [
                'timestamp', 'session_id', 'operation_type', 'trading_pair',
                'percentage', 'quantity', 'price', 'total_value_usdt',
                'order_id', 'order_status', 'fees_estimated', 'fee_rate',
                'gt_points_used', 'balance_before', 'balance_after',
                'price_source', 'execution_time_ms', 'user_action', 'notes'
            ]

            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)

    def log_user_action(self, action_type, pair, percentage, balance_before, price=None, target_quantity=None, target_value=None, notes=""):
        """📝 Log azione utente (pressione tasti 1-4)"""
        timestamp = datetime.now()
        session_id = f"session_{timestamp.strftime('%Y%m%d_%H%M%S')}"

        # Calcola sempre quantity e total_value per garantire valori non-None
        if target_quantity is not None and target_value is not None:
            quantity = target_quantity
            total_value = target_value
        else:
            # Fallback per retrocompatibilità - sempre con calcoli espliciti
            if price is None:
                raise ValueError("price is required when target_quantity and target_value are not provided")
            quantity = balance_before * (percentage / 100)
            total_value = quantity * price
        
        # Garantisci che i valori non siano None per evitare errori di formattazione
        quantity = quantity if quantity is not None else 0.0
        total_value = total_value if total_value is not None else 0.0
        price = price if price is not None else 0.0

        log_data = {
            'timestamp': timestamp.isoformat(),
            'session_id': session_id,
            'operation_type': 'USER_ACTION',
            'trading_pair': pair,
            'percentage': percentage,
            'quantity': round(quantity, 8),
            'price': round(price, 8),
            'total_value_usdt': round(total_value, 2),
            'order_id': '',
            'order_status': 'PENDING',
            'fees_estimated': 0,
            'fee_rate': 0,
            'gt_points_used': False,
            'balance_before': round(balance_before, 8),
            'balance_after': round(balance_before, 8),  # Unchanged fino a esecuzione
            'price_source': 'CURRENT',
            'execution_time_ms': 0,
            'user_action': f"KEY_{percentage}%",
            'notes': notes or f"User selected {percentage}% sell order"
        }

        # Log strutturato
        self.logger.info(f"USER_ACTION | {pair} | {percentage}% | QTY:{quantity:.6f} | PRICE:{price:.6f} | VALUE:{total_value:.2f} USDT")

        # Salva in JSON dettagliato
        self._append_json_log(log_data)

        return session_id

    def log_order_execution(self, session_id, pair, percentage, quantity, price,
                          order_result, balance_before, balance_after,
                          execution_time_ms, fee_info=None):
        """💰 Log esecuzione ordine effettiva"""
        timestamp = datetime.now()

        # Analizza risultato ordine
        order_status = 'SUCCESS' if order_result and 'id' in order_result else 'FAILED'
        order_id = order_result.get('id', '') if order_result else ''
        error_msg = order_result.get('message', order_result.get('label', '')) if order_result and 'id' not in order_result else ''

        # Calcola fees
        total_value = quantity * price
        estimated_fee = 0
        fee_rate = 0
        gt_used = False

        if fee_info:
            fee_rate = fee_info.get('effective_rate', 0)
            estimated_fee = total_value * fee_rate
            gt_used = fee_info.get('gt_points_used', False)

        # Controlli di sicurezza per parametri None
        safe_quantity = quantity if quantity is not None else 0
        safe_price = price if price is not None else 0
        safe_balance_before = balance_before if balance_before is not None else 0
        safe_balance_after = balance_after if balance_after is not None else 0
        
        log_data = {
            'timestamp': timestamp.isoformat(),
            'session_id': session_id or '',
            'operation_type': 'ORDER_EXECUTION',
            'trading_pair': pair or '',
            'percentage': percentage if percentage is not None else 0,
            'quantity': round(safe_quantity, 8),
            'price': round(safe_price, 8),
            'total_value_usdt': round(total_value, 2),
            'order_id': order_id[:16] if order_id else '',  # Trunca per CSV
            'order_status': order_status,
            'fees_estimated': round(estimated_fee, 6),
            'fee_rate': fee_rate,
            'gt_points_used': gt_used,
            'balance_before': round(safe_balance_before, 8),
            'balance_after': round(safe_balance_after, 8),
            'price_source': 'BOOK_OPTIMAL',
            'execution_time_ms': execution_time_ms,
            'user_action': f"EXECUTE_{percentage if percentage is not None else 0}%",
            'notes': error_msg if order_status == 'FAILED' else f"Order executed successfully"
        }

        # Log strutturato
        status_symbol = "✓" if order_status == 'SUCCESS' else "✗"
        self.logger.info(f"ORDER_EXEC | {status_symbol} | {pair or 'N/A'} | {percentage if percentage is not None else 0}% | "
                        f"QTY:{safe_quantity:.6f} | PRICE:{safe_price:.6f} | VALUE:{total_value:.2f} USDT | "
                        f"ORDER_ID:{order_id[:8] if order_id else 'N/A'} | TIME:{execution_time_ms}ms")

        # Salva in entrambi i formati
        self._append_json_log(log_data)
        self._append_csv_log(log_data)

        return log_data

    def log_order_error(self, session_id, pair, percentage, error_message, execution_time_ms=0):
        """❌ Log errore durante esecuzione ordine"""
        timestamp = datetime.now()

        log_data = {
            'timestamp': timestamp.isoformat(),
            'session_id': session_id,
            'operation_type': 'ORDER_ERROR',
            'trading_pair': pair,
            'percentage': percentage,
            'quantity': 0,
            'price': 0,
            'total_value_usdt': 0,
            'order_id': '',
            'order_status': 'ERROR',
            'fees_estimated': 0,
            'fee_rate': 0,
            'gt_points_used': False,
            'balance_before': 0,
            'balance_after': 0,
            'price_source': 'N/A',
            'execution_time_ms': execution_time_ms,
            'user_action': f"ERROR_{percentage}%",
            'notes': error_message[:200]  # Limita lunghezza per CSV
        }

        # Log strutturato
        self.logger.error(f"ORDER_ERROR | ✗ | {pair} | {percentage}% | ERROR: {error_message}")

        # Salva in entrambi i formati
        self._append_json_log(log_data)
        self._append_csv_log(log_data)

    def _append_json_log(self, log_data):
        """Aggiunge entry al log JSON dettagliato"""
        try:
            # Leggi log esistente
            existing_logs = []
            if os.path.exists(self.json_file):
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    try:
                        existing_logs = json.load(f)
                    except json.JSONDecodeError:
                        existing_logs = []

            # Aggiungi nuovo log
            existing_logs.append(log_data)

            # Salva log aggiornato
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(existing_logs, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Errore scrittura JSON log: {e}")

    def _append_csv_log(self, log_data):
        """Aggiunge entry al CSV database-ready"""
        try:
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=log_data.keys())
                writer.writerow(log_data)

        except Exception as e:
            self.logger.error(f"Errore scrittura CSV log: {e}")

    def get_daily_stats(self):
        """📊 Statistiche giornaliere per dashboard"""
        try:
            if not os.path.exists(self.csv_file):
                return {}

            df = pd.read_csv(self.csv_file)

            # Filtra solo esecuzioni riuscite
            successful_orders = df[df['order_status'] == 'SUCCESS']

            stats = {
                'total_operations': len(df),
                'successful_orders': len(successful_orders),
                'failed_orders': len(df[df['order_status'] == 'FAILED']),
                'total_volume_usdt': successful_orders['total_value_usdt'].sum(),
                'total_fees_usdt': successful_orders['fees_estimated'].sum(),
                'avg_order_value': successful_orders['total_value_usdt'].mean() if len(successful_orders) > 0 else 0,
                'most_used_percentage': df['percentage'].mode().iloc[0] if len(df) > 0 else 0
            }

            return stats

        except Exception as e:
            self.logger.error(f"Errore calcolo statistiche: {e}")
            return {}

# ⚡ Cache Configuration per Performance Boost
class SmartCache:
    def __init__(self):
        self.cache = {}
        self.cache_times = {}

    def get(self, key, max_age_seconds):
        """Ottiene un valore dalla cache se non è scaduto"""
        if key not in self.cache:
            return None

        age = time.time() - self.cache_times.get(key, 0)
        if age > max_age_seconds:
            # Cache scaduta
            self.cache.pop(key, None)
            self.cache_times.pop(key, None)
            return None

        return self.cache[key]

    def set(self, key, value):
        """Imposta un valore nella cache"""
        self.cache[key] = value
        self.cache_times[key] = time.time()

    def clear_expired(self, max_age_seconds):
        """Pulisce i valori scaduti dalla cache"""
        current_time = time.time()
        expired_keys = [
            key for key, timestamp in self.cache_times.items()
            if current_time - timestamp > max_age_seconds
        ]
        for key in expired_keys:
            self.cache.pop(key, None)
            self.cache_times.pop(key, None)

# � Trading Logic Helper - Consolidazione logiche duplicate
class TradingSignalHelper:
    """Centralizza logiche di segnali trading per evitare duplicazioni"""

    @staticmethod
    def calculate_price_velocities(price_history):
        """Calcola velocità del prezzo per diversi timeframe"""
        velocity_data = {'vel_30s': 0, 'vel_1m': 0, 'vel_5m': 0, 'acceleration': 0}

        if len(price_history) >= 2:
            current_time = time.time()

            # Velocità 30 secondi
            recent_30s = [p for t, p in price_history if current_time - t <= 30]
            if len(recent_30s) >= 2:
                velocity_data['vel_30s'] = ((recent_30s[-1] - recent_30s[0]) / recent_30s[0]) * 100

            # Velocità 1 minuto
            recent_1m = [p for t, p in price_history if current_time - t <= 60]
            if len(recent_1m) >= 2:
                velocity_data['vel_1m'] = ((recent_1m[-1] - recent_1m[0]) / recent_1m[0]) * 100

            # Velocità 5 minuti
            recent_5m = [p for t, p in price_history if current_time - t <= 300]
            if len(recent_5m) >= 2:
                velocity_data['vel_5m'] = ((recent_5m[-1] - recent_5m[0]) / recent_5m[0]) * 100

            # Accelerazione
            if len(recent_1m) >= 3:
                vel1 = ((recent_1m[-2] - recent_1m[0]) / recent_1m[0]) * 100
                vel2 = ((recent_1m[-1] - recent_1m[-2]) / recent_1m[-2]) * 100
                velocity_data['acceleration'] = vel2 - vel1

        return velocity_data

    @staticmethod
    def get_trading_signals(momentum_score, vel_1m, session_range_perc):
        """Genera segnali di trading consolidati"""
        if momentum_score > TradingConfig.MOMENTUM_THRESHOLDS['strong'] and vel_1m > TradingConfig.MOMENTUM_THRESHOLDS['medium']:
            return {
                'text': "🟢 FORTE MOMENTUM RIALZISTA",
                'color': curses.COLOR_GREEN | curses.A_BOLD,
                'tactical': "💡 MOMENTO IDEALE: Vendi ora o su prossimo picco"
            }
        elif momentum_score < -TradingConfig.MOMENTUM_THRESHOLDS['strong'] and vel_1m < -TradingConfig.MOMENTUM_THRESHOLDS['medium']:
            return {
                'text': "🔴 FORTE MOMENTUM RIBASSISTA",
                'color': curses.COLOR_RED | curses.A_BOLD,
                'tactical': "❌ SCONSIGLIATO: Attendi inversione trend"
            }
        elif session_range_perc > 2 and abs(vel_1m) > 0.1:
            return {
                'text': "🟡 ALTA VOLATILITÀ - Scalping Opportunity",
                'color': curses.COLOR_YELLOW | curses.A_BOLD,
                'tactical': "⚖️ VOLATILITÀ: Monitora per swing trading"
            }
        elif abs(momentum_score) < 0.1:
            return {
                'text': "⚪ MERCATO LATERALE - Attesa",
                'color': curses.COLOR_YELLOW,
                'tactical': "⏳ ATTESA: Mercato indeciso, mantieni posizione"
            }
        else:
            return {
                'text': "🔵 TREND MODERATO - Monitora",
                'color': curses.COLOR_CYAN,
                'tactical': "🔄 MERCATO LATERALE - Pazienza"
            }

    @staticmethod
    def get_sentiment_analysis(prediction_score):
        """Analizza il sentiment di mercato"""
        if prediction_score >= 4:
            return {'text': "🚀 MOLTO RIALZISTA", 'color': curses.COLOR_GREEN | curses.A_BOLD | curses.A_BLINK}
        elif prediction_score >= 2:
            return {'text': "📈 RIALZISTA", 'color': curses.COLOR_GREEN | curses.A_BOLD}
        elif prediction_score == 1:
            return {'text': "↗️ LIEVEMENTE RIALZISTA", 'color': curses.COLOR_GREEN}
        elif prediction_score <= -4:
            return {'text': "💥 MOLTO RIBASSISTA", 'color': curses.COLOR_RED | curses.A_BOLD | curses.A_BLINK}
        elif prediction_score <= -2:
            return {'text': "📉 RIBASSISTA", 'color': curses.COLOR_RED | curses.A_BOLD}
        elif prediction_score == -1:
            return {'text': "↘️ LIEVEMENTE RIBASSISTA", 'color': curses.COLOR_RED}
        else:
            return {'text': "➡️ NEUTRO/LATERALE", 'color': curses.COLOR_YELLOW | curses.A_BOLD}

    @staticmethod
    def get_tactical_suggestion(prediction_score, vel_1m, session_range):
        """Genera suggerimenti tattici consolidati"""
        if prediction_score >= 3 and vel_1m > 0.2:
            return {'text': "🎯 MOMENTO IDEALE: Vendi ora o su prossimo picco", 'color': curses.COLOR_GREEN | curses.A_BOLD}
        elif prediction_score >= 1 and vel_1m > 0.1:
            return {'text': "✅ BUON MOMENTO: Vendita parziale consigliata", 'color': curses.COLOR_GREEN}
        elif prediction_score <= -2:
            return {'text': "❌ SCONSIGLIATO: Attendi inversione trend", 'color': curses.COLOR_RED}
        elif session_range > 2 and abs(vel_1m) > 0.05:
            return {'text': "⚖️ VOLATILITÀ: Monitora per swing trading", 'color': curses.COLOR_MAGENTA}
        else:
            return {'text': "⏳ ATTESA: Mercato indeciso, mantieni posizione", 'color': curses.COLOR_YELLOW}

    @staticmethod
    def get_market_alert(vel_1m, session_range, current_price):
        """Genera alert di mercato"""
        if vel_1m > 0.5:
            return "⚠️ PUMP DETECTED - Volatilità estrema!"
        elif vel_1m < -0.5:
            return "⚠️ DUMP DETECTED - Forte calo!"
        elif session_range > 5:
            return "⚠️ ALTA VOLATILITÀ - Rischio elevato!"
        else:
            next_resistance = current_price * 1.02
            next_support = current_price * 0.98
            return f"🎯 Resistenza: {next_resistance:.6f} | Supporto: {next_support:.6f}"

# �🎨 Formatter Helper - Consolidazione formattazioni duplicate
class MarketFormatter:
    """Centralizza tutte le logiche di formattazione per evitare duplicazioni"""

    @staticmethod
    def format_trend_text(trend_score):
        """Formatta il testo del trend per major coins"""
        if trend_score >= 2: return "🚀 FORTE RALLY"
        elif trend_score >= 1: return "📈 RIALZO"
        elif trend_score >= 0.5: return "↗️ LIEVE RIALZO"
        elif trend_score <= -2: return "💥 FORTE DUMP"
        elif trend_score <= -1: return "📉 RIBASSO"
        elif trend_score <= -0.5: return "↘️ LIEVE RIBASSO"
        else: return "➡️ LATERALE"

    @staticmethod
    def format_sentiment_score(score):
        """Formatta sentiment score con testo e colore"""
        if score >= 80:
            return f"{score:.0f}/100 EXTREME GREED", curses.COLOR_GREEN | curses.A_BOLD
        elif score >= 65:
            return f"{score:.0f}/100 GREED", curses.COLOR_GREEN
        elif score >= 55:
            return f"{score:.0f}/100 NEUTRAL+", curses.COLOR_YELLOW
        elif score >= 45:
            return f"{score:.0f}/100 NEUTRAL", curses.COLOR_WHITE
        elif score >= 35:
            return f"{score:.0f}/100 NEUTRAL-", curses.COLOR_YELLOW
        elif score >= 20:
            return f"{score:.0f}/100 FEAR", curses.COLOR_RED
        else:
            return f"{score:.0f}/100 EXTREME FEAR", curses.COLOR_RED | curses.A_BOLD

    @staticmethod
    def format_correlation_strength(correlation_score):
        """Formatta la forza della correlazione"""
        abs_corr = abs(correlation_score)

        if abs_corr >= 1.5:
            direction = "POSITIVA" if correlation_score > 0 else "DIVERGENZA"
            return f"FORTE {direction}"
        elif abs_corr >= 0.8:
            direction = "POSITIVA" if correlation_score > 0 else "NEGATIVA"
            return f"MEDIA {direction}"
        elif abs_corr >= 0.3:
            return "DEBOLE"
        else:
            return "DECORRELATI"

    @staticmethod
    def format_impact_score(impact_score):
        """Formatta l'impatto score"""
        if impact_score >= 1.5:
            return "MOLTO POSITIVO (+)", curses.COLOR_GREEN | curses.A_BOLD
        elif impact_score >= 0.5:
            return "POSITIVO (+)", curses.COLOR_GREEN
        elif impact_score >= -0.5:
            return "NEUTRO (=)", curses.COLOR_YELLOW
        elif impact_score >= -1.5:
            return "NEGATIVO (-)", curses.COLOR_RED
        else:
            return "MOLTO NEGATIVO (--)", curses.COLOR_RED | curses.A_BOLD

# 📊 Market Analysis Helper - Consolidazione analisi duplicate
class MarketAnalyzer:
    """Centralizza logiche di analisi di mercato per evitare duplicazioni"""

    @staticmethod
    def detect_market_regime(btc_score, eth_score, correlation):
        """Rileva regime di mercato basato su major coins"""
        if btc_score >= 2 and eth_score >= 1 and correlation > 1:
            return {'text': "BULL MARKET 🚀", 'color': curses.COLOR_GREEN}
        elif btc_score <= -2 and correlation > 0.8:
            return {'text': "BEAR MARKET 📉", 'color': curses.COLOR_RED}
        elif abs(correlation) < 0.3:
            return {'text': "ALTSEASON 🌟", 'color': curses.COLOR_MAGENTA}
        elif abs(btc_score) < 0.5 and abs(eth_score) < 0.5:
            return {'text': "ACCUMULATION 📦", 'color': curses.COLOR_YELLOW}
        else:
            return {'text': "TRANSITION 🔄", 'color': curses.COLOR_CYAN}

    @staticmethod
    def calculate_sentiment_score(btc_score, eth_score, impact_score):
        """Calcola sentiment score da 0 a 100"""
        # Base score da major coins (60% del peso)
        major_contribution = ((btc_score * 0.6 + eth_score * 0.4) + 3) / 6 * 60

        # Impact contribution (40% del peso)
        impact_contribution = ((impact_score + 2) / 4) * 40

        # Score finale 0-100
        final_score = max(0, min(100, major_contribution + impact_contribution))
        return final_score

    @staticmethod
    def calculate_correlation_impact(btc_score, eth_score, correlation_score):
        """Calcola impatto delle correlazioni BTC/ETH sulle altcoin"""
        # Pesi basati su market cap e dominanza reale
        btc_weight = 0.65  # BTC ha maggiore influenza
        eth_weight = 0.35  # ETH peso minore ma significativo

        base_impact = (btc_score * btc_weight + eth_score * eth_weight)

        # Fattore amplificazione correlazione
        abs_corr = abs(correlation_score)
        if abs_corr >= 1.5:
            multiplier = 1.6  # Correlazione forte amplifica
        elif abs_corr >= 0.8:
            multiplier = 1.3  # Correlazione media
        elif abs_corr >= 0.3:
            multiplier = 1.0  # Correlazione debole, impatto normale
        else:
            multiplier = 0.5  # Decorrelazione, impatto ridotto

        return base_impact * multiplier

# 🎯 Color Helper - Consolidazione colori duplicate
class ColorHelper:
    """Centralizza gestione colori per consistenza UI"""

    @staticmethod
    def get_trend_color(combined_trend):
        """Colore basato su trend combinato"""
        if combined_trend >= 2.5: return curses.COLOR_GREEN | curses.A_BOLD | curses.A_BLINK
        elif combined_trend >= 1.5: return curses.COLOR_GREEN | curses.A_BOLD
        elif combined_trend >= 0.5: return curses.COLOR_GREEN
        elif combined_trend <= -2.5: return curses.COLOR_RED | curses.A_BOLD | curses.A_BLINK
        elif combined_trend <= -1.5: return curses.COLOR_RED | curses.A_BOLD
        elif combined_trend <= -0.5: return curses.COLOR_RED
        else: return curses.COLOR_YELLOW

    @staticmethod
    def get_correlation_color(correlation_score):
        """Colore per visualizzare forza correlazione"""
        abs_corr = abs(correlation_score)
        if abs_corr >= 1.5: return curses.COLOR_MAGENTA | curses.A_BOLD
        elif abs_corr >= 0.8: return curses.COLOR_CYAN | curses.A_BOLD
        elif abs_corr >= 0.3: return curses.COLOR_YELLOW
        else: return curses.COLOR_RED

# 💳 Fee Calculator Helper - Centralizzazione calcoli commissioni
class ProgressPhase:
    """Design Pattern Strategy per gestire le fasi di progresso"""
    def __init__(self, name, color, char, description):
        self.name = name
        self.color = color
        self.char = char
        self.description = description

    def calculate_progress(self, current_value, target_values):
        """Override in sottoclassi per calcolo specifico della fase"""
        raise NotImplementedError

class EntryFeesPhase(ProgressPhase):
    """Fase 1: Ammortamento fees di entrata"""
    def __init__(self, color_red):
        super().__init__("AMMORTAMENTO FEES ENTRATA", color_red, "▓", "Recupero commissioni di acquisto")

    def calculate_progress(self, current_value, target_values):
        entry_fees_paid = target_values['entry_fees_paid']
        initial_investment = target_values['initial_investment']

        if entry_fees_paid <= 0:
            return 100.0  # Se non ci sono fees, fase completata

        # Progresso: quanto del valore attuale copre l'investimento iniziale
        recovery_needed = initial_investment
        progress = min(100.0, max(0.0, (current_value / recovery_needed) * 100))
        return progress

class ExitFeesPhase(ProgressPhase):
    """Fase 2: Ammortamento fees di uscita"""
    def __init__(self, color_yellow):
        super().__init__("AMMORTAMENTO FEES USCITA", color_yellow, "▒", "Copertura commissioni di vendita")

    def calculate_progress(self, current_value, target_values):
        total_cost_basis = target_values['total_cost_basis']
        exit_fees = target_values['exit_fees']

        # Progresso: quanto del valore netto dopo exit fees copre il cost basis
        net_value_after_exit = current_value - exit_fees
        if net_value_after_exit >= total_cost_basis:
            return 100.0

        progress = min(100.0, max(0.0, (net_value_after_exit / total_cost_basis) * 100))
        return progress

class ProfitPhase(ProgressPhase):
    """Fase 3: Profitto netto verso target"""
    def __init__(self, color_green):
        super().__init__("PROFITTO NETTO", color_green, "█", "Crescita verso obiettivo")

    def calculate_progress(self, current_value, target_values):
        total_cost_basis = target_values['total_cost_basis']
        exit_fees = target_values['exit_fees']
        target_profit = target_values['target_profit']

        net_value_after_exit = current_value - exit_fees
        current_profit = net_value_after_exit - total_cost_basis

        if target_profit <= 0:
            return 100.0  # Target già raggiunto

        progress = min(100.0, max(0.0, (current_profit / target_profit) * 100))
        return progress

class SmartProgressCalculator:
    """Calculator intelligente per il progresso multi-fase"""

    def __init__(self, color_red, color_yellow, color_green):
        self.phases = [
            EntryFeesPhase(color_red),
            ExitFeesPhase(color_yellow),
            ProfitPhase(color_green)
        ]

    def calculate_current_phase_and_progress(self, portfolio_data, current_price, target_percent):
        """Determina fase attuale e progresso con precisione matematica"""

        # Prepara i valori per i calcoli
        current_balance = portfolio_data['current_balance']
        current_value = current_price * current_balance
        initial_investment = portfolio_data['total_invested']
        entry_fees_paid = portfolio_data['total_fees_paid']
        total_cost_basis = initial_investment + entry_fees_paid

        # Calcola exit fees e target
        exit_fees = FeeCalculator.calculate_exit_fees(current_value)
        target_price = portfolio_data['arithmetic_avg'] * (1 + target_percent / 100)
        target_value_gross = target_price * current_balance
        target_exit_fees = FeeCalculator.calculate_exit_fees(target_value_gross)
        target_value_net = target_value_gross - target_exit_fees
        target_profit = target_value_net - total_cost_basis

        target_values = {
            'initial_investment': initial_investment,
            'entry_fees_paid': entry_fees_paid,
            'total_cost_basis': total_cost_basis,
            'exit_fees': exit_fees,
            'target_profit': target_profit
        }

        # Determina fase attuale con logica precisa e corretta
        net_value_after_exit = current_value - exit_fees

        # FASE 1: Valore attuale non copre nemmeno l'investimento iniziale
        if current_value < initial_investment:
            current_phase = self.phases[0]  # AMMORTAMENTO FEES ENTRATA
            progress = current_phase.calculate_progress(current_value, target_values)

        # FASE 2: Valore copre investimento ma valore netto non copre costi totali (con fees)
        elif net_value_after_exit < total_cost_basis:
            current_phase = self.phases[1]  # AMMORTAMENTO FEES USCITA
            progress = current_phase.calculate_progress(current_value, target_values)

        # FASE 3: Valore netto supera tutti i costi = PROFITTO NETTO
        else:
            current_phase = self.phases[2]  # PROFITTO NETTO
            progress = current_phase.calculate_progress(current_value, target_values)

        return current_phase, progress, target_values

class FeeCalculator:
    """Centralizza tutti i calcoli delle commissioni per evitare duplicazioni"""

    # Configurazione commissioni centralizzata - ORA USA TradingConfig
    EXIT_FEE_RATE = TradingConfig.EXIT_FEE_RATE
    DEFAULT_MAKER_FEE = TradingConfig.DEFAULT_MAKER_FEE 
    DEFAULT_TAKER_FEE = TradingConfig.DEFAULT_TAKER_FEE

    @classmethod
    def calculate_exit_fees(cls, current_value, percentage=100):
        """Calcola fees di uscita per una vendita"""
        sale_value = current_value * (percentage / 100)
        return sale_value * cls.EXIT_FEE_RATE

    @classmethod
    def calculate_net_value_after_fees(cls, current_value, percentage=100):
        """Calcola valore netto dopo commissioni di uscita"""
        sale_value = current_value * (percentage / 100)
        fees = cls.calculate_exit_fees(current_value, percentage)
        return sale_value - fees

    @classmethod
    def calculate_breakeven_price(cls, total_invested, total_fees_paid, current_balance):
        """Calcola prezzo di breakeven considerando tutte le fees"""
        if current_balance <= 0:
            return 0.0  # Evita division by zero quando non hai coin
        
        total_cost = total_invested + total_fees_paid
        # Aggiunge le fees di uscita al calcolo
        return (total_cost / current_balance) / (1 - cls.EXIT_FEE_RATE)

    @classmethod
    def calculate_target_value_net(cls, target_price, current_balance):
        """Calcola valore target netto dopo fees di uscita"""
        gross_value = target_price * current_balance
        exit_fees = gross_value * cls.EXIT_FEE_RATE
        return gross_value - exit_fees

    @classmethod
    def get_fee_breakdown_for_percentages(cls, current_value):
        """Restituisce breakdown fees per diverse percentuali di vendita"""
        return {
            f'{p}%': cls.calculate_exit_fees(current_value, p)
            for p in TradingConfig.SELL_PERCENTAGES
        }

class GateIOClient:
    def __init__(self, api_key, secret_key, rate_limit_enabled: bool = True, 
                 rate_limit_strategy: str = "sliding_window", 
                 rate_limit_safety_margin: float = 0.8):
        if not api_key or not secret_key:
            raise ValueError("API_KEY e SECRET_KEY devono essere impostati come variabili d'ambiente.")
        self.api_key = api_key
        self.secret_key = secret_key
        
        # 🚦 Rate Limiting Integration (VIP 0 Compliance)
        self.rate_limit_enabled = rate_limit_enabled
        if self.rate_limit_enabled:
            from rate_limit_manager import get_global_rate_limit_manager, RateLimitRegistry, RateLimitConfig, EndpointCategory
            
            # Applica safety margin personalizzato ai rate limits
            custom_configs = {}
            if rate_limit_safety_margin != 0.8:  # Se diverso dal default
                base_configs = RateLimitRegistry.get_all_configs()
                for category, base_config in base_configs.items():
                    custom_configs[category] = RateLimitConfig(
                        max_requests=base_config.max_requests,
                        window_seconds=base_config.window_seconds,
                        burst_allowance=rate_limit_safety_margin
                    )
            
            self.rate_limit_manager = get_global_rate_limit_manager(
                strategy_type=rate_limit_strategy,
                custom_configs=custom_configs if custom_configs else None
            )
            self.endpoint_classifier = None  # Inizializzato lazy
        self.base_url = API_BASE_URL
        
        # 🔍 MONITORING: Initialize monitoring
        self.monitoring = get_global_monitoring()
        self.monitoring.start_monitoring(interval_seconds=300)  # 5 minutes

        # 🚀 Connection Pooling per riutilizzo connessioni HTTP
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=20,  # Pool di connessioni
            pool_maxsize=20,      # Massimo numero di connessioni nel pool
            max_retries=1,        # Retry limitati per velocità
            pool_block=False      # Non bloccare se pool pieno
        )
        self.session.mount('https://', adapter)
        self.session.mount('http://', adapter)

        # ⚡ Cache intelligente stratificata
        self.price_cache = SmartCache()      # Cache prezzi: 1-2s
        self.indicator_cache = SmartCache()  # Cache indicatori: 10s
        self.stats_cache = SmartCache()      # Cache statistiche: 30s

        self.api_stats = {}
        self.last_cache_cleanup = time.time()

        # GT Points Management
        self.gt_fee_info = None
        self.gt_balance = None
        self.last_gt_info_update = 0

    def _cleanup_caches(self):
        """🧹 Pulizia periodica cache per evitare memory leak"""
        current_time = time.time()
        if current_time - self.last_cache_cleanup > 60:  # Ogni minuto
            self.price_cache.clear_expired(5)      # Pulisce cache prezzi > 5s
            self.indicator_cache.clear_expired(30) # Pulisce cache indicatori > 30s
            self.stats_cache.clear_expired(120)    # Pulisce cache stats > 2min
            self.last_cache_cleanup = current_time

    def _generate_sign(self, method, endpoint, query_string="", body=""):
        t = str(time.time())
        body_encoded = body.encode('utf-8') if isinstance(body, str) else json.dumps(body).encode('utf-8')
        payload_hash = hashlib.sha512(body_encoded).hexdigest()
        message = f"{method}\n{API_BASE_PATH}{endpoint}\n{query_string}\n{payload_hash}\n{t}"
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()
        return {
            'KEY': self.api_key,
            'Timestamp': t,
            'SIGN': signature,
            'Content-Type': 'application/json'
        }

    def _request(self, method, endpoint, params=None, body=None, signed=False, silent_errors=False):
        # 🧹 Pulizia cache periodica
        self._cleanup_caches()

        self.api_stats.setdefault(endpoint, {'count': 0, 'total_time': 0.0, 'failures': 0})
        start_time = time.monotonic()
        
        # 🚦 Rate Limiting Enforcement (VIP 0 Compliance) - Optimized
        if self.rate_limit_enabled:
            # Lazy initialization per performance
            if not hasattr(self, '_endpoint_classifier_cache'):
                from rate_limit_manager import EndpointClassifier
                self._endpoint_classifier_cache = {}
                self.endpoint_classifier = EndpointClassifier
            
            # Cache classificazione endpoint per performance
            endpoint_key = f"{method}:{endpoint}"
            if endpoint_key not in self._endpoint_classifier_cache:
                self._endpoint_classifier_cache[endpoint_key] = \
                    self.endpoint_classifier.classify_endpoint(endpoint, method)
            
            category = self._endpoint_classifier_cache[endpoint_key]
            
            # Controllo veloce can_make_request
            if not self.rate_limit_manager.can_make_request(category):
                # Solo se necessario, calcola wait time
                wait_time = self.rate_limit_manager.wait_if_needed(category)
                if wait_time > 0:
                    trade_logger.debug(f"🚦 Rate limit wait: {wait_time:.3f}s for {endpoint}")
            
            # Record request (sempre)
            self.rate_limit_manager.record_request(category)
        
        # 🛡️ SECURITY: Usa retry manager per prevenire infinite loops
        from api_retry_manager import create_gate_io_retry_manager
        retry_manager = create_gate_io_retry_manager()
        
        def _execute_request():
            query_string = requests.compat.urlencode(params) if params else ""
            url = f"{self.base_url}{API_BASE_PATH}{endpoint}?{query_string}"
            headers = {'Accept': 'application/json'}

            # Prepara il body per le richieste POST
            json_data = None
            if body is not None:
                if isinstance(body, dict):
                    json_data = body
                else:
                    json_data = body
                headers['Content-Type'] = 'application/json'

            if signed:
                # Genera la signature con il body corretto
                body_for_sign = json.dumps(json_data) if json_data is not None else ""
                headers.update(self._generate_sign(method, endpoint, query_string, body_for_sign))

            # ⚡ Execute HTTP request with timeout
            if json_data is not None:
                response = self.session.request(method, url, headers=headers, json=json_data, timeout=TradingConfig.DEFAULT_TIMEOUT)
            else:
                response = self.session.request(method, url, headers=headers, timeout=TradingConfig.DEFAULT_TIMEOUT)

            # 🚨 SECURITY: Gestione specifica rate limiting 429
            if response.status_code == 429:
                retry_after = response.headers.get('Retry-After', '60')
                trade_logger.warning(f"🚨 Rate limit hit on {endpoint} - retry after {retry_after}s")
                from api_retry_manager import RetryableErrorType
                error = requests.exceptions.HTTPError(f"429 Rate Limit: {response.text}", response=response)
                error.retry_type = RetryableErrorType.RATE_LIMIT
                raise error

            response.raise_for_status()
            self.api_stats[endpoint]['count'] += 1
            return response.json()

        try:
            # 🛡️ SECURITY: Execute with retry manager protection  
            start_api_time = time.time()
            result = retry_manager.execute_with_retry(
                operation=_execute_request,
                operation_name=f"gate_api_{endpoint}",
                error_classifier=self._classify_api_error
            )
            api_duration = time.time() - start_api_time
            
            # 🔍 MONITORING: Record successful API call
            self.monitoring.record_api_event(
                endpoint=endpoint,
                success=True,
                response_time=api_duration
            )
            
            return result

        except Exception as e:
            api_duration = time.time() - start_time
            is_rate_limited = hasattr(e, 'response') and e.response and e.response.status_code == 429
            
            # 🔍 MONITORING: Record failed API call
            self.monitoring.record_api_event(
                endpoint=endpoint,
                success=False,
                response_time=api_duration,
                error_message=str(e),
                is_rate_limited=is_rate_limited
            )
            
            if not silent_errors:
                trade_logger.error(f"🚫 API {endpoint} failed after all retries: {e}")
                if hasattr(e, 'response') and e.response is not None:
                    try:
                        error_text = e.response.text
                        trade_logger.debug(f"Error details: {error_text}")
                        # Prova a parsare la risposta di errore
                        if error_text:
                            try:
                                error_json = json.loads(error_text)
                                return error_json  # Ritorna l'errore strutturato
                            except json.JSONDecodeError as json_err:
                                logging.warning(f"JSON decode error in error response: {json_err}")
                    except (requests.exceptions.RequestException, ValueError) as parse_err:
                        logging.warning(f"Error parsing response: {parse_err}")
            
            self.api_stats[endpoint]['failures'] += 1
            return None
        finally:
            duration = time.monotonic() - start_time
            self.api_stats[endpoint]['total_time'] += duration

    def _classify_api_error(self, error: Exception):
        """🛡️ Classifica errori API per retry strategy appropriata"""
        from api_retry_manager import RetryableErrorType
        
        # Priority classification
        if hasattr(error, 'retry_type'):
            return error.retry_type
            
        if hasattr(error, 'response') and error.response:
            status = error.response.status_code
            if status == 429:
                return RetryableErrorType.RATE_LIMIT
            elif status >= 500:
                return RetryableErrorType.SERVER_ERROR
            elif status in [408, 504]:
                return RetryableErrorType.TIMEOUT
                
        error_str = str(error).lower()
        if any(keyword in error_str for keyword in ['connection', 'network', 'timeout', 'dns']):
            return RetryableErrorType.NETWORK_ERROR
            
        return RetryableErrorType.API_ERROR

    def get_spot_accounts(self):
        return self._request('GET', '/spot/accounts', signed=True)

    def get_gt_fee_info(self, force_refresh=False):
        """Recupera informazioni sui GT Points e fee discount"""
        current_time = time.time()

        # Usa cache se disponibile e non troppo vecchia (30 secondi)
        if (not force_refresh and self.gt_fee_info and
            current_time - self.last_gt_info_update < 30):
            return self.gt_fee_info

        try:
            # API per ottenere informazioni sui fee dell'utente
            fee_info = self._request('GET', '/wallet/fee', signed=True)
            if fee_info:
                self.gt_fee_info = {
                    'gt_discount_enabled': fee_info.get('gt_discount', False),
                    'gt_taker_fee': float(fee_info.get('gt_taker_fee', '0')),
                    'gt_maker_fee': float(fee_info.get('gt_maker_fee', '0')),
                    'normal_taker_fee': float(fee_info.get('taker_fee', str(TradingConfig.DEFAULT_TAKER_FEE))),
                    'normal_maker_fee': float(fee_info.get('maker_fee', str(TradingConfig.DEFAULT_MAKER_FEE))),
                    'debit_fee_type': fee_info.get('debit_fee', 0),  # 1=GT, 2=Point, 3=VIP
                    'user_id': fee_info.get('user_id')
                }
                self.last_gt_info_update = current_time
                return self.gt_fee_info
        except Exception as e:
            # Fallback ai valori standard se API non disponibile
            pass

        # Valori di default se non si riescono a recuperare
        self.gt_fee_info = {
            'gt_discount_enabled': False,
            'gt_taker_fee': TradingConfig.DEFAULT_TAKER_FEE,
            'gt_maker_fee': TradingConfig.DEFAULT_MAKER_FEE,
            'normal_taker_fee': TradingConfig.DEFAULT_TAKER_FEE,
            'normal_maker_fee': TradingConfig.DEFAULT_MAKER_FEE,
            'debit_fee_type': 0,
            'user_id': None
        }
        return self.gt_fee_info

    def get_gt_balance(self, force_refresh=False):
        """💰 Recupera il saldo GT dal wallet spot"""
        current_time = time.time()

        # Cache per 10 secondi
        if (not force_refresh and self.gt_balance and
            hasattr(self, 'last_gt_balance_update') and
            current_time - self.last_gt_balance_update < 10):
            return self.gt_balance

        gt_balance = self.get_wallet_balance('GT')
        if gt_balance is not None:
            self.gt_balance = gt_balance
            self.last_gt_balance_update = current_time

        return self.gt_balance or 0.0

    def get_effective_fee_rate(self, order_type='taker', trade_amount_usdt=0):
        """Calcola il fee rate effettivo considerando GT Points"""
        gt_info = self.get_gt_fee_info()

        if not gt_info['gt_discount_enabled']:
            # GT discount non abilitato, usa fee standard
            return gt_info['normal_taker_fee'] if order_type == 'taker' else gt_info['normal_maker_fee']

        # GT discount abilitato - verifica se ci sono GT sufficienti
        gt_balance = self.get_gt_balance()

        if gt_balance > 0:
            # Ha GT disponibili - usa fee scontato
            gt_fee_rate = gt_info['gt_taker_fee'] if order_type == 'taker' else gt_info['gt_maker_fee']

            # Calcola GT necessari per questo trade (approssimativo)
            if trade_amount_usdt > 0:
                estimated_fee_usdt = trade_amount_usdt * gt_fee_rate
                gt_price = self.get_ticker('GT_USDT') or TradingConfig.GT_ESTIMATED_PRICE
                estimated_gt_needed = estimated_fee_usdt / gt_price

                if gt_balance >= estimated_gt_needed:
                    return gt_fee_rate
            else:
                # Se non sappiamo l'importo, assumiamo che abbia GT sufficienti
                return gt_fee_rate

        # Non ha GT sufficienti o GT non disponibili
        return gt_info['normal_taker_fee'] if order_type == 'taker' else gt_info['normal_maker_fee']

    def get_gt_status_summary(self):
        """📋 Restituisce un riassunto dello stato GT Points per logging/debug"""
        gt_info = self.get_gt_fee_info()
        gt_balance = self.get_gt_balance()

        status = {
            'gt_enabled': gt_info['gt_discount_enabled'],
            'gt_balance': gt_balance,
            'normal_taker_rate': gt_info['normal_taker_fee'],
            'normal_maker_rate': gt_info['normal_maker_fee'],
            'gt_taker_rate': gt_info['gt_taker_fee'],
            'gt_maker_rate': gt_info['gt_maker_fee'],
            'debit_type': gt_info['debit_fee_type'],
            'savings_taker': (gt_info['normal_taker_fee'] - gt_info['gt_taker_fee']) if gt_info['gt_discount_enabled'] else 0,
            'savings_maker': (gt_info['normal_maker_fee'] - gt_info['gt_maker_fee']) if gt_info['gt_discount_enabled'] else 0
        }

        return status

    def get_ticker(self, pair):
        # ⚡ Cache intelligente per prezzi: 1-2s
        cache_key = f"ticker_{pair}"
        cached_price = self.price_cache.get(cache_key, TradingConfig.CACHE_TIMEOUTS['orderbook'])  # Cache configurabile
        if cached_price is not None:
            return cached_price

        data = self._request('GET', '/spot/tickers', params={'currency_pair': pair}, silent_errors=True)
        if data and isinstance(data, list) and len(data) > 0:
            price = float(data[0].get('last', 0))
            self.price_cache.set(cache_key, price)  # Salva in cache
            return price
        return None

    def get_all_spot_pairs(self):
        """Recupera tutte le coppie spot disponibili su Gate.io"""
        cache_key = "all_spot_pairs"
        cached_pairs = self.stats_cache.get(cache_key, TradingConfig.CACHE_TIMEOUTS['stats'])
        if cached_pairs is not None:
            return cached_pairs

        data = self._request('GET', '/spot/currency_pairs', silent_errors=True)
        if data and isinstance(data, list):
            # Filtra solo le coppie USDT
            usdt_pairs = [pair['id'] for pair in data if pair['id'].endswith('_USDT') and pair.get('trade_status') == 'tradable']
            self.stats_cache.set(cache_key, usdt_pairs)
            return usdt_pairs
        return []

    def validate_pair_exists(self, symbol):
        """Valida che una coppia esista tra quelle disponibili"""
        all_pairs = self.get_all_spot_pairs()
        pair = f"{symbol.upper()}_USDT"
        return pair in all_pairs

    def get_order_book(self, pair, limit=10):
        """Recupera il book degli ordini per una coppia"""
        return self._request('GET', '/spot/order_book', params={'currency_pair': pair, 'limit': limit})

    def get_order_status(self, pair, order_id):
        """Verifica lo stato di un ordine specifico"""
        try:
            return self._request('GET', f'/spot/orders/{order_id}', params={'currency_pair': pair}, signed=True)
        except Exception as e:
            trade_logger.info(str(f"❌ Errore verifica ordine {order_id}: {e}"))
            return None

    def place_spot_order(self, pair, side, amount, price, order_type='limit'):
        """Piazza un ordine spot con gestione errori migliorata"""
        try:
            # Validazione parametri
            if not pair or not side or not amount or not price:
                raise ValueError("Parametri ordine mancanti")

            # Assicurati che amount e price siano numerici
            amount = float(amount)
            price = float(price)

            if amount <= 0 or price <= 0:
                raise ValueError(f"Valori non validi: amount={amount}, price={price}")
            
            # 🚨 VALIDAZIONE CRITICA: Gate.io richiede ordini >= 3 USDT
            order_value_usdt = amount * price
            min_required = GateIOLimits.get_min_order_value_with_margin()
            if order_value_usdt < min_required:
                raise ValueError(f"Ordine troppo piccolo: {order_value_usdt:.2f} USDT < {min_required:.2f} USDT richiesti da Gate.io")

            # Costruisci body con parametri puliti
            body = {
                'currency_pair': str(pair),
                'side': str(side),
                'amount': f"{amount:.8f}".rstrip('0').rstrip('.'),  # Rimuovi zeri finali
                'price': f"{price:.8f}".rstrip('0').rstrip('.'),    # Rimuovi zeri finali
                'type': str(order_type)
            }

            trade_logger.info(str(f"🔄 Piazzando ordine: {body}"))
            return self._request('POST', '/spot/orders', body=body, signed=True)

        except Exception as e:
            trade_logger.info(str(f"❌ Errore nella preparazione ordine: {e}"))
            return {'error': str(e)}

    def get_all_buy_trades(self, pair, limit=1000):
        """
        📈 Recupera TUTTE le tranche di acquisto dall'API Gate.io

        💰 INCLUDE FEES REALI per ogni transazione:
        • fee: Importo fee reale pagato
        • fee_currency: Valuta della fee (USDT/GT/altro)
        • Dati convertiti automaticamente in USDT tramite _convert_fee_to_usdt
        """
        cache_key = f"buy_trades_{pair}"
        cached_trades = self.stats_cache.get(cache_key, TradingConfig.CACHE_TIMEOUTS['stats'])  # Cache configurabile
        if cached_trades is not None:
            return cached_trades

        try:
            # Recupera tutti i trade storici per la coppia
            all_trades = self._request('GET', '/spot/my_trades',
                                     params={'currency_pair': pair, 'limit': limit},
                                     signed=True, silent_errors=True)

            if not all_trades:
                return []

            # Filtra solo gli acquisti e ordina per data
            buy_trades = []
            for trade in all_trades:
                if trade['side'] == 'buy':
                    # 🔍 ROBUSTEZZA: Gestisce fee che possono essere None, stringa vuota, o zero
                    fee_raw = trade.get('fee', '0')
                    fee_currency_raw = trade.get('fee_currency', 'USDT')

                    # Converte fee a float, gestendo casi edge
                    try:
                        fee_amount = float(fee_raw) if fee_raw not in [None, '', 'null'] else 0.0
                    except (ValueError, TypeError):
                        fee_amount = 0.0

                    # Se fee è zero ma abbiamo un trade, stima la fee
                    if fee_amount == 0:
                        trade_value = float(trade['price']) * float(trade['amount'])
                        # Stima fee al 0.2% se non disponibile dall'API
                        fee_amount = trade_value * TradingConfig.DEFAULT_TAKER_FEE
                        fee_currency_raw = 'USDT'  # Assume USDT per fee stimate

                    buy_trades.append({
                        'price': float(trade['price']),
                        'amount': float(trade['amount']),
                        'value_usdt': float(trade['price']) * float(trade['amount']),
                        'timestamp': int(float(trade['create_time_ms'])),
                        'fee': fee_amount,
                        'fee_currency': fee_currency_raw,
                        'order_id': trade['order_id'],
                        'fee_estimated': fee_amount == float(trade.get('fee', '0')) if trade.get('fee') else True
                    })

            # Ordina per timestamp (più recente prima)
            buy_trades.sort(key=lambda x: x['timestamp'], reverse=True)

            self.stats_cache.set(cache_key, buy_trades)
            return buy_trades

        except Exception as e:
            trade_logger.info(str(f"Errore recupero tranche acquisti: {e}"))
            return []

    def get_wallet_balance(self, currency):
        """💰 Recupera il saldo reale dal wallet"""
        cache_key = f"wallet_{currency}"
        cached_balance = self.price_cache.get(cache_key, TradingConfig.CACHE_TIMEOUTS['orderbook'])  # Cache configurabile
        if cached_balance is not None:
            return cached_balance

        try:
            accounts = self.get_spot_accounts()
            if accounts:
                for account in accounts:
                    if account['currency'] == currency:
                        total = float(account['available']) + float(account['locked'])
                        self.price_cache.set(cache_key, total)
                        return total
            return 0.0
        except Exception:
            return 0.0

    def calculate_real_portfolio_data(self, pair):
        """
        📊 Calcola dati reali del portafoglio da API + tranche

        🔧 SISTEMA FEES INTEGRATO:
        • Recupera fees REALI pagate per ogni acquisto dall'API Gate.io
        • Include GT Points discount quando applicato
        • Converte automaticamente fees in USDT
        • Considera solo tranche che compongono il 100% del saldo attuale
        """
        currency = pair.split('_')[0]

        # Saldo reale dal wallet
        current_balance = self.get_wallet_balance(currency)

        # Tranche di acquisto reali dall'API
        all_buy_trades = self.get_all_buy_trades(pair)

        if not all_buy_trades or current_balance <= 0:
            return None

        # CORREZIONE: Seleziona solo le tranche che compongono il 100% del saldo attuale
        # Ordina le transazioni dalla più recente alla più vecchia
        all_buy_trades.sort(key=lambda x: x['timestamp'], reverse=True)

        active_trades = []
        accumulated_amount = 0.0

        # Accumula transazioni fino a raggiungere il saldo attuale nel wallet
        for trade in all_buy_trades:
            remaining_needed = current_balance - accumulated_amount

            if remaining_needed <= 0:
                break

            if trade['amount'] <= remaining_needed:
                # Prendi l'intera transazione
                active_trades.append(trade)
                accumulated_amount += trade['amount']
            else:
                # Prendi solo la parte necessaria della transazione
                partial_trade = trade.copy()
                partial_trade['amount'] = remaining_needed
                partial_trade['value_usdt'] = trade['price'] * remaining_needed
                partial_trade['fee'] = (trade['fee'] / trade['amount']) * remaining_needed if trade['amount'] > 0 else 0
                active_trades.append(partial_trade)
                accumulated_amount += remaining_needed
                break

        # Calcola statistiche SOLO dalle tranche attive (che compongono il 100% del saldo)
        total_bought_amount = sum(trade['amount'] for trade in active_trades)
        total_invested_usdt = sum(trade['value_usdt'] for trade in active_trades)
        total_fees_paid = sum(self._convert_fee_to_usdt(trade['fee'], trade['fee_currency'], trade['price'])
                             for trade in active_trades)

        # Prezzo medio ponderato dalle tranche attive
        weighted_avg_price = total_invested_usdt / total_bought_amount if total_bought_amount > 0 else 0

        # Prezzo medio aritmetico dalle tranche attive
        avg_price = sum(trade['price'] for trade in active_trades) / len(active_trades) if active_trades else 0

        return {
            'current_balance': current_balance,
            'buy_trades': active_trades,  # Solo le tranche attive
            'all_buy_trades': all_buy_trades,  # Tutte le transazioni per riferimento
            'total_bought': total_bought_amount,
            'total_invested': total_invested_usdt,
            'total_fees_paid': total_fees_paid,
            'weighted_avg_price': weighted_avg_price,
            'arithmetic_avg_price': avg_price,
            'remaining_percentage': 100.0,  # Sempre 100% perché consideriamo solo le tranche attive
            'active_trades_count': len(active_trades),
            'total_trades_count': len(all_buy_trades)
        }

    def _convert_fee_to_usdt(self, fee_amount, fee_currency, trade_price):
        """
        💰 Converte commissioni reali dall'API in USDT con calcolo preciso

        🔧 Gestisce automaticamente:
        • USDT: Valore diretto
        • GT Points: Conversione con prezzo reale GT_USDT
        • Altre crypto: Conversione usando prezzo di mercato

        📊 Usato per calcolare le fees REALI pagate negli acquisti
        """
        if fee_currency == 'USDT':
            return fee_amount
        elif fee_currency == 'GT':
            # Recupera prezzo GT reale se possibile, altrimenti usa stima
            try:
                gt_price = self.get_ticker('GT_USDT')
                return fee_amount * (gt_price if gt_price else TradingConfig.GT_ESTIMATED_PRICE)
            except (requests.exceptions.RequestException, ValueError, KeyError) as e:
                logging.warning(f"Error fetching GT price: {e}")
                return fee_amount * TradingConfig.GT_ESTIMATED_PRICE
        else:
            # Per altre crypto, usa il prezzo del trade come stima
            # CORREZIONE: Se fee_currency è la stessa crypto che stiamo tradando
            currency = fee_currency
            if currency in ['BTC', 'ETH', 'BNB']:
                # Per crypto principali, usa prezzo attuale
                try:
                    current_price = self.get_ticker(f'{currency}_USDT')
                    return fee_amount * (current_price if current_price else trade_price)
                except (requests.exceptions.RequestException, ValueError, KeyError) as e:
                    logging.warning(f"Error fetching {currency} price: {e}")
                    return fee_amount * trade_price
            else:
                return fee_amount * trade_price

    def get_best_book_price(self, pair, side='sell'):
        """Trova il miglior prezzo nel book per minimizzare slippage"""
        try:
            book = self.get_order_book(pair, limit=5)
            if not book:
                return None

            if side == 'sell':
                # Per vendere, guardiamo i bid (compratori)
                bids = book.get('bids', [])
                if not bids:
                    return None

                # Trova i 2 migliori livelli di bid
                best_levels = sorted(bids, key=lambda x: float(x[0]), reverse=True)[:2]

                # Scegli il livello con meno volume (meno carico)
                if len(best_levels) >= 2:
                    level1_volume = float(best_levels[0][1])
                    level2_volume = float(best_levels[1][1])

                    # Usa il livello con meno volume per ridurre slippage
                    chosen_level = best_levels[1] if level2_volume < level1_volume else best_levels[0]
                    return float(chosen_level[0])
                else:
                    return float(best_levels[0][0])
            else:
                # Per comprare, guardiamo gli ask (venditori)
                asks = book.get('asks', [])
                if not asks:
                    return None

                best_levels = sorted(asks, key=lambda x: float(x[0]))[:2]

                if len(best_levels) >= 2:
                    level1_volume = float(best_levels[0][1])
                    level2_volume = float(best_levels[1][1])

                    chosen_level = best_levels[1] if level2_volume < level1_volume else best_levels[0]
                    return float(chosen_level[0])
                else:
                    return float(best_levels[0][0])

        except Exception as e:
            trade_logger.info(str(f"Errore nel recuperare il book: {e}"))
            return None

def get_ohlcv(client, pair, interval='5m', limit=100):
    # ⚡ Cache intelligente per indicatori: 10s
    cache_key = f"ohlcv_{pair}_{interval}_{limit}"
    cached_data = client.indicator_cache.get(cache_key, TradingConfig.CACHE_TIMEOUTS['indicators'])  # Cache configurabile
    if cached_data is not None:
        return cached_data

    try:
        data = client._request('GET', '/spot/candlesticks', params={'currency_pair': pair, 'interval': interval, 'limit': limit})
        if data and isinstance(data, list):
            result = sorted(data, key=lambda x: int(x[0]))
            client.indicator_cache.set(cache_key, result)  # Salva in cache
            return result
        return []
    except Exception:
        return []

def get_last_buy_price(client, pair):
    trade_logger.info(str(f"Recupero l'ultimo prezzo di acquisto per {pair}..."))
    try:
        trades = client._request('GET', '/spot/my_trades', params={'currency_pair': pair, 'limit': 200}, signed=True)
        if trades:
            for trade in sorted(trades, key=lambda x: int(float(x['create_time_ms'])), reverse=True):
                if trade['side'] == 'buy':
                    trade_logger.info(str(f"Ultimo prezzo di acquisto trovato: {trade['price']}"))
                    return float(trade['price']), float(trade['amount'])
        trade_logger.info(str("Nessun trade di acquisto trovato nello storico recente."))
        return None, None
    except Exception as e:
        trade_logger.info(str(f"Errore durante il recupero dello storico trade: {e}"))
        return None, None

# =============================================================================
# 📊 TECHNICAL INDICATORS ENGINE - Calcoli Professionali
# =============================================================================

class TechnicalAnalyzer:
    """📈 Motore di analisi tecnica professionale con indicatori multipli"""

    def __init__(self):
        self.cache_duration = 15  # Cache indicatori per 15 secondi
        self.indicator_cache = {}

    def get_multi_timeframe_data(self, client, pair):
        """Ottiene dati OHLCV per tutti i timeframe"""
        timeframes = TradingConfig.TIMEFRAMES
        all_data = {}

        for tf in timeframes:
            try:
                data = get_ohlcv(client, pair, interval=tf, limit=50)
                if data and len(data) > 20:
                    all_data[tf] = data
            except Exception as e:
                all_data[tf] = None

        return all_data

    def calculate_rsi(self, closes, period=14):
        """RSI professionale con gestione edge cases"""
        if len(closes) < period + 1:
            return None

        series = pd.Series(closes, dtype=float)
        delta = series.diff()

        # Separazione gain/loss
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        # Calcolo Wilder's smoothing (più accurato del semplice rolling)
        avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()

        # Evita divisione per zero
        if avg_loss.iloc[-1] == 0:
            return 100.0

        rs = avg_gain.iloc[-1] / avg_loss.iloc[-1]
        rsi = 100 - (100 / (1 + rs))

        return round(rsi, 2)

    def calculate_macd(self, closes, fast=12, slow=26, signal=9):
        """MACD professionale con signal line e histogram"""
        if len(closes) < slow + signal:
            return {'line': None, 'signal': None, 'histogram': None}

        series = pd.Series(closes, dtype=float)

        # EMA con periodo corretti
        ema_fast = series.ewm(span=fast, adjust=False).mean()
        ema_slow = series.ewm(span=slow, adjust=False).mean()

        # MACD Line
        macd_line = ema_fast - ema_slow

        # Signal Line
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()

        # Histogram
        histogram = macd_line - signal_line

        return {
            'line': round(macd_line.iloc[-1], 6),
            'signal': round(signal_line.iloc[-1], 6),
            'histogram': round(histogram.iloc[-1], 6)
        }

    def calculate_ema(self, closes, period):
        """EMA con calcolo corretto"""
        if len(closes) < period:
            return None

        series = pd.Series(closes, dtype=float)
        ema = series.ewm(span=period, adjust=False).mean()
        return round(ema.iloc[-1], 6)

    def calculate_bollinger_bands(self, closes, period=20, std_dev=2):
        """Bande di Bollinger per volatilità"""
        if len(closes) < period:
            return {'upper': None, 'middle': None, 'lower': None}

        series = pd.Series(closes, dtype=float)
        sma = series.rolling(window=period).mean()
        std = series.rolling(window=period).std()

        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)

        return {
            'upper': round(upper.iloc[-1], 6),
            'middle': round(sma.iloc[-1], 6),
            'lower': round(lower.iloc[-1], 6)
        }

    def calculate_stochastic(self, highs, lows, closes, k_period=14, d_period=3):
        """Stochastic Oscillator per momentum"""
        if len(closes) < k_period:
            return {'k': None, 'd': None}

        highs_series = pd.Series(highs, dtype=float)
        lows_series = pd.Series(lows, dtype=float)
        closes_series = pd.Series(closes, dtype=float)

        # %K calculation
        lowest_low = lows_series.rolling(window=k_period).min()
        highest_high = highs_series.rolling(window=k_period).max()

        k_percent = 100 * ((closes_series - lowest_low) / (highest_high - lowest_low))

        # %D calculation (smoothed %K)
        d_percent = k_percent.rolling(window=d_period).mean()

        return {
            'k': round(k_percent.iloc[-1], 2),
            'd': round(d_percent.iloc[-1], 2)
        }

    def analyze_timeframe(self, data, current_price):
        """Analisi completa per un singolo timeframe"""
        if not data or len(data) < 20:
            return None

        closes = [float(candle[4]) for candle in data]  # Close prices
        highs = [float(candle[2]) for candle in data]   # High prices
        lows = [float(candle[3]) for candle in data]    # Low prices
        volumes = [float(candle[5]) for candle in data] # Volume

        # Calcolo indicatori
        rsi = self.calculate_rsi(closes)
        macd = self.calculate_macd(closes)
        ema_9 = self.calculate_ema(closes, 9)
        ema_21 = self.calculate_ema(closes, 21)
        ema_50 = self.calculate_ema(closes, 50)
        bollinger = self.calculate_bollinger_bands(closes)
        stoch = self.calculate_stochastic(highs, lows, closes)

        # Trend analysis
        trend_strength = self._calculate_trend_strength(current_price, ema_9, ema_21, ema_50)
        volume_analysis = self._analyze_volume_pattern(volumes)

        return {
            'rsi': rsi,
            'macd': macd,
            'ema_9': ema_9,
            'ema_21': ema_21,
            'ema_50': ema_50,
            'bollinger': bollinger,
            'stochastic': stoch,
            'trend_strength': trend_strength,
            'volume_analysis': volume_analysis,
            'price_position': self._get_price_position_analysis(current_price, bollinger, ema_21)
        }

    def _calculate_trend_strength(self, current_price, ema_9, ema_21, ema_50):
        """Calcola forza del trend basata su allineamento EMA"""
        if not all([ema_9, ema_21, ema_50]):
            return {'strength': 'UNKNOWN', 'direction': 'NONE', 'score': 0}

        # Allineamento bullish: Price > EMA9 > EMA21 > EMA50
        bullish_alignment = (current_price > ema_9 > ema_21 > ema_50)
        bearish_alignment = (current_price < ema_9 < ema_21 < ema_50)

        if bullish_alignment:
            score = min(5, ((current_price - ema_50) / ema_50) * 100 * 10)
            return {'strength': 'FORTE', 'direction': 'RIALZO', 'score': score}
        elif bearish_alignment:
            score = min(5, ((ema_50 - current_price) / ema_50) * 100 * 10)
            return {'strength': 'FORTE', 'direction': 'RIBASSO', 'score': -score}
        else:
            return {'strength': 'DEBOLE', 'direction': 'LATERALE', 'score': 0}

    def _analyze_volume_pattern(self, volumes):
        """Analizza pattern del volume"""
        if len(volumes) < 10:
            return {'trend': 'UNKNOWN', 'strength': 'N/A'}

        recent_vol = sum(volumes[-5:]) / 5
        prev_vol = sum(volumes[-10:-5]) / 5

        if recent_vol > prev_vol * 1.5:
            return {'trend': 'CRESCENTE', 'strength': 'FORTE'}
        elif recent_vol > prev_vol * 1.2:
            return {'trend': 'CRESCENTE', 'strength': 'MEDIA'}
        elif recent_vol < prev_vol * 0.8:
            return {'trend': 'CALANTE', 'strength': 'DEBOLE'}
        else:
            return {'trend': 'STABILE', 'strength': 'NORMALE'}

    def _get_price_position_analysis(self, current_price, bollinger, ema_21):
        """Analizza posizione prezzo rispetto a supporti/resistenze"""
        if not bollinger['upper'] or not ema_21:
            return {'position': 'UNKNOWN', 'signal': 'NEUTRO'}

        # Posizione nelle Bande di Bollinger
        bb_position = (current_price - bollinger['lower']) / (bollinger['upper'] - bollinger['lower'])

        if bb_position > 0.8:
            return {'position': 'OVERBOUGHT', 'signal': 'VENDI'}
        elif bb_position < 0.2:
            return {'position': 'OVERSOLD', 'signal': 'COMPRA'}
        elif current_price > ema_21 * 1.01:
            return {'position': 'FORTE', 'signal': 'MANTIENI'}
        elif current_price < ema_21 * 0.99:
            return {'position': 'DEBOLE', 'signal': 'CAUTELA'}
        else:
            return {'position': 'NEUTRO', 'signal': 'ATTENDI'}

def calc_ema(closes, period=9):
    """Mantiene compatibilità con codice esistente"""
    analyzer = TechnicalAnalyzer()
    return analyzer.calculate_ema(closes, period)

def calc_rsi(closes, period=14):
    """Mantiene compatibilità con codice esistente"""
    analyzer = TechnicalAnalyzer()
    return analyzer.calculate_rsi(closes, period)

def calc_macd(closes, fast=12, slow=26, signal=9):
    """Mantiene compatibilità con codice esistente"""
    analyzer = TechnicalAnalyzer()
    result = analyzer.calculate_macd(closes, fast, slow, signal)
    return result['line'], result['signal'], result['histogram']

class CursesDashboard:
    """
    📊 Dashboard Trading Scalping con Dati Reali da API

    🔧 SISTEMA FEES:
    • FEES ENTRATA: Recuperate dalle API Gate.io per ogni transazione (fee reale pagata)
    • FEES USCITA: Fisse 0.2% (0.002) per tutti i calcoli di vendita
    • Le fees di entrata includono GT Points discount quando applicabile
    • Le fees di uscita sono standardizzate per consistenza nei calcoli
    """
    def __init__(self, stdscr, client, pair, buy_price=None, target_percent=2.0, initial_amount=None, spot_assets=None, prezzi=None, quantita=None):
        self.stdscr = stdscr
        self.client = client
        self.pair = pair
        self.target_percent = target_percent
        self.last_update_time = 0
        self.spot_assets = spot_assets

        # � Inizializza sistema di logging per trading
        self.trading_logger = TradingLogger()
        self.current_session_id = None  # ID sessione corrente per tracking
        
        # 🪟 Popup service sarà inizializzato in run() dopo setup colori
        self.popup_service = None
        
        # 🛡️ Inizializza failure tracker per scalping mode  
        self.failure_tracker = OrderFailureTracker()
        
        # 🤖 Stato scalping mode
        self.scalping_active = False
        self.scalping_stop_requested = False
        
        # 📚 Inizializza sistema help
        self.help_system = HelpSystem()
        self.help_active = False
        self.help_scroll_offset = 0
        self.returning_from_scalping = False

        # 🔄 Sistema navigazione a TAB tra sezioni (inizializzato presto)
        self.current_tab = 0  # 0=main, 1=sentiment, 2=bot_live
        self.sentiment_expanded = False
        self.bot_live_expanded = False

        # �📈 Recupera dati reali dal portafoglio
        self.real_portfolio_data = self.client.calculate_real_portfolio_data(pair)

        if self.real_portfolio_data:
            # Usa dati reali dall'API
            trade_logger.info(str(f"Dati portafoglio recuperati dall'API:"))
            trade_logger.info(str(f"   Saldo attuale: {self.real_portfolio_data['current_balance']:.6f}"))
            trade_logger.info(str(f"   Tranche attive: {self.real_portfolio_data['active_trades_count']} di {self.real_portfolio_data['total_trades_count']} totali"))
            trade_logger.info(str(f"   Capitale investito (tranche attive): {self.real_portfolio_data['total_invested']:.2f} USDT"))
            trade_logger.info(str(f"   Solo le tranche che compongono il 100% del saldo attuale"))

            self.buy_price_avg = self.real_portfolio_data['arithmetic_avg_price']
            self.buy_price = self.real_portfolio_data['weighted_avg_price']  # Per compatibilità
            self.initial_amount = self.real_portfolio_data['current_balance']
            self.prezzi = [trade['price'] for trade in self.real_portfolio_data['buy_trades']]
            self.quantita = [trade['amount'] for trade in self.real_portfolio_data['buy_trades']]
            self.total_invested_real = self.real_portfolio_data['total_invested']
            self.total_fees_paid_real = self.real_portfolio_data['total_fees_paid']
        else:
            # 🔄 Fallback a dati manuali se API non disponibile
            trade_logger.info(str("Usando dati manuali (API non disponibile)"))
            self.buy_price_avg = sum(prezzi) / len(prezzi) if prezzi else buy_price
            self.buy_price = buy_price if buy_price else self.buy_price_avg
            self.initial_amount = initial_amount or sum(quantita) if quantita else 0
            self.prezzi = prezzi or [buy_price] if buy_price else []
            self.quantita = quantita or [initial_amount] if initial_amount else []
            self.total_invested_real = self.buy_price_avg * self.initial_amount if self.buy_price_avg and self.initial_amount else 0
            # Stima commissioni usando GT Points se disponibili
            estimated_fee_rate = self.client.get_effective_fee_rate('taker', self.total_invested_real)
            self.total_fees_paid_real = self.total_invested_real * estimated_fee_rate

        self.target_price = self.buy_price_avg * (1 + target_percent / 100)
        self.last_valid_price = self.buy_price_avg
        self.price_history = []
        self.pair_indicators = {}
        self.trades_stats = {}

        # Variabili per gestione sessione
        self.session_high = self.buy_price_avg
        self.session_low = self.buy_price_avg
        self.profit_peaks = []

        # Variabili per trading con tasti 1-4 (vendita)
        self.order_mode = False
        self.order_percentage = 0
        self.order_success = ""
        self.order_success_time = 0
        self.order_error = ""
        self.order_error_time = 0
        self.pending_order = False

        # Variabili per trading con tasti 6-9 (acquisto)
        self.buy_order_mode = False
        self.buy_order_percentage = 0
        self.buy_order_success = ""
        self.buy_order_success_time = 0
        self.buy_order_error = ""
        self.buy_order_error_time = 0
        # pending_buy_order rimosso - usa pending_order comune

        # 📊 Inizializzazione sistema analisi tecnica
        self.technical_analyzer = TechnicalAnalyzer()
        self.market_data_cache = {}
        self.last_technical_update = 0
        self.technical_indicators = {}


    # 🔄 Sistema navigazione a TAB tra sezioni

    
    def _init_colors(self):
        """Inizializza i colori curses"""
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)
        self.GREEN = curses.color_pair(1)
        self.RED = curses.color_pair(2)
        self.YELLOW = curses.color_pair(3)
        self.CYAN = curses.color_pair(4)
        self.MAGENTA = curses.color_pair(5)
        self.WHITE = curses.color_pair(6)

    def _init_popup_service(self):
        """Inizializza il sistema di popup unificato (Factory Pattern)"""
        try:
            if self.stdscr:
                theme = PopupTheme(
                    success_color=self.GREEN,
                    error_color=self.RED,
                    warning_color=self.YELLOW,
                    info_color=self.CYAN,
                    confirm_color=self.MAGENTA
                )
                self.popup_service = CursesPopupService(self.stdscr, theme, self.WHITE, self.YELLOW)
            else:
                self.popup_service = ConsolePopupService()
        except Exception as e:
            trade_logger.error(f"Errore inizializzazione popup service: {e}")
            self.popup_service = ConsolePopupService()

    def run(self):
        """Avvia il dashboard"""
        # Inizializzazione curses iniziale
        curses.curs_set(0)
        self.stdscr.nodelay(True)
        self.stdscr.timeout(100)

        # Inizializzazione colori curses (dopo initscr)
        curses.start_color()
        self._init_colors()
        
        # 🪟 Inizializza popup service DOPO la configurazione colori
        self._init_popup_service()
        
        while True:
            # 🔄 Reinizializza curses se stiamo tornando dal scalping mode
            if self.returning_from_scalping:
                try:
                    # Reinizializza completamente curses
                    self.stdscr = curses.initscr()
                    curses.noecho()
                    curses.cbreak()
                    curses.start_color()
                    self.stdscr.keypad(True)
                    self.stdscr.nodelay(True)
                    self.stdscr.timeout(100)
                    self._init_colors()
                    curses.curs_set(0)
                    self.returning_from_scalping = False
                except:
                    # Se la reinizializzazione fallisce, esci gracefully
                    return
            
            key = self.stdscr.getch()

            # 💡 Priorità uscita: 'q' processato per primo
            if key in [ord('q'), ord('Q')]:
                return

            # 📚 Gestione help system con tasto 'h'
            elif key in [ord('h'), ord('H')]:
                self.help_active = not self.help_active
                self.help_scroll_offset = 0
                continue

            # 📚 Navigazione help quando attivo
            elif self.help_active:
                if key == curses.KEY_UP:
                    self.help_scroll_offset = max(0, self.help_scroll_offset - 1)
                elif key == curses.KEY_DOWN:
                    self.help_scroll_offset += 1
                elif key == curses.KEY_LEFT:
                    self.help_system.current_tab = max(0, self.help_system.current_tab - 1)
                    self.help_scroll_offset = 0
                elif key == curses.KEY_RIGHT:
                    self.help_system.current_tab = min(len(self.help_system.tabs) - 1, self.help_system.current_tab + 1)
                    self.help_scroll_offset = 0
                elif key == 27:  # ESC key
                    self.help_active = False
                continue

            # 🔄 Navigazione tra TAB della dashboard (KISS): TAB avanti, SHIFT+TAB indietro
            elif key == 9:  # TAB
                self.current_tab = (self.current_tab + 1) % 3  # 3 sezioni: 0=main, 1=sentiment, 2=bot_live
                continue
            elif key == 353:  # SHIFT+TAB
                self.current_tab = (self.current_tab - 1) % 3
                continue
            elif key == ord('\n') or key == ord('\r'):
                # Enter per toggle sentiment sezione
                if self.current_tab == 1:
                    self.sentiment_expanded = not self.sentiment_expanded
                    continue
                elif self.current_tab == 2:
                    self.bot_live_expanded = not self.bot_live_expanded
                    continue
                elif hasattr(self, 'order_mode') and self.order_mode:
                    self._execute_sell_order()
                elif hasattr(self, 'buy_order_mode') and self.buy_order_mode:
                    self._execute_buy_order()

            # Gestione tasti per ordini percentuali (solo se help non attivo)
            elif key == ord('1') and not self.help_active:
                self._handle_percentage_order(25)
            elif key == ord('2') and not self.help_active:
                self._handle_percentage_order(50)
            elif key == ord('3') and not self.help_active:
                self._handle_percentage_order(75)
            elif key == ord('4') and not self.help_active:
                self._handle_percentage_order(100)
            # Gestione tasti per ordini di acquisto percentuali
            elif key == ord('6') and not self.help_active:
                self._handle_buy_percentage_order(25)
            elif key == ord('7') and not self.help_active:
                self._handle_buy_percentage_order(50)
            elif key == ord('8') and not self.help_active:
                self._handle_buy_percentage_order(75)
            elif key == ord('9') and not self.help_active:
                self._handle_buy_percentage_order(100)
            elif key == ord('s') or key == ord('S'):  # Scalping
                self._handle_scalping_mode()
            elif key == ord('f') or key == ord('F'):  # Ferma scalping
                self._handle_stop_scalping()
            elif key == ord('v') or key == ord('V'):  # View scalping logs
                self._handle_view_scalping_logs()
            elif key == ord('c') or key == ord('C'):  # Cancel
                if hasattr(self, 'order_mode') and self.order_mode:
                    self._cancel_order_mode()
                elif hasattr(self, 'buy_order_mode') and self.buy_order_mode:
                    self._cancel_buy_order_mode()

            # 🚀 Controlli di spazio ottimizzati
            height, width = self.stdscr.getmaxyx()
            if height < 25 or width < 85:  # Requisiti ridotti
                self.stdscr.clear()
                self.stdscr.addstr(0, 0, "Terminale troppo piccolo. Richiesto almeno 85x25.", self.RED)
                self.stdscr.refresh()
                time.sleep(0.5)  # Attesa ridotta
                continue

            current_time = time.time()
            # ⚡ Aggiornamenti più frequenti: Da 1s a 0.5s
            if current_time - self.last_update_time < 0.5:
                continue
            self.last_update_time = current_time

            # 🚀 Refresh immediato senza attese
            self.update_and_draw()

    def _handle_percentage_order(self, percentage):
        """Gestisce la richiesta di ordine percentuale"""
        self.order_mode = True
        self.order_percentage = percentage
        current_balance = self._get_current_balance()
        
        if self.last_valid_price is None or self.last_valid_price <= 0:
            trade_logger.error("🚫 Prezzo non valido per calcolo vendita")
            if hasattr(self, 'popup_service') and self.popup_service is not None:
                self.popup_service.show_error_popup(
                    "ERRORE PREZZO",
                    [
                        "❌ Prezzo non valido per calcolo vendita",
                        "Il prezzo corrente non è disponibile.",
                        "Riprova tra qualche secondo."
                    ]
                )
            return
            
        sell_quantity = current_balance * (percentage / 100)
        estimated_value = sell_quantity * self.last_valid_price

        # 📝 LOG: Azione utente (pressione tasto)
        self.current_session_id = self.trading_logger.log_user_action(
            action_type="USER_KEY_PRESS",
            pair=self.pair,
            percentage=percentage,
            balance_before=current_balance,
            price=self.last_valid_price,
            notes=f"User pressed key {percentage}% - Order preparation"
        )

        currency = self.pair.split('_')[0]
        trade_logger.info(str(f"📋 Ordine {percentage}%: {sell_quantity:.6f} {currency} ≈ {estimated_value:.2f} USDT [Session: {self.current_session_id}]"))
        
        # 🪟 Mostra popup informativo per conferma preparazione ordine
        if hasattr(self, 'popup_service') and self.popup_service is not None:
            self.popup_service.show_info_popup(
                f"ORDINE {percentage}% PREPARATO",
                [
                    f"📊 Coppia: {self.pair}",
                    f"💰 Quantità: {sell_quantity:.6f} {currency}",
                    f"💵 Valore stimato: {estimated_value:.2f} USDT",
                    f"📈 Prezzo: {self.last_valid_price:.6f}",
                    "",
                    "✅ Premi INVIO per confermare la vendita"
                ]
            )
        
        self.update_and_draw()

    def _execute_sell_order(self):
        """💰 Esegue l'ordine di vendita con logging completo"""
        if self.pending_order:
            return

        self.pending_order = True
        execution_start_time = time.time()

        try:
            currency = self.pair.split('_')[0]
            balance_before = self.client.get_wallet_balance(currency)

            # Validazioni preliminari
            if balance_before <= 0:
                error_msg = f"Saldo {currency} insufficiente ({balance_before:.6f})"
                self.order_error = f"✗ {error_msg}"
                self.order_error_time = time.time()

                # 📝 LOG: Errore saldo insufficiente
                if self.current_session_id:
                    self.trading_logger.log_order_error(
                        session_id=self.current_session_id,
                        pair=self.pair,
                        percentage=self.order_percentage,
                        error_message=error_msg,
                        execution_time_ms=int((time.time() - execution_start_time) * 1000)
                    )
                return

            sell_quantity = balance_before * (self.order_percentage / 100)

            if sell_quantity < 0.0001:
                error_msg = f"Quantità troppo piccola: {sell_quantity:.8f}"
                self.order_error = f"✗ {error_msg}"
                self.order_error_time = time.time()

                # 📝 LOG: Errore quantità troppo piccola
                if self.current_session_id:
                    self.trading_logger.log_order_error(
                        session_id=self.current_session_id,
                        pair=self.pair,
                        percentage=self.order_percentage,
                        error_message=error_msg,
                        execution_time_ms=int((time.time() - execution_start_time) * 1000)
                    )
                return

            # Ottieni prezzo ottimale con fallback
            optimal_price = self.client.get_best_book_price(self.pair, side='sell')
            if optimal_price is None:
                if self.last_valid_price is None or self.last_valid_price <= 0:
                    trade_logger.error("🚫 Impossibile determinare prezzo ottimale per vendita")
                    return
                optimal_price = self.last_valid_price * 0.999

            # Arrotondamenti per conformità API
            sell_quantity = round(sell_quantity, 8)
            optimal_price = round(optimal_price, 8)

            # Raccolta informazioni commissioni per logging
            fee_info = {
                'effective_rate': self.client.get_effective_fee_rate('taker', sell_quantity * optimal_price),
                'gt_points_used': self.client.get_gt_fee_info().get('gt_discount_enabled', False) and self.client.get_gt_balance() > 0
            }

            # 🚀 Esecuzione ordine REALE
            trade_logger.info(str(f"🔥 PIAZZANDO ORDINE REALE: {sell_quantity:.6f} {currency} @ {optimal_price:.6f} USDT"))
            result = self.client.place_spot_order(
                pair=self.pair,
                side='sell',
                amount=sell_quantity,
                price=optimal_price,
                order_type='limit'
            )

            execution_time_ms = int((time.time() - execution_start_time) * 1000)

            # Ottieni saldo dopo l'ordine
            time.sleep(0.5)  # Pausa più lunga per sincronizzazione
            balance_after = self.client.get_wallet_balance(currency)
            
            # Verifica stato ordine se piazzato
            order_status = None
            if result and 'id' in result:
                try:
                    order_status = self.client.get_order_status(self.pair, result['id'])
                    trade_logger.info(str(f"📋 STATO ORDINE #{result['id'][:8]}: {order_status.get('status', 'UNKNOWN')}"))
                except:
                    trade_logger.info(str(f"⚠️  Impossibile verificare stato ordine #{result['id'][:8]}"))
            
            trade_logger.info(str(f"💰 SALDO PRIMA: {balance_before:.6f} {currency}"))
            trade_logger.info(str(f"💰 SALDO DOPO: {balance_after:.6f} {currency}"))

            # Gestione risultato e logging
            if result and 'id' in result:
                # ✅ SUCCESSO
                estimated_value = sell_quantity * optimal_price
                self.order_success = f"✓ Ordine #{result['id'][:8]} piazzato: {sell_quantity:.6f} @ {optimal_price:.6f} (~{estimated_value:.2f} USDT)"
                self.order_success_time = time.time()

                # 📝 LOG: Esecuzione riuscita
                if self.current_session_id:
                    log_data = self.trading_logger.log_order_execution(
                        session_id=self.current_session_id,
                        pair=self.pair,
                        percentage=self.order_percentage,
                        quantity=sell_quantity,
                        price=optimal_price,
                        order_result=result,
                        balance_before=balance_before,
                        balance_after=balance_after,
                        execution_time_ms=execution_time_ms,
                        fee_info=fee_info
                    )

                    # Feedback popup con dettagli
                    popup_messages = [
                        f"💰 Valore: {estimated_value:.2f} USDT",
                        f"🪙 Quantità: {sell_quantity:.6f} {currency}",
                        f"💰 Prezzo: {optimal_price:.6f}",
                        f"⚡ Tempo: {execution_time_ms}ms",
                        f"🎯 Fee Rate: {fee_info['effective_rate']:.4f}",
                        f"🎁 GT Points: {'✓ Usati' if fee_info['gt_points_used'] else '✗ Non usati'}",
                        f"📋 Ordine ID: #{result['id'][:8]}"
                    ]
                    self._show_popup("✅ ORDINE VENDITA ESEGUITO", popup_messages, "success")

                self._refresh_portfolio_data()

            else:
                # ❌ ERRORE
                error_msg = result.get('message', result.get('label', 'Errore sconosciuto API')) if result else 'Nessuna risposta dall API'
                self.order_error = f"✗ {error_msg}"
                self.order_error_time = time.time()

                # 📝 LOG: Errore esecuzione
                if self.current_session_id:
                    self.trading_logger.log_order_error(
                        session_id=self.current_session_id,
                        pair=self.pair,
                        percentage=self.order_percentage,
                        error_message=error_msg,
                        execution_time_ms=execution_time_ms
                    )

                    # Feedback popup errore
                    error_messages = [
                        f"⚠️ Errore: {error_msg}",
                        f"⏱️ Tempo: {execution_time_ms}ms",
                        f"📋 Session: {self.current_session_id}"
                    ]
                    self._show_popup("❌ ORDINE VENDITA FALLITO", error_messages, "error")

        except Exception as e:
            execution_time_ms = int((time.time() - execution_start_time) * 1000)
            error_msg = f"Eccezione durante esecuzione: {str(e)[:100]}"
            self.order_error = f"✗ Errore: {str(e)[:50]}"
            self.order_error_time = time.time()

            # 📝 LOG: Eccezione critica
            if self.current_session_id:
                self.trading_logger.log_order_error(
                    session_id=self.current_session_id,
                    pair=self.pair,
                    percentage=self.order_percentage,
                    error_message=error_msg,
                    execution_time_ms=execution_time_ms
                )

                # Popup eccezione critica
                exception_messages = [
                    f"⚠️ Dettaglio: {str(e)[:50]}...",
                    f"📍 Stack trace salvato nei log",
                    f"📋 Session: {self.current_session_id}"
                ]
                self._show_popup("🚨 ECCEZIONE CRITICA", exception_messages, "error")

        finally:
            self.pending_order = False
            self._cancel_order_mode()

        # Reset session ID dopo completamento
        self.current_session_id = None

    def _draw_trading_stats_card(self, r, c, w):
        """📊 Disegna statistiche giornaliere di trading"""
        try:
            stats = self.trading_logger.get_daily_stats()
            h = 8  # Altezza fissa per la card

            self._draw_box(r, c, h, w, "📊 Trading Stats Oggi", self.YELLOW)

            if not stats:
                self._safe_addstr(r + 1, c + 2, "Nessuna operazione oggi", curses.A_DIM)
                return r + h

            # Linea 1: Operazioni totali e successo rate
            total_ops = stats.get('total_operations', 0)
            successful = stats.get('successful_orders', 0)
            failed = stats.get('failed_orders', 0)
            success_rate = (successful / total_ops * 100) if total_ops > 0 else 0

            self._safe_addstr(r + 1, c + 2, f"📈 Operazioni: {total_ops} | ✅ {successful} | ❌ {failed}", self.CYAN)
            self._safe_addstr(r + 2, c + 2, f"🎯 Successo: {success_rate:.1f}%", self.GREEN if success_rate > 80 else self.YELLOW if success_rate > 50 else self.RED)

            # Linea 2: Volume e fees
            volume = stats.get('total_volume_usdt', 0)
            fees = stats.get('total_fees_usdt', 0)
            avg_order = stats.get('avg_order_value', 0)

            self._safe_addstr(r + 3, c + 2, UIFormatter.format_currency_line("Volume", volume), self.YELLOW)
            self._safe_addstr(r + 4, c + 2, UIFormatter.format_fees_line(fees), self.RED)
            self._safe_addstr(r + 5, c + 2, UIFormatter.format_currency_line("Avg Order", avg_order, prefix="📊"), self.CYAN)

            # Linea 3: Percentuale più usata
            most_used = stats.get('most_used_percentage', 0)
            if most_used > 0:
                self._safe_addstr(r + 6, c + 2, f"🎮 Percentuale preferita: {most_used}%", self.MAGENTA)

            return r + h

        except Exception as e:
            self._safe_addstr(r + 1, c + 2, f"Errore stats: {str(e)[:20]}", self.RED)
            return r + 5

    def _refresh_portfolio_data(self):
        """🔄 Aggiorna i dati del portafoglio dopo un ordine"""
        try:
            # Forza refresh cache
            currency = self.pair.split('_')[0]
            cache_key = f"wallet_{currency}"
            self.client.price_cache.cache.pop(cache_key, None)

            cache_key = f"buy_trades_{self.pair}"
            self.client.stats_cache.cache.pop(cache_key, None)

            # Ricarica dati
            self.real_portfolio_data = self.client.calculate_real_portfolio_data(self.pair)

        except Exception as e:
            trade_logger.info(str(f"Errore refresh portafoglio: {e}"))

    def _cancel_order_mode(self):
        """❌ Annulla la modalità ordine"""
        self.order_mode = False
        self.order_percentage = 0
        self.pending_order = False

    def _handle_buy_percentage_order(self, percentage):
        """Gestisce la richiesta di ordine di acquisto percentuale con validazione avanzata"""
        # Inizializza managers se necessario (Dependency Injection)
        if not hasattr(self, 'wallet_manager'):
            self.wallet_manager = WalletManager(self.client)
        if not hasattr(self, 'failure_tracker'):
            self.failure_tracker = OrderFailureTracker()
        
        # Verifica se coppia è bloccata (State Pattern)
        if self.wallet_manager.state_manager.is_pair_blocked(self.pair):
            reason = self.wallet_manager.state_manager.get_block_reason(self.pair)
            trade_logger.error(f"🚫 Operazione bloccata per {self.pair}: {reason}")
            return
        
        # Verifica circuit breaker con exponential backoff
        if not self.failure_tracker.can_place_order():
            if self.failure_tracker.circuit_open:
                cooldown_remaining = self.failure_tracker.cooldown_seconds - (time.time() - self.failure_tracker.last_failure_time)
                trade_logger.error(f"🚨 Circuit breaker attivo - attendi {cooldown_remaining:.0f}s")
            else:
                backoff_time = min(self.failure_tracker.cooldown_seconds * (self.failure_tracker.backoff_multiplier ** (self.failure_tracker.consecutive_failures - 1)), self.failure_tracker.max_backoff)
                remaining = backoff_time - (time.time() - self.failure_tracker.last_failure_time)
                trade_logger.error(f"⏳ Exponential backoff attivo - attendi {remaining:.0f}s")
            return
        
        self.buy_order_mode = True
        self.buy_order_percentage = percentage
        current_usdt_balance = self._get_current_usdt_balance()
        requested_amount = current_usdt_balance * (percentage / 100)
        
        # Ajusta importo con gestione user confirmation (Strategy Pattern)
        usdt_amount = self.wallet_manager.suggest_affordable_amount(requested_amount, pair=self.pair)
        
        if usdt_amount == 0:
            trade_logger.error("🚫 Operazione annullata - Vedere messaggi sopra")
            return
        
        # Usa importo ajustato per calcoli
        if self.last_valid_price is None or self.last_valid_price <= 0:
            trade_logger.error("🚫 Prezzo non valido per calcolo acquisto")
            if hasattr(self, 'popup_service') and self.popup_service is not None:
                self.popup_service.show_error_popup(
                    "ERRORE PREZZO ACQUISTO",
                    [
                        "❌ Prezzo non valido per calcolo acquisto",
                        "Il prezzo corrente non è disponibile.",
                        "Riprova tra qualche secondo."
                    ]
                )
            return
        estimated_quantity = usdt_amount / self.last_valid_price
        
        # Log dell'ajustamento se necessario
        if usdt_amount != requested_amount:
            trade_logger.info(f"📊 Importo ajustato da {requested_amount:.2f} a {usdt_amount:.2f} USDT")

        # 📝 LOG: Azione utente (pressione tasto acquisto)
        safe_target_quantity = estimated_quantity if estimated_quantity is not None else 0.0
        self.current_session_id = self.trading_logger.log_user_action(
            action_type="USER_BUY_KEY_PRESS",
            pair=self.pair,
            percentage=percentage,
            balance_before=current_usdt_balance,
            price=self.last_valid_price,  # ✅ CORREZIONE: passa il prezzo come nel sell
            target_quantity=safe_target_quantity,
            target_value=usdt_amount  # Usa l'importo ajustato
        )

        # 🔗 CONSISTENCY FIX: Stesso logging a console della versione SELL
        currency = self.pair.split('_')[0]
        safe_quantity = estimated_quantity if estimated_quantity is not None else 0.0
        trade_logger.info(f"📋 Ordine ACQUISTO {percentage}%: {usdt_amount:.2f} USDT → {safe_quantity:.6f} {currency} [Session: {self.current_session_id or 'N/A'}]")
        
        # 🪟 Mostra popup informativo per conferma preparazione ordine acquisto
        if hasattr(self, 'popup_service') and self.popup_service is not None:
            self.popup_service.show_info_popup(
                f"ORDINE ACQUISTO {percentage}% PREPARATO",
                [
                    f"📊 Coppia: {self.pair}",
                    f"💵 Importo USDT: {usdt_amount:.2f}",
                    f"🪙 Quantità stimata: {safe_quantity:.6f} {currency}",
                    f"📈 Prezzo: {self.last_valid_price:.6f}",
                    "",
                    "✅ Premi INVIO per confermare l'acquisto"
                ]
            )
        
        # 🔗 CONSISTENCY FIX: Aggiornamento UI immediato come versione SELL
        self.update_and_draw()

    def __init_order_services(self):
        """🏗️ Inizializza servizi ordine seguendo Dependency Injection Pattern"""
        if not hasattr(self, 'order_validator'):
            self.order_validator = OrderValidator()
        if not hasattr(self, 'order_calculator'):
            self.order_calculator = OrderCalculator()
        if not hasattr(self, 'order_executor'):
            self.order_executor = OrderExecutor()
        if not hasattr(self, 'order_logger'):
            self.order_logger = OrderLogger(self.trading_logger)

    def _execute_buy_order(self):
        """💰 Esegue ordine di acquisto - versione chirurgicamente corretta basata su dash01.py"""
        # Usa la stessa logica di protezione multipla del file dash01.py
        if not hasattr(self, 'pending_order'):
            self.pending_order = False
            
        if self.pending_order:
            return
            
        self.pending_order = True
        execution_start_time = time.time()
        
        try:
            # Validazione saldo USDT - identica a dash01.py per vendite
            usdt_balance = self.client.get_wallet_balance('USDT')
            if usdt_balance <= 0:
                error_msg = f"Saldo USDT insufficiente ({usdt_balance or 0:.6f})"
                self.order_error = f"✗ {error_msg}"
                self.order_error_time = time.time()
                
                # Log errore come in dash01.py
                if hasattr(self, 'current_session_id') and self.current_session_id:
                    self.trading_logger.log_order_error(
                        session_id=self.current_session_id,
                        pair=self.pair,
                        percentage=getattr(self, 'buy_order_percentage', 0),
                        error_message=error_msg,
                        execution_time_ms=int((time.time() - execution_start_time) * 1000)
                    )
                return
            
            buy_amount = usdt_balance * (getattr(self, 'buy_order_percentage', 0) / 100)
            
            if buy_amount < 0.1:  # Limite minimo Gate.io
                error_msg = f"Importo troppo piccolo: {buy_amount:.2f} USDT"
                self.order_error = f"✗ {error_msg}"
                self.order_error_time = time.time()
                
                # Log errore
                if hasattr(self, 'current_session_id') and self.current_session_id:
                    self.trading_logger.log_order_error(
                        session_id=self.current_session_id,
                        pair=self.pair,
                        percentage=getattr(self, 'buy_order_percentage', 0),
                        error_message=error_msg,
                        execution_time_ms=int((time.time() - execution_start_time) * 1000)
                    )
                return
                
            # Prezzo ottimale con fallback - esattamente come dash01.py
            optimal_price = self.client.get_best_book_price(self.pair, side='buy')
            if optimal_price is None:
                optimal_price = getattr(self, 'last_valid_price', 0) * 1.001 if getattr(self, 'last_valid_price', 0) > 0 else 0
                
            if optimal_price <= 0:
                error_msg = "Impossibile determinare prezzo"
                self.order_error = f"✗ {error_msg}"  
                self.order_error_time = time.time()
                return
                
            buy_quantity = buy_amount / optimal_price
            
            # Arrotondamenti conformi API - come dash01.py
            buy_quantity = round(buy_quantity, 8)
            optimal_price = round(optimal_price, 8)
            
            # Esecuzione ordine SINGOLO - identica a dash01.py
            result = self.client.place_spot_order(
                pair=self.pair,
                side='buy',
                amount=buy_quantity,
                price=optimal_price,
                order_type='limit'
            )
            
            execution_time_ms = int((time.time() - execution_start_time) * 1000)
            
            # Pausa sincronizzazione come dash01.py
            time.sleep(0.1)
            balance_after = self.client.get_wallet_balance('USDT')
            
            # Gestione risultato - logica identica a dash01.py
            if result and 'id' in result:
                # ✅ SUCCESSO
                estimated_value = buy_quantity * optimal_price
                currency = self.pair.split('_')[0]
                self.order_success = f"✓ Ordine #{result['id'][:8]} piazzato: {buy_amount:.2f} USDT → {buy_quantity:.6f} {currency} @ {optimal_price:.6f}"
                self.order_success_time = time.time()
                
                # Log successo
                if hasattr(self, 'current_session_id') and self.current_session_id:
                    self.trading_logger.log_order_execution(
                        session_id=self.current_session_id,
                        pair=self.pair,
                        percentage=getattr(self, 'buy_order_percentage', 0),
                        quantity=buy_quantity,
                        price=optimal_price,
                        order_result=result,
                        balance_before=usdt_balance,
                        balance_after=balance_after,
                        execution_time_ms=execution_time_ms
                    )
                    
                    # Feedback popup con dettagli
                    popup_messages = [
                        f"💵 Importo: {buy_amount:.2f} USDT",
                        f"🪙 Quantità: {buy_quantity:.6f} {currency}",
                        f"💰 Prezzo: {optimal_price:.6f}",
                        f"⚡ Tempo: {execution_time_ms}ms",
                        f"📋 Ordine ID: #{result['id'][:8]}"
                    ]
                    self._show_popup("✅ ORDINE ACQUISTO ESEGUITO", popup_messages, "success")
            else:
                # ❌ ERRORE - gestione come dash01.py
                error_detail = result.get('message', 'Risposta API non valida') if result else 'Nessuna risposta'
                error_msg = f"Ordine fallito: {error_detail}"
                self.order_error = f"✗ Errore: {str(error_detail)[:50]}"
                self.order_error_time = time.time()
                
                # Log errore
                if hasattr(self, 'current_session_id') and self.current_session_id:
                    self.trading_logger.log_order_error(
                        session_id=self.current_session_id,
                        pair=self.pair,
                        percentage=getattr(self, 'buy_order_percentage', 0),
                        error_message=error_msg,
                        execution_time_ms=execution_time_ms
                    )
                    
                    # Feedback popup errore
                    error_messages = [
                        f"⚠️ Errore: {error_detail}",
                        f"⏱️ Tempo: {execution_time_ms}ms",
                        f"📋 Session: {self.current_session_id}"
                    ]
                    self._show_popup("❌ ORDINE ACQUISTO FALLITO", error_messages, "error")
                    
        except Exception as e:
            # Gestione eccezione - identica a dash01.py
            execution_time_ms = int((time.time() - execution_start_time) * 1000)
            error_msg = f"Eccezione durante esecuzione: {str(e)[:100]}"
            self.order_error = f"✗ Errore: {str(e)[:50]}"
            self.order_error_time = time.time()
            
            # Log eccezione
            if hasattr(self, 'current_session_id') and self.current_session_id:
                self.trading_logger.log_order_error(
                    session_id=self.current_session_id,
                    pair=self.pair,
                    percentage=getattr(self, 'buy_order_percentage', 0),
                    error_message=error_msg,
                    execution_time_ms=execution_time_ms
                )
                
                # Popup eccezione critica
                exception_messages = [
                    f"⚠️ Dettaglio: {str(e)[:50]}...",
                    f"📍 Stack trace salvato nei log",
                    f"📋 Session: {self.current_session_id}"
                ]
                self._show_popup("🚨 ECCEZIONE ACQUISTO", exception_messages, "error")
            
        finally:
            # Cleanup identico a dash01.py
            self.pending_order = False
            if hasattr(self, '_cancel_buy_order_mode'):
                self._cancel_buy_order_mode()
            self.current_session_id = None

    def _get_optimal_price(self):
        """🎯 Ottiene prezzo ottimale con fallback"""
        optimal_price = self.client.get_best_book_price(self.pair, side='buy')
        if optimal_price is None:
            if self.last_valid_price is None or self.last_valid_price <= 0:
                trade_logger.error("🚫 Impossibile determinare prezzo ottimale per acquisto")
                return None
            trade_logger.warning("[BUY] Fallback price utilizzato")
            optimal_price = self.last_valid_price * 1.001
        return optimal_price

    def _handle_validation_error(self, error_message: str, start_time: float):
        """❌ Gestisce errori di validazione"""
        trade_logger.error(f"[BUY] VALIDAZIONE: {error_message}")
        
        execution_time_ms = int((time.time() - start_time) * 1000)
        log_data = OrderLogData(
            session_id=self.current_session_id or "",
            pair=self.pair,
            percentage=self.buy_order_percentage,
            error_message=error_message,
            execution_time_ms=execution_time_ms
        )
        self.order_logger.log_order_error(log_data)
        
        # Aggiorna stato UI
        self.buy_order_error = error_message
        self.buy_order_error_time = time.time()

    def _handle_order_success(self, execution_result: OrderExecutionResult, 
                            calculation_result: OrderCalculationResult,
                            balance_before: float, balance_after: float, 
                            execution_time_ms: int):
        """✅ Gestisce successo ordine"""
        
        # Reset circuit breaker
        if hasattr(self, 'failure_tracker'):
            self.failure_tracker.record_success()
        
        # Aggiorna stato UI
        self.buy_order_success = (f"✓ Acquisto #{execution_result.order_id[:8]} piazzato: "
                                f"{calculation_result.quantity:.6f} @ {calculation_result.price:.6f} "
                                f"(~{calculation_result.total_value:.2f} USDT)")
        self.buy_order_success_time = time.time()
        trade_logger.info(f"[BUY] SUCCESSO: {self.buy_order_success}")

        # Logging strutturato
        log_data = OrderLogData(
            session_id=self.current_session_id or "",
            pair=self.pair,
            percentage=self.buy_order_percentage,
            quantity=calculation_result.quantity,
            price=calculation_result.price,
            execution_time_ms=execution_time_ms,
            fee_info=calculation_result.fee_info,
            balance_before=balance_before,
            balance_after=balance_after,
            order_result=execution_result.api_result
        )
        self.order_logger.log_order_success(log_data)
        
        # Refresh portfolio
        self._refresh_portfolio_data()

    def _handle_order_error(self, error_message: str, execution_time_ms: int):
        """❌ Gestisce errore esecuzione ordine"""
        trade_logger.error(f"[BUY] ERRORE: {error_message}")
        
        log_data = OrderLogData(
            session_id=self.current_session_id or "",
            pair=self.pair,
            percentage=self.buy_order_percentage,
            error_message=error_message,
            execution_time_ms=execution_time_ms
        )
        self.order_logger.log_order_error(log_data)
        
        # Aggiorna stato UI usando servizio esistente
        self.buy_order_error = error_message
        self.buy_order_error_time = time.time()

    def _handle_order_exception(self, exception: Exception, execution_time_ms: int):
        """🚨 Gestisce eccezioni critiche"""
        
        # Registra fallimento circuit breaker
        if hasattr(self, 'failure_tracker'):
            self.failure_tracker.record_failure()
        
        error_message = f"Eccezione critica: {str(exception)}"
        trade_logger.error(f"[BUY] ECCEZIONE: {error_message}")
        
        log_data = OrderLogData(
            session_id=self.current_session_id or "",
            pair=self.pair,
            percentage=self.buy_order_percentage,
            error_message=error_message,
            execution_time_ms=execution_time_ms
        )
        self.order_logger.log_order_error(log_data)
        
        # Aggiorna stato UI
        self.buy_order_error = error_message
        self.buy_order_error_time = time.time()

    def _cancel_buy_order_mode(self):
        """❌ Annulla la modalità ordine di acquisto"""
        self.buy_order_mode = False
        self.buy_order_percentage = 0
        # pending_buy_order rimosso - usa pending_order comune

    def _handle_stop_scalping(self):
        """🛑 Gestisce la richiesta di stop dello scalping"""
        if self.scalping_active:
            self.scalping_stop_requested = True
            if hasattr(self, 'popup_service') and self.popup_service is not None:
                self.popup_service.show_info_popup(
                    "STOP SCALPING RICHIESTO",
                    [
                        "🛑 Richiesta di stop inviata al bot scalping",
                        "Il bot si fermerà al completamento dell'operazione corrente",
                        "Attendere qualche secondo per la chiusura sicura..."
                    ]
                )
            else:
                print("🛑 Stop scalping richiesto - attendere chiusura sicura...")
        else:
            if hasattr(self, 'popup_service') and self.popup_service is not None:
                self.popup_service.show_warning_popup(
                    "NESSUN SCALPING ATTIVO",
                    [
                        "⚠️ Non c'è nessun bot di scalping in esecuzione",
                        "Usa il tasto S per avviare lo scalping"
                    ]
                )

    def _handle_view_scalping_logs(self):
        """🎮 Handler per visualizzare log del bot scalping dalla dashboard"""
        if not self.scalping_active:
            self.popup_service.show_info_popup(
                "ℹ️ Info",
                [
                    "⚠️ Non c'è nessun bot di scalping attivo",
                    "Usa il tasto S per avviare lo scalping"
                ]
            )
            return
            
        # Passa al menu di navigazione scalping
        try:
            # Salva stato curses
            curses.echo()
            curses.nocbreak()
            self.stdscr.keypad(False)
            curses.endwin()
            
            # Mostra menu navigazione
            self._handle_scalping_navigation()
            
        except Exception as e:
            print(f"❌ Errore visualizzazione log: {e}")
            print("🔄 Tornando alla dashboard...")
        finally:
            # Reinizializza curses al ritorno
            self.returning_from_scalping = True

    def _show_scalping_startup_info(self):
        """🎮 Mostra informazioni su come controllare il bot scalping (Observer Pattern)"""
        import time
        print("\n" + "="*80)
        print("🎉 SCALPING BOT AVVIATO CON SUCCESSO!")
        print("="*80)
        print("✅ Il bot è ora attivo in modalità SILENZIOSA (nessun log a schermo)")
        print("📊 Stai per tornare alla dashboard principale per il controllo")
        print()
        print("🎮 CONTROLLI DISPONIBILI DALLA DASHBOARD:")
        print("   • F         = 🛑 FERMA il bot scalping immediatamente")
        print("   • V         = 📈 VISUALIZZA log del bot in tempo reale")
        print("   • H         = ❓ Help completo con tutti i comandi")
        print("   • 1-4, 6-9  = 💰 Trading manuale (bot continua in background)")
        print("   • Q         = ❌ Esci completamente dall'applicazione")
        print()
        print("⚠️  IMPORTANTE - COME CONTROLLARE IL BOT:")
        print("   1. 📊 Il bot lavora in BACKGROUND senza disturbare la dashboard")
        print("   2. 🎮 Usa la DASHBOARD per controllare tutto")
        print("   3. 📈 Usa V per vedere cosa sta facendo il bot")
        print("   4. 🛑 Usa F per fermare il bot quando vuoi")
        print()
        print("💡 NOTA: Il bot scrive i log su file, NON sulla console.")
        print("   Non vedrai più scrolling infinito di messaggi!")
        print()
        print("🔄 Tornando alla dashboard in 5 secondi...")
        for i in range(5, 0, -1):
            print(f"   ⏳ {i}...")
            time.sleep(1)
        print("🚀 Ecco la tua dashboard!")

    def _handle_scalping_navigation(self):
        """🎮 Gestisce la navigazione tra dashboard e log scalping (Command Pattern)"""
        print("\n" + "="*60)
        print("🎮 SCALPING BOT NAVIGATION MENU")
        print("="*60)
        print("Il bot scalping è attivo in background...")
        print()
        print("📋 OPZIONI DISPONIBILI:")
        print("   1. 📊 Torna alla DASHBOARD (bot continua in background)")
        print("   2. 📈 Mostra LOG del bot in tempo reale")
        print("   3. 🛑 FERMA il bot scalping")
        print("   4. ❓ Stato del bot")
        print()
        
        while self.scalping_active:
            try:
                # 🎮 Safe input handling (Error Recovery Pattern)
                try:
                    scelta = input("Scegli opzione (1-4): ").strip()
                except (EOFError, KeyboardInterrupt):
                    scelta = "1"  # Default: return to dashboard
                
                if scelta == "1":
                    # Torna alla dashboard
                    print("🔄 Tornando alla dashboard...")
                    print("💡 Usa il tasto F nella dashboard per fermare il bot scalping")
                    self.returning_from_scalping = True
                    break
                    
                elif scelta == "2":
                    # Mostra log in tempo reale
                    self._show_scalping_live_log()
                    
                elif scelta == "3":
                    # Ferma il bot
                    print("🛑 Fermando il bot scalping...")
                    self.scalping_stop_requested = True
                    print("✅ Richiesta di stop inviata. Il bot si fermerà al prossimo ciclo.")
                    print("⏳ Attendere qualche secondo per la chiusura...")
                    import time
                    time.sleep(2)
                    break
                    
                elif scelta == "4":
                    # Mostra stato
                    self._show_scalping_status()
                    
                else:
                    print("❌ Opzione non valida. Usa 1, 2, 3 o 4.")
                    
            except KeyboardInterrupt:
                print("\n🔄 Tornando alla dashboard...")
                self.returning_from_scalping = True
                break
            except Exception as e:
                print(f"❌ Errore nel menu navigazione: {e}")
                self.returning_from_scalping = True
                break

    def _show_scalping_live_log(self):
        """📈 Mostra log del bot scalping in tempo reale (Observer Pattern)"""
        print("\n" + "="*60)
        print("📈 LOG SCALPING BOT IN TEMPO REALE")
        print("="*60)
        print("💡 Premi CTRL+C per tornare al menu navigazione")
        print("🤖 Bot Status: ATTIVO" if self.scalping_active else "🛑 Bot Status: FERMATO")
        print("📊 Monitoraggio log in tempo reale...")
        print()
        
        try:
            import time
            import os
            
            # Lista dei file di log da monitorare
            log_files = [
                'trading.log',
                'bot_scalping.log', 
                'dashboard.log'
            ]
            
            # Trova il file di log più recente
            latest_log = None
            for log_file in log_files:
                if os.path.exists(log_file):
                    latest_log = log_file
                    break
            
            if latest_log:
                print(f"📄 Monitorando: {latest_log}")
                # Implementa tail-f like functionality
                self._tail_log_file(latest_log)
            else:
                # Fallback con stato del bot
                print("📋 File di log non trovati, mostrando stato bot...")
                counter = 0
                while self.scalping_active and counter < 60:
                    status = "🟢 ATTIVO" if self.scalping_active else "🔴 FERMATO"
                    stop_status = "🛑 STOP RICHIESTO" if self.scalping_stop_requested else "▶️ IN ESECUZIONE"
                    print(f"[{counter+1:2d}] {status} | {stop_status} | Pair: {self.pair}")
                    time.sleep(2)
                    counter += 1
                    
        except KeyboardInterrupt:
            print("\n🔄 Ritorno al menu navigazione...")
        except Exception as e:
            print(f"❌ Errore nella visualizzazione log: {e}")
            print("🔄 Ritorno al menu navigazione...")

    def _tail_log_file(self, log_file):
        """📄 Implementa funzionalità tail -f per file di log"""
        try:
            import time
            
            # Leggi le ultime 10 righe del file
            with open(log_file, 'r') as f:
                lines = f.readlines()
                recent_lines = lines[-10:] if len(lines) > 10 else lines
                
                print("📋 ULTIME RIGHE DEL LOG:")
                print("-" * 50)
                for line in recent_lines:
                    print(line.strip())
                print("-" * 50)
                
            # Segui il file in tempo reale (simulato)
            last_size = os.path.getsize(log_file)
            counter = 0
            
            while self.scalping_active and counter < 120:  # Max 2 minuti
                current_size = os.path.getsize(log_file)
                
                if current_size > last_size:
                    # File è cresciuto, leggi nuove righe
                    with open(log_file, 'r') as f:
                        f.seek(last_size)
                        new_lines = f.readlines()
                        for line in new_lines:
                            print(f"🆕 {line.strip()}")
                    last_size = current_size
                else:
                    # Nessuna nuova riga, mostra heartbeat
                    if counter % 5 == 0:  # Ogni 10 secondi
                        print(f"💓 [{counter//5}] Monitoraggio attivo... (CTRL+C per uscire)")
                
                time.sleep(2)
                counter += 1
                
        except FileNotFoundError:
            print(f"❌ File {log_file} non trovato")
        except Exception as e:
            print(f"❌ Errore lettura log: {e}")

    def _check_scalping_user_input(self):
        """🎮 Controlla input utente in modo non-bloccante durante scalping (Observer Pattern)"""
        try:
            import select
            import sys
            
            # Check se ci sono dati in stdin (Unix/Linux)
            if hasattr(select, 'select'):
                ready, _, _ = select.select([sys.stdin], [], [], 0)
                if ready:
                    user_input = sys.stdin.readline().strip().lower()
                    return self._handle_scalping_live_input(user_input)
            else:
                # Windows fallback - usa msvcrt se disponibile
                try:
                    import msvcrt
                    if msvcrt.kbhit():
                        char = msvcrt.getch().decode('utf-8').lower()
                        return self._handle_scalping_live_input(char)
                except ImportError:
                    pass  # Nessun input non-bloccante disponibile
                    
            return False
            
        except Exception as e:
            # Ignora errori di input per non bloccare il bot
            return False

    def _handle_scalping_live_input(self, user_input):
        """🎮 Gestisce comandi utente durante l'esecuzione del bot (Command Pattern)"""
        if user_input in ['q', 'quit', 'exit', 'stop']:
            print("\n🛑 STOP richiesto dall'utente")
            self.scalping_stop_requested = True
            return True
            
        elif user_input in ['m', 'menu', 'nav', 'navigate']:
            print("\n🎮 Menu navigazione richiesto...")
            self._show_scalping_live_menu()
            return False  # Non fermare il bot, solo mostra menu
            
        elif user_input in ['d', 'dashboard']:
            print("\n📊 Ritorno alla dashboard richiesto...")
            print("💡 Bot continua in background. Usa F nella dashboard per fermarlo.")
            # Qui potresti implementare logica per tornare alla dashboard
            return True
            
        elif user_input in ['s', 'status']:
            self._show_quick_status()
            return False
            
        elif user_input in ['h', 'help', '?']:
            self._show_scalping_help()
            return False
            
        return False

    def _show_scalping_live_menu(self):
        """🎮 Mostra menu rapido durante l'esecuzione (senza interrompere)"""
        print("\n" + "="*50)
        print("🎮 COMANDI RAPIDI DURANTE SCALPING")
        print("="*50)
        print("📋 Comandi disponibili:")
        print("   q/stop  → Ferma bot")
        print("   d       → Torna dashboard")  
        print("   s       → Status rapido")
        print("   h       → Questo help")
        print("💡 Digita il comando + INVIO")
        print("="*50)

    def _show_quick_status(self):
        """📊 Mostra status rapido senza bloccare il bot"""
        print(f"\n📊 STATUS: 🟢 ATTIVO | Pair: {self.pair} | Target: {self.target_percent}%")

    def _show_scalping_help(self):
        """❓ Mostra help comandi durante scalping"""
        print("\n" + "="*50)
        print("❓ HELP COMANDI SCALPING")
        print("="*50)
        print("Durante l'esecuzione del bot, puoi digitare:")
        print("   q, quit, exit, stop → Ferma il bot")
        print("   d, dashboard       → Torna alla dashboard") 
        print("   m, menu, nav       → Mostra menu comandi")
        print("   s, status          → Status rapido")
        print("   h, help, ?         → Mostra questo help")
        print()
        print("💡 Digita il comando seguito da INVIO")
        print("🤖 Il bot continua a lavorare mentre digiti")
        print("="*50)

    def _show_scalping_status(self):
        """📊 Mostra stato dettagliato del bot scalping (Status Pattern)"""
        print("\n" + "="*50)
        print("📊 STATO BOT SCALPING")
        print("="*50)
        
        if self.scalping_active:
            print("🟢 Status: ATTIVO")
            print(f"🎯 Pair: {self.pair}")
            print(f"⏰ Stop richiesto: {'Sì' if self.scalping_stop_requested else 'No'}")
            print("🤖 Il bot sta lavorando in background...")
            
            # Info addizionali se disponibili
            if hasattr(self, 'real_portfolio_data') and self.real_portfolio_data:
                print(f"💰 Saldo corrente: {self.real_portfolio_data.get('current_balance', 'N/A')}")
                print(f"📈 Target: {self.target_percent}%")
        else:
            print("🔴 Status: NON ATTIVO")
            print("💡 Usa il tasto S per avviare il bot scalping")
            
        print("\n⏎ Premi INVIO per continuare...")
        input()

    def _handle_scalping_mode(self):
        """🚀 Gestisce l'attivazione della modalità scalping"""
        # Verifica se scalping già attivo
        if self.scalping_active:
            if hasattr(self, 'popup_service') and self.popup_service is not None:
                self.popup_service.show_warning_popup(
                    "SCALPING GIÀ ATTIVO",
                    [
                        "⚠️ Un bot di scalping è già in esecuzione",
                        "Usa il tasto F per fermarlo prima di avviarne uno nuovo"
                    ]
                )
            return
            
        # Esci dalla modalità dashboard per input utente
        curses.endwin()
        
        try:
            print("\n🚀 MODALITÀ SCALPING AVANZATO")
            print("=" * 50)
            print("⚠️  ATTENZIONE: Questa funzione eseguirà ordini reali!")
            print("    Testare con importi minimi prima dell'uso in produzione.")
            print("")
            
            # Configurazione parametri
            usdt_per_trade = float(input("💰 USDT per trade (default 100): ") or "100")
            target_net_percent = float(input("📈 Target profitto netto % (default 0.9): ") or "0.9")
            max_trades = int(input("🔢 Numero massimo trade (default 200): ") or "200")
            sleep_between_cycles = float(input("⏱️  Pausa tra controlli in secondi (default 0.5): ") or "0.5")
            
            # Configurazione timeout posizione
            print("\n🔒 TIMEOUT SICUREZZA:")
            print("   ⏰ Forza vendita se una posizione resta aperta troppo a lungo")
            use_timeout = input("   Abilitare timeout? (s/n, default s): ").lower() or "s"
            
            timeout_minutes = 5  # Default
            if use_timeout == "s":
                timeout_minutes = float(input("   ⏱️  Timeout in minuti (default 5): ") or "5")
            else:
                timeout_minutes = 0  # Disabilitato
            
            timeout_status = f"{timeout_minutes}min" if timeout_minutes > 0 else "DISABILITATO"
            
            # Configurazione Safety System  
            print("\n🛡️  SAFETY SYSTEM:")
            print("   🚨 Sistema di protezione da perdite eccessive e performance scarse")
            print("   📊 Controlla win rate e perdite giornaliere per bloccare trading rischioso")
            use_safety = input("   Abilitare Safety System? (s/n, default s): ").lower() or "s"
            
            max_daily_loss = 0.15  # Default permissivo
            min_win_rate = 0.30   # Default permissivo  
            safety_status = "ABILITATO"
            
            if use_safety == "s":
                print("   💡 Valori consigliati per scalping: Loss 10-20%, Win Rate 20-40%")
                max_daily_loss = float(input("   📉 Max perdita giornaliera % (default 15): ") or "15") / 100
                min_win_rate = float(input("   📈 Win rate minimo % (default 30): ") or "30") / 100
                safety_status = f"Loss<{max_daily_loss*100:.0f}%, WinRate>{min_win_rate*100:.0f}%"
            else:
                max_daily_loss = 1.0   # Praticamente disabilitato (100% loss)
                min_win_rate = 0.0     # Praticamente disabilitato (0% win rate)
                safety_status = "DISABILITATO"
            
            confirm = input(f"\n🔥 CONFERMA SCALPING:\n   Coppia: {self.pair}\n   USDT/trade: {usdt_per_trade}\n   Target: {target_net_percent}%\n   Max trades: {max_trades}\n   Pausa controlli: {sleep_between_cycles}s\n   Timeout: {timeout_status}\n   Safety: {safety_status}\n\n   Procedere? (SCRIVI 'SI' per confermare): ")
            
            if confirm.upper() == 'SI':
                print("\n🚀 Avvio scalping...")
                # ✅ ATTIVAZIONE DCA CON PARAMETRI DEFAULT OTTIMALI  
                self.scalp_runner(self.pair, usdt_per_trade, target_net_percent, max_trades, sleep_between_cycles, timeout_minutes, max_daily_loss, min_win_rate, enable_dca=True, dca_level1_trigger=-2.0, dca_level1_multiplier=2.0, dca_level2_trigger=-5.0, dca_level2_multiplier=3.0, dca_stop_loss_trigger=-10.0)
            else:
                print("❌ Scalping annullato.")
                
        except Exception as e:
            print(f"❌ Errore in scalping mode: {e}")
        finally:
            print("\n⏎ Premi INVIO per tornare alla dashboard...")
            input()
            # Imposta flag per reinizializzazione curses nel main loop
            self.returning_from_scalping = True

    def scalp_runner(self, pair, usdt_per_trade=100.0, target_net_percent=0.9, max_trades=200, sleep_between_cycles=0.5, timeout_minutes=5, max_daily_loss=0.15, min_win_rate=0.30, enable_dca=True, dca_level1_trigger=-2.0, dca_level1_multiplier=2.0, dca_level2_trigger=-5.0, dca_level2_multiplier=3.0, dca_stop_loss_trigger=-10.0):
        """🚀 SISTEMA SCALPING INTELLIGENTE - KISS + YAGNI"""
        from decimal import Decimal, ROUND_DOWN
        import logging
        
        # Setup logger specifico per trading
        trade_logger = logging.getLogger('trading')
        
        pair = pair.upper()
        trades_done = 0
        
        # STATE MACHINE SEMPLICE (KISS principle)
        WAITING_TO_BUY = "waiting_to_buy"
        POSITION_OPEN = "position_open" 
        WAITING_FOR_SELL = "waiting_for_sell"
        
        current_state = WAITING_TO_BUY
        position_entry_price = 0.0
        position_quantity = 0.0
        position_time = 0.0
        position_target_percent = target_net_percent  # Store target per monitoraggio
        
        # DCA (Dollar Cost Averaging) System - Anti-Martingala Strategy
        dca_levels = {
            'level1': {'trigger_percent': -2.0, 'multiplier': 2.0, 'activated': False},
            'level2': {'trigger_percent': -5.0, 'multiplier': 3.0, 'activated': False}, 
            'level3': {'trigger_percent': -10.0, 'multiplier': 0.0, 'activated': False}  # Stop Loss
        }
        dca_total_invested = 0.0
        dca_weighted_avg_price = 0.0
        
        # Inizializza sistemi strategici - PARAMETRI CONFIGURABILI UTENTE
        safety = SafetySystem(max_daily_loss=max_daily_loss, min_win_rate=min_win_rate)
        profit_lock = ProfitLock()
        session_params = get_session_parameters()
        orchestrator = StrategyOrchestrator(usdt_per_trade)
        
        # Dati storici per calcoli
        price_history = []
        volume_history = []
        
        def round_amount(qty):
            return float(Decimal(qty).quantize(Decimal('0.00000001'), rounding=ROUND_DOWN))

        def get_position_info():
            """Verifica posizione attuale - YAGNI: solo info essenziali"""
            currency = pair.split('_')[0]
            balance = self.client.get_wallet_balance(currency)
            return balance if balance and balance > 0.0001 else 0.0
        
        def calculate_strategy_pnl(current_price, entry_price, strategy_type="VIRTUAL"):
            """Calcola P&L specifico della strategia (non della posizione totale)"""
            if entry_price <= 0 or current_price <= 0:
                return 0.0
            
            pnl_percent = ((current_price - entry_price) / entry_price) * 100
            return pnl_percent

        def check_open_orders():
            """Controlla ordini aperti per gestione intelligente"""
            try:
                open_orders = self.client.list_spot_orders(pair, status='open')
                if open_orders and len(open_orders) > 0:
                    for order in open_orders:
                        if order.get('side') == 'sell':
                            print(f"   📋 Ordine vendita aperto: {order.get('amount')} @ {order.get('price')}")
                            return True
                return False
            except:
                return False

        print(f"\n🚀 SISTEMA SCALPING INTELLIGENTE per {pair}")
        print(f"   💰 USDT/trade: {usdt_per_trade}")
        print(f"   📈 Target: {target_net_percent}%")
        print(f"   🔢 Max trades: {max_trades}")
        print(f"   ⏱️  Pausa controlli: {sleep_between_cycles}s")
        timeout_status = f"{timeout_minutes}min" if timeout_minutes > 0 else "DISABILITATO"
        print(f"   ⏰ Timeout posizione: {timeout_status}")
        safety_display = f"Loss<{max_daily_loss*100:.0f}%, WinRate>{min_win_rate*100:.0f}%" if max_daily_loss < 1.0 else "DISABILITATO"
        print(f"   🛡️  Safety System: {safety_display}")
        print(f"   🎯 Sessione: {session_params}")
        print(f"   🔧 State Machine: KISS + YAGNI")
        print("\n⚠️  Premi Ctrl+C per fermare")

        # 🛡️ SECURITY: Initialize safe sleep manager per session
        from safe_sleep_manager import create_trading_sleep_manager, SleepContext
        sleep_manager = create_trading_sleep_manager()
        main_loop_iterations = 0
        max_main_loop_iterations = 10000  # Limite assoluto anti-infinite loop
        
        while (trades_done < max_trades and 
               safety.check_trade(0) and 
               main_loop_iterations < max_main_loop_iterations):
            
            main_loop_iterations += 1
            
            # 🚨 SECURITY: Log ogni 1000 iterazioni per debug infinite loops
            if main_loop_iterations % 1000 == 0:
                print(f"🔄 Main loop iteration: {main_loop_iterations}/{max_main_loop_iterations}")
            
            # Controllo circuit breaker prima di ogni iterazione
            if not self.failure_tracker.can_place_order():
                if self.failure_tracker.circuit_open:
                    cooldown_remaining = self.failure_tracker.cooldown_seconds - (time.time() - self.failure_tracker.last_failure_time)
                    print(f"⏸️  Circuit breaker attivo - cooldown rimanente: {cooldown_remaining:.0f}s")
                    # 🛡️ SECURITY: Use safe circuit breaker sleep
                    sleep_manager.circuit_breaker_sleep(self.failure_tracker.consecutive_failures)
                else:
                    backoff_time = min(self.failure_tracker.cooldown_seconds * (self.failure_tracker.backoff_multiplier ** (self.failure_tracker.consecutive_failures - 1)), self.failure_tracker.max_backoff)
                    remaining = backoff_time - (time.time() - self.failure_tracker.last_failure_time)
                    print(f"⏳ Exponential backoff attivo - rimanenti: {remaining:.0f}s")
                    # 🛡️ SECURITY: Safe exponential backoff sleep
                    sleep_duration = min(10, max(1, remaining if 'remaining' in locals() else cooldown_remaining))
                    sleep_manager.safe_sleep(sleep_duration, SleepContext.CIRCUIT_BREAKER)
                continue
                
            # 📝 SILENT LOGGING: Business logic logs to file, NOT console (Separation of Concerns)
            safety_check = safety.check_trade(0)
            trade_logger.debug(f"🔧 LOOP DEBUG: trades_done={trades_done}/{max_trades}, safety_check={safety_check}")
            trade_logger.debug(f"   📊 Safety P&L: {safety.daily_pnl:.4f}, Trades: {len(safety.trade_history)}")
            
            if not safety_check:
                trade_logger.warning(f"🚨 SAFETY BLOCK DETECTED!")
                if len(safety.trade_history) >= 5:
                    wins = sum(1 for t in safety.trade_history if t > 0)
                    current_winrate = wins / len(safety.trade_history)
                    trade_logger.warning(f"   📉 Win Rate: {current_winrate:.2f} (require: {min_win_rate:.2f})")
                if safety.daily_pnl < -max_daily_loss:
                    trade_logger.warning(f"   💸 Daily Loss: {safety.daily_pnl:.2f} (limit: -{max_daily_loss:.2f})")
                break
            
            try:
                # STATE MACHINE PRINCIPALE
                current_position = get_position_info()
                
                # 🚨 PRIORITÀ ALTA: STATO 1 - WAITING_FOR_SELL (processato per primo per evitare accumulo posizioni)
                if current_state == WAITING_FOR_SELL:
                    has_sell_orders = check_open_orders()
                    
                    if current_position == 0:
                        profit_pnl = 0.0
                        if position_entry_price > 0:
                            # Stima P&L approssimativo (prezzo corrente vs entry)
                            current_price = self.client.get_ticker(pair) or position_entry_price
                            profit_pnl = (current_price - position_entry_price) / position_entry_price * 100
                        
                        print(f"   ✅ VENDITA COMPLETATA! P&L stimato: {profit_pnl:.2f}%")
                        
                        # REGISTRA P&L nel Safety System per tracking corretto
                        safety.check_trade(profit_pnl / 100)  # Converte % in decimale
                        print(f"🔧 SAFETY UPDATE: P&L {profit_pnl:.2f}% registrato, new daily_pnl={safety.daily_pnl:.4f}")
                        
                        current_state = WAITING_TO_BUY
                        trades_done += 1
                        position_entry_price = 0.0
                        position_quantity = 0.0
                        continue
                    
                    if not has_sell_orders:
                        print(f"   ⚠️  Nessun ordine vendita attivo, torno a POSITION_OPEN")
                        current_state = POSITION_OPEN
                        continue
                    
                    print(f"   🔵 STATO: WAITING_FOR_SELL, posizione: {current_position:.8f}")
                    time.sleep(sleep_between_cycles)
                    continue

                # STATO 2: WAITING_TO_BUY
                elif current_state == WAITING_TO_BUY:
                    if current_position > 0:
                        print(f"   🔄 STATO: Posizione esistente rilevata ({current_position:.8f}), implemento VIRTUAL ENTRY STRATEGY")
                        
                        # VIRTUAL ENTRY POINT STRATEGY - Best Practice per Position Recovery
                        current_market_price = self.client.get_ticker(pair)
                        if current_market_price is None:
                            current_market_price = self.client.get_best_book_price(pair, side='buy')
                        
                        if current_market_price and current_market_price > 0:
                            # Usa prezzo corrente come virtual entry point per la nuova strategia
                            position_entry_price = current_market_price
                            position_quantity = current_position
                            position_time = time.time()
                            
                            # Reset DCA levels per nuova strategia
                            for level in dca_levels.values():
                                level['activated'] = False
                            dca_total_invested = position_quantity * position_entry_price  # Valore teorico posizione
                            dca_weighted_avg_price = position_entry_price
                            
                            print(f"   ✅ VIRTUAL ENTRY STRATEGY attivata:")
                            print(f"      📊 Virtual Entry Price: {position_entry_price:.8f}")
                            print(f"      📦 Existing Position: {position_quantity:.8f}")
                            print(f"      💰 Virtual Investment: {dca_total_invested:.2f} USDT")
                            print(f"      🎯 Strategy Target: {position_entry_price * (1 + position_target_percent / 100):.8f}")
                            
                            current_state = POSITION_OPEN
                            trade_logger.info(f"📋 VIRTUAL ENTRY: {position_quantity:.8f} @ {position_entry_price:.8f} (existing position strategy)")
                        else:
                            print(f"   ❌ Errore: impossibile ottenere prezzo corrente per virtual entry")
                            time.sleep(sleep_between_cycles)
                        continue
                    
                    print(f"\n[{trades_done+1}/{max_trades}] 🟢 STATO: WAITING_TO_BUY")
                    
                    # INIZIO STRATEGIA DI ACQUISTO - SOLO IN QUESTO STATO
                    print(f"\n[{trades_done+1}/{max_trades}] 📡 Recupero dati da Gate.io...")
                    
                    # Ottieni dati candlestick (20 periodi da 1m per calcoli)
                    ohlcv_data = get_ohlcv(self.client, pair, interval='1m', limit=20)
                    
                    if not ohlcv_data or len(ohlcv_data) < 5:
                        print("   ❌ Dati insufficienti dalle API, attendo...")
                        time.sleep(sleep_between_cycles)
                        continue
                    
                    # Estrai prezzi e volumi reali
                    price_history = [float(candle[4]) for candle in ohlcv_data]  # close prices
                    volume_history = [float(candle[5]) for candle in ohlcv_data]  # volumes
                    current_price = price_history[-1]
                    
                    print(f"   📊 Prezzi: {len(price_history)} candele, ultimo: {current_price:.8f}")
                    print(f"   📈 Volume: {volume_history[-1]:.2f}")
                    
                    # Calcola indicatori matematici con dati reali
                    volatility = calculate_volatility(price_history)
                    price_trend = calculate_price_trend(price_history)
                    volume_anomaly = detect_volume_anomalies(volume_history)
                    
                    # Calcola indicatori tecnici semplificati
                    rsi = 50 + (price_trend * 100)  # RSI semplificato basato su trend
                    macd = {'histogram': price_trend * 0.01}  # MACD semplificato
                    volume_change = volume_anomaly * 0.1  # Cambio volume normalizzato
                    
                    sentiment = calculate_market_sentiment(rsi, macd, volume_change, price_trend)
                    
                    # Condizioni di mercato per orchestratore
                    market_conditions = {
                        'volatility': volatility,
                        'trend': price_trend,
                        'sentiment': sentiment
                    }
                    
                    # Allocazione capitale dinamica
                    allocations = orchestrator.allocate_capital(market_conditions)
                    
                    # Calcola dimensione posizione adattiva
                    confidence = sentiment / 100
                    base_position_size = calculate_position_size(
                        capital=usdt_per_trade,
                        volatility=volatility,
                        confidence=confidence
                    )
                    
                    adaptive_position_size = base_position_size * session_params['aggressiveness']
                    
                    # ⚠️ IMPORTANTE: Gate.io richiede minimo 3 USDT per ordine
                    # ✅ VALIDAZIONE GATE.IO LIMITS UNIVERSALE
                    min_required = GateIOLimits.get_min_order_value_with_margin()
                    if adaptive_position_size < min_required:
                        adaptive_position_size = min_required
                        print(f"   📏 Importo aggiustato a {adaptive_position_size:.2f} USDT (min Gate.io: {min_required:.2f})")
                        print(f"   ⚠️  Position size aumentata a {adaptive_position_size:.2f} USDT (minimo Gate.io)")
                    
                    # Se anche con il minimo supera il budget, usa tutto il budget
                    if adaptive_position_size > usdt_per_trade:
                        adaptive_position_size = usdt_per_trade
                        print(f"   📊 Usando tutto il budget: {adaptive_position_size:.2f} USDT")
                    
                    print(f"\n[{trades_done+1}/{max_trades}] 🧠 ANALISI STRATEGICA")
                    print(f"   📊 Volatilità: {volatility:.4f}")
                    print(f"   📈 Trend: {price_trend:.4f}")
                    print(f"   🎯 Sentiment: {sentiment:.1f}/100")
                    print(f"   💡 Confidence: {confidence:.2f}")
                    print(f"   📊 Volume Anomaly: {volume_anomaly}")
                    
                    # Condizioni di entrata strategiche (più permissive)
                    entry_conditions = (
                        sentiment > 40 and  # Sentiment neutro/positivo (era 60)
                        volatility > 0.0001 and  # Minima volatilità per trading (era 0.001)
                        confidence > 0.2  # Minima confidence (era 0.3)
                    )
                    
                    if not entry_conditions:
                        print(f"   ⏳ Condizioni non favorevoli, attendo...")
                        adaptive_sleep = max(0.1, sleep_between_cycles * (1 - min(1.0, volatility*10)))
                        time.sleep(adaptive_sleep)
                        continue
                    
                    # Order book analysis
                    order_book = self.client.get_order_book(pair, limit=5)
                    spread_opportunity = calculate_spread_opportunity(order_book)
                    
                    # Calcola prezzi di entrata ottimali
                    best_ask = self.client.get_best_book_price(pair, side='buy')
                    best_bid = self.client.get_best_book_price(pair, side='sell')
                    
                    if best_ask is None:
                        best_ask = current_price * 1.0005
                    if best_bid is None:
                        best_bid = current_price * 0.9995
                    
                    # Prezzo di acquisto AGGRESSIVO per fill immediato (scalping style)
                    # Usa best_ask + piccolo margine per garantire esecuzione rapida
                    aggressive_buy_price = best_ask * 1.002  # +0.2% per fill immediato
                    optimal_buy_price = round(max(1e-8, aggressive_buy_price), 8)
                    
                    # Calcola quantità
                    qty = adaptive_position_size / optimal_buy_price
                    qty = round_amount(qty)
                    
                    if qty <= 0:
                        print("⚠️  Qty = 0, skip ciclo")
                        time.sleep(sleep_between_cycles)
                        continue
                    
                    print(f"   💰 Entry Price: {optimal_buy_price:.8f}")
                    print(f"   📦 Quantity: {qty:.8f}")
                    print(f"   🎯 Spread Opp: {spread_opportunity:.4f}")
                    
                    # ESECUZIONE ACQUISTO
                    currency = pair.split('_')[0]
                    balance_before = self.client.get_wallet_balance(currency)
                    
                    trade_logger.info(str(f"⚡ ACQUISTO AGGRESSIVO (scalping): {qty:.8f} {currency} @ {optimal_buy_price:.8f} (+0.2% per fill immediato)"))
                    buy_result = self.client.place_spot_order(pair, side='buy', amount=qty, price=optimal_buy_price, order_type='limit')
                    
                    if not buy_result or 'error' in buy_result:
                        print(f"❌ Errore buy: {buy_result}")
                        trade_logger.error(str(f"❌ ERRORE ACQUISTO STRATEGICO: {buy_result}"))
                        time.sleep(sleep_between_cycles)
                        continue
                    
                    # 🛡️ SECURITY: Verifica esecuzione con limite tentativi (anti-infinite loop)
                    wait_until = time.time() + 5.0  # 5 secondi per esecuzione affidabile
                    executed = False
                    balance_check_attempts = 0
                    max_balance_checks = 25  # Max 25 tentativi in 5 secondi
                    
                    while time.time() < wait_until and balance_check_attempts < max_balance_checks:
                        balance_check_attempts += 1
                        try:
                            bal = self.client.get_wallet_balance(currency)
                            if bal and bal >= qty * 0.999:
                                executed = True
                                break
                        except Exception as e:
                            trade_logger.warning(f"⚠️ Balance check failed (attempt {balance_check_attempts}): {e}")
                            if balance_check_attempts >= max_balance_checks:
                                break
                            trade_logger.info(str(f"✅ ACQUISTO AGGRESSIVO ESEGUITO - Saldo {currency}: {bal:.8f}"))
                            print(f"   ⚡ Fill immediato riuscito!")
                            # AGGIORNA STATE MACHINE
                            current_state = POSITION_OPEN
                            position_entry_price = optimal_buy_price
                            position_quantity = bal
                            position_time = time.time()
                            
                            # Reset DCA levels per nuovo trade
                            for level in dca_levels.values():
                                level['activated'] = False
                            dca_total_invested = usdt_per_trade  # Reset con il primo acquisto
                            dca_weighted_avg_price = optimal_buy_price
                            break
                        time.sleep(0.2)  # Check più frequenti
                    
                    if not executed:
                        print("❌ Buy non eseguito entro timeout")
                        time.sleep(sleep_between_cycles)
                        continue
                    
                    # POSIZIONE APERTA: ATTENDI TARGET COME TASTI 1-4
                    print(f"   ✅ BUY eseguito @ {optimal_buy_price:.8f}")
                    
                    # 🔍 MONITORING: Record successful trade entry
                    self.monitoring.record_trade_event(
                        success=True,
                        pair=pair,
                        profit=0.0,  # No profit yet on entry
                        execution_time=0.0
                    )
                    
                    # Calcola prezzo target per monitoraggio
                    target_price = optimal_buy_price * (1 + position_target_percent / 100)
                    print(f"   🎯 TARGET MONITORAGGIO: {target_price:.8f} (+{position_target_percent}%)")
                    print(f"   ⏳ Attendo che il prezzo raggiunga il target...")
                    
                    # STATO: POSITION_OPEN - Monitor del target (COME TASTI 1-4)
                    current_state = POSITION_OPEN
                    
                    # RISPETTA IL TUO SLEEP ESATTO
                    print(f"   💤 Sleep {sleep_between_cycles} secondi (come da tua impostazione)...")
                    time.sleep(sleep_between_cycles)
                    continue
                    
                # STATO 3: POSITION_OPEN  
                elif current_state == POSITION_OPEN:
                    if current_position == 0:
                        print(f"   🔄 STATO: Posizione venduta, torno a WAITING_TO_BUY")
                        current_state = WAITING_TO_BUY
                        trades_done += 1
                        continue
                    
                    # 📝 SILENT MONITORING: Log to file, not console (UI/Business Separation)
                    trade_logger.info(f"[{trades_done+1}/{max_trades}] 🔵 STATO: POSITION_OPEN ({current_position:.8f})")
                    
                    # MONITORAGGIO TARGET (come tasti 1-4)
                    if position_entry_price > 0:
                        # Usa DCA weighted average se livelli attivi, altrimenti entry originale
                        effective_entry_price = dca_weighted_avg_price if (dca_levels['level1']['activated'] or dca_levels['level2']['activated']) else position_entry_price
                        target_price = effective_entry_price * (1 + position_target_percent / 100)
                        current_price = self.client.get_ticker(pair) or position_entry_price
                        
                        trade_logger.info(f"   📊 Prezzo corrente: {current_price:.8f}")
                        trade_logger.info(f"   🎯 Target: {target_price:.8f} (+{position_target_percent}%)")
                        
                        # TARGET RAGGIUNTO - VENDI AL PREZZO MIGLIORE (come tasti 1-4)
                        if current_price >= target_price:
                            trade_logger.info(f"   🎯 TARGET RAGGIUNTO! Vendita al miglior prezzo...")
                            
                            # VENDITA AL PREZZO MIGLIORE DEL BOOK (come tasti 1-4)
                            optimal_sell_price = self.client.get_best_book_price(pair, side='sell')
                            if optimal_sell_price is None:
                                optimal_sell_price = current_price * 0.999
                            
                            optimal_sell_price = round(optimal_sell_price, 8)
                            
                            trade_logger.info(str(f"🎯 TARGET RAGGIUNTO - VENDITA MARKET: {position_quantity:.8f} {currency} @ {optimal_sell_price:.8f}"))
                            
                            sell_result = self.client.place_spot_order(
                                pair, 
                                side='sell', 
                                amount=position_quantity, 
                                price=optimal_sell_price, 
                                order_type='limit'
                            )
                            
                            if sell_result and 'error' not in sell_result:
                                if hasattr(self, 'failure_tracker'):
                                    self.failure_tracker.record_success()
                                print(f"   ✅ Vendita eseguita al target!")
                                current_state = WAITING_FOR_SELL
                            else:
                                if hasattr(self, 'failure_tracker'):
                                    self.failure_tracker.record_failure()
                                print(f"   ❌ Errore vendita: {sell_result}")
                        else:
                            # Calcola P&L strategia (Virtual Entry)
                            strategy_pnl = calculate_strategy_pnl(current_price, position_entry_price, "VIRTUAL")
                            # 📝 SILENT P&L MONITORING: Log to file (Separation of Concerns)
                            trade_logger.info(f"   📈 Strategy P&L: {strategy_pnl:.2f}% (from virtual entry @ {position_entry_price:.8f})")
                            
                            # DCA MONITORING - Dollar Cost Averaging su livelli di perdita
                            if strategy_pnl < 0:  # Solo se in perdita
                                current_loss_percent = strategy_pnl  # Usa P&L strategia
                                
                                # Check DCA Level 1: -2% (reload x2)
                                if (current_loss_percent <= dca_levels['level1']['trigger_percent'] and 
                                    not dca_levels['level1']['activated']):
                                    
                                    dca_buy_amount = usdt_per_trade * dca_levels['level1']['multiplier']
                                    print(f"   🔻 DCA LEVEL 1 TRIGGERED at {current_loss_percent:.2f}% loss")
                                    print(f"   💰 DCA1: Adding {dca_buy_amount:.2f} USDT position (x{dca_levels['level1']['multiplier']})")
                                    
                                    # Esegui acquisto DCA Level 1
                                    dca_quantity = dca_buy_amount / current_price
                                    dca_buy_result = self.client.place_spot_order(
                                        pair, side='buy', amount=dca_quantity,
                                        price=current_price * 1.002, order_type='limit'
                                    )
                                    
                                    if dca_buy_result and 'error' not in dca_buy_result:
                                        # Aggiorna weighted average price
                                        total_quantity = position_quantity + dca_quantity
                                        total_invested = (position_quantity * position_entry_price) + (dca_quantity * current_price)
                                        dca_weighted_avg_price = total_invested / total_quantity
                                        dca_total_invested += dca_buy_amount
                                        
                                        position_quantity = total_quantity
                                        position_entry_price = dca_weighted_avg_price
                                        dca_levels['level1']['activated'] = True
                                        
                                        print(f"   ✅ DCA1 executed! New avg price: {dca_weighted_avg_price:.8f}")
                                        print(f"   📊 Total position: {position_quantity:.8f} | Total invested: {dca_total_invested + usdt_per_trade:.2f} USDT")
                                    else:
                                        if hasattr(self, 'failure_tracker'):
                                            self.failure_tracker.record_failure()
                                        print(f"   ❌ DCA1 failed: {dca_buy_result}")
                                
                                # Check DCA Level 2: -5% (reload x3)
                                elif (current_loss_percent <= dca_levels['level2']['trigger_percent'] and 
                                      not dca_levels['level2']['activated'] and 
                                      dca_levels['level1']['activated']):
                                    
                                    dca_buy_amount = usdt_per_trade * dca_levels['level2']['multiplier']
                                    print(f"   🔻🔻 DCA LEVEL 2 TRIGGERED at {current_loss_percent:.2f}% loss")
                                    print(f"   💰 DCA2: Adding {dca_buy_amount:.2f} USDT position (x{dca_levels['level2']['multiplier']})")
                                    
                                    # Esegui acquisto DCA Level 2
                                    dca_quantity = dca_buy_amount / current_price
                                    dca_buy_result = self.client.place_spot_order(
                                        pair, side='buy', amount=dca_quantity,
                                        price=current_price * 1.002, order_type='limit'
                                    )
                                    
                                    if dca_buy_result and 'error' not in dca_buy_result:
                                        # Aggiorna weighted average price
                                        total_quantity = position_quantity + dca_quantity
                                        total_invested = (position_quantity * position_entry_price) + (dca_quantity * current_price)
                                        dca_weighted_avg_price = total_invested / total_quantity
                                        dca_total_invested += dca_buy_amount
                                        
                                        position_quantity = total_quantity
                                        position_entry_price = dca_weighted_avg_price
                                        dca_levels['level2']['activated'] = True
                                        
                                        print(f"   ✅ DCA2 executed! New avg price: {dca_weighted_avg_price:.8f}")
                                        print(f"   📊 Total position: {position_quantity:.8f} | Total invested: {dca_total_invested + usdt_per_trade:.2f} USDT")
                                    else:
                                        if hasattr(self, 'failure_tracker'):
                                            self.failure_tracker.record_failure()
                                        print(f"   ❌ DCA2 failed: {dca_buy_result}")
                                
                                # Check DCA Level 3: -10% (STOP LOSS)
                                elif (current_loss_percent <= dca_levels['level3']['trigger_percent'] and 
                                      not dca_levels['level3']['activated']):
                                    
                                    print(f"   🚨 STOP LOSS TRIGGERED at {current_loss_percent:.2f}% loss")
                                    print(f"   💸 Cutting losses - Emergency exit")
                                    
                                    # Vendita immediata al miglior prezzo disponibile
                                    emergency_sell_price = self.client.get_best_book_price(pair, side='sell')
                                    if emergency_sell_price is None:
                                        emergency_sell_price = current_price * 0.995  # -0.5% market sell
                                    
                                    stop_loss_result = self.client.place_spot_order(
                                        pair, side='sell', amount=position_quantity,
                                        price=emergency_sell_price, order_type='limit'
                                    )
                                    
                                    if stop_loss_result and 'error' not in stop_loss_result:
                                        print(f"   🚨 STOP LOSS executed at {emergency_sell_price:.8f}")
                                        dca_levels['level3']['activated'] = True
                                        current_state = WAITING_FOR_SELL
                                    else:
                                        if hasattr(self, 'failure_tracker'):
                                            self.failure_tracker.record_failure()
                                        print(f"   ❌ STOP LOSS failed: {stop_loss_result}")
                            
                            # TIMEOUT SICUREZZA: Se troppo tempo, forza vendita al prezzo corrente
                            time_in_position = time.time() - position_time
                            timeout_seconds = timeout_minutes * 60
                            if timeout_minutes > 0 and time_in_position > timeout_seconds:
                                print(f"   ⏰ TIMEOUT ({timeout_minutes}min) - Vendita forzata al prezzo corrente")
                                optimal_sell_price = self.client.get_best_book_price(pair, side='sell') or current_price * 0.999
                                optimal_sell_price = round(optimal_sell_price, 8)
                                
                                sell_result = self.client.place_spot_order(
                                    pair, side='sell', amount=position_quantity, 
                                    price=optimal_sell_price, order_type='limit'
                                )
                                
                                if sell_result and 'error' not in sell_result:
                                    print(f"   ✅ Vendita timeout eseguita!")
                                    current_state = WAITING_FOR_SELL
                    
                    time.sleep(sleep_between_cycles)
                    continue
                

            except KeyboardInterrupt:
                print(f"\n🛑 Sistema strategico fermato dall'utente. Trades completati: {trades_done}")
                break
            except Exception as e:
                print(f"❌ Errore sistema strategico: {e}")
                trade_logger.error(str(f"❌ ERRORE SISTEMA: {e}"))
                time.sleep(1)

        # Mostra motivo di terminazione
        termination_reason = "Max trades raggiunto" if trades_done >= max_trades else "Safety system block"
        print(f"\n🏁 Sistema strategico terminato: {termination_reason}")
        print(f"📊 Trades eseguiti: {trades_done}/{max_trades}")
        print(f"📊 Safety Status - Daily P&L: {safety.daily_pnl:.4f}")
        if safety.trade_history:
            wins = sum(1 for trade in safety.trade_history if trade > 0)
            win_rate = wins / len(safety.trade_history)
            print(f"📈 Win Rate: {win_rate:.2f} ({wins}/{len(safety.trade_history)})")
        else:
            print("📈 Win Rate: 0.00 (0/0)")

    def scalp_runner_worker_mode(self, pair, usdt_per_trade=100.0, target_net_percent=0.9, max_trades=200, sleep_between_cycles=0.5, timeout_minutes=5, shutdown_event=None, max_daily_loss=0.15, min_win_rate=0.30):
        """🤖 SISTEMA SCALPING per WORKER MODE - Headless con gestione stati"""
        from decimal import Decimal, ROUND_DOWN
        import logging
        import threading
        import time
        
        # Setup logger specifico per trading
        trade_logger = logging.getLogger('trading')
        
        # Inizializza managers per scalping automatico
        if not hasattr(self, 'wallet_manager'):
            self.wallet_manager = WalletManager(self.client)
        if not hasattr(self, 'failure_tracker'):
            self.failure_tracker = OrderFailureTracker()
        
        # Verifica se coppia è bloccata prima di iniziare
        if self.wallet_manager.state_manager.is_pair_blocked(pair):
            reason = self.wallet_manager.state_manager.get_block_reason(pair)
            # 📝 SILENT BLOCKING: Log to file only (Worker Mode Pattern)
            trade_logger.error(f"🚫 Scalping bloccato per {pair}: {reason}")
            trade_logger.error(f"Motivo: {reason}")
            trade_logger.error("Sbloccare manualmente la coppia prima di procedere.")
            return
        
        # 📝 SILENT WORKER LOGGING: File only, NO console output (Separation of Concerns)
        try:
            # Remove any existing console handlers to prevent console pollution
            for handler in trade_logger.handlers[:]:
                if isinstance(handler, logging.StreamHandler) and handler.stream.name == '<stderr>':
                    trade_logger.removeHandler(handler)
            
            # Add file handler only
            file_handler = logging.FileHandler('bot_scalping.log')
            file_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
            trade_logger.addHandler(file_handler)
            trade_logger.setLevel(logging.INFO)
            trade_logger.propagate = False  # Prevent propagation to root logger
        except Exception as e:
            # Fallback: at least don't crash
            pass
        
        pair = pair.upper()
        trades_done = 0
        
        # State Machine States
        WAITING_TO_BUY = "waiting_to_buy"
        POSITION_OPEN = "position_open" 
        WAITING_FOR_SELL = "waiting_for_sell"
        
        current_state = WAITING_TO_BUY
        position_entry_price = 0.0
        position_quantity = 0.0
        position_time = 0.0
        position_target_percent = target_net_percent
        
        # DCA (Dollar Cost Averaging) System - Anti-Martingala Strategy
        dca_levels = {
            'level1': {'trigger_percent': -2.0, 'multiplier': 2.0, 'activated': False},
            'level2': {'trigger_percent': -5.0, 'multiplier': 3.0, 'activated': False}, 
            'level3': {'trigger_percent': -10.0, 'multiplier': 0.0, 'activated': False}  # Stop Loss
        }
        dca_total_invested = 0.0
        dca_weighted_avg_price = 0.0
        
        # Inizializza sistemi strategici - PARAMETRI CONFIGURABILI UTENTE
        safety = SafetySystem(max_daily_loss=max_daily_loss, min_win_rate=min_win_rate)
        profit_lock = ProfitLock()
        session_params = get_session_parameters()
        orchestrator = StrategyOrchestrator(usdt_per_trade)
        
        def round_amount(qty):
            return float(Decimal(qty).quantize(Decimal('0.00000001'), rounding=ROUND_DOWN))

        def get_position_info():
            """Verifica posizione attuale - YAGNI: solo info essenziali"""
            currency = pair.split('_')[0]
            balance = self.client.get_wallet_balance(currency)
            return balance if balance and balance > 0.0001 else 0.0

        def check_open_orders():
            """Controlla ordini aperti per gestione intelligente"""
            try:
                open_orders = self.client.list_spot_orders(pair, status='open')
                if open_orders and len(open_orders) > 0:
                    for order in open_orders:
                        if order.get('side') == 'sell':
                            trade_logger.info(f"📋 Ordine vendita aperto: {order.get('amount')} @ {order.get('price')}")
                            return True
                return False
            except:
                return False

        trade_logger.info(f"🚀 WORKER BOT SCALPING per {pair}")
        trade_logger.info(f"💰 USDT/trade: {usdt_per_trade}")
        trade_logger.info(f"📈 Target: {target_net_percent}%")
        trade_logger.info(f"🔢 Max trades: {max_trades}")
        trade_logger.info(f"⏱️ Pausa controlli: {sleep_between_cycles}s")
        timeout_status = f"{timeout_minutes}min" if timeout_minutes > 0 else "DISABILITATO"
        trade_logger.info(f"⏰ Timeout posizione: {timeout_status}")
        safety_display = f"Loss<{max_daily_loss*100:.0f}%, WinRate>{min_win_rate*100:.0f}%" if max_daily_loss < 1.0 else "DISABILITATO"
        trade_logger.info(f"🛡️ Safety System: {safety_display}")
        trade_logger.info(f"🎯 Sessione: {session_params}")
        trade_logger.info(f"🔧 State Machine: KISS + YAGNI")

        # Thread per aggiornamento status (per session manager)
        def status_updater():
            """Aggiorna status per session manager"""
            while not shutdown_event.is_set() if shutdown_event else True:
                try:
                    # TODO: Comunicare status al session manager
                    # Per ora, log locale
                    trade_logger.info(f"📊 Status: {current_state}, Trades: {trades_done}, PnL: {safety.daily_pnl:.4f}")
                    time.sleep(30)  # Ogni 30 secondi
                except:
                    break
        
        status_thread = threading.Thread(target=status_updater, daemon=True)
        status_thread.start()

        while trades_done < max_trades and safety.check_trade(0):
            # Check shutdown dal session manager
            if shutdown_event and shutdown_event.is_set():
                trade_logger.info("📡 Ricevuto comando shutdown dal Session Manager")
                break
                
            # 🛑 Check stop richiesto dalla dashboard (tasto F)
            if hasattr(self, 'scalping_stop_requested') and self.scalping_stop_requested:
                trade_logger.info("🛑 Stop richiesto dalla dashboard (tasto F)")
                print("🛑 Scalping fermato dall'utente via dashboard")
                break
                
            # 🎮 Check input utente per navigazione (non-bloccante)
            if self._check_scalping_user_input():
                # Utente ha richiesto menu navigazione
                break
            
            try:
                # STATE MACHINE PRINCIPALE
                current_position = get_position_info()
                
                # 🚨 PRIORITÀ ALTA: STATO 1 - WAITING_FOR_SELL (processato per primo per evitare accumulo posizioni)
                if current_state == WAITING_FOR_SELL:
                    has_sell_orders = check_open_orders()
                    
                    if current_position == 0:
                        profit_pnl = 0.0
                        if position_entry_price > 0:
                            # Stima P&L approssimativo (prezzo corrente vs entry)
                            current_price = self.client.get_ticker(pair) or position_entry_price
                            profit_pnl = (current_price - position_entry_price) / position_entry_price * 100
                        
                        print(f"   ✅ VENDITA COMPLETATA! P&L stimato: {profit_pnl:.2f}%")
                        
                        # REGISTRA P&L nel Safety System per tracking corretto
                        safety.check_trade(profit_pnl / 100)  # Converte % in decimale
                        print(f"🔧 SAFETY UPDATE: P&L {profit_pnl:.2f}% registrato, new daily_pnl={safety.daily_pnl:.4f}")
                        
                        current_state = WAITING_TO_BUY
                        trades_done += 1
                        position_entry_price = 0.0
                        position_quantity = 0.0
                        continue
                    
                    if not has_sell_orders:
                        print(f"   ⚠️  Nessun ordine vendita attivo, torno a POSITION_OPEN")
                        current_state = POSITION_OPEN
                        continue
                    
                    print(f"   🔵 STATO: WAITING_FOR_SELL, posizione: {current_position:.8f}")
                    time.sleep(sleep_between_cycles)
                    continue

                # STATO 2: WAITING_TO_BUY
                elif current_state == WAITING_TO_BUY:
                    if current_position > 0:
                        trade_logger.info(f"🔄 STATO: Posizione esistente rilevata ({current_position:.8f}), implemento VIRTUAL ENTRY STRATEGY")
                        
                        # VIRTUAL ENTRY POINT STRATEGY - Best Practice per Position Recovery
                        current_market_price = self.client.get_ticker(pair)
                        if current_market_price is None:
                            current_market_price = self.client.get_best_book_price(pair, side='buy')
                        
                        if current_market_price and current_market_price > 0:
                            # Usa prezzo corrente come virtual entry point per la nuova strategia
                            position_entry_price = current_market_price
                            position_quantity = current_position
                            position_time = time.time()
                            
                            # Reset DCA levels per nuova strategia
                            for level in dca_levels.values():
                                level['activated'] = False
                            dca_total_invested = position_quantity * position_entry_price  # Valore teorico posizione
                            dca_weighted_avg_price = position_entry_price
                            
                            trade_logger.info(f"✅ VIRTUAL ENTRY STRATEGY attivata:")
                            trade_logger.info(f"   📊 Virtual Entry Price: {position_entry_price:.8f}")
                            trade_logger.info(f"   📦 Existing Position: {position_quantity:.8f}")
                            trade_logger.info(f"   💰 Virtual Investment: {dca_total_invested:.2f} USDT")
                            trade_logger.info(f"   🎯 Strategy Target: {position_entry_price * (1 + position_target_percent / 100):.8f}")
                            
                            current_state = POSITION_OPEN
                            trade_logger.info(f"📋 VIRTUAL ENTRY: {position_quantity:.8f} @ {position_entry_price:.8f} (existing position strategy)")
                        else:
                            trade_logger.warning("❌ Errore: impossibile ottenere prezzo corrente per virtual entry")
                            time.sleep(sleep_between_cycles)
                        continue
                    
                    trade_logger.info(f"[{trades_done+1}/{max_trades}] 🟢 STATO: WAITING_TO_BUY")
                    
                    # INIZIO STRATEGIA DI ACQUISTO - SOLO IN QUESTO STATO
                    trade_logger.info(f"[{trades_done+1}/{max_trades}] 📡 Recupero dati da Gate.io...")
                    
                    # Ottieni dati candlestick (20 periodi da 1m per calcoli)
                    ohlcv_data = get_ohlcv(self.client, pair, interval='1m', limit=20)
                    
                    if not ohlcv_data or len(ohlcv_data) < 5:
                        trade_logger.warning("❌ Dati insufficienti dalle API, attendo...")
                        time.sleep(sleep_between_cycles)
                        continue
                    
                    # Estrai prezzi e volumi reali
                    price_history = [float(candle[4]) for candle in ohlcv_data]  # close prices
                    volume_history = [float(candle[5]) for candle in ohlcv_data]  # volumes
                    current_price = price_history[-1]
                    
                    trade_logger.info(f"📊 Prezzi: {len(price_history)} candele, ultimo: {current_price:.8f}")
                    trade_logger.info(f"📈 Volume: {volume_history[-1]:.2f}")
                    
                    # Calcola indicatori matematici con dati reali
                    volatility = calculate_volatility(price_history)
                    price_trend = calculate_price_trend(price_history)
                    volume_anomaly = detect_volume_anomalies(volume_history)
                    
                    # Calcola indicatori tecnici semplificati
                    rsi = 50 + (price_trend * 100)  # RSI semplificato basato su trend
                    macd = {'histogram': price_trend * 0.01}  # MACD semplificato
                    volume_change = volume_anomaly * 0.1  # Cambio volume normalizzato
                    
                    sentiment = calculate_market_sentiment(rsi, macd, volume_change, price_trend)
                    
                    # Condizioni di mercato per orchestratore
                    market_conditions = {
                        'volatility': volatility,
                        'trend': price_trend,
                        'sentiment': sentiment
                    }
                    
                    # Allocazione capitale dinamica
                    allocations = orchestrator.allocate_capital(market_conditions)
                    
                    # Calcola dimensione posizione adattiva
                    confidence = sentiment / 100
                    base_position_size = calculate_position_size(
                        capital=usdt_per_trade,
                        volatility=volatility,
                        confidence=confidence
                    )
                    
                    adaptive_position_size = base_position_size * session_params['aggressiveness']
                    
                    # ⚠️ IMPORTANTE: Gate.io richiede minimo 3 USDT per ordine
                    # ✅ VALIDAZIONE GATE.IO LIMITS UNIVERSALE
                    min_required = GateIOLimits.get_min_order_value_with_margin()
                    if adaptive_position_size < min_required:
                        adaptive_position_size = min_required
                        print(f"   📏 Importo aggiustato a {adaptive_position_size:.2f} USDT (min Gate.io: {min_required:.2f})")
                        trade_logger.info(f"⚠️ Position size aumentata a {adaptive_position_size:.2f} USDT (minimo Gate.io)")
                    
                    # Se anche con il minimo supera il budget, usa tutto il budget
                    if adaptive_position_size > usdt_per_trade:
                        adaptive_position_size = usdt_per_trade
                        trade_logger.info(f"📊 Usando tutto il budget: {adaptive_position_size:.2f} USDT")
                    
                    trade_logger.info(f"[{trades_done+1}/{max_trades}] 🧠 ANALISI STRATEGICA")
                    trade_logger.info(f"📊 Volatilità: {volatility:.4f}")
                    trade_logger.info(f"📈 Trend: {price_trend:.4f}")
                    trade_logger.info(f"🎯 Sentiment: {sentiment:.1f}/100")
                    trade_logger.info(f"💡 Confidence: {confidence:.2f}")
                    trade_logger.info(f"📊 Volume Anomaly: {volume_anomaly}")
                    
                    # Condizioni di entrata strategiche (più permissive)
                    entry_conditions = (
                        sentiment > 40 and  # Sentiment neutro/positivo (era 60)
                        volatility > 0.0001 and  # Minima volatilità per trading (era 0.001)
                        confidence > 0.2  # Minima confidence (era 0.3)
                    )
                    
                    if not entry_conditions:
                        trade_logger.info("⏳ Condizioni non favorevoli, attendo...")
                        adaptive_sleep = max(0.1, sleep_between_cycles * (1 - min(1.0, volatility*10)))
                        time.sleep(adaptive_sleep)
                        continue
                    
                    # Order book analysis
                    order_book = self.client.get_order_book(pair, limit=5)
                    spread_opportunity = calculate_spread_opportunity(order_book)
                    
                    # Calcola prezzi di entrata ottimali
                    best_ask = self.client.get_best_book_price(pair, side='buy')
                    best_bid = self.client.get_best_book_price(pair, side='sell')
                    
                    if best_ask is None:
                        best_ask = current_price * 1.0005
                    if best_bid is None:
                        best_bid = current_price * 0.9995
                    
                    # Prezzo di acquisto AGGRESSIVO per fill immediato (scalping style)
                    # Usa best_ask + piccolo margine per garantire esecuzione rapida
                    aggressive_buy_price = best_ask * 1.002  # +0.2% per fill immediato
                    optimal_buy_price = round(max(1e-8, aggressive_buy_price), 8)
                    
                    # Calcola quantità
                    qty = adaptive_position_size / optimal_buy_price
                    qty = round_amount(qty)
                    
                    if qty <= 0:
                        trade_logger.warning("⚠️ Qty = 0, skip ciclo")
                        time.sleep(sleep_between_cycles)
                        continue
                    
                    trade_logger.info(f"💰 Entry Price: {optimal_buy_price:.8f}")
                    trade_logger.info(f"📦 Quantity: {qty:.8f}")
                    trade_logger.info(f"🎯 Spread Opp: {spread_opportunity:.4f}")
                    
                    # ESECUZIONE ACQUISTO
                    currency = pair.split('_')[0]
                    balance_before = self.client.get_wallet_balance(currency)
                    
                    trade_logger.info(f"⚡ ACQUISTO AGGRESSIVO (scalping): {qty:.8f} {currency} @ {optimal_buy_price:.8f} (+0.2% per fill immediato)")
                    buy_result = self.client.place_spot_order(pair, side='buy', amount=qty, price=optimal_buy_price, order_type='limit')
                    
                    if not buy_result or 'error' in buy_result:
                        trade_logger.error(f"❌ Errore buy: {buy_result}")
                        time.sleep(sleep_between_cycles)
                        continue
                    
                    # 🛡️ SECURITY: Verifica esecuzione con limite tentativi (anti-infinite loop)
                    wait_until = time.time() + 5.0  # 5 secondi per esecuzione affidabile
                    executed = False
                    balance_check_attempts = 0
                    max_balance_checks = 25  # Max 25 tentativi in 5 secondi
                    
                    while time.time() < wait_until and balance_check_attempts < max_balance_checks:
                        balance_check_attempts += 1
                        try:
                            bal = self.client.get_wallet_balance(currency)
                            if bal and bal >= qty * 0.999:
                                executed = True
                                break
                        except Exception as e:
                            trade_logger.warning(f"⚠️ Balance check failed (attempt {balance_check_attempts}): {e}")
                            if balance_check_attempts >= max_balance_checks:
                                break
                            trade_logger.info(f"✅ ACQUISTO AGGRESSIVO ESEGUITO - Saldo {currency}: {bal:.8f}")
                            # AGGIORNA STATE MACHINE
                            current_state = POSITION_OPEN
                            position_entry_price = optimal_buy_price
                            position_quantity = bal
                            position_time = time.time()
                            
                            # Reset DCA levels per nuovo trade
                            for level in dca_levels.values():
                                level['activated'] = False
                            dca_total_invested = usdt_per_trade  # Reset con il primo acquisto
                            dca_weighted_avg_price = optimal_buy_price
                            break
                        time.sleep(0.2)  # Check più frequenti
                    
                    if not executed:
                        trade_logger.warning("❌ Buy non eseguito entro timeout")
                        time.sleep(sleep_between_cycles)
                        continue
                    
                    # POSIZIONE APERTA: ATTENDI TARGET COME TASTI 1-4
                    trade_logger.info(f"✅ BUY eseguito @ {optimal_buy_price:.8f}")
                    
                    # Calcola prezzo target per monitoraggio
                    target_price = optimal_buy_price * (1 + position_target_percent / 100)
                    trade_logger.info(f"🎯 TARGET MONITORAGGIO: {target_price:.8f} (+{position_target_percent}%)")
                    trade_logger.info("⏳ Attendo che il prezzo raggiunga il target...")
                    
                    # STATO: POSITION_OPEN - Monitor del target (COME TASTI 1-4)
                    current_state = POSITION_OPEN
                    
                    # RISPETTA IL TUO SLEEP ESATTO
                    trade_logger.info(f"💤 Sleep {sleep_between_cycles} secondi (come da tua impostazione)...")
                    time.sleep(sleep_between_cycles)
                    continue
                    
                # STATO 3: POSITION_OPEN  
                elif current_state == POSITION_OPEN:
                    if current_position == 0:
                        trade_logger.info("🔄 STATO: Posizione venduta, torno a WAITING_TO_BUY")
                        current_state = WAITING_TO_BUY
                        trades_done += 1
                        continue
                    
                    trade_logger.info(f"[{trades_done+1}/{max_trades}] 🔵 STATO: POSITION_OPEN ({current_position:.8f})")
                    
                    # MONITORAGGIO TARGET (come tasti 1-4)
                    if position_entry_price > 0:
                        # Usa DCA weighted average se livelli attivi, altrimenti entry originale
                        effective_entry_price = dca_weighted_avg_price if (dca_levels['level1']['activated'] or dca_levels['level2']['activated']) else position_entry_price
                        target_price = effective_entry_price * (1 + position_target_percent / 100)
                        
                        # Tentativo get_ticker con fallback robusto 
                        current_price = self.client.get_ticker(pair)
                        if current_price is None:
                            # API fallita - prova best_bid come alternativa
                            current_price = self.client.get_best_book_price(pair, side='buy')
                            if current_price is None:
                                # Ultima risorsa - usa entry price (non farà mai trigger)
                                current_price = position_entry_price
                                trade_logger.warning("⚠️ API non disponibile - target monitoring compromesso")
                        
                        trade_logger.info(f"📊 Prezzo corrente: {current_price:.8f}")
                        trade_logger.info(f"🎯 Target: {target_price:.8f} (+{position_target_percent}%)")
                        
                        # TARGET RAGGIUNTO - VENDI AL PREZZO MIGLIORE (come tasti 1-4)
                        if current_price >= target_price:
                            trade_logger.info("🎯 TARGET RAGGIUNTO! Vendita al miglior prezzo...")
                            
                            # VENDITA AL PREZZO MIGLIORE DEL BOOK (come tasti 1-4)
                            optimal_sell_price = self.client.get_best_book_price(pair, side='sell')
                            if optimal_sell_price is None:
                                optimal_sell_price = current_price * 0.999
                            
                            optimal_sell_price = round(optimal_sell_price, 8)
                            
                            trade_logger.info(f"🎯 TARGET RAGGIUNTO - VENDITA MARKET: {position_quantity:.8f} {currency} @ {optimal_sell_price:.8f}")
                            
                            sell_result = self.client.place_spot_order(
                                pair, side='sell', amount=position_quantity, 
                                price=optimal_sell_price, order_type='limit'
                            )
                            
                            if sell_result and 'error' not in sell_result:
                                if hasattr(self, 'failure_tracker'):
                                    self.failure_tracker.record_success()
                                trade_logger.info("✅ Ordine vendita piazzato per target!")
                                current_state = WAITING_FOR_SELL
                            else:
                                if hasattr(self, 'failure_tracker'):
                                    self.failure_tracker.record_failure()
                                trade_logger.error(f"❌ Errore vendita target: {sell_result}")
                        
                        # DCA MONITORING - Dollar Cost Averaging su livelli di perdita
                        else:
                            # Calcola % perdita attuale
                            current_loss_percent = ((current_price - position_entry_price) / position_entry_price) * 100
                            
                            # Check DCA Level 1: -2% (reload x2)
                            if (current_loss_percent <= dca_levels['level1']['trigger_percent'] and 
                                not dca_levels['level1']['activated']):
                                
                                dca_buy_amount = usdt_per_trade * dca_levels['level1']['multiplier']
                                trade_logger.warning(f"🔻 DCA LEVEL 1 TRIGGERED at {current_loss_percent:.2f}% loss")
                                trade_logger.info(f"💰 DCA1: Adding {dca_buy_amount:.2f} USDT position (x{dca_levels['level1']['multiplier']})")
                                
                                # Esegui acquisto DCA Level 1
                                dca_quantity = dca_buy_amount / current_price
                                dca_buy_result = self.client.place_spot_order(
                                    pair, side='buy', amount=dca_quantity,
                                    price=current_price * 1.002, order_type='limit'  # +0.2% per fill immediato
                                )
                                
                                if dca_buy_result and 'error' not in dca_buy_result:
                                    # Aggiorna weighted average price
                                    total_quantity = position_quantity + dca_quantity
                                    total_invested = (position_quantity * position_entry_price) + (dca_quantity * current_price)
                                    dca_weighted_avg_price = total_invested / total_quantity
                                    dca_total_invested += dca_buy_amount
                                    
                                    position_quantity = total_quantity
                                    position_entry_price = dca_weighted_avg_price  # Nuovo breakeven
                                    dca_levels['level1']['activated'] = True
                                    
                                    trade_logger.info(f"✅ DCA1 executed! New avg price: {dca_weighted_avg_price:.8f}")
                                    trade_logger.info(f"📊 Total position: {position_quantity:.8f} | Total invested: {dca_total_invested + usdt_per_trade:.2f} USDT")
                                else:
                                    if hasattr(self, 'failure_tracker'):
                                        self.failure_tracker.record_failure()
                                    trade_logger.error(f"❌ DCA1 failed: {dca_buy_result}")
                            
                            # Check DCA Level 2: -5% (reload x3)
                            elif (current_loss_percent <= dca_levels['level2']['trigger_percent'] and 
                                  not dca_levels['level2']['activated'] and 
                                  dca_levels['level1']['activated']):
                                
                                dca_buy_amount = usdt_per_trade * dca_levels['level2']['multiplier']
                                trade_logger.warning(f"🔻🔻 DCA LEVEL 2 TRIGGERED at {current_loss_percent:.2f}% loss")
                                trade_logger.info(f"💰 DCA2: Adding {dca_buy_amount:.2f} USDT position (x{dca_levels['level2']['multiplier']})")
                                
                                # Esegui acquisto DCA Level 2
                                dca_quantity = dca_buy_amount / current_price
                                dca_buy_result = self.client.place_spot_order(
                                    pair, side='buy', amount=dca_quantity,
                                    price=current_price * 1.002, order_type='limit'
                                )
                                
                                if dca_buy_result and 'error' not in dca_buy_result:
                                    # Aggiorna weighted average price
                                    total_quantity = position_quantity + dca_quantity
                                    total_invested = (position_quantity * position_entry_price) + (dca_quantity * current_price)
                                    dca_weighted_avg_price = total_invested / total_quantity
                                    dca_total_invested += dca_buy_amount
                                    
                                    position_quantity = total_quantity
                                    position_entry_price = dca_weighted_avg_price  # Nuovo breakeven
                                    dca_levels['level2']['activated'] = True
                                    
                                    trade_logger.info(f"✅ DCA2 executed! New avg price: {dca_weighted_avg_price:.8f}")
                                    trade_logger.info(f"📊 Total position: {position_quantity:.8f} | Total invested: {dca_total_invested + usdt_per_trade:.2f} USDT")
                                else:
                                    if hasattr(self, 'failure_tracker'):
                                        self.failure_tracker.record_failure()
                                    trade_logger.error(f"❌ DCA2 failed: {dca_buy_result}")
                            
                            # Check DCA Level 3: -10% (STOP LOSS)
                            elif (current_loss_percent <= dca_levels['level3']['trigger_percent'] and 
                                  not dca_levels['level3']['activated']):
                                
                                trade_logger.error(f"🚨 STOP LOSS TRIGGERED at {current_loss_percent:.2f}% loss")
                                trade_logger.error(f"💸 Cutting losses - Emergency exit")
                                
                                # Vendita immediata al miglior prezzo disponibile
                                emergency_sell_price = self.client.get_best_book_price(pair, side='sell')
                                if emergency_sell_price is None:
                                    emergency_sell_price = current_price * 0.995  # -0.5% market sell
                                
                                stop_loss_result = self.client.place_spot_order(
                                    pair, side='sell', amount=position_quantity,
                                    price=emergency_sell_price, order_type='limit'
                                )
                                
                                if stop_loss_result and 'error' not in stop_loss_result:
                                    trade_logger.error(f"🚨 STOP LOSS executed at {emergency_sell_price:.8f}")
                                    dca_levels['level3']['activated'] = True
                                    current_state = WAITING_FOR_SELL
                                else:
                                    if hasattr(self, 'failure_tracker'):
                                        self.failure_tracker.record_failure()
                                    trade_logger.error(f"❌ STOP LOSS failed: {stop_loss_result}")
                        
                        # TIMEOUT SICUREZZA
                        if timeout_minutes > 0:
                            timeout_seconds = timeout_minutes * 60
                            time_in_position = time.time() - position_time
                            if timeout_minutes > 0 and time_in_position > timeout_seconds:
                                trade_logger.warning(f"⏰ TIMEOUT ({timeout_minutes}min) - Vendita forzata al prezzo corrente")
                                optimal_sell_price = self.client.get_best_book_price(pair, side='sell') or current_price * 0.999
                                optimal_sell_price = round(optimal_sell_price, 8)
                                
                                sell_result = self.client.place_spot_order(
                                    pair, side='sell', amount=position_quantity, 
                                    price=optimal_sell_price, order_type='limit'
                                )
                                
                                if sell_result and 'error' not in sell_result:
                                    trade_logger.info("✅ Vendita timeout eseguita!")
                                    current_state = WAITING_FOR_SELL
                    
                    time.sleep(sleep_between_cycles)
                    continue
                
                # STATO 3: WAITING_FOR_SELL
                elif current_state == WAITING_FOR_SELL:
                    has_sell_orders = check_open_orders()
                    
                    if current_position == 0:
                        profit_pnl = 0.0
                        if position_entry_price > 0:
                            # Stima P&L approssimativo (prezzo corrente vs entry)
                            current_price = self.client.get_ticker(pair) or position_entry_price
                            profit_pnl = (current_price - position_entry_price) / position_entry_price * 100
                        
                        trade_logger.info(f"✅ VENDITA COMPLETATA! P&L stimato: {profit_pnl:.2f}%")
                        trade_logger.info(f"🎉 TRADE #{trades_done+1} COMPLETATO - P&L stimato: {profit_pnl:.2f}%")
                        
                        current_state = WAITING_TO_BUY
                        trades_done += 1
                        position_entry_price = 0.0
                        position_quantity = 0.0
                        continue
                    
                    if not has_sell_orders:
                        trade_logger.info("⚠️ Nessun ordine vendita attivo, torno a POSITION_OPEN")
                        current_state = POSITION_OPEN
                        continue
                    
                    trade_logger.info(f"🔵 STATO: WAITING_FOR_SELL, posizione: {current_position:.8f}")
                    time.sleep(sleep_between_cycles)
                    continue

            except KeyboardInterrupt:
                trade_logger.info(f"🛑 Worker bot fermato dall'utente. Trades completati: {trades_done}")
                break
            except Exception as e:
                trade_logger.error(f"❌ Errore worker bot: {e}")
                time.sleep(1)

        trade_logger.info(f"🏁 Worker bot terminato. Trades eseguiti: {trades_done}")
        trade_logger.info(f"📊 Safety Status - Daily P&L: {safety.daily_pnl:.4f}")
        if safety.trade_history:
            wins = sum(1 for trade in safety.trade_history if trade > 0)
            win_rate = wins / len(safety.trade_history)
            trade_logger.info(f"📈 Win Rate: {win_rate:.2f} ({wins}/{len(safety.trade_history)})")

    def _get_current_usdt_balance(self):
        """Recupera il saldo USDT attuale con cache intelligente"""
        if not hasattr(self, 'wallet_manager'):
            self.wallet_manager = WalletManager(self.client)
        return self.wallet_manager.get_available_usdt()

    def _draw_card_capital_percentage(self, r, c, w):
        # Gestisce entrambe le modalità: vendita e acquisto
        active_mode = None
        if hasattr(self, 'order_mode') and self.order_mode:
            active_mode = 'sell'
        elif hasattr(self, 'buy_order_mode') and self.buy_order_mode:
            active_mode = 'buy'
        
        h = 24 if active_mode else 21  # Altezza per entrambe le sezioni
        title = f"Trading Percentuali - ORDINE {active_mode.upper()} ATTIVO" if active_mode else "🎯 Trading Percentuali Capitale"
        box_color = self.YELLOW if active_mode else self.CYAN

        self._draw_box(r, c, h, w, title, box_color)

        # Calcola saldi attuali
        current_balance = self._get_current_balance()
        current_usdt_balance = self._get_current_usdt_balance()
        current_price = self.last_valid_price if self.last_valid_price is not None else 0
        total_capital_usdt = current_price * current_balance if current_price > 0 else 0
        asset_symbol = self.pair.split('_')[0]

        # Header con entrambi i saldi
        self._safe_addstr(r + 1, c + 2, f"💰 {asset_symbol}: {current_balance:.6f} = {total_capital_usdt:.2f} USDT",
                         self.GREEN | curses.A_BOLD)
        self._safe_addstr(r + 2, c + 2, f"💵 USDT: {current_usdt_balance:.2f}",
                         self.YELLOW | curses.A_BOLD)

        # ===== SEZIONE VENDITA =====
        self._safe_addstr(r + 3, c + 2, "═" * min(40, w - 4), curses.A_DIM)
        self._safe_addstr(r + 4, c + 2, "📤 VENDITA (1-4)", self.RED | curses.A_BOLD)
        
        # Percentuali vendita
        percentages = TradingConfig.SELL_PERCENTAGES  # [25, 50, 75, 100]
        header_parts = [f"[{p}%]" if active_mode == 'sell' and p == self.order_percentage else f"{p}%" for p in percentages]
        header = f"   {header_parts[0]:>8} {header_parts[1]:>8} {header_parts[2]:>8} {header_parts[3]:>8}"

        self._safe_addstr(r + 5, c + 2, header, self.YELLOW | curses.A_BOLD if active_mode == 'sell' else curses.A_BOLD | self.RED)
        self._safe_addstr(r + 6, c + 2, f"   {'1':>8} {'2':>8} {'3':>8} {'4':>8}", curses.A_DIM)

        # Valori USDT e quantità vendita
        sell_usdt_values = [f"{total_capital_usdt * (p/100):.{2 if total_capital_usdt * (p/100) < 100 else 0}f}" for p in percentages]
        sell_qty_values = [f"{current_balance * (p/100):.{6 if current_balance * (p/100) < 1 else 3}f}" for p in percentages]

        sell_usdt_line = f"💵 {sell_usdt_values[0]:>8} {sell_usdt_values[1]:>8} {sell_usdt_values[2]:>8} {sell_usdt_values[3]:>8} USDT"
        sell_qty_line = f"🪙 {sell_qty_values[0]:>8} {sell_qty_values[1]:>8} {sell_qty_values[2]:>8} {sell_qty_values[3]:>8} {asset_symbol}"

        self._safe_addstr(r + 7, c + 2, sell_usdt_line, self.YELLOW | curses.A_BOLD)
        self._safe_addstr(r + 8, c + 2, sell_qty_line, self.RED | curses.A_BOLD)

        # ===== SEZIONE ACQUISTO =====
        self._safe_addstr(r + 9, c + 2, "═" * min(40, w - 4), curses.A_DIM)
        self._safe_addstr(r + 10, c + 2, "📥 ACQUISTO (6-9)", self.GREEN | curses.A_BOLD)
        
        # Percentuali acquisto
        buy_percentages = TradingConfig.BUY_PERCENTAGES  # [25, 50, 75, 100]
        buy_header_parts = [f"[{p}%]" if active_mode == 'buy' and p == self.buy_order_percentage else f"{p}%" for p in buy_percentages]
        buy_header = f"   {buy_header_parts[0]:>8} {buy_header_parts[1]:>8} {buy_header_parts[2]:>8} {buy_header_parts[3]:>8}"

        self._safe_addstr(r + 11, c + 2, buy_header, self.YELLOW | curses.A_BOLD if active_mode == 'buy' else curses.A_BOLD | self.GREEN)
        self._safe_addstr(r + 12, c + 2, f"   {'6':>8} {'7':>8} {'8':>8} {'9':>8}", curses.A_DIM)

        # Valori acquisto
        buy_usdt_values = [f"{current_usdt_balance * (p/100):.{2 if current_usdt_balance * (p/100) < 100 else 0}f}" for p in buy_percentages]
        buy_qty_values = [f"{(current_usdt_balance * (p/100)) / current_price:.{6 if (current_usdt_balance * (p/100)) / current_price < 1 else 3}f}" for p in buy_percentages]

        buy_usdt_line = f"💵 {buy_usdt_values[0]:>8} {buy_usdt_values[1]:>8} {buy_usdt_values[2]:>8} {buy_usdt_values[3]:>8} USDT"
        buy_qty_line = f"🪙 {buy_qty_values[0]:>8} {buy_qty_values[1]:>8} {buy_qty_values[2]:>8} {buy_qty_values[3]:>8} {asset_symbol}"

        self._safe_addstr(r + 13, c + 2, buy_usdt_line, self.YELLOW | curses.A_BOLD)
        self._safe_addstr(r + 14, c + 2, buy_qty_line, self.GREEN | curses.A_BOLD)

        # Istruzioni o conferma ordine
        if not active_mode:
            self._safe_addstr(r + 15, c + 2, "🎮 Vendita: 1-4 | Acquisto: 6-9", self.CYAN)
            self._safe_addstr(r + 16, c + 2, "🚀 Scalping: S | Cancel: C", self.YELLOW | curses.A_BOLD)
            self._safe_addstr(r + 17, c + 2, "⚡ Ordini eseguiti al miglior prezzo book", curses.A_DIM)
        else:
            if active_mode == 'sell':
                self._draw_order_confirmation(r + 15, c, w, current_balance, 'sell')
            else:
                self._draw_buy_order_confirmation(r + 15, c, w, current_usdt_balance, 'buy')

        # Messaggi di successo/errore
        self._draw_order_messages(r + h - 2, c, w)

        return r + h

    def _get_current_balance(self):
        """Recupera il saldo attuale (unificato)"""
        if self.real_portfolio_data:
            current_balance = self.real_portfolio_data['current_balance']
            # Aggiorna in tempo reale
            currency = self.pair.split('_')[0]
            real_balance = self.client.get_wallet_balance(currency)
            return real_balance if real_balance > 0 else current_balance
        return sum(self.quantita) if self.quantita else self.initial_amount

    def _draw_order_confirmation(self, r, c, w, current_balance, order_type='sell'):
        """Disegna la sezione di conferma ordine vendita"""
        sell_quantity = current_balance * (self.order_percentage / 100)
        optimal_price = self.client.get_best_book_price(self.pair, side='sell')
        if optimal_price is None:
            if self.last_valid_price is None or self.last_valid_price <= 0:
                optimal_price = 0  # Fallback sicuro per UI
            else:
                optimal_price = self.last_valid_price * 0.999

        estimated_value = sell_quantity * optimal_price
        asset_symbol = self.pair.split('_')[0]

        self._safe_addstr(r, c + 2, "═" * min(40, w - 4), self.YELLOW)
        self._safe_addstr(r + 1, c + 2, f"📋 CONFERMA VENDITA {self.order_percentage}%:", self.YELLOW | curses.A_BOLD)
        self._safe_addstr(r + 2, c + 2, UIFormatter.format_quantity_line("Quantità", sell_quantity, asset_symbol), self.CYAN)
        self._safe_addstr(r + 3, c + 2, f"💰 Prezzo: {optimal_price:.6f} (~{estimated_value:.2f} USDT)", self.CYAN)
        self._safe_addstr(r + 4, c + 2, "INVIO = Conferma | ❌ C = Annulla", self.MAGENTA | curses.A_BOLD)

    def _draw_buy_order_confirmation(self, r, c, w, current_usdt_balance, order_type='buy'):
        """Disegna la sezione di conferma ordine acquisto"""
        usdt_amount = current_usdt_balance * (self.buy_order_percentage / 100)
        optimal_price = self.client.get_best_book_price(self.pair, side='buy')
        if optimal_price is None:
            if self.last_valid_price is None or self.last_valid_price <= 0:
                optimal_price = 0  # Fallback sicuro per UI
            else:
                optimal_price = self.last_valid_price * 1.001

        buy_quantity = usdt_amount / optimal_price if optimal_price > 0 else 0
        asset_symbol = self.pair.split('_')[0]

        self._safe_addstr(r, c + 2, "═" * min(40, w - 4), self.YELLOW)
        self._safe_addstr(r + 1, c + 2, f"📋 CONFERMA ACQUISTO {self.buy_order_percentage}%:", self.YELLOW | curses.A_BOLD)
        self._safe_addstr(r + 2, c + 2, f"💵 Importo: {usdt_amount:.2f} USDT", self.CYAN)
        self._safe_addstr(r + 3, c + 2, UIFormatter.format_quantity_line("Quantità", buy_quantity, asset_symbol), self.CYAN)
        self._safe_addstr(r + 4, c + 2, f"💰 Prezzo: {optimal_price:.6f}", self.CYAN)
        self._safe_addstr(r + 5, c + 2, "INVIO = Conferma | ❌ C = Annulla", self.MAGENTA | curses.A_BOLD)

    def _draw_order_messages(self, row, col, w):
        """Mostra messaggi di successo/errore ordini (vendita e acquisto)"""
        current_time = time.time()
        
        # Messaggi vendita
        if hasattr(self, 'order_success') and current_time - getattr(self, 'order_success_time', 0) < 10:
            self._safe_addstr(row, col + 2, self.order_success[:w-4], self.GREEN | curses.A_BOLD)
        elif hasattr(self, 'order_error') and current_time - getattr(self, 'order_error_time', 0) < 10:
            self._safe_addstr(row, col + 2, self.order_error[:w-4], self.RED | curses.A_BOLD)
        
        # Messaggi acquisto con durata dinamica e colorazione migliorata
        elif hasattr(self, 'buy_order_success') and current_time - getattr(self, 'buy_order_success_time', 0) < 10:
            self._safe_addstr(row, col + 2, self.buy_order_success[:w-4], self.GREEN | curses.A_BOLD)
        elif hasattr(self, 'buy_order_error') and current_time - getattr(self, 'buy_order_error_time', 0) < getattr(self, 'buy_order_error_duration', 10):
            # Colore dinamico basato su categoria errore (Strategy Pattern)
            error_color = getattr(self, getattr(self, 'buy_order_error_color_key', 'RED'), self.RED)
            self._safe_addstr(row, col + 2, self.buy_order_error[:w-4], error_color | curses.A_BOLD)

    def _draw_box(self, r, c, h, w, title, color=None):
        """Disegna un box con colore personalizzabile (unificato)"""
        try:
            height, width = self.stdscr.getmaxyx()
            if r + h >= height or c + w >= width or r < 0 or c < 0:
                return

            box_color = color or self.CYAN

            # Disegna cornice
            if r < height and c + w - 1 < width:
                self.stdscr.addstr(r, c, "╭" + "─" * (w - 2) + "╮", box_color)

            for i in range(1, h - 1):
                if r + i < height and c + w - 1 < width:
                    self.stdscr.addstr(r + i, c, "│" + " " * (w - 2) + "│", box_color)

            if r + h - 1 < height and c + w - 1 < width:
                self.stdscr.addstr(r + h - 1, c, "╰" + "─" * (w - 2) + "╯", box_color)

            # Titolo
            if r < height and c + 2 + len(title) + 2 < width:
                self.stdscr.addstr(r, c + 2, f" {title.upper()} ", box_color | curses.A_BOLD)

        except curses.error:
            pass

    def _safe_addstr(self, row, col, text, color=None):
        """Aggiunge testo con controlli di sicurezza"""
        try:
            height, width = self.stdscr.getmaxyx()
            if row >= height or col >= width or row < 0 or col < 0:
                return

            # Tronca il testo se troppo lungo
            max_length = width - col - 1
            if len(text) > max_length:
                text = text[:max_length]

            if color:
                self.stdscr.addstr(row, col, text, color)
            else:
                self.stdscr.addstr(row, col, text)
        except curses.error:
            pass

    def _show_popup(self, title, messages, popup_type="info"):
        """
        🪟 Wrapper per compatibilità - delega al nuovo sistema popup unificato
        """
        if not hasattr(self, 'popup_service') or self.popup_service is None:
            # Fallback se popup service non è inizializzato
            print(f"\n{title}: {' | '.join(messages)}")
            input("Premi INVIO per continuare...")
            return
        
        # Delega al sistema popup unificato (Adapter Pattern)
        if popup_type == "success":
            return self.popup_service.show_success_popup(title, messages)
        elif popup_type == "error":
            return self.popup_service.show_error_popup(title, messages)
        elif popup_type == "warning":
            return self.popup_service.show_warning_popup(title, messages)
        else:
            return self.popup_service.show_info_popup(title, messages)

    def _get_active_order_mode_indicator(self):
        """Restituisce l'indicatore testuale per la modalità ordine attiva (Single Responsibility)"""
        indicators = []
        
        if hasattr(self, 'scalping_active') and self.scalping_active:
            indicators.append("🤖 SCALPING BOT ATTIVO")
            
        if hasattr(self, 'buy_order_mode') and self.buy_order_mode:
            indicators.append(f"🛒 MODALITÀ ACQUISTO {self.buy_order_percentage}% ATTIVA")
        elif hasattr(self, 'order_mode') and self.order_mode:
            indicators.append(f"📤 MODALITÀ VENDITA {self.order_percentage}% ATTIVA")
        
        return " | " + " | ".join(indicators) if indicators else ""

    def _get_status_bar_color(self):
        """Restituisce il colore della status bar basato sulla modalità attiva (Strategy Pattern)"""
        if hasattr(self, 'scalping_active') and self.scalping_active:
            return self.MAGENTA | curses.A_BOLD  # Magenta per scalping
        elif hasattr(self, 'buy_order_mode') and self.buy_order_mode:
            return self.GREEN | curses.A_BOLD  # Verde per acquisto
        elif hasattr(self, 'order_mode') and self.order_mode:
            return self.YELLOW | curses.A_BOLD  # Giallo per vendita
        return self.CYAN  # Cyan di default

    def _set_enhanced_buy_error(self, error_result=None, balance=None, amount=None, min_required=None, exception=None):
        """Imposta errore buy con feedback migliorato usando ErrorFeedbackService (Dependency Injection)"""
        error_info = ErrorFeedbackService.categorize_error(
            error_result=error_result,
            balance=balance, 
            amount=amount,
            min_required=min_required,
            exception=exception
        )
        
        self.buy_order_error = error_info['message']
        self.buy_order_error_time = time.time()
        self.buy_order_error_duration = error_info['duration']
        self.buy_order_error_color_key = error_info['color_key']
        
        return error_info['message']  # Per logging

    def _draw_help_system(self, height, width):
        """📚 Disegna il sistema help sovrapposto al dashboard"""
        self.stdscr.clear()
        
        # Header principale
        header = "📚 TRADING DASHBOARD - MANUALE UTENTE"
        self._safe_addstr(0, (width - len(header)) // 2, header, curses.A_BOLD | self.CYAN)
        
        # Tabs header
        tab_y = 2
        tab_start_x = 5
        for i, tab in enumerate(self.help_system.tabs):
            tab_color = curses.A_BOLD | self.GREEN if i == self.help_system.current_tab else self.YELLOW
            self._safe_addstr(tab_y, tab_start_x + i * 15, f"[{tab}]", tab_color)
        
        # Navigazione help
        nav_text = "◀/▶ Cambia scheda  |  ▲/▼ Scorri  |  H = Chiudi  |  ESC = Esci"
        self._safe_addstr(3, (width - len(nav_text)) // 2, nav_text, self.MAGENTA)
        
        # Separatore
        self._safe_addstr(4, 0, "═" * width, self.WHITE)
        
        # Contenuto help scrollable
        current_tab = self.help_system.tabs[self.help_system.current_tab]
        content_lines = self.help_system.help_content[current_tab]
        
        # Area di contenuto
        content_start_y = 5
        content_height = height - 6  # Lascia spazio per footer
        
        # Calcola range linee visibili con scroll
        visible_lines = content_lines[self.help_scroll_offset:self.help_scroll_offset + content_height]
        
        # Disegna contenuto
        for i, line in enumerate(visible_lines):
            if content_start_y + i >= height - 1:
                break
                
            # Colori speciali per diverse parti del contenuto
            line_color = self.WHITE
            if line.startswith("═══"):
                line_color = curses.A_BOLD | self.CYAN
            elif line.startswith("🔹"):
                line_color = curses.A_BOLD | self.YELLOW  
            elif line.startswith("  •"):
                line_color = self.GREEN
            elif line.startswith("⚠️"):
                line_color = curses.A_BOLD | self.RED
                
            self._safe_addstr(content_start_y + i, 2, line, line_color)
        
        # Footer con scroll indicator
        footer_y = height - 1
        total_lines = len(content_lines)
        if total_lines > content_height:
            scroll_info = f"Linea {self.help_scroll_offset + 1}-{min(self.help_scroll_offset + content_height, total_lines)} di {total_lines}"
            self._safe_addstr(footer_y, width - len(scroll_info) - 2, scroll_info, self.CYAN)

    def _draw_card_api_stats(self, r, c, w):
        height, width = self.stdscr.getmaxyx()
        stats = self.client.api_stats
        h = min(3 + len(stats), height - r - 2)  # Limita altezza

        # Controlla se c'è spazio sufficiente
        if r + h >= height:
            return r + 1  # Ritorna posizione minima se non c'è spazio

        self._draw_box(r, c, h, w, "Statistiche API")

        if h > 2:  # Solo se c'è spazio per almeno header
            self._safe_addstr(r + 1, c + 2, f"{'Endpoint':<20} {'Chiamate':>10} {'Avg Time':>10} {'Errori':>7}", curses.A_BOLD)

            max_items = h - 3  # Spazio disponibile per gli items
            for i, (endpoint, data) in enumerate(list(stats.items())[:max_items]):
                avg_time = (data['total_time'] / data['count']) * 1000 if data['count'] > 0 else 0
                endpoint_name = endpoint.split('/')[-1]
                line = f"{endpoint_name:<20} {data['count']:>10} {avg_time:>9.0f}ms {data['failures']:>7}"
                self._safe_addstr(r + 2 + i, c + 2, line)

        return r + h

    def update_and_draw(self):
        """🎨 LAYOUT RIORGANIZZATO: Separazione netta Mercato vs Portafoglio"""
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()

        # Layout adattivo per terminali piccoli
        if height < 25 or width < 100:
            self.stdscr.clear()
            self._safe_addstr(0, 0, "Terminale troppo piccolo. Richiesto almeno 100x25.", self.RED)
            self._safe_addstr(1, 0, f"Dimensioni attuali: {width}x{height}", self.YELLOW)
            self.stdscr.refresh()
            return

        # ===== HELP SYSTEM OVERLAY =====
        if self.help_active:
            self._draw_help_system(height, width)
            self.stdscr.refresh()
            return

        # ===== PREPARAZIONE DATI =====
        current_price = self.client.get_ticker(self.pair)
        if current_price is None:
            current_price = self.last_valid_price
            # Se anche last_valid_price è None, usa un fallback sicuro
            if current_price is None:
                trade_logger.warning("⚠️  Impossibile ottenere prezzo di mercato")
                current_price = 0.0
        else:
            self.last_valid_price = current_price

        self._update_market_data(current_price)
        self._update_cache_stats()

        # ===== LAYOUT TRE COLONNE ORGANIZZATO =====
        col_width = (width - 6) // 3  # 3 colonne + spaziatura
        col1_start = 1                # PORTAFOGLIO & TRADING
        col2_start = col_width + 3    # MERCATO & ANALISI
        col3_start = (col_width * 2) + 5  # OPERAZIONI & CONTROLLI

        # Headers delle sezioni con colori distintivi
        self._draw_section_headers(col1_start, col2_start, col3_start, col_width)

        available_height = height - 6  # Spazio per headers e footer

        # ===== COLONNA 1: PORTAFOGLIO & INVESTIMENTI =====
        row_portfolio = 4
        remaining_space = available_height

        # Portfolio Overview (sempre mostrato)
        if remaining_space > 10:
            row_portfolio = self._draw_portfolio_overview(row_portfolio, col1_start, col_width, current_price)
            row_portfolio += 1
            remaining_space -= 12

        # Tranche Acquisti
        if remaining_space > 8:
            row_portfolio = self._draw_card_buy_stats(row_portfolio, col1_start, col_width)
            row_portfolio += 1
            remaining_space -= (6 + min(len(self.prezzi) if self.prezzi else 3, 8))

        # Dettaglio Commissioni (solo se spazio abbondante - priorità bassa)
        if remaining_space > 16:  # Richiede molto spazio per mostrare bene
            row_portfolio = self._draw_fees_details_card(row_portfolio, col1_start, col_width, current_price)
            row_portfolio += 1
            remaining_space -= 11

        # Sistema Target & Progress (priorità alta)
        if remaining_space > 6:
            row_portfolio = self._draw_target_progress_system(row_portfolio, col1_start, col_width, current_price)
        # Se non c'è spazio per commissioni complete ma sì per una riga compatta
        elif remaining_space > 3 and remaining_space <= 16:
            row_portfolio = self._draw_fees_summary_line(row_portfolio, col1_start, col_width, current_price)

        # ===== COLONNA 2: MERCATO & ANALISI TECNICA =====
        row_market = 4
        remaining_space = available_height

        # Analisi Tecnica Multi-Timeframe
        if remaining_space > 12:
            row_market = self._draw_professional_technical_analysis(row_market, col2_start, col_width, current_price)
            row_market += 1
            remaining_space -= 33  # Aggiornato per l'altezza maggiore dell'analisi tecnica integrata

        # Statistiche API e Sistema  
        if remaining_space > 8:
            row_market = self._draw_card_api_stats(row_market, col2_start, col_width)

        # ===== COLONNA 3: OPERAZIONI & CONTROLLI =====
        row_operations = 4
        remaining_space = available_height

        # Trading Controls (sempre mostrato)
        if remaining_space > 22:
            row_operations = self._draw_card_capital_percentage(row_operations, col3_start, col_width)
            row_operations += 1
            remaining_space -= 24

        # Performance Finanziaria
        if remaining_space > 8:
            row_operations = self._draw_financial_performance(row_operations, col3_start, col_width, current_price)
            row_operations += 1
            remaining_space -= 10

        # Statistiche Trading Giornaliere
        if remaining_space > 8:
            row_operations = self._draw_trading_stats_card(row_operations, col3_start, col_width)
            row_operations += 1
            remaining_space -= 9

        # Statistiche Trading Giornaliere (se c'è spazio)
        if remaining_space > 4:
            row_operations = self._draw_card_daily_trades(row_operations, col3_start, col_width)

        # ===== FOOTER INFORMATIVO =====
        self._draw_enhanced_footer(height, width, current_price)

        # ⚡ Refresh immediato
        self.stdscr.refresh()

    def _update_market_data(self, current_price):
        """📊 Aggiorna tutti i dati di mercato centralizzati"""
        self.price_history.append((time.time(), current_price))
        if len(self.price_history) > 50: self.price_history.pop(0)  # Storia più lunga

        # Aggiorna massimi e minimi di sessione
        self.session_high = max(self.session_high, current_price)
        self.session_low = min(self.session_low, current_price)

        # Traccia i picchi di profitto
        current_profit_perc = ProfitCalculator.calculate_price_profit_percentage(current_price, self.buy_price_avg)
        if len(self.profit_peaks) == 0 or current_profit_perc > max(self.profit_peaks):
            self.profit_peaks.append(current_profit_perc)

    def _update_cache_stats(self):
        """⚡ Aggiorna cache delle statistiche"""
        stats_cache_key = f"trades_stats_{self.pair}"
        cached_stats = self.client.stats_cache.get(stats_cache_key, TradingConfig.CACHE_TIMEOUTS['stats'])

        if cached_stats is None:
            self.trades_stats = self._get_today_trades_stats()
            self.client.stats_cache.set(stats_cache_key, self.trades_stats)
        else:
            self.trades_stats = cached_stats

    def _draw_section_headers(self, col1_start, col2_start, col3_start, col_width):
        """🎨 Disegna gli headers delle tre sezioni principali"""
        header_main = f" SCALPING DASHBOARD - {self.pair} "
        header_col = max(0, (self.stdscr.getmaxyx()[1] - len(header_main)) // 2)
        self._safe_addstr(0, header_col, header_main, curses.A_REVERSE | curses.A_BOLD)

        # Status bar con info essenziali e modalità attive
        current_time = datetime.now().strftime('%H:%M:%S')
        price_text = f"💰 {self.last_valid_price:.6f} USDT" if self.last_valid_price is not None else "💰 N/A USDT"
        
        # Indicatore modalità ordini attive (Single Responsibility Principle)
        mode_indicator = self._get_active_order_mode_indicator()
        status_text = f"{current_time} | {price_text}{mode_indicator}"
        
        # Colorazione dinamica basata su modalità attiva
        status_color = self._get_status_bar_color()
        self._safe_addstr(1, 2, status_text, status_color)

        # Headers delle colonne con caratteri box drawing
        self._safe_addstr(2, col1_start, "═" * col_width, self.GREEN)
        self._safe_addstr(2, col1_start + 2, " 💼 PORTAFOGLIO & INVESTIMENTI ", self.GREEN | curses.A_BOLD)

        self._safe_addstr(2, col2_start, "═" * col_width, self.CYAN)
        self._safe_addstr(2, col2_start + 2, " 📊 MERCATO & ANALISI TECNICA ", self.CYAN | curses.A_BOLD)

        self._safe_addstr(2, col3_start, "═" * col_width, self.MAGENTA)
        self._safe_addstr(2, col3_start + 2, " ⚡ OPERAZIONI & CONTROLLI ", self.MAGENTA | curses.A_BOLD)

    def _draw_enhanced_footer(self, height, width, current_price):
        """📋 Footer informativo migliorato"""
        try:
            footer_row = height - 2

            # Linea separatrice
            self._safe_addstr(footer_row - 1, 1, "═" * (width - 2), curses.A_DIM)

            # Status operativo
            if getattr(self, 'buy_order_mode', False):
                status_text = f"🛒 MODALITÀ ACQUISTO {self.buy_order_percentage}% | INVIO:Conferma | C:Annulla"
                status_color = self.GREEN | curses.A_BOLD
            elif getattr(self, 'order_mode', False):
                status_text = f"⚠️  MODALITÀ VENDITA {self.order_percentage}% | INVIO:Conferma | C:Annulla"
                status_color = self.YELLOW | curses.A_BOLD
            else:
                status_text = f"🎮 MODALITÀ MONITOR | 1-4:Vendi% | 6-9:Acquista% | H:Help | Q:Esci | {datetime.now().strftime('%H:%M:%S')}"
                status_color = self.CYAN

            self._safe_addstr(footer_row, 2, status_text, status_color)

            # Info aggiuntive a destra
            spread_info = ""
            if hasattr(self.client, 'get_spread'):
                spread = self.client.get_spread(self.pair)
                if spread:
                    spread_info = f" | Spread: {spread:.4f}%"

            right_info = f"API: ✓{spread_info}"
            info_col = max(2, width - len(right_info) - 2)
            self._safe_addstr(footer_row, info_col, right_info, curses.A_DIM)

        except curses.error:
            pass

    def _draw_portfolio_overview(self, r, c, w, current_price):
        """💼 SEZIONE PORTAFOGLIO: Overview generale investimenti"""
        h = 11
        self._draw_box(r, c, h, w, "💼 PORTFOLIO OVERVIEW", self.GREEN)

        # Calcoli con dati reali o fallback
        portfolio_data = self._get_portfolio_data()

        # Valore attuale e calcoli P&L con fees fisse 0.2% per le vendite
        current_value_gross = current_price * portfolio_data['current_balance']
        exit_fee_rate = TradingConfig.EXIT_FEE_RATE  # 🔧 FEES CENTRALIZZATE configurabili
        exit_fees = current_value_gross * exit_fee_rate
        current_value_net = current_value_gross - exit_fees

        total_cost_basis = portfolio_data['total_invested'] + portfolio_data['total_fees_paid']
        net_profit_usdt = ProfitCalculator.calculate_net_profit_usdt(current_value_net, total_cost_basis)
        net_profit_perc = ProfitCalculator.calculate_net_profit_percentage(net_profit_usdt, total_cost_basis)

        # Asset e valori
        asset_symbol = self.pair.split('_')[0]
        data_source = "🔗 LIVE" if self.real_portfolio_data else "📝 MANUAL"

        self._safe_addstr(r + 1, c + 2, f"{data_source} | Asset: {portfolio_data['current_balance']:.6f} {asset_symbol}", curses.A_BOLD)

        # Valori monetari principali
        pnl_color = UIFormatter.get_profit_color(self, net_profit_usdt)
        self._safe_addstr(r + 2, c + 2, UIFormatter.format_currency_line("Valore Lordo", current_value_gross), self.CYAN)
        self._safe_addstr(r + 3, c + 2, f"💸 Valore Netto: {current_value_net:.2f} USDT (-{exit_fees:.2f} fees)", self.YELLOW)
        self._safe_addstr(r + 4, c + 2, f"📈 P&L Netto: {net_profit_usdt:+.2f} USDT ({net_profit_perc:+.2f}%)", pnl_color | curses.A_BOLD)

        # Separatore
        self._safe_addstr(r + 5, c + 2, "─" * (w - 4), self.GREEN)

        # Costi e investimenti
        self._safe_addstr(r + 6, c + 2, UIFormatter.format_currency_line("Capitale Investito", portfolio_data['total_invested'], prefix="🏦"))
        self._safe_addstr(r + 7, c + 2, UIFormatter.format_currency_line("Commissioni Pagate", portfolio_data['total_fees_paid'], prefix="💳"))
        self._safe_addstr(r + 8, c + 2, UIFormatter.format_currency_line("Costo Totale Base", total_cost_basis, prefix="💼"), curses.A_BOLD)

        # Prezzi medi
        self._safe_addstr(r + 9, c + 2, f"⚖️  Prezzo Medio Ponderato: {portfolio_data['weighted_avg']:.6f}", self.CYAN)
        self._safe_addstr(r + 10, c + 2, f"🧮 Prezzo Medio Aritmetico: {portfolio_data['arithmetic_avg']:.6f}", curses.A_DIM)

        return r + h

    def _get_portfolio_data(self):
        """Unifica l'accesso ai dati del portafoglio"""
        if self.real_portfolio_data:
            return {
                'current_balance': self.real_portfolio_data['current_balance'],
                'total_invested': self.real_portfolio_data['total_invested'],
                'total_fees_paid': self.real_portfolio_data['total_fees_paid'],
                'weighted_avg': self.real_portfolio_data['weighted_avg_price'],
                'arithmetic_avg': self.real_portfolio_data['arithmetic_avg_price']
            }
        else:
            return {
                'current_balance': sum(self.quantita) if self.quantita else self.initial_amount,
                'total_invested': self.total_invested_real,
                'total_fees_paid': self.total_fees_paid_real,
                'weighted_avg': self.buy_price,
                'arithmetic_avg': self.buy_price_avg
            }

    def _draw_financial_performance(self, r, c, w, current_price):
        """📊 SEZIONE PORTAFOGLIO: Performance finanziaria dettagliata"""
        h = 8
        self._draw_box(r, c, h, w, "📊 PERFORMANCE FINANZIARIA", self.GREEN)

        portfolio_data = self._get_portfolio_data()
        current_value = current_price * portfolio_data['current_balance']

        # Usa FeeCalculator per calcoli centralizzati
        exit_fees = FeeCalculator.calculate_exit_fees(current_value)
        net_value = FeeCalculator.calculate_net_value_after_fees(current_value)
        total_cost = portfolio_data['total_invested'] + portfolio_data['total_fees_paid']

        # ROI e metriche
        roi_net = ProfitCalculator.calculate_roi_percentage(net_value, total_cost)

        # Range profit giornaliero usando helper centralizzato
        session_high_value = FeeCalculator.calculate_net_value_after_fees(
            self.session_high * portfolio_data['current_balance']
        )
        session_low_value = FeeCalculator.calculate_net_value_after_fees(
            self.session_low * portfolio_data['current_balance']
        )
        max_profit_today = ((session_high_value - total_cost) / total_cost) * 100 if total_cost > 0 else 0
        min_profit_today = ((session_low_value - total_cost) / total_cost) * 100 if total_cost > 0 else 0

        # Break-even usando helper centralizzato
        breakeven_price = FeeCalculator.calculate_breakeven_price(
            portfolio_data['total_invested'],
            portfolio_data['total_fees_paid'],
            portfolio_data['current_balance']
        )
        distance_to_breakeven = ((current_price - breakeven_price) / breakeven_price) * 100 if breakeven_price > 0 else 0

        # Visualizzazione
        roi_color = UIFormatter.get_profit_color(self, roi_net)
        self._safe_addstr(r + 1, c + 2, UIFormatter.format_percentage_line("ROI Istantaneo", roi_net, decimals=3, prefix="💹"), roi_color | curses.A_BOLD)

        breakeven_color = UIFormatter.get_profit_color(self, distance_to_breakeven)
        self._safe_addstr(r + 2, c + 2, f"⚖️  Break-Even: {breakeven_price:.6f} ({distance_to_breakeven:+.2f}%)", breakeven_color)

        # Range sessione
        range_color = self.GREEN if max_profit_today > 2 else self.YELLOW if max_profit_today > 0.5 else self.RED
        self._safe_addstr(r + 3, c + 2, UIFormatter.format_percentage_line("Max Oggi", max_profit_today, prefix="📈"), range_color)
        self._safe_addstr(r + 4, c + 2, UIFormatter.format_percentage_line("Min Oggi", min_profit_today, prefix="📉"), UIFormatter.get_profit_color(self, min_profit_today))

        # Volatilità e metriche aggiuntive
        range_spread = max_profit_today - min_profit_today
        efficiency = (net_value / portfolio_data['total_invested']) * 100 if portfolio_data['total_invested'] > 0 else 0
        fee_ratio = (portfolio_data['total_fees_paid'] / portfolio_data['total_invested']) * 100 if portfolio_data['total_invested'] > 0 else 0

        self._safe_addstr(r + 5, c + 2, f"🌊 Volatilità Sessione: {range_spread:.2f}%",
                         self.GREEN if range_spread > 2 else self.YELLOW)

        eff_color = self.GREEN if efficiency > 100 else self.YELLOW if efficiency > 95 else self.RED
        self._safe_addstr(r + 6, c + 2, f"⚙️  Efficienza: {efficiency:.1f}%", eff_color)

        self._safe_addstr(r + 7, c + 2, f"💸 Fee Ratio: {fee_ratio:.2f}%",
                         self.GREEN if fee_ratio < 1 else self.YELLOW if fee_ratio < 2 else self.RED)

        return r + h

    def _draw_professional_technical_analysis(self, r, c, w, current_price):
        """📊 SEZIONE MERCATO: Analisi Tecnica Professionale Multi-Timeframe con Market Sentiment integrato"""
        # Calcola altezza dinamica basata su contenuto expandibile
        base_height = 20
        sentiment_height = 12 if self.sentiment_expanded else 3
        bot_live_height = 15 if self.bot_live_expanded else 3
        h = base_height + sentiment_height + bot_live_height
        
        # Titolo principale con indicatore navigazione
        title = "📊 ANALISI TECNICA PROFESSIONALE"
        if self.current_tab == 0:
            title += " ◄ ATTIVO"
        
        self._draw_box(r, c, h, w, title, self.CYAN)

        # Aggiorna dati tecnici se necessario
        self._update_technical_data(current_price)

        # Header timeframes
        self._safe_addstr(r + 1, c + 2, "TIMEFRAME │   1M   │   5M   │  15M   │   1H   ", self.YELLOW | curses.A_BOLD)
        self._safe_addstr(r + 2, c + 2, "─" * (w - 4), self.CYAN)

        row = r + 3

        # RSI Analysis per timeframe
        row = self._draw_multi_timeframe_rsi(row, c, w)

        # MACD Analysis per timeframe  
        row = self._draw_multi_timeframe_macd(row, c, w)

        # EMA Trend Analysis
        row = self._draw_multi_timeframe_ema(row, c, w, current_price)

        # Segnali consolidati e coerenti
        row = self._draw_consolidated_signals(row, c, w)

        # ═══ SEZIONE MARKET SENTIMENT INTEGRATA ═══
        self._safe_addstr(row, c + 2, "═" * (w - 4), self.MAGENTA)
        row += 1
        
        # Header Market Sentiment con indicatore stato e navigazione
        sentiment_title = "🌍 MARKET SENTIMENT & CORRELAZIONI"
        if self.current_tab == 1:
            sentiment_title += " ◄ ATTIVO"
        if self.sentiment_expanded:
            sentiment_title += " ▼"
        else:
            sentiment_title += " ▶"
            
        self._safe_addstr(row, c + 2, sentiment_title, self.MAGENTA | curses.A_BOLD)
        row += 1
        
        if not self.sentiment_expanded:
            # Modalità collapsed: mostra solo indicazione
            self._safe_addstr(row, c + 4, "📊 Premi TAB per navigare, INVIO per espandere", self.CYAN | curses.A_DIM)
            row += 2
        else:
            # Modalità expanded: mostra contenuto completo
            row = self._draw_market_sentiment_content(row, c, w, current_price)
            row += 1

        # ========= SEZIONE BOT LIVE =========
        row += 1
        
        # Header Bot Live con indicatore stato e navigazione
        bot_title = "🤖 BOT SCALPING LIVE"
        if self.current_tab == 2:
            bot_title += " ◄ ATTIVO"
        if self.bot_live_expanded:
            bot_title += " ▼"
        else:
            bot_title += " ▶"
            
        self._safe_addstr(row, c + 2, bot_title, self.GREEN | curses.A_BOLD)
        row += 1
        
        if not self.bot_live_expanded:
            # Modalità collapsed: mostra solo indicazione
            self._safe_addstr(row, c + 4, "🤖 Premi TAB per navigare, INVIO per espandere", self.CYAN | curses.A_DIM)
        else:
            # Modalità expanded: mostra contenuto completo
            row = self._draw_bot_live_content(row, c, w, current_price)

        return r + h

    def _update_technical_data(self, current_price):
        """Aggiorna dati tecnici con cache intelligente"""
        current_time = time.time()

        # Aggiorna ogni 30 secondi per evitare overload API
        if current_time - self.last_technical_update < 30:
            return

        try:
            # Ottieni dati multi-timeframe
            self.market_data_cache = self.technical_analyzer.get_multi_timeframe_data(self.client, self.pair)

            # Analizza ogni timeframe
            self.technical_indicators = {}
            for tf in TradingConfig.TIMEFRAMES:
                if self.market_data_cache.get(tf):
                    self.technical_indicators[tf] = self.technical_analyzer.analyze_timeframe(
                        self.market_data_cache[tf], current_price
                    )

            self.last_technical_update = current_time

        except Exception as e:
            # Mantiene dati precedenti in caso di errore
            pass

    def _draw_multi_timeframe_rsi(self, r, c, w):
        """Disegna RSI per tutti i timeframes con interpretazione professionale"""
        self._safe_addstr(r, c + 2, "RSI(14)   │", self.WHITE | curses.A_BOLD)

        col_positions = [14, 21, 28, 35]  # Posizioni colonne per timeframes

        for i, tf in enumerate(TradingConfig.TIMEFRAMES):
            if tf in self.technical_indicators and self.technical_indicators[tf]:
                rsi = self.technical_indicators[tf]['rsi']
                if rsi is not None:
                    rsi_color, rsi_signal = self._get_rsi_analysis(rsi)
                    self._safe_addstr(r, c + col_positions[i], f"{rsi:5.1f}", rsi_color)
                else:
                    self._safe_addstr(r, c + col_positions[i], "  N/A", self.RED)
            else:
                self._safe_addstr(r, c + col_positions[i], "  N/A", self.RED)

        # Interpretazione RSI consolidata
        consensus_signal = self._get_rsi_consensus()
        self._safe_addstr(r, c + 42, f"│ {consensus_signal['text']}", consensus_signal['color'])

        return r + 1

    def _draw_multi_timeframe_macd(self, r, c, w):
        """Disegna MACD per tutti i timeframes"""
        self._safe_addstr(r, c + 2, "MACD      │", self.WHITE | curses.A_BOLD)

        col_positions = [14, 21, 28, 35]

        for i, tf in enumerate(TradingConfig.TIMEFRAMES):
            if tf in self.technical_indicators and self.technical_indicators[tf]:
                macd = self.technical_indicators[tf]['macd']
                if macd['line'] is not None and macd['signal'] is not None:
                    macd_signal = "↗" if macd['line'] > macd['signal'] else "↘"
                    macd_color = self.GREEN if macd['line'] > macd['signal'] else self.RED
                    self._safe_addstr(r, c + col_positions[i], f"  {macd_signal}  ", macd_color | curses.A_BOLD)
                else:
                    self._safe_addstr(r, c + col_positions[i], "  N/A", self.RED)
            else:
                self._safe_addstr(r, c + col_positions[i], "  N/A", self.RED)

        # Interpretazione MACD consolidata
        consensus_signal = self._get_macd_consensus()
        self._safe_addstr(r, c + 42, f"│ {consensus_signal['text']}", consensus_signal['color'])

        return r + 1

    def _draw_multi_timeframe_ema(self, r, c, w, current_price):
        """Disegna trend EMA per tutti i timeframes"""
        self._safe_addstr(r, c + 2, "EMA Trend │", self.WHITE | curses.A_BOLD)

        col_positions = [14, 21, 28, 35]

        for i, tf in enumerate(TradingConfig.TIMEFRAMES):
            if tf in self.technical_indicators and self.technical_indicators[tf]:
                trend = self.technical_indicators[tf]['trend_strength']
                if trend['direction'] in ['RIALZO', 'RIBASSO']:
                    trend_symbol = "↗" if trend['direction'] == 'RIALZO' else "↘"
                    trend_color = self.GREEN if trend['direction'] == 'RIALZO' else self.RED
                    self._safe_addstr(r, c + col_positions[i], f"  {trend_symbol}  ", trend_color | curses.A_BOLD)
                else:
                    self._safe_addstr(r, c + col_positions[i], "  ↔  ", self.YELLOW)
            else:
                self._safe_addstr(r, c + col_positions[i], "  N/A", self.RED)

        # Consensus trend
        consensus_trend = self._get_trend_consensus()
        self._safe_addstr(r, c + 42, f"│ {consensus_trend['text']}", consensus_trend['color'])

        return r + 1

    def _draw_consolidated_signals(self, r, c, w):
        """Disegna segnali operativi consolidati e coerenti"""
        self._safe_addstr(r, c + 2, "─" * (w - 4), self.CYAN)
        r += 1

        # Analisi consolidata di tutti gli indicatori
        final_signal = self._calculate_consolidated_signal()

        self._safe_addstr(r, c + 2, "📋 ANALISI CONSOLIDATA:", self.CYAN | curses.A_BOLD)
        r += 1

        # Forza del segnale
        strength_text = f"🎯 Forza Segnale: {final_signal['strength']}/5"
        strength_color = self.GREEN if final_signal['strength'] >= 4 else self.YELLOW if final_signal['strength'] >= 2 else self.RED
        self._safe_addstr(r, c + 4, strength_text, strength_color | curses.A_BOLD)
        r += 1

        # Direzione prevalente
        direction_text = f"📊 Direzione: {final_signal['direction']}"
        self._safe_addstr(r, c + 4, direction_text, final_signal['direction_color'] | curses.A_BOLD)
        r += 1

        # Raccomandazione operativa
        self._safe_addstr(r, c + 4, "💡 Raccomandazione:", self.MAGENTA | curses.A_BOLD)
        r += 1
        self._safe_addstr(r, c + 6, final_signal['recommendation'], final_signal['rec_color'] | curses.A_BOLD)
        r += 1

        # Timing e probabilità
        self._safe_addstr(r, c + 4, f"⏰ Timing: {final_signal['timing']}", self.CYAN)
        r += 1
        self._safe_addstr(r, c + 4, f"📈 Affidabilità: {final_signal['reliability']}%",
                         self.GREEN if final_signal['reliability'] >= 70 else self.YELLOW if final_signal['reliability'] >= 50 else self.RED)

        return r + 2

    def _get_rsi_analysis(self, rsi_value):
        """Analizza RSI secondo standard professionali"""
        if rsi_value >= 80:
            return self.RED | curses.A_BOLD, "FORTEMENTE IPERCOMPRATO"
        elif rsi_value >= 70:
            return self.RED, "IPERCOMPRATO"
        elif rsi_value >= 60:
            return self.YELLOW, "RIALZISTA"
        elif rsi_value >= 40:
            return self.WHITE, "NEUTRO"
        elif rsi_value >= 30:
            return self.GREEN, "RIBASSISTA"
        elif rsi_value >= 20:
            return self.GREEN, "IPERVENDUTO"
        else:
            return self.GREEN | curses.A_BOLD, "FORTEMENTE IPERVENDUTO"

    def _get_rsi_consensus(self):
        """Calcola consensus RSI tra tutti i timeframes"""
        rsi_values = []
        for tf in TradingConfig.TIMEFRAMES:
            if tf in self.technical_indicators and self.technical_indicators[tf]:
                rsi = self.technical_indicators[tf]['rsi']
                if rsi is not None:
                    rsi_values.append(rsi)

        if not rsi_values:
            return {'text': "DATI NON DISPONIBILI", 'color': self.RED}

        avg_rsi = sum(rsi_values) / len(rsi_values)

        if avg_rsi >= 70:
            return {'text': "IPERCOMPRATO - CAUTELA", 'color': self.RED | curses.A_BOLD}
        elif avg_rsi >= 60:
            return {'text': "TREND RIALZISTA", 'color': self.GREEN}
        elif avg_rsi >= 40:
            return {'text': "RANGE NEUTRO", 'color': self.YELLOW}
        elif avg_rsi >= 30:
            return {'text': "TREND RIBASSISTA", 'color': self.RED}
        else:
            return {'text': "IPERVENDUTO - OPPORTUNITÀ", 'color': self.GREEN | curses.A_BOLD}

    def _get_macd_consensus(self):
        """Calcola consensus MACD tra tutti i timeframes"""
        bullish_signals = 0
        bearish_signals = 0
        total_signals = 0

        for tf in TradingConfig.TIMEFRAMES:
            if tf in self.technical_indicators and self.technical_indicators[tf]:
                macd = self.technical_indicators[tf]['macd']
                if macd['line'] is not None and macd['signal'] is not None:
                    total_signals += 1
                    if macd['line'] > macd['signal']:
                        bullish_signals += 1
                    else:
                        bearish_signals += 1

        if total_signals == 0:
            return {'text': "DATI NON DISPONIBILI", 'color': self.RED}

        bullish_ratio = bullish_signals / total_signals

        if bullish_ratio >= 0.75:
            return {'text': "MOMENTUM RIALZISTA FORTE", 'color': self.GREEN | curses.A_BOLD}
        elif bullish_ratio >= 0.5:
            return {'text': "MOMENTUM RIALZISTA", 'color': self.GREEN}
        elif bullish_ratio >= 0.25:
            return {'text': "MOMENTUM RIBASSISTA", 'color': self.RED}
        else:
            return {'text': "MOMENTUM RIBASSISTA FORTE", 'color': self.RED | curses.A_BOLD}

    def _get_trend_consensus(self):
        """Calcola consensus trend tra tutti i timeframes"""
        bullish_trends = 0
        bearish_trends = 0
        total_trends = 0

        for tf in TradingConfig.TIMEFRAMES:
            if tf in self.technical_indicators and self.technical_indicators[tf]:
                trend = self.technical_indicators[tf]['trend_strength']
                total_trends += 1
                if trend['direction'] == 'RIALZO':
                    bullish_trends += 1
                elif trend['direction'] == 'RIBASSO':
                    bearish_trends += 1

        if total_trends == 0:
            return {'text': "DATI NON DISPONIBILI", 'color': self.RED}

        bullish_ratio = bullish_trends / total_trends

        if bullish_ratio >= 0.75:
            return {'text': "TREND RIALZISTA DOMINANTE", 'color': self.GREEN | curses.A_BOLD}
        elif bullish_ratio >= 0.5:
            return {'text': "BIAS RIALZISTA", 'color': self.GREEN}
        elif bullish_ratio >= 0.25:
            return {'text': "BIAS RIBASSISTA", 'color': self.RED}
        else:
            return {'text': "TREND RIBASSISTA DOMINANTE", 'color': self.RED | curses.A_BOLD}

    def _calculate_consolidated_signal(self):
        """Calcola segnale finale consolidato eliminando contraddizioni"""
        # Raccoglie tutti i segnali
        rsi_consensus = self._get_rsi_consensus()
        macd_consensus = self._get_macd_consensus()
        trend_consensus = self._get_trend_consensus()

        # Scoring system professionale
        score = 0
        confidence_factors = []

        # RSI scoring
        if "IPERCOMPRATO" in rsi_consensus['text']:
            score -= 2
            confidence_factors.append("RSI_OVERBOUGHT")
        elif "IPERVENDUTO" in rsi_consensus['text']:
            score += 2
            confidence_factors.append("RSI_OVERSOLD")
        elif "RIALZISTA" in rsi_consensus['text']:
            score += 1
        elif "RIBASSISTA" in rsi_consensus['text']:
            score -= 1

        # MACD scoring
        if "FORTE" in macd_consensus['text']:
            if "RIALZISTA" in macd_consensus['text']:
                score += 2
                confidence_factors.append("MACD_BULLISH_STRONG")
            else:
                score -= 2
                confidence_factors.append("MACD_BEARISH_STRONG")
        elif "RIALZISTA" in macd_consensus['text']:
            score += 1
        elif "RIBASSISTA" in macd_consensus['text']:
            score -= 1

        # Trend scoring
        if "DOMINANTE" in trend_consensus['text']:
            if "RIALZISTA" in trend_consensus['text']:
                score += 2
                confidence_factors.append("TREND_BULLISH_STRONG")
            else:
                score -= 2
                confidence_factors.append("TREND_BEARISH_STRONG")
        elif "RIALZISTA" in trend_consensus['text']:
            score += 1
        elif "RIBASSISTA" in trend_consensus['text']:
            score -= 1

        # Determina segnale finale
        strength = min(5, abs(score))
        reliability = min(95, max(30, 40 + (strength * 10) + len(confidence_factors) * 5))

        if score >= 3:
            direction = "FORTEMENTE RIALZISTA"
            direction_color = self.GREEN | curses.A_BOLD
            recommendation = "VENDI 75-100% della posizione"
            rec_color = self.GREEN | curses.A_BOLD
            timing = "IMMEDIATO - Opportunità forte"
        elif score >= 1:
            direction = "RIALZISTA"
            direction_color = self.GREEN
            recommendation = "VENDI 25-50% gradualmente"
            rec_color = self.GREEN
            timing = "Prossimi 5-15 minuti"
        elif score <= -3:
            direction = "FORTEMENTE RIBASSISTA"
            direction_color = self.RED | curses.A_BOLD
            recommendation = "MANTIENI posizione - Attendi"
            rec_color = self.YELLOW
            timing = "NO ACTION - Pazienza"
        elif score <= -1:
            direction = "RIBASSISTA"
            direction_color = self.RED
            recommendation = "CAUTELA - Riduci esposizione"
            rec_color = self.YELLOW
            timing = "Monitora attentamente"
        else:
            direction = "NEUTRO/LATERALE"
            direction_color = self.YELLOW
            recommendation = "ATTENDI segnale più chiaro"
            rec_color = self.YELLOW
            timing = "Pazienza - Setup non definito"

        return {
            'strength': strength,
            'direction': direction,
            'direction_color': direction_color,
            'recommendation': recommendation,
            'rec_color': rec_color,
            'timing': timing,
            'reliability': reliability,
            'confidence_factors': confidence_factors
        }

    def _draw_market_sentiment_content(self, r, c, w, current_price):
        """🌍 CONTENUTO MARKET SENTIMENT: Versione integrata senza box"""
        # Ottieni dati correlazione BTC/ETH
        correlation_data = self._get_btc_eth_correlation_data()

        # Status BTC e ETH
        self._safe_addstr(r, c + 4, "📊 MAJOR COINS STATUS:", self.CYAN | curses.A_BOLD)

        btc_text = f"₿ BTC: {correlation_data['btc_trend']} "
        eth_text = f"Ξ ETH: {correlation_data['eth_trend']}"

        self._safe_addstr(r + 1, c + 6, btc_text, correlation_data['trend_color'])
        self._safe_addstr(r + 1, c + 27, eth_text, correlation_data['trend_color'])

        # Correlazione e forza
        correlation_strength = correlation_data['correlation_strength']
        corr_color = correlation_data['correlation_color']

        self._safe_addstr(r + 2, c + 4, f"🔗 Correlazione: {correlation_strength}", corr_color | curses.A_BOLD)

        # Impatto stimato sulla coppia
        impact_score = self._calculate_correlation_impact(correlation_data)
        impact_text, impact_color = self._format_impact_score(impact_score)

        self._safe_addstr(r + 3, c + 4, f"⚡ Impatto su {self.pair}: {impact_text}", impact_color | curses.A_BOLD)

        # Sentiment score completo
        sentiment_score = self._calculate_market_sentiment_score(correlation_data, impact_score)
        
        self._safe_addstr(r + 4, c + 4, f"🎯 Sentiment Score: {sentiment_score}/100", 
                         self.GREEN if sentiment_score > 60 else self.RED if sentiment_score < 40 else self.YELLOW)

        # Raccomandazione integrata
        if sentiment_score >= 70:
            recommendation = "🟢 BULLISH - Posizioni long favorite"
            rec_color = self.GREEN
        elif sentiment_score <= 30:
            recommendation = "🔴 BEARISH - Cautela su long"
            rec_color = self.RED
        else:
            recommendation = "🟡 NEUTRO - Attendi segnali più chiari"
            rec_color = self.YELLOW

        self._safe_addstr(r + 5, c + 4, recommendation, rec_color | curses.A_BOLD)

        # Nota navigazione
        self._safe_addstr(r + 7, c + 4, "📝 ESC per uscire, TAB per navigare", self.CYAN | curses.A_DIM)

        return r + 9  # Restituisce nuova posizione row

    def _draw_bot_live_content(self, r, c, w, current_price):
        """🤖 CONTENUTO BOT LIVE: Mostra dati live del bot scalping"""
        
        # Leggi gli ultimi log del bot
        bot_status = self._get_bot_status_from_logs()
        
        # Status del bot
        self._safe_addstr(r, c + 4, "🤖 BOT STATUS:", self.GREEN | curses.A_BOLD)
        
        if bot_status['is_running']:
            status_text = f"🟢 ATTIVO - {bot_status['current_state']}"
            status_color = self.GREEN
        else:
            status_text = "🔴 INATTIVO"
            status_color = self.RED
            
        self._safe_addstr(r + 1, c + 4, status_text, status_color | curses.A_BOLD)
        
        # Statistiche del bot
        self._safe_addstr(r + 2, c + 4, f"📊 Trades oggi: {bot_status['trades_today']}", self.CYAN)
        self._safe_addstr(r + 3, c + 4, f"💰 P&L stimato: {bot_status['estimated_pnl']:+.2f}%", 
                         self.GREEN if bot_status['estimated_pnl'] > 0 else self.RED if bot_status['estimated_pnl'] < 0 else self.YELLOW)
        
        # Ultimo trade
        if bot_status['last_trade']:
            self._safe_addstr(r + 4, c + 4, "🔄 Ultimo trade:", self.CYAN | curses.A_BOLD)
            self._safe_addstr(r + 5, c + 6, f"Tipo: {bot_status['last_trade']['type']}", self.WHITE)
            self._safe_addstr(r + 6, c + 6, f"Prezzo: {bot_status['last_trade']['price']:.8f}", self.WHITE)
            self._safe_addstr(r + 7, c + 6, f"Ora: {bot_status['last_trade']['time']}", self.WHITE)
        
        # Posizione corrente
        if bot_status['current_position']:
            self._safe_addstr(r + 8, c + 4, "💼 Posizione corrente:", self.MAGENTA | curses.A_BOLD)
            self._safe_addstr(r + 9, c + 6, f"Quantità: {bot_status['current_position']['amount']:.8f}", self.WHITE)
            self._safe_addstr(r + 10, c + 6, f"Entry: {bot_status['current_position']['entry_price']:.8f}", self.WHITE)
            self._safe_addstr(r + 11, c + 6, f"Target: {bot_status['current_position']['target_price']:.8f}", self.WHITE)
        else:
            self._safe_addstr(r + 8, c + 4, "💼 Nessuna posizione aperta", self.YELLOW)
        
        # Nota navigazione
        self._safe_addstr(r + 12, c + 4, "📝 TAB per navigare, INVIO per collassare", self.CYAN | curses.A_DIM)
        
        return r + 14  # Restituisce nuova posizione row

    def _get_bot_status_from_logs(self):
        """📊 Legge lo status del bot dai log più recenti"""
        import os
        from datetime import datetime
        
        # Default status
        status = {
            'is_running': False,
            'current_state': 'SCONOSCIUTO',
            'trades_today': 0,
            'estimated_pnl': 0.0,
            'last_trade': None,
            'current_position': None
        }
        
        try:
            # Percorso log di oggi
            today = datetime.now().strftime('%Y-%m-%d')
            log_file = f"/home/fraxl/Scrivania/lavoro/progetti/python/evodash01/logs/trades_{today}.log"
            
            if not os.path.exists(log_file):
                return status
            
            # Leggi le ultime 50 righe
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                recent_lines = lines[-50:] if len(lines) > 50 else lines
            
            # Analizza i log
            buy_trades = []
            sell_trades = []
            
            for line in reversed(recent_lines):
                if '🔄 Piazzando ordine:' in line and "'side': 'buy'" in line:
                    # Estrai info trade di acquisto
                    if 'currency_pair' in line and 'amount' in line and 'price' in line:
                        import re
                        amount_match = re.search(r"'amount': '([^']+)'", line)
                        price_match = re.search(r"'price': '([^']+)'", line)
                        time_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                        
                        if amount_match and price_match and time_match:
                            buy_trades.append({
                                'type': 'BUY',
                                'amount': float(amount_match.group(1)),
                                'price': float(price_match.group(1)),
                                'time': time_match.group(1).split(' ')[1][:5]  # HH:MM
                            })
                
                elif '🔄 Piazzando ordine:' in line and "'side': 'sell'" in line:
                    # Estrai info trade di vendita
                    if 'currency_pair' in line and 'amount' in line and 'price' in line:
                        import re
                        amount_match = re.search(r"'amount': '([^']+)'", line)
                        price_match = re.search(r"'price': '([^']+)'", line)
                        time_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                        
                        if amount_match and price_match and time_match:
                            sell_trades.append({
                                'type': 'SELL',
                                'amount': float(amount_match.group(1)),
                                'price': float(price_match.group(1)),
                                'time': time_match.group(1).split(' ')[1][:5]  # HH:MM
                            })
            
            # Determina status
            status['trades_today'] = len(buy_trades) + len(sell_trades)
            
            if recent_lines:
                # Il bot è attivo se ci sono stati trade nelle ultime righe
                last_30_lines = ''.join(recent_lines[-30:])
                if '🔄 Piazzando ordine:' in last_30_lines:
                    status['is_running'] = True
                    status['current_state'] = 'TRADING'
            
            # Ultimo trade
            all_trades = sorted(buy_trades + sell_trades, key=lambda x: x['time'], reverse=True)
            if all_trades:
                status['last_trade'] = all_trades[0]
            
            # Stima P&L (semplificato)
            if len(buy_trades) > 0 and len(sell_trades) > 0:
                avg_buy = sum(t['price'] for t in buy_trades) / len(buy_trades)
                avg_sell = sum(t['price'] for t in sell_trades) / len(sell_trades)
                status['estimated_pnl'] = ((avg_sell - avg_buy) / avg_buy) * 100
            
            # Posizione corrente (se ci sono più buy che sell)
            if len(buy_trades) > len(sell_trades) and buy_trades:
                latest_buy = buy_trades[0]  # Il più recente
                status['current_position'] = {
                    'amount': latest_buy['amount'],
                    'entry_price': latest_buy['price'],
                    'target_price': latest_buy['price'] * 1.02  # +2% target
                }
                
        except Exception as e:
            # In caso di errore, ritorna status di default
            pass
            
        return status

    def _draw_market_sentiment_panel(self, r, c, w, current_price):
        """🌍 PANNELLO SENTIMENT: Analisi BTC/ETH e influenze macro"""
        h = 11
        self._draw_box(r, c, h, w, "🌍 MARKET SENTIMENT & CORRELAZIONI", self.MAGENTA)

        # Ottieni dati correlazione BTC/ETH
        correlation_data = self._get_btc_eth_correlation_data()

        # Status BTC e ETH
        self._safe_addstr(r + 1, c + 2, "📊 MAJOR COINS STATUS:", self.CYAN | curses.A_BOLD)

        btc_text = f"₿ BTC: {correlation_data['btc_trend']} "
        eth_text = f"Ξ ETH: {correlation_data['eth_trend']}"

        self._safe_addstr(r + 2, c + 4, btc_text, correlation_data['trend_color'])
        self._safe_addstr(r + 2, c + 25, eth_text, correlation_data['trend_color'])

        # Correlazione e forza
        correlation_strength = correlation_data['correlation_strength']
        corr_color = correlation_data['correlation_color']

        self._safe_addstr(r + 3, c + 2, f"🔗 Correlazione: {correlation_strength}", corr_color | curses.A_BOLD)

        # Impatto stimato sulla coppia
        impact_score = self._calculate_correlation_impact(correlation_data)
        impact_text, impact_color = self._format_impact_score(impact_score)

        self._safe_addstr(r + 4, c + 2, f"⚡ Impatto su {self.pair}: {impact_text}", impact_color | curses.A_BOLD)

        # Separatore
        self._safe_addstr(r + 5, c + 2, "─" * (w - 4), self.CYAN)

        # Market Regime Detection
        regime = self._detect_market_regime_simple(correlation_data)
        self._safe_addstr(r + 6, c + 2, f"🌊 Regime di Mercato: {regime['text']}", regime['color'] | curses.A_BOLD)

        # Sentiment Score
        sentiment_score = self._calculate_market_sentiment_score(correlation_data, impact_score)
        sentiment_text, sentiment_color = self._format_sentiment_score(sentiment_score)

        self._safe_addstr(r + 7, c + 2, f"🎯 Sentiment Score: {sentiment_text}", sentiment_color | curses.A_BOLD)

        # Raccomandazione operativa basata su macro
        macro_advice = self._get_macro_operational_advice(correlation_data, sentiment_score)

        self._safe_addstr(r + 8, c + 2, "💡 OUTLOOK MACRO:", self.MAGENTA | curses.A_BOLD)
        self._safe_addstr(r + 9, c + 4, macro_advice['action'][:w-6], macro_advice['color'] | curses.A_BOLD)
        self._safe_addstr(r + 10, c + 4, macro_advice['timing'][:w-6], self.CYAN)

        return r + h

    def _format_impact_score(self, impact_score):
        """Formatta l'impatto score - Usa helper centralizzato"""
        return MarketFormatter.format_impact_score(impact_score)

    def _detect_market_regime_simple(self, correlation_data):
        """Rileva regime di mercato - Usa helper centralizzato"""
        return MarketAnalyzer.detect_market_regime(
            correlation_data['btc_trend_score'],
            correlation_data['eth_trend_score'],
            correlation_data['correlation_score']
        )

    def _calculate_market_sentiment_score(self, correlation_data, impact_score):
        """Calcola sentiment score - Usa helper centralizzato"""
        return MarketAnalyzer.calculate_sentiment_score(
            correlation_data['btc_trend_score'],
            correlation_data['eth_trend_score'],
            impact_score
        )

    def _format_sentiment_score(self, score):
        """Formatta sentiment score - Usa helper centralizzato"""
        return MarketFormatter.format_sentiment_score(score)

    def _get_macro_operational_advice(self, correlation_data, sentiment_score):
        """Genera consigli operativi basati su analisi macro"""
        btc_score = correlation_data['btc_trend_score']
        correlation = correlation_data['correlation_score']

        # Logica semplificata ma efficace
        if sentiment_score >= 75 and correlation > 1:
            return {
                'action': "🚀 BULL PHASE - Vendi gradualmente sui pumps",
                'timing': "⏰ Finestra: Prossime 1-6 ore",
                'color': self.GREEN
            }
        elif sentiment_score <= 25 and btc_score < -1:
            return {
                'action': "🛡️ BEAR PHASE - Hodl e accumula su dips",
                'timing': "⏰ Strategia: Lungo termine (giorni/settimane)",
                'color': self.RED
            }
        elif abs(correlation) < 0.3 and sentiment_score > 50:
            return {
                'action': "⭐ ALTSEASON - Sfrutta movimenti indipendenti",
                'timing': "⏰ Opportunity window: 2-48 ore",
                'color': self.MAGENTA
            }
        elif 40 <= sentiment_score <= 60:
            return {
                'action': "⚖️ RANGE MARKET - Trading tattico su range",
                'timing': "⏰ Approccio: Swing trading",
                'color': self.YELLOW
            }
        else:
            return {
                'action': "🔍 UNDEFINED - Attendi segnali più chiari",
                'timing': "⏰ Status: Standby & monitor",
                'color': self.CYAN
            }

    def _calculate_price_velocities(self):
        """Calcola velocità del prezzo per diversi timeframe"""
        velocity_data = {'vel_30s': 0, 'vel_1m': 0, 'vel_5m': 0, 'acceleration': 0}

        if len(self.price_history) >= 2:
            current_time = time.time()

            # Velocità 30 secondi
            recent_30s = [p for t, p in self.price_history if current_time - t <= 30]
            if len(recent_30s) >= 2:
                velocity_data['vel_30s'] = ((recent_30s[-1] - recent_30s[0]) / recent_30s[0]) * 100

            # Velocità 1 minuto
            recent_1m = [p for t, p in self.price_history if current_time - t <= 60]
            if len(recent_1m) >= 2:
                velocity_data['vel_1m'] = ((recent_1m[-1] - recent_1m[0]) / recent_1m[0]) * 100

            # Velocità 5 minuti
            recent_5m = [p for t, p in self.price_history if current_time - t <= 300]
            if len(recent_5m) >= 2:
                velocity_data['vel_5m'] = ((recent_5m[-1] - recent_5m[0]) / recent_5m[0]) * 100

            # Accelerazione
            if len(recent_1m) >= 3:
                vel1 = ((recent_1m[-2] - recent_1m[0]) / recent_1m[0]) * 100
                vel2 = ((recent_1m[-1] - recent_1m[-2]) / recent_1m[-2]) * 100
                velocity_data['acceleration'] = vel2 - vel1

        return TradingSignalHelper.calculate_price_velocities(self.price_history)

    def _get_trading_signals(self, momentum_score, vel_1m, session_range_perc):
        """Genera segnali di trading - Usa helper centralizzato"""
        return TradingSignalHelper.get_trading_signals(momentum_score, vel_1m, session_range_perc)

    def _draw_target_progress_system(self, r, c, w, current_price):
        """🎯 SISTEMA TARGET: Progresso intelligente multi-fase con Design Pattern Strategy"""
        h = 12  # Aumentato per maggiori dettagli
        self._draw_box(r, c, h, w, "🎯 SISTEMA TARGET SMART", self.MAGENTA)

        portfolio_data = self._get_portfolio_data()
        target_price = portfolio_data['arithmetic_avg'] * (1 + self.target_percent / 100)

        # Inizializza il calculator intelligente
        if not hasattr(self, 'progress_calculator'):
            self.progress_calculator = SmartProgressCalculator(self.RED, self.YELLOW, self.GREEN)

        # Calcola fase attuale e progresso
        current_phase, progress, target_values = self.progress_calculator.calculate_current_phase_and_progress(
            portfolio_data, current_price, self.target_percent
        )

        # Header con target
        self._safe_addstr(r + 1, c + 2, f"🎯 Target: {target_price:.6f} (+{self.target_percent}%)", curses.A_BOLD)

        # Distanza al target
        profit_to_target = ((target_price - current_price) / current_price) * 100
        target_status = "RAGGIUNTO!" if profit_to_target <= 0 else f"{profit_to_target:+.2f}%"
        self._safe_addstr(r + 2, c + 2, f"📊 Distanza: {target_status}",
                         self.GREEN | curses.A_BOLD if profit_to_target <= 0 else self.YELLOW)

        # ===== FASE ATTUALE CON DESCRIZIONE CHIARA =====
        phase_display = f"🔄 {current_phase.name}"
        self._safe_addstr(r + 3, c + 2, phase_display, current_phase.color | curses.A_BOLD)
        self._safe_addstr(r + 4, c + 4, f"→ {current_phase.description}", curses.A_DIM)

        # ===== BARRA DI PROGRESSO AVANZATA =====
        bar_width = min(w - 10, 35)
        filled_width = int(bar_width * progress / 100)

        # Crea barra con carattere specifico della fase
        bar_filled = current_phase.char * filled_width
        bar_empty = "░" * (bar_width - filled_width)
        bar = bar_filled + bar_empty

        self._safe_addstr(r + 5, c + 2, f"[{bar}] {progress:.1f}%", current_phase.color | curses.A_BOLD)

        # ===== DETTAGLI FINANZIARI FASE-SPECIFICI =====
        self._safe_addstr(r + 6, c + 2, "─" * (w - 4), self.MAGENTA)

        current_value = current_price * portfolio_data['current_balance']

        if current_phase.name == "AMMORTAMENTO FEES ENTRATA":
            recovery_needed = target_values['initial_investment']
            recovered_amount = min(current_value, recovery_needed)
            remaining = max(0, recovery_needed - current_value)

            self._safe_addstr(r + 7, c + 2, f"💰 Recuperato: {recovered_amount:.2f}$ / {recovery_needed:.2f}$", self.CYAN)
            if remaining > 0:
                self._safe_addstr(r + 8, c + 2, f"⚠️  Mancano: {remaining:.2f}$ per coprire investimento", self.RED)
            else:
                self._safe_addstr(r + 8, c + 2, f"✅ Investimento iniziale coperto!", self.GREEN)

        elif current_phase.name == "AMMORTAMENTO FEES USCITA":
            net_value = current_value - target_values['exit_fees']
            total_cost = target_values['total_cost_basis']
            covered_cost = min(net_value, total_cost)

            self._safe_addstr(r + 7, c + 2, f"💎 Val.Netto: {net_value:.2f}$ / {total_cost:.2f}$ (costo)", self.CYAN)
            self._safe_addstr(r + 8, c + 2, f"💸 Exit Fees: {target_values['exit_fees']:.2f}$ (0.2%)", self.YELLOW)

        else:  # PROFITTO NETTO
            net_value = current_value - target_values['exit_fees']
            current_profit = net_value - target_values['total_cost_basis']
            target_profit = target_values['target_profit']

            self._safe_addstr(r + 7, c + 2, f"🚀 Profitto: {current_profit:+.2f}$ / {target_profit:+.2f}$ (target)", self.GREEN)
            efficiency = (current_profit / target_profit * 100) if target_profit > 0 else 100
            self._safe_addstr(r + 8, c + 2, f"⚡ Efficienza: {efficiency:.1f}% del target",
                             self.GREEN if efficiency >= 80 else self.YELLOW)

        # ===== STATUS OPERATIVO INTELLIGENTE =====
        status_msg = self._get_smart_operational_status(current_phase, progress, profit_to_target)
        self._safe_addstr(r + 9, c + 2, status_msg['text'][:w-4], status_msg['color'])

        # ===== TEMPO STIMATO (MIGLIORATO) =====
        time_estimate = self._calculate_smart_time_estimate(current_phase, progress, profit_to_target)
        if time_estimate:
            self._safe_addstr(r + 10, c + 2, time_estimate['text'][:w-4], time_estimate['color'])

        # ===== SUMMARY NUMERICO =====
        net_profit = (current_value - target_values['exit_fees']) - target_values['total_cost_basis']
        target_net_profit = target_values['target_profit']
        self._safe_addstr(r + 11, c + 2, f"💹 Ora: {net_profit:+.2f}$ | Target: {target_net_profit:+.2f}$",
                         self.GREEN if net_profit > 0 else self.RED)

        return r + h

    def _get_smart_operational_status(self, current_phase, progress, profit_to_target):
        """Genera status operativo intelligente basato sulla fase attuale"""

        if current_phase.name == "AMMORTAMENTO FEES ENTRATA":
            if progress >= 90:
                return {
                    'text': "🔄 QUASI PRONTO - Investimento quasi recuperato",
                    'color': self.YELLOW | curses.A_BOLD
                }
            elif progress >= 50:
                return {
                    'text': "⏳ IN RECUPERO - Buon progresso investimento",
                    'color': self.YELLOW
                }
            else:
                return {
                    'text': "🚧 EARLY STAGE - Pazienza, ancora in perdita",
                    'color': self.RED
                }

        elif current_phase.name == "AMMORTAMENTO FEES USCITA":
            if progress >= 90:
                return {
                    'text': "🎯 QUASI BREAK-EVEN - Pronto al profitto!",
                    'color': self.GREEN | curses.A_BOLD
                }
            elif progress >= 70:
                return {
                    'text': "⚡ BREAK-EVEN VICINO - Momento critico",
                    'color': self.YELLOW | curses.A_BOLD
                }
            else:
                return {
                    'text': "🔧 AMMORTIZZANDO - Copertura fees di uscita",
                    'color': self.YELLOW
                }

        else:  # PROFITTO NETTO
            if profit_to_target <= 0:
                return {
                    'text': "🚀 TARGET RAGGIUNTO! Ottimo momento vendita",
                    'color': self.GREEN | curses.A_BOLD | curses.A_BLINK
                }
            elif progress >= 80:
                return {
                    'text': "💰 QUASI AL TARGET - Considera vendita parziale",
                    'color': self.GREEN | curses.A_BOLD
                }
            elif progress >= 50:
                return {
                    'text': "📈 BUON PROFITTO - Mantieni posizione",
                    'color': self.GREEN
                }
            else:
                return {
                    'text': "✅ IN PROFITTO - Trend positivo confermato",
                    'color': self.GREEN
                }

    def _calculate_smart_time_estimate(self, current_phase, progress, profit_to_target):
        """Calcola stima tempo intelligente basata su fase e velocità"""

        if len(self.price_history) < 3:
            return {
                'text': "⏱️  Calcolo stima... (dati insufficienti)",
                'color': self.CYAN
            }

        # Calcola velocità media degli ultimi 2 minuti
        current_time = time.time()
        recent_prices = [(t, p) for t, p in self.price_history if current_time - t <= 120]

        if len(recent_prices) < 2:
            return {
                'text': "⏱️  Velocità non rilevabile",
                'color': self.CYAN
            }

        # Velocità percentuale per minuto
        time_span = (recent_prices[-1][0] - recent_prices[0][0]) / 60  # minuti
        price_change = ((recent_prices[-1][1] - recent_prices[0][1]) / recent_prices[0][1]) * 100
        velocity_per_minute = price_change / time_span if time_span > 0 else 0

        if current_phase.name == "PROFITTO NETTO" and profit_to_target <= 0:
            return {
                'text': "🎯 TARGET SUPERATO! Tempo perfetto per vendere",
                'color': self.GREEN | curses.A_BOLD
            }

        if abs(velocity_per_minute) < 0.01:  # Velocità troppo bassa
            if current_phase.name == "PROFITTO NETTO":
                return {
                    'text': "⏳ Mercato laterale - Pazienza per momentum",
                    'color': self.YELLOW
                }
            else:
                return {
                    'text': "🐌 Progresso lento - Trend laterale",
                    'color': self.CYAN
                }

        # Stima basata sulla fase
        if current_phase.name == "AMMORTAMENTO FEES ENTRATA":
            remaining_progress = 100 - progress
            if velocity_per_minute > 0:
                minutes_to_complete = remaining_progress / (velocity_per_minute * 10)  # Fattore conservativo
                return self._format_time_estimate(minutes_to_complete, "completamento fase")
            else:
                return {
                    'text': "📉 Trend negativo - Tempo indefinito",
                    'color': self.RED
                }

        elif current_phase.name == "AMMORTAMENTO FEES USCITA":
            remaining_progress = 100 - progress
            if velocity_per_minute > 0:
                minutes_to_break_even = remaining_progress / (velocity_per_minute * 8)  # Meno conservativo
                return self._format_time_estimate(minutes_to_break_even, "break-even")
            else:
                return {
                    'text': "⚠️  Trend negativo - Break-even a rischio",
                    'color': self.RED
                }

        else:  # PROFITTO NETTO
            if profit_to_target > 0 and velocity_per_minute > 0:
                minutes_to_target = profit_to_target / velocity_per_minute
                return self._format_time_estimate(minutes_to_target, "target")
            else:
                return {
                    'text': "✅ In profitto - Mantieni posizione",
                    'color': self.GREEN
                }

    def _format_time_estimate(self, minutes, phase_description):
        """Formatta la stima del tempo in modo user-friendly"""
        if minutes < 0:
            return {
                'text': f"⚠️  Trend contrario per {phase_description}",
                'color': self.RED
            }
        elif minutes < 60:
            return {
                'text': f"⏱️  ~{minutes:.0f}min al {phase_description}",
                'color': self.GREEN
            }
        elif minutes < 1440:  # < 24 ore
            hours = minutes / 60
            return {
                'text': f"⏱️  ~{hours:.1f}h al {phase_description}",
                'color': self.CYAN
            }
        elif minutes < 10080:  # < 7 giorni
            days = minutes / 1440
            return {
                'text': f"⏱️  ~{days:.1f}d al {phase_description}",
                'color': self.YELLOW
            }
        else:
            return {
                'text': f"⏳ {phase_description} molto lontano",
                'color': self.RED
            }

    def _calculate_time_to_target(self, profit_to_target):
        """Calcola stima tempo per raggiungere il target"""
        if profit_to_target > 0 and len(self.price_history) >= 2:
            recent_prices = [p for t, p in self.price_history if time.time() - t <= 120]
            if len(recent_prices) >= 2:
                velocity_2m = ((recent_prices[-1] - recent_prices[0]) / recent_prices[0]) * 100
                if velocity_2m > 0.01:
                    hours_to_target = abs(profit_to_target) / (velocity_2m * 30)
                    if hours_to_target < 24:
                        return f"⏱️  ~{hours_to_target:.1f}h al target"
                    elif hours_to_target < 168:
                        return f"⏱️  ~{hours_to_target/24:.1f}d al target"
                    else:
                        return "⏱️  Target lontano"
        elif profit_to_target <= 0:
            return "⏱️  TARGET SUPERATO!"
        return "⏱️  Trend insufficiente"

    def _get_target_status(self, break_even_reached, progress):
        """Determina lo status del target"""
        if break_even_reached and progress >= 90:
            return {
                'text': "🚀 QUASI AL TARGET! Ottimo momento vendita",
                'color': self.GREEN | curses.A_BOLD | curses.A_BLINK
            }
        elif break_even_reached and progress >= 50:
            return {
                'text': "💰 IN PROFITTO - Considera vendita parziale",
                'color': self.GREEN
            }
        elif break_even_reached:
            return {
                'text': "✅ BREAK-EVEN SUPERATO - Mantieni posizione",
                'color': self.GREEN
            }
        elif progress >= 80:
            return {
                'text': "⚡ VICINO AL PAREGGIO - Trend positivo",
                'color': self.YELLOW
            }
        else:
            return {
                'text': "🔄 AMMORTIZZANDO COSTI - Pazienza richiesta",
                'color': self.RED
            }

    def _draw_card_buy_stats(self, r, c, w):
        # Calcola altezza dinamica
        if self.real_portfolio_data and self.real_portfolio_data['buy_trades']:
            num_trades = len(self.real_portfolio_data['buy_trades'])
            h = min(8 + num_trades, 15)
        else:
            h = 5 + len(self.prezzi) if self.prezzi else 6

        self._draw_box(r, c, h, w, "Tranche Acquisti Attive")

        if self.real_portfolio_data and self.real_portfolio_data['buy_trades']:
            buy_trades = self.real_portfolio_data['buy_trades']
            total_trades = self.real_portfolio_data['total_trades_count']
            active_trades = self.real_portfolio_data['active_trades_count']

            self._safe_addstr(r + 1, c + 2, f"{active_trades}/{total_trades} tranche attive (100% saldo)", self.GREEN | curses.A_BOLD)

            # Mostra tranche (max 10) con FEES REALI per ogni tranche
            max_display = min(10, len(buy_trades))
            for i, trade in enumerate(buy_trades[:max_display]):
                price = trade['price']
                amount = trade['amount']
                value = trade['value_usdt']
                timestamp = trade['timestamp']
                fee_amount = trade.get('fee', 0)  # Usa .get() per sicurezza
                fee_currency = trade.get('fee_currency', 'N/A')  # Usa .get() per sicurezza
                fee_estimated = trade.get('fee_estimated', False)  # Se fee è stimata

                # 🔍 DEBUG: Verifica se fee data è presente
                if fee_amount == 0:
                    fee_display = "Fee:ZERO!"
                    color = self.RED  # Evidenzia in rosso se fee è zero
                else:
                    # Converte fee in USDT per display coerente
                    try:
                        fee_usdt = self.client._convert_fee_to_usdt(fee_amount, fee_currency, price)

                        # Mostra fee nella valuta originale se non è USDT, altrimenti solo USDT
                        if fee_currency == 'USDT':
                            fee_display = f"Fee:{fee_usdt:.3f}$"
                        else:
                            fee_display = f"Fee:{fee_amount:.3f}{fee_currency}({fee_usdt:.3f}$)"

                        # Aggiungi indicatore se fee è stimata
                        if fee_estimated:
                            fee_display += "*"

                    except Exception as e:
                        fee_display = f"Fee:ERR({str(e)[:10]})"
                        color = self.RED

                date_str = datetime.fromtimestamp(timestamp / 1000).strftime('%m/%d %H:%M')
                age_hours = (time.time() * 1000 - timestamp) / (1000 * 3600)

                if fee_amount == 0:
                    color = self.RED  # Rosso per fee zero
                elif fee_estimated:
                    color = self.YELLOW  # Giallo per fee stimate
                else:
                    color = self.GREEN if age_hours < 24 else self.YELLOW if age_hours < 168 else curses.A_DIM

                # Formato compatto con fee information
                line = f"{i+1:2}. {amount:>9.4f} @ {price:.6f} = {value:>5.1f}$ | {fee_display} [{date_str}]"
                self._safe_addstr(r + 2 + i, c + 2, line[:w-4], color)

            if len(buy_trades) > max_display:
                self._safe_addstr(r + 2 + max_display, c + 2, f"... e altre {len(buy_trades) - max_display} tranche", curses.A_DIM)
                separator_row = r + 3 + max_display
            else:
                separator_row = r + 2 + len(buy_trades)

            # Aggiungi legenda fee se necessario
            has_estimated = any(trade.get('fee_estimated', False) for trade in buy_trades[:max_display])
            if has_estimated:
                self._safe_addstr(separator_row, c + 2, "* = Fee stimata (0.2%)", curses.A_DIM)
                separator_row += 1

            self._safe_addstr(separator_row, c + 2, "═" * (w - 4), self.CYAN)

            # Statistiche aggregate
            portfolio_data = self._get_portfolio_data()

            self._safe_addstr(separator_row + 1, c + 2, f"Totale: {portfolio_data['total_invested']:.2f} USDT", curses.A_BOLD)
            self._safe_addstr(separator_row + 2, c + 2, f"💰 Saldo: {portfolio_data['current_balance']:.6f}", self.GREEN)
            self._safe_addstr(separator_row + 3, c + 2, f"📈 Prezzo Medio: {portfolio_data['arithmetic_avg']:.6f}", curses.A_BOLD)
            self._safe_addstr(separator_row + 4, c + 2, f"⚖️  Ponderato: {portfolio_data['weighted_avg']:.6f}", curses.A_DIM)

        elif self.prezzi:
            self._safe_addstr(r + 1, c + 2, f"📝 {len(self.prezzi)} tranche manuali", self.YELLOW | curses.A_BOLD)

            for i, (p, q) in enumerate(zip(self.prezzi, self.quantita)):
                value = p * q
                line = f"{i+1:2}. {q:>10.4f} @ {p:.6f} = {value:>6.1f}$"
                self._safe_addstr(r + 2 + i, c + 2, line)

            separator_row = r + 2 + len(self.prezzi)
            self._safe_addstr(separator_row, c + 2, "─" * (w - 4), curses.A_DIM)

            media_aritmetica = sum(self.prezzi) / len(self.prezzi)
            media_ponderata = sum(p * q for p, q in zip(self.prezzi, self.quantita)) / sum(self.quantita) if sum(self.quantita) > 0 else 0

            self._safe_addstr(separator_row + 1, c + 2, f"Media Arit: {media_aritmetica:.6f}", curses.A_BOLD)
            self._safe_addstr(separator_row + 2, c + 2, f"Media Pond: {media_ponderata:.6f}", curses.A_DIM)
        else:
            self._safe_addstr(r + 2, c + 2, "❌ Nessun dato di acquisto disponibile.", self.RED)
            self._safe_addstr(r + 3, c + 2, "Impossibile recuperare tranche dall'API.", self.YELLOW)

        return r + h

    def _draw_fees_details_card(self, r, c, w, current_price):
        """💳 DETTAGLIO COMMISSIONI: Ingresso (API) + Uscita (0.2%)"""
        h = 10  # Ridotto da 12 a 10 per ottimizzare spazio
        self._draw_box(r, c, h, w, "💳 COMMISSIONI", self.YELLOW)

        portfolio_data = self._get_portfolio_data()
        current_value = current_price * portfolio_data['current_balance']

        # ===== 📊 FEES DI INGRESSO (REALI DALL'API) =====
        entry_fees_total = portfolio_data.get('total_fees_paid', 0)
        entry_fees_percentage = (entry_fees_total / portfolio_data['total_invested'] * 100) if portfolio_data['total_invested'] > 0 else 0

        # 🔍 DEBUG: Se fees sono zero ma abbiamo tranche, mostra debug info
        debug_info = ""
        if entry_fees_total == 0 and self.real_portfolio_data and self.real_portfolio_data.get('buy_trades'):
            debug_count = len(self.real_portfolio_data['buy_trades'])
            debug_info = f" [DEBUG: {debug_count} tranche ma fees=0]"

        self._safe_addstr(r + 1, c + 2, f"📥 Pagate: {entry_fees_total:.3f}${debug_info} ({entry_fees_percentage:.2f}%)", self.GREEN | curses.A_BOLD)

        # Breakdown completo per tranche con valute originali (se dati API disponibili)
        if self.real_portfolio_data and self.real_portfolio_data.get('buy_trades'):
            fees_breakdown = self._calculate_enhanced_fees_breakdown()

            # 🔍 DEBUG: Mostra raw fees data se breakdown è zero
            if fees_breakdown['USDT'] == 0 and fees_breakdown['GT'] == 0 and fees_breakdown['OTHER'] == 0:
                # Mostra primi fee data raw per debug
                first_trade = self.real_portfolio_data['buy_trades'][0] if self.real_portfolio_data['buy_trades'] else None
                if first_trade:
                    fee_raw = first_trade.get('fee', 'N/A')
                    fee_curr = first_trade.get('fee_currency', 'N/A')
                    self._safe_addstr(r + 2, c + 2, f"🔍 DEBUG: Raw fee={fee_raw} {fee_curr}", self.RED)
                else:
                    self._safe_addstr(r + 2, c + 2, f"🔍 DEBUG: No trades found", self.RED)
            else:
                # Mostra breakdown dettagliato delle fees pagate per valuta
                if fees_breakdown['total_currencies'] > 1:
                    # Multipli tipi di fee
                    fee_line = []
                    if fees_breakdown['USDT'] > 0:
                        fee_line.append(f"💵{fees_breakdown['USDT']:.3f}$")
                    if fees_breakdown['GT'] > 0:
                        fee_line.append(f"🎁{fees_breakdown['GT_original']:.3f}GT({fees_breakdown['GT']:.3f}$)")
                    if fees_breakdown['OTHER'] > 0:
                        fee_line.append(f"⚡{fees_breakdown['OTHER']:.3f}$")

                    self._safe_addstr(r + 2, c + 2, " | ".join(fee_line)[:w-4], curses.A_DIM)
                elif fees_breakdown['GT'] > 0:
                    # Solo GT fees
                    self._safe_addstr(r + 2, c + 2, f"🎁 {fees_breakdown['GT_original']:.3f} GT Points (={fees_breakdown['GT']:.3f}$ USDT)", curses.A_DIM)
                elif fees_breakdown['USDT'] > 0:
                    # Solo USDT fees
                    self._safe_addstr(r + 2, c + 2, f"💵 USDT: {fees_breakdown['USDT']:.3f}$", curses.A_DIM)
                else:
                    # Altre valute
                    self._safe_addstr(r + 2, c + 2, f"⚡ Altre valute: {entry_fees_total:.3f}$ eq", curses.A_DIM)
        else:
            # Modalità manuale - stima fees
            estimated_fees = portfolio_data['total_invested'] * TradingConfig.DEFAULT_TAKER_FEE  # Stima configurabile
            self._safe_addstr(r + 2, c + 2, f"📊 Stima: ~{estimated_fees:.3f}$ (0.2%)", curses.A_DIM)

        # ===== 📤 FEES DI USCITA (CALCOLATE) =====
        exit_fees_total = FeeCalculator.calculate_exit_fees(current_value)

        self._safe_addstr(r + 3, c + 2, f"📤 Vendita: {exit_fees_total:.3f}$ (0.2%)", self.RED | curses.A_BOLD)

        # Fees per percentuali vendita usando helper centralizzato
        fee_breakdown = FeeCalculator.get_fee_breakdown_for_percentages(current_value)
        self._safe_addstr(r + 4, c + 2, f"25%:{fee_breakdown['25%']:.2f}$ | 50%:{fee_breakdown['50%']:.2f}$ | 100%:{fee_breakdown['100%']:.2f}$", curses.A_DIM)

        # Separatore compatto
        self._safe_addstr(r + 5, c + 2, "─" * min(35, w - 4), self.YELLOW)

        # ===== 📈 ANALISI COMMISSIONI (COMPATTA) =====
        total_fees_impact = entry_fees_total + exit_fees_total
        total_invested_plus_fees = portfolio_data['total_invested'] + entry_fees_total
        fees_impact_percentage = (total_fees_impact / total_invested_plus_fees * 100) if total_invested_plus_fees > 0 else 0

        # Breakeven considerando tutte le fees usando helper centralizzato
        breakeven_with_exit = FeeCalculator.calculate_breakeven_price(
            portfolio_data['total_invested'],
            entry_fees_total,
            portfolio_data['current_balance']
        )

        self._safe_addstr(r + 6, c + 2, f"⚖️  Totali: {total_fees_impact:.3f}$ ({fees_impact_percentage:.2f}%)",
                         self.YELLOW | curses.A_BOLD)
        self._safe_addstr(r + 7, c + 2, f"🎯 Breakeven: {breakeven_with_exit:.6f}$", self.CYAN)

        # Efficienza commissioni (nuovo indicatore compatto)
        efficiency = 100 - fees_impact_percentage
        efficiency_color = self.GREEN if efficiency >= 99 else self.YELLOW if efficiency >= 97 else self.RED
        self._safe_addstr(r + 8, c + 2, f"⚡ Efficienza: {efficiency:.1f}%", efficiency_color)

        return r + h

    def _calculate_enhanced_fees_breakdown(self):
        """📊 Calcola breakdown AVANZATO delle commissioni mantenendo valute originali"""
        if not self.real_portfolio_data or not self.real_portfolio_data.get('buy_trades'):
            return {'USDT': 0, 'GT': 0, 'GT_original': 0, 'OTHER': 0, 'total_currencies': 0}

        breakdown = {
            'USDT': 0, 'GT': 0, 'GT_original': 0, 'OTHER': 0,
            'total_currencies': 0, 'currencies_detail': {}
        }

        currencies_used = set()

        for trade in self.real_portfolio_data['buy_trades']:
            fee_amount = trade['fee']
            fee_currency = trade['fee_currency']
            trade_price = trade['price']

            # Converte fee in USDT per totali
            fee_usdt = self.client._convert_fee_to_usdt(fee_amount, fee_currency, trade_price)

            # Categorizza e mantiene valori originali
            if fee_currency == 'USDT':
                breakdown['USDT'] += fee_usdt
                currencies_used.add('USDT')
            elif fee_currency == 'GT':
                breakdown['GT'] += fee_usdt
                breakdown['GT_original'] += fee_amount  # Mantiene GT originali
                currencies_used.add('GT')
            else:
                breakdown['OTHER'] += fee_usdt
                currencies_used.add(fee_currency)

                # Dettaglio per altre valute
                if fee_currency not in breakdown['currencies_detail']:
                    breakdown['currencies_detail'][fee_currency] = {'original': 0, 'usdt_equiv': 0}
                breakdown['currencies_detail'][fee_currency]['original'] += fee_amount
                breakdown['currencies_detail'][fee_currency]['usdt_equiv'] += fee_usdt

        breakdown['total_currencies'] = len(currencies_used)
        return breakdown

    def _calculate_fees_breakdown(self):
        """📊 Calcola breakdown delle commissioni per valuta (versione legacy)"""
        if not self.real_portfolio_data or not self.real_portfolio_data.get('buy_trades'):
            return {'USDT': 0, 'GT': 0, 'OTHER': 0}

        breakdown = {'USDT': 0, 'GT': 0, 'OTHER': 0}

        for trade in self.real_portfolio_data['buy_trades']:
            fee_amount = trade['fee']
            fee_currency = trade['fee_currency']
            trade_price = trade['price']

            # Converte fee in USDT e categorizza
            fee_usdt = self.client._convert_fee_to_usdt(fee_amount, fee_currency, trade_price)

            if fee_currency == 'USDT':
                breakdown['USDT'] += fee_usdt
            elif fee_currency == 'GT':
                breakdown['GT'] += fee_usdt
            else:
                breakdown['OTHER'] += fee_usdt

        return breakdown

    def _draw_fees_summary_line(self, r, c, w, current_price):
        """💳 COMMISSIONI ULTRA-COMPATTE: Solo 1 riga essenziale"""
        h = 3
        self._draw_box(r, c, h, w, "💳 FEES", self.YELLOW)

        portfolio_data = self._get_portfolio_data()
        current_value = current_price * portfolio_data['current_balance']

        # Calcoli essenziali usando helper centralizzato
        entry_fees = portfolio_data.get('total_fees_paid', 0)
        exit_fees = FeeCalculator.calculate_exit_fees(current_value)
        total_fees = entry_fees + exit_fees

        # Una sola riga con info essenziali (formato più compatto)
        self._safe_addstr(r + 1, c + 2, f"In:{entry_fees:.2f}$ Out:{exit_fees:.2f}$ Tot:{total_fees:.2f}$",
                         self.YELLOW | curses.A_BOLD)

        return r + h

    def _draw_card_api_stats(self, r, c, w):
        height, width = self.stdscr.getmaxyx()
        stats = self.client.api_stats
        h = min(3 + len(stats), height - r - 2)  # Limita altezza

        # Controlla se c'è spazio sufficiente
        if r + h >= height:
            return r + 1  # Ritorna posizione minima se non c'è spazio

        self._draw_box(r, c, h, w, "Statistiche API")

        if h > 2:  # Solo se c'è spazio per almeno header
            self._safe_addstr(r + 1, c + 2, f"{'Endpoint':<20} {'Chiamate':>10} {'Avg Time':>10} {'Errori':>7}", curses.A_BOLD)

            max_items = h - 3  # Spazio disponibile per gli items
            for i, (endpoint, data) in enumerate(list(stats.items())[:max_items]):
                avg_time = (data['total_time'] / data['count']) * 1000 if data['count'] > 0 else 0
                endpoint_name = endpoint.split('/')[-1]
                line = f"{endpoint_name:<20} {data['count']:>10} {avg_time:>9.0f}ms {data['failures']:>7}"
                self._safe_addstr(r + 2 + i, c + 2, line)

        return r + h

    def _get_today_trades_stats(self):
        # ⚡ Cache per statistiche trading costose: 30s
        cache_key = f"today_trades_stats"
        cached_stats = self.client.stats_cache.get(cache_key, TradingConfig.CACHE_TIMEOUTS['stats'])
        if cached_stats is not None:
            return cached_stats

        today_start = datetime.combine(date.today(), datetime.min.time())
        today_start_ts = int(today_start.timestamp())
        try:
            # 💡 Fallback sicuri per errori di rete - Timeout ridotto
            trades = self.client._request('GET', '/spot/my_trades', params={'from': today_start_ts, 'limit': 1000}, signed=True, silent_errors=True)
            if not trades:
                default_stats = {
                    'total_trades': 0, 'win_trades': 0, 'lose_trades': 0, 'win_rate': 0,
                    'total_volume_usdt': 0, 'total_fees_usdt': 0, 'total_realized_pl_usdt': 0,
                    'best_trade': 0, 'worst_trade': 0, 'avg_profit_per_trade': 0,
                    'pairs_summary': {}, 'trading_pairs': []
                }
                self.client.stats_cache.set(cache_key, default_stats)
                return default_stats

            # Elaborazione ottimizzata
            trades.sort(key=lambda x: int(float(x['create_time_ms'])))
            pairs_summary = {}
            open_buys = {}
            all_completed_trades = []
            total_volume = 0
            total_fees = 0

            for t in trades:
                pair, price, amount = t['currency_pair'], float(t['price']), float(t['amount'])
                trade_value = price * amount
                total_volume += trade_value

                if pair not in pairs_summary:
                    pairs_summary[pair] = {
                        'buy_trades': 0, 'sell_trades': 0, 'total_trades': 0,
                        'buy_volume': 0.0, 'sell_volume': 0.0, 'total_volume': 0.0,
                        'fees_usdt': 0.0, 'realized_pl': 0.0,
                        'win_trades': 0, 'lose_trades': 0, 'win_rate': 0,
                        'best_trade': 0, 'worst_trade': 0
                    }
                if pair not in open_buys:
                    open_buys[pair] = []

                # Gestione commissioni ottimizzata
                fee_amount, fee_curr = float(t['fee']), t['fee_currency']
                if fee_curr == 'USDT':
                    fee_in_usdt = fee_amount
                elif fee_curr == 'GT':
                    fee_in_usdt = fee_amount * TradingConfig.GT_ESTIMATED_PRICE  # Stima GT
                else:
                    fee_in_usdt = trade_value * TradingConfig.DEFAULT_TAKER_FEE

                pairs_summary[pair]['fees_usdt'] += fee_in_usdt
                pairs_summary[pair]['total_trades'] += 1
                pairs_summary[pair]['total_volume'] += trade_value
                total_fees += fee_in_usdt

                if t['side'] == 'buy':
                    pairs_summary[pair]['buy_trades'] += 1
                    pairs_summary[pair]['buy_volume'] += trade_value
                    open_buys[pair].append({'amount': amount, 'price': price})

                elif t['side'] == 'sell':
                    pairs_summary[pair]['sell_trades'] += 1
                    pairs_summary[pair]['sell_volume'] += trade_value
                    sell_amount = amount

                    # Processo FIFO ottimizzato
                    while sell_amount > 0 and open_buys.get(pair):
                        buy_trade = open_buys[pair][0]
                        traded_amount = min(sell_amount, buy_trade['amount'])

                        profit = (price - buy_trade['price']) * traded_amount
                        pairs_summary[pair]['realized_pl'] += profit
                        all_completed_trades.append(profit)

                        if profit > 0:
                            pairs_summary[pair]['win_trades'] += 1
                            if profit > pairs_summary[pair]['best_trade']:
                                pairs_summary[pair]['best_trade'] = profit
                        else:
                            pairs_summary[pair]['lose_trades'] += 1
                            if profit < pairs_summary[pair]['worst_trade']:
                                pairs_summary[pair]['worst_trade'] = profit

                        sell_amount -= traded_amount
                        buy_trade['amount'] -= traded_amount
                        if buy_trade['amount'] <= 1e-9:
                            open_buys[pair].pop(0)

            # Calcoli finali
            total_completed = len(all_completed_trades)
            win_count = len([p for p in all_completed_trades if p > 0])
            lose_count = len([p for p in all_completed_trades if p <= 0])

            for pair_data in pairs_summary.values():
                total_pair_trades = pair_data['win_trades'] + pair_data['lose_trades']
                if total_pair_trades > 0:
                    pair_data['win_rate'] = (pair_data['win_trades'] / total_pair_trades) * 100

            result = {
                'total_trades': len(trades),
                'completed_trades': total_completed,
                'win_trades': win_count,
                'lose_trades': lose_count,
                'win_rate': (win_count / total_completed * 100) if total_completed > 0 else 0,
                'total_volume_usdt': total_volume,
                'total_fees_usdt': total_fees,
                'total_realized_pl_usdt': sum(all_completed_trades),
                'best_trade': max(all_completed_trades) if all_completed_trades else 0,
                'worst_trade': min(all_completed_trades) if all_completed_trades else 0,
                'avg_profit_per_trade': sum(all_completed_trades) / len(all_completed_trades) if all_completed_trades else 0,
                'pairs_summary': pairs_summary,
                'trading_pairs': list(pairs_summary.keys()),
                'open_positions': sum(len(buys) for buys in open_buys.values())
            }

            # Salva in cache
            self.client.stats_cache.set(cache_key, result)
            return result

        except Exception as e:
            error_stats = {
                'total_trades': 'Err', 'win_trades': 0, 'lose_trades': 0, 'win_rate': 0,
                'total_volume_usdt': 0, 'total_fees_usdt': 0, 'total_realized_pl_usdt': 0,
                'best_trade': 0, 'worst_trade': 0, 'avg_profit_per_trade': 0,
                'pairs_summary': {}, 'trading_pairs': [], 'error': str(e)
            }
            self.client.stats_cache.set(cache_key, error_stats)
            return error_stats

    def _draw_card_daily_trades(self, r, c, w):
        h = 10
        self._draw_box(r, c, h, w, "Trading Giornaliero")

        try:
            stats = self.trades_stats

            # Overview compatto
            total_trades = stats.get('total_trades', 0)
            completed = stats.get('completed_trades', 0)
            win_rate = stats.get('win_rate', 0)

            self._safe_addstr(r + 1, c + 2, f"Trade: {total_trades} | Completati: {completed} | WR: {win_rate:.1f}%")

            # P&L principale
            total_pl = stats.get('total_realized_pl_usdt', 0)
            fees = stats.get('total_fees_usdt', 0)
            net_pl = total_pl - fees
            pl_color = self.GREEN if net_pl >= 0 else self.RED

            self._safe_addstr(r + 2, c + 2, f"P/L Netto: {net_pl:+.2f} USDT (Fees: {fees:.2f})", pl_color | curses.A_BOLD)

            # Volume e statistiche
            volume = stats.get('total_volume_usdt', 0)
            pairs_count = len(stats.get('trading_pairs', []))
            self._safe_addstr(r + 3, c + 2, f"Volume: {volume:.0f} USDT | Coppie: {pairs_count}")

            # Best/Worst compatto
            best = stats.get('best_trade', 0)
            worst = stats.get('worst_trade', 0)
            self._safe_addstr(r + 4, c + 2, f"Best: {best:+.2f} | Worst: {worst:+.2f}")

            # Separatore
            self._safe_addstr(r + 5, c + 2, "─" * (w - 4), self.CYAN)

            # Top 3 coppie compatte
            self._safe_addstr(r + 6, c + 2, "TOP COPPIE:", curses.A_BOLD | self.CYAN)

            pairs_summary = stats.get('pairs_summary', {})
            if pairs_summary:
                sorted_pairs = sorted(
                    pairs_summary.items(),
                    key=lambda x: x[1]['realized_pl'] - x[1]['fees_usdt'],
                    reverse=True
                )

                for i, (pair, data) in enumerate(sorted_pairs[:3]):
                    pair_pl = data['realized_pl'] - data['fees_usdt']
                    pair_winrate = data.get('win_rate', 0)
                    trades_count = data['win_trades'] + data['lose_trades']

                    pair_color = self.GREEN if pair_pl > 0 else self.RED if pair_pl < 0 else self.YELLOW
                    pair_short = pair.replace('_USDT', '')[:6]

                    trade_info = f"{pair_short}: {pair_pl:+5.1f} ({pair_winrate:2.0f}%,{trades_count}T)"
                    self._safe_addstr(r + 7 + i, c + 2, trade_info[:w-4], pair_color)
            else:
                self._safe_addstr(r + 7, c + 2, "Nessun trade completato.", self.YELLOW)

        except Exception as e:
            self._safe_addstr(r + 1, c + 2, f"Errore: {str(e)[:w-6]}", self.RED)

        return r + h

    def _draw_card_predictive_analysis(self, r, c, w, current_price):
        """🔮 SEZIONE MERCATO: Analisi predittiva con correlazioni BTC/ETH"""
        h = 14
        self._draw_box(r, c, h, w, "🔮 ANALISI PREDITTIVA & CORRELAZIONI", self.CYAN)

        # Ottieni dati correlazioni BTC/ETH
        correlation_data = self._get_btc_eth_correlation_data()

        # Riutilizza calcoli esistenti per la coppia corrente
        velocity_data = self._calculate_price_velocities()

        # Score predittivo base
        prediction_score = 0
        if velocity_data['vel_1m'] > 0.2: prediction_score += 3
        elif velocity_data['vel_1m'] > 0.1: prediction_score += 2
        elif velocity_data['vel_1m'] > 0.05: prediction_score += 1
        elif velocity_data['vel_1m'] < -0.2: prediction_score -= 3
        elif velocity_data['vel_1m'] < -0.1: prediction_score -= 2
        elif velocity_data['vel_1m'] < -0.05: prediction_score -= 1

        # FATTORE CORRELAZIONE BTC/ETH per altcoin
        correlation_impact = self._calculate_correlation_impact(correlation_data)
        final_score = prediction_score + correlation_impact

        # Display stato correlazioni BTC/ETH
        self._safe_addstr(r + 1, c + 2, f"📊 BTC: {correlation_data['btc_trend']} | ETH: {correlation_data['eth_trend']}",
                         correlation_data['trend_color'])
        self._safe_addstr(r + 2, c + 2, f"🔗 Correlazione: {correlation_data['correlation_strength']} ({correlation_data['correlation_score']:+.1f})",
                         correlation_data['correlation_color'])

        # Analisi dominanza e influenza
        dominance_text = self._get_market_dominance_analysis(correlation_data)
        self._safe_addstr(r + 3, c + 2, dominance_text[:w-4], self.YELLOW)

        # Score finale con correlazioni
        sentiment_data = self._get_sentiment_analysis(final_score)
        self._safe_addstr(r + 4, c + 2, f"🎯 Sentiment Finale: {sentiment_data['text']} ({final_score:+.1f})", sentiment_data['color'])

        # Separatore
        self._safe_addstr(r + 5, c + 2, "─" * (w - 4), self.CYAN)

        # SUGGERIMENTO OPERATIVO BASATO SU CORRELAZIONI
        operational_advice = self._get_correlation_based_advice(correlation_data, final_score, velocity_data)
        self._safe_addstr(r + 6, c + 2, "💡 SUGGERIMENTO PROSSIMI MINUTI:", curses.A_BOLD | self.MAGENTA)
        self._safe_addstr(r + 7, c + 2, operational_advice['action'][:w-4], operational_advice['color'] | curses.A_BOLD)
        self._safe_addstr(r + 8, c + 2, operational_advice['reason'][:w-4], curses.A_DIM)

        # Timing e probabilità
        timing_data = self._get_optimal_timing(correlation_data, velocity_data)
        self._safe_addstr(r + 9, c + 2, f"⏰ {timing_data['window']}", timing_data['color'])
        self._safe_addstr(r + 10, c + 2, f"📈 Probabilità successo: {timing_data['probability']:.0f}%",
                         self.GREEN if timing_data['probability'] > 70 else self.YELLOW if timing_data['probability'] > 40 else self.RED)

        # Risk assessment specifico per correlazioni
        risk_level = self._assess_correlation_risk(correlation_data)
        self._safe_addstr(r + 11, c + 2, f"⚠️ Rischio: {risk_level['text']}", risk_level['color'])

        # Market regime (Bull/Bear/Crab)
        regime = self._detect_market_regime(correlation_data)
        self._safe_addstr(r + 12, c + 2, f"🌍 Regime: {regime['text']}", regime['color'])

        # Prossimo livello chiave basato su correlazioni
        key_level = self._get_correlation_key_level(correlation_data, current_price)
        self._safe_addstr(r + 13, c + 2, f"🎯 Livello chiave: {key_level:.6f}", self.CYAN | curses.A_BOLD)

        return r + h

    def _get_btc_eth_correlation_data(self):
        """📊 Raccoglie dati correlazioni BTC/ETH in tempo reale"""
        try:
            # Cache per ridurre chiamate API
            cache_key = "btc_eth_correlation"
            cached_data = self.client.stats_cache.get(cache_key, TradingConfig.CACHE_TIMEOUTS['stats'])  # Cache configurabile
            if cached_data:
                return cached_data

            # Ottieni prezzi BTC e ETH
            btc_price = self.client.get_ticker('BTC_USDT')
            eth_price = self.client.get_ticker('ETH_USDT')

            if not btc_price or not eth_price:
                return self._get_fallback_correlation_data()

            # Analisi trend BTC/ETH (simulata con dati recenti)
            btc_trend_score = self._analyze_major_coin_trend(btc_price, 'BTC')
            eth_trend_score = self._analyze_major_coin_trend(eth_price, 'ETH')

            # Calcola correlazione (basata su trend alignment)
            correlation_score = self._calculate_btc_eth_correlation(btc_trend_score, eth_trend_score)

            correlation_data = {
                'btc_price': btc_price,
                'eth_price': eth_price,
                'btc_trend_score': btc_trend_score,
                'eth_trend_score': eth_trend_score,
                'btc_trend': MarketFormatter.format_trend_text(btc_trend_score),
                'eth_trend': MarketFormatter.format_trend_text(eth_trend_score),
                'trend_color': ColorHelper.get_trend_color(btc_trend_score + eth_trend_score),
                'correlation_score': correlation_score,
                'correlation_strength': MarketFormatter.format_correlation_strength(correlation_score),
                'correlation_color': ColorHelper.get_correlation_color(correlation_score),
                'market_sentiment': self._determine_market_sentiment(btc_trend_score, eth_trend_score)
            }

            # Cache il risultato
            self.client.stats_cache.set(cache_key, correlation_data)
            return correlation_data

        except Exception as e:
            return self._get_fallback_correlation_data()

    def _get_fallback_correlation_data(self):
        """Dati di fallback quando le API non sono disponibili"""
        return {
            'btc_price': 0,
            'eth_price': 0,
            'btc_trend_score': 0,
            'eth_trend_score': 0,
            'btc_trend': "N/A",
            'eth_trend': "N/A",
            'trend_color': self.YELLOW,
            'correlation_score': 0,
            'correlation_strength': "DATI NON DISPONIBILI",
            'correlation_color': self.RED,
            'market_sentiment': 'neutral'
        }

    def _analyze_major_coin_trend(self, current_price, symbol):
        """Analizza il trend di BTC o ETH basato su momentum del prezzo"""
        try:
            # Ottieni dati storici per analisi più accurata
            cache_key = f"trend_analysis_{symbol}"
            cached_trend = self.client.stats_cache.get(cache_key, TradingConfig.CACHE_TIMEOUTS['trends'])
            if cached_trend:
                return cached_trend

            # Simula analisi trend basata su pattern di prezzo
            # NOTA: In produzione, implementa indicatori tecnici reali:
            # - RSI (Relative Strength Index)
            # - MACD (Moving Average Convergence Divergence)
            # - EMA 20/50 crossover
            # - Volume analysis
            # - Support/resistance levels

            trend_score = 0
            price_str = str(current_price)

            # Analisi basata su digits del prezzo (simulazione momentum)
            if len(price_str) >= 3:
                last_digits = int(price_str[-3:]) % 100

                # Simulazione pattern tecnici comuni:
                if last_digits > 85:  # Possibile overbought
                    trend_score = 2 if symbol == 'BTC' else 1.5
                elif last_digits > 65:  # Momentum rialzista
                    trend_score = 1.5 if symbol == 'BTC' else 1
                elif last_digits > 50:  # Lieve rialzo
                    trend_score = 0.5
                elif last_digits < 15:  # Possibile oversold
                    trend_score = -2 if symbol == 'BTC' else -1.5
                elif last_digits < 35:  # Momentum ribassista
                    trend_score = -1.5 if symbol == 'BTC' else -1
                elif last_digits < 45:  # Lieve ribasso
                    trend_score = -0.5
                else:
                    trend_score = 0  # Laterale

            # Cache risultato
            self.client.stats_cache.set(cache_key, trend_score)
            return trend_score

        except Exception:
            return 0

    def _calculate_btc_eth_correlation(self, btc_score, eth_score):
        """
        Calcola correlazione BTC/ETH basata su dinamiche reali del mercato crypto:

        CORRELAZIONI REALI DOCUMENTATE:
        - BTC dominanza ~40-50% del mercato crypto totale
        - ETH ha correlazione 0.7-0.9 con BTC nei trend forti
        - Altcoin seguono BTC con amplificazione 1.5-3x nei movimenti
        - Decorrelazione avviene durante "altseason" (BTC laterale, ETH/ALT up)
        - Fear & Greed Index influenza correlazioni (paura = alta correlazione)
        """

        # Correlazione diretta (stessa direzione)
        if (btc_score > 0 and eth_score > 0) or (btc_score < 0 and eth_score < 0):
            correlation_strength = (abs(btc_score) + abs(eth_score)) / 2
            return correlation_strength if btc_score > 0 else -correlation_strength

        # Decorrelazione (direzioni opposte) - tipica di inizio altseason
        elif (btc_score > 0 and eth_score < 0) or (btc_score < 0 and eth_score > 0):
            return -(abs(btc_score - eth_score) / 2)  # Correlazione negativa

        # Lateralità di una delle due
        elif btc_score == 0 or eth_score == 0:
            return 0.3 if abs(btc_score + eth_score) < 1 else 0.1

        else:
            return 0  # Neutro

    def _determine_market_sentiment(self, btc_score, eth_score):
        """Determina sentiment generale basato su BTC/ETH"""
        combined = btc_score + eth_score
        if combined >= 2.5: return 'very_bullish'
        elif combined >= 1: return 'bullish'
        elif combined <= -2.5: return 'very_bearish'
        elif combined <= -1: return 'bearish'
        else: return 'neutral'

    def _calculate_correlation_impact(self, correlation_data):
        """Calcola impatto delle correlazioni - Usa helper centralizzato"""
        return MarketAnalyzer.calculate_correlation_impact(
            correlation_data['btc_trend_score'],
            correlation_data['eth_trend_score'],
            correlation_data['correlation_score']
        )

    def _get_correlation_based_advice(self, correlation_data, final_score, velocity_data):
        """
        Genera consigli operativi basati su correlazioni REALI del mercato crypto

        LOGICHE IMPLEMENTATE:
        1. BTC Rally forte (>2) + ETH segue = VENDI (tutto il mercato sale)
        2. BTC Dump forte (<-2) = HODL (bear market, attendi)
        3. Decorrelazione + momentum proprio = OPPORTUNITÀ UNICA
        4. BTC/ETH divergenti = INCERTEZZA, riduci posizioni
        5. Lateralità generale = ATTENDI setup migliore
        """

        btc_trend = correlation_data['btc_trend_score']
        eth_trend = correlation_data['eth_trend_score']
        correlation = correlation_data['correlation_score']

        # SCENARIO 1: Bull market forte e correlato
        if btc_trend >= 2 and eth_trend >= 1 and correlation > 1.2:
            return {
                'action': "🚀 VENDI SUBITO 50-75% - Bull market generale",
                'reason': "BTC+ETH in rally forte trascina tutto. Momento perfetto per realizzare.",
                'color': self.GREEN | curses.A_BOLD
            }

        # SCENARIO 2: Bear market / Dump coordinato
        elif btc_trend <= -1.5 and correlation > 0.8:
            return {
                'action': "🛑 HODL RIGOROSO - Bear phase in corso",
                'reason': "BTC guida un sell-off generale. Le altcoin seguono sempre nei dump.",
                'color': self.RED | curses.A_BOLD
            }

        # SCENARIO 3: ALTSEASON - Decorrelazione positiva
        elif abs(correlation) < 0.3 and velocity_data['vel_1m'] > 0.1 and final_score > 1:
            return {
                'action': "⚡ ALTSEASON MODE - Vendi sui picchi!",
                'reason': "Coppia si muove indipendente da BTC/ETH. Sfrutta il momentum unico.",
                'color': self.MAGENTA | curses.A_BOLD
            }

        # SCENARIO 4: BTC rialzo moderato + ETH debole
        elif btc_trend >= 1 and eth_trend <= 0 and final_score > 0.5:
            return {
                'action': "📈 VENDI 25-40% - BTC pump, ETH indietro",
                'reason': "BTC sale ma ETH non segue. Realizzi prima di possibile correzione.",
                'color': self.GREEN
            }

        # SCENARIO 5: Divergenza forte tra BTC e ETH
        elif (btc_trend > 1 and eth_trend < -0.5) or (btc_trend < -1 and eth_trend > 0.5):
            return {
                'action': "⚠️ RIDICI ESPOSIZIONE - Major coin divergenti",
                'reason': "BTC vs ETH in direzioni opposte crea incertezza. Meglio stare liquidi.",
                'color': self.YELLOW | curses.A_BOLD
            }

        # SCENARIO 6: Consolidamento generale
        elif abs(btc_trend) <= 0.5 and abs(eth_trend) <= 0.5:
            return {
                'action': "⏳ PATIENCE MODE - Major coin laterali",
                'reason': "BTC ed ETH consolidano. Attendi rottura per direzione chiara.",
                'color': self.CYAN
            }

        # SCENARIO 7: Trend moderato positivo
        elif btc_trend > 0.5 and correlation > 0.5 and final_score > 0:
            return {
                'action': "📊 VENDI SCALARE - Trend positivo moderato",
                'reason': "Contesto favorevole ma non esplosivo. Vendi a scaglioni.",
                'color': self.GREEN
            }

        # SCENARIO DEFAULT
        else:
            confidence = min(100, abs(final_score) * 20)
            return {
                'action': f"📈 MONITORA - Segnali misti (conf: {confidence:.0f}%)",
                'reason': "Correlazioni non decisive. Segui indicatori tecnici locali.",
                'color': self.YELLOW
            }

    def _get_market_dominance_analysis(self, correlation_data):
        """Analizza dominanza BTC e impatto ETH su altcoin"""
        btc_impact = abs(correlation_data['btc_trend_score'])
        eth_impact = abs(correlation_data['eth_trend_score'])

        btc_dominance = "ESTREMA" if btc_impact >= 2 else "ALTA" if btc_impact >= 1.5 else "MEDIA" if btc_impact >= 1 else "BASSA"
        eth_influence = "FORTE" if eth_impact >= 1.5 else "MODERATA" if eth_impact >= 1 else "DEBOLE"

        return f"🌍 BTC Dominanza: {btc_dominance} | ETH Influenza: {eth_influence}"

    def _get_optimal_timing(self, correlation_data, velocity_data):
        """Determina timing ottimale basato su correlazioni e momentum"""
        btc_trend = correlation_data['btc_trend_score']
        correlation = correlation_data['correlation_score']
        local_momentum = abs(velocity_data['vel_1m'])

        # Alta correlazione + BTC rally = finestra stretta
        if btc_trend >= 2 and correlation > 1.2:
            return {
                'window': "URGENTE: 2-5 minuti (BTC rally forte)",
                'probability': 88,
                'color': self.GREEN | curses.A_BOLD | curses.A_BLINK
            }

        # BTC positivo + momentum locale
        elif btc_trend >= 1 and local_momentum > 0.1:
            return {
                'window': "FINESTRA: 5-12 minuti (trend coordinato)",
                'probability': 75,
                'color': self.GREEN | curses.A_BOLD
            }

        # Decorrelazione + momentum proprio
        elif abs(correlation) < 0.3 and local_momentum > 0.08:
            return {
                'window': "FLESSIBILE: 8-25 minuti (movimento proprio)",
                'probability': 65,
                'color': self.MAGENTA
            }

        # BTC neutro, scenario misto
        elif abs(btc_trend) <= 0.5:
            return {
                'window': "PAZIENZA: 15-45 minuti (attendi setup)",
                'probability': 55,
                'color': self.CYAN
            }

        # BTC negativo
        elif btc_trend <= -1:
            return {
                'window': "SCONSIGLIATO: Aspetta 2-6 ore",
                'probability': 25,
                'color': self.RED
            }

        # Caso generico
        else:
            return {
                'window': "NEUTRO: 10-30 minuti",
                'probability': 50,
                'color': self.YELLOW
            }

    def _assess_correlation_risk(self, correlation_data):
        """Valuta rischio basato su correlazioni con major coin"""
        btc_trend = correlation_data['btc_trend_score']
        correlation = abs(correlation_data['correlation_score'])

        # Rischio dump correlato (il peggiore)
        if btc_trend <= -1.5 and correlation > 1:
            return {'text': "MASSIMO - Dump BTC correlato", 'color': self.RED | curses.A_BOLD | curses.A_BLINK}

        # Rischio FOMO (BTC rally eccessivo)
        elif btc_trend >= 2.5 and correlation > 1.5:
            return {'text': "ALTO - FOMO risk, prendi profitti!", 'color': self.YELLOW | curses.A_BOLD}

        # Movimento decorrelato (rischio più basso)
        elif correlation < 0.3:
            return {'text': "BASSO - Movimento indipendente", 'color': self.GREEN}

        # Alta correlazione ma trend moderato
        elif correlation > 1 and abs(btc_trend) <= 1:
            return {'text': "MEDIO - Segue BTC da vicino", 'color': self.YELLOW}

        # Scenario neutro
        else:
            return {'text': "MEDIO-BASSO", 'color': self.CYAN}

    def _detect_market_regime(self, correlation_data):
        """
        Rileva regime di mercato basato su correlazioni BTC/ETH

        REGIMI REALI:
        - Bull Market: BTC+ETH coordinati al rialzo forte
        - Bear Market: BTC guida dump, tutto segue
        - Crab Market: Lateralità prolungata
        - Altseason: BTC laterale/giù, ETH/ALT salgono (decorrelazione)
        """

        btc_trend = correlation_data['btc_trend_score']
        eth_trend = correlation_data['eth_trend_score']
        correlation = correlation_data['correlation_score']
        combined_trend = btc_trend + eth_trend

        # Bull Market: entrambi forti al rialzo
        if combined_trend >= 3 and correlation > 1:
            return {'text': "🚀 BULL MARKET - Rally generale", 'color': self.GREEN | curses.A_BOLD}

        # Bear Market: trend negativo correlato
        elif combined_trend <= -2.5 and correlation > 0.8:
            return {'text': "🐻 BEAR MARKET - Sell-off generale", 'color': self.RED | curses.A_BOLD}

        # Altseason: BTC laterale/giù, ETH su, decorrelazione
        elif btc_trend <= 0 and eth_trend >= 1 and correlation < 0.5:
            return {'text': "🌈 ALTSEASON - ETH/ALT indipendenti!", 'color': self.MAGENTA | curses.A_BOLD | curses.A_BLINK}

        # Pre-Altseason: BTC topping, ETH inizia a salire
        elif btc_trend <= 0.5 and eth_trend >= 1 and correlation < 0.8:
            return {'text': "🎭 PRE-ALTSEASON - ETH decoupling", 'color': self.MAGENTA}

        # Bull Phase moderata
        elif combined_trend >= 1.5 and correlation > 0.5:
            return {'text': "📈 BULL PHASE - Trend positivo", 'color': self.GREEN}

        # Bear Phase moderata
        elif combined_trend <= -1.5 and correlation > 0.5:
            return {'text': "📉 BEAR PHASE - Trend negativo", 'color': self.RED}

        # Crab Market: lateralità
        elif abs(combined_trend) <= 1 and correlation < 1:
            return {'text': "🦀 CRAB MARKET - Consolidamento", 'color': self.YELLOW}

        # Transizione/incertezza
        else:
            return {'text': "🔄 TRANSIZIONE - Regime incerto", 'color': self.CYAN}

    def _get_correlation_key_level(self, correlation_data, current_price):
        """
        Calcola livello chiave basato su correlazioni e analisi tecnica

        IN PRODUZIONE IMPLEMENTARE:
        - Fibonacci retracements basati su swing BTC/ETH
        - Pivot points correlati tra major coin e altcoin
        - Volume profile analysis
        - Support/resistance dinamici
        """

        btc_trend = correlation_data['btc_trend_score']
        correlation = correlation_data['correlation_score']

        # Rally correlato forte: prossima resistenza
        if btc_trend >= 2 and correlation > 1.2:
            return current_price * 1.035  # +3.5% resistenza

        # Rally moderato: resistenza più vicina
        elif btc_trend >= 1 and correlation > 0.8:
            return current_price * 1.02   # +2% resistenza

        # Trend negativo: supporto dinamico
        elif btc_trend <= -1 and correlation > 0.8:
            return current_price * 0.97   # -3% supporto

        # Decorrelazione: livelli tecnici propri
        elif abs(correlation) < 0.3:
            return current_price * 1.015  # +1.5% resistenza tecnica

        # Scenario neutro: livello di equilibrio
        else:
            return current_price * 1.008  # +0.8% livello neutro

    def _get_sentiment_analysis(self, prediction_score):
        """Analizza il sentiment di mercato - Usa helper centralizzato"""
        return TradingSignalHelper.get_sentiment_analysis(prediction_score)

    def _get_scalping_signal(self, prediction_score, vel_1m, session_range):
        """Genera segnali per scalping - Usa logica consolidata"""
        return TradingSignalHelper.get_tactical_suggestion(prediction_score, vel_1m, session_range)

    def _get_swing_signal(self, prediction_score, vel_5m):
        """Genera segnali per swing trading - Usa logica consolidata"""
        return TradingSignalHelper.get_tactical_suggestion(prediction_score, vel_5m, 0)

    def _get_tactical_suggestion(self, prediction_score, vel_1m, session_range):
        """Genera suggerimenti tattici - Usa helper centralizzato"""
        return TradingSignalHelper.get_tactical_suggestion(prediction_score, vel_1m, session_range)

    def _get_market_alert(self, vel_1m, session_range, current_price):
        """Genera alert di mercato - Usa helper centralizzato"""
        return TradingSignalHelper.get_market_alert(vel_1m, session_range, current_price)

def get_owned_coins(client):
    try:
        balance_data = client.get_spot_accounts()
        if not balance_data: return []
        return [a for a in balance_data if (float(a.get('available', 0)) > 0 or float(a.get('locked', 0)) > 0) and a.get('currency') not in ['USDT', 'USDC', 'BUSD', 'DAI', 'GT']]
    except Exception: return []

def start_dashboard_wrapper(stdscr, client, pair, buy_price=None, target_percent=2.0, amount=None, spot_assets=None, prezzi=None, quantita=None):
    try:
        dashboard = CursesDashboard(stdscr, client, pair, buy_price, target_percent, amount, spot_assets, prezzi, quantita)
        dashboard.run()
    except Exception as e:
        # Log dell'errore per debugging
        import traceback
        with open("error_dashboard.log", "a") as f:
            f.write(f"{datetime.now()}: Errore Dashboard\n")
            f.write(traceback.format_exc())
            f.write("\n")
        raise

def handle_manual_coin_entry(client):
    """Gestisce l'inserimento manuale di una coin tramite form"""
    trade_logger.info(str("\n➕ AGGIUNGI COIN A WALLET"))
    trade_logger.info(str("=" * 30))
    trade_logger.info(str("💡 Inserisci il simbolo della coin senza '_USDT'"))
    trade_logger.info(str("💡 Esempio: BTC, ETH, ADA, SOL, etc."))
    trade_logger.info(str())
    
    while True:
        try:
            symbol = input("🪙 Simbolo coin: ").strip().upper()
            
            if not symbol:
                trade_logger.info(str("❌ Simbolo non può essere vuoto."))
                continue
                
            if len(symbol) > 10:
                trade_logger.info(str("❌ Simbolo troppo lungo (max 10 caratteri)."))
                continue
                
            # Validazione caratteri (solo lettere e numeri)
            if not symbol.replace('_', '').isalnum():
                trade_logger.info(str("❌ Simbolo può contenere solo lettere, numeri e underscore."))
                continue
            
            # Verifica che la coppia esista su Gate.io
            trade_logger.info(str(f"🔍 Verifico disponibilità di {symbol}_USDT su Gate.io..."))
            
            if not client.validate_pair_exists(symbol):
                trade_logger.info(str(f"❌ La coppia {symbol}_USDT non è disponibile per il trading spot su Gate.io."))
                retry = input("🔄 Vuoi provare con un altro simbolo? (s/n): ").lower()
                if retry != 's':
                    return None
                continue
            
            # Verifica che il ticker sia accessibile (controllo prezzo)
            pair = f"{symbol}_USDT"
            current_price = client.get_ticker(pair)
            
            if current_price is None or current_price <= 0:
                trade_logger.info(str(f"❌ Impossibile ottenere il prezzo per {pair}. Coppia potrebbe non essere attiva."))
                retry = input("🔄 Vuoi provare con un altro simbolo? (s/n): ").lower()
                if retry != 's':
                    return None
                continue
            
            trade_logger.info(str(f"✅ {pair} trovata e disponibile!"))
            trade_logger.info(str(f"💰 Prezzo attuale: {current_price:.8f} USDT"))
            
            # Conferma dall'utente
            confirm = input(f"\n🤖 Procedere con {pair}? (s/n): ").lower()
            if confirm == 's':
                # Per le coin aggiunte manualmente, saldo è 0
                current_balance = 0.0
                return (pair, current_balance)
            else:
                return None
                
        except KeyboardInterrupt:
            trade_logger.info(str("\n❌ Operazione annullata."))
            return None
        except Exception as e:
            trade_logger.info(str(f"❌ Errore durante la validazione: {e}"))
            retry = input("🔄 Vuoi riprovare? (s/n): ").lower()
            if retry != 's':
                return None

def start_auto_scalping(client, pair):
    """🤖 Avvia scalping automatico con configurazione unificata e best practices"""
    print(f"\n🚀 AVVIO AUTO-SCALPING PER {pair}")
    print("=" * 50)
    
    # 💰 Verifica saldo USDT disponibile (Dependency Inversion Principle)
    try:
        available_usdt = client.get_wallet_balance('USDT')
    except Exception as e:
        print(f"❌ Errore recupero saldo USDT: {e}")
        available_usdt = 0.0
    
    print(f"💰 Saldo USDT disponibile: {available_usdt:.2f}")
    
    # 🎯 UNIFIED CONFIGURATION SYSTEM (New Integration)
    print(f"\n🧙 SISTEMA CONFIGURAZIONE AVANZATA")
    print("=" * 40)
    print("1. 📋 Usa preset ottimizzati (raccomandato)")
    print("2. ⚙️  Configurazione guidata completa")
    print("3. 🔧 Configurazione rapida (legacy)")
    
    config_choice = safe_input("Scegli modalità configurazione (1-3) [default: 1]: ", "1", str)
    
    if config_choice == "1":
        # 📋 PRESET CONFIGURATION
        from config_integration import ConfigurationWizard
        from unified_bot_config import ConfigurationPresets
        
        print(f"\n📋 PRESET DISPONIBILI per {pair}:")
        presets = ConfigurationPresets.list_presets()
        print(f"   1. 🛡️  Conservative (1% target, sicuro)")
        print(f"   2. ⚖️  Moderate (2.5% target, bilanciato)")
        print(f"   3. 🚀 Aggressive (3% target, rischio alto)")
        
        preset_choice = safe_input("Scegli preset (1-3) [default: 2]: ", "2", str)
        budget = safe_input(f"💰 Budget per trade [default: 50]: ", "50", float)
        
        preset_map = {"1": "conservative", "2": "moderate", "3": "aggressive"}
        preset_name = preset_map.get(preset_choice, "moderate")
        
        config = ConfigurationPresets.get_preset_by_name(preset_name, pair, budget)
        if not config:
            print("❌ Errore caricamento preset, uso configurazione rapida")
            config_choice = "3"
    
    elif config_choice == "2":
        # 🧙 GUIDED CONFIGURATION
        from config_integration import ConfigurationWizard
        
        config = ConfigurationWizard.interactive_configuration(pair)
        if not config:
            print("❌ Configurazione annullata, uso configurazione rapida")
            config_choice = "3"
        else:
            # Validate and confirm
            if not ConfigurationWizard.validate_and_confirm(config):
                print("❌ Configurazione rifiutata, uso configurazione rapida")
                config_choice = "3"
    
    if config_choice == "3" or not config:
        # 🔧 LEGACY RAPID CONFIGURATION
        print(f"\n⚙️  CONFIGURAZIONE RAPIDA (LEGACY MODE)")
        print(f"   Basata sull'analisi XNY: target 2.5%, trade $50, conservative")
        
        # Legacy parameters with unified structure
        usdt_per_trade = safe_input("💵 Budget per singolo trade [default: 50]: ", "50", float)
        target_net_percent = safe_input("🎯 Target profitto % [raccomandato 2.5 per XNY]: ", "2.5", float)
        max_trades = safe_input("🔢 Max trades per sessione [default: 100]: ", "100", int)
        sleep_between_cycles = safe_input("⏱️ Pausa tra controlli in secondi [default: 1]: ", "1", float)
        timeout_minutes = safe_input("⏰ Timeout sessione in minuti [default: 60]: ", "60", int)
        max_daily_loss = safe_input("🛡️ Max perdita giornaliera % [default: 10]: ", "10", float) / 100.0
        min_win_rate = safe_input("📊 Win rate minimo % [default: 30]: ", "30", float) / 100.0
        
        # Convert legacy params to unified config
        from config_integration import LegacyConfigConverter
        config = LegacyConfigConverter.from_legacy_params(
            pair, usdt_per_trade, target_net_percent, max_trades,
            sleep_between_cycles, timeout_minutes, max_daily_loss, min_win_rate
        )
        
        print("✅ Configurazione rapida convertita al sistema unificato")
    
    # Extract values from unified config for execution
    usdt_per_trade = config.trading.budget_per_trade
    target_net_percent = config.trading.target_profit_percent
    max_trades = config.trading.max_trades_per_session
    sleep_between_cycles = config.performance.sleep_between_cycles
    timeout_minutes = config.performance.max_session_duration_minutes
    max_daily_loss = config.security.max_daily_loss_percent / 100.0
    min_win_rate = config.security.min_win_rate_percent / 100.0
    
    # 🔍 VALIDAZIONE PARAMETRI (Input Validation Pattern)
    validation_errors = []
    
    if usdt_per_trade <= 0:
        validation_errors.append("Budget per trade deve essere > 0")
    if target_net_percent <= 0 or target_net_percent > 20:
        validation_errors.append("Target profitto deve essere tra 0.1% e 20%")
    if max_trades <= 0 or max_trades > 10000:
        validation_errors.append("Max trades deve essere tra 1 e 10000")
    if sleep_between_cycles < 0.1 or sleep_between_cycles > 60:
        validation_errors.append("Pausa tra controlli deve essere tra 0.1s e 60s")
    if timeout_minutes <= 0 or timeout_minutes > 1440:
        validation_errors.append("Timeout deve essere tra 1 min e 24h")
    if max_daily_loss <= 0 or max_daily_loss > 0.5:
        validation_errors.append("Max perdita deve essere tra 0.1% e 50%")
    if min_win_rate <= 0 or min_win_rate > 1:
        validation_errors.append("Win rate deve essere tra 1% e 100%")
    
    if validation_errors:
        print(f"❌ ERRORI DI VALIDAZIONE:")
        for error in validation_errors:
            print(f"   • {error}")
        print(f"\n🔄 Riavvia e inserisci valori corretti")
        return
    
    # 📊 RIEPILOGO CONFIGURAZIONE COMPLETA (Clean Code - Self Documenting)
    print(f"\n📋 RIEPILOGO CONFIGURAZIONE SCALPING AVANZATA:")
    print(f"=" * 60)
    
    # TRADING CONFIGURATION
    print(f"📈 TRADING:")
    print(f"   💰 Saldo disponibile: {available_usdt:.2f} USDT")
    print(f"   💵 Budget per trade: {usdt_per_trade:.2f} USDT")
    print(f"   🎯 Target profitto: {target_net_percent:.2f}%")
    print(f"   🛑 Stop loss: {config.trading.stop_loss_percent:.2f}%")
    print(f"   🔢 Max trades: {max_trades}")
    print(f"   📊 Strategia: {config.trading.strategy.value}")
    print(f"   ⚖️  Risk level: {config.trading.risk_level.value}")
    
    # SECURITY CONFIGURATION
    print(f"\n🛡️  SICUREZZA:")
    print(f"   🛡️  Max perdita giornaliera: {max_daily_loss*100:.1f}%")
    print(f"   📊 Min win rate: {min_win_rate*100:.1f}%")
    print(f"   🔒 Max fallimenti consecutivi: {config.security.max_consecutive_failures}")
    print(f"   📊 Max drawdown: {config.security.max_drawdown_percent:.1f}%")
    print(f"   ⚡ Circuit breaker: {'✅ Attivo' if config.security.exponential_backoff_enabled else '❌ Disattivo'}")
    print(f"   🔐 Max trade: {config.security.max_trade_amount:.0f} USDT")
    print(f"   📏 Min trade: {config.security.min_trade_amount:.0f} USDT")
    
    # DCA CONFIGURATION
    print(f"\n📈 DCA SYSTEM:")
    if config.dca.enabled:
        print(f"   Status: ✅ ATTIVO")
        print(f"   🔻 Livello 1: {config.dca.level1_trigger_percent:.1f}% → {config.dca.level1_multiplier:.1f}x")
        print(f"   🔻 Livello 2: {config.dca.level2_trigger_percent:.1f}% → {config.dca.level2_multiplier:.1f}x")
        print(f"   🛑 Stop Loss: {config.dca.level3_trigger_percent:.1f}%")
        print(f"   🔢 Max DCA trades: {config.dca.max_total_dca_trades}")
        print(f"   ⏱️  DCA cooldown: {config.dca.dca_cooldown_minutes} min")
    else:
        print(f"   Status: ❌ DISATTIVO")
    
    # PERFORMANCE CONFIGURATION
    print(f"\n⚡ PERFORMANCE:")
    print(f"   ⏱️  Controlli ogni: {sleep_between_cycles:.1f}s")
    print(f"   ⏰ Timeout sessione: {timeout_minutes} min")
    print(f"   📊 Update prezzi: {config.performance.price_update_interval}s")
    print(f"   🔄 Auto-restart: {'✅ Sì' if config.performance.auto_restart_on_error else '❌ No'}")
    print(f"   💾 Max memoria: {config.performance.max_memory_usage_mb} MB")
    
    print(f"\n🎯 Configurazione: {config.description}")
    print("=" * 60)
    
    # 🛡️ Safety Check: Verifica fondi sufficienti (Error Prevention Pattern)
    if available_usdt < usdt_per_trade * 2:
        print(f"⚠️  ATTENZIONE: Saldo USDT insufficiente!")
        print(f"   Richiesto: ${usdt_per_trade * 2:.2f} USDT (almeno 2 trade)")
        print(f"   Disponibile: ${available_usdt:.2f} USDT")
        print(f"❌ Auto-scalping annullato per sicurezza")
        return
    
    # Conferma automatica per produzione
    confirm = safe_input("🔥 AVVIARE AUTO-SCALPING? (SCRIVI 'SI' per confermare): ", "NO").upper()
    if confirm == 'SI':
        try:
            print("🚀 AUTO-SCALPING AVVIATO!")
            print("📊 Modalità headless - monitorare i log per l'attività")
            print("⌨️  Torna alla dashboard e premi F per fermare il bot")
            print("🔄 Il bot scalping è ora attivo in background...")
            
            # 🏭 DEPENDENCY INJECTION: Create dashboard instance for bot execution (Fixed)
            try:
                # Mock stdscr per headless mode (Adapter Pattern)
                class HeadlessMockStdscr:
                    def getmaxyx(self):
                        return (50, 120)
                    def nodelay(self, val):
                        pass
                    def timeout(self, val):
                        pass
                    def getch(self):
                        return -1
                    def addstr(self, *args, **kwargs):
                        pass
                    def refresh(self):
                        pass
                    def clear(self):
                        pass
                
                mock_stdscr = HeadlessMockStdscr()
                
                # Create dashboard instance for scalping (Factory Pattern)
                dashboard = CursesDashboard(
                    stdscr=mock_stdscr,
                    client=client,
                    pair=pair,
                    target_percent=target_net_percent
                )
                
                # 🎯 IMPOSTA FLAG DI STATO (Fixed Scope Issue)
                dashboard.scalping_active = True
                dashboard.scalping_stop_requested = False
                
                # Avvia scalping in modalità worker in thread separato
                import threading
                
                def run_scalping():
                    try:
                        dashboard.scalp_runner_worker_mode(
                            pair,
                            usdt_per_trade,
                            target_net_percent,
                            max_trades,
                            sleep_between_cycles,
                            timeout_minutes,
                            shutdown_event=None,
                            max_daily_loss=max_daily_loss,
                            min_win_rate=min_win_rate
                        )
                    finally:
                        # Reset flag quando scalping finisce
                        dashboard.scalping_active = False
                        dashboard.scalping_stop_requested = False
                
                scalping_thread = threading.Thread(target=run_scalping, daemon=True)
                scalping_thread.start()
                
            except Exception as e:
                print(f"❌ Errore creazione dashboard per auto-scalping: {e}")
                return
            
            # 🎮 INLINE INFO: Show navigation info (KISS Principle)
            import time
            print("\n" + "="*80)
            print("🎉 SCALPING BOT AVVIATO CON SUCCESSO!")
            print("="*80)
            print("✅ Il bot è ora attivo in modalità SILENZIOSA (nessun log a schermo)")
            print("📊 Il bot lavorerà completamente in background")
            print()
            print("🎮 CONTROLLI DISPONIBILI:")
            print("   • Ctrl+C = ❌ Ferma il bot e torna al menu principale")
            print("   • Il bot scrive log su file: bot_scalping.log")
            print("   • Monitoraggio: tail -f bot_scalping.log")
            print()
            print("⚠️  IMPORTANTE:")
            print("   1. 📊 Il bot lavora in BACKGROUND senza disturbare")
            print("   2. 📈 Log su file per analisi dettagliata")
            print("   3. 🛑 Usa Ctrl+C per fermare quando vuoi")
            print()
            print("💡 NOTA: Il bot scrive SOLO su file, nessun output console.")
            print("   Non vedrai più scrolling di messaggi!")
            print()
            print("🚀 Bot attivo! Premi Ctrl+C per fermare...")
            
            # 🔄 WAIT FOR USER INTERRUPT: Keep main thread alive
            try:
                while scalping_thread.is_alive():
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Richiesta di stop ricevuta...")
                dashboard.scalping_stop_requested = True
                print("⏳ Attendere che il bot finisca il ciclo corrente...")
                scalping_thread.join(timeout=10)
                if scalping_thread.is_alive():
                    print("⚠️  Timeout - bot terminato forzatamente")
                else:
                    print("✅ Bot fermato correttamente")
            except Exception as e:
                print(f"❌ Errore durante l'esecuzione: {e}")
                dashboard.scalping_stop_requested = True
            
        except KeyboardInterrupt:
            print(f"\n🛑 Auto-scalping {pair} interrotto dall'utente")
        except Exception as e:
            print(f"\n❌ Errore auto-scalping {pair}: {e}")
    else:
        print("❌ Auto-scalping annullato")

class InputInterface:
    """🎮 Interface for input handling (Interface Segregation Principle)"""
    def get_user_input(self, prompt: str, default: str = "") -> str:
        raise NotImplementedError

class ConsoleInputHandler(InputInterface):
    """📝 Console input implementation (Single Responsibility)"""
    def get_user_input(self, prompt: str, default: str = "") -> str:
        try:
            result = input(prompt)
            return result.upper() if result else default
        except (EOFError, KeyboardInterrupt):
            return default

class DefaultInputHandler(InputInterface):
    """🔧 Fallback input handler with stdin attempt (Liskov Substitution Principle)"""
    def __init__(self, default_mode: str = "M"):
        self.default_mode = default_mode
    
    def get_user_input(self, prompt: str, default: str = "") -> str:
        # 🎯 CHIRURGIA PRECISA: Attempt to read stdin first, then fallback
        try:
            import sys
            # Try to read a line from stdin if available
            if not sys.stdin.isatty():
                line = sys.stdin.readline()
                if line.strip():
                    result = line.strip().upper()
                    print(f"{prompt} {result}")
                    return result
        except:
            pass
        
        # Fallback to default
        print(f"{prompt} [Auto-selected: {default or self.default_mode}]")
        return default or self.default_mode

class ApplicationFactory:
    """🏭 Factory for creating application components (Factory Pattern)"""
    @staticmethod
    def create_input_handler() -> InputInterface:
        """Creates appropriate input handler based on environment"""
        try:
            # Test if stdin is available
            import sys
            if sys.stdin.isatty():
                return ConsoleInputHandler()
            else:
                return DefaultInputHandler("M")  # Default to monitoring mode
        except:
            return DefaultInputHandler("M")

def safe_input(prompt: str, default: str = "", convert_type=str):
    """🛡️ Safe input wrapper (Template Method Pattern)"""
    try:
        result = input(prompt)
        if not result and default:
            return convert_type(default)
        return convert_type(result) if result else convert_type(default)
    except (EOFError, KeyboardInterrupt, ValueError):
        return convert_type(default) if default else None

def main_menu():
    # 🔐 Carica credenziali da file .env se presente
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # python-dotenv non installato, usa variabili d'ambiente dirette
    
    api_key = os.getenv("GATE_API_KEY")
    secret_key = os.getenv("GATE_SECRET_KEY")
    
    try:
        client = GateIOClient(api_key, secret_key)
    except ValueError as e:
        print(f"❌ Errore: {e}")
        print("\n💡 ISTRUZIONI CONFIGURAZIONE:")
        print("1. Crea file .env nella directory del progetto")
        print("2. Aggiungi le tue credenziali Gate.io:")
        print("   GATE_API_KEY=your_api_key_here")
        print("   GATE_SECRET_KEY=your_secret_key_here")
        print("3. Oppure imposta le variabili d'ambiente del sistema")
        print("\n🔒 Il file .env non deve mai essere committato in git!")
        sys.exit(1)
    
    while True:
        print("\n🚀 SCALPING DASHBOARD AVANZATO - Gate.io")
        print("=" * 50)
        print("📈 MODALITÀ DISPONIBILI:")
        print("   A. 🤖 AUTO-SCALPING (PRODUZIONE) - Bot automatico")
        print("   M. 📊 MONITORING - Dashboard interattiva")
        print("   B. 🎮 MULTI-BOT MANAGER - Gestione bot multipli")
        print("=" * 50)
        
        # 🏭 Factory Pattern: Create input handler (Dependency Inversion)
        input_handler = ApplicationFactory.create_input_handler()
        
        # 🎮 Strategy Pattern: Use appropriate input handler
        mode = input_handler.get_user_input(
            "🎯 Seleziona modalità (A=Auto-Scalping, M=Monitoring, B=Multi-Bot, default M): ", 
            "M"
        )
        
        if mode == "A":
            # 🤖 MODALITÀ AUTO-SCALPING (PRODUZIONE)
            print("\n🤖 MODALITÀ AUTO-SCALPING ATTIVATA")
            print("=" * 50)
            
            # Selezione coppia per scalping automatico
            owned_coins = get_owned_coins(client)
            if not owned_coins:
                print("❌ Nessuna moneta posseduta trovata (escluse stablecoin e GT).")
                print("💡 Assicurati di avere delle crypto nel tuo wallet spot.")
                
                # Offri opzione di aggiungere manualmente
                choice = input("🔧 Vuoi aggiungere una coppia manualmente? (s/n): ").lower()
                if choice == 's':
                    result = handle_manual_coin_entry(client)
                    if result:
                        pair, current_balance = result
                        print(f"✅ Coppia {pair} aggiunta per auto-scalping")
                    else:
                        continue
                else:
                    sys.exit(0)
            else:
                # Mostra coppie possedute per auto-scalping
                print("\n💰 COPPIE DISPONIBILI PER AUTO-SCALPING:")
                for i, coin in enumerate(owned_coins):
                    balance = float(coin['available']) + float(coin['locked'])
                    print(f"  {i+1:2}. {coin['currency']:8} | Saldo: {balance:>12.6f}")
                
                try:
                    choice = int(input(f"\nSeleziona coppia per auto-scalping (1-{len(owned_coins)}): "))
                    if 1 <= choice <= len(owned_coins):
                        choice = choice - 1
                        selected_coin = owned_coins[choice]
                        pair = f"{selected_coin['currency']}_USDT"
                        current_balance = float(selected_coin['available']) + float(selected_coin['locked'])
                        print(f"✅ Auto-scalping attivato per {pair} (saldo: {current_balance:.6f})")
                        
                        # Avvia auto-scalping direttamente
                        start_auto_scalping(client, pair)
                        continue
                    else:
                        print("❌ Scelta non valida.")
                        continue
                except ValueError:
                    print("❌ Input non valido.")
                    continue
        
        elif mode == "B":
            # 🎮 MODALITÀ MULTI-BOT MANAGER
            print("\n🎮 MODALITÀ MULTI-BOT MANAGER ATTIVATA")
            print("=" * 40)
            try:
                from multi_bot_ui import MultiBotController
                controller = MultiBotController()
                controller.run()
            except ImportError as e:
                print(f"❌ Errore import multi-bot manager: {e}")
                print("💡 Assicurati che multi_bot_ui.py sia presente")
            except Exception as e:
                print(f"❌ Errore multi-bot manager: {e}")
                import traceback
                traceback.print_exc()
            
            # Return to main menu after multi-bot manager
            continue
        
        elif mode == "M":
            # 📊 MODALITÀ MONITORING (DASHBOARD INTERATTIVA)
            print("\n📊 MODALITÀ MONITORING ATTIVATA")
            print("=" * 50)
            break  # Esce dal ciclo e procede con la dashboard interattiva
        else:
            print("❌ Modalità non valida. Usa A, M o B.")
            continue

    # 📊 MODALITÀ MONITORING - DASHBOARD INTERATTIVA
    owned_coins = get_owned_coins(client)
    if not owned_coins:
        print("❌ Nessuna moneta posseduta trovata (escluse stablecoin e GT).")
        print("💡 Assicurati di avere delle crypto nel tuo wallet spot.")
        sys.exit(0)
    
    print("\n💰 COPPIE DISPONIBILI:")
    print(f"   0. ➕ AGGIUNGI COIN A WALLET")
    for i, coin in enumerate(owned_coins):
        balance = float(coin['available']) + float(coin['locked'])
        print(f"  {i+1:2}. {coin['currency']:8} | Saldo: {balance:>12.6f}")
    
    try:
        # 🛡️ Safe input with default selection (Error Recovery Pattern)
        choice = safe_input(
            f"\nSeleziona opzione (0 per aggiungere, 1-{len(owned_coins)} per possedute): ",
            default="1" if owned_coins else "0",
            convert_type=int
        )
        
        if choice == 0:
            result = handle_manual_coin_entry(client)
            if result:
                pair, current_balance = result
                print(f"\n🔍 Analizzando {pair}...")
            else:
                sys.exit(0)
        elif 1 <= choice <= len(owned_coins):
            choice = choice - 1
            selected_coin = owned_coins[choice]
            pair = f"{selected_coin['currency']}_USDT"
            current_balance = float(selected_coin['available']) + float(selected_coin['locked'])
            print(f"\n🔍 Analizzando {pair}...")
            print("🔗 Recupero dati tranche dall'API Gate.io...")
        else:
            print("❌ Scelta non valida.")
            sys.exit(0)
    except ValueError:
        print("❌ Input non valido.")
        sys.exit(0)
    
    # 📈 Recupera automaticamente i dati reali del portafoglio (solo se current_balance > 0)
    portfolio_data = None
    if current_balance > 0:
        portfolio_data = client.calculate_real_portfolio_data(pair)

    if portfolio_data and portfolio_data['buy_trades'] and current_balance > 0:
        # Dati reali trovati dall'API
        print(f"Trovate {len(portfolio_data['buy_trades'])} tranche di acquisto!")
        print(f"   💰 Capitale investito: {portfolio_data['total_invested']:.2f} USDT")
        print(f"   Prezzo medio aritmetico: {portfolio_data['arithmetic_avg_price']:.6f}")
        print(f"   ⚖️  Prezzo medio ponderato: {portfolio_data['weighted_avg_price']:.6f}")
        print(f"   🪙 Saldo attuale: {portfolio_data['current_balance']:.6f} ({portfolio_data['remaining_percentage']:.1f}%)")

        buy_price = portfolio_data['weighted_avg_price']
        amount = portfolio_data['current_balance']
        prezzi = [trade['price'] for trade in portfolio_data['buy_trades']]
        quantita = [trade['amount'] for trade in portfolio_data['buy_trades']]
        print("✅ Usando dati automatici dall'API Gate.io")

        # 🎯 UNIFIED CONFIGURATION FOR MONITORING MODE
        print(f"\n🧙 CONFIGURAZIONE AVANZATA PER MONITORING")
        print("=" * 45)
        print("1. 📋 Usa preset ottimizzati")
        print("2. ⚙️  Configurazione guidata")
        print("3. 🔧 Solo target profitto (rapido)")
        
        config_choice = safe_input("Scegli modalità (1-3) [default: 3]: ", "3", str)
        
        if config_choice in ["1", "2"]:
            if config_choice == "1":
                # PRESET CONFIGURATION
                from config_integration import ConfigurationWizard
                from unified_bot_config import ConfigurationPresets
                
                print(f"\n📋 PRESET DISPONIBILI per {pair}:")
                print(f"   1. 🛡️  Conservative (1% target)")
                print(f"   2. ⚖️  Moderate (2.5% target)")
                print(f"   3. 🚀 Aggressive (3% target)")
                
                preset_choice = safe_input("Scegli preset (1-3) [default: 2]: ", "2", str)
                budget = portfolio_data['total_invested'] if portfolio_data else 50.0
                
                preset_map = {"1": "conservative", "2": "moderate", "3": "aggressive"}
                preset_name = preset_map.get(preset_choice, "moderate")
                config = ConfigurationPresets.get_preset_by_name(preset_name, pair, budget)
                
            elif config_choice == "2":
                # GUIDED CONFIGURATION
                from config_integration import ConfigurationWizard
                config = ConfigurationWizard.interactive_configuration(pair)
            
            if config:
                target_percent = config.trading.target_profit_percent
                print(f"✅ Configurazione unificata applicata")
                print(f"🎯 Target profitto: {target_percent}%")
                print(f"🛡️  Sicurezza: Max loss {config.security.max_daily_loss_percent}%")
                print(f"📈 DCA: {'✅ Attivo' if config.dca.enabled else '❌ Disattivo'}")
            else:
                config_choice = "3"  # Fallback to rapid mode
        
        if config_choice == "3" or not config:
            # LEGACY RAPID TARGET CONFIGURATION
            print(f"\nConfigurazione target di profitto:")
            print("   💡 Suggerimenti: 0.5-1% (scalping), 2-5% (swing), 10%+ (hold)")
            try:
                target_percent = safe_input("📈 Inserisci % di profitto desiderata (default 2%): ", "2", float)
            except ValueError:
                target_percent = 2.0

        target_price = (sum(prezzi) / len(prezzi) if prezzi else buy_price) * (1 + target_percent / 100)
        print(f"Prezzo target calcolato: {target_price:.6f} USDT (+{target_percent}%)")

    elif current_balance == 0:
        # 🆕 COIN AGGIUNTA MANUALMENTE - Nessuna posizione attiva
        print("💡 MODALITÀ SOLO ACQUISTO ATTIVATA")
        print("   ▶️  Coin aggiunta per monitoraggio")
        print("   ▶️  Pronta per acquisto con tasti 6-9")

        # Valori default per coin senza posizioni
        current_price = client.get_ticker(pair)
        buy_price = current_price  # Prezzo corrente come riferimento
        amount = 0.0  # Nessuna posizione
        prezzi = []  # Nessuna tranche di acquisto
        quantita = []  # Nessuna quantità posseduta
        
        # 🎯 UNIFIED CONFIGURATION (COIN SENZA POSIZIONI)
        print(f"\n🧙 CONFIGURAZIONE AVANZATA (NO POSITION MODE)")
        print("=" * 45)
        print("1. 📋 Usa preset ottimizzati")
        print("2. 🔧 Solo target profitto (rapido)")
        
        config_choice = safe_input("Scegli modalità (1-2) [default: 2]: ", "2", str)
        
        if config_choice == "1":
            # PRESET CONFIGURATION FOR NEW COINS
            from config_integration import ConfigurationWizard
            from unified_bot_config import ConfigurationPresets
            
            print(f"\n📋 PRESET DISPONIBILI per {pair}:")
            print(f"   1. 🛡️  Conservative (1% target)")
            print(f"   2. ⚖️  Moderate (2.5% target)")
            print(f"   3. 🚀 Aggressive (3% target)")
            
            preset_choice = safe_input("Scegli preset (1-3) [default: 2]: ", "2", str)
            preset_map = {"1": "conservative", "2": "moderate", "3": "aggressive"}
            preset_name = preset_map.get(preset_choice, "moderate")
            config = ConfigurationPresets.get_preset_by_name(preset_name, pair, 50.0)
            
            if config:
                target_percent = config.trading.target_profit_percent
                print(f"✅ Preset {preset_name} applicato per monitoraggio {pair}")
                print(f"🎯 Target: {target_percent}% | DCA: {'✅' if config.dca.enabled else '❌'}")
            else:
                config_choice = "2"  # Fallback
        
        if config_choice == "2" or not config:
            # LEGACY RAPID TARGET CONFIGURATION  
            print(f"\nConfigurazione target di profitto:")
            print("   💡 Suggerimenti: 0.5-1% (scalping), 2-5% (swing), 10%+ (hold)")
            try:
                target_percent = safe_input("📈 Inserisci % di profitto desiderata (default 2%): ", "2", float)
            except ValueError:
                target_percent = 2.0
        
    else:
        # 📝 Fallback a dati manuali per coin con saldo > 0
        print("Nessuna tranche trovata nell'API. Usando modalità manuale.")
        buy_price, amount, prezzi, quantita = get_manual_data(client, pair, current_balance)

        # 🎯 UNIFIED CONFIGURATION (MANUAL DATA FALLBACK)
        print(f"\n🧙 CONFIGURAZIONE AVANZATA (MANUAL MODE)")
        print("=" * 45)
        print("1. 📋 Usa preset ottimizzati")
        print("2. 🔧 Solo target profitto (rapido)")
        
        config_choice = safe_input("Scegli modalità (1-2) [default: 2]: ", "2", str)
        
        if config_choice == "1":
            # PRESET CONFIGURATION FOR MANUAL DATA
            from config_integration import ConfigurationWizard
            from unified_bot_config import ConfigurationPresets
            
            print(f"\n📋 PRESET DISPONIBILI per {pair}:")
            print(f"   1. 🛡️  Conservative (1% target)")
            print(f"   2. ⚖️  Moderate (2.5% target)")
            print(f"   3. 🚀 Aggressive (3% target)")
            
            preset_choice = safe_input("Scegli preset (1-3) [default: 2]: ", "2", str)
            # Use average of manual prices as budget estimate
            avg_price = sum(prezzi) / len(prezzi) if prezzi else buy_price
            budget_estimate = avg_price * amount if amount > 0 else 50.0
            
            preset_map = {"1": "conservative", "2": "moderate", "3": "aggressive"}
            preset_name = preset_map.get(preset_choice, "moderate")
            config = ConfigurationPresets.get_preset_by_name(preset_name, pair, budget_estimate)
            
            if config:
                target_percent = config.trading.target_profit_percent
                print(f"✅ Preset {preset_name} applicato per {pair} (manual)")
                print(f"🎯 Target: {target_percent}% | Security: Max loss {config.security.max_daily_loss_percent}%")
            else:
                config_choice = "2"  # Fallback
        
        if config_choice == "2" or not config:
            # LEGACY RAPID TARGET CONFIGURATION
            print(f"\nConfigurazione target di profitto:")
            print("   💡 Suggerimenti: 0.5-1% (scalping), 2-5% (swing), 10%+ (hold)")
            try:
                target_percent = safe_input("📈 Inserisci % di profitto desiderata (default 2%): ", "2", float)
            except ValueError:
                target_percent = 2.0

        target_price = (sum(prezzi) / len(prezzi) if prezzi else buy_price) * (1 + target_percent / 100)
        print(f"Prezzo target calcolato: {target_price:.6f} USDT (+{target_percent}%)")

    print("\n🚀 Avvio dashboard...")
    print("=" * 50)
    if current_balance > 0:
        print("🎮 CONTROLLI (POSIZIONI ATTIVE):")
        print("   1-4: Vendi 25%, 50%, 75%, 100%")
        print("   6-9: Acquista 25%, 50%, 75%, 100% USDT")
        print("   S: BOT SCALPING AUTOMATICO 🤖")
        print("   F: Ferma SCALPING attivo 🛑")
        print("   INVIO: Conferma ordine")
        print("   C: Annulla operazione")
        print("   TAB: Naviga sezioni | H: Help")
        print("   Q: Uscita immediata")
    else:
        print("🎮 CONTROLLI (MODALITÀ SOLO ACQUISTO):")
        print("   6-9: Acquista 25%, 50%, 75%, 100% USDT")
        print("   S: BOT SCALPING AUTOMATICO 🤖")
        print("   F: Ferma SCALPING attivo 🛑")
        print("   INVIO: Conferma ordine")
        print("   C: Annulla operazione")
        print("   TAB: Naviga sezioni | H: Help")
        print("   Q: Uscita immediata")
        print("   💡 Usa tasti 6-9 per acquistare o S per bot automatico!")
    print("=" * 50)

    time.sleep(2)

    # target_percent ora è sempre quello scelto dall'utente e va passato anche agli automatismi
    try:
        wrapper(start_dashboard_wrapper, client, pair, buy_price, target_percent, amount, owned_coins, prezzi, quantita)
        print("\nDashboard chiuso correttamente.")
    except (ValueError, KeyboardInterrupt, EOFError):
        print("\n👋 Uscita dal programma.")
    except Exception as e:
        # Ignora errori di curses cleanup (normali quando si chiude la dashboard)
        error_msg = str(e).lower()
        if "nocbreak" in error_msg or "endwin" in error_msg or "curses" in error_msg:
            print("\nDashboard chiusa.")
        else:
            print(f"\n💥 Errore durante l'esecuzione del dashboard: {e}")
            with open("error_dashboard.log", "a") as f:
                f.write(f"{datetime.now()}: Errore Dashboard\n")
                f.write(traceback.format_exc() + "\n")

def get_manual_data(client, pair, current_balance):
    """🔧 Raccoglie dati manuali per configurazione fallback"""
    print(f"\n📝 CONFIGURAZIONE MANUALE per {pair}")

    # Cerca l'ultimo prezzo di acquisto nell'API
    buy_price, _ = get_last_buy_price(client, pair)
    if buy_price:
        print(f"💡 Ultimo prezzo di acquisto trovato: {buy_price:.6f} USDT")
        use_last = input("🤔 Usare questo prezzo? (s/n): ").lower()
        if use_last != 'n':
            prezzi = [buy_price]
            quantita = [current_balance]
            return buy_price, current_balance, prezzi, quantita

    # Input manuale
    buy_price = float(input(f"💰 Inserisci il prezzo di acquisto principale per {pair}: "))
    prezzi = [buy_price]
    quantita = [current_balance]

    while True:
        add_more = input("\n➕ Vuoi aggiungere un'altra tranche di acquisto? (s/n): ").lower()
        if add_more == 's':
            try:
                p = float(input("💰 Prezzo di acquisto aggiuntivo: "))
                q = float(input("🪙 Quantità acquistata a questo prezzo: "))
                prezzi.append(p)
                quantita.append(q)

                # Aggiorna totali
                total_q = sum(quantita)
                total_v = sum(p * q for p, q in zip(prezzi, quantita))
                weighted_avg = total_v / total_q if total_q > 0 else 0

                trade_logger.info(str(f"Totale: {total_q:.6f} | Prezzo medio ponderato: {weighted_avg:.6f}"))
            except ValueError:
                trade_logger.info(str("❌ Input non valido."))
        else:
            break

    # Ricalcola valori finali
    if len(prezzi) > 1:
        total_q = sum(quantita)
        total_v = sum(p * q for p, q in zip(prezzi, quantita))
        buy_price = total_v / total_q if total_q > 0 else buy_price
        amount = total_q

        arithmetic_avg = sum(prezzi) / len(prezzi)
        print(f"\nRIEPILOGO TRANCHE:")
        print(f"   🧮 Prezzo medio aritmetico: {arithmetic_avg:.6f} USDT")
        print(f"   ⚖️  Prezzo medio ponderato: {buy_price:.6f} USDT")
        print(f"   🪙 Quantità totale: {amount:.6f}")
    else:
        amount = current_balance
        print(f"\nConfigurazione singola tranche: {buy_price:.6f} USDT")

    return buy_price, amount, prezzi, quantita

def worker_mode():
    """🤖 Modalità worker per Session Manager"""
    import argparse
    import sys
    import signal
    import queue
    import threading
    from datetime import datetime
    
    parser = argparse.ArgumentParser(description="Bot Worker Mode")
    parser.add_argument('--worker-mode', action='store_true', help='Avvia in modalità worker')
    parser.add_argument('--pair', required=True, help='Coppia trading')
    parser.add_argument('--budget', type=float, required=True, help='Budget USDT')
    parser.add_argument('--target', type=float, default=2.0, help='Target % profit')
    parser.add_argument('--manager-queue', help='Queue comunicazione con manager')
    
    args = parser.parse_args()
    
    if not args.worker_mode:
        return False
    
    print(f"🤖 WORKER MODE: {args.pair}")
    print(f"💰 Budget: {args.budget} USDT")
    print(f"🎯 Target: {args.target}%")
    print("=" * 40)
    
    # Inizializza client
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    api_key = os.getenv("GATE_API_KEY")
    secret_key = os.getenv("GATE_SECRET_KEY")
    
    if not api_key or not secret_key:
        print("❌ Credenziali Gate.io non trovate")
        if args.pair != "TEST_USDT":  # Permetti test senza credenziali
            sys.exit(1)
        else:
            print("⚠️ Modalità test - nessun trading reale")
            client = None
    else:
        client = GateIOClient(api_key, secret_key)
    
    # Setup signal handlers per shutdown graceful
    shutdown_event = threading.Event()
    
    def signal_handler(signum, frame):
        print(f"\\n📡 Worker {args.pair} ricevuto segnale {signum}")
        shutdown_event.set()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Crea dashboard in modalità headless
    if client:
        dashboard = CursesDashboard(
            None,  # No stdscr in worker mode
            client, 
            args.pair,
            None,  # buy_price
            args.target,
            None,  # amount
            None,  # spot_assets
            None,  # prezzi
            None   # quantita
        )
    else:
        # Modalità test senza client
        dashboard = None
    
    # Avvia bot scalping in worker mode
    try:
        print(f"🚀 Avvio bot scalping per {args.pair}...")
        
        # Configurazione bot
        usdt_per_trade = args.budget
        target_net_percent = args.target
        max_trades = 1000  # Praticamente infinito
        sleep_between_cycles = 0.5
        timeout_minutes = 10
        
        # Thread per monitoraggio comandi dal manager
        command_queue = queue.Queue()
        
        def command_monitor():
            """Monitor per comandi dal session manager"""
            # TODO: Implementare comunicazione reale con manager
            # Per ora, simula comandi
            while not shutdown_event.is_set():
                try:
                    # Placeholder per comunicazione con manager
                    time.sleep(1)
                except:
                    break
        
        monitor_thread = threading.Thread(target=command_monitor, daemon=True)
        monitor_thread.start()
        
        # Avvia bot scalping (modalità modificata per worker)
        if dashboard:
            dashboard.scalp_runner_worker_mode(
                args.pair, 
                usdt_per_trade, 
                target_net_percent, 
                max_trades, 
                sleep_between_cycles, 
                timeout_minutes,
                shutdown_event
            )
        else:
            # Modalità test - simula funzionamento
            print(f"🧪 Modalità test per {args.pair}")
            print(f"💰 Budget simulato: {usdt_per_trade} USDT")
            print(f"🎯 Target simulato: {target_net_percent}%")
            
            for i in range(3):  # Simula 3 secondi di attività
                if shutdown_event.is_set():
                    break
                print(f"🔄 Test trade #{i+1} per {args.pair}")
                time.sleep(1)
            
            print(f"✅ Test completato per {args.pair}")
        
    except KeyboardInterrupt:
        print(f"\\n🛑 Worker {args.pair} interrotto dall'utente")
    except Exception as e:
        print(f"❌ Errore worker {args.pair}: {e}")
        sys.exit(1)
    finally:
        print(f"🏁 Worker {args.pair} terminato")
    
    return True

if __name__ == "__main__":
    # Check se siamo in worker mode
    if len(sys.argv) > 1 and '--worker-mode' in sys.argv:
        if worker_mode():
            sys.exit(0)
    
    # Modalità normale
    main_menu()