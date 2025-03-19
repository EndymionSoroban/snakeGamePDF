PDF_FILE_TEMPLATE = """
%PDF-1.6

% Root
1 0 obj
<<
  /AcroForm <<
    /Fields [ ###FIELD_LIST### ]
  >>
  /Pages 2 0 R
  /OpenAction 17 0 R
  /Type /Catalog
>>
endobj

2 0 obj
<<
  /Count 1
  /Kids [
    16 0 R
  ]
  /Type /Pages
>>

%% Annots Page 1 (also used as overall fields list)
21 0 obj
[
  ###FIELD_LIST###
]
endobj

###FIELDS###

%% Page 1
16 0 obj
<<
  /Annots 21 0 R
  /Contents 3 0 R
  /CropBox [
    0.0
    0.0
    612.0
    792.0
  ]
  /MediaBox [
    0.0
    0.0
    612.0
    792.0
  ]
  /Parent 2 0 R
  /Resources <<
  >>
  /Rotate 0
  /Type /Page
>>
endobj

3 0 obj
<< >>
stream
endstream
endobj

17 0 obj
<<
  /JS 42 0 R
  /S /JavaScript
>>
endobj


42 0 obj
<< >>
stream

// Hacky wrapper to work with a callback instead of a string 
function setInterval(cb, ms) {
    evalStr = "(" + cb.toString() + ")();";
    return app.setInterval(evalStr, ms);
}

// Random number generation
var rand_seed = Date.now() % 2147483647;
function rand() {
    return rand_seed = rand_seed * 16807 % 2147483647;
}

// Game constants
var GRID_WIDTH = ###GRID_WIDTH###;
var GRID_HEIGHT = ###GRID_HEIGHT###;
var TICK_INTERVAL = 50;
var GAME_STEP_TIME = 200;

// Game state
var snake = [];
var direction = "right";
var nextDirection = "right";
var food = { x: 0, y: 0 };
var pixel_fields = [];
var field = [];
var score = 0;
var time_ms = 0;
var last_update = 0;
var interval = 0;
var gameActive = false;

// Direction vectors
var directions = {
    "up": { x: 0, y: -1 },
    "right": { x: 1, y: 0 },
    "down": { x: 0, y: 1 },
    "left": { x: -1, y: 0 }
};

function set_controls_visibility(state) {
    this.getField("T_input").hidden = !state;
    this.getField("B_left").hidden = !state;
    this.getField("B_right").hidden = !state;
    this.getField("B_up").hidden = !state;
    this.getField("B_down").hidden = !state;
}

function placeFood() {
    var validPositions = [];
    
    // Find all empty cells
    for (var x = 0; x < GRID_WIDTH; x++) {
        for (var y = 0; y < GRID_HEIGHT; y++) {
            var isEmpty = true;
            
            // Check if cell contains snake
            for (var i = 0; i < snake.length; i++) {
                if (snake[i].x === x && snake[i].y === y) {
                    isEmpty = false;
                    break;
                }
            }
            
            if (isEmpty) {
                validPositions.push({ x: x, y: y });
            }
        }
    }
    
    // Choose random empty cell
    if (validPositions.length > 0) {
        var randomIndex = Math.floor(Math.random() * validPositions.length);
        food = validPositions[randomIndex];
    }
}

function initializeSnake() {
    // Start with a snake of length 3 in the middle of the grid
    snake = [
        { x: Math.floor(GRID_WIDTH / 2), y: Math.floor(GRID_HEIGHT / 2) },
        { x: Math.floor(GRID_WIDTH / 2) - 1, y: Math.floor(GRID_HEIGHT / 2) },
        { x: Math.floor(GRID_WIDTH / 2) - 2, y: Math.floor(GRID_HEIGHT / 2) }
    ];
    
    direction = "right";
    nextDirection = "right";
}

function game_init() {
    // Initialize game state
    initializeSnake();
    
    // Gather references to pixel field objects
    // and initialize game state
    for (var x = 0; x < GRID_WIDTH; ++x) {
        pixel_fields[x] = [];
        field[x] = [];
        for (var y = 0; y < GRID_HEIGHT; ++y) {
            pixel_fields[x][y] = this.getField(`P_${x}_${y}`);
            field[x][y] = 0;
        }
    }
    
    // Place initial food
    placeFood();
    
    // Reset game variables
    last_update = time_ms;
    score = 0;
    gameActive = true;
    
    // Start timer
    interval = setInterval(game_tick, TICK_INTERVAL);
    
    // Hide start button
    this.getField("B_start").hidden = true;
    
    // Show input box and controls
    set_controls_visibility(true);
    
    // Update score display
    draw_updated_score();
    
    // Auto-focus the text input field
    this.getField("T_input").setFocus();
}

function game_update() {
    if (!gameActive) return;
    
    if (time_ms - last_update >= GAME_STEP_TIME) {
        moveSnake();
        last_update = time_ms;
    }
}

function game_over() {
    app.clearInterval(interval);
    gameActive = false;
    app.alert(`Game over! Score: ${score}\\nClick OK to restart.`);
    
    // Show start button again
    this.getField("B_start").hidden = false;
    
    // Hide controls
    set_controls_visibility(false);
}

function isValidDirection(newDir) {
    // Prevent 180-degree turns
    if (newDir === "up" && direction === "down") return false;
    if (newDir === "down" && direction === "up") return false;
    if (newDir === "left" && direction === "right") return false;
    if (newDir === "right" && direction === "left") return false;
    return true;
}

function handle_input(event) {
    if (!gameActive) return;
    
    switch (event.change) {
        case 'w': if (isValidDirection("up")) nextDirection = "up"; break;
        case 'a': if (isValidDirection("left")) nextDirection = "left"; break;
        case 'd': if (isValidDirection("right")) nextDirection = "right"; break;
        case 's': if (isValidDirection("down")) nextDirection = "down"; break;
    }
}

function moveUp() {
    if (isValidDirection("up")) nextDirection = "up";
}

function moveDown() {
    if (isValidDirection("down")) nextDirection = "down";
}

function moveLeft() {
    if (isValidDirection("left")) nextDirection = "left";
}

function moveRight() {
    if (isValidDirection("right")) nextDirection = "right";
}

function moveSnake() {
    if (!gameActive) return;
    
    // Update direction
    direction = nextDirection;
    
    // Calculate new head position
    var head = { x: snake[0].x, y: snake[0].y };
    var dir = directions[direction];
    
    head.x += dir.x;
    head.y += dir.y;
    
    // Check for collision with walls
    if (head.x < 0 || head.x >= GRID_WIDTH || head.y < 0 || head.y >= GRID_HEIGHT) {
        game_over();
        return;
    }
    
    // Check for collision with self
    for (var i = 0; i < snake.length; i++) {
        if (snake[i].x === head.x && snake[i].y === head.y) {
            game_over();
            return;
        }
    }
    
    // Add new head
    snake.unshift(head);
    
    // Check if food is eaten
    if (head.x === food.x && head.y === food.y) {
        // Increase score
        score++;
        draw_updated_score();
        
        // Place new food
        placeFood();
        
        // Speed up the game slightly as score increases
        if (score % 5 === 0 && GAME_STEP_TIME > 50) {
            GAME_STEP_TIME -= 10;
        }
    } else {
        // Remove tail if no food was eaten
        snake.pop();
    }
}

function draw_updated_score() {
    this.getField("T_score").value = `Score: ${score}`;
}

function set_pixel(x, y, state) {
    if (x < 0 || y < 0 || x >= GRID_WIDTH || y >= GRID_HEIGHT) {
        return;
    }
    pixel_fields[x][GRID_HEIGHT - 1 - y].hidden = !state;
}

function draw() {
    // Clear all pixels
    for (var x = 0; x < GRID_WIDTH; x++) {
        for (var y = 0; y < GRID_HEIGHT; y++) {
            set_pixel(x, y, false);
        }
    }
    
    // Draw snake
    for (var i = 0; i < snake.length; i++) {
        set_pixel(snake[i].x, snake[i].y, true);
    }
    
    // Draw food
    set_pixel(food.x, food.y, true);
}

function game_tick() {
    time_ms += TICK_INTERVAL;
    game_update();
    draw();
}

// Hide controls to start with
set_controls_visibility(false);

// Zoom to fit (on FF)
app.execMenuItem("FitPage");

endstream
endobj


18 0 obj
<<
  /JS 43 0 R
  /S /JavaScript
>>
endobj


43 0 obj
<< >>
stream



endstream
endobj

trailer
<<
  /Root 1 0 R
>>

%%EOF
"""

