import asyncio
import datetime
import random


class TCPClient:
    def __init__(self, host, port, client_id):
        self.host = host
        self.port = port
        self.client_id = client_id
        self.request_counter = 0

    async def send_ping(self, writer):
        while True:
            message = f"[{self.request_counter}] PING\n"
            now = datetime.datetime.now()
            log_message = f"{now.strftime('%Y-%m-%d;%H:%M:%S.%f')[:-3]};{message}"
            writer.write(message.encode())
            await writer.drain()
            self.request_counter += 1
            # Запись в лог отправки
            print(f"Client {self.client_id} sent: {log_message}")  # Замените печать на запись в файл лога
            await asyncio.sleep(random.randint(300, 3000) / 1000)

    async def receive_pong(self, reader):
        while True:
            data = await reader.readline()
            if data:
                message = data.decode().strip()
                now = datetime.datetime.now()
                log_message = f"{now.strftime('%Y-%m-%d;%H:%M:%S.%f')[:-3]};;{message}"
                # Запись в лог получения
                print(f"Client {self.client_id} received: {log_message}")  # Замените печать на запись в файл лога

    async def run(self):
        reader, writer = await asyncio.open_connection(self.host, self.port)
        task1 = asyncio.create_task(self.send_ping(writer))
        task2 = asyncio.create_task(self.receive_pong(reader))
        await asyncio.gather(task1, task2)


if __name__ == "__main__":
    client = TCPClient(host='127.0.0.1', port=8888, client_id=1)
    asyncio.run(client.run())
