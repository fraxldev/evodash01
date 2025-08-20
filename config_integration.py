#!/usr/bin/env python3
"""
🔧 Configuration Integration Module
Integrates unified configuration system with existing bot infrastructure
"""

import sys
import os
from typing import Dict, Any, Optional, Tuple

# Add current directory for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from unified_bot_config import (
    UnifiedBotConfig, ConfigurationPresets, TradingStrategy, RiskLevel,
    TradingConfig, SecurityConfig, DCAConfig, PerformanceConfig
)

class ConfigurationWizard:
    """🧙 Interactive configuration wizard (Wizard Pattern)"""
    
    @staticmethod
    def interactive_configuration(pair: str = "") -> Optional[UnifiedBotConfig]:
        """Create configuration through interactive wizard"""
        print("\n🧙 CONFIGURAZIONE GUIDATA BOT AVANZATA")
        print("=" * 45)
        
        try:
            # Step 1: Basic Trading Setup
            print("\n📊 STEP 1/5 - CONFIGURAZIONE BASE")
            print("-" * 35)
            
            if not pair:
                pair = input("📈 Coppia di trading (es. XNY_USDT): ").strip().upper()
                if not pair:
                    print("❌ Coppia richiesta")
                    return None
            
            # Show presets
            print(f"\n🎯 PRESET DISPONIBILI per {pair}:")
            presets = ConfigurationPresets.list_presets()
            print("   0. ⚙️  Configurazione personalizzata")
            for i, preset in enumerate(presets, 1):
                print(f"   {i}. 📋 {preset.title()}")
            
            try:
                preset_choice = int(input(f"\nScegli preset (0-{len(presets)}): ") or "0")
                
                if preset_choice > 0 and preset_choice <= len(presets):
                    # Use preset as base
                    preset_name = presets[preset_choice - 1]
                    budget = float(input("💰 Budget per trade ($): ") or "50")
                    config = ConfigurationPresets.get_preset_by_name(preset_name, pair, budget)
                    
                    print(f"✅ Preset '{preset_name}' caricato come base")
                    
                    # Ask if user wants to customize
                    customize = input("🔧 Vuoi personalizzare il preset? (s/n): ").lower()
                    if customize != 's':
                        return config
                else:
                    # Custom configuration
                    config = UnifiedBotConfig()
                    config.trading.pair = pair
                    print("⚙️  Configurazione personalizzata selezionata")
                
            except ValueError:
                print("❌ Input non valido, uso configurazione personalizzata")
                config = UnifiedBotConfig()
                config.trading.pair = pair
            
            # Step 2: Advanced Trading Configuration
            print("\n📈 STEP 2/5 - TRADING AVANZATO")
            print("-" * 32)
            
            config.trading.budget_per_trade = float(input(
                f"💰 Budget per trade [attuale: ${config.trading.budget_per_trade}]: ") 
                or config.trading.budget_per_trade)
            
            config.trading.target_profit_percent = float(input(
                f"🎯 Target profitto % [attuale: {config.trading.target_profit_percent}]: ") 
                or config.trading.target_profit_percent)
            
            config.trading.max_trades_per_session = int(input(
                f"🔢 Max trades/sessione [attuale: {config.trading.max_trades_per_session}]: ") 
                or config.trading.max_trades_per_session)
            
            config.trading.stop_loss_percent = float(input(
                f"🛑 Stop loss % [attuale: {config.trading.stop_loss_percent}]: ") 
                or config.trading.stop_loss_percent)
            
            # Step 3: Security Configuration
            print("\n🛡️  STEP 3/5 - SICUREZZA E RISK MANAGEMENT")
            print("-" * 40)
            
            config.security.max_daily_loss_percent = float(input(
                f"📉 Max perdita giornaliera % [attuale: {config.security.max_daily_loss_percent}]: ") 
                or config.security.max_daily_loss_percent)
            
            config.security.min_win_rate_percent = float(input(
                f"📊 Min win rate % [attuale: {config.security.min_win_rate_percent}]: ") 
                or config.security.min_win_rate_percent)
            
            config.security.max_consecutive_failures = int(input(
                f"🔒 Max fallimenti consecutivi [attuale: {config.security.max_consecutive_failures}]: ") 
                or config.security.max_consecutive_failures)
            
            config.security.max_drawdown_percent = float(input(
                f"📊 Max drawdown % [attuale: {config.security.max_drawdown_percent}]: ") 
                or config.security.max_drawdown_percent)
            
            # Step 4: DCA Configuration
            print("\n📈 STEP 4/5 - DOLLAR COST AVERAGING (DCA)")
            print("-" * 40)
            
            dca_enabled = input(
                f"🔄 Abilitare DCA? [attuale: {'Sì' if config.dca.enabled else 'No'}] (s/n): ")
            if dca_enabled.lower() in ['s', 'y']:
                config.dca.enabled = True
                
                config.dca.level1_trigger_percent = float(input(
                    f"📉 DCA Livello 1 trigger % [attuale: {config.dca.level1_trigger_percent}]: ") 
                    or config.dca.level1_trigger_percent)
                
                config.dca.level1_multiplier = float(input(
                    f"📊 DCA Livello 1 moltiplicatore [attuale: {config.dca.level1_multiplier}x]: ") 
                    or config.dca.level1_multiplier)
                
                config.dca.level2_trigger_percent = float(input(
                    f"📉 DCA Livello 2 trigger % [attuale: {config.dca.level2_trigger_percent}]: ") 
                    or config.dca.level2_trigger_percent)
                
                config.dca.level2_multiplier = float(input(
                    f"📊 DCA Livello 2 moltiplicatore [attuale: {config.dca.level2_multiplier}x]: ") 
                    or config.dca.level2_multiplier)
                
                config.dca.level3_trigger_percent = float(input(
                    f"🛑 Stop Loss trigger % [attuale: {config.dca.level3_trigger_percent}]: ") 
                    or config.dca.level3_trigger_percent)
                
                config.dca.max_total_dca_trades = int(input(
                    f"🔢 Max DCA trades totali [attuale: {config.dca.max_total_dca_trades}]: ") 
                    or config.dca.max_total_dca_trades)
                
            elif dca_enabled.lower() in ['n', 'no']:
                config.dca.enabled = False
            
            # Step 5: Performance Configuration
            print("\n⚡ STEP 5/5 - PERFORMANCE E TIMING")
            print("-" * 35)
            
            config.performance.sleep_between_cycles = float(input(
                f"⏱️  Pausa tra cicli (s) [attuale: {config.performance.sleep_between_cycles}]: ") 
                or config.performance.sleep_between_cycles)
            
            config.performance.max_session_duration_minutes = int(input(
                f"⏰ Durata max sessione (min) [attuale: {config.performance.max_session_duration_minutes}]: ") 
                or config.performance.max_session_duration_minutes)
            
            # Add description
            config.description = f"Custom configuration for {pair} via wizard"
            
            return config
            
        except (EOFError, KeyboardInterrupt):
            print("\n❌ Configurazione annullata")
            return None
        except Exception as e:
            print(f"\n❌ Errore nella configurazione: {e}")
            return None
    
    @staticmethod
    def display_configuration_summary(config: UnifiedBotConfig):
        """Display configuration summary"""
        print(f"\n📋 RIEPILOGO CONFIGURAZIONE COMPLETA:")
        print("=" * 50)
        
        # Trading
        print(f"📈 TRADING:")
        print(f"   Coppia: {config.trading.pair}")
        print(f"   Budget/trade: ${config.trading.budget_per_trade}")
        print(f"   Target: {config.trading.target_profit_percent}%")
        print(f"   Stop Loss: {config.trading.stop_loss_percent}%")
        print(f"   Max trades: {config.trading.max_trades_per_session}")
        print(f"   Strategia: {config.trading.strategy.value}")
        print(f"   Risk Level: {config.trading.risk_level.value}")
        
        # Security
        print(f"\n🛡️  SICUREZZA:")
        print(f"   Max perdita giornaliera: {config.security.max_daily_loss_percent}%")
        print(f"   Min win rate: {config.security.min_win_rate_percent}%")
        print(f"   Max fallimenti consecutivi: {config.security.max_consecutive_failures}")
        print(f"   Max drawdown: {config.security.max_drawdown_percent}%")
        print(f"   Circuit breaker: {'Attivo' if config.security.exponential_backoff_enabled else 'Disattivo'}")
        
        # DCA
        print(f"\n📈 DCA SYSTEM:")
        if config.dca.enabled:
            print(f"   Status: ✅ ATTIVO")
            print(f"   Livello 1: {config.dca.level1_trigger_percent}% → {config.dca.level1_multiplier}x")
            print(f"   Livello 2: {config.dca.level2_trigger_percent}% → {config.dca.level2_multiplier}x")
            print(f"   Stop Loss: {config.dca.level3_trigger_percent}%")
            print(f"   Max DCA trades: {config.dca.max_total_dca_trades}")
        else:
            print(f"   Status: ❌ DISATTIVO")
        
        # Performance  
        print(f"\n⚡ PERFORMANCE:")
        print(f"   Pausa cicli: {config.performance.sleep_between_cycles}s")
        print(f"   Max sessione: {config.performance.max_session_duration_minutes} min")
        print(f"   Auto-restart: {'Sì' if config.performance.auto_restart_on_error else 'No'}")
        
        print("=" * 50)
    
    @staticmethod
    def validate_and_confirm(config: UnifiedBotConfig) -> bool:
        """Validate configuration and get user confirmation"""
        print("\n🔍 VALIDAZIONE CONFIGURAZIONE:")
        print("-" * 35)
        
        validation = config.validate()
        has_errors = False
        
        for component, errors in validation.items():
            if errors:
                has_errors = True
                print(f"❌ {component.upper()}:")
                for error in errors:
                    print(f"   • {error}")
        
        if not has_errors:
            print("✅ Configurazione valida!")
        else:
            print("\n⚠️  Configurazione ha degli errori. Correggere prima di procedere.")
            return False
        
        ConfigurationWizard.display_configuration_summary(config)
        
        confirm = input(f"\n🔥 CONFERMARE QUESTA CONFIGURAZIONE? (s/n): ").lower()
        return confirm in ['s', 'si', 'y', 'yes']