PLAYING_FIELD_OBJ = """
###IDX### obj
<<
  /FT /Btn
  /Ff 1
  /MK <<
    /BG [
      0.8
    ]
    /BC [
      0 0 0
    ]
  >>
  /Border [ 0 0 1 ]
  /P 16 0 R
  /Rect [
    ###RECT###
  ]
  /Subtype /Widget
  /T (playing_field)
  /Type /Annot
>>
endobj
"""

PIXEL_OBJ = """
###IDX### obj
<<
  /FT /Btn
  /Ff 1
  /MK <<
    /BG [
      ###COLOR###
    ]
    /BC [
      0.5 0.5 0.5
    ]
  >>
  /Border [ 0 0 1 ]
  /P 16 0 R
  /Rect [
    ###RECT###
  ]
  /Subtype /Widget
  /T (P_###X###_###Y###)
  /Type /Annot
>>
endobj
"""

BUTTON_AP_STREAM = """
###IDX### obj
<<
  /BBox [ 0.0 0.0 ###WIDTH### ###HEIGHT### ]
  /FormType 1
  /Matrix [ 1.0 0.0 0.0 1.0 0.0 0.0]
  /Resources <<
    /Font <<
      /HeBo 10 0 R
    >>
    /ProcSet [ /PDF /Text ]
  >>
  /Subtype /Form
  /Type /XObject
>>
stream
q
0.75 g
0 0 ###WIDTH### ###HEIGHT### re
f
Q
q
1 1 ###WIDTH### ###HEIGHT### re
W
n
BT
/HeBo 12 Tf
0 g
10 8 Td
(###TEXT###) Tj
ET
Q
endstream
endobj
"""

