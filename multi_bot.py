#!/usr/bin/env python3
"""
🚀 MULTI-BOT LAUNCHER
=====================
Launcher principale per il sistema Multi-Bot Session Manager.

Uso:
    python multi_bot.py                    # Menu interattivo
    python multi_bot.py start              # Avvia session manager
    python multi_bot.py dashboard          # Dashboard aggregata
    python multi_bot.py add BTC_USDT 50    # Aggiungi bot BTC_USDT con 50 USDT
    python multi_bot.py stop BTC_USDT      # Ferma bot BTC_USDT
    python multi_bot.py status             # Status sistema

Autore: Claude Code + User
Data: 2025-08-12
"""

import sys
import os
import argparse
import time
import subprocess
from pathlib import Path

def print_banner():
    """Stampa banner del sistema"""
    banner = """
🤖 MULTI-BOT SESSION MANAGER v1.0
===================================
Sistema di gestione multi-bot per trading automatico su Gate.io

Caratteristiche:
✅ Gestione simultanea di più bot su coppie diverse
✅ Allocazione automatica del budget USDT
✅ Dashboard aggregata real-time
✅ Coordinamento intelligente anti-conflitti
✅ Monitoraggio performance centralizzato
    """
    print(banner)

def check_dependencies():
    """Verifica dipendenze del sistema"""
    required_files = [
        'session_manager.py',
        'dash01_refactored.py', 
        'shared_dashboard.py'
    ]
    
    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)
    
    if missing:
        print(f"❌ File mancanti: {', '.join(missing)}")
        return False
    
    # Verifica credenziali
    if not os.getenv("GATE_API_KEY") or not os.getenv("GATE_SECRET_KEY"):
        print("❌ Credenziali Gate.io non configurate")
        print("💡 Configura GATE_API_KEY e GATE_SECRET_KEY nel file .env")
        return False
    
    print("✅ Tutte le dipendenze soddisfatte")
    return True

