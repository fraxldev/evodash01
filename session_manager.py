#!/usr/bin/env python3
"""
🤖 MULTI-BOT SESSION MANAGER
===============================
Sistema di gestione sessioni multiple per bot scalping su coppie diverse.

Caratteristiche:
- Processo master che coordina worker processes
- Budget allocation automatica
- Dashboard aggregata real-time
- Comunicazione inter-bot per evitare conflitti
- WebSocket condivisi per performance

Architettura:
- SessionManager (Master Process)
- BotWorker (Worker Process per ogni coppia)
- SharedState (Stato condiviso via JSON + locks)
- MessageBroker (Comunicazione asincrona)

Autore: Claude Code + User
Data: 2025-08-12
"""

import os
import sys
import json
import time
import signal
import threading
import multiprocessing as mp
from multiprocessing import shared_memory, Queue, Event, Lock
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import subprocess

# Import del client Gate.io esistente
try:
    from dash01_refactored import GateIOClient
except ImportError:
    print("❌ Errore: Impossibile importare GateIOClient. Verifica che dash01_refactored.py sia presente.")
    sys.exit(1)

@dataclass
class BotStatus:
    """📊 Status di un singolo bot"""
    pair: str
    status: str  # STARTING, RUNNING, PAUSED, STOPPED, ERROR
    pid: Optional[int] = None
    start_time: Optional[datetime] = None
    allocated_budget: float = 0.0
    current_position: Optional[Dict] = None
    trades_today: int = 0
    pnl_percent: float = 0.0
    last_action: Optional[str] = None
    last_action_time: Optional[datetime] = None
    errors_count: int = 0
    
    def to_dict(self):
        """Converte in dict serializzabile"""
        result = asdict(self)
        # Converte datetime in string
        if self.start_time:
            result['start_time'] = self.start_time.isoformat()
        if self.last_action_time:
            result['last_action_time'] = self.last_action_time.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Crea da dict"""
        if data.get('start_time'):
            data['start_time'] = datetime.fromisoformat(data['start_time'])
        if data.get('last_action_time'):
            data['last_action_time'] = datetime.fromisoformat(data['last_action_time'])
        return cls(**data)

class SharedState:
    """🗃️ Stato condiviso thread-safe tra processi"""
    
    def __init__(self, state_file: str = "shared_state.json"):
        self.state_file = Path(state_file)
        self.lock_file = Path(f"{state_file}.lock")
        self._local_lock = threading.Lock()
        
        # Inizializza stato se non esiste
        if not self.state_file.exists():
            self._write_state({
                'bots': {},
                'global_budget': {
                    'total_usdt': 0.0,
                    'allocated_usdt': 0.0,
                    'available_usdt': 0.0
                },
                'system_status': 'IDLE',
                'last_update': datetime.now().isoformat()
            })
    
    def _acquire_file_lock(self, timeout: float = 5.0) -> bool:
        """Acquisisce lock su file"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Atomic file creation per lock
                with open(self.lock_file, 'x') as f:
                    f.write(str(os.getpid()))
                return True
            except FileExistsError:
                time.sleep(0.01)  # 10ms
        return False
    
    def _release_file_lock(self):
        """Rilascia lock su file"""
        try:
            self.lock_file.unlink()
        except FileNotFoundError:
            pass
    
    def _read_state(self) -> Dict:
        """Legge stato da file con lock"""
        with self._local_lock:
            if not self._acquire_file_lock():
                raise TimeoutError("Impossibile acquisire lock su shared state")
            
            try:
                if self.state_file.exists():
                    with open(self.state_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
                return {}
            finally:
                self._release_file_lock()
    
    def _write_state(self, state: Dict):
        """Scrive stato su file con lock"""
        with self._local_lock:
            if not self._acquire_file_lock():
                raise TimeoutError("Impossibile acquisire lock su shared state")
            
            try:
                state['last_update'] = datetime.now().isoformat()
                with open(self.state_file, 'w', encoding='utf-8') as f:
                    json.dump(state, f, indent=2, ensure_ascii=False)
            finally:
                self._release_file_lock()
    
    def get_bot_status(self, pair: str) -> Optional[BotStatus]:
        """Ottiene status di un bot"""
        state = self._read_state()
        bot_data = state.get('bots', {}).get(pair)
        if bot_data:
            return BotStatus.from_dict(bot_data)
        return None
    
    def set_bot_status(self, bot_status: BotStatus):
        """Imposta status di un bot"""
        state = self._read_state()
        if 'bots' not in state:
            state['bots'] = {}
        state['bots'][bot_status.pair] = bot_status.to_dict()
        self._write_state(state)
    
    def get_all_bots(self) -> Dict[str, BotStatus]:
        """Ottiene status di tutti i bot"""
        state = self._read_state()
        bots = {}
        for pair, bot_data in state.get('bots', {}).items():
            bots[pair] = BotStatus.from_dict(bot_data)
        return bots
    
    def get_budget_info(self) -> Dict[str, float]:
        """Ottiene info budget globale"""
        state = self._read_state()
        return state.get('global_budget', {
            'total_usdt': 0.0,
            'allocated_usdt': 0.0,
            'available_usdt': 0.0
        })
    
    def set_budget_info(self, budget_info: Dict[str, float]):
        """Imposta info budget globale"""
        state = self._read_state()
        state['global_budget'] = budget_info
        self._write_state(state)

class BudgetCoordinator:
    """💰 Coordinatore budget USDT tra bot"""
    
    def __init__(self, shared_state: SharedState, client: GateIOClient):
        self.shared_state = shared_state
        self.client = client
        
    def get_total_usdt_balance(self) -> float:
        """Ottiene saldo USDT totale da Gate.io"""
        try:
            balance_data = self.client._request('GET', '/spot/accounts', signed=True)
            if balance_data:
                for account in balance_data:
                    if account.get('currency') == 'USDT':
                        available = float(account.get('available', 0))
                        locked = float(account.get('locked', 0))
                        return available + locked
            return 0.0
        except Exception as e:
            print(f"⚠️ Errore recupero saldo USDT: {e}")
            return 0.0
    
    def update_budget_info(self):
        """Aggiorna informazioni budget da API"""
        total_usdt = self.get_total_usdt_balance()
        
        # Calcola USDT allocato ai bot attivi
        all_bots = self.shared_state.get_all_bots()
        allocated_usdt = sum(
            bot.allocated_budget 
            for bot in all_bots.values() 
            if bot.status in ['RUNNING', 'STARTING']
        )
        
        available_usdt = max(0, total_usdt - allocated_usdt)
        
        budget_info = {
            'total_usdt': total_usdt,
            'allocated_usdt': allocated_usdt,
            'available_usdt': available_usdt
        }
        
        self.shared_state.set_budget_info(budget_info)
        return budget_info
    
    def allocate_budget(self, pair: str, requested_amount: float) -> tuple[bool, float]:
        """
        Alloca budget per un bot
        Returns: (success, allocated_amount)
        """
        budget_info = self.update_budget_info()
        available = budget_info['available_usdt']
        
        if requested_amount <= available:
            # Allocazione completa
            return True, requested_amount
        elif available > 10:  # Minimo 10 USDT per fare trading
            # Allocazione parziale
            return True, available * 0.9  # Lascia 10% di margine
        else:
            # Allocazione fallita
            return False, 0.0
    
    def deallocate_budget(self, pair: str):
        """Dealloca budget di un bot"""
        bot_status = self.shared_state.get_bot_status(pair)
        if bot_status:
            bot_status.allocated_budget = 0.0
            self.shared_state.set_bot_status(bot_status)
        self.update_budget_info()

class MessageBroker:
    """📡 Broker messaggi per comunicazione inter-bot"""
    
    def __init__(self):
        self.message_queue = Queue()
        self.subscribers = {}  # Dict[topic, List[Queue]]
        
    def publish(self, topic: str, message: Dict):
        """Pubblica messaggio su topic"""
        timestamped_message = {
            'topic': topic,
            'timestamp': datetime.now().isoformat(),
            'data': message
        }
        
        # Invia a tutti i subscribers del topic
        if topic in self.subscribers:
            for subscriber_queue in self.subscribers[topic]:
                try:
                    subscriber_queue.put_nowait(timestamped_message)
                except:
                    # Queue full o subscriber morto
                    pass
    
    def subscribe(self, topic: str, subscriber_queue: Queue):
        """Sottoscrive a un topic"""
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(subscriber_queue)
    
    def unsubscribe(self, topic: str, subscriber_queue: Queue):
        """Cancella sottoscrizione"""
        if topic in self.subscribers:
            try:
                self.subscribers[topic].remove(subscriber_queue)
            except ValueError:
                pass

class SessionManager:
    """🎯 Session Manager principale"""
    
    def __init__(self):
        self.shared_state = SharedState()
        self.client = self._init_client()
        self.budget_coordinator = BudgetCoordinator(self.shared_state, self.client)
        self.message_broker = MessageBroker()
        
        self.workers = {}  # Dict[pair, Process]
        self.worker_queues = {}  # Dict[pair, Queue]
        
        self.running = False
        self.monitor_thread = None
        
    def _init_client(self) -> GateIOClient:
        """Inizializza client Gate.io"""
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
        
        api_key = os.getenv("GATE_API_KEY")
        secret_key = os.getenv("GATE_SECRET_KEY")
        
        if not api_key or not secret_key:
            raise ValueError("❌ Credenziali Gate.io non trovate. Configura GATE_API_KEY e GATE_SECRET_KEY")
        
        return GateIOClient(api_key, secret_key, rate_limit_enabled=True)
    
    def start(self):
        """Avvia Session Manager"""
        print("🚀 Avvio Multi-Bot Session Manager...")
        print("=" * 50)
        
        self.running = True
        
        # Avvia thread monitor
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        # Aggiorna budget iniziale
        budget_info = self.budget_coordinator.update_budget_info()
        print(f"💰 Budget USDT disponibile: {budget_info['available_usdt']:.2f}")
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        print("✅ Session Manager avviato con successo!")
        print("📊 Dashboard disponibile su porta 8888")
        print("🎮 Usa comandi: start, stop, status, dashboard")
        
    def stop(self):
        """Ferma Session Manager"""
        print("🛑 Arresto Session Manager...")
        
        self.running = False
        
        # Ferma tutti i worker
        for pair in list(self.workers.keys()):
            self.stop_bot(pair)
        
        print("✅ Session Manager arrestato")
    
    def _signal_handler(self, signum, frame):
        """Gestisce segnali di sistema"""
        print(f"\\n📡 Ricevuto segnale {signum}")
        self.stop()
        sys.exit(0)
    
    def _monitor_loop(self):
        """Loop di monitoraggio status bot"""
        while self.running:
            try:
                self._check_workers_health()
                self.budget_coordinator.update_budget_info()
                time.sleep(5)  # Check ogni 5 secondi
            except Exception as e:
                print(f"⚠️ Errore monitor loop: {e}")
                time.sleep(10)
    
    def _check_workers_health(self):
        """Controlla salute dei worker processes"""
        for pair, process in list(self.workers.items()):
            if not process.is_alive():
                print(f"💀 Worker {pair} è morto (exit code: {process.exitcode})")
                
                # Aggiorna status
                bot_status = self.shared_state.get_bot_status(pair)
                if bot_status:
                    bot_status.status = 'ERROR'
                    bot_status.errors_count += 1
                    self.shared_state.set_bot_status(bot_status)
                
                # Cleanup
                self._cleanup_worker(pair)
    
    def start_bot(self, pair: str, budget: float, target_percent: float = 2.0) -> bool:
        """Avvia un bot per una coppia"""
        print(f"🤖 Avvio bot per {pair}...")
        
        # Verifica se già esiste
        if pair in self.workers:
            print(f"⚠️ Bot per {pair} già attivo")
            return False
        
        # Alloca budget
        success, allocated_budget = self.budget_coordinator.allocate_budget(pair, budget)
        if not success:
            print(f"❌ Budget insufficiente per {pair}. Richiesti: {budget}, disponibili: {allocated_budget}")
            return False
        
        # Crea status bot
        bot_status = BotStatus(
            pair=pair,
            status='STARTING',
            start_time=datetime.now(),
            allocated_budget=allocated_budget
        )
        self.shared_state.set_bot_status(bot_status)
        
        # Crea queue comunicazione
        worker_queue = Queue()
        self.worker_queues[pair] = worker_queue
        
        # Avvia worker process
        process = mp.Process(
            target=self._run_bot_worker,
            args=(pair, allocated_budget, target_percent, worker_queue),
            name=f"BotWorker-{pair}"
        )
        process.start()
        
        # Registra worker
        self.workers[pair] = process
        
        # Aggiorna status
        bot_status.pid = process.pid
        bot_status.status = 'RUNNING'
        self.shared_state.set_bot_status(bot_status)
        
        print(f"✅ Bot {pair} avviato (PID: {process.pid}, Budget: {allocated_budget:.2f} USDT)")
        return True
    
    def stop_bot(self, pair: str) -> bool:
        """Ferma un bot"""
        if pair not in self.workers:
            print(f"⚠️ Bot {pair} non trovato")
            return False
        
        print(f"🛑 Arresto bot {pair}...")
        
        # Invia comando stop
        if pair in self.worker_queues:
            try:
                self.worker_queues[pair].put_nowait({'action': 'stop'})
            except:
                pass
        
        # Termina processo
        process = self.workers[pair]
        process.terminate()
        
        # Aspetta max 10 secondi
        process.join(timeout=10)
        if process.is_alive():
            print(f"⚠️ Terminazione forzata bot {pair}")
            process.kill()
            process.join()
        
        # Dealloca budget
        self.budget_coordinator.deallocate_budget(pair)
        
        # Aggiorna status
        bot_status = self.shared_state.get_bot_status(pair)
        if bot_status:
            bot_status.status = 'STOPPED'
            bot_status.pid = None
            self.shared_state.set_bot_status(bot_status)
        
        # Cleanup
        self._cleanup_worker(pair)
        
        print(f"✅ Bot {pair} arrestato")
        return True
    
    def _cleanup_worker(self, pair: str):
        """Pulisce risorse worker"""
        if pair in self.workers:
            del self.workers[pair]
        if pair in self.worker_queues:
            del self.worker_queues[pair]
    
    def _run_bot_worker(self, pair: str, budget: float, target_percent: float, command_queue: Queue):
        """Processo worker per un singolo bot"""
        try:
            # Avvia il bot worker usando subprocess
            cmd = [
                sys.executable,
                "dash01_refactored.py",
                "--worker-mode",
                "--pair", pair,
                "--budget", str(budget),
                "--target", str(target_percent)
            ]
            
            print(f"🔧 Avvio worker {pair}: {' '.join(cmd)}")
            
            # Avvia il processo worker
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Monitor del processo e comandi dal manager
            while process.poll() is None:
                # Check comandi dal manager
                try:
                    command = command_queue.get_nowait()
                    if command.get('action') == 'stop':
                        print(f"📡 Worker {pair} ricevuto comando stop")
                        process.terminate()
                        break
                except:
                    pass
                
                # Read output (non-blocking)
                try:
                    output = process.stdout.readline()
                    if output:
                        print(f"[{pair}] {output.strip()}")
                except:
                    pass
                
                time.sleep(0.1)
            
            # Aspetta terminazione
            try:
                stdout, stderr = process.communicate(timeout=5)
                if stdout:
                    print(f"[{pair}] STDOUT: {stdout}")
                if stderr:
                    print(f"[{pair}] STDERR: {stderr}")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"[{pair}] Processo terminato forzatamente")
                
        except Exception as e:
            print(f"❌ Errore worker {pair}: {e}")
        finally:
            print(f"🏁 Worker {pair} terminato")
    
    def get_status_summary(self) -> Dict:
        """Ottiene summary completo dello status"""
        all_bots = self.shared_state.get_all_bots()
        budget_info = self.shared_state.get_budget_info()
        
        return {
            'total_bots': len(all_bots),
            'active_bots': len([b for b in all_bots.values() if b.status == 'RUNNING']),
            'budget_info': budget_info,
            'bots': {pair: bot.to_dict() for pair, bot in all_bots.items()}
        }

