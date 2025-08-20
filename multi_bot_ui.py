#!/usr/bin/env python3
"""
🎮 Multi-Bot Management UI
Interactive console interface following MVC pattern and SOLID principles
"""

import os
import sys
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multi_bot_manager import (
    MultiBotManager, BotConfiguration, BotInstance, BotStatus, 
    BotObserver, StartBotCommand, StopBotCommand, ConsoleBotObserver
)

class MultiBotView:
    """🎨 View layer for multi-bot management (MVC Pattern - View)"""
    
    @staticmethod
    def clear_screen():
        """Clear console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def show_header():
        """Display application header"""
        print("🤖 MULTI-BOT MANAGER - GESTIONE SCALPING AVANZATA")
        print("=" * 60)
    
    @staticmethod  
    def show_main_menu():
        """Display main menu options"""
        print("\n📋 MENU PRINCIPALE:")
        print("   1. 📊 Visualizza tutti i bot")
        print("   2. 🚀 Avvia nuovo bot")  
        print("   3. 🎮 Gestione bot attivi")
        print("   4. 📈 Statistiche e performance")
        print("   5. 🔧 Configurazione avanzata")
        print("   6. ❌ Esci")
        print()
    
    @staticmethod
    def show_bot_list(bots: Dict[str, BotInstance]):
        """Display list of all bots"""
        if not bots:
            print("📝 Nessun bot registrato")
            return
        
        print(f"\n📊 LISTA BOT ({len(bots)} totali):")
        print("-" * 80)
        print(f"{'ID':<15} {'PAIR':<12} {'STATUS':<12} {'BUDGET':<10} {'TARGET':<8} {'CREATO':<10}")
        print("-" * 80)
        
        for bot_id, bot in bots.items():
            created = datetime.fromisoformat(bot.created_at).strftime("%H:%M:%S") if bot.created_at else "N/A"
            status_emoji = MultiBotView._get_status_emoji(bot.status)
            
            print(f"{bot_id:<15} {bot.pair:<12} {status_emoji}{bot.status.value:<11} "
                  f"${bot.config.budget_per_trade:<9.0f} {bot.config.target_profit:<7.1f}% {created:<10}")
        print("-" * 80)
    
    @staticmethod
    def show_running_bots(running_bots: List[BotInstance]):
        """Display running bots with detailed info"""
        if not running_bots:
            print("⚠️  Nessun bot in esecuzione")
            return
        
        print(f"\n🏃 BOT IN ESECUZIONE ({len(running_bots)}):")
        print("=" * 70)
        
        for i, bot in enumerate(running_bots, 1):
            runtime = "N/A"
            if bot.started_at:
                start_time = datetime.fromisoformat(bot.started_at)
                runtime = str(datetime.now() - start_time).split('.')[0]  # Remove microseconds
            
            print(f"{i}. 🤖 {bot.bot_id}")
            print(f"   📈 Coppia: {bot.pair}")
            print(f"   💰 Budget: ${bot.config.budget_per_trade}")
            print(f"   🎯 Target: {bot.config.target_profit}%")
            print(f"   ⏰ Runtime: {runtime}")
            print(f"   📊 Trades: {bot.trade_count}")
            if bot.profit_loss != 0:
                pnl_color = "📈" if bot.profit_loss > 0 else "📉"
                print(f"   {pnl_color} P&L: ${bot.profit_loss:.2f}")
            print()
    
    @staticmethod
    def show_bot_management_menu():
        """Display bot management options"""
        print("\n🎮 GESTIONE BOT ATTIVI:")
        print("   1. 🛑 Ferma bot specifico")
        print("   2. 🛑 Ferma tutti i bot") 
        print("   3. 📊 Dettagli bot specifico")
        print("   4. 🔄 Refresh status")
        print("   5. ⬅️  Torna al menu principale")
        print()
    
    @staticmethod
    def show_bot_details(bot: BotInstance):
        """Display detailed bot information"""
        print(f"\n🔍 DETTAGLI BOT: {bot.bot_id}")
        print("=" * 50)
        print(f"📈 Coppia: {bot.pair}")
        print(f"📊 Status: {MultiBotView._get_status_emoji(bot.status)} {bot.status.value}")
        print(f"💰 Budget per trade: ${bot.config.budget_per_trade}")
        print(f"🎯 Target profitto: {bot.config.target_profit}%")
        print(f"🔢 Max trades: {bot.config.max_trades}")
        print(f"⏱️  Sleep cicli: {bot.config.sleep_between_cycles}s")
        print(f"⏰ Timeout: {bot.config.timeout_minutes} min")
        print(f"🛡️  Max loss: {bot.config.max_daily_loss*100:.1f}%")
        print(f"📊 Min win rate: {bot.config.min_win_rate*100:.1f}%")
        
        if bot.created_at:
            print(f"📅 Creato: {datetime.fromisoformat(bot.created_at).strftime('%Y-%m-%d %H:%M:%S')}")
        if bot.started_at:
            print(f"🚀 Avviato: {datetime.fromisoformat(bot.started_at).strftime('%Y-%m-%d %H:%M:%S')}")
        if bot.stopped_at:
            print(f"🛑 Fermato: {datetime.fromisoformat(bot.stopped_at).strftime('%Y-%m-%d %H:%M:%S')}")
        
        if bot.last_error:
            print(f"❌ Ultimo errore: {bot.last_error}")
        
        print("=" * 50)
    
    @staticmethod
    def show_statistics(bots: Dict[str, BotInstance]):
        """Display bot statistics"""
        if not bots:
            print("📊 Nessuna statistica disponibile")
            return
        
        total = len(bots)
        running = len([b for b in bots.values() if b.status == BotStatus.RUNNING])
        stopped = len([b for b in bots.values() if b.status == BotStatus.STOPPED])
        error = len([b for b in bots.values() if b.status == BotStatus.ERROR])
        idle = len([b for b in bots.values() if b.status == BotStatus.IDLE])
        
        # Group by pair
        pairs = {}
        for bot in bots.values():
            if bot.pair not in pairs:
                pairs[bot.pair] = {'count': 0, 'running': 0}
            pairs[bot.pair]['count'] += 1
            if bot.status == BotStatus.RUNNING:
                pairs[bot.pair]['running'] += 1
        
        print(f"\n📊 STATISTICHE GENERALI:")
        print("=" * 40)
        print(f"🤖 Bot totali: {total}")
        print(f"🏃 In esecuzione: {running}")
        print(f"🛑 Fermati: {stopped}")
        print(f"😴 Inattivi: {idle}")
        print(f"❌ Con errori: {error}")
        print()
        
        print(f"📈 DISTRIBUZIONE PER COPPIA:")
        print("-" * 30)
        for pair, stats in pairs.items():
            print(f"{pair}: {stats['count']} bot ({stats['running']} attivi)")
        print("-" * 30)
    
    @staticmethod
    def _get_status_emoji(status: BotStatus) -> str:
        """Get emoji for bot status"""
        emoji_map = {
            BotStatus.IDLE: "😴 ",
            BotStatus.STARTING: "🟡 ",
            BotStatus.RUNNING: "🟢 ",
            BotStatus.STOPPING: "🟠 ",
            BotStatus.STOPPED: "⚫ ",
            BotStatus.ERROR: "🔴 "
        }
        return emoji_map.get(status, "❓ ")
    
    @staticmethod
    def get_user_input(prompt: str, valid_options: List[str] = None) -> str:
        """Get validated user input"""
        while True:
            try:
                user_input = input(prompt).strip()
                if not user_input:
                    continue
                
                if valid_options and user_input not in valid_options:
                    print(f"❌ Opzione non valida. Scegli tra: {', '.join(valid_options)}")
                    continue
                
                return user_input
            except (EOFError, KeyboardInterrupt):
                return ""
    
    @staticmethod
    def get_bot_config() -> Optional[BotConfiguration]:
        """Get bot configuration from user input"""
        print("\n⚙️  CONFIGURAZIONE NUOVO BOT:")
        print("-" * 35)
        
        try:
            pair = MultiBotView.get_user_input("📈 Coppia (es. XNY_USDT): ")
            if not pair:
                return None
            
            budget = float(MultiBotView.get_user_input("💰 Budget per trade ($): ") or "50")
            target = float(MultiBotView.get_user_input("🎯 Target profitto (%): ") or "2.5") 
            max_trades = int(MultiBotView.get_user_input("🔢 Max trades: ") or "100")
            sleep_cycles = float(MultiBotView.get_user_input("⏱️  Sleep tra cicli (s): ") or "1.0")
            timeout = int(MultiBotView.get_user_input("⏰ Timeout sessione (min): ") or "60")
            max_loss = float(MultiBotView.get_user_input("🛡️  Max perdita giornaliera (%): ") or "10") / 100
            min_winrate = float(MultiBotView.get_user_input("📊 Min win rate (%): ") or "30") / 100
            
            return BotConfiguration(
                pair=pair.upper(),
                budget_per_trade=budget,
                target_profit=target,
                max_trades=max_trades,
                sleep_between_cycles=sleep_cycles,
                timeout_minutes=timeout,
                max_daily_loss=max_loss,
                min_win_rate=min_winrate
            )
        except (ValueError, EOFError, KeyboardInterrupt):
            print("❌ Configurazione annullata")
            return None

class MultiBotController:
    """🎯 Controller layer for multi-bot management (MVC Pattern - Controller)"""
    
    def __init__(self):
        """Initialize controller (Dependency Injection)"""
        self.manager = MultiBotManager()
        self.view = MultiBotView()
        self.observer = ConsoleBotObserver()
        self.manager.add_observer(self.observer)
        self.running = True
    
    def run(self):
        """Main application loop (Template Method Pattern)"""
        while self.running:
            try:
                self._show_main_screen()
                choice = self.view.get_user_input("🎯 Scelta: ", ["1", "2", "3", "4", "5", "6"])
                
                if choice == "1":
                    self._handle_view_bots()
                elif choice == "2":  
                    self._handle_create_bot()
                elif choice == "3":
                    self._handle_manage_bots()
                elif choice == "4":
                    self._handle_statistics()
                elif choice == "5":
                    self._handle_advanced_config()
                elif choice == "6":
                    self._handle_exit()
                else:
                    print("❌ Opzione non valida")
                
                if choice != "6":
                    input("\n⏸️  Premi INVIO per continuare...")
                    
            except (EOFError, KeyboardInterrupt):
                self._handle_exit()
                break
    
    def _show_main_screen(self):
        """Display main screen (Template Method)"""
        self.view.clear_screen()
        self.view.show_header()
        
        # Show quick status
        all_bots = self.manager.get_all_bots()
        running_count = len([b for b in all_bots.values() if b.status == BotStatus.RUNNING])
        
        print(f"📊 Status: {len(all_bots)} bot totali | {running_count} in esecuzione")
        
        self.view.show_main_menu()
    
    def _handle_view_bots(self):
        """Handle view all bots (Single Responsibility)"""
        print("\n📊 VISUALIZZAZIONE BOT")
        print("=" * 30)
        
        all_bots = self.manager.get_all_bots()
        self.view.show_bot_list(all_bots)
        
        if all_bots:
            print(f"\n💡 Usa opzione 3 per gestire i bot attivi")
    
    def _handle_create_bot(self):
        """Handle create new bot (Single Responsibility)"""
        print("\n🚀 CREAZIONE NUOVO BOT")
        print("=" * 25)
        
        config = self.view.get_bot_config()
        if not config:
            return
        
        try:
            bot_id = self.manager.register_bot(config)
            print(f"✅ Bot creato con successo!")
            print(f"🤖 ID Bot: {bot_id}")
            print(f"📈 Coppia: {config.pair}")
            
            # Ask if user wants to start immediately
            start_now = self.view.get_user_input("\n🚀 Avviare subito? (s/n): ", ["s", "n", "S", "N"])
            if start_now.lower() == 's':
                command = StartBotCommand(self.manager, bot_id)
                if self.manager.execute_command(command):
                    print("✅ Bot avviato con successo!")
                else:
                    print("❌ Errore nell'avvio del bot")
                    
        except Exception as e:
            print(f"❌ Errore nella creazione: {e}")
    
    def _handle_manage_bots(self):
        """Handle bot management (Single Responsibility)"""
        while True:
            self.view.clear_screen()
            print("\n🎮 GESTIONE BOT ATTIVI")
            print("=" * 25)
            
            running_bots = self.manager.get_running_bots()
            self.view.show_running_bots(running_bots)
            
            self.view.show_bot_management_menu()
            
            choice = self.view.get_user_input("🎯 Scelta: ", ["1", "2", "3", "4", "5"])
            
            if choice == "1":
                self._handle_stop_specific_bot()
            elif choice == "2":
                self._handle_stop_all_bots()
            elif choice == "3":
                self._handle_bot_details()
            elif choice == "4":
                continue  # Refresh by restarting loop
            elif choice == "5":
                break  # Return to main menu
            
            if choice in ["1", "2", "3"]:
                input("\n⏸️  Premi INVIO per continuare...")
    
    def _handle_stop_specific_bot(self):
        """Handle stopping specific bot"""
        running_bots = self.manager.get_running_bots()
        if not running_bots:
            print("⚠️  Nessun bot in esecuzione")
            return
        
        print("\n🛑 FERMA BOT SPECIFICO:")
        for i, bot in enumerate(running_bots, 1):
            print(f"   {i}. {bot.bot_id} ({bot.pair})")
        
        try:
            choice = int(self.view.get_user_input(f"Scegli bot (1-{len(running_bots)}): "))
            if 1 <= choice <= len(running_bots):
                selected_bot = running_bots[choice - 1]
                
                confirm = self.view.get_user_input(f"🛑 Confermi stop di {selected_bot.bot_id}? (s/n): ", ["s", "n", "S", "N"])
                if confirm.lower() == 's':
                    command = StopBotCommand(self.manager, selected_bot.bot_id)
                    if self.manager.execute_command(command):
                        print("✅ Bot fermato con successo!")
                    else:
                        print("❌ Errore nel fermare il bot")
            else:
                print("❌ Scelta non valida")
        except ValueError:
            print("❌ Inserire un numero valido")
    
    def _handle_stop_all_bots(self):
        """Handle stopping all bots"""
        running_bots = self.manager.get_running_bots()
        if not running_bots:
            print("⚠️  Nessun bot in esecuzione")
            return
        
        confirm = self.view.get_user_input(f"🛑 Confermi stop di TUTTI i {len(running_bots)} bot? (s/n): ", ["s", "n", "S", "N"])
        if confirm.lower() == 's':
            success_count = 0
            for bot in running_bots:
                command = StopBotCommand(self.manager, bot.bot_id)
                if self.manager.execute_command(command):
                    success_count += 1
            
            print(f"✅ {success_count}/{len(running_bots)} bot fermati con successo")
    
    def _handle_bot_details(self):
        """Handle showing bot details"""
        all_bots = self.manager.get_all_bots()
        if not all_bots:
            print("📝 Nessun bot disponibile")
            return
        
        print("\n🔍 DETTAGLI BOT - Scegli bot:")
        bot_list = list(all_bots.items())
        for i, (bot_id, bot) in enumerate(bot_list, 1):
            status_emoji = self.view._get_status_emoji(bot.status)
            print(f"   {i}. {bot_id} - {bot.pair} {status_emoji}")
        
        try:
            choice = int(self.view.get_user_input(f"Scegli bot (1-{len(bot_list)}): "))
            if 1 <= choice <= len(bot_list):
                selected_bot = bot_list[choice - 1][1]
                self.view.show_bot_details(selected_bot)
            else:
                print("❌ Scelta non valida")
        except ValueError:
            print("❌ Inserire un numero valido")
    
    def _handle_statistics(self):
        """Handle statistics display"""
        print("\n📊 STATISTICHE E PERFORMANCE")
        print("=" * 35)
        
        all_bots = self.manager.get_all_bots()
        self.view.show_statistics(all_bots)
    
    def _handle_advanced_config(self):
        """Handle advanced configuration"""
        print("\n🔧 CONFIGURAZIONE AVANZATA")
        print("=" * 30)
        print("⚠️  Funzionalità in sviluppo")
        print("💡 Prossime features:")
        print("   - Backup/Restore configurazioni")
        print("   - Templates bot predefiniti") 
        print("   - Gestione log avanzata")
        print("   - Notifiche email/telegram")
    
    def _handle_exit(self):
        """Handle application exit"""
        running_bots = self.manager.get_running_bots()
        if running_bots:
            print(f"\n⚠️  Attenzione: {len(running_bots)} bot ancora in esecuzione!")
            print("🤖 Bot attivi:")
            for bot in running_bots:
                print(f"   - {bot.bot_id} ({bot.pair})")
            
            choice = self.view.get_user_input("\n🛑 Fermare tutti i bot prima di uscire? (s/n): ", ["s", "n", "S", "N"])
            if choice.lower() == 's':
                print("🛑 Fermando tutti i bot...")
                for bot in running_bots:
                    command = StopBotCommand(self.manager, bot.bot_id)
                    self.manager.execute_command(command)
                print("✅ Tutti i bot fermati")
        
        print("\n👋 Arrivederci! Bot manager chiuso.")
        self.running = False

def main():
    """🚀 Main application entry point"""
    print("🤖 Inizializzazione Multi-Bot Manager...")
    
    # Check environment
    if not os.getenv("GATE_API_KEY") or not os.getenv("GATE_SECRET_KEY"):
        print("❌ Credenziali API Gate.io non configurate!")
        print("💡 Configura GATE_API_KEY e GATE_SECRET_KEY nelle variabili d'ambiente")
        return
    
    try:
        controller = MultiBotController()
        controller.run()
    except Exception as e:
        print(f"❌ Errore critico: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()