#!/usr/bin/env python3
"""
🔍 ADVANCED MONITORING SYSTEM - DEFENSIVE SECURITY
==================================================
Sistema completo di monitoring, log analysis e alerting per trading bot.
Previene failure cascading e fornisce early warning su pattern anomali.

Principi implementati:
- SOLID: Single Responsibility, Open/Closed, Interface Segregation
- Observer Pattern: Event-driven monitoring
- Strategy Pattern: Diverse strategie di analisi
- Security by Design: Anomaly detection, failure prediction
"""

import os
import re
import json
import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import glob


class AlertSeverity(Enum):
    """Livelli di severity per alert"""
    INFO = "info"
    WARNING = "warning"  
    ERROR = "error"
    CRITICAL = "critical"


class EventType(Enum):
    """Tipi di eventi monitorati"""
    TRADE_SUCCESS = "trade_success"
    TRADE_FAILURE = "trade_failure"
    API_ERROR = "api_error"
    CIRCUIT_BREAKER = "circuit_breaker"
    RATE_LIMIT = "rate_limit"
    BALANCE_LOW = "balance_low"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    ANOMALY_DETECTED = "anomaly_detected"


@dataclass(frozen=True)
class MonitoringEvent:
    """Evento monitorato immutabile"""
    timestamp: float
    event_type: EventType
    severity: AlertSeverity
    source: str  # Nome bot/modulo
    message: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp,
            'event_type': self.event_type.value,
            'severity': self.severity.value,
            'source': self.source,
            'message': self.message,
            'metadata': self.metadata
        }


@dataclass
class PerformanceMetrics:
    """Metriche performance per analisi"""
    success_rate: float = 0.0
    avg_execution_time: float = 0.0
    total_trades: int = 0
    api_failures: int = 0
    circuit_breaker_triggers: int = 0
    rate_limit_hits: int = 0
    total_profit: float = 0.0
    
    def reset(self):
        """Reset metriche per nuovo periodo"""
        self.success_rate = 0.0
        self.avg_execution_time = 0.0
        self.total_trades = 0
        self.api_failures = 0
        self.circuit_breaker_triggers = 0
        self.rate_limit_hits = 0
        self.total_profit = 0.0


class IAlertHandler:
    """Interface per gestori di alert"""
    def handle_alert(self, event: MonitoringEvent) -> bool:
        raise NotImplementedError


class ConsoleAlertHandler(IAlertHandler):
    """Handler alert su console"""
    
    def __init__(self):
        self.colors = {
            AlertSeverity.INFO: '\033[94m',      # Blue
            AlertSeverity.WARNING: '\033[93m',   # Yellow
            AlertSeverity.ERROR: '\033[91m',     # Red
            AlertSeverity.CRITICAL: '\033[95m'   # Magenta
        }
        self.reset_color = '\033[0m'
    
    def handle_alert(self, event: MonitoringEvent) -> bool:
        color = self.colors.get(event.severity, '')
        timestamp = datetime.fromtimestamp(event.timestamp).strftime('%H:%M:%S')
        
        print(f"{color}🚨 [{timestamp}] {event.severity.value.upper()} - {event.source}: {event.message}{self.reset_color}")
        
        if event.metadata:
            for key, value in event.metadata.items():
                print(f"   {key}: {value}")
        
        return True


class FileAlertHandler(IAlertHandler):
    """Handler alert su file"""
    
    def __init__(self, alert_file: str = "alerts.log"):
        self.alert_file = alert_file
        
    def handle_alert(self, event: MonitoringEvent) -> bool:
        try:
            with open(self.alert_file, 'a', encoding='utf-8') as f:
                f.write(f"{json.dumps(event.to_dict())}\n")
            return True
        except Exception as e:
            logging.error(f"Failed to write alert to file: {e}")
            return False


