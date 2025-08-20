#!/usr/bin/env python3
"""
⚙️ Unified Bot Configuration System
Standardized configuration following SOLID principles and best practices
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, List
from enum import Enum
import json
import os
from datetime import datetime

class RiskLevel(Enum):
    """📊 Risk level enumeration (Type Safety)"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate" 
    AGGRESSIVE = "aggressive"
    CUSTOM = "custom"

class TradingStrategy(Enum):
    """📈 Trading strategy enumeration"""
    SCALPING = "scalping"
    SWING = "swing"
    HODL = "hodl"
    DCA_ONLY = "dca_only"

@dataclass
class SecurityConfig:
    """🛡️ Security and safety configuration (Single Responsibility)"""
    # Circuit Breaker Settings
    max_consecutive_failures: int = 5
    failure_cooldown_minutes: int = 10
    exponential_backoff_enabled: bool = True
    
    # Safety Limits
    max_daily_loss_percent: float = 10.0  # Max daily loss %
    min_win_rate_percent: float = 30.0    # Minimum win rate %
    max_drawdown_percent: float = 25.0    # Max portfolio drawdown
    
    # Position Size Limits
    max_position_size_percent: float = 20.0  # Max position size of portfolio
    min_trade_amount: float = 10.0           # Minimum trade amount USDT
    max_trade_amount: float = 1000.0         # Maximum trade amount USDT
    
    # API Rate Limiting
    max_api_calls_per_minute: int = 100
    api_timeout_seconds: int = 10
    retry_attempts: int = 3
    
    def validate(self) -> List[str]:
        """Validate security configuration"""
        errors = []
        if self.max_consecutive_failures < 1:
            errors.append("max_consecutive_failures must be >= 1")
        if not 0.1 <= self.max_daily_loss_percent <= 50:
            errors.append("max_daily_loss_percent must be between 0.1% and 50%")
        if not 1 <= self.min_win_rate_percent <= 100:
            errors.append("min_win_rate_percent must be between 1% and 100%")
        if self.min_trade_amount >= self.max_trade_amount:
            errors.append("min_trade_amount must be < max_trade_amount")
        return errors

@dataclass  
class DCAConfig:
    """📈 Dollar Cost Averaging configuration (Single Responsibility)"""
    enabled: bool = True
    
    # DCA Level 1 (Minor dip)
    level1_trigger_percent: float = -2.0    # Trigger at -2% loss
    level1_multiplier: float = 2.0          # 2x the original trade size
    level1_max_trades: int = 3              # Max 3 DCA trades at this level
    
    # DCA Level 2 (Moderate dip) 
    level2_trigger_percent: float = -5.0    # Trigger at -5% loss
    level2_multiplier: float = 3.0          # 3x the original trade size
    level2_max_trades: int = 2              # Max 2 DCA trades at this level
    
    # DCA Level 3 (Major dip - Stop Loss)
    level3_trigger_percent: float = -10.0   # Trigger at -10% loss
    level3_action: str = "stop_loss"        # Action: stop_loss or dca
    level3_multiplier: float = 0.0          # 0 = stop loss, >0 = continue DCA
    
    # Global DCA Settings
    max_total_dca_trades: int = 5           # Max total DCA trades per position
    dca_cooldown_minutes: int = 5           # Minutes between DCA trades
    
    def validate(self) -> List[str]:
        """Validate DCA configuration"""
        errors = []
        if self.level1_trigger_percent >= 0:
            errors.append("level1_trigger_percent must be negative")
        if self.level2_trigger_percent >= self.level1_trigger_percent:
            errors.append("level2_trigger_percent must be < level1_trigger_percent")
        if self.level3_trigger_percent >= self.level2_trigger_percent:
            errors.append("level3_trigger_percent must be < level2_trigger_percent")
        if self.max_total_dca_trades < 1:
            errors.append("max_total_dca_trades must be >= 1")
        return errors

@dataclass
class PerformanceConfig:
    """⚡ Performance and timing configuration (Single Responsibility)"""
    # Execution Timing
    sleep_between_cycles: float = 1.0       # Sleep between bot cycles (seconds)
    order_timeout_seconds: int = 30         # Order execution timeout
    price_update_interval: int = 5          # Price update interval (seconds)
    
    # Session Management
    max_session_duration_minutes: int = 480 # Max 8 hours per session
    auto_restart_on_error: bool = True      # Auto-restart after errors
    graceful_shutdown_timeout: int = 60     # Graceful shutdown timeout
    
    # Resource Management
    max_memory_usage_mb: int = 512          # Max memory usage
    log_rotation_size_mb: int = 10          # Log file rotation size
    cleanup_old_logs_days: int = 7          # Delete logs older than 7 days
    
    def validate(self) -> List[str]:
        """Validate performance configuration"""
        errors = []
        if not 0.1 <= self.sleep_between_cycles <= 60:
            errors.append("sleep_between_cycles must be between 0.1s and 60s")
        if self.max_session_duration_minutes < 10:
            errors.append("max_session_duration_minutes must be >= 10")
        return errors

