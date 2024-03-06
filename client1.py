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
        self.send_time = None
        self.message = None

    async def send_ping(self, writer):
        while True:
            try:
                self.message = f"[{self.request_counter}] PING\n"
                self.send_time = datetime.datetime.now()
                writer.write(self.message.encode())
                await writer.drain()
                self.request_counter += 1
                await asyncio.sleep(random.randint(300, 3000) / 1000)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.info(f"Клиент {self.client_id}. Ошибка при отправке сообщения: {e}")
                break

    async def handle_response(self, reader):
        while True:
            response = await reader.readline()
            response_time = datetime.datetime.now()
            if response:
                response_message = response.decode().strip()
                if "keepalive" in response_message:
                    log_message = f"{datetime.datetime.now().strftime('%Y-%m-%d')};{response_time.strftime('%H:%M:%S.%f')};(keepalive)"
                else:
                    log_message = f"{self.send_time.strftime('%Y-%m-%d;%H:%M:%S.%f')};{self.message.rstrip()};{response_time.strftime('%H:%M:%S.%f')};{response_message}"
            else:
                break

            logging.info(log_message)
            file_logger.info(log_message)

    async def run(self):
        writer = None
        try:
            reader, writer = await asyncio.open_connection(self.host, self.port)
            send_ping_task = asyncio.create_task(self.send_ping(writer))
            receive_task = asyncio.create_task(self.handle_response(reader))
            await asyncio.sleep(300)
            send_ping_task.cancel()
            receive_task.cancel()
            await asyncio.gather(send_ping_task, receive_task)
        except Exception as e:
            logging.error(f"Клиент {self.client_id} ошибка: {e}")
        finally:
            if writer and not writer.is_closing():
                writer.close()
            if writer:
                try:
                    await writer.wait_closed()
                except Exception as e:
                    logging.info(f"Клиент {self.client_id}. Ошибка при закрытии соединения: {e}")
            logging.info(f"Клиент {self.client_id} завершил работу.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    file_logger = logging.getLogger('fileLogger')
    file_logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler('logs/client1.log')
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(message)s')
    file_handler.setFormatter(file_formatter)
    file_logger.addHandler(file_handler)
    file_logger.propagate = False

    client = TCPClient('server', 8888, 1)
    asyncio.run(client.run())