class LogAnalyzer:
    """🔍 Analizzatore automatico log con pattern recognition"""
    
    def __init__(self, log_directory: str = "logs"):
        self.log_directory = log_directory
        self.pattern_cache = {}
        
        # Pattern regex per riconoscimento eventi
        self.patterns = {
            'trade_success': re.compile(r'✅.*SELL.*profit=([0-9.-]+)'),
            'trade_failure': re.compile(r'❌.*(?:Errore|Error|FAILED).*'),
            'api_error': re.compile(r'🚫.*API.*(?:failed|error|timeout)', re.IGNORECASE),
            'rate_limit': re.compile(r'🚨.*Rate limit.*', re.IGNORECASE),
            'circuit_breaker': re.compile(r'🔴.*Circuit breaker.*', re.IGNORECASE),
            'balance_check': re.compile(r'Balance check failed'),
            'retry_attempt': re.compile(r'⚠️.*attempt (\d+).*'),
        }
    
    def analyze_recent_logs(self, hours_back: int = 24) -> Dict[str, Any]:
        """Analizza log recenti per pattern anomali"""
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        analysis_results = {
            'total_events': 0,
            'error_count': 0,
            'success_count': 0,
            'api_failures': 0,
            'rate_limits': 0,
            'circuit_breakers': 0,
            'anomalies': [],
            'performance_trends': {}
        }
        
        log_files = self._get_recent_log_files(cutoff_time)
        
        for log_file in log_files:
            events = self._parse_log_file(log_file)
            self._update_analysis_results(analysis_results, events)
        
        # Detect anomalies
        analysis_results['anomalies'] = self._detect_anomalies(analysis_results)
        
        return analysis_results
    
    def _get_recent_log_files(self, cutoff_time: datetime) -> List[str]:
        """Trova file log recenti"""
        log_files = []
        
        if not os.path.exists(self.log_directory):
            return log_files
        
        pattern = os.path.join(self.log_directory, "*.log")
        for file_path in glob.glob(pattern):
            try:
                # Check file modification time
                mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if mod_time >= cutoff_time:
                    log_files.append(file_path)
            except OSError:
                continue
        
        return sorted(log_files)
    
    def _parse_log_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse singolo log file per eventi"""
        events = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Extract timestamp se presente
                    timestamp = self._extract_timestamp(line)
                    
                    # Match patterns
                    for pattern_name, regex in self.patterns.items():
                        match = regex.search(line)
                        if match:
                            event = {
                                'file': file_path,
                                'line': line_num,
                                'timestamp': timestamp,
                                'type': pattern_name,
                                'message': line,
                                'match_groups': match.groups() if match.groups() else []
                            }
                            events.append(event)
                            break
        
        except Exception as e:
            logging.error(f"Error parsing log file {file_path}: {e}")
        
        return events
    
    def _extract_timestamp(self, line: str) -> Optional[float]:
        """Estrae timestamp dalla linea log"""
        # Try common timestamp formats
        timestamp_patterns = [
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',
            r'(\d{2}:\d{2}:\d{2})',
            r'\[([^\]]+)\]'
        ]
        
        for pattern in timestamp_patterns:
            match = re.search(pattern, line)
            if match:
                try:
                    timestamp_str = match.group(1)
                    # Try to parse timestamp
                    if ':' in timestamp_str and '-' not in timestamp_str:
                        # Time only, assume today
                        today = datetime.now().strftime('%Y-%m-%d')
                        timestamp_str = f"{today} {timestamp_str}"
                    
                    dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    return dt.timestamp()
                except ValueError:
                    continue
        
        return None
    
    def _update_analysis_results(self, results: Dict[str, Any], events: List[Dict[str, Any]]):
        """Aggiorna risultati analisi con nuovi eventi"""
        for event in events:
            results['total_events'] += 1
            event_type = event['type']
            
            if event_type == 'trade_success':
                results['success_count'] += 1
                # Extract profit if available
                if event['match_groups']:
                    try:
                        profit = float(event['match_groups'][0])
                        results['performance_trends'].setdefault('profits', []).append(profit)
                    except (ValueError, IndexError):
                        pass
            
            elif event_type in ['trade_failure', 'api_error']:
                results['error_count'] += 1
                if event_type == 'api_error':
                    results['api_failures'] += 1
            
            elif event_type == 'rate_limit':
                results['rate_limits'] += 1
                
            elif event_type == 'circuit_breaker':
                results['circuit_breakers'] += 1
    
    def _detect_anomalies(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Rileva anomalie nei dati analizzati"""
        anomalies = []
        
        # High error rate
        if results['total_events'] > 0:
            error_rate = results['error_count'] / results['total_events']
            if error_rate > 0.2:  # 20% error rate
                anomalies.append({
                    'type': 'high_error_rate',
                    'severity': 'warning' if error_rate < 0.5 else 'critical',
                    'value': error_rate,
                    'description': f"High error rate detected: {error_rate:.2%}"
                })
        
        # Frequent rate limiting
        if results['rate_limits'] > 5:
            anomalies.append({
                'type': 'frequent_rate_limiting',
                'severity': 'warning',
                'value': results['rate_limits'],
                'description': f"Frequent rate limiting: {results['rate_limits']} hits"
            })
        
        # Multiple circuit breaker triggers
        if results['circuit_breakers'] > 3:
            anomalies.append({
                'type': 'multiple_circuit_breakers',
                'severity': 'critical',
                'value': results['circuit_breakers'],
                'description': f"Multiple circuit breaker triggers: {results['circuit_breakers']}"
            })
        
        # Performance degradation
        profits = results['performance_trends'].get('profits', [])
        if len(profits) > 10:
            recent_profits = profits[-10:]
            older_profits = profits[-20:-10] if len(profits) >= 20 else profits[:-10]
            
            if older_profits and recent_profits:
                recent_avg = sum(recent_profits) / len(recent_profits)
                older_avg = sum(older_profits) / len(older_profits)
                
                if recent_avg < older_avg * 0.7:  # 30% decline
                    anomalies.append({
                        'type': 'performance_degradation',
                        'severity': 'warning',
                        'value': {'recent': recent_avg, 'older': older_avg},
                        'description': f"Performance decline detected: {recent_avg:.4f} vs {older_avg:.4f}"
                    })
        
        return anomalies


