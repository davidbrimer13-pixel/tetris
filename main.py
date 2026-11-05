# MakeCode micro:bit Python APIs (not MicroPython's microbit module).
WIDTH = 5
HEIGHT = 5
FULL_ROW = 31


def start_pressed():
    # The touch logo is available on micro:bit V2; A+B is the V1 fallback.
    return input.logo_is_pressed() or (input.button_is_pressed(Button.A) and input.button_is_pressed(Button.B))


def show_start_prompt():
    basic.show_leds("""
. . # . .
. # # # .
. . # . .
. . # . .
. . # . .
""")


def occupied(board, x, y):
    if x < 0 or x >= WIDTH or y >= HEIGHT:
        return True
    if y < 0:
        return False
    return (board[y] // (2 ** x)) % 2 == 1


def can_place(board, kind, px, py):
    if occupied(board, px, py):
        return False
    if kind == 1 and occupied(board, px + 1, py):
        return False
    if kind == 2 and occupied(board, px, py + 1):
        return False
    return True


def draw_board(board, kind, px, py):
    basic.clear_screen()
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if occupied(board, x, y):
                led.plot_brightness(x, y, 100)

    if kind >= 0:
        led.plot_brightness(px, py, 35)
        if kind == 1:
            led.plot_brightness(px + 1, py, 35)
        elif kind == 2:
            led.plot_brightness(px, py + 1, 35)


def lock_piece(board, kind, px, py):
    board[py] = board[py] + 2 ** px
    if kind == 1:
        board[py] = board[py] + 2 ** (px + 1)
    elif kind == 2:
        board[py + 1] = board[py + 1] + 2 ** px


def clear_rows(board):
    cleared = 0
    y = HEIGHT - 1
    while y >= 0:
        if board[y] == FULL_ROW:
            # Flash the full row before removing it.
            for x in range(WIDTH):
                led.plot_brightness(x, y, 255)
            basic.pause(100)
            for x in range(WIDTH):
                led.unplot(x, y)
            basic.pause(60)

            # Collapse the rows above into the gap, showing each step.
            row = y
            while row > 0:
                board[row] = board[row - 1]
                row = row - 1
                draw_board(board, -1, 0, 0)
                basic.pause(90)
            board[0] = 0
            draw_board(board, -1, 0, 0)
            basic.pause(90)
            cleared = cleared + 1
            # Recheck this row in case another full row fell into it.
        else:
            y = y - 1
    return cleared


def make_piece():
    # 0 = one LED, 1 = two horizontal LEDs, 2 = two vertical LEDs.
    return Math.random_range(0, 2)


while True:
    show_start_prompt()
    while not start_pressed():
        basic.pause(25)
    basic.pause(250)
    while start_pressed():
        basic.pause(25)

    board = [0, 0, 0, 0, 0]
    score = 0
    kind = make_piece()
    if kind == 1:
        px = 1
    else:
        px = 2
    py = 0
    game_over = not can_place(board, kind, px, py)
    last_fall = control.millis()
    previous_a = input.button_is_pressed(Button.A)
    previous_b = input.button_is_pressed(Button.B)
    draw_board(board, kind, px, py)

    while not game_over:
        moved = False
        a_down = input.button_is_pressed(Button.A)
        b_down = input.button_is_pressed(Button.B)
        if a_down and not previous_a and can_place(board, kind, px - 1, py):
            px = px - 1
            moved = True
        if b_down and not previous_b and can_place(board, kind, px + 1, py):
            px = px + 1
            moved = True
        previous_a = a_down
        previous_b = b_down

        if input.is_gesture(Gesture.SHAKE):
            while can_place(board, kind, px, py + 1):
                py = py + 1
                draw_board(board, kind, px, py)
                basic.pause(35)
            lock_piece(board, kind, px, py)
            score = score + clear_rows(board)
            kind = make_piece()
            if kind == 1:
                px = 1
            else:
                px = 2
            py = 0
            game_over = not can_place(board, kind, px, py)
            last_fall = control.millis()
            draw_board(board, kind, px, py)
        else:
            fall_delay = 700 - score * 30
            if fall_delay < 180:
                fall_delay = 180
            if control.millis() - last_fall >= fall_delay:
                last_fall = control.millis()
                if can_place(board, kind, px, py + 1):
                    py = py + 1
                    moved = True
                else:
                    lock_piece(board, kind, px, py)
                    score = score + clear_rows(board)
                    kind = make_piece()
                    if kind == 1:
                        px = 1
                    else:
                        px = 2
                    py = 0
                    game_over = not can_place(board, kind, px, py)
                    moved = True

        if moved and not game_over:
            draw_board(board, kind, px, py)
        basic.pause(20)

    basic.show_leds("""
# . . . #
. # . # .
. . # . .
. # . # .
# . . . #
""")
    basic.pause(700)
