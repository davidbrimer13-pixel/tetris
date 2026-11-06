let board: number;
let kind: number;
let px: number;
let py: number;
let game_over: boolean;
let last_fall: number;
let previous_a: boolean;
let previous_b: boolean;
let moved: boolean;
let a_down: boolean;
let b_down: boolean;
//  MakeCode micro:bit Python Tetris.
//  The board is stored as one integer bit field rather than a Python list;
//  this avoids the unsupported list-index operation that caused the runtime crash.
let WIDTH = 5
let HEIGHT = 5
let FULL_ROW = 31
function bit_value(index: any): number {
    let value = 1
    let count = 0
    while (count < index) {
        value = value * 2
        count = count + 1
    }
    return value
}

function start_pressed() {
    //  The touch logo is available on micro:bit V2; A+B is the V1 fallback.
    return input.logoIsPressed() || input.buttonIsPressed(Button.A) && input.buttonIsPressed(Button.B)
}

function show_start_prompt() {
    basic.showLeds(`
. . # . .
. # # # .
. . # . .
. . # . .
. . # . .
`)
}

function occupied(board: number, x: number, y: number): boolean {
    if (x < 0 || x >= WIDTH || y >= HEIGHT) {
        return true
    }
    
    if (y < 0) {
        return false
    }
    
    let index = y * WIDTH + x
    return Math.idiv(board, bit_value(index)) % 2 == 1
}

function can_place(board: number, kind: number, px: number, py: number): boolean {
    if (occupied(board, px, py)) {
        return false
    }
    
    if (kind == 1 && occupied(board, px + 1, py)) {
        return false
    }
    
    if (kind == 2 && occupied(board, px, py + 1)) {
        return false
    }
    
    return true
}

function draw_board(board: number, kind: number, px: number, py: number) {
    basic.clearScreen()
    for (let y = 0; y < HEIGHT; y++) {
        for (let x = 0; x < WIDTH; x++) {
            if (occupied(board, x, y)) {
                led.plotBrightness(x, y, 100)
            }
            
        }
    }
    if (kind >= 0) {
        led.plotBrightness(px, py, 35)
        if (kind == 1) {
            led.plotBrightness(px + 1, py, 35)
        } else if (kind == 2) {
            led.plotBrightness(px, py + 1, 35)
        }
        
    }
    
}

function lock_piece(board: number, kind: number, px: number, py: number): number {
    board = board + bit_value(py * WIDTH + px)
    if (kind == 1) {
        board = board + bit_value(py * WIDTH + px + 1)
    } else if (kind == 2) {
        board = board + bit_value((py + 1) * WIDTH + px)
    }
    
    return board
}

function row_is_full(board: number, y: number): boolean {
    let x = 0
    while (x < WIDTH) {
        if (!occupied(board, x, y)) {
            return false
        }
        
        x = x + 1
    }
    return true
}

function clear_one_row(board: number, clear_y: number): number {
    let x: number;
    //  Repack every other row toward the bottom. Rows below the cleared row
    //  stay in place, while rows above it fall down into the gap.
    let result = 0
    let dest_y = HEIGHT - 1
    let source_y = HEIGHT - 1
    while (source_y >= 0) {
        if (source_y != clear_y) {
            x = 0
            while (x < WIDTH) {
                if (occupied(board, x, source_y)) {
                    result = result + bit_value(dest_y * WIDTH + x)
                }
                
                x = x + 1
            }
            dest_y = dest_y - 1
        }
        
        source_y = source_y - 1
    }
    return result
}

function clear_rows(board: number): number {
    let x: number;
    let y = HEIGHT - 1
    while (y >= 0) {
        if (row_is_full(board, y)) {
            //  Flash the full row before removing it.
            x = 0
            while (x < WIDTH) {
                led.plotBrightness(x, y, 255)
                x = x + 1
            }
            basic.pause(100)
            x = 0
            while (x < WIDTH) {
                led.unplot(x, y)
                x = x + 1
            }
            basic.pause(60)
            board = clear_one_row(board, y)
            draw_board(board, -1, 0, 0)
            basic.pause(120)
        } else {
            //  Recheck this row in case another complete row moved into it.
            y = y - 1
        }
        
    }
    return board
}

function make_piece(): number {
    //  0 = one LED, 1 = two horizontal LEDs, 2 = two vertical LEDs.
    return Math.randomRange(0, 2)
}

while (true) {
    show_start_prompt()
    while (!start_pressed()) {
        basic.pause(25)
    }
    basic.pause(250)
    while (start_pressed()) {
        basic.pause(25)
    }
    board = 0
    kind = make_piece()
    if (kind == 1) {
        px = 1
    } else {
        px = 2
    }
    
    py = 0
    game_over = !can_place(board, kind, px, py)
    last_fall = control.millis()
    previous_a = input.buttonIsPressed(Button.A)
    previous_b = input.buttonIsPressed(Button.B)
    draw_board(board, kind, px, py)
    while (!game_over) {
        moved = false
        a_down = input.buttonIsPressed(Button.A)
        b_down = input.buttonIsPressed(Button.B)
        if (a_down && !previous_a && can_place(board, kind, px - 1, py)) {
            px = px - 1
            moved = true
        }
        
        if (b_down && !previous_b && can_place(board, kind, px + 1, py)) {
            px = px + 1
            moved = true
        }
        
        previous_a = a_down
        previous_b = b_down
        if (input.isGesture(Gesture.Shake)) {
            while (can_place(board, kind, px, py + 1)) {
                py = py + 1
                draw_board(board, kind, px, py)
                basic.pause(35)
            }
            board = lock_piece(board, kind, px, py)
            board = clear_rows(board)
            kind = make_piece()
            if (kind == 1) {
                px = 1
            } else {
                px = 2
            }
            
            py = 0
            game_over = !can_place(board, kind, px, py)
            last_fall = control.millis()
            draw_board(board, kind, px, py)
        } else if (control.millis() - last_fall >= 700) {
            last_fall = control.millis()
            if (can_place(board, kind, px, py + 1)) {
                py = py + 1
                moved = true
            } else {
                board = lock_piece(board, kind, px, py)
                board = clear_rows(board)
                kind = make_piece()
                if (kind == 1) {
                    px = 1
                } else {
                    px = 2
                }
                
                py = 0
                game_over = !can_place(board, kind, px, py)
                moved = true
            }
            
        }
        
        if (moved && !game_over) {
            draw_board(board, kind, px, py)
        }
        
        basic.pause(20)
    }
    basic.showLeds(`
# . . . #
. # . # .
. . # . .
. # . # .
# . . . #
`)
    basic.pause(700)
}
