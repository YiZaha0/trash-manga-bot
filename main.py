import importlib
import sys 
import asyncio as aio
import glob
import os
import uvloop
uvloop.install()

from bot import bot, manga_updater
from models import DB
from pathlib import Path

def load_plugin(plugin_name):
    if plugin_name.startswith("__"):
    	pass
    else:
    	path = Path(f"_extras/{plugin_name}.py")
    	name = "_extras.{}".format(plugin_name)
    	spec = importlib.util.spec_from_file_location(name, path)
    	load = importlib.util.module_from_spec(spec)
    	spec.loader.exec_module(load)
    	sys.modules["_extras." + plugin_name] = load

path = "./_extras/*py"
files = glob.glob(path)
for name in files:
	plugin_path = Path(name)
	plugin_name = plugin_path.stem
	try:
		load_plugin(plugin_name)
	except BaseException as e:
		print(f"Got Error While Loading {plugin_name}: {e}")

async def async_main():
    db = DB()
    await db.connect()

if __name__ == '__main__':
    loop = aio.get_event_loop_policy().get_event_loop() or aio.get_event_loop_policy().new_event_loop()
    loop.run_until_complete(async_main())
    loop.create_task(manga_updater())
    bot.run()