@dataclass
class TradingConfig:
    """💰 Core trading configuration (Single Responsibility)"""
    # Basic Settings
    pair: str = ""
    budget_per_trade: float = 50.0
    target_profit_percent: float = 2.5
    max_trades_per_session: int = 100
    
    # Strategy Settings
    strategy: TradingStrategy = TradingStrategy.SCALPING
    risk_level: RiskLevel = RiskLevel.MODERATE
    
    # Profit/Loss Management
    take_profit_percent: float = 2.5        # Take profit target
    stop_loss_percent: float = 5.0          # Stop loss trigger
    trailing_stop_enabled: bool = False      # Trailing stop loss
    trailing_stop_percent: float = 1.0      # Trailing stop distance
    
    # Entry/Exit Logic
    entry_strategy: str = "market"          # market, limit, smart
    exit_strategy: str = "market"           # market, limit, smart  
    slippage_tolerance_percent: float = 0.1 # Max slippage tolerance
    
    def validate(self) -> List[str]:
        """Validate trading configuration"""
        errors = []
        if not self.pair:
            errors.append("pair is required")
        if self.budget_per_trade <= 0:
            errors.append("budget_per_trade must be > 0")
        if not 0.1 <= self.target_profit_percent <= 50:
            errors.append("target_profit_percent must be between 0.1% and 50%")
        if self.max_trades_per_session < 1:
            errors.append("max_trades_per_session must be >= 1")
        return errors

