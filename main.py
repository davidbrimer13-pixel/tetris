from microbit import *
import random

WIDTH = 5
HEIGHT = 5

# Locked LEDs use brightness 2; the moving piece uses brightness 1.
EMPTY_ROW = [0, 0, 0, 0, 0]


def start_pressed():
    """Use the micro:bit V2 touch logo; on V1, start with A+B together."""
    try:
        return logo.is_pressed()
    except (NameError, AttributeError):
        return button_a.is_pressed() and button_b.is_pressed()


def wait_for_start():
    display.show(Image("00000:00900:09990:00900:00900"))
    while not start_pressed():
        sleep(30)
    sleep(250)
    while start_pressed():
        sleep(30)


def draw(board, piece=None, piece_x=0, piece_y=0):
    display.clear()
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if board[y][x]:
                display.set_pixel(x, y, 2)

    if piece is not None:
        for dx, dy in piece:
            x = piece_x + dx
            y = piece_y + dy
            if 0 <= x < WIDTH and 0 <= y < HEIGHT:
                display.set_pixel(x, y, 1)


def new_piece():
    """Pieces are one LED or a two-LED horizontal/vertical brick."""
    kind = random.randrange(3)
    if kind == 0:
        return [(0, 0)], 2
    if kind == 1:
        return [(0, 0), (1, 0)], 1
    return [(0, 0), (0, 1)], 2


def can_place(board, piece, piece_x, piece_y):
    for dx, dy in piece:
        x = piece_x + dx
        y = piece_y + dy
        if x < 0 or x >= WIDTH or y >= HEIGHT:
            return False
        if y >= 0 and board[y][x]:
            return False
    return True


def clear_rows(board):
    rows = []
    for y in range(HEIGHT):
        if all(board[y]):
            rows.append(y)

    if not rows:
        return 0

    # Briefly brighten each completed row, then animate the rows above
    # falling down one step at a time as the cleared space closes.
    for y in rows:
        for brightness in (3, 6, 9):
            for x in range(WIDTH):
                display.set_pixel(x, y, brightness)
            sleep(45)
        draw(board)
        sleep(35)

    # Remove bottom-up so the remaining original row indexes stay valid.
    for y in reversed(rows):
        board.pop(y)
        board.insert(0, EMPTY_ROW[:])
        draw(board)
        sleep(90)

    return len(rows)


def lock_piece(board, piece, piece_x, piece_y):
    for dx, dy in piece:
        x = piece_x + dx
        y = piece_y + dy
        if y < 0:
            return False
        board[y][x] = 1
    return True


def play_game():
    board = [EMPTY_ROW[:] for _ in range(HEIGHT)]
    score = 0
    piece, piece_x = new_piece()
    piece_y = 0

    if not can_place(board, piece, piece_x, piece_y):
        return

    draw(board, piece, piece_x, piece_y)
    last_fall = running_time()

    while True:
        moved = False
        if button_a.was_pressed() and can_place(board, piece, piece_x - 1, piece_y):
            piece_x -= 1
            moved = True
        if button_b.was_pressed() and can_place(board, piece, piece_x + 1, piece_y):
            piece_x += 1
            moved = True

        # A shake makes the current brick drop rapidly to its landing spot.
        if accelerometer.was_gesture("shake"):
            while can_place(board, piece, piece_x, piece_y + 1):
                piece_y += 1
                draw(board, piece, piece_x, piece_y)
                sleep(45)
            if not lock_piece(board, piece, piece_x, piece_y):
                return
            score += clear_rows(board)
            piece, piece_x = new_piece()
            piece_y = 0
            if not can_place(board, piece, piece_x, piece_y):
                return
            last_fall = running_time()
            draw(board, piece, piece_x, piece_y)
            continue

        fall_delay = max(180, 700 - score * 30)
        if running_time() - last_fall >= fall_delay:
            last_fall = running_time()
            if can_place(board, piece, piece_x, piece_y + 1):
                piece_y += 1
                moved = True
            else:
                if not lock_piece(board, piece, piece_x, piece_y):
                    return
                score += clear_rows(board)
                piece, piece_x = new_piece()
                piece_y = 0
                if not can_place(board, piece, piece_x, piece_y):
                    return
                moved = True

        if moved:
            draw(board, piece, piece_x, piece_y)
        sleep(20)


while True:
    wait_for_start()
    play_game()
    display.show(Image.NO)
    sleep(700)
