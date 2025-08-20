#!/usr/bin/env python3
"""
🔍 MONITORING INTEGRATION EXAMPLE
=================================
Esempio pratico di integrazione del sistema monitoring avanzato
nel trading bot per dimostrare le funzionalità implementate.
"""

import time
from advanced_monitoring_system import (
    create_production_monitoring_system,
    EventType,
    AlertSeverity
)

def demonstrate_monitoring_capabilities():
    """Dimostra le funzionalità del sistema monitoring"""
    
    print("🔍 ADVANCED MONITORING SYSTEM - DEMONSTRATION")
    print("=" * 50)
    
    # Crea sistema monitoring
    monitoring = create_production_monitoring_system()
    
    print("✅ Starting monitoring system...")
    monitoring.start_monitoring(interval_seconds=30)
    
    # Simula eventi di trading
    print("\n📊 Simulating trading events...")
    
    # 1. Trade success
    monitoring.record_trade_event(
        success=True,
        pair="BTC_USDT",
        profit=0.025,
        execution_time=1.2
    )
    
    # 2. API success
    monitoring.record_api_event(
        endpoint="/spot/accounts",
        success=True,
        response_time=0.5
    )
    
    # 3. API failure
    monitoring.record_api_event(
        endpoint="/spot/orders",
        success=False,
        response_time=5.0,
        error_message="Connection timeout"
    )
    
    # 4. Rate limiting
    monitoring.record_api_event(
        endpoint="/spot/ticker",
        success=False,
        response_time=0.1,
        error_message="Rate limit exceeded",
        is_rate_limited=True
    )
    
    # 5. Multiple failures to trigger pattern detection
    print("\n⚠️ Simulating failure pattern...")
    for i in range(6):
        monitoring.record_trade_event(
            success=False,
            pair="ETH_USDT",
            error_message=f"Order failed - attempt {i+1}"
        )
        time.sleep(0.1)
    
    # 6. Circuit breaker
    monitoring.record_circuit_breaker_event(
        source="test_bot",
        failure_count=5,
        cooldown_seconds=300
    )
    
    # Wait for monitoring to process
    time.sleep(2)
    
    # Get performance summary
    print("\n📈 PERFORMANCE SUMMARY:")
    print("=" * 30)
    summary = monitoring.get_performance_summary()
    
    metrics = summary['performance_metrics']
    print(f"Total Trades: {metrics['total_trades']}")
    print(f"Success Rate: {metrics['success_rate']:.2%}")
    print(f"API Failures: {metrics['api_failures']}")
    print(f"Rate Limit Hits: {metrics['rate_limit_hits']}")
    print(f"Circuit Breaker Triggers: {metrics['circuit_breaker_triggers']}")
    print(f"Total Profit: {metrics['total_profit']:.4f} USDT")
    
    # Log analysis
    log_analysis = summary['recent_log_analysis']
    print(f"\n📋 LOG ANALYSIS:")
    print(f"Total Events: {log_analysis['total_events']}")
    print(f"Error Count: {log_analysis['error_count']}")
    print(f"Success Count: {log_analysis['success_count']}")
    
    if log_analysis['anomalies']:
        print(f"\n🚨 ANOMALIES DETECTED:")
        for anomaly in log_analysis['anomalies']:
            print(f"  - {anomaly['type']}: {anomaly['description']}")
    else:
        print("\n✅ No anomalies detected")
    
    # Demonstrate event subscription
    print("\n📡 Setting up event subscriber...")
    
    def on_critical_event(event):
        print(f"🚨 CRITICAL EVENT: {event.message}")
    
    monitoring.subscribe_to_event(EventType.CIRCUIT_BREAKER, on_critical_event)
    monitoring.subscribe_to_event(EventType.ANOMALY_DETECTED, on_critical_event)
    
    # Trigger critical event
    monitoring.record_circuit_breaker_event(
        source="demo_critical",
        failure_count=10,
        cooldown_seconds=600
    )
    
    time.sleep(1)
    
    print("\n🛑 Stopping monitoring system...")
    monitoring.stop_monitoring()
    
    print("\n✅ Monitoring demonstration completed!")
    print("\n💡 Integration Benefits:")
    print("  - Real-time failure detection")
    print("  - Pattern recognition for anomalies") 
    print("  - Automated alerting system")
    print("  - Performance analytics")
    print("  - Circuit breaker monitoring")
    print("  - Rate limiting detection")


if __name__ == "__main__":
    demonstrate_monitoring_capabilities()