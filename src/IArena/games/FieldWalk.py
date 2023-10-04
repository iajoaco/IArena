
from typing import Dict, Iterator, List
from enum import Enum
import random
import math

from IArena.interfaces.IPosition import IPosition
from IArena.interfaces.IMovement import IMovement
from IArena.interfaces.IGameRules import IGameRules
from IArena.interfaces.PlayerIndex import PlayerIndex, two_player_game_change_player
from IArena.utils.decorators import override

"""
This game represents a grid search where each square has a different weight.
There is a grid of NxN and the player must reach the position [N-1,N-1] from [0,0].
The player can move in 4 directions: up, down, left and right.
Each movement has a cost equal to the weight of the square.
The player must reach the end with the minimum cost.
"""

class FieldWalkSquare:

    def __init__(
            self,
            position: List[int],
            weight: int):
        self.position = position
        self.weight = weight

    def __str__(self) -> str:
        return "| {0:4d} |".format(self.weight)


class FieldWalkMovement(IMovement):

    class MovementDirection(Enum):
        Up = 0
        Down = 1
        Left = 2
        Right = 3

    def __init__(
            self,
            direction: MovementDirection):
        self.direction = direction

    def __eq__(
            self,
            other: "FieldWalkMovement"):
        return self.direction == other.direction

    def __str__(self):
        return f'{{direction: {self.direction}}}'


class FieldWalkPosition(IPosition):

    def __init__(
            self,
            square: FieldWalkSquare,
            cost: int,
            neighbors: Dict[FieldWalkMovement.MovementDirection, FieldWalkSquare]):
        self.square = square
        self.cost = cost
        self.neighbors = neighbors

    @override
    def next_player(
            self) -> PlayerIndex:
        return PlayerIndex.FirstPlayer

    def __eq__(
            self,
            other: "FieldWalkPosition"):
        return self.square == other.square and self.cost == other.cost

    def __str__(self):
        st = "=============================================\n"
        st += f"Square: {self.square.position}   Cost: {self.cost}\n\n"
        for direction, neighbor in self.neighbors.items():
            st += "  " + str(direction) + "  " + str(neighbor) + "\n"
        st += "=============================================\n"
        return st


class FieldWalkMap:

    def __init__(
            self,
            squares: List[List[FieldWalkSquare]]):
        self.squares = squares

    def __str__(self):
        st = ""
        st += "-" * 8 * len(self.squares[0]) + "\n"
        for row in self.squares:
            for square in row:
                st += str(square)
            st += "\n" + "-" * 8 * len(self.squares[0]) + "\n"
        return st

    def generate_random_map(rows: int, cols: int, seed: int = 0):
        random.seed(seed)
        lambda_parameter = 0.5  # You can adjust this to your preference

        def exponential_random_number():
            return max(1, int(-1/lambda_parameter * math.log(1 - random.random())))

        return FieldWalkMap([
            [
                FieldWalkSquare(
                    position=[i, j],
                    weight=exponential_random_number()
                ) for j in range(cols)
            ] for i in range(rows)
        ])

    def get_neigbhours(self, square: FieldWalkSquare) -> Dict[FieldWalkMovement.MovementDirection, FieldWalkSquare]:
        row = square.position[0]
        col = square.position[1]
        result = {}
        if row > 0:
            result[FieldWalkMovement.MovementDirection.Up] = self.squares[row - 1][col]
        if row < len(self.squares) - 1:
            result[FieldWalkMovement.MovementDirection.Down] = self.squares[row + 1][col]
        if col > 0:
            result[FieldWalkMovement.MovementDirection.Left] = self.squares[row][col - 1]
        if col < len(self.squares[row]) - 1:
            result[FieldWalkMovement.MovementDirection.Right] = self.squares[row][col + 1]
        return result

    def get_next_position(self, square: FieldWalkSquare, movement: FieldWalkMovement):
        if movement == FieldWalkMovement.MovementDirection.Up:
            return self.squares[square.position[0]-1][square.position[1]]
        elif movement == FieldWalkMovement.MovementDirection.Down:
            return self.squares[square.position[0]+1][square.position[1]]
        elif movement == FieldWalkMovement.MovementDirection.Right:
            return self.squares[square.position[0]][square.position[1]+1]
        elif movement == FieldWalkMovement.MovementDirection.Left:
            return self.squares[square.position[0]][square.position[1]-1]




class FieldWalkRules(IGameRules):

    def __init__(
            self,
            initial_map: FieldWalkMap = None,
            rows: int = 10,
            cols: int = 10,
            seed: int = 0,):
        if initial_map:
            self.map = initial_map
        else:
            self.map = FieldWalkMap.generate_random_map(rows, cols, seed)


    @override
    def n_players(self) -> int:
        return 1

    @override
    def first_position(self) -> FieldWalkPosition:
        return FieldWalkPosition(
            square=self.map.squares[0][0],
            cost=0,
            neighbors=self.map.get_neigbhours(self.map.squares[0][0]))

    @override
    def next_position(
            self,
            movement: FieldWalkMovement,
            position: FieldWalkPosition) -> FieldWalkPosition:
        new_square = self.map.get_next_position(position.square, movement)
        return FieldWalkPosition(
            new_square,
            cost=position.cost + new_square.weight,
            neighbors=self.map.get_neigbhours(new_square))

    @override
    def possible_movements(
            self,
            position: FieldWalkPosition) -> Iterator[FieldWalkMovement]:
        movements = self.map.get_neigbhours(position.square)
        return list(movements.keys())

    @override
    def finished(
            self,
            position: FieldWalkPosition) -> bool:
        return position.square.position[0] == len(self.map.squares) - 1 and position.square.position[1] == len(self.map.squares[0]) - 1

    @override
    def score(
            self,
            position: FieldWalkPosition) -> dict[PlayerIndex, float]:
        return position.cost