import os
import requests
import json
import redis
import toml
import docker

API_KEY = os.getenv("API_KEY")
DOWNLOAD_URL = os.getenv("DOWNLOAD_URL")
TEMP_FILE = os.getenv("TEMP_FILE")
IPSET_NAME = os.getenv("IPSET_NAME")
DYNAMIC_CONF_PATH = os.getenv("DYNAMIC_CONF_PATH")

# Configuration de Redis
redis_host = "redis"
redis_port = 6379
redis_db = 0

def download_blacklist(api_key, url, file_path):
    headers = {
        'Accept': 'application/json',
        'Key': api_key,
    }
    params = {
        'maxAgeInDays': 90
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        with open(file_path, 'w') as file:
            file.write(response.text)
        return True
    else:
        print("Erreur lors du téléchargement de la liste des IPs.")
        return False

def extract_ips(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return [entry['ipAddress'] for entry in data['data']]

def update_redis(ip_list):
    r = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
    new_ips = []
    for ip in ip_list:
        if not r.sismember(IPSET_NAME, ip):
            r.sadd(IPSET_NAME, ip)
            new_ips.append(ip)
    return new_ips

def update_dynamic_conf(ip_list, conf_path):
    config = {
        'http': {
            'middlewares': {
                'ipblacklist': {
                    'ipWhiteList': {
                        'sourceRange': ip_list,
                        'ipStrategy': {
                            'depth': 0,
                            'excludedIPs': []
                        }
                    }
                }
            }
        }
    }
    with open(conf_path, 'w') as file:
        toml.dump(config, file)

def restart_traefik():
    client = docker.from_env()
    traefik_container = client.containers.get('traefik')
    traefik_container.restart()

def main():
    if download_blacklist(API_KEY, DOWNLOAD_URL, TEMP_FILE):
        ip_list = extract_ips(TEMP_FILE)
        new_ips = update_redis(ip_list)
        print(f"{len(new_ips)} nouvelles adresses IP ajoutées à la liste noire.")
        r = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
        all_ips = list(r.smembers(IPSET_NAME))
        update_dynamic_conf(all_ips, DYNAMIC_CONF_PATH)
        print("Configuration dynamique mise à jour.")
        restart_traefik()

if __name__ == "__main__":
    main()
