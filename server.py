import asyncio
import datetime
import random
import logging


class TCPServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_counter = 0
        self.message_counter = 0
        self.clients = {}

    async def handle_client(self, reader, writer):
        client_id = self.client_counter = self.client_counter + 1
        self.clients[client_id] = writer
        try:
            while True:
                data = await reader.readline()
                if data:
                    message = data.decode()
                    now = datetime.datetime.now()
                    log_message = f"{now.strftime('%Y-%m-%d;%H:%M:%S.%f')[:-3]};{message};"
                    if random.random() < 0.1:  # 10% chance to ignore
                        log_message += "(проигнорировано)"
                    else:
                        await asyncio.sleep(random.randint(100, 1000) / 1000)
                        response = f"[{self.message_counter}]{message.split()[0]} PONG ({client_id})\n"
                        writer.write(response.encode())
                        await writer.drain()
                        self.message_counter += 1
                        now = datetime.datetime.now()
                        log_message += f"{now.strftime('%H:%M:%S.%f')[:-3]};{response}"
                    logging.info(log_message)
                else:
                    break
        except Exception as e:
            logging.error(f"Ошибка при обработке клиента {client_id}: {e}")
        finally:
            if client_id in self.clients:  # Проверяем наличие client_id перед удалением
                del self.clients[client_id]
                logging.info(f"Соединение с клиентом {client_id} закрыто.")
            writer.close()
            await writer.wait_closed()

    async def send_keepalive(self):
        while True:
            await asyncio.sleep(5)  # Wait for 5 seconds between keepalive messages
            message = f"[{self.message_counter}] keepalive\n"
            for writer in self.clients.values():
                try:
                    writer.write(message.encode())
                    await writer.drain()
                except Exception as e:
                    logging.error(f"Error sending keepalive: {e}")
            self.message_counter += 1

    async def run(self):
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        server_task = asyncio.create_task(server.serve_forever())
        keepalive_task = asyncio.create_task(self.send_keepalive())
        try:
            await asyncio.sleep(20)  # Run for 5 minutes
        finally:
            keepalive_task.cancel()
            try:
                await keepalive_task
            except asyncio.CancelledError:
                pass
            server_task.cancel()
            writers = list(self.clients.values())
            for writer in writers:
                writer.close()
                await writer.wait_closed()
            server.close()
            await server.wait_closed()
            logging.info("Server shutdown cleanly.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    server = TCPServer('localhost', 8888)
    asyncio.run(server.run())
