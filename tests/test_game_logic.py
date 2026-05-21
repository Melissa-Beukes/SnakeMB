# AAFM Test Suite v1 — unit tests
import pytest
import game_logic
from game_logic import (
    check_wall_collision,
    check_self_collision,
    get_next_head,
    calculate_new_score,
    is_valid_food_position,
    is_valid_mine_position,
    GRID_WIDTH,
    GRID_HEIGHT,
    RIGHT,
    UP,
    DOWN,
    LEFT,
)


# --- check_wall_collision ---

def test_check_wall_collision_valid_position():
    assert check_wall_collision((15, 15)) is False


def test_check_wall_collision_left_wall():
    assert check_wall_collision((-1, 10)) is True


def test_check_wall_collision_top_wall():
    assert check_wall_collision((10, -1)) is True


def test_check_wall_collision_right_wall():
    assert check_wall_collision((GRID_WIDTH, 10)) is True


def test_check_wall_collision_bottom_wall():
    assert check_wall_collision((10, GRID_HEIGHT)) is True


# --- check_self_collision ---

def test_check_self_collision_no_collision(default_snake_body):
    head = (16, 15)
    assert check_self_collision(head, default_snake_body) is False


def test_check_self_collision_head_in_middle_of_body():
    body = [(15, 15), (14, 15), (13, 15), (15, 15)]
    head = (15, 15)
    assert check_self_collision(head, body) is True


def test_check_self_collision_head_matches_tail(default_snake_body):
    head = (13, 15)
    assert check_self_collision(head, default_snake_body) is True


# --- get_next_head ---

def test_get_next_head_move_right():
    assert get_next_head((10, 10), RIGHT) == (11, 10)


def test_get_next_head_move_up():
    assert get_next_head((10, 10), UP) == (10, 9)


def test_get_next_head_move_down():
    assert get_next_head((10, 10), DOWN) == (10, 11)


def test_get_next_head_move_left():
    assert get_next_head((10, 10), LEFT) == (9, 10)


# --- calculate_new_score ---

def test_calculate_new_score_from_zero():
    assert calculate_new_score(0) == 1


def test_calculate_new_score_from_nonzero():
    assert calculate_new_score(5) == 6


def test_calculate_new_score_large_value():
    assert calculate_new_score(999) == 1000


# --- is_valid_food_position ---

def test_is_valid_food_position_valid(default_snake_body):
    assert is_valid_food_position((0, 0), default_snake_body) is True


def test_is_valid_food_position_in_snake(default_snake_body):
    assert is_valid_food_position((15, 15), default_snake_body) is False


def test_is_valid_food_position_edge_valid(default_snake_body):
    assert is_valid_food_position((GRID_WIDTH - 1, GRID_HEIGHT - 1), default_snake_body) is True


# --- is_valid_mine_position ---

def test_is_valid_mine_position_valid():
    snake_body = [(15, 15), (14, 15), (13, 15)]
    mines = []
    assert is_valid_mine_position((0, 0), snake_body, RIGHT, (28, 28), mines) is True


def test_is_valid_mine_position_in_snake_body():
    snake_body = [(15, 15), (14, 15), (13, 15)]
    mines = []
    assert is_valid_mine_position((15, 15), snake_body, RIGHT, (28, 28), mines) is False


def test_is_valid_mine_position_too_close_to_snake():
    snake_body = [(15, 15), (14, 15), (13, 15)]
    mines = []
    # (20, 15) is 5 steps from head (15,15) — within Manhattan distance 10
    assert is_valid_mine_position((20, 15), snake_body, RIGHT, (28, 28), mines) is False