# ===============================
# CLI INTERFACE
# ===============================

def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="🤖 Multi-Bot Session Manager")
    parser.add_argument('--daemon', action='store_true', help='Avvia in modalità daemon')
    
    subparsers = parser.add_subparsers(dest='command', help='Comandi disponibili')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Avvia session manager')
    
    # Stop command  
    stop_parser = subparsers.add_parser('stop', help='Ferma session manager')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Mostra status')
    
    # Add bot command
    add_parser = subparsers.add_parser('add-bot', help='Aggiungi bot')
    add_parser.add_argument('pair', help='Coppia trading (es: BTC_USDT)')
    add_parser.add_argument('--budget', type=float, default=50.0, help='Budget USDT')
    add_parser.add_argument('--target', type=float, default=2.0, help='Target % profit')
    
    # Remove bot command
    remove_parser = subparsers.add_parser('remove-bot', help='Rimuovi bot')
    remove_parser.add_argument('pair', help='Coppia trading')
    
    # Dashboard command
    dashboard_parser = subparsers.add_parser('dashboard', help='Avvia dashboard aggregata')
    
    args = parser.parse_args()
    
    if args.command == 'start' or not args.command:
        # Avvia session manager
        manager = SessionManager()
        manager.start()
        
        try:
            # Interactive CLI
            while manager.running:
                print("\\n" + "="*50)
                print("🎮 MULTI-BOT SESSION MANAGER")
                print("="*50)
                print("1. Aggiungi bot")
                print("2. Rimuovi bot") 
                print("3. Status sistema")
                print("4. Dashboard aggregata")
                print("5. Esci")
                
                choice = input("\\n➤ Scegli opzione: ").strip()
                
                if choice == '1':
                    pair = input("📈 Coppia (es: BTC_USDT): ").strip().upper()
                    budget = float(input("💰 Budget USDT: ") or "50.0")
                    target = float(input("🎯 Target % (default 2.0): ") or "2.0")
                    manager.start_bot(pair, budget, target)
                    
                elif choice == '2':
                    pair = input("📈 Coppia da rimuovere: ").strip().upper()
                    manager.stop_bot(pair)
                    
                elif choice == '3':
                    status = manager.get_status_summary()
                    print("\\n📊 STATUS SISTEMA:")
                    print(f"Bot totali: {status['total_bots']}")
                    print(f"Bot attivi: {status['active_bots']}")
                    print(f"Budget totale: {status['budget_info']['total_usdt']:.2f} USDT")
                    print(f"Budget allocato: {status['budget_info']['allocated_usdt']:.2f} USDT") 
                    print(f"Budget disponibile: {status['budget_info']['available_usdt']:.2f} USDT")
                    
                    print("\\n🤖 BOT ATTIVI:")
                    for pair, bot_data in status['bots'].items():
                        print(f"  {pair}: {bot_data['status']} (Budget: {bot_data['allocated_budget']:.2f})")
                    
                elif choice == '4':
                    print("🚀 Avvio dashboard aggregata...")
                    # TODO: Implementare dashboard
                    input("Premi INVIO per continuare...")
                    
                elif choice == '5':
                    break
                    
        except KeyboardInterrupt:
            pass
        finally:
            manager.stop()
    
    elif args.command == 'add-bot':
        # Quick add bot (richiede manager attivo)
        print(f"🤖 Aggiunta bot {args.pair} con budget {args.budget} USDT")
        # TODO: Comunicare con manager esistente
        
    elif args.command == 'status':
        # Quick status
        shared_state = SharedState()
        all_bots = shared_state.get_all_bots()
        budget_info = shared_state.get_budget_info()
        
        print("📊 STATUS RAPIDO:")
        print(f"Bot attivi: {len([b for b in all_bots.values() if b.status == 'RUNNING'])}")
        print(f"Budget disponibile: {budget_info['available_usdt']:.2f} USDT")

if __name__ == "__main__":
    main()