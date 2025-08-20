
import os
from datetime import datetime
import glob

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")

def analyze_logs(date_filter=None):
    """
    Analizza i log in LOG_DIR.
    - date_filter: stringa 'YYYY-MM-DD' per filtrare un giorno specifico, oppure None per tutti
    """
    if not os.path.exists(LOG_DIR):
        print(f"Nessuna cartella log trovata in {LOG_DIR}")
        return

    files = []
    if date_filter:
        pattern = os.path.join(LOG_DIR, f"trades_{date_filter}.log")
        files = glob.glob(pattern)
    else:
        files = glob.glob(os.path.join(LOG_DIR, "trades_*.log"))

    if not files:
        print("Nessun file di log trovato per il filtro richiesto.")
        return

    total_trades = 0
    buy_count = 0
    sell_count = 0
    cancel_count = 0
    total_profit = 0.0
    daily_profit = {}

    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            for line in f:
                total_trades += 1
                if "| BUY |" in line:
                    buy_count += 1
                elif "| SELL |" in line:
                    sell_count += 1
                    # estrai profitto se presente
                    parts = line.strip().split('|')
                    for p in parts:
                        if 'profit=' in p:
                            try:
                                profit_str = p.split('profit=')[1].strip().split(' ')[0]
                                profit_val = float(profit_str)
                                total_profit += profit_val
                                day = file.split('trades_')[-1].replace('.log','')
                                daily_profit[day] = daily_profit.get(day, 0.0) + profit_val
                            except:
                                pass
                elif "| CANCEL |" in line:
                    cancel_count += 1

    success_rate = (sell_count / buy_count * 100) if buy_count > 0 else 0

    print("===== ANALISI LOG =====")
    print(f"File analizzati: {len(files)}")
    print(f"Trade totali: {total_trades}")
    print(f"BUY: {buy_count} | SELL: {sell_count} | CANCEL: {cancel_count}")
    print(f"Profitto totale: {total_profit:.8f} USDT")
    print(f"Profitto medio per SELL: {(total_profit/sell_count):.8f} USDT" if sell_count > 0 else "Profitto medio per SELL: N/A")
    print(f"Tasso di successo: {success_rate:.2f}%")
    if daily_profit:
        best_day = max(daily_profit, key=daily_profit.get)
        print(f"Giorno più profittevole: {best_day} con {daily_profit[best_day]:.8f} USDT")
    print("========================")

if __name__ == "__main__":
    # Esempio: analizza tutti i log
    analyze_logs()
    # Esempio: analizza un giorno specifico
    # analyze_logs("2025-08-11")