BUTTON_OBJ = """
###IDX### obj
<<
  /A <<
    /JS ###SCRIPT_IDX### R
    /S /JavaScript
  >>
  /AP <<
    /N ###AP_IDX### R
  >>
  /F 4
  /FT /Btn
  /Ff 65536
  /MK <<
    /BG [
      0.75
    ]
    /CA (###LABEL###)
  >>
  /P 16 0 R
  /Rect [
    ###RECT###
  ]
  /Subtype /Widget
  /T (###NAME###)
  /Type /Annot
>>
endobj
"""

TEXT_OBJ = """
###IDX### obj
<<
  /AA <<
    /K <<
      /JS ###SCRIPT_IDX### R
      /S /JavaScript
    >>
  >>
  /F 4
  /FT /Tx
  /MK <<
  >>
  /MaxLen 0
  /P 16 0 R
  /Rect [
    ###RECT###
  ]
  /Subtype /Widget
  /T (###NAME###)
  /V (###LABEL###)
  /Type /Annot
>>
endobj
"""

STREAM_OBJ = """
###IDX### obj
<< >>
stream
###CONTENT###
endstream
endobj
"""

# Game configuration
PX_SIZE = 20
GRID_WIDTH = 15
GRID_HEIGHT = 15
GRID_OFF_X = 200
GRID_OFF_Y = 350

fields_text = ""
field_indexes = []
obj_idx_ctr = 50

def add_field(field):
    global fields_text, field_indexes, obj_idx_ctr
    fields_text += field
    field_indexes.append(obj_idx_ctr)
    obj_idx_ctr += 1


# Playing field outline
playing_field = PLAYING_FIELD_OBJ
playing_field = playing_field.replace("###IDX###", f"{obj_idx_ctr} 0")
playing_field = playing_field.replace("###RECT###", f"{GRID_OFF_X} {GRID_OFF_Y} {GRID_OFF_X+GRID_WIDTH*PX_SIZE} {GRID_OFF_Y+GRID_HEIGHT*PX_SIZE}")
add_field(playing_field)

# Add pixels (for snake segments and food)
for x in range(GRID_WIDTH):
    for y in range(GRID_HEIGHT):
        # Build object
        pixel = PIXEL_OBJ
        pixel = pixel.replace("###IDX###", f"{obj_idx_ctr} 0")
        # Green color for snake segments - they'll be hidden initially
        c = [0, 0.6, 0]
        pixel = pixel.replace("###COLOR###", f"{c[0]} {c[1]} {c[2]}")
        pixel = pixel.replace("###RECT###", f"{GRID_OFF_X+x*PX_SIZE} {GRID_OFF_Y+y*PX_SIZE} {GRID_OFF_X+x*PX_SIZE+PX_SIZE} {GRID_OFF_Y+y*PX_SIZE+PX_SIZE}")
        pixel = pixel.replace("###X###", f"{x}")
        pixel = pixel.replace("###Y###", f"{y}")

        add_field(pixel)

