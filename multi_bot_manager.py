#!/usr/bin/env python3
"""
🤖 Multi-Bot Manager System
Advanced bot management following SOLID principles and enterprise patterns
"""

import threading
import time
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from abc import ABC, abstractmethod
import logging

# Configure structured logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(name)s | %(levelname)s | %(message)s')
logger = logging.getLogger('multi_bot_manager')

class BotStatus(Enum):
    """📊 Bot status enumeration (Type Safety)"""
    IDLE = "idle"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"

@dataclass
class BotConfiguration:
    """⚙️ Bot configuration data class (Single Responsibility)"""
    pair: str
    budget_per_trade: float
    target_profit: float
    max_trades: int
    sleep_between_cycles: float
    timeout_minutes: int
    max_daily_loss: float
    min_win_rate: float
    # 🚦 Rate Limiting Configuration (VIP 0 defaults)
    rate_limit_enabled: bool = True
    rate_limit_strategy: str = "sliding_window"  # "sliding_window" or "token_bucket"
    rate_limit_safety_margin: float = 0.8  # Use 80% of limits for safety
    created_at: str = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

@dataclass
class BotInstance:
    """🤖 Bot instance data class (Data Transfer Object Pattern)"""
    bot_id: str
    pair: str
    status: BotStatus
    config: BotConfiguration
    thread: threading.Thread = None
    dashboard: Any = None
    created_at: str = None
    started_at: str = None
    stopped_at: str = None
    trade_count: int = 0
    profit_loss: float = 0.0
    last_error: str = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

class BotObserver(ABC):
    """👁️ Observer interface for bot status changes (Observer Pattern)"""
    @abstractmethod
    def on_bot_status_changed(self, bot_id: str, old_status: BotStatus, new_status: BotStatus):
        pass
    
    @abstractmethod
    def on_bot_error(self, bot_id: str, error: str):
        pass

class BotCommand(ABC):
    """📋 Command interface for bot operations (Command Pattern)"""
    @abstractmethod
    def execute(self) -> bool:
        pass
    
    @abstractmethod
    def can_undo(self) -> bool:
        pass
    
    @abstractmethod
    def undo(self) -> bool:
        pass

class StartBotCommand(BotCommand):
    """🚀 Command to start a bot (Command Pattern)"""
    def __init__(self, bot_manager: 'MultiBotManager', bot_id: str):
        self.bot_manager = bot_manager
        self.bot_id = bot_id
    
    def execute(self) -> bool:
        return self.bot_manager._start_bot_instance(self.bot_id)
    
    def can_undo(self) -> bool:
        return True
    
    def undo(self) -> bool:
        return self.bot_manager._stop_bot_instance(self.bot_id)

class StopBotCommand(BotCommand):
    """🛑 Command to stop a bot (Command Pattern)"""
    def __init__(self, bot_manager: 'MultiBotManager', bot_id: str):
        self.bot_manager = bot_manager
        self.bot_id = bot_id
    
    def execute(self) -> bool:
        return self.bot_manager._stop_bot_instance(self.bot_id)
    
    def can_undo(self) -> bool:
        return False  # Cannot undo stop
    
    def undo(self) -> bool:
        return False

