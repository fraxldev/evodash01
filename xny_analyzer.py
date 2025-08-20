#!/usr/bin/env python3
"""
🔬 XNY_USDT Price Analysis Module
Follows SOLID principles for market analysis and bot optimization
"""

import os
import sys
import requests
import json
import time
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class PriceData:
    """📊 Price data structure (Single Responsibility)"""
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float

@dataclass
class VolatilityMetrics:
    """📈 Volatility analysis results (Interface Segregation)"""
    avg_daily_range: float
    max_daily_range: float
    min_daily_range: float
    volatility_percent: float
    trend_direction: str
    support_level: float
    resistance_level: float

@dataclass
class BotRecommendation:
    """🤖 Bot configuration recommendations (Dependency Inversion)"""
    optimal_profit_target: float
    max_loss_threshold: float
    recommended_trade_size: float
    cycle_frequency: str
    risk_level: str
    confidence_score: float

class MarketDataInterface:
    """🔌 Interface for market data sources (Interface Segregation)"""
    def get_candlestick_data(self, symbol: str, interval: str, limit: int) -> List[PriceData]:
        raise NotImplementedError
    
    def get_current_price(self, symbol: str) -> float:
        raise NotImplementedError

class GateIOMarketData(MarketDataInterface):
    """🏭 Gate.io market data implementation (Factory Pattern)"""
    
    def __init__(self):
        self.base_url = "https://api.gateio.ws/api/v4"
        
    def get_candlestick_data(self, symbol: str, interval: str = "1h", limit: int = 100) -> List[PriceData]:
        """📊 Fetch candlestick data from Gate.io API"""
        try:
            url = f"{self.base_url}/spot/candlesticks"
            params = {
                'currency_pair': symbol,
                'interval': interval,
                'limit': limit
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            price_data = []
            
            for candle in data:
                price_data.append(PriceData(
                    timestamp=int(candle[0]),
                    volume=float(candle[1]),
                    close=float(candle[2]),
                    high=float(candle[3]),
                    low=float(candle[4]),
                    open=float(candle[5])
                ))
            
            return sorted(price_data, key=lambda x: x.timestamp)
            
        except Exception as e:
            print(f"❌ Error fetching candlestick data: {e}")
            return []
    
    def get_current_price(self, symbol: str) -> float:
        """💱 Get current ticker price"""
        try:
            url = f"{self.base_url}/spot/tickers"
            params = {'currency_pair': symbol}
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            if data:
                return float(data[0]['last'])
            return 0.0
            
        except Exception as e:
            print(f"❌ Error fetching current price: {e}")
            return 0.0

class PriceAnalyzer:
    """🔬 Price analysis engine (Strategy Pattern)"""
    
    def __init__(self, market_data: MarketDataInterface):
        self.market_data = market_data
    
    def calculate_volatility_metrics(self, price_data: List[PriceData]) -> VolatilityMetrics:
        """📈 Calculate comprehensive volatility metrics"""
        if len(price_data) < 2:
            return VolatilityMetrics(0, 0, 0, 0, "UNKNOWN", 0, 0)
        
        # Calculate daily ranges
        daily_ranges = []
        closing_prices = []
        
        for candle in price_data:
            daily_range = ((candle.high - candle.low) / candle.low) * 100
            daily_ranges.append(daily_range)
            closing_prices.append(candle.close)
        
        # Volatility metrics
        avg_daily_range = statistics.mean(daily_ranges)
        max_daily_range = max(daily_ranges)
        min_daily_range = min(daily_ranges)
        
        # Price volatility (standard deviation)
        price_volatility = (statistics.stdev(closing_prices) / statistics.mean(closing_prices)) * 100
        
        # Trend analysis
        first_half = closing_prices[:len(closing_prices)//2]
        second_half = closing_prices[len(closing_prices)//2:]
        
        first_avg = statistics.mean(first_half)
        second_avg = statistics.mean(second_half)
        
        trend_direction = "BULLISH" if second_avg > first_avg else "BEARISH"
        
        # Support and resistance levels
        support_level = min(closing_prices[-20:]) if len(closing_prices) >= 20 else min(closing_prices)
        resistance_level = max(closing_prices[-20:]) if len(closing_prices) >= 20 else max(closing_prices)
        
        return VolatilityMetrics(
            avg_daily_range=avg_daily_range,
            max_daily_range=max_daily_range,
            min_daily_range=min_daily_range,
            volatility_percent=price_volatility,
            trend_direction=trend_direction,
            support_level=support_level,
            resistance_level=resistance_level
        )
    
    def analyze_price_patterns(self, price_data: List[PriceData]) -> Dict:
        """🔍 Analyze price patterns for bot optimization"""
        if len(price_data) < 10:
            return {}
        
        patterns = {
            'consecutive_gains': 0,
            'consecutive_losses': 0,
            'max_gain_sequence': 0,
            'max_loss_sequence': 0,
            'gain_loss_ratio': 0,
            'avg_gain_percent': 0,
            'avg_loss_percent': 0
        }
        
        gains = []
        losses = []
        current_gain_streak = 0
        current_loss_streak = 0
        max_gain_streak = 0
        max_loss_streak = 0
        
        for i in range(1, len(price_data)):
            prev_close = price_data[i-1].close
            curr_close = price_data[i].close
            change_percent = ((curr_close - prev_close) / prev_close) * 100
            
            if change_percent > 0:
                gains.append(change_percent)
                current_gain_streak += 1
                current_loss_streak = 0
                max_gain_streak = max(max_gain_streak, current_gain_streak)
            else:
                losses.append(abs(change_percent))
                current_loss_streak += 1
                current_gain_streak = 0
                max_loss_streak = max(max_loss_streak, current_loss_streak)
        
        patterns['max_gain_sequence'] = max_gain_streak
        patterns['max_loss_sequence'] = max_loss_streak
        patterns['gain_loss_ratio'] = len(gains) / len(losses) if losses else float('inf')
        patterns['avg_gain_percent'] = statistics.mean(gains) if gains else 0
        patterns['avg_loss_percent'] = statistics.mean(losses) if losses else 0
        
        return patterns

class BotOptimizer:
    """🤖 Bot configuration optimizer (Template Method Pattern)"""
    
    def __init__(self, analyzer: PriceAnalyzer):
        self.analyzer = analyzer
    
    def generate_recommendations(self, symbol: str) -> BotRecommendation:
        """🎯 Generate optimal bot configuration"""
        
        # Fetch different timeframe data
        hourly_data = self.analyzer.market_data.get_candlestick_data(symbol, "1h", 168)  # 7 days
        daily_data = self.analyzer.market_data.get_candlestick_data(symbol, "1d", 30)   # 30 days
        
        if not hourly_data or not daily_data:
            return BotRecommendation(2.0, 5.0, 100.0, "CONSERVATIVE", "HIGH", 0.1)
        
        # Analyze volatility
        hourly_volatility = self.analyzer.calculate_volatility_metrics(hourly_data)
        daily_volatility = self.analyzer.calculate_volatility_metrics(daily_data)
        
        # Analyze patterns
        patterns = self.analyzer.analyze_price_patterns(hourly_data)
        
        # Calculate optimal parameters
        optimal_profit = self._calculate_optimal_profit_target(hourly_volatility, patterns)
        max_loss = self._calculate_max_loss_threshold(daily_volatility)
        trade_size = self._calculate_trade_size(daily_volatility)
        cycle_freq = self._determine_cycle_frequency(hourly_volatility)
        risk_level = self._assess_risk_level(daily_volatility, patterns)
        confidence = self._calculate_confidence_score(hourly_data, daily_data, patterns)
        
        return BotRecommendation(
            optimal_profit_target=optimal_profit,
            max_loss_threshold=max_loss,
            recommended_trade_size=trade_size,
            cycle_frequency=cycle_freq,
            risk_level=risk_level,
            confidence_score=confidence
        )
    
    def _calculate_optimal_profit_target(self, volatility: VolatilityMetrics, patterns: Dict) -> float:
        """📊 Calculate optimal profit target based on volatility"""
        base_target = volatility.avg_daily_range * 0.3  # 30% of average daily range
        
        # Adjust based on gain/loss ratio
        if patterns.get('gain_loss_ratio', 1) > 1.5:
            base_target *= 1.2  # Increase target in bullish market
        elif patterns.get('gain_loss_ratio', 1) < 0.7:
            base_target *= 0.8  # Decrease target in bearish market
        
        # Ensure reasonable bounds
        return max(0.5, min(5.0, base_target))
    
    def _calculate_max_loss_threshold(self, volatility: VolatilityMetrics) -> float:
        """🛡️ Calculate maximum loss threshold"""
        base_threshold = volatility.avg_daily_range * 0.6  # 60% of average daily range
        return max(2.0, min(10.0, base_threshold))
    
    def _calculate_trade_size(self, volatility: VolatilityMetrics) -> float:
        """💰 Calculate recommended trade size"""
        if volatility.volatility_percent > 15:
            return 50.0  # Lower size for high volatility
        elif volatility.volatility_percent > 8:
            return 100.0  # Medium size for medium volatility
        else:
            return 200.0  # Higher size for low volatility
    
    def _determine_cycle_frequency(self, volatility: VolatilityMetrics) -> str:
        """⏱️ Determine optimal cycle frequency"""
        if volatility.avg_daily_range > 8:
            return "AGGRESSIVE"  # High volatility = more frequent trades
        elif volatility.avg_daily_range > 4:
            return "MODERATE"
        else:
            return "CONSERVATIVE"
    
    def _assess_risk_level(self, volatility: VolatilityMetrics, patterns: Dict) -> str:
        """⚠️ Assess overall risk level"""
        risk_score = 0
        
        if volatility.volatility_percent > 20:
            risk_score += 3
        elif volatility.volatility_percent > 10:
            risk_score += 2
        else:
            risk_score += 1
        
        if patterns.get('max_loss_sequence', 0) > 5:
            risk_score += 2
        
        if patterns.get('gain_loss_ratio', 1) < 0.5:
            risk_score += 2
        
        if risk_score >= 6:
            return "HIGH"
        elif risk_score >= 4:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _calculate_confidence_score(self, hourly_data: List[PriceData], 
                                  daily_data: List[PriceData], patterns: Dict) -> float:
        """🎯 Calculate confidence score for recommendations"""
        score = 0.5  # Base score
        
        # Data quality bonus
        if len(hourly_data) >= 168 and len(daily_data) >= 30:
            score += 0.2
        
        # Pattern consistency bonus
        if patterns.get('gain_loss_ratio', 0) > 0.8 and patterns.get('gain_loss_ratio', 0) < 1.5:
            score += 0.2
        
        # Volume consistency (if available)
        if hourly_data:
            avg_volume = statistics.mean([p.volume for p in hourly_data])
            if avg_volume > 1000:  # Good liquidity
                score += 0.1
        
        return min(1.0, score)

def main():
    """🚀 Main analysis function"""
    print("🔬 XNY_USDT Analysis & Bot Optimization")
    print("=" * 60)
    
    # Initialize components (Dependency Injection)
    market_data = GateIOMarketData()
    analyzer = PriceAnalyzer(market_data)
    optimizer = BotOptimizer(analyzer)
    
    symbol = "XNY_USDT"
    
    print(f"📊 Analyzing {symbol}...")
    
    # Get current price
    current_price = market_data.get_current_price(symbol)
    print(f"💱 Current Price: ${current_price:.8f}")
    
    # Get recommendations
    recommendations = optimizer.generate_recommendations(symbol)
    
    print("\n🤖 BOT OPTIMIZATION RECOMMENDATIONS:")
    print("=" * 50)
    print(f"🎯 Optimal Profit Target: {recommendations.optimal_profit_target:.2f}%")
    print(f"🛡️ Max Loss Threshold: {recommendations.max_loss_threshold:.2f}%")
    print(f"💰 Recommended Trade Size: ${recommendations.recommended_trade_size:.0f} USDT")
    print(f"⏱️ Cycle Frequency: {recommendations.cycle_frequency}")
    print(f"⚠️ Risk Level: {recommendations.risk_level}")
    print(f"🎯 Confidence Score: {recommendations.confidence_score:.1%}")
    
    # Detailed analysis
    print("\n📈 DETAILED MARKET ANALYSIS:")
    print("=" * 40)
    
    # Get detailed data
    hourly_data = market_data.get_candlestick_data(symbol, "1h", 168)
    daily_data = market_data.get_candlestick_data(symbol, "1d", 30)
    
    if hourly_data:
        hourly_volatility = analyzer.calculate_volatility_metrics(hourly_data)
        patterns = analyzer.analyze_price_patterns(hourly_data)
        
        print(f"📊 Average Daily Range: {hourly_volatility.avg_daily_range:.2f}%")
        print(f"📈 Max Daily Range: {hourly_volatility.max_daily_range:.2f}%")
        print(f"📉 Min Daily Range: {hourly_volatility.min_daily_range:.2f}%")
        print(f"🎯 Trend Direction: {hourly_volatility.trend_direction}")
        print(f"🔻 Support Level: ${hourly_volatility.support_level:.8f}")
        print(f"🔺 Resistance Level: ${hourly_volatility.resistance_level:.8f}")
        print(f"📊 Win/Loss Ratio: {patterns.get('gain_loss_ratio', 0):.2f}")
        print(f"📈 Avg Gain: {patterns.get('avg_gain_percent', 0):.2f}%")
        print(f"📉 Avg Loss: {patterns.get('avg_loss_percent', 0):.2f}%")
    
    print("\n💡 CONFIGURATION SUGGESTIONS:")
    print("=" * 35)
    print("Per il tuo bot scalping:")
    print(f"   Target profitto: {recommendations.optimal_profit_target:.1f}%")
    print(f"   Stop loss: {recommendations.max_loss_threshold:.1f}%")
    print(f"   Importo per trade: ${recommendations.recommended_trade_size:.0f}")
    print(f"   Strategia: {recommendations.cycle_frequency.lower()}")

if __name__ == "__main__":
    main()