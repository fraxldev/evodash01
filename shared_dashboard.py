#!/usr/bin/env python3
"""
📊 SHARED DASHBOARD AGGREGATA
==============================
Dashboard unificata per monitoraggio multi-bot real-time.

Caratteristiche:
- Vista aggregata di tutti i bot attivi
- Monitoraggio budget e performance in tempo reale
- Controlli per start/stop bot individuali
- Statistiche globali e per-bot
- WebSocket integration per performance

Autore: Claude Code + User
Data: 2025-08-12
"""

import curses
import json
import time
import threading
import signal
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

# Import dei componenti del session manager
try:
    from session_manager import SharedState, BotStatus, BudgetCoordinator, SessionManager
    from dash01_refactored import GateIOClient
except ImportError as e:
    print(f"❌ Errore import: {e}")
    print("💡 Assicurati che session_manager.py e dash01_refactored.py siano presenti")
    sys.exit(1)

class SharedDashboard:
    """📊 Dashboard aggregata per Session Manager"""
    
    def __init__(self, shared_state: SharedState):
        self.shared_state = shared_state
        self.stdscr = None
        self.height = 0
        self.width = 0
        
        # Stati UI
        self.current_selection = 0
        self.scroll_offset = 0
        self.refresh_rate = 1.0  # secondi
        self.last_refresh = 0
        
        # Thread per aggiornamento automatico
        self.update_thread = None
        self.running = False
        
        # Colors
        self.colors_initialized = False
        
        # Cache dati
        self.cached_data = {}
        self.cache_timestamp = 0
        
    def init_colors(self):
        """Inizializza colori curses"""
        if self.colors_initialized:
            return
            
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)    # Verde
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)      # Rosso
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)   # Giallo
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)     # Ciano
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  # Magenta
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)    # Bianco
        
        self.GREEN = curses.color_pair(1)
        self.RED = curses.color_pair(2)
        self.YELLOW = curses.color_pair(3)
        self.CYAN = curses.color_pair(4)
        self.MAGENTA = curses.color_pair(5)
        self.WHITE = curses.color_pair(6)
        
        self.colors_initialized = True
    
    def start(self, stdscr):
        """Avvia dashboard"""
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        
        # Setup curses
        curses.curs_set(0)  # Nasconde cursore
        stdscr.nodelay(1)   # Non-blocking input
        stdscr.timeout(100) # 100ms timeout
        
        self.init_colors()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.running = True
        
        # Avvia thread aggiornamento
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        
        # Main UI loop
        try:
            self._main_loop()
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()
    
    def stop(self):
        """Ferma dashboard"""
        self.running = False
        if self.update_thread:
            self.update_thread.join(timeout=1)
    
    def _signal_handler(self, signum, frame):
        """Gestisce segnali di sistema"""
        self.running = False
    
    def _update_loop(self):
        """Loop aggiornamento dati in background"""
        while self.running:
            try:
                # Aggiorna cache dati
                self._update_cache()
                time.sleep(self.refresh_rate)
            except Exception as e:
                # Log errore ma continua
                pass
    
    def _update_cache(self):
        """Aggiorna cache dati dal shared state"""
        try:
            # Ottieni tutti i dati
            all_bots = self.shared_state.get_all_bots()
            budget_info = self.shared_state.get_budget_info()
            
            # Calcola statistiche aggregate
            total_bots = len(all_bots)
            active_bots = len([b for b in all_bots.values() if b.status == 'RUNNING'])
            total_trades = sum(b.trades_today for b in all_bots.values())
            total_pnl = sum(b.pnl_percent for b in all_bots.values())
            
            # Errori totali
            total_errors = sum(b.errors_count for b in all_bots.values())
            
            self.cached_data = {
                'bots': all_bots,
                'budget': budget_info,
                'stats': {
                    'total_bots': total_bots,
                    'active_bots': active_bots,
                    'total_trades': total_trades,
                    'total_pnl': total_pnl,
                    'total_errors': total_errors
                },
                'timestamp': datetime.now()
            }
            self.cache_timestamp = time.time()
            
        except Exception as e:
            # In caso di errore, mantieni cache precedente
            pass
    
    def _main_loop(self):
        """Main loop UI"""
        while self.running:
            try:
                # Aggiorna dimensioni schermo
                self.height, self.width = self.stdscr.getmaxyx()
                
                # Disegna UI
                self._draw_ui()
                
                # Gestisci input
                key = self.stdscr.getch()
                if key != -1:  # Key premuto
                    if self._handle_input(key):
                        break  # Uscita richiesta
                
                # Refresh schermo
                self.stdscr.refresh()
                
                time.sleep(0.05)  # 20 FPS
                
            except curses.error:
                # Errore curses (es. resize), ignora
                pass
    
    def _handle_input(self, key) -> bool:
        """Gestisce input utente. Returns True per uscita"""
        
        if key in [ord('q'), ord('Q'), 27]:  # Q o ESC
            return True
            
        elif key == curses.KEY_UP:
            self.current_selection = max(0, self.current_selection - 1)
            
        elif key == curses.KEY_DOWN:
            max_selection = len(self.cached_data.get('bots', {}))
            self.current_selection = min(max_selection, self.current_selection + 1)
            
        elif key in [ord('\\n'), ord('\\r'), curses.KEY_ENTER, 10]:  # ENTER
            self._handle_action()
            
        elif key in [ord('r'), ord('R')]:  # Refresh
            self._update_cache()
            
        elif key in [ord('a'), ord('A')]:  # Add bot
            self._add_bot_dialog()
            
        elif key in [ord('d'), ord('D')]:  # Delete bot
            self._delete_bot_dialog()
            
        elif key in [ord('s'), ord('S')]:  # Start/Stop bot
            self._toggle_bot()
            
        elif key in [ord('h'), ord('H')]:  # Help
            self._show_help()
        
        return False
    
    def _draw_ui(self):
        """Disegna interfaccia utente"""
        try:
            self.stdscr.clear()
            
            # Header
            self._draw_header()
            
            # Budget panel
            row = self._draw_budget_panel(3)
            
            # Stats panel
            row = self._draw_stats_panel(row + 1)
            
            # Bots list
            row = self._draw_bots_list(row + 1)
            
            # Footer
            self._draw_footer()
            
        except curses.error:
            pass
    
    def _draw_header(self):
        """Disegna header"""
        title = "🤖 MULTI-BOT SESSION MANAGER - DASHBOARD AGGREGATA"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Centrare titolo
        title_x = max(0, (self.width - len(title)) // 2)
        time_x = max(0, self.width - len(timestamp) - 2)
        
        try:
            self.stdscr.addstr(0, title_x, title, self.CYAN | curses.A_BOLD)
            self.stdscr.addstr(1, time_x, timestamp, self.WHITE)
            
            # Linea separatore
            self.stdscr.addstr(2, 0, "=" * self.width, self.YELLOW)
        except curses.error:
            pass
    
    def _draw_budget_panel(self, start_row) -> int:
        """Disegna pannello budget"""
        budget = self.cached_data.get('budget', {})
        
        try:
            self.stdscr.addstr(start_row, 2, "💰 BUDGET GLOBALE", self.MAGENTA | curses.A_BOLD)
            
            total = budget.get('total_usdt', 0)
            allocated = budget.get('allocated_usdt', 0)
            available = budget.get('available_usdt', 0)
            
            allocation_percent = (allocated / total * 100) if total > 0 else 0
            
            self.stdscr.addstr(start_row + 1, 4, f"Totale: {total:.2f} USDT", self.WHITE)
            self.stdscr.addstr(start_row + 2, 4, f"Allocato: {allocated:.2f} USDT ({allocation_percent:.1f}%)", 
                              self.YELLOW if allocation_percent > 80 else self.GREEN)
            self.stdscr.addstr(start_row + 3, 4, f"Disponibile: {available:.2f} USDT", 
                              self.RED if available < 10 else self.GREEN)
                              
        except curses.error:
            pass
            
        return start_row + 4
    
    def _draw_stats_panel(self, start_row) -> int:
        """Disegna pannello statistiche"""
        stats = self.cached_data.get('stats', {})
        
        try:
            self.stdscr.addstr(start_row, 2, "📊 STATISTICHE GLOBALI", self.CYAN | curses.A_BOLD)
            
            total_bots = stats.get('total_bots', 0)
            active_bots = stats.get('active_bots', 0)
            total_trades = stats.get('total_trades', 0)
            total_pnl = stats.get('total_pnl', 0)
            total_errors = stats.get('total_errors', 0)
            
            # Riga 1: Bot info
            self.stdscr.addstr(start_row + 1, 4, f"Bot totali: {total_bots}", self.WHITE)
            self.stdscr.addstr(start_row + 1, 20, f"Bot attivi: {active_bots}", 
                              self.GREEN if active_bots > 0 else self.RED)
            
            # Riga 2: Performance
            self.stdscr.addstr(start_row + 2, 4, f"Trades oggi: {total_trades}", self.WHITE)
            pnl_color = self.GREEN if total_pnl > 0 else self.RED if total_pnl < 0 else self.YELLOW
            self.stdscr.addstr(start_row + 2, 20, f"P&L totale: {total_pnl:+.2f}%", pnl_color)
            
            # Riga 3: Errori
            error_color = self.RED if total_errors > 5 else self.YELLOW if total_errors > 0 else self.GREEN
            self.stdscr.addstr(start_row + 3, 4, f"Errori totali: {total_errors}", error_color)
            
        except curses.error:
            pass
            
        return start_row + 4
    
    def _draw_bots_list(self, start_row) -> int:
        """Disegna lista bot"""
        bots = self.cached_data.get('bots', {})
        
        try:
            self.stdscr.addstr(start_row, 2, "🤖 BOT ATTIVI", self.GREEN | curses.A_BOLD)
            
            if not bots:
                self.stdscr.addstr(start_row + 2, 4, "Nessun bot configurato", self.YELLOW)
                return start_row + 3
            
            # Header tabella
            header_row = start_row + 1
            self.stdscr.addstr(header_row, 4, "PAIR", self.WHITE | curses.A_BOLD)
            self.stdscr.addstr(header_row, 15, "STATUS", self.WHITE | curses.A_BOLD)
            self.stdscr.addstr(header_row, 25, "BUDGET", self.WHITE | curses.A_BOLD)
            self.stdscr.addstr(header_row, 35, "TRADES", self.WHITE | curses.A_BOLD)
            self.stdscr.addstr(header_row, 45, "P&L %", self.WHITE | curses.A_BOLD)
            self.stdscr.addstr(header_row, 55, "LAST ACTION", self.WHITE | curses.A_BOLD)
            
            # Linea separatore
            self.stdscr.addstr(header_row + 1, 4, "-" * (self.width - 8), self.WHITE)
            
            # Lista bot
            row = header_row + 2
            bot_index = 0
            
            for pair, bot in bots.items():
                if row >= self.height - 3:  # Lascia spazio per footer
                    break
                    
                # Highlight selezione corrente
                attr = curses.A_REVERSE if bot_index == self.current_selection else 0
                
                # Status color
                status_color = (self.GREEN if bot.status == 'RUNNING' else 
                              self.YELLOW if bot.status in ['STARTING', 'PAUSED'] else 
                              self.RED)
                
                # P&L color
                pnl_color = (self.GREEN if bot.pnl_percent > 0 else 
                           self.RED if bot.pnl_percent < 0 else 
                           self.YELLOW)
                
                # Disegna riga
                self.stdscr.addstr(row, 4, pair[:10], self.WHITE | attr)
                self.stdscr.addstr(row, 15, bot.status[:8], status_color | attr)
                self.stdscr.addstr(row, 25, f"{bot.allocated_budget:.1f}", self.CYAN | attr)
                self.stdscr.addstr(row, 35, str(bot.trades_today), self.WHITE | attr)
                self.stdscr.addstr(row, 45, f"{bot.pnl_percent:+.2f}", pnl_color | attr)
                
                # Last action
                last_action = bot.last_action[:15] if bot.last_action else "N/A"
                self.stdscr.addstr(row, 55, last_action, self.WHITE | attr)
                
                row += 1
                bot_index += 1
                
        except curses.error:
            pass
            
        return row
    
    def _draw_footer(self):
        """Disegna footer con comandi"""
        footer_row = self.height - 1
        
        commands = [
            "Q:Quit", "↑↓:Navigate", "ENTER:Action", "S:Start/Stop",
            "A:Add", "D:Delete", "R:Refresh", "H:Help"
        ]
        
        footer_text = "  |  ".join(commands)
        
        try:
            # Centrare footer
            footer_x = max(0, (self.width - len(footer_text)) // 2)
            self.stdscr.addstr(footer_row, footer_x, footer_text, self.MAGENTA)
        except curses.error:
            pass
    
    def _handle_action(self):
        """Gestisce azione su bot selezionato"""
        bots = list(self.cached_data.get('bots', {}).items())
        
        if 0 <= self.current_selection < len(bots):
            pair, bot = bots[self.current_selection]
            
            # Toggle start/stop
            if bot.status == 'RUNNING':
                self._stop_bot(pair)
            else:
                self._start_bot(pair)
    
    def _toggle_bot(self):
        """Toggle start/stop bot selezionato"""
        self._handle_action()
    
    def _start_bot(self, pair: str):
        """Avvia bot (placeholder - comunica con session manager)"""
        # TODO: Implementare comunicazione con session manager per start bot
        pass
    
    def _stop_bot(self, pair: str):
        """Ferma bot (placeholder - comunica con session manager)"""
        # TODO: Implementare comunicazione con session manager per stop bot
        pass
    
    def _add_bot_dialog(self):
        """Dialog per aggiungere nuovo bot"""
        # TODO: Implementare dialog per aggiungere bot
        pass
    
    def _delete_bot_dialog(self):
        """Dialog per eliminare bot"""
        # TODO: Implementare dialog per eliminare bot
        pass
    
    def _show_help(self):
        """Mostra help"""
        help_text = [
            "🤖 MULTI-BOT SESSION MANAGER - HELP",
            "",
            "COMANDI:",
            "  Q / ESC     - Esci dalla dashboard",
            "  ↑ / ↓       - Naviga lista bot",
            "  ENTER / S   - Start/Stop bot selezionato",
            "  A           - Aggiungi nuovo bot",
            "  D           - Elimina bot selezionato",
            "  R           - Refresh dati",
            "  H           - Mostra questo help",
            "",
            "STATI BOT:",
            "  RUNNING     - Bot attivo e operativo",
            "  STARTING    - Bot in fase di avvio",
            "  STOPPED     - Bot fermato",
            "  ERROR       - Bot in errore",
            "  PAUSED      - Bot in pausa",
            "",
            "BUDGET:",
            "  Totale      - Budget USDT totale disponibile",
            "  Allocato    - Budget attualmente allocato ai bot",
            "  Disponibile - Budget libero per nuovi bot",
            "",
            "Premi un tasto per chiudere..."
        ]
        
        # Dialog help
        try:
            self.stdscr.clear()
            
            start_row = max(0, (self.height - len(help_text)) // 2)
            
            for i, line in enumerate(help_text):
                if start_row + i < self.height:
                    line_x = max(0, (self.width - len(line)) // 2)
                    self.stdscr.addstr(start_row + i, line_x, line, self.WHITE)
            
            self.stdscr.refresh()
            self.stdscr.getch()  # Aspetta input
            
        except curses.error:
            pass

def start_shared_dashboard():
    """Avvia dashboard aggregata"""
    
    def dashboard_wrapper(stdscr):
        shared_state = SharedState()
        dashboard = SharedDashboard(shared_state)
        dashboard.start(stdscr)
    
    # Avvia con curses wrapper
    try:
        curses.wrapper(dashboard_wrapper)
    except KeyboardInterrupt:
        print("\\n👋 Dashboard chiusa")
    except Exception as e:
        print(f"❌ Errore dashboard: {e}")

if __name__ == "__main__":
    print("🚀 Avvio Shared Dashboard...")
    start_shared_dashboard()