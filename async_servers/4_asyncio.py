import asyncio

###############################################
# Асинхронный сервер на asyncio
###############################################


async def handle_client(reader, writer):
    request = None
    while request != "quit":
        request = (await reader.read(255)).decode("utf8")
        prepared_req = f"Обработанный ответ: --{request[:-1]}--"
        print(prepared_req)
        # response = str(prepared_req)
        # writer.write(response.encode('utf8'))
        # await writer.drain()
    writer.close()


async def run_server():
    server = await asyncio.start_server(handle_client, "localhost", 15555)
    async with server:
        await server.serve_forever()


asyncio.run(run_server())