class FailurePatternDetector:
    """🎯 Rilevatore pattern di fallimento per early warning"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.failure_history = deque(maxlen=window_size)
        self.pattern_thresholds = {
            'consecutive_failures': 5,
            'failure_rate_threshold': 0.3,
            'api_timeout_threshold': 10,
            'balance_check_failures': 5
        }
    
    def record_event(self, event_type: EventType, success: bool = True, metadata: Dict[str, Any] = None):
        """Registra evento per analisi pattern"""
        event_record = {
            'timestamp': time.time(),
            'type': event_type,
            'success': success,
            'metadata': metadata or {}
        }
        
        self.failure_history.append(event_record)
        
        # Check per pattern critici
        critical_patterns = self._analyze_recent_patterns()
        return critical_patterns
    
    def _analyze_recent_patterns(self) -> List[Dict[str, Any]]:
        """Analizza pattern recenti per warning precoci"""
        if len(self.failure_history) < 10:
            return []
        
        patterns = []
        recent_events = list(self.failure_history)[-20:]  # Last 20 events
        
        # Consecutive failures
        consecutive_failures = self._count_consecutive_failures(recent_events)
        if consecutive_failures >= self.pattern_thresholds['consecutive_failures']:
            patterns.append({
                'type': 'consecutive_failures',
                'severity': 'critical',
                'count': consecutive_failures,
                'description': f"{consecutive_failures} consecutive failures detected"
            })
        
        # High failure rate
        failures = sum(1 for e in recent_events if not e['success'])
        failure_rate = failures / len(recent_events)
        if failure_rate >= self.pattern_thresholds['failure_rate_threshold']:
            patterns.append({
                'type': 'high_failure_rate',
                'severity': 'warning' if failure_rate < 0.5 else 'critical',
                'rate': failure_rate,
                'description': f"High failure rate: {failure_rate:.2%}"
            })
        
        # API timeout pattern
        api_timeouts = sum(1 for e in recent_events 
                          if e['type'] == EventType.API_ERROR and 
                          'timeout' in str(e.get('metadata', {})).lower())
        if api_timeouts >= self.pattern_thresholds['api_timeout_threshold']:
            patterns.append({
                'type': 'api_timeout_cluster',
                'severity': 'warning',
                'count': api_timeouts,
                'description': f"API timeout cluster detected: {api_timeouts} timeouts"
            })
        
        return patterns
    
    def _count_consecutive_failures(self, events: List[Dict[str, Any]]) -> int:
        """Conta fallimenti consecutivi"""
        consecutive = 0
        for event in reversed(events):
            if not event['success']:
                consecutive += 1
            else:
                break
        return consecutive


class MonitoringSystem:
    """🔍 Sistema principale di monitoring con alerting intelligente"""
    
    def __init__(self, alert_handlers: List[IAlertHandler] = None):
        self.alert_handlers = alert_handlers or [ConsoleAlertHandler()]
        self.log_analyzer = LogAnalyzer()
        self.failure_detector = FailurePatternDetector()
        self.performance_metrics = PerformanceMetrics()
        
        # Threading per monitoring asincrono
        self.monitoring_active = False
        self.monitoring_thread = None
        
        # Event subscribers (Observer pattern)
        self.event_subscribers: Dict[EventType, List[Callable]] = defaultdict(list)
        
        # Throttling per evitare spam di alert
        self.alert_throttle = defaultdict(lambda: 0)  # Last alert timestamp per type
        self.throttle_interval = 300  # 5 minuti tra alert dello stesso tipo
    
    def start_monitoring(self, interval_seconds: int = 60):
        """Avvia monitoring continuo"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval_seconds,),
            daemon=True
        )
        self.monitoring_thread.start()
        
        self._emit_event(MonitoringEvent(
            timestamp=time.time(),
            event_type=EventType.TRADE_SUCCESS,
            severity=AlertSeverity.INFO,
            source="monitoring_system",
            message="Monitoring system started",
            metadata={"interval": interval_seconds}
        ))
    
    def stop_monitoring(self):
        """Ferma monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
    
    def record_trade_event(self, success: bool, pair: str, profit: float = 0.0, 
                          execution_time: float = 0.0, error_message: str = ""):
        """Registra evento trading per monitoring"""
        event_type = EventType.TRADE_SUCCESS if success else EventType.TRADE_FAILURE
        severity = AlertSeverity.INFO if success else AlertSeverity.WARNING
        
        metadata = {
            'pair': pair,
            'profit': profit,
            'execution_time': execution_time
        }
        
        if not success and error_message:
            metadata['error'] = error_message
            
        # Update performance metrics
        self.performance_metrics.total_trades += 1
        if success:
            self.performance_metrics.total_profit += profit
        
        # Check failure patterns
        failure_patterns = self.failure_detector.record_event(
            event_type, success, metadata
        )
        
        # Generate alerts for critical patterns
        for pattern in failure_patterns:
            self._emit_alert_for_pattern(pattern)
        
        # Emit main event
        message = f"Trade {'SUCCESS' if success else 'FAILED'} for {pair}"
        if success:
            message += f" - Profit: {profit:.4f} USDT"
            
        event = MonitoringEvent(
            timestamp=time.time(),
            event_type=event_type,
            severity=severity,
            source=f"trading_bot_{pair}",
            message=message,
            metadata=metadata
        )
        
        self._emit_event(event)
    
    def record_api_event(self, endpoint: str, success: bool, response_time: float = 0.0,
                        error_message: str = "", is_rate_limited: bool = False):
        """Registra evento API"""
        if is_rate_limited:
            event_type = EventType.RATE_LIMIT
            severity = AlertSeverity.WARNING
            message = f"Rate limited on {endpoint}"
            self.performance_metrics.rate_limit_hits += 1
        elif success:
            event_type = EventType.TRADE_SUCCESS  # API success
            severity = AlertSeverity.INFO
            message = f"API call to {endpoint} succeeded"
        else:
            event_type = EventType.API_ERROR
            severity = AlertSeverity.ERROR
            message = f"API call to {endpoint} failed: {error_message}"
            self.performance_metrics.api_failures += 1
        
        metadata = {
            'endpoint': endpoint,
            'response_time': response_time,
            'is_rate_limited': is_rate_limited
        }
        
        if error_message:
            metadata['error'] = error_message
        
        event = MonitoringEvent(
            timestamp=time.time(),
            event_type=event_type,
            severity=severity,
            source="api_client",
            message=message,
            metadata=metadata
        )
        
        self._emit_event(event)
    
    def record_circuit_breaker_event(self, source: str, failure_count: int, 
                                   cooldown_seconds: int):
        """Registra evento circuit breaker"""
        self.performance_metrics.circuit_breaker_triggers += 1
        
        event = MonitoringEvent(
            timestamp=time.time(),
            event_type=EventType.CIRCUIT_BREAKER,
            severity=AlertSeverity.CRITICAL,
            source=source,
            message=f"Circuit breaker activated - {failure_count} failures",
            metadata={
                'failure_count': failure_count,
                'cooldown_seconds': cooldown_seconds
            }
        )
        
        self._emit_event(event)
    
    def subscribe_to_event(self, event_type: EventType, callback: Callable[[MonitoringEvent], None]):
        """Subscribe to specific event types (Observer pattern)"""
        self.event_subscribers[event_type].append(callback)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Ottieni riassunto performance"""
        success_rate = 0.0
        if self.performance_metrics.total_trades > 0:
            successful_trades = self.performance_metrics.total_trades - self.performance_metrics.api_failures
            success_rate = successful_trades / self.performance_metrics.total_trades
            
        self.performance_metrics.success_rate = success_rate
        
        return {
            'performance_metrics': asdict(self.performance_metrics),
            'recent_log_analysis': self.log_analyzer.analyze_recent_logs(),
            'monitoring_active': self.monitoring_active
        }
    
    def _monitoring_loop(self, interval_seconds: int):
        """Loop principale monitoring"""
        while self.monitoring_active:
            try:
                # Analyze recent logs
                analysis = self.log_analyzer.analyze_recent_logs(hours_back=1)
                
                # Check for anomalies
                if analysis.get('anomalies'):
                    for anomaly in analysis['anomalies']:
                        severity = AlertSeverity.WARNING
                        if anomaly.get('severity') == 'critical':
                            severity = AlertSeverity.CRITICAL
                        
                        event = MonitoringEvent(
                            timestamp=time.time(),
                            event_type=EventType.ANOMALY_DETECTED,
                            severity=severity,
                            source="log_analyzer",
                            message=f"Anomaly detected: {anomaly['description']}",
                            metadata=anomaly
                        )
                        
                        self._emit_event(event)
                
                time.sleep(interval_seconds)
                
            except Exception as e:
                logging.error(f"Monitoring loop error: {e}")
                time.sleep(interval_seconds)
    
    def _emit_event(self, event: MonitoringEvent):
        """Emette evento a tutti gli handler e subscriber"""
        # Check throttling
        throttle_key = f"{event.event_type}_{event.source}"
        now = time.time()
        
        if now - self.alert_throttle[throttle_key] < self.throttle_interval:
            if event.severity not in [AlertSeverity.CRITICAL]:  # Always emit critical
                return
        
        self.alert_throttle[throttle_key] = now
        
        # Send to alert handlers
        for handler in self.alert_handlers:
            try:
                handler.handle_alert(event)
            except Exception as e:
                logging.error(f"Alert handler error: {e}")
        
        # Notify subscribers
        for callback in self.event_subscribers.get(event.event_type, []):
            try:
                callback(event)
            except Exception as e:
                logging.error(f"Event subscriber error: {e}")
    
    def _emit_alert_for_pattern(self, pattern: Dict[str, Any]):
        """Emette alert per pattern critici rilevati"""
        severity_map = {
            'warning': AlertSeverity.WARNING,
            'critical': AlertSeverity.CRITICAL,
            'error': AlertSeverity.ERROR
        }
        
        severity = severity_map.get(pattern.get('severity', 'warning'), AlertSeverity.WARNING)
        
        event = MonitoringEvent(
            timestamp=time.time(),
            event_type=EventType.ANOMALY_DETECTED,
            severity=severity,
            source="failure_detector",
            message=f"Critical pattern detected: {pattern['description']}",
            metadata=pattern
        )
        
        self._emit_event(event)


