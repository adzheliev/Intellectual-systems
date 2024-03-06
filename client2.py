import asyncio
import datetime
import random
import logging
from asyncio import StreamReader, StreamWriter


class TCPClient:
    """
    A simple TCP client that sends periodic pings to a server and logs
    any responses it receives.
    """

    def __init__(self, host: str, port: int, client_id: int) -> None:
        """
        Initialize the client with the specified host, port, and client ID.

        Args:
            host (str): The hostname or IP address of the server.
            port (int): The port number of the server.
            client_id (int): The unique ID of this client.
        """
        self.host: str = host
        self.port: int = port
        self.client_id: int = client_id
        self.request_counter: int = 0
        self.send_time = None
        self.message = None

    async def send_ping(self, writer: StreamWriter) -> None:
        """
        Send a ping to the server and log any responses.

        Args:
            writer (asyncio.StreamWriter): The writer for the active connection
                to the server.
        """
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
                logging.info(
                    f"Client {self.client_id}. "
                    f"Error sending message: {e}"
                )
                break

    async def handle_response(self, reader: StreamReader) -> None:
        """
        Read a response from the server and log it.

        Args:
            reader (asyncio.StreamReader): The reader for the active connection
                to the server.
        """
        while True:
            response = await reader.readline()
            response_time = datetime.datetime.now()
            if response:
                response_message = response.decode().strip()
                if "keepalive" in response_message:
                    log_message = (
                        f"{datetime.datetime.now().strftime('%Y-%m-%d')};"
                        f"{response_time.strftime('%H:%M:%S.%f')};"
                        f"(keepalive)"
                    )
                else:
                    log_message = (
                        f"{self.send_time.strftime('%Y-%m-%d;%H:%M:%S.%f')};"
                        f"{self.message.rstrip()};"
                        f"{response_time.strftime('%H:%M:%S.%f')};"
                        f"{response_message}"
                    )
            else:
                break

            logging.info(log_message)

    async def run(self) -> None:
        """
        Start the client and wait for the specified duration.
        """
        writer = None
        try:
            reader, writer = await asyncio.open_connection(
                self.host,
                self.port
            )
            send_ping_task = asyncio.create_task(self.send_ping(writer))
            receive_task = asyncio.create_task(self.handle_response(reader))
            await asyncio.sleep(300)
            send_ping_task.cancel()
            receive_task.cancel()
            await asyncio.gather(send_ping_task, receive_task)
        except Exception as e:
            logging.error(f"Client {self.client_id} error: {e}")
        finally:
            if writer and not writer.is_closing():
                writer.close()
            if writer:
                try:
                    await writer.wait_closed()
                except Exception as e:
                    logging.info(
                        f"Client {self.client_id}. "
                        f"Error closing connection: {e}"
                    )
            logging.info(f"Client {self.client_id} finished.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    file_logger = logging.getLogger('fileLogger')
    file_logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler('logs/client2.log')
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(message)s')
    file_handler.setFormatter(file_formatter)
    file_logger.addHandler(file_handler)
    file_logger.propagate = False

    client = TCPClient(
        'server',
        8888,
        2
    )
    asyncio.run(client.run())
