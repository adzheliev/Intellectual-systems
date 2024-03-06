import asyncio
import datetime
import random
import logging


class TCPServer:
    """
    A simple TCP server that echoes back any incoming data.

    Attributes:
        host (str): The hostname or IP address to bind to.
        port (int): The port to listen on.
        client_counter (int): A counter for tracking the number of connected clients.
        message_counter (int): A counter for tracking the number of messages sent.
        clients (dict): A dictionary of connected clients, keyed by their client ID.
    """

    def __init__(self, host, port):
        """
        Initialize a new TCP server.

        Args:
            host (str): The hostname or IP address to bind to.
            port (int): The port to listen on.
        """
        self.host = host
        self.port = port
        self.client_counter = 0
        self.message_counter = 0
        self.clients = {}

    async def handle_client(self, reader, writer):
        """
        A coroutine that handles incoming connections from clients.

        Args:
            reader (StreamReader): A asyncio stream reader for reading incoming data.
            writer (StreamWriter): A asyncio stream writer for writing outgoing data.
        """
        client_id = self.client_counter = self.client_counter + 1
        self.clients[client_id] = writer
        try:
            while True:
                data = await reader.readline()
                request_time = datetime.datetime.now()
                if data:
                    message = data.decode()
                    if random.random() < 0.1:
                        log_message = (
                            f"{request_time.strftime('%Y-%m-%d;%H:%M:%S.%f')[:-3]};"
                            f"{message.rstrip()};(проигнорировано)"
                        )
                    else:
                        await asyncio.sleep(random.randint(100, 1000) / 1000)
                        response = (
                            f"[{self.message_counter}]/"
                            f"{message.split()[0]} "
                            f"PONG ({client_id})\n"
                        )
                        response_time = datetime.datetime.now()
                        writer.write(response.encode())
                        await writer.drain()
                        self.message_counter += 1
                        log_message = (
                            f"{request_time.strftime('%Y-%m-%d;%H:%M:%S.%f')[:-3]};"
                            f"{message.rstrip()};"
                            f"{response_time.strftime('%H:%M:%S.%f')[:-3]};"
                            f"{response.rstrip()}"
                        )
                    logging.info(log_message)
                    file_logger.info(log_message)
                else:
                    break
        except Exception as e:
            logging.error(f"Ошибка при обработке клиента {client_id}: {e}")
        finally:
            if client_id in self.clients:
                del self.clients[client_id]
                logging.info(f"Соединение с клиентом {client_id} закрыто.")
            writer.close()
            await writer.wait_closed()

    async def send_keepalive(self):
        """
        A coroutine that sends a keepalive message to all connected clients every 5 seconds.
        """
        while True:
            await asyncio.sleep(5)
            message = f"[{self.message_counter}] keepalive\n"
            for writer in self.clients.values():
                try:
                    writer.write(message.encode())
                    await writer.drain()
                except Exception as e:
                    logging.error(f"Ошибка отправки keepalive: {e}")
            self.message_counter += 1

    async def run(self):
        """
        A coroutine that starts the server and waits for incoming connections.
        """
        server = await asyncio.start_server(
            self.handle_client,
            self.host,
            self.port
        )
        server_task = asyncio.create_task(server.serve_forever())
        keepalive_task = asyncio.create_task(self.send_keepalive())
        try:
            await asyncio.sleep(300)
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
            logging.info("Время работы сервера истекло.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    file_logger = logging.getLogger('fileLogger')
    file_logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler('logs/server.log')
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(message)s')
    file_handler.setFormatter(file_formatter)
    file_logger.addHandler(file_handler)
    file_logger.propagate = False

    server = TCPServer(
        '0.0.0.0',
        8888
    )
    asyncio.run(server.run())
