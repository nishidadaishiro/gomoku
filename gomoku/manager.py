import numpy as np
import sys

from gomoku.agent.base import BaseAgent, RandomAgent, ConsoleAgent
from gomoku.agent.greedy import GreedyAgent, GreedyDefendingAgent
from gomoku.board import GomokuBoard
from gomoku.util import CsvStream, Side

class GameManager:

    NUM_RETRIES = 10

    def __init__(self, size: int = 19, quiet: bool = False):
        self.__board = GomokuBoard(size, quiet)
        self.__quiet = quiet

    def get_board(self):
        return self.__board

    def get_agent_class(self, name):
        if name == "random":
            return RandomAgent
        elif name == "console":
            return ConsoleAgent
        elif name == "greedy":
            return GreedyAgent
        elif name == "greedy_defender":
            return GreedyDefendingAgent
        else:
            print(f'Invalid agent type: {name}')
            sys.exit()

    def reset_game(self):
        self.__board.reset()

    def add_piece(self, coord: np.array, side: Side) -> (bool, Side, GomokuBoard):
        """
        Place a piece on the board and check ending criteria

        Parameters
        ----------
        coord : np.array
            coordinate to place the piece
        side : int
            side of the piece

        Returns
        -------
        success: bool
            validity of the move
        winner: int
            winning side if it exists, -1 if tied, 0 otherwise
        board: GomokuBoard
            state of the board after the move
        """

        assert side.is_player()

        if not self.__board.add_piece(coord, side):
            return False, Side.NONE, self.__board

        if self.__board.check_win(coord, side):
            winner = side
            if not self.__quiet:
                print(f'{side} wins!')
        elif self.__board.check_tie():
            winner = Side.TIE
            if not self.__quiet:
                print('game tied!')
        else:
            winner = Side.NONE

        return True, winner, self.__board

    def make_agent_move(self, agent: BaseAgent, stream: CsvStream = None) -> bool:
        """
        Have an agent make a move

        Parameters
        ----------
        agent : BaseAgent
            agent to make the move
        stream : CsvStream
            stream to output moves

        Returns
        -------
        winner: int
            winning side if it exists, -1 if tied, 0 otherwise
        """
        while True:
            for num_try in range(self.NUM_RETRIES):
                move = agent.move(self.__board)
                if self.__board.is_valid_move(move):
                    break

            if num_try == self.NUM_RETRIES - 1:
                print(f'{agent.get_side()} failed to find a valid move')
                return agent.get_opponent()

            success, winner, _ = self.add_piece(move, agent.get_side())
            if stream:
                stream.add_move(agent.get_side(), move, self.__board.get_board(), winner)
            if success:
                return winner


    def run_game_custom(self, agent1: BaseAgent, agent2: BaseAgent, output: bool = False, path: str = None):
        """
        Run a game between two agents

        Parameters
        ----------
        agent1 : BaseAgent
            agent to play black
        agent2 : BaseAgent
            agent to play white
        output : bool
            whether to output moves to csv
        path : str
            directory of output csv file

        Returns
        -------
        winner: int
            winning side if it exists, -1 if tied, 0 otherwise
        """
        if output:
            assert path is not None

        self.reset_game()

        stream = None
        if output:
            stream = CsvStream(path, self.__board.get_size())

        agent1.set_side(Side.BLACK)
        agent2.set_side(Side.WHITE)

        while True:
            winner = self.make_agent_move(agent1, stream)
            if winner != Side.NONE:
                break
            winner = self.make_agent_move(agent2, stream)
            if winner != Side.NONE:
                break
        if not self.__quiet:
            print('Game done')
        return winner


    def run_game(self, agent_name1: str, agent_name2: str, output: bool = False, path: str = None):
        """
        Run a game between two agents

        Parameters
        ----------
        agent_name1 : str
            name of agent to play black
        agent_name2 : str
            name of agent to play white
        output : bool
            whether to output moves to csv
        path : str
            directory of output csv file

        Returns
        -------
        winner: int
            winning side if it exists, -1 if tied, 0 otherwise
        """
        agent1 = self.get_agent_class(agent_name1)()
        agent2 = self.get_agent_class(agent_name2)()
        return self.run_game_custom(agent1, agent2, output, path)
