import unittest

from minigolf import HitsMatch, HolesMatch, Player


class TestHitsMatch(unittest.TestCase):
    def setUp(self):
        self.players_list = [Player('A'), Player('B'), Player('C')]
        self.players_names_tuple = tuple(player.name for player in self.players_list)
        self.hits_match = HitsMatch(3, self.players_list)

    def test_one_not_successful_hit_on_first_hole(self):
        """
        Checks, that after unsuccessful hit nothing will be showed in the table
        """
        self.hits_match.hit()  # 1
        self.assertEqual([self.players_names_tuple,
                          (None, None, None),
                          (None, None, None),
                          (None, None, None)],
                         self.hits_match.get_table())

    def test_one_successful_hit_on_first_hole(self):
        """
        Checks that first hit on the first hole will be made by a first player
        """
        self.hits_match.hit(success=True)  # 1
        self.assertEqual([self.players_names_tuple,
                          (1, None, None),
                          (None, None, None),
                          (None, None, None)],
                         self.hits_match.get_table())

    def test_first_hole_auto_closing_after_reaching_the_limit_of_hits_1(self):
        """
        Checks reaching the limit of hits
        """
        self.hits_match.hit()  # 1
        self.hits_match.hit(success=True)  # 2
        self.hits_match.hit()  # 3
        self.hits_match.hit(success=True)  # 1
        [self.hits_match.hit() for _ in range(8)]  # 3

        self.assertEqual([self.players_names_tuple,
                          (2, 1, 10),
                          (None, None, None),
                          (None, None, None)],
                         self.hits_match.get_table())

    def test_first_hole_auto_closing_after_reaching_the_limit_of_hits_2(self):
        """
        Checks that hole will close automatically after 30 unsuccessful hits
        """
        for _ in range(10):
            for _ in range(3):
                self.hits_match.hit()  # 2, 3, 1
        self.assertEqual([self.players_names_tuple,
                          (10, 10, 10),
                          (None, None, None),
                          (None, None, None)],
                         self.hits_match.get_table())

    def _close_first_hole_with_successful_first_hits(self):
        self.hits_match.hit(success=True)  # 1
        self.hits_match.hit(success=True)  # 2
        self.hits_match.hit(success=True)  # 3

    def test_one_successful_hit_on_second_hole(self):
        """
        Checks that first hit on the second hole will be made by a second player
        """
        self._close_first_hole_with_successful_first_hits()
        self.hits_match.hit(success=True)  # 2 because it's a second hole
        self.assertEqual([self.players_names_tuple,
                          (1, 1, 1),
                          (None, 1, None),
                          (None, None, None)],
                         self.hits_match.get_table())

    def test_second_hole_auto_closing_after_reaching_the_limit_of_hits(self):
        """
        Checks reaching the limit of hits
        """
        self._close_first_hole_with_successful_first_hits()

        self.hits_match.hit()  # 2
        self.hits_match.hit(success=True)  # 3
        self.hits_match.hit()  # 1
        self.hits_match.hit(success=True)  # 2
        [self.hits_match.hit() for _ in range(8)]  # 1

        self.assertEqual([self.players_names_tuple,
                          (1, 1, 1),
                          (10, 2, 1),
                          (None, None, None)],
                         self.hits_match.get_table())

    def _close_second_hole_with_successful_first_hits(self):
        self.hits_match.hit(success=True)  # 2
        self.hits_match.hit(success=True)  # 3
        self.hits_match.hit(success=True)  # 1

    def test_one_successful_hit_on_third_hole(self):
        """
        Checks that first hit on the third hole will be made by a third player
        """
        self._close_first_hole_with_successful_first_hits()
        self._close_second_hole_with_successful_first_hits()

        self.hits_match.hit(success=True)  # 3 because it's a third hole
        self.assertEqual([self.players_names_tuple,
                          (1, 1, 1),
                          (1, 1, 1),
                          (None, None, 1)],
                         self.hits_match.get_table())

    def _close_third_hole_with_successful_first_hits(self):
        self.hits_match.hit(success=True)  # 3
        self.hits_match.hit(success=True)  # 1
        self.hits_match.hit(success=True)  # 2

    def test_runtime_error_by_hit_on_finished_game(self):
        self._close_first_hole_with_successful_first_hits()
        self._close_second_hole_with_successful_first_hits()
        self._close_third_hole_with_successful_first_hits()

        with self.assertRaises(RuntimeError):
            self.hits_match.hit()

    def test_runtime_error_by_get_winners_on_unfinished_game(self):
        with self.assertRaises(RuntimeError):
            self.hits_match.get_winners()

    def test_get_winners_1(self):
        self._close_first_hole_with_successful_first_hits()
        self._close_second_hole_with_successful_first_hits()
        self._close_third_hole_with_successful_first_hits()

        self.assertEqual([self.players_names_tuple,
                          (1, 1, 1),
                          (1, 1, 1),
                          (1, 1, 1)],
                         self.hits_match.get_table())

        self.assertEqual(self.hits_match.get_winners(),
                         self.players_list)

    def test_get_winners_2(self):
        self.hits_match.hit(success=True)  # 1
        self.hits_match.hit()  # 2
        self.hits_match.hit(success=True)  # 3
        self.hits_match.hit(success=True)  # 2
        self._close_second_hole_with_successful_first_hits()
        self._close_third_hole_with_successful_first_hits()

        self.assertEqual([self.players_names_tuple,
                          (1, 2, 1),
                          (1, 1, 1),
                          (1, 1, 1)],
                         self.hits_match.get_table())

        self.assertEqual(self.hits_match.get_winners(),
                         [self.players_list[0], self.players_list[2]])

    def test_get_winners_3(self):
        self.hits_match.hit()  # 1
        self.hits_match.hit()  # 2
        self.hits_match.hit(success=True)  # 3
        self.hits_match.hit(success=True)  # 1
        self.hits_match.hit(success=True)  # 2
        self._close_second_hole_with_successful_first_hits()
        self._close_third_hole_with_successful_first_hits()

        self.assertEqual([self.players_names_tuple,
                          (2, 2, 1),
                          (1, 1, 1),
                          (1, 1, 1)],
                         self.hits_match.get_table())

        self.assertEqual(self.hits_match.get_winners(),
                         [self.players_list[2]])


