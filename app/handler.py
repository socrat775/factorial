from aiohttp import web, WSMsgType
import json, logging, traceback, uuid, asyncio


class FactorialHandler(web.View):

    async def get(self):
        ws = web.WebSocketResponse()
        await ws.prepare(self.request)
        conn_id = str(uuid.uuid4())
        self.request.app["ws_conn"][conn_id] = ws

        async for msg in ws:
            logging.debug("DATA: %s", msg.data)
            try:
                if msg.type == WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    if data.get("status") == "init":
                        try:
                            number = int(data["number"])
                            task = self.request.app["loop"].create_task(
                                factorial(number, ws)
                            )
                            await ws.send_json({"status": "wait"})
                        except ValueError:
                            await ws.send_json({
                                "status": "error",
                                "data": "пожалуйства ввидете число",
                            })
                    else:
                        response = {
                            "status": "error",
                            "data": "Not found API method",
                        }
                elif msg.type == WSMsgType.ERROR:
                    logging.error(
                        "Connection closed with exception %s", ws.exception()
                    )
                elif msg.type == WSMsgType.CLOSED:
                    logging.warning("Connection closed %s", self.store_id)
                    self.request.app["ws_conn"].pop(self.store_id)
            except Exception as e:
                traceback.print_exc()
                {"status": "error", "data": str(e)}


        if not self.request.app["is_shutdowning"]:
            self.request.app["ws_conn"].pop(self.store_id)

        return ws


async def factorial(number, ws):
    f = 1
    for i in range(2, number + 1):
        await asyncio.sleep(0)
        f *= i
    await ws.send_json({"status": "done", "data": "%d! = %d" % (number, f,)})