def add_button(label, name, x, y, width, height, js):
    script = STREAM_OBJ
    script = script.replace("###IDX###", f"{obj_idx_ctr} 0")
    script = script.replace("###CONTENT###", js)
    add_field(script)

    ap_stream = BUTTON_AP_STREAM
    ap_stream = ap_stream.replace("###IDX###", f"{obj_idx_ctr} 0")
    ap_stream = ap_stream.replace("###TEXT###", label)
    ap_stream = ap_stream.replace("###WIDTH###", f"{width}")
    ap_stream = ap_stream.replace("###HEIGHT###", f"{height}")
    add_field(ap_stream)

    button = BUTTON_OBJ
    button = button.replace("###IDX###", f"{obj_idx_ctr} 0")
    button = button.replace("###SCRIPT_IDX###", f"{obj_idx_ctr-2} 0")
    button = button.replace("###AP_IDX###", f"{obj_idx_ctr-1} 0")
    button = button.replace("###LABEL###", label)
    button = button.replace("###NAME###", name if name else f"B_{obj_idx_ctr}")
    button = button.replace("###RECT###", f"{x} {y} {x + width} {y + height}")
    add_field(button)

def add_text(label, name, x, y, width, height, js):
    script = STREAM_OBJ
    script = script.replace("###IDX###", f"{obj_idx_ctr} 0")
    script = script.replace("###CONTENT###", js)
    add_field(script)

    text = TEXT_OBJ
    text = text.replace("###IDX###", f"{obj_idx_ctr} 0")
    text = text.replace("###SCRIPT_IDX###", f"{obj_idx_ctr-1} 0")
    text = text.replace("###LABEL###", label)
    text = text.replace("###NAME###", name)
    text = text.replace("###RECT###", f"{x} {y} {x + width} {y + height}")
    add_field(text)


# Add direction buttons - with updated positions moved lower
add_button("LEFT", "B_left", GRID_OFF_X + 0, GRID_OFF_Y - 150, 50, 50, "moveLeft();")
add_button("RIGHT", "B_right", GRID_OFF_X + 110, GRID_OFF_Y - 150, 50, 50, "moveRight();")
add_button("UP", "B_up", GRID_OFF_X + 55, GRID_OFF_Y - 100, 50, 50, "moveUp();")
add_button("DOWN", "B_down", GRID_OFF_X + 55, GRID_OFF_Y - 200, 50, 50, "moveDown();")

# Add start button
add_button("Start Snake Game", "B_start", GRID_OFF_X + (GRID_WIDTH*PX_SIZE)/2-75, GRID_OFF_Y + (GRID_HEIGHT*PX_SIZE)/2-25, 150, 50, "game_init();")

# Add keyboard input
add_text("Type here for keyboard controls (WASD)", "T_input", GRID_OFF_X + 0, GRID_OFF_Y - 250, GRID_WIDTH*PX_SIZE, 40, "handle_input(event);")

# Add score display
add_text("Score: 0", "T_score", GRID_OFF_X + GRID_WIDTH*PX_SIZE+10, GRID_OFF_Y + GRID_HEIGHT*PX_SIZE-50, 100, 50, "")

# Fill in template
filled_pdf = PDF_FILE_TEMPLATE.replace("###FIELDS###", fields_text)
filled_pdf = filled_pdf.replace("###FIELD_LIST###", " ".join([f"{i} 0 R" for i in field_indexes]))
filled_pdf = filled_pdf.replace("###GRID_WIDTH###", f"{GRID_WIDTH}")
filled_pdf = filled_pdf.replace("###GRID_HEIGHT###", f"{GRID_HEIGHT}")

# Write to file with explicit encoding
with open("snakeGame.pdf", "w", encoding="utf-8") as pdffile:
    pdffile.write(filled_pdf)

print("Snake game PDF created as 'snakeGame.pdf'")