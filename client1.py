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
                log_message = f"{message.strip()}"
                writer.write(message.encode())
                await writer.drain()
                self.request_counter += 1
                logging.info(log_message)
                await asyncio.sleep(random.randint(300, 3000) / 1000)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.info(f"Клиент {self.client_id}. Ошибка при отправке сообщения: {e}")
                break

    async def run(self):
        writer = None
        try:
            reader, writer = await asyncio.open_connection(self.host, self.port)
            send_ping_task = asyncio.create_task(self.send_ping(writer))
            await asyncio.sleep(20)
            send_ping_task.cancel()
            await send_ping_task
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

    client = TCPClient('localhost', 8888, 1)
    asyncio.run(client.run())
