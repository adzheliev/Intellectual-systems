import asyncio
import datetime
import random
import logging



class TCPClient:
    def __init__(self, host, port, client_id):
        self.host = host
        self.port = port
        self.client_id = client_id
        self.request_counter = 0


    async def send_ping(self, writer):
        while True:
            try:
                message = f"[{self.request_counter}] PING\n"
                now = datetime.datetime.now()
                log_message = f"Client {self.client_id} sent: {message.strip()}"
                writer.write(message.encode())
                await writer.drain()
                self.request_counter += 1
                logging.info(log_message)
                await asyncio.sleep(random.randint(300, 3000) / 1000)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.info(f"Client {self.client_id} encountered an error while sending ping: {e}")
                break

    async def receive_pong(self, reader):
        while True:
            data = await reader.readline()
            if data:
                message = data.decode().strip()
                log_message = f"Client {self.client_id} received: {message}"
                logging.info(log_message)

    async def run(self):
        writer = None
        try:
            reader, writer = await asyncio.open_connection(self.host, self.port)
            send_ping_task = asyncio.create_task(self.send_ping(writer))
            await asyncio.sleep(20)  # Operational period
            send_ping_task.cancel()
            await send_ping_task
        except Exception as e:
            logging.error(f"Client {self.client_id} error: {e}")
        finally:
            if writer and not writer.is_closing():
                writer.close()
            if writer:
                try:
                    await writer.wait_closed()
                except Exception as e:
                    logging.info(f"Client {self.client_id} closing connection encountered an error: {e}")
            logging.info(f"Client {self.client_id} exited cleanly.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    client = TCPClient('localhost', 8888, 2)
    asyncio.run(client.run())
