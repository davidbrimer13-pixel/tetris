# MakeCode micro:bit Python Tetris.
# The board is stored as one integer bit field rather than a Python list;
# this avoids the unsupported list-index operation that caused the runtime crash.
WIDTH = 5
HEIGHT = 5
FULL_ROW = 31


def bit_value(index):
    value = 1
    count = 0
    while count < index:
        value = value * 2
        count = count + 1
    return value


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
    index = y * WIDTH + x
    return (board // bit_value(index)) % 2 == 1


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
    board = board + bit_value(py * WIDTH + px)
    if kind == 1:
        board = board + bit_value(py * WIDTH + px + 1)
    elif kind == 2:
        board = board + bit_value((py + 1) * WIDTH + px)
    return board


def row_is_full(board, y):
    x = 0
    while x < WIDTH:
        if not occupied(board, x, y):
            return False
        x = x + 1
    return True


def clear_one_row(board, clear_y):
    # Repack every other row toward the bottom. Rows below the cleared row
    # stay in place, while rows above it fall down into the gap.
    result = 0
    dest_y = HEIGHT - 1
    source_y = HEIGHT - 1
    while source_y >= 0:
        if source_y != clear_y:
            x = 0
            while x < WIDTH:
                if occupied(board, x, source_y):
                    result = result + bit_value(dest_y * WIDTH + x)
                x = x + 1
            dest_y = dest_y - 1
        source_y = source_y - 1
    return result


def clear_rows(board):
    y = HEIGHT - 1
    while y >= 0:
        if row_is_full(board, y):
            # Flash the full row before removing it.
            x = 0
            while x < WIDTH:
                led.plot_brightness(x, y, 255)
                x = x + 1
            basic.pause(100)
            x = 0
            while x < WIDTH:
                led.unplot(x, y)
                x = x + 1
            basic.pause(60)

            board = clear_one_row(board, y)
            draw_board(board, -1, 0, 0)
            basic.pause(120)
            # Recheck this row in case another complete row moved into it.
        else:
            y = y - 1
    return board


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

    board = 0
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
            board = lock_piece(board, kind, px, py)
            board = clear_rows(board)
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
            if control.millis() - last_fall >= 700:
                last_fall = control.millis()
                if can_place(board, kind, px, py + 1):
                    py = py + 1
                    moved = True
                else:
                    board = lock_piece(board, kind, px, py)
                    board = clear_rows(board)
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
