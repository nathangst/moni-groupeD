from pysnmp.hlapi import *
import time
import csv
import os
import requests

# Fonction pour envoyer le message Discord via webhook en cas d'erreur
def send_discord_webhook(message):
    webhook_url = 'https://discord.com/api/webhooks/1229728556293161031/sA6_mvfJr76zPdTnjSDDAKk-ewn4ZLv8ounYFpEc1m-6COfNJymrafloxrQGBK9SfjBY'
    data = {'content': message}
    response = requests.post(webhook_url, json=data)
    if response.status_code != 204:
        print(f"Failed to send Discord webhook. Status code: {response.status_code}")

def get_snmp_data(oid, host='192.168.128.24', community='HELMpAllUser9465CmA'):
    iterator = getCmd(
        SnmpEngine(),
        CommunityData(community),
        UdpTransportTarget((host, 161)),
        ContextData(),
        ObjectType(ObjectIdentity(oid))
    )

    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

    if errorIndication:
        send_discord_webhook(f"SNMP Error: {errorIndication}")
        print(errorIndication)
    elif errorStatus:
        error_msg = '%s at %s' % (
            errorStatus.prettyPrint(),
            errorIndex and varBinds[int(errorIndex) - 1][0] or '?'
        )
        send_discord_webhook(f"SNMP Error: {error_msg}")
        print(error_msg)
    else:
        for varBind in varBinds:
            value = varBind[1]
            return value

def write_to_csv(data, filename, headers):
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)

        # Écrire les en-têtes si le fichier est vide
        if os.path.getsize(filename) == 0:
            writer.writerow(headers)

        for row in data:
            writer.writerow(row)

def main():

    csv_filename = '/home/helmo/travail/data/data.csv'
    csv_headers = ['Time', 'CPU Load', 'RAM Load', 'Disk Used', 'Interface', 'In', 'Out']

    while True:
        try:
            cpu_load_oid = '.1.3.6.1.4.1.2021.10.1.3.1'
            cpu_load = get_snmp_data(cpu_load_oid)

            ram_used_oid = '1.3.6.1.4.1.2021.4.6.0'
            ram_total_oid = '1.3.6.1.4.1.2021.4.5.0'
            ram_used = get_snmp_data(ram_used_oid)
            ram_total = get_snmp_data(ram_total_oid)
            ram_load = float((ram_used / ram_total) * 100)

            disk_left_oid = '1.3.6.1.4.1.2021.9.1.7.1'
            disk_left = float((get_snmp_data(disk_left_oid) / 1024) / 1024)

            oid_if = '1.3.6.1.2.1.2.2.1'
            oid_if_int = ['2', '3']
            dico_if = []

            for i in range(len(oid_if_int)):
                name_if = get_snmp_data(oid_if + '.2.' + oid_if_int[i])
                in_oct_if = get_snmp_data(oid_if + '.10.' + oid_if_int[i])
                out_oct_if = get_snmp_data(oid_if + '.16.' + oid_if_int[i])

                in_mo = in_oct_if / (1024**2)
                out_mo = out_oct_if / (1024**2)

                dico_if.append({
                    'interface': str(name_if),
                    'in': float(in_mo),
                    'out': float(out_mo),
                })

            current_time = time.strftime('%Y-%m-%d %H:%M:%S')
            csv_data = [[current_time, cpu_load, ram_load, disk_left] + list(item.values()) for item in dico_if]

            write_to_csv(csv_data, csv_filename, csv_headers)
            print("écriture")

            time.sleep(300)

        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            send_discord_webhook(error_msg)
            print(error_msg)

main()
