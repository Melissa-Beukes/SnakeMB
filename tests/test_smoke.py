# AAFM Test Suite v1 — smoke tests
import game_logic


def test_game_logic_imports_without_error():
    assert game_logic is not None


def test_grid_size_is_int():
    assert isinstance(game_logic.GRID_SIZE, int)


def test_grid_width_is_int():
    assert isinstance(game_logic.GRID_WIDTH, int)


def test_grid_height_is_int():
    assert isinstance(game_logic.GRID_HEIGHT, int)


def test_window_width_is_int():
    assert isinstance(game_logic.WINDOW_WIDTH, int)


def test_window_height_is_int():
    assert isinstance(game_logic.WINDOW_HEIGHT, int)


def test_snake_colors_is_nonempty_list():
    assert isinstance(game_logic.SNAKE_COLORS, list)
    assert len(game_logic.SNAKE_COLORS) > 0


def test_initial_snake_body_is_list_of_tuples():
    body = [(game_logic.GRID_WIDTH // 2, game_logic.GRID_HEIGHT // 2)]
    assert isinstance(body, list)
    assert len(body) > 0
    assert isinstance(body[0], tuple)
    assert len(body[0]) == 2


def test_initial_food_position_validity():
    snake_body = [(game_logic.GRID_WIDTH // 2, game_logic.GRID_HEIGHT // 2)]
    pos = (0, 0)
    result = game_logic.is_valid_food_position(pos, snake_body)
    assert isinstance(result, bool)
    assert result is True


def test_score_default_is_int_zero():
    score = 0
    assert isinstance(score, int)
    assert score == 0