class MultiBotManager:
    """🎯 Centralized multi-bot manager (Singleton Pattern)"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton implementation (Thread-Safe)"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize manager (Single Responsibility)"""
        if not self._initialized:
            self.bots: Dict[str, BotInstance] = {}
            self.observers: List[BotObserver] = []
            self.command_history: List[BotCommand] = []
            self.data_lock = threading.RLock()  # Reentrant lock for nested calls
            self.persistence_file = "multi_bot_state.json"
            self._load_state()
            self._initialized = True
    
    def add_observer(self, observer: BotObserver):
        """Add status observer (Observer Pattern)"""
        with self.data_lock:
            if observer not in self.observers:
                self.observers.append(observer)
    
    def remove_observer(self, observer: BotObserver):
        """Remove status observer"""
        with self.data_lock:
            if observer in self.observers:
                self.observers.remove(observer)
    
    def _notify_status_change(self, bot_id: str, old_status: BotStatus, new_status: BotStatus):
        """Notify observers of status change (Observer Pattern)"""
        for observer in self.observers:
            try:
                observer.on_bot_status_changed(bot_id, old_status, new_status)
            except Exception as e:
                logger.error(f"Observer notification error: {e}")
    
    def _notify_error(self, bot_id: str, error: str):
        """Notify observers of bot error"""
        for observer in self.observers:
            try:
                observer.on_bot_error(bot_id, error)
            except Exception as e:
                logger.error(f"Observer error notification failed: {e}")
    
    def register_bot(self, config: BotConfiguration) -> str:
        """📝 Register a new bot instance (Factory Pattern)"""
        with self.data_lock:
            bot_id = f"bot_{config.pair}_{int(time.time())}"
            
            # Check for duplicate pair (Business Rule)
            existing_pair_bots = [b for b in self.bots.values() 
                                if b.pair == config.pair and b.status in [BotStatus.RUNNING, BotStatus.STARTING]]
            
            if existing_pair_bots:
                logger.warning(f"Bot for {config.pair} already exists and is active")
                # Allow multiple bots per pair but with warning
            
            bot_instance = BotInstance(
                bot_id=bot_id,
                pair=config.pair,
                status=BotStatus.IDLE,
                config=config
            )
            
            self.bots[bot_id] = bot_instance
            logger.info(f"Bot {bot_id} registered for pair {config.pair}")
            
            self._save_state()
            return bot_id
    
    def execute_command(self, command: BotCommand) -> bool:
        """Execute bot command (Command Pattern)"""
        with self.data_lock:
            try:
                success = command.execute()
                if success:
                    self.command_history.append(command)
                    # Keep history limited (Memory Management)
                    if len(self.command_history) > 100:
                        self.command_history = self.command_history[-50:]
                return success
            except Exception as e:
                logger.error(f"Command execution failed: {e}")
                return False
    
    def _start_bot_instance(self, bot_id: str) -> bool:
        """🚀 Internal method to start bot (Single Responsibility)"""
        if bot_id not in self.bots:
            logger.error(f"Bot {bot_id} not found")
            return False
        
        bot = self.bots[bot_id]
        if bot.status != BotStatus.IDLE and bot.status != BotStatus.STOPPED:
            logger.warning(f"Bot {bot_id} is not in startable state: {bot.status}")
            return False
        
        try:
            old_status = bot.status
            bot.status = BotStatus.STARTING
            self._notify_status_change(bot_id, old_status, bot.status)
            
            # Create and start bot thread
            def bot_worker():
                try:
                    bot.started_at = datetime.now().isoformat()
                    old_status = bot.status
                    bot.status = BotStatus.RUNNING
                    self._notify_status_change(bot_id, old_status, bot.status)
                    
                    # Import and create dashboard instance (Late Binding)
                    from dash01_refactored import CursesDashboard
                    
                    # Mock stdscr for headless mode
                    class HeadlessMockStdscr:
                        def getmaxyx(self): return (50, 120)
                        def nodelay(self, val): pass
                        def timeout(self, val): pass
                        def getch(self): return -1
                        def addstr(self, *args, **kwargs): pass
                        def refresh(self): pass
                        def clear(self): pass
                    
                    mock_stdscr = HeadlessMockStdscr()
                    
                    # Create dashboard instance (Dependency Injection)
                    from dash01_refactored import GateIOClient
                    client = GateIOClient(
                        os.getenv("GATE_API_KEY"),
                        os.getenv("GATE_SECRET_KEY"),
                        rate_limit_enabled=bot.config.rate_limit_enabled,
                        rate_limit_strategy=bot.config.rate_limit_strategy,
                        rate_limit_safety_margin=bot.config.rate_limit_safety_margin
                    )
                    
                    dashboard = CursesDashboard(
                        stdscr=mock_stdscr,
                        client=client,
                        pair=bot.config.pair,
                        target_percent=bot.config.target_profit
                    )
                    
                    bot.dashboard = dashboard
                    dashboard.scalping_active = True
                    dashboard.scalping_stop_requested = False
                    
                    # Run scalping worker mode
                    dashboard.scalp_runner_worker_mode(
                        bot.config.pair,
                        bot.config.budget_per_trade,
                        bot.config.target_profit,
                        bot.config.max_trades,
                        bot.config.sleep_between_cycles,
                        bot.config.timeout_minutes,
                        shutdown_event=None,
                        max_daily_loss=bot.config.max_daily_loss,
                        min_win_rate=bot.config.min_win_rate
                    )
                    
                except Exception as e:
                    logger.error(f"Bot {bot_id} execution error: {e}")
                    bot.last_error = str(e)
                    old_status = bot.status
                    bot.status = BotStatus.ERROR
                    self._notify_status_change(bot_id, old_status, bot.status)
                    self._notify_error(bot_id, str(e))
                finally:
                    # Cleanup
                    if hasattr(bot, 'dashboard') and bot.dashboard:
                        bot.dashboard.scalping_active = False
                        bot.dashboard.scalping_stop_requested = True
                    
                    bot.stopped_at = datetime.now().isoformat()
                    old_status = bot.status
                    if bot.status != BotStatus.ERROR:
                        bot.status = BotStatus.STOPPED
                    self._notify_status_change(bot_id, old_status, bot.status)
                    
                    self._save_state()
            
            bot.thread = threading.Thread(target=bot_worker, daemon=True, name=f"Bot-{bot_id}")
            bot.thread.start()
            
            logger.info(f"Bot {bot_id} started successfully")
            self._save_state()
            return True
            
        except Exception as e:
            logger.error(f"Failed to start bot {bot_id}: {e}")
            bot.status = BotStatus.ERROR
            bot.last_error = str(e)
            self._notify_error(bot_id, str(e))
            return False
    
    def _stop_bot_instance(self, bot_id: str) -> bool:
        """🛑 Internal method to stop bot (Single Responsibility)"""
        if bot_id not in self.bots:
            logger.error(f"Bot {bot_id} not found")
            return False
        
        bot = self.bots[bot_id]
        if bot.status not in [BotStatus.RUNNING, BotStatus.STARTING]:
            logger.warning(f"Bot {bot_id} is not in stoppable state: {bot.status}")
            return False
        
        try:
            old_status = bot.status
            bot.status = BotStatus.STOPPING
            self._notify_status_change(bot_id, old_status, bot.status)
            
            # Signal bot to stop
            if hasattr(bot, 'dashboard') and bot.dashboard:
                bot.dashboard.scalping_stop_requested = True
            
            # Wait for thread to finish (with timeout)
            if bot.thread and bot.thread.is_alive():
                bot.thread.join(timeout=10)
                if bot.thread.is_alive():
                    logger.warning(f"Bot {bot_id} thread did not stop gracefully")
            
            old_status = bot.status
            bot.status = BotStatus.STOPPED
            bot.stopped_at = datetime.now().isoformat()
            self._notify_status_change(bot_id, old_status, bot.status)
            
            logger.info(f"Bot {bot_id} stopped successfully")
            self._save_state()
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop bot {bot_id}: {e}")
            bot.last_error = str(e)
            self._notify_error(bot_id, str(e))
            return False
    
    def get_bot_status(self, bot_id: str) -> Optional[BotInstance]:
        """📊 Get bot status (Read-Only Access)"""
        with self.data_lock:
            return self.bots.get(bot_id)
    
    def get_all_bots(self) -> Dict[str, BotInstance]:
        """📋 Get all bots (Read-Only Access)"""
        with self.data_lock:
            return dict(self.bots)  # Return copy to prevent external modification
    
    def get_running_bots(self) -> List[BotInstance]:
        """🏃 Get running bots only"""
        with self.data_lock:
            return [bot for bot in self.bots.values() if bot.status == BotStatus.RUNNING]
    
    def remove_bot(self, bot_id: str) -> bool:
        """🗑️ Remove bot instance (Cleanup)"""
        with self.data_lock:
            if bot_id not in self.bots:
                return False
            
            bot = self.bots[bot_id]
            
            # Stop bot if running
            if bot.status in [BotStatus.RUNNING, BotStatus.STARTING]:
                self._stop_bot_instance(bot_id)
            
            # Remove from registry
            del self.bots[bot_id]
            logger.info(f"Bot {bot_id} removed from registry")
            
            self._save_state()
            return True
    
    def _save_state(self):
        """💾 Persist bot state to file (Repository Pattern)"""
        try:
            state_data = {
                'bots': {},
                'timestamp': datetime.now().isoformat()
            }
            
            for bot_id, bot in self.bots.items():
                # Only save persistent data, not runtime objects
                state_data['bots'][bot_id] = {
                    'bot_id': bot.bot_id,
                    'pair': bot.pair,
                    'status': bot.status.value,
                    'config': asdict(bot.config),
                    'created_at': bot.created_at,
                    'started_at': bot.started_at,
                    'stopped_at': bot.stopped_at,
                    'trade_count': bot.trade_count,
                    'profit_loss': bot.profit_loss,
                    'last_error': bot.last_error
                }
            
            with open(self.persistence_file, 'w') as f:
                json.dump(state_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
    
    def _load_state(self):
        """📂 Load bot state from file (Repository Pattern)"""
        try:
            if not os.path.exists(self.persistence_file):
                return
            
            with open(self.persistence_file, 'r') as f:
                state_data = json.load(f)
            
            for bot_id, bot_data in state_data.get('bots', {}).items():
                config = BotConfiguration(**bot_data['config'])
                
                bot_instance = BotInstance(
                    bot_id=bot_data['bot_id'],
                    pair=bot_data['pair'],
                    status=BotStatus(bot_data['status']),
                    config=config,
                    created_at=bot_data.get('created_at'),
                    started_at=bot_data.get('started_at'),
                    stopped_at=bot_data.get('stopped_at'),
                    trade_count=bot_data.get('trade_count', 0),
                    profit_loss=bot_data.get('profit_loss', 0.0),
                    last_error=bot_data.get('last_error')
                )
                
                # Reset running bots to stopped (they were interrupted)
                if bot_instance.status in [BotStatus.RUNNING, BotStatus.STARTING, BotStatus.STOPPING]:
                    bot_instance.status = BotStatus.STOPPED
                
                self.bots[bot_id] = bot_instance
            
            logger.info(f"Loaded {len(self.bots)} bot instances from state file")
            
        except Exception as e:
            logger.error(f"Failed to load state: {e}")

class ConsoleBotObserver(BotObserver):
    """🖥️ Console observer for bot status changes (Observer Pattern)"""
    
    def on_bot_status_changed(self, bot_id: str, old_status: BotStatus, new_status: BotStatus):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] 🤖 Bot {bot_id}: {old_status.value} → {new_status.value}")
    
    def on_bot_error(self, bot_id: str, error: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] ❌ Bot {bot_id} error: {error}")