# Factory functions per configurazioni predefinite
def create_production_monitoring_system() -> MonitoringSystem:
    """Crea sistema monitoring per produzione"""
    handlers = [
        ConsoleAlertHandler(),
        FileAlertHandler("trading_alerts.log")
    ]
    
    return MonitoringSystem(handlers)


def create_development_monitoring_system() -> MonitoringSystem:
    """Crea sistema monitoring per sviluppo"""
    return MonitoringSystem([ConsoleAlertHandler()])


# Global instance
_global_monitoring = None


def get_global_monitoring() -> MonitoringSystem:
    """Get singleton monitoring instance"""
    global _global_monitoring
    if _global_monitoring is None:
        _global_monitoring = create_production_monitoring_system()
    return _global_monitoring


if __name__ == "__main__":
    # Test example
    monitoring = create_development_monitoring_system()
    monitoring.start_monitoring(interval_seconds=10)
    
    # Simulate some events
    monitoring.record_trade_event(True, "BTC_USDT", profit=0.05, execution_time=1.2)
    monitoring.record_trade_event(False, "BTC_USDT", error_message="Insufficient balance")
    monitoring.record_api_event("/spot/accounts", False, error_message="Timeout", response_time=5.0)
    
    # Get summary
    summary = monitoring.get_performance_summary()
    print(f"Performance summary: {json.dumps(summary, indent=2)}")
    
    time.sleep(2)
    monitoring.stop_monitoring()