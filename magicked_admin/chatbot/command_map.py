from chatbot.commands.event_commands import *
from chatbot.commands.info_commands import *
from chatbot.commands.player_commands import *
from chatbot.commands.server_commands import *


class CommandMap:
    def __init__(self, server, chatbot):
        self.server = server
        self.chatbot = chatbot
        self.command_map = self.generate_map()

    def generate_map(self):
        scheduler = self.chatbot.scheduler

        command_map = {
            'start_jc': CommandStartJoinCommand(self.server, scheduler),
            'stop_jc': CommandStopJoinCommands(self.server, scheduler),

            'start_wc': CommandStartWaveCommand(self.server, scheduler),
            'stop_wc': CommandStopWaveCommands(self.server, scheduler),

            'start_tc': CommandStartTimeCommand(self.server, scheduler),
            'stop_tc': CommandStopTimeCommands(self.server, scheduler),

            'start_trc': CommandStartTraderCommand(self.server, scheduler),
            'stop_trc': CommandStopTraderCommands(self.server, scheduler),

            'record_wave': CommandHighWave(self.server),
            'enforce_levels': CommandEnforceLevels(self.server),
            'enforce_dosh': CommandEnforceDosh(self.server),
            'say': CommandSay(self.server),
            'restart': CommandRestart(self.server),
            'load_map': CommandLoadMap(self.server),
            'password': CommandPassword(self.server),
            'silent': CommandSilent(self.server, self.chatbot),
            'run': CommandRun(self.server, self.chatbot),
            'length': CommandLength(self.server),
            'difficulty': CommandDifficulty(self.server),
            'game_mode': CommandGameMode(self.server),
            'players': CommandPlayers(self.server),
            'game': CommandGame(self.server),
            'help': CommandHelp(self.server),
            'kills': CommandKills(self.server),
            'kick': CommandKick(self.server),
            'ban': CommandBan(self.server),
            'dosh': CommandDosh(self.server),
            'top_kills': CommandTopKills(self.server),
            'top_dosh': CommandTopDosh(self.server),
            'top_time': CommandTopTime(self.server),
            'top_wave_kills': CommandTopWaveKills(self.server),
            'top_wave_dosh': CommandTopWaveDosh(self.server),
            'stats': CommandStats(self.server),
            'game_time': CommandGameTime(self.server),
            'server_kills': CommandServerKills(self.server),
            'server_dosh': CommandServerDosh(self.server),
            'op': CommandOp(self.server),
            'deop': CommandDeop(self.server),
            'map': CommandGameMap(self.server),
            'maps': CommandGameMaps(self.server),
            'marquee': CommandMarquee(self.server, self.chatbot),
            'player_count': CommandPlayerCount(self.server),

            # TODO List internal commands and their listeners
            # Internal command list:
            # 'player_join' -> []
            # 't_open' -> []
            # 'new_wave' -> []
            # 'new_game' -> []
        }

        return command_map
