# AES-Text-Encryptor

## Cloudflare Tunnel

This project can be exposed through Cloudflare Tunnel so your mobile app can use a stable public URL without changing the websocket server.

### Server target

The websocket server listens on `localhost:8765`.

### Starter config

Edit [cloudflared/config.yml](cloudflared/config.yml) and replace:

- `YOUR_TUNNEL_UUID` with your Cloudflare tunnel ID
- `YOUR_WINDOWS_USER` with your Windows username
- `chat.example.com` with the hostname you route in Cloudflare

### Basic flow

1. Install `cloudflared`.
2. Create a tunnel in Cloudflare.
3. Point the tunnel to `http://localhost:8765`.
4. Run the websocket server.
5. Start the tunnel with the config file.

### Example command

```bash
cloudflared tunnel run YOUR_TUNNEL_NAME
```
