"""
Killing Floor 2 Magicked Admin
Copyright th3-z (the_z) 2018
Released under the terms of the MIT license
"""

import gettext
import os
import sys
from signal import signal, SIGTERM, SIGINT


from chatbot.chatbot import Chatbot
from chatbot.motd_updater import MotdUpdater
from chatbot.commands.command_map import CommandMap
from server.server import Server
from settings import Settings
from utils import find_data_file
from web_admin.state_transition_worker import StateTransitionWorker
from web_admin import WebAdmin
from web_admin.web_interface import WebInterface, AuthorizationException
from web_admin.chat_worker import ChatWorker
from lua_bridge.lua_bridge import LuaBridge
from events import EventManager
from database import db_init

gettext.bindtextdomain('magicked_admin', find_data_file('locale'))
gettext.textdomain('magicked_admin')
gettext.install('magicked_admin', find_data_file('locale'))

"""parser = argparse.ArgumentParser(
    description=_('Killing Floor 2 Magicked Administrator')
)
parser.add_argument('-s', '--skip_setup', action='store_true',
                    help=_('Skips the guided setup process'))
args = parser.parse_args()"""

GUI_MODE = False

if hasattr(sys, "frozen"):
    import certifi.core

    requests_ca_bundle_path = find_data_file("./certifi/cacert.pem")
    os.environ["REQUESTS_CA_BUNDLE"] = requests_ca_bundle_path
    certifi.core.where = requests_ca_bundle_path

    import requests.utils
    import requests.adapters

    requests.utils.DEFAULT_CA_BUNDLE_PATH = requests_ca_bundle_path
    requests.adapters.DEFAULT_CA_BUNDLE_PATH = requests_ca_bundle_path


class MagickedAdmin:
    version = "0.2.0"
    servers = {}
    ui = None

    @classmethod
    def add_server(cls, server_name, server_config):
        if server_name in cls.servers.keys():
            return

        cls.servers[server_name] = []

        event_manager = EventManager()
        web_interface = WebInterface(
            server_config.address, server_config.username,
            server_config.password, server_name
        )
        web_admin = WebAdmin(web_interface, event_manager)

        chat_worker = ChatWorker(
            web_admin, event_manager, refresh_rate=1
        )
        chat_worker.start()

        cls.servers[server_name].append(chat_worker)

        state_transition_worker = StateTransitionWorker(
            web_admin, event_manager, int(server_config.refresh_rate)
        )
        state_transition_worker.start()
        cls.servers[server_name].append(state_transition_worker)

        server = Server(web_admin, event_manager, server_name)
        server.game_password = server_config.game_password
        server.url_extras = server_config.url_extras
        cls.servers[server_name].append(server)

        chatbot = Chatbot(server.web_admin, server.event_manager)

        commands = CommandMap().get_commands(
            server, chatbot, MotdUpdater(server)
        )

        for command_name, command in commands.items():
            chatbot.add_command(command_name, command)

        chatbot.run_init(find_data_file(
            "conf/scripts/" + server_name + ".init"
        ))
        lua_bridge = LuaBridge(server, chatbot)
        chatbot.lua_bridge = lua_bridge

        if server_name not in Settings.servers.keys():
            Settings.add_server(server_name, server_config)

    @classmethod
    def remove_server(cls, name):
        if name not in cls.servers.keys():
            return

        for item in cls.servers[name]:
            item.close()
        cls.servers.pop(name)

        Settings.remove_server(name)

    @classmethod
    def run(cls):
        cls.banner()
        db_init()

        for server_name, server_config in Settings.servers.items():
            cls.add_server(server_name, server_config)

    @classmethod
    def close(cls):
        for stop_list in cls.servers.values():
            for item in stop_list:
                item.close()
        sys.exit(0)

    @classmethod
    def banner(cls):
        version_text = "<<{}{}>>".format(
            cls.version, "#DEBUG" if Settings.debug else ""
        )

        # figlet -f rectangles "example"
        lines = [
            "               _     _         _\n"
            " _____ ___ ___|_|___| |_ ___ _| |\n",
            "|     | .'| . | |  _| '_| -_| . |\n",
            "|_|_|_|__,|_  |_|___|_,_|___|___|\n",
            "        _ |___| _ \n",
            "  ___ _| |_____|_|___   {}\n".format(version_text),
            " | .'| . |     | |   |  {}\n".format(Settings.banner_url),
            " |__,|___|_|_|_|_|_|_|\n"
        ]
        print(str.join('', lines))


if __name__ == "__main__":
    MagickedAdmin.run()

    signal(SIGINT, MagickedAdmin.close)
    signal(SIGTERM, MagickedAdmin.close)

    if GUI_MODE:
        sys.exit()
    elif len(Settings.servers.keys()) < 1:
        Settings.append_template()
        print(
            " [!] No servers have been configured yet, "
            "please amend '{}' with your server details".format(
                Settings.config_path_display
            )
        )
        MagickedAdmin.close()