class LegacyConfigConverter:
    """🔄 Legacy configuration converter (Adapter Pattern)"""
    
    @staticmethod
    def from_legacy_params(
        pair: str,
        budget_per_trade: float,
        target_profit: float, 
        max_trades: int,
        sleep_cycles: float,
        timeout_minutes: int,
        max_daily_loss: float,
        min_win_rate: float
    ) -> UnifiedBotConfig:
        """Convert legacy parameters to unified configuration"""
        config = UnifiedBotConfig()
        
        # Trading
        config.trading.pair = pair
        config.trading.budget_per_trade = budget_per_trade
        config.trading.target_profit_percent = target_profit
        config.trading.max_trades_per_session = max_trades
        
        # Security
        config.security.max_daily_loss_percent = max_daily_loss * 100 if max_daily_loss < 1 else max_daily_loss
        config.security.min_win_rate_percent = min_win_rate * 100 if min_win_rate < 1 else min_win_rate
        
        # Performance
        config.performance.sleep_between_cycles = sleep_cycles
        config.performance.max_session_duration_minutes = timeout_minutes
        
        # Set description
        config.description = f"Converted from legacy parameters for {pair}"
        
        return config
    
    @staticmethod
    def to_legacy_params(config: UnifiedBotConfig) -> Dict[str, Any]:
        """Convert unified configuration to legacy parameters"""
        return {
            'pair': config.trading.pair,
            'usdt_per_trade': config.trading.budget_per_trade,
            'target_net_percent': config.trading.target_profit_percent,
            'max_trades': config.trading.max_trades_per_session,
            'sleep_between_cycles': config.performance.sleep_between_cycles,
            'timeout_minutes': config.performance.max_session_duration_minutes,
            'max_daily_loss': config.security.max_daily_loss_percent / 100,
            'min_win_rate': config.security.min_win_rate_percent / 100,
            
            # DCA parameters
            'enable_dca': config.dca.enabled,
            'dca_level1_trigger': config.dca.level1_trigger_percent,
            'dca_level1_multiplier': config.dca.level1_multiplier,
            'dca_level2_trigger': config.dca.level2_trigger_percent,
            'dca_level2_multiplier': config.dca.level2_multiplier,
            'dca_stop_loss_trigger': config.dca.level3_trigger_percent,
            
            # Security parameters
            'max_consecutive_failures': config.security.max_consecutive_failures,
            'circuit_breaker_enabled': config.security.exponential_backoff_enabled
        }

def main():
    """🧪 Test configuration integration"""
    print("🔧 Configuration Integration Test")
    print("=" * 40)
    
    # Test wizard
    config = ConfigurationWizard.interactive_configuration("TEST_USDT")
    if config:
        print("\n✅ Wizard completed successfully")
        
        # Test validation
        if ConfigurationWizard.validate_and_confirm(config):
            print("✅ Configuration confirmed")
            
            # Test legacy conversion
            legacy_params = LegacyConfigConverter.to_legacy_params(config)
            print(f"✅ Legacy conversion: {len(legacy_params)} parameters")
        else:
            print("❌ Configuration rejected")
    else:
        print("❌ Wizard cancelled")

if __name__ == "__main__":
    main()