import asyncio
import datetime
import random


class TCPServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_counter = 0
        self.message_counter = 0
        self.clients = {}  # client_id: transport

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
                    print(log_message)  # Вместо печати, записываем в файл
                else:
                    break
        finally:
            writer.close()
            del self.clients[client_id]

    async def send_keepalive(self):
        while True:
            await asyncio.sleep(5)
            for client_id, writer in self.clients.items():
                response = f"[{self.message_counter}] keepalive\n"
                writer.write(response.encode())
                await writer.drain()
                self.message_counter += 1

    async def run(self):
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        async with server:
            await asyncio.gather(server.serve_forever(), self.send_keepalive())


if __name__ == "__main__":
    server = TCPServer(host='127.0.0.1', port=8888)
    asyncio.run(server.run())