def main():
    """🚀 Test multi-bot manager"""
    print("🤖 Multi-Bot Manager Test")
    print("=" * 40)
    
    # Create manager (Singleton)
    manager = MultiBotManager()
    
    # Add console observer
    console_observer = ConsoleBotObserver()
    manager.add_observer(console_observer)
    
    # Create test configurations
    config1 = BotConfiguration(
        pair="XNY_USDT",
        budget_per_trade=50.0,
        target_profit=2.5,
        max_trades=100,
        sleep_between_cycles=1.0,
        timeout_minutes=60,
        max_daily_loss=0.10,
        min_win_rate=0.30
    )
    
    config2 = BotConfiguration(
        pair="BTC_USDT",
        budget_per_trade=100.0,
        target_profit=1.5,
        max_trades=50,
        sleep_between_cycles=2.0,
        timeout_minutes=120,
        max_daily_loss=0.05,
        min_win_rate=0.40
    )
    
    # Register bots
    bot1_id = manager.register_bot(config1)
    bot2_id = manager.register_bot(config2)
    
    print(f"Registered bot 1: {bot1_id}")
    print(f"Registered bot 2: {bot2_id}")
    
    # Show all bots
    all_bots = manager.get_all_bots()
    print(f"\nTotal bots: {len(all_bots)}")
    for bot_id, bot in all_bots.items():
        print(f"  {bot_id}: {bot.pair} - {bot.status.value}")

if __name__ == "__main__":
    main()