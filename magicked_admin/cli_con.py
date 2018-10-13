import logging
import signal

from colorama import init
from termcolor import colored

init()

from server.server import Server
from chatbot.chatbot import Chatbot

from utils import die
from utils.text import str_to_bool
from utils.logger import logger

from setting import Setting

settings = Setting()


class CliCon:

    def __init__(self):
        signal.signal(signal.SIGINT, self.terminate)
        self.servers = []

    def run(self):
        for server_name in settings.sections():
            logger.setLevel(
                logging.getLevelName(
                    settings.setting(server_name, "log_level"))
            )

            server = Server(server_name,
                            settings.setting(server_name, "address"),
                            settings.setting(server_name, "username"),
                            settings.setting(server_name, "password")
                            )

            server.game_password = \
                settings.setting(server_name, "game_password")
            server.url_extras = \
                settings.setting(server_name, "url_extras")
            server.level_threshold = \
                settings.setting(server_name, "level_threshold")

            has_motd_scoreboard = str_to_bool(
                settings.setting(server_name, "motd_scoreboard")
            )

            if has_motd_scoreboard:
                scoreboard_type = settings.setting(server_name,
                                                   "scoreboard_type")
                # MotdUpdater(server, scoreboard_type).start()

            self.servers.append(server)

            Chatbot(server,
                    str_to_bool(
                        settings.setting(server_name, "enable_greeter")),
                    settings.setting(server_name, "username")
                    )

        print("Initialisation complete")

    def terminate(self, signal, frame):
        print("\nProgram interrupted, terminating...")

        for server in self.servers:
            server.write_all_players(final=True)
            server.write_game_map()
            server.close()

        die()


if __name__ == "__main__":
    if __debug__:
        debug_message = "Debug mode is enabled!"
        print(colored(debug_message, 'red'))

    application = MagickedAdministrator()
    application.run()
