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
                request_time = datetime.datetime.now()
                if data:
                    message = data.decode()
                    if random.random() < 0.1:
                        log_message = f"{request_time.strftime('%Y-%m-%d;%H:%M:%S.%f')[:-3]};{message.rstrip()};(проигнорировано)"
                    else:
                        await asyncio.sleep(random.randint(100, 1000) / 1000)
                        response = f"[{self.message_counter}]/{message.split()[0]} PONG ({client_id})\n"
                        response_time = datetime.datetime.now()
                        writer.write(response.encode())
                        await writer.drain()
                        self.message_counter += 1
                        log_message = f"{request_time.strftime('%Y-%m-%d;%H:%M:%S.%f')[:-3]};{message.rstrip()};{response_time.strftime('%H:%M:%S.%f')[:-3]};{response.rstrip()}"
                    logging.info(log_message)
                    file_logger.info(log_message)
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
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
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

    server = TCPServer('0.0.0.0', 8888)
    asyncio.run(server.run())