@dataclass
class UnifiedBotConfig:
    """🎯 Unified bot configuration (Composite Pattern)"""
    # Core Components
    trading: TradingConfig = field(default_factory=TradingConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    dca: DCAConfig = field(default_factory=DCAConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    
    # Metadata
    config_version: str = "1.0.0"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    created_by: str = "multi_bot_system"
    description: str = ""
    
    def validate(self) -> Dict[str, List[str]]:
        """Validate entire configuration (Composite Validation)"""
        validation_results = {
            'trading': self.trading.validate(),
            'security': self.security.validate(), 
            'dca': self.dca.validate(),
            'performance': self.performance.validate()
        }
        
        # Cross-validation between components
        cross_errors = []
        if self.trading.stop_loss_percent <= self.trading.target_profit_percent:
            cross_errors.append("stop_loss_percent should be > target_profit_percent")
        
        if self.security.max_trade_amount < self.trading.budget_per_trade:
            cross_errors.append("security.max_trade_amount should be >= trading.budget_per_trade")
        
        if cross_errors:
            validation_results['cross_validation'] = cross_errors
        
        return validation_results
    
    def is_valid(self) -> bool:
        """Check if configuration is completely valid"""
        validation = self.validate()
        return all(not errors for errors in validation.values())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (Serialization)"""
        data = asdict(self)
        
        # Convert enums to their values for JSON serialization
        if 'trading' in data:
            if 'strategy' in data['trading']:
                data['trading']['strategy'] = data['trading']['strategy'].value
            if 'risk_level' in data['trading']:
                data['trading']['risk_level'] = data['trading']['risk_level'].value
        
        return data
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def save_to_file(self, filepath: str):
        """Save configuration to file (Repository Pattern)"""
        self.updated_at = datetime.now().isoformat()
        
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_json())
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'UnifiedBotConfig':
        """Load configuration from file (Repository Pattern)"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return cls.from_dict(data)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UnifiedBotConfig':
        """Create from dictionary (Deserialization)"""
        # Extract nested configurations
        trading_data = data.get('trading', {})
        security_data = data.get('security', {})
        dca_data = data.get('dca', {})
        performance_data = data.get('performance', {})
        
        # Convert enum strings back to enum objects
        if 'strategy' in trading_data:
            trading_data['strategy'] = TradingStrategy(trading_data['strategy'])
        if 'risk_level' in trading_data:
            trading_data['risk_level'] = RiskLevel(trading_data['risk_level'])
        
        return cls(
            trading=TradingConfig(**trading_data),
            security=SecurityConfig(**security_data),
            dca=DCAConfig(**dca_data),
            performance=PerformanceConfig(**performance_data),
            config_version=data.get('config_version', '1.0.0'),
            created_at=data.get('created_at', datetime.now().isoformat()),
            updated_at=data.get('updated_at', datetime.now().isoformat()),
            created_by=data.get('created_by', 'unknown'),
            description=data.get('description', '')
        )

class ConfigurationPresets:
    """📋 Pre-defined configuration presets (Factory Pattern)"""
    
    @staticmethod
    def conservative_scalping(pair: str, budget: float = 30.0) -> UnifiedBotConfig:
        """Conservative scalping preset"""
        config = UnifiedBotConfig()
        
        # Trading
        config.trading.pair = pair
        config.trading.budget_per_trade = budget
        config.trading.target_profit_percent = 1.0
        config.trading.max_trades_per_session = 50
        config.trading.strategy = TradingStrategy.SCALPING
        config.trading.risk_level = RiskLevel.CONSERVATIVE
        config.trading.stop_loss_percent = 3.0
        
        # Security (Conservative)
        config.security.max_daily_loss_percent = 5.0
        config.security.min_win_rate_percent = 40.0
        config.security.max_consecutive_failures = 3
        config.security.max_drawdown_percent = 15.0
        
        # DCA (Minimal)
        config.dca.level1_trigger_percent = -1.5
        config.dca.level2_trigger_percent = -3.0
        config.dca.level3_trigger_percent = -5.0
        config.dca.max_total_dca_trades = 3
        
        # Performance (Slow)
        config.performance.sleep_between_cycles = 2.0
        config.performance.max_session_duration_minutes = 240
        
        config.description = f"Conservative scalping for {pair}"
        return config
    
    @staticmethod
    def aggressive_scalping(pair: str, budget: float = 100.0) -> UnifiedBotConfig:
        """Aggressive scalping preset"""
        config = UnifiedBotConfig()
        
        # Trading
        config.trading.pair = pair
        config.trading.budget_per_trade = budget
        config.trading.target_profit_percent = 3.0
        config.trading.max_trades_per_session = 200
        config.trading.strategy = TradingStrategy.SCALPING
        config.trading.risk_level = RiskLevel.AGGRESSIVE
        config.trading.stop_loss_percent = 8.0
        
        # Security (Relaxed)
        config.security.max_daily_loss_percent = 15.0
        config.security.min_win_rate_percent = 25.0
        config.security.max_consecutive_failures = 8
        config.security.max_drawdown_percent = 35.0
        
        # DCA (Aggressive)
        config.dca.level1_trigger_percent = -3.0
        config.dca.level2_trigger_percent = -7.0
        config.dca.level3_trigger_percent = -12.0
        config.dca.max_total_dca_trades = 7
        
        # Performance (Fast)
        config.performance.sleep_between_cycles = 0.5
        config.performance.max_session_duration_minutes = 720
        
        config.description = f"Aggressive scalping for {pair}"
        return config
    
    @staticmethod
    def moderate_swing(pair: str, budget: float = 75.0) -> UnifiedBotConfig:
        """Moderate swing trading preset"""
        config = UnifiedBotConfig()
        
        # Trading
        config.trading.pair = pair
        config.trading.budget_per_trade = budget
        config.trading.target_profit_percent = 5.0
        config.trading.max_trades_per_session = 20
        config.trading.strategy = TradingStrategy.SWING
        config.trading.risk_level = RiskLevel.MODERATE
        config.trading.stop_loss_percent = 10.0
        
        # Security (Balanced)
        config.security.max_daily_loss_percent = 10.0
        config.security.min_win_rate_percent = 35.0
        config.security.max_consecutive_failures = 5
        config.security.max_drawdown_percent = 25.0
        
        # DCA (Moderate)
        config.dca.level1_trigger_percent = -4.0
        config.dca.level2_trigger_percent = -8.0
        config.dca.level3_trigger_percent = -15.0
        config.dca.max_total_dca_trades = 5
        
        # Performance (Medium)
        config.performance.sleep_between_cycles = 5.0
        config.performance.max_session_duration_minutes = 1440  # 24 hours
        
        config.description = f"Moderate swing trading for {pair}"
        return config
    
    @staticmethod
    def get_preset_by_name(name: str, pair: str, budget: float) -> Optional[UnifiedBotConfig]:
        """Get preset by name (Factory Method)"""
        presets = {
            'conservative': ConfigurationPresets.conservative_scalping,
            'aggressive': ConfigurationPresets.aggressive_scalping,
            'moderate': ConfigurationPresets.moderate_swing
        }
        
        preset_func = presets.get(name.lower())
        if preset_func:
            return preset_func(pair, budget)
        return None
    
    @staticmethod
    def list_presets() -> List[str]:
        """List available presets"""
        return ['conservative', 'aggressive', 'moderate']

def main():
    """🧪 Test unified configuration system"""
    print("⚙️ Unified Bot Configuration System Test")
    print("=" * 50)
    
    # Test presets
    print("📋 Testing presets:")
    for preset_name in ConfigurationPresets.list_presets():
        config = ConfigurationPresets.get_preset_by_name(preset_name, "XNY_USDT", 50.0)
        print(f"✅ {preset_name.title()}: {config.trading.target_profit_percent}% target, "
              f"{config.security.max_daily_loss_percent}% max loss")
    
    # Test validation
    print(f"\n🔍 Testing validation:")
    config = ConfigurationPresets.conservative_scalping("BTC_USDT", 100.0)
    validation = config.validate()
    
    if config.is_valid():
        print("✅ Configuration is valid")
    else:
        print("❌ Configuration has errors:")
        for component, errors in validation.items():
            if errors:
                print(f"  {component}: {errors}")
    
    # Test serialization
    print(f"\n💾 Testing serialization:")
    json_config = config.to_json()
    print(f"JSON size: {len(json_config)} characters")
    
    # Test save/load
    filepath = "test_config.json"
    config.save_to_file(filepath)
    loaded_config = UnifiedBotConfig.load_from_file(filepath)
    
    if loaded_config.trading.pair == config.trading.pair:
        print("✅ Save/Load works correctly")
        os.remove(filepath)  # Cleanup
    else:
        print("❌ Save/Load failed")
    
    print(f"\n🎉 Configuration system ready!")

if __name__ == "__main__":
    main()