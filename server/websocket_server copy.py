# # type: ignore
# import asyncio
# import logging
# import signal
# from datetime import datetime
# from typing import Optional
# import random

# import websockets
# from rich.live import Live
# from rich.panel import Panel
# from rich.text import Text

# from crypto.encrypt import encrypt
# from crypto.decrypt import decrypt

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)

# # Configuration
# CONFIG = {
#     "host": "0.0.0.0",
#     "port": 8765,
#     "ping_interval": 20,
#     "max_size": 10_000,  # max message size in bytes
#     "streaming_delay": 0.02,  # delay between character streaming
# }

# bars = "▁▂▃▄▅▆▇"
# global_history = []
# current_client = None  # Track current client for UI display


# class ClientHandler:
#     """Handle per-client state to avoid conflicts with multiple clients"""
    
#     def __init__(self, client_id: str):
#         self.client_id = client_id
#         self.status = "Idle"
#         self.encrypted_chars = []
#         self.decrypted_chars = []
#         self.encrypted_text = ""
#         self.decrypted_text = ""
    
#     def get_encrypted(self) -> str:
#         return "".join(self.encrypted_chars)
    
#     def get_decrypted(self) -> str:
#         return "".join(self.decrypted_chars)
    
#     def reset(self):
#         """Reset buffers for new message"""
#         self.encrypted_chars = []
#         self.decrypted_chars = []
#         self.encrypted_text = ""
#         self.decrypted_text = ""


# async def handler(websocket):
#     """Handle individual client connections"""
#     global current_client
    
#     client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
#     client = ClientHandler(client_id)
#     current_client = client  # Set as current client for UI display
    
#     logger.info(f"Client connected: {client_id}")
    
#     try:
#         async for message in websocket:
#             # Validate message
#             if not message or not isinstance(message, str):
#                 logger.warning(f"Invalid message from {client_id}: {message}")
#                 await websocket.send("Error: Invalid message format")
#                 continue
            
#             if len(message) > CONFIG["max_size"]:
#                 logger.warning(f"Message too large from {client_id}: {len(message)} bytes")
#                 await websocket.send(f"Error: Message exceeds {CONFIG['max_size']} bytes")
#                 continue
            
#             logger.debug(f"Received message from {client_id}: {len(message)} chars")
            
#             client.status = "Encrypting"
#             client.encrypted_text = ""
#             client.decrypted_text = ""
#             client.encrypted_chars = []
#             client.decrypted_chars = []
            
#             try:
#                 # Encrypt message
#                 result = encrypt(message)
                
#                 # Stream encrypted characters (faster using list + join)
#                 for char in result:
#                     client.encrypted_chars.append(char)
#                     await asyncio.sleep(CONFIG["streaming_delay"])
                
#                 client.encrypted_text = client.get_encrypted()
#                 client.status = "Decrypting"
                
#                 # Decrypt and stream
#                 original = decrypt(result)
#                 for char in original:
#                     client.decrypted_chars.append(char)
#                     await asyncio.sleep(CONFIG["streaming_delay"])
                
#                 client.decrypted_text = client.get_decrypted()
                
#                 # Send encrypted result to client
#                 await websocket.send(result)
#                 logger.info(f"Processed message from {client_id}: sent encrypted result")
                
#                 # Add to global history
#                 global_history.append((result, datetime.now().strftime("%H:%M:%S"), client_id))
#                 if len(global_history) > 10:
#                     global_history.pop(0)
                
#                 client.status = "Idle"
                
#             except Exception as e:
#                 logger.exception(f"Error processing message from {client_id}: {e}")
#                 client.status = "Error"
#                 await websocket.send(f"Error: {str(e)}")
    
#     except asyncio.TimeoutError:
#         logger.error(f"Timeout from {client_id}")
#         client.status = "Timeout"
#     except websockets.exceptions.ConnectionClosed:
#         logger.info(f"Connection closed from {client_id}")
#     except Exception as e:
#         logger.exception(f"Unexpected error from {client_id}: {e}")
#     finally:
#         logger.info(f"Client disconnected: {client_id}")


# def generate_wave() -> str:
#     """Generate animation wave"""
#     return "".join(random.choice(bars) for _ in range(30))


# async def ui_loop():
#     """Display real-time UI with client status and history"""
#     with Live(refresh_per_second=10) as live:
#         while True:
#             try:
#                 wave = generate_wave() if current_client and current_client.status != "Idle" else ""
                
#                 content = Text()
#                 content.append("=== AES FILE ENCRYPTOR SERVER ===\n", style="bold cyan")
#                 content.append(f"Server: {CONFIG['host']}:{CONFIG['port']}\n\n", style="bold white")
                
#                 if current_client:
#                     content.append(f"Status: {current_client.status}\n\n", style="bold green")
#                     content.append(wave + "\n\n", style="cyan")
#                     content.append("Encrypted:\n", style="bold yellow")
#                     content.append(current_client.encrypted_text, style="yellow")
#                     content.append("\n\nDecrypted:\n", style="bold green")
#                     content.append(current_client.decrypted_text, style="green")
#                 else:
#                     content.append("Status: Idle\n\n", style="bold green")
#                     content.append("Waiting for client connection...\n\n", style="dim white")
                
#                 # Display history
#                 content.append("\nHistory:\n", style="bold magenta")
#                 if global_history:
#                     for item, timestamp, client_id in global_history[-5:]:
#                         content.append(f"[{timestamp}] {client_id}\n", style="magenta")
#                         preview = item[:50] + ('...' if len(item) > 50 else '')
#                         content.append(f"  → {preview}\n", style="dim magenta")
#                 else:
#                     content.append("No activity yet\n", style="dim white")
                
#                 live.update(Panel(content, title="🔐 Encrypt CLI", border_style="cyan"))
                
#                 await asyncio.sleep(0.1)
#             except Exception as e:
#                 logger.exception(f"Error in UI loop: {e}")
#                 await asyncio.sleep(0.1)


# async def main():
#     """Main server function with graceful shutdown"""
#     logger.info(f"Starting server on {CONFIG['host']}:{CONFIG['port']}")
    
#     try:
#         async with websockets.serve(
#             handler,
#             CONFIG["host"],
#             CONFIG["port"],
#             ping_interval=CONFIG["ping_interval"],
#             max_size=CONFIG["max_size"],
#         ) as server:
#             logger.info("✅ Server started successfully")
            
#             # Run server and UI loop concurrently
#             await asyncio.gather(
#                 asyncio.Future(),  # Run forever
#                 ui_loop()
#             )
    
#     except Exception as e:
#         logger.exception(f"Failed to start server: {e}")
#         raise


# def handle_shutdown(signum, frame):
#     """Handle graceful shutdown on SIGINT/SIGTERM"""
#     logger.info("Shutdown signal received, cleaning up...")
#     raise KeyboardInterrupt()


# if __name__ == "__main__":
#     # Register signal handlers for graceful shutdown
#     signal.signal(signal.SIGINT, handle_shutdown)
    
#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         logger.info("Server stopped")
#     except Exception as e:
#         logger.exception(f"Server error: {e}")
