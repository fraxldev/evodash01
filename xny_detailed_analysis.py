#!/usr/bin/env python3
"""
📊 XNY_USDT Detailed Analysis & Bot Configuration Report
Advanced market analysis following SOLID principles
"""

import requests
import statistics
from datetime import datetime, timedelta
from typing import List, Dict
import json

class XNYAnalysisEngine:
    """🔬 Advanced XNY analysis engine (Single Responsibility)"""
    
    def __init__(self):
        self.base_url = "https://api.gateio.ws/api/v4"
        self.symbol = "XNY_USDT"
    
    def get_comprehensive_data(self) -> Dict:
        """📊 Fetch comprehensive market data"""
        try:
            # Get multiple timeframes
            data = {
                'current_price': self._get_ticker(),
                'hourly_candles': self._get_candles("1h", 168),  # 7 days
                'daily_candles': self._get_candles("1d", 30),    # 30 days
                '15min_candles': self._get_candles("15m", 96),   # 24 hours
                'order_book': self._get_order_book(),
                'recent_trades': self._get_recent_trades()
            }
            return data
        except Exception as e:
            print(f"❌ Error fetching data: {e}")
            return {}
    
    def _get_ticker(self) -> Dict:
        """💱 Get current ticker data"""
        url = f"{self.base_url}/spot/tickers"
        params = {'currency_pair': self.symbol}
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        return data[0] if data else {}
    
    def _get_candles(self, interval: str, limit: int) -> List:
        """📊 Get candlestick data"""
        url = f"{self.base_url}/spot/candlesticks"
        params = {
            'currency_pair': self.symbol,
            'interval': interval,
            'limit': limit
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        return response.json()
    
    def _get_order_book(self) -> Dict:
        """📖 Get order book depth"""
        url = f"{self.base_url}/spot/order_book"
        params = {'currency_pair': self.symbol, 'limit': 20}
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        
        return response.json()
    
    def _get_recent_trades(self) -> List:
        """💹 Get recent trades"""
        url = f"{self.base_url}/spot/trades"
        params = {'currency_pair': self.symbol, 'limit': 100}
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        
        return response.json()

class ScalpingOptimizer:
    """🤖 Scalping strategy optimizer (Strategy Pattern)"""
    
    def analyze_scalping_opportunities(self, data: Dict) -> Dict:
        """🎯 Analyze scalping opportunities"""
        if not data.get('15min_candles'):
            return {}
        
        candles = data['15min_candles']
        
        # Convert candle data
        prices = []
        volumes = []
        ranges = []
        
        for candle in candles:
            close = float(candle[2])
            high = float(candle[3])
            low = float(candle[4])
            volume = float(candle[1])
            
            prices.append(close)
            volumes.append(volume)
            ranges.append(((high - low) / low) * 100)
        
        analysis = {
            'volatility_15min': {
                'avg_range': statistics.mean(ranges),
                'max_range': max(ranges),
                'min_range': min(ranges),
                'range_std': statistics.stdev(ranges) if len(ranges) > 1 else 0
            },
            'volume_analysis': {
                'avg_volume': statistics.mean(volumes),
                'volume_trend': 'INCREASING' if volumes[-5:] > volumes[:5] else 'DECREASING',
                'volume_spikes': len([v for v in volumes if v > statistics.mean(volumes) * 2])
            },
            'price_momentum': {
                'short_term_trend': 'BULLISH' if prices[-5] > prices[-10] else 'BEARISH',
                'price_acceleration': self._calculate_acceleration(prices),
                'support_resistance': self._find_sr_levels(prices)
            }
        }
        
        return analysis
    
    def _calculate_acceleration(self, prices: List[float]) -> str:
        """📈 Calculate price acceleration"""
        if len(prices) < 10:
            return "INSUFFICIENT_DATA"
        
        recent_slope = (prices[-1] - prices[-5]) / 5
        previous_slope = (prices[-5] - prices[-10]) / 5
        
        if recent_slope > previous_slope * 1.2:
            return "ACCELERATING_UP"
        elif recent_slope < previous_slope * 0.8:
            return "ACCELERATING_DOWN"
        else:
            return "STABLE"
    
    def _find_sr_levels(self, prices: List[float]) -> Dict:
        """🔍 Find support and resistance levels"""
        sorted_prices = sorted(prices)
        length = len(sorted_prices)
        
        return {
            'strong_support': sorted_prices[int(length * 0.1)],
            'support': sorted_prices[int(length * 0.25)],
            'resistance': sorted_prices[int(length * 0.75)],
            'strong_resistance': sorted_prices[int(length * 0.9)]
        }

class BotConfigGenerator:
    """⚙️ Bot configuration generator (Builder Pattern)"""
    
    def generate_optimal_config(self, market_data: Dict, scalping_analysis: Dict) -> Dict:
        """🔧 Generate optimal bot configuration"""
        
        # Base configuration
        config = {
            'basic_settings': {},
            'risk_management': {},
            'timing_settings': {},
            'advanced_settings': {},
            'explanation': []
        }
        
        # Analyze current conditions
        current_price = float(market_data['current_price']['last'])
        daily_change = float(market_data['current_price']['change_percentage'])
        
        # Basic Settings
        volatility = scalping_analysis.get('volatility_15min', {})
        avg_range = volatility.get('avg_range', 5)
        
        if avg_range > 8:
            # High volatility
            config['basic_settings'] = {
                'profit_target_percent': 1.8,
                'trade_amount_usdt': 30,
                'max_trades_per_session': 150
            }
            config['explanation'].append("🔥 Alta volatilità: target bassi, trade frequenti")
        elif avg_range > 4:
            # Medium volatility
            config['basic_settings'] = {
                'profit_target_percent': 2.5,
                'trade_amount_usdt': 50,
                'max_trades_per_session': 100
            }
            config['explanation'].append("⚖️ Volatilità media: bilanciato risk/reward")
        else:
            # Low volatility
            config['basic_settings'] = {
                'profit_target_percent': 3.5,
                'trade_amount_usdt': 80,
                'max_trades_per_session': 50
            }
            config['explanation'].append("😴 Bassa volatilità: target alti, meno trade")
        
        # Risk Management
        config['risk_management'] = {
            'max_daily_loss_percent': min(15, avg_range * 1.5),
            'stop_loss_percent': avg_range * 0.8,
            'max_drawdown_percent': 25,
            'circuit_breaker_losses': 5
        }
        
        # Timing Settings
        momentum = scalping_analysis.get('price_momentum', {})
        if momentum.get('price_acceleration') == 'ACCELERATING_UP':
            config['timing_settings'] = {
                'entry_delay_seconds': 2,
                'exit_speed': 'FAST',
                'cycle_frequency': 'AGGRESSIVE'
            }
            config['explanation'].append("🚀 Momentum positivo: entrate rapide")
        elif momentum.get('price_acceleration') == 'ACCELERATING_DOWN':
            config['timing_settings'] = {
                'entry_delay_seconds': 8,
                'exit_speed': 'CAUTIOUS',
                'cycle_frequency': 'CONSERVATIVE'
            }
            config['explanation'].append("📉 Momentum negativo: cautela")
        else:
            config['timing_settings'] = {
                'entry_delay_seconds': 5,
                'exit_speed': 'MODERATE',
                'cycle_frequency': 'BALANCED'
            }
        
        # Advanced Settings
        volume_data = scalping_analysis.get('volume_analysis', {})
        config['advanced_settings'] = {
            'dca_enabled': True,
            'dca_level1_trigger': -2.5,
            'dca_level2_trigger': -6.0,
            'volume_filter_enabled': volume_data.get('volume_spikes', 0) > 3,
            'trend_following': momentum.get('short_term_trend') == 'BULLISH'
        }
        
        return config

def main():
    """🚀 Main analysis function"""
    print("🎯 XNY_USDT - ANALISI DETTAGLIATA PER BOT SCALPING")
    print("=" * 65)
    
    # Initialize analyzer
    analyzer = XNYAnalysisEngine()
    optimizer = ScalpingOptimizer()
    config_generator = BotConfigGenerator()
    
    print("📊 Raccogliendo dati di mercato...")
    
    # Get comprehensive data
    market_data = analyzer.get_comprehensive_data()
    
    if not market_data:
        print("❌ Impossibile ottenere i dati di mercato")
        return
    
    print("✅ Dati raccolti con successo!")
    
    # Current market status
    ticker = market_data['current_price']
    current_price = float(ticker['last'])
    daily_change = float(ticker['change_percentage'])
    volume_24h = float(ticker['quote_volume'])
    
    print(f"\n💱 STATO ATTUALE DEL MERCATO:")
    print(f"   Prezzo: ${current_price:.8f}")
    print(f"   Variazione 24h: {daily_change:+.2f}%")
    print(f"   Volume 24h: ${volume_24h:,.0f} USDT")
    print(f"   High 24h: ${float(ticker['high_24h']):.8f}")
    print(f"   Low 24h: ${float(ticker['low_24h']):.8f}")
    
    # Analyze scalping opportunities
    print(f"\n🔬 ANALISI OPPORTUNITÀ SCALPING:")
    scalping_analysis = optimizer.analyze_scalping_opportunities(market_data)
    
    if scalping_analysis:
        vol_data = scalping_analysis['volatility_15min']
        print(f"   📊 Range medio 15min: {vol_data['avg_range']:.2f}%")
        print(f"   📈 Range massimo: {vol_data['max_range']:.2f}%")
        print(f"   📉 Range minimo: {vol_data['min_range']:.2f}%")
        
        volume_data = scalping_analysis['volume_analysis']
        print(f"   💹 Volume medio: {volume_data['avg_volume']:,.0f}")
        print(f"   📊 Trend volume: {volume_data['volume_trend']}")
        
        momentum = scalping_analysis['price_momentum']
        print(f"   🎯 Trend breve: {momentum['short_term_trend']}")
        print(f"   ⚡ Accelerazione: {momentum['price_acceleration']}")
        
        sr_levels = momentum['support_resistance']
        print(f"   🔻 Supporto: ${sr_levels['support']:.8f}")
        print(f"   🔺 Resistenza: ${sr_levels['resistance']:.8f}")
    
    # Generate optimal configuration
    print(f"\n🤖 CONFIGURAZIONE OTTIMALE DEL BOT:")
    print("=" * 45)
    
    optimal_config = config_generator.generate_optimal_config(market_data, scalping_analysis)
    
    basic = optimal_config['basic_settings']
    risk = optimal_config['risk_management']
    timing = optimal_config['timing_settings']
    advanced = optimal_config['advanced_settings']
    
    print(f"📊 IMPOSTAZIONI BASE:")
    print(f"   🎯 Target profitto: {basic['profit_target_percent']:.1f}%")
    print(f"   💰 Importo per trade: ${basic['trade_amount_usdt']} USDT")
    print(f"   🔄 Max trades/sessione: {basic['max_trades_per_session']}")
    
    print(f"\n🛡️ GESTIONE RISCHIO:")
    print(f"   📉 Max perdita giornaliera: {risk['max_daily_loss_percent']:.1f}%")
    print(f"   🚨 Stop loss: {risk['stop_loss_percent']:.1f}%")
    print(f"   🔥 Circuit breaker: {risk['circuit_breaker_losses']} perdite")
    
    print(f"\n⏰ TIMING:")
    print(f"   ⏱️ Ritardo entrata: {timing['entry_delay_seconds']}s")
    print(f"   🚀 Velocità uscita: {timing['exit_speed']}")
    print(f"   📊 Frequenza cicli: {timing['cycle_frequency']}")
    
    print(f"\n🔧 IMPOSTAZIONI AVANZATE:")
    print(f"   📈 DCA attivo: {'✅' if advanced['dca_enabled'] else '❌'}")
    print(f"   📊 DCA Livello 1: {advanced['dca_level1_trigger']:.1f}%")
    print(f"   📉 DCA Livello 2: {advanced['dca_level2_trigger']:.1f}%")
    print(f"   📈 Filtro volume: {'✅' if advanced['volume_filter_enabled'] else '❌'}")
    print(f"   🎯 Trend following: {'✅' if advanced['trend_following'] else '❌'}")
    
    print(f"\n💡 SPIEGAZIONE STRATEGIA:")
    for explanation in optimal_config['explanation']:
        print(f"   • {explanation}")
    
    # Trading session recommendations
    print(f"\n⏰ RACCOMANDAZIONI ORARI:")
    print(f"   🟢 Orari migliori: 14:00-18:00 UTC (mercati EU/US attivi)")
    print(f"   🟡 Orari medi: 08:00-14:00 UTC (mercati asiatici)")
    print(f"   🔴 Evitare: 00:00-06:00 UTC (bassa liquidità)")
    
    # Final recommendations
    print(f"\n🎯 RACCOMANDAZIONI FINALI:")
    print(f"   1. 🧪 Inizia con importi bassi per testare")
    print(f"   2. 📊 Monitora performance per primi 20 trade")
    print(f"   3. ⚖️ Regola parametri in base ai risultati")
    print(f"   4. 🛑 Usa sempre stop loss e circuit breaker")
    print(f"   5. 📈 Approfitta dei momenti di alta volatilità")
    
    # Risk warnings
    print(f"\n⚠️ AVVERTENZE RISCHIO:")
    print(f"   • XNY mostra volatilità elevata (±{vol_data.get('avg_range', 5):.1f}% range)")
    print(f"   • Possibili perdite rapide in caso di trend improvvisi")
    print(f"   • Monitorare sempre liquidità e spread")
    print(f"   • Non investire mai più del 5% del portafoglio totale")

if __name__ == "__main__":
    main()