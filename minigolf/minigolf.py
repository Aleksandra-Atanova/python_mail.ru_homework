from collections import defaultdict
from abc import ABCMeta, abstractmethod


class Player:

    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, repr(self.name))


class Match(metaclass=ABCMeta):

    def __init__(self, holes, players):
        self.holes = holes
        self.players = players
        self._table = [self.players, *[tuple(None for _ in self.players) for _ in range(self.holes)]]
        self._hit_counter = defaultdict(lambda: [[False, 0] for _ in range(self.holes)])
        self.players_names_list = [player.name for player in self.players]

    @abstractmethod
    def hit(self, success=False):
        pass

    # find current_hole
    def _get_current_hole(self):
        finished_holes = 0
        current_hole = 0
        for hole in range(self.holes):
            finished_players = 0
            for parameters in self._hit_counter.values():
                if parameters[hole][0] is True:
                    finished_players += 1
            if finished_players == len(self.players):
                finished_holes += 1
            else:
                current_hole = hole
                break
        if finished_holes == self.holes:
            raise RuntimeError('The game is finished')
        else:
            return current_hole

    def get_winners(self):
        result_dict = {}

        if not self.finished:
            raise RuntimeError('Match isn\'t finished')
        else:
            for player, points in self._hit_counter.items():
                result_score = 0
                for hole in range(self.holes):
                    result_score += points[hole][1]
                result_dict[player] = result_score
        return self._find_winners_in_dict(result_dict)

    @abstractmethod
    def _find_winners_in_dict(self, players_dict):
        pass

    @property
    def hole_points(self):
        holes = self.holes
        hole_points = [[] for _ in range(holes)]

        for player_name in self.players_names_list:
            points = self._hit_counter[player_name]
            for hole in range(holes):
                if points[hole][0] is True:
                    hole_points[hole].append(points[hole][1])
                else:
                    hole_points[hole].append(None)
        return hole_points

    def get_table(self):
        table = [tuple(player.name for player in self.players)]
        table.extend(tuple(element) for element in self.hole_points)
        return table

    @property
    def finished(self):
        match_status = None
        for hole in range(self.holes):
            if None in self.hole_points[hole]:
                match_status = False
                break
            else:
                match_status = True
        return match_status


class HitsMatch(Match):

    def __init__(self, holes, players):
        super().__init__(holes, players)
        self._hits_limit = 10
        self._penalty_points = 1
        self.step_to_next_player = 0  # counts how many players have already hit during the hole game

    def hit(self, success=False):

        current_hole = self._get_current_hole()
        current_player_index = ((current_hole + self.step_to_next_player) % len(self.players))
        current_player = self.players[current_player_index].name

        while self._hit_counter[current_player][current_hole][0] is True:
            current_player_index = ((current_hole + self.step_to_next_player + 1) % len(self.players))
            current_player = self.players[current_player_index].name
            self.step_to_next_player += 1

        if self._hit_counter[current_player][current_hole][1] < self._hits_limit - 1:
            self._hit_counter[current_player][current_hole][1] += 1
            self._hit_counter[current_player][current_hole][0] = success
        if self._hit_counter[current_player][current_hole][1] == (self._hits_limit - 1) and success is False:
            self._hit_counter[current_player][current_hole][1] += self._penalty_points
            self._hit_counter[current_player][current_hole][0] = True  # finished
        self.step_to_next_player += 1

        if all(player_results[current_hole][0] for player_results in self._hit_counter.values()):
            self.step_to_next_player = 0

    def _find_winners_in_dict(self, players_dict):
        self._winners = [player for player in self.players if players_dict[player.name] == min(players_dict.values())]
        return self._winners


class HolesMatch(Match):
    def __init__(self, holes, players):
        super().__init__(holes, players)
        self.circles_limit = 10
        self.circle_number = 0
        self.step_to_next_player = 0

    def hit(self, success=False):

        current_hole = self._get_current_hole()
        current_player_index = (current_hole + self.step_to_next_player) % len(self.players)
        current_player = self.players_names_list[current_player_index]
        success_in_circle = 0  # counts how many successful hits in the end of circle (if the hole is finished)

        # if current player has the same number as the current hole (new circle is started)
        if current_hole == self.players_names_list.index(current_player):
            self.circle_number += 1

        # if it's the last player in last circle
        next_player_index = (current_hole + self.step_to_next_player + 1) % len(self.players)
        if (self.circle_number == self.circles_limit) and \
                (next_player_index == current_hole):  # if it's True, then current player is the last in the circle
            for player in self.players_names_list:
                self._hit_counter[player][current_hole][0] = True
            self.step_to_next_player = 0

        # if it's the last player, but not in the last circle
        elif next_player_index == current_hole:
            self._hit_counter[current_player][current_hole][0] = success  # add information about current player
            for player in self.players_names_list:
                if self._hit_counter[player][current_hole][0] is True:
                    success_in_circle += 1

            # if we have players in this circle, who hits(True), hole is finished
            if success_in_circle > 0:
                for player in self.players_names_list:
                    self._hit_counter[player][current_hole][0] = True
                self._hit_counter[current_player][current_hole][1] += int(success)
                self.step_to_next_player = 0
                self.circle_number = 0

            # if there're no players with hit(True) in the circle
            else:
                self.step_to_next_player += 1

        # if this player is't the last in the circle
        else:
            self._hit_counter[current_player][current_hole][0] = success
            self.step_to_next_player += 1
            self._hit_counter[current_player][current_hole][1] += int(success)

    def _find_winners_in_dict(self, players_dict):
        self._winners = [player for player in self.players if players_dict[player.name] == max(players_dict.values())]
        return self._winners
