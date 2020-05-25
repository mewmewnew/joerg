import json
import logging
import random
from collections import deque
from typing import Deque, List

from board import Board
from cards.card import Card
from cards.cards import json_read_card
from order import Order
from player import Player

NUMBER_OF_WINNING_ROUNDS_NEEDED = 3
NUM_PLAYERS = 4
STARTING_HAND_SIZE = NUMBER_OF_WINNING_ROUNDS_NEEDED + 1
LIBRARY_PATH = "./cards/cards.json"


class InvalidLibraryFileError(Exception):
    def __init__(self, msg="Unable to read 'cards' field from library."):
        super().__init__(msg)


def shuffle_deck(cards: Deque[Card]) -> None:
    random.shuffle(cards)


def deal_cards(cards: Deque[Card], players: List[Player]) -> None:
    for player in players:
        for j in range(STARTING_HAND_SIZE):
            card = cards.pop()
            player.add_card_to_hand(card)

    assert len(player.hand) == STARTING_HAND_SIZE


def read_cards() -> Deque[Card]:
    with open(LIBRARY_PATH, "r") as fp:
        raw_object = json.load(fp)

    raw_cards = raw_object.get("cards", None)
    if not raw_cards:
        raise InvalidLibraryFileError()

    cards = [json_read_card(rc) for rc in raw_cards]
    assert len(cards) == len(
        set(cards)
    ), "Name collision in library! Two cards with same name."

    return deque(cards)


def randomly_assign_pole(players: List[Player]) -> Player:
    return random.choice(players)


def all_players_except_winner(
    players: List[Player], winning_player: Player
) -> List[Player]:
    return [p for p in players if p != winning_player]


def main():
    logging.basicConfig()
    cards = read_cards()
    shuffle_deck(cards)

    players: List[Player] = []

    for p in range(NUM_PLAYERS):
        players.append(Player(p))

    deal_cards(cards, players)
    pole_player = randomly_assign_pole(players)

    board = Board(players)

    victories = {p: 0 for p in players}
    while max(victories.values()) < NUMBER_OF_WINNING_ROUNDS_NEEDED:
        board.begin_round()
        board.set_pole(pole_player)

        # trade phase
        # pick card, pick player

        # commit phase
        # choose card, choose position

        for player in players:
            _, random_card = player.pop_random_card()
            random_order = random.choice([Order.attack, Order.defense])
            board.commit_card(player, random_card, random_order)

        # reveal phase
        # beginning from pole, reveal card
        # trigger abilities

        logging.debug(board)

        # resolve phase
        # from pole, find the winning power (lowest for defense, highest for attack), in case of multiple cards with the same power, the card closest from pole wins (linearly, not bilinearly).
        for resolving_card in board.resolve_cards():
            logging.debug(resolving_card)
            resolving_card.card.on_reveal()

        # Before power
        for resolving_card in board.resolve_cards():
            logging.debug(resolving_card)
            resolving_card.card.before_power()

        winning_card = board.resolve_power()
        for resolving_card in board.resolve_cards():
            if (
                "On Win" in resolving_card.card.ruling
                and resolving_card.card == winning_card.card
            ):
                resolving_card.on_win(board)
            elif (
                "On Lose" in resolving_card.card.ruling
                and resolving_card.card != winning_card.card
            ):
                resolving_card.card.on_lose()

        logging.debug("")
        logging.debug("Winning card!", winning_card)
        logging.debug("")
        victories[winning_card.player] += 1
        for active_card in board.losing_cards():
            active_card.player.add_card_to_hand(active_card.card)

        pole_player = board.get_next_player(pole_player)

        # Cycle
        # When any player recieves their second victory, all other players cycles 1 card.
        if victories[winning_card.player] == 2:
            cycled_cards = []
            for player in all_players_except_winner(
                players, winning_player=winning_card.player
            ):
                cycled_card_index, random_card = player.pop_random_card()
                random_card.on_cycle()
                cycled_cards.append(random_card)
                new_card = cards.popleft()
                player.add_card_to_hand(new_card, index=cycled_card_index)

            logging.debug("CYCLE!")

    logging.debug("")
    logging.debug("Victories", victories)
    logging.debug("")


if __name__ == "__main__":
    main()
