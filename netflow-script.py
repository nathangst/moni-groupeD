import subprocess
import csv
import sqlite3
from io import StringIO
from datetime import datetime
import os.path
import time
import requests


TIMESTAMPS_CSV_FILE = "timestamps.csv"


def create_database():
    conn = sqlite3.connect('ips.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS ips (ip TEXT PRIMARY KEY)''')
    conn.commit()
    conn.close()


def add_ip_to_database(ip):
    conn = sqlite3.connect('ips.db')
    c = conn.cursor()
    c.execute('''INSERT OR IGNORE INTO ips VALUES (?)''', (ip,))
    conn.commit()
    conn.close()


def save_timestamp(timestamp):
    with open(TIMESTAMPS_CSV_FILE, "a") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp])
        print("Timestamp ajouté :", timestamp)


def check_ip_in_db(ip):
    conn = sqlite3.connect('ips.db')
    c = conn.cursor()
    c.execute('''SELECT COUNT(*) FROM ips WHERE ip = ?''', (ip,))
    count = c.fetchone()[0]
    conn.close()
    return count > 0


def extract_ips_from_string(csv_string, compteur):
    ips = set()
    reader = csv.reader(StringIO(csv_string))
    next(reader)
    
    for row in reader:
        if "Summary" in row:  
            return ips, compteur
            
        if row:  
            if len(row) >= 5:
                ip = row[3] 
                ips.add(ip)
                
                if not check_ip_in_db(ip):
                    save_timestamp(row[0])
                    compteur += 1
                
                add_ip_to_database(ip)
                
    return ips, compteur


def run_nfdump(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    
    if process.returncode != 0:
        print(f"Erreur lors de l'exécution de la commande: {error.decode()}")
        return None
    else:
        return output.decode()
        

def webhook_alert(cpteur):
    message = f"{datetime.now()} - Une alerte DDoS est détectée - {cpteur} nouvelles IP détectées"
    WEBHOOK_URL = "https://discord.com/api/webhooks/1221823200103759932/eGpzOaipTRTNTM5kI1z-ZfkjGwM1f37excK-zXwoBIPQoooJWn-N7yARbqEBaELOke7p"

    data = {"content": message.strip()}
    response = requests.post(WEBHOOK_URL, json=data)
    if response.status_code != 204:
        print(f"Failed to send message to Discord: {response.status_code}, {response.text}", file=sys.stderr)
        

def main(cpteur):
    create_database()
    
    command = "nfdump -r /var/cache/nfdump -A srcip -o csv"
    netflow_data = run_nfdump(command)
    
    if netflow_data:
        print(netflow_data)
    
        ips, compteur = extract_ips_from_string(netflow_data, cpteur)
    
    return compteur


if __name__ == "__main__":
    while True:
        cpteur = 0
        
        cpteur = main(cpteur)
        
        if cpteur > 1000:
            webhook_alert(cpteur)
        time.sleep(30)
