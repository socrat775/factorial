from app.handler import FactorialHandler
from aiohttp_jinja2 import setup as setup_jinja2, render_template
from jinja2 import FileSystemLoader
from aiohttp import web, WSCloseCode
from yarl import URL
from contextlib import suppress
import asyncio, logging, traceback


class Server:

    def __init__(self, config):
        self._listen = URL(config["listen"])
        self._loop = asyncio.get_event_loop()
        self._app = web.Application(middlewares=(ws_conn,))
        self._runner = web.AppRunner(self._app, handle_signals=True)

    def start(self):
        try:
            self._loop.run_until_complete(self._setup())
            logging.info("Running server on: %r" % str(self._listen))
            self._loop.run_forever()
        except Exception:
            traceback.print_exc()
        except KeyboardInterrupt:
            pass
        finally:
            logging.info("Stopping app")
            self._loop.run_until_complete(self._runner.cleanup())

    async def _setup(self):
        self._app["ws_conn"] = {}
        self._app["loop"] = self._loop
        self._app["is_shutdowning"] = False
        self._app["ws_url"] = str(self._listen.with_scheme("ws").with_path("ws"))
        self._app.on_cleanup.append(close_tasks)
        self._app.on_shutdown.append(shutdown_ws_connect)
        self._app.router.add_view("/factorial/", FactorialHandler)
        self._app.router.add_static(
            prefix="/static",
            path="app/static",
            name="static",
        )
        setup_jinja2(app=self._app, loader=FileSystemLoader("app/static/"))
        await self._runner.setup()
        self.site = web.TCPSite(
            self._runner,
            self._listen.host,
            self._listen.port,
        )
        await self.site.start()


@web.middleware
async def ws_conn(request, handler):
    if request.path.startswith("/factorial") and not request.query.get("conn"):
        logging.debug("main.html")
        return render_template("html/main.html", request, {})
    logging.debug(handler)
    return await handler(request)


async def close_tasks(app):
    logging.debug("Tasks are closing")
    tasks = asyncio.Task.all_tasks()
    for t in tasks:
        t.cancel()
        with suppress(asyncio.CancelledError):
            await t


async def shutdown_ws_connect(app):
    logging.debug("WebSocket-connects are shutdowning")
    app["is_shutdowning"] = True
    for ws in app['ws_conn'].values():
        await ws.close(
            code=WSCloseCode.GOING_AWAY,
            message='Server shutdown',
        )
