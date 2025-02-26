# WebSocket Stress Testing Tool

A generic tool for stress testing WebSocket endpoints by sending regular and burst updates with customizable data templates.

## Requirements

```
pip install websocket-client requests PySocks
```

## Usage

Basic usage with default data template:
```
python websocket_stress_test.py --endpoint wss://your-target-endpoint.com/socket
```

### Custom Data Template

Create a JSON file with your data structure:
```json
{
  "type": "message",
  "id": "user123",
  "content": "hello",
  "timestamp": 1234567890
}
```

Use it with the script:
```
python websocket_stress_test.py --endpoint wss://your-target-endpoint.com/socket --template your_template.json --id-field id
```

The script will:
1. Keep the structure of your template
2. Replace values with random data of the same type
3. Use the specified ID field for sequential IDs
4. Add a timestamp if not present

### Proxy Configuration

Configure a local proxy (e.g., Shadowsocks):
```
python websocket_stress_test.py --endpoint wss://your-target-endpoint.com/socket --proxy-type socks5 --proxy-addr 127.0.0.1 --proxy-port 1080
```

### SSL Configuration

For SSL certificate issues, you should use a proper certificate file. You can download Mozilla's trusted certificate bundle:

1. Download from: https://curl.se/ca/cacert.pem
2. Use it with the script:
```
python websocket_stress_test.py --endpoint wss://your-target-endpoint.com/socket --cert-file cacert.pem
```

Note: While `--skip-ssl-verify` is available for testing purposes, it's not recommended for production use as it bypasses security checks.

### All Options

```
  --endpoint ENDPOINT     WebSocket endpoint URL (wss://example.com/socket)
  --template TEMPLATE     JSON template file for data structure
  --id-field ID_FIELD    Field name to use for ID in the data template
  --proxy-type PROXY_TYPE Proxy type (socks5, socks4, http)
  --proxy-addr PROXY_ADDR Proxy address
  --proxy-port PROXY_PORT Proxy port
  --frequency FREQUENCY   Updates per second (default: 10.0)
  --burst-delay DELAY    Delay before burst in seconds (default: 5)
  --burst-items ITEMS    Number of items in burst (default: 100)
  --burst-size SIZE      Number of bursts (default: 50)
  --cert-file CERT_FILE  SSL certificate file path
  --debug                Enable debug output
  --skip-ssl-verify      Skip SSL certificate verification (not recommended)
```

## Performance Settings

- `--frequency`: Controls how many updates are sent per second during regular operation
- `--burst-delay`: Time to wait before starting burst mode
- `--burst-items`: Number of items to update in each burst
- `--burst-size`: Number of bursts to perform

Example with custom performance settings:
```
python websocket_stress_test.py --endpoint wss://your-target-endpoint.com/socket --frequency 20 --burst-delay 10 --burst-items 200 --burst-size 100
```