def start_session_manager():
    """Avvia il session manager"""
    print("🚀 Avvio Session Manager...")
    
    try:
        subprocess.run([sys.executable, "session_manager.py", "start"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Errore avvio session manager: {e}")
        return False
    except KeyboardInterrupt:
        print("\\n🛑 Session Manager interrotto")
    
    return True

def start_dashboard():
    """Avvia dashboard aggregata"""
    print("📊 Avvio Dashboard Aggregata...")
    
    try:
        subprocess.run([sys.executable, "shared_dashboard.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Errore avvio dashboard: {e}")
        return False
    except KeyboardInterrupt:
        print("\\n🛑 Dashboard interrotta")
    
    return True

def add_bot(pair: str, budget: float, target: float = 2.0):
    """Aggiunge un bot"""
    print(f"🤖 Aggiunta bot {pair} con budget {budget} USDT...")
    
    try:
        subprocess.run([
            sys.executable, "session_manager.py", "add-bot", 
            pair, "--budget", str(budget), "--target", str(target)
        ], check=True)
        print(f"✅ Bot {pair} aggiunto con successo")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Errore aggiunta bot: {e}")
        return False

def remove_bot(pair: str):
    """Rimuove un bot"""
    print(f"🛑 Rimozione bot {pair}...")
    
    try:
        subprocess.run([
            sys.executable, "session_manager.py", "remove-bot", pair
        ], check=True)
        print(f"✅ Bot {pair} rimosso con successo")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Errore rimozione bot: {e}")
        return False

def show_status():
    """Mostra status del sistema"""
    print("📊 Status Sistema...")
    
    try:
        subprocess.run([sys.executable, "session_manager.py", "status"], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Errore recupero status: {e}")
        return False

def interactive_menu():
    """Menu interattivo"""
    print_banner()
    
    if not check_dependencies():
        return
    
    while True:
        print("\\n" + "="*50)
        print("🎮 MULTI-BOT SESSION MANAGER - MENU PRINCIPALE")
        print("="*50)
        print("1. 🚀 Avvia Session Manager")
        print("2. 📊 Dashboard Aggregata")
        print("3. 🤖 Aggiungi Bot")
        print("4. 🛑 Rimuovi Bot")
        print("5. 📈 Status Sistema")
        print("6. 📚 Guida Rapida")
        print("7. 🧪 Test Sistema")
        print("8. ❌ Esci")
        
        try:
            choice = input("\\n➤ Scegli opzione (1-8): ").strip()
            
            if choice == '1':
                start_session_manager()
                
            elif choice == '2':
                start_dashboard()
                
            elif choice == '3':
                pair = input("📈 Coppia (es: BTC_USDT): ").strip().upper()
                if not pair:
                    print("❌ Coppia non valida")
                    continue
                    
                try:
                    budget = float(input("💰 Budget USDT: "))
                    target = float(input("🎯 Target % (default 2.0): ") or "2.0")
                except ValueError:
                    print("❌ Valori non validi")
                    continue
                    
                add_bot(pair, budget, target)
                
            elif choice == '4':
                pair = input("📈 Coppia da rimuovere: ").strip().upper()
                if not pair:
                    print("❌ Coppia non valida")
                    continue
                remove_bot(pair)
                
            elif choice == '5':
                show_status()
                
            elif choice == '6':
                show_quick_guide()
                
            elif choice == '7':
                run_system_test()
                
            elif choice == '8':
                print("👋 Arrivederci!")
                break
                
            else:
                print("❌ Opzione non valida")
                
        except KeyboardInterrupt:
            print("\\n👋 Uscita dal menu")
            break
        except EOFError:
            print("\\n👋 Uscita dal menu")
            break

def show_quick_guide():
    """Mostra guida rapida"""
    guide = """
📚 GUIDA RAPIDA MULTI-BOT SESSION MANAGER
==========================================

🚀 PRIMO AVVIO:
1. Configura credenziali Gate.io nel file .env:
   GATE_API_KEY=your_api_key
   GATE_SECRET_KEY=your_secret_key

2. Avvia Session Manager:
   python multi_bot.py start

3. In un altro terminale, apri Dashboard:
   python multi_bot.py dashboard

🤖 GESTIONE BOT:
- Aggiungi bot: Specifica coppia e budget
- Il sistema alloca automaticamente il budget
- Ogni bot opera indipendentemente
- Dashboard mostra status aggregato

💰 BUDGET:
- Budget totale viene letto da Gate.io
- Allocazione automatica evita conflitti
- Monitoraggio real-time disponibilità

📊 MONITORAGGIO:
- Dashboard aggregata per vista globale
- Log individuali per ogni bot
- Statistiche performance in tempo reale

⚠️ RACCOMANDAZIONI:
- Inizia con budget piccoli per test
- Monitora performance regolarmente
- Mantieni sempre margine di sicurezza
- Non allocare tutto il budget disponibile

🛑 EMERGENZA:
- Ctrl+C ferma il Session Manager
- Dashboard può essere chiusa indipendentemente
- Bot si fermano automaticamente al logout
    """
    print(guide)
    input("\\nPremi INVIO per continuare...")

def run_system_test():
    """Esegue test del sistema"""
    print("🧪 Avvio test sistema...")
    
    try:
        subprocess.run([sys.executable, "test_session_manager.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Test falliti: {e}")
    except KeyboardInterrupt:
        print("\\n🛑 Test interrotti")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Multi-Bot Session Manager")
    subparsers = parser.add_subparsers(dest='command', help='Comandi disponibili')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Avvia session manager')
    
    # Dashboard command
    dashboard_parser = subparsers.add_parser('dashboard', help='Avvia dashboard aggregata')
    
    # Add bot command
    add_parser = subparsers.add_parser('add', help='Aggiungi bot')
    add_parser.add_argument('pair', help='Coppia trading (es: BTC_USDT)')
    add_parser.add_argument('budget', type=float, help='Budget USDT')
    add_parser.add_argument('--target', type=float, default=2.0, help='Target % profit')
    
    # Remove bot command
    remove_parser = subparsers.add_parser('remove', help='Rimuovi bot')
    remove_parser.add_argument('pair', help='Coppia trading')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Mostra status')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test sistema')
    
    # Guide command
    guide_parser = subparsers.add_parser('guide', help='Guida rapida')
    
    args = parser.parse_args()
    
    if not args.command:
        # Menu interattivo
        interactive_menu()
        return
    
    # Controlla dipendenze per tutti i comandi tranne test e guide
    if args.command not in ['test', 'guide']:
        if not check_dependencies():
            sys.exit(1)
    
    # Esegui comando
    if args.command == 'start':
        start_session_manager()
        
    elif args.command == 'dashboard':
        start_dashboard()
        
    elif args.command == 'add':
        add_bot(args.pair, args.budget, args.target)
        
    elif args.command == 'remove':
        remove_bot(args.pair)
        
    elif args.command == 'status':
        show_status()
        
    elif args.command == 'test':
        run_system_test()
        
    elif args.command == 'guide':
        show_quick_guide()

if __name__ == "__main__":
    main()