class TestHolesMatch(unittest.TestCase):
    def setUp(self):
        self.players_list = [Player('A'), Player('B'), Player('C')]
        # TODO: tuple instead of list
        self.players_names_tuple = tuple(player.name for player in self.players_list)
        self.holes_match = HolesMatch(3, self.players_list)

    def test_one_not_successful_hit_on_first_hole(self):
        """
        Checks, that after unsuccessful hit nothing will be showed in the table
        """
        self.holes_match.hit()  # 1
        self.assertEqual([self.players_names_tuple,
                          (None, None, None),
                          (None, None, None),
                          (None, None, None)],
                         self.holes_match.get_table())

    def test_one_successful_hit_on_first_hole(self):
        """
        Checks that first hit on the first hole will be made by a first player
        """
        self.holes_match.hit(success=True)  # 1
        self.assertEqual([self.players_names_tuple,
                          (1, None, None),
                          (None, None, None),
                          (None, None, None)],
                         self.holes_match.get_table())

    def test_auto_closed_first_hole_by_one_successful_hit(self):
        """
        Checks that after one successful hit by one of the players
        hole will be closed and other players will get zero
        """
        self.holes_match.hit()  # 1
        self.holes_match.hit(success=True)  # 2
        self.holes_match.hit()  # 3

        self.assertEqual([self.players_names_tuple,
                          (0, 1, 0),
                          (None, None, None),
                          (None, None, None)],
                         self.holes_match.get_table())

    def test_hole_auto_closing_after_reaching_the_limit_of_hits(self):
        """
        Checks that hole will close automatically after 30 unsuccessful hits
        """
        for _ in range(10):
            for _ in range(3):
                self.holes_match.hit()  # 2, 3, 1
        self.assertEqual([self.players_names_tuple,
                          (0, 0, 0),
                          (None, None, None),
                          (None, None, None)],
                         self.holes_match.get_table())

    def _close_first_hole_with_successful_first_hits(self):
        self.holes_match.hit(success=True)  # 1
        self.holes_match.hit(success=True)  # 2
        self.holes_match.hit(success=True)  # 3

    def test_one_successful_hit_on_second_hole(self):
        """
        Checks that first hit on the second hole will be made by a second player
        """
        self._close_first_hole_with_successful_first_hits()
        self.holes_match.hit(success=True)  # 2 because it's a second hole
        self.assertEqual([self.players_names_tuple,
                          (1, 1, 1),
                          (None, 1, None),
                          (None, None, None)],
                         self.holes_match.get_table())

    def test_auto_closed_second_hole_by_one_successful_hit(self):
        """
        Checks that after one successful hit by one of the players
        hole will be closed and other players will get zero
        """
        self._close_first_hole_with_successful_first_hits()

        self.holes_match.hit()  # 2
        self.holes_match.hit(success=True)  # 3
        self.holes_match.hit()  # 1

        self.assertEqual([self.players_names_tuple,
                          (1, 1, 1),
                          (0, 0, 1),
                          (None, None, None)],
                         self.holes_match.get_table())

    def _close_second_hole_with_successful_first_hits(self):
        self.holes_match.hit(success=True)  # 2
        self.holes_match.hit(success=True)  # 3
        self.holes_match.hit(success=True)  # 1

    def test_one_successful_hit_on_third_hole(self):
        """
        Checks that first hit on the third hole will be made by a third player
        """
        self._close_first_hole_with_successful_first_hits()
        self._close_second_hole_with_successful_first_hits()

        self.holes_match.hit(success=True)  # 3 because it's a third hole
        self.assertEqual([self.players_names_tuple,
                          (1, 1, 1),
                          (1, 1, 1),
                          (None, None, 1)],
                         self.holes_match.get_table())

    def _close_third_hole_with_successful_first_hits(self):
        self.holes_match.hit(success=True)  # 3
        self.holes_match.hit(success=True)  # 1
        self.holes_match.hit(success=True)  # 2

    def test_runtime_error_by_hit_on_finished_game(self):
        self._close_first_hole_with_successful_first_hits()
        self._close_second_hole_with_successful_first_hits()
        self._close_third_hole_with_successful_first_hits()

        with self.assertRaises(RuntimeError):
            self.holes_match.hit()

    def test_runtime_error_by_get_winners_on_unfinished_game(self):
        with self.assertRaises(RuntimeError):
            self.holes_match.get_winners()

    def test_get_winners_1(self):
        self._close_first_hole_with_successful_first_hits()
        self._close_second_hole_with_successful_first_hits()
        self._close_third_hole_with_successful_first_hits()

        self.assertEqual([self.players_names_tuple,
                          (1, 1, 1),
                          (1, 1, 1),
                          (1, 1, 1)],
                         self.holes_match.get_table())

        self.assertEqual(self.holes_match.get_winners(),
                         self.players_list)

    def test_get_winners_2(self):
        self.holes_match.hit(success=True)
        self.holes_match.hit()
        self.holes_match.hit(success=True)
        self._close_second_hole_with_successful_first_hits()
        self._close_third_hole_with_successful_first_hits()

        self.assertEqual([self.players_names_tuple,
                          (1, 0, 1),
                          (1, 1, 1),
                          (1, 1, 1)],
                         self.holes_match.get_table())

        self.assertEqual(self.holes_match.get_winners(),
                         [self.players_list[0], self.players_list[2]])

    def test_get_winners_3(self):
        self.holes_match.hit()
        self.holes_match.hit()
        self.holes_match.hit(success=True)
        self._close_second_hole_with_successful_first_hits()
        self._close_third_hole_with_successful_first_hits()

        self.assertEqual([self.players_names_tuple,
                          (0, 0, 1),
                          (1, 1, 1),
                          (1, 1, 1)],
                         self.holes_match.get_table())

        self.assertEqual(self.holes_match.get_winners(),
                         [self.players_list[2]])
