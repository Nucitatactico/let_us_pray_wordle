from pyscript import document


# Datos del juego
WORDS = [
    {
        "word": "DRILLING",
        "description": "The process of tactically and intensely interrogating, pressuring, "
                       "or harassing a suspect to extract information or subdue them."
    },
    {
        "word": "YAHOO BOYS",
        "description": "Colloquial term for young individuals involved in cybercrime, "
                       "online scams, and internet fraud."
    },
    {
        "word": "GO PUNISH",
        "description": "Emphatic expression of warning or threat that predicts negative "
                       "consequences or moral punishment for someone."
    },
    {
        "word": "CATCH AND TRANSFER",
        "description": "Method of extortion or quick street transaction that seeks to demand "
                       "cash payments or instant transfers after a detention."
    },
    {
        "word": "SHOUTING",
        "description": "Act of issuing orders or shouting loudly from a distance to try to "
                       "stop or intimidate a suspect."
    },
    {
        "word": "NIGERIAN PIDGIN",
        "description": "Linguistic variety and creole dialect that combines English with local "
                       "languages for informal daily communication."
    },
    {
        "word": "NAIRA",
        "description": "Currency of Nigeria."
    },
]

MAX_ATTEMPTS = 6


# Estado
current_index = 0
attempts = []


# Helpers
def el(element_id):
    return document.getElementById(element_id)


def build_board(target):
    board = el("wordle-board")
    board.innerHTML = ""

    cell_size = max(24, min(42, 540 // len(target)))

    for row_idx in range(MAX_ATTEMPTS):
        row = document.createElement("div")
        row.className = "wordle-row"
        for col_idx in range(len(target)):
            cell = document.createElement("div")
            cell.className = "wordle-cell"
            cell.id = f"cell-{row_idx}-{col_idx}"
            cell.style.width = f"{cell_size}px"
            cell.style.height = f"{cell_size}px"
            cell.style.fontSize = f"{max(0.7, cell_size / 45)}rem"
            row.appendChild(cell)
        board.appendChild(row)


def compute_feedback(guess, target):
    result = [None] * len(target)
    remaining = list(target)

    for i in range(len(target)):
        if guess[i] == target[i]:
            result[i] = "green"
            remaining[i] = None

    for i in range(len(target)):
        if result[i] is None:
            if guess[i] in remaining:
                result[i] = "yellow"
                remaining[remaining.index(guess[i])] = None
            else:
                result[i] = "gray"

    return result


# Ciclo de juego
def init_game():
    global attempts
    attempts = []

    word_data = WORDS[current_index]
    target = word_data["word"].upper()

    build_board(target)

    el("description-text").innerText = word_data["description"]

    message_el = el("message")
    message_el.innerText = ""
    message_el.className = "message"

    input_el = el("guess-input")
    input_el.value = ""
    input_el.disabled = False
    input_el.focus()
    el("guess-btn").disabled = False


def handle_keydown(event):
    if event.key == "Enter" and not event.repeat:
        submit_guess()


def submit_guess(*args, **kwargs):
    if len(attempts) >= MAX_ATTEMPTS:
        return

    input_el = el("guess-input")
    guess = input_el.value.strip().upper()
    target = WORDS[current_index]["word"].upper()

    if not guess:
        el("message").innerText = "Please enter a guess."
        return

    if len(guess) != len(target):
        el("message").innerText = f"Guess must be {len(target)} characters long."
        return

    feedback = compute_feedback(guess, target)
    row_idx = len(attempts)

    for i, status in enumerate(feedback):
        cell = el(f"cell-{row_idx}-{i}")
        cell.innerText = guess[i]
        cell.className = f"wordle-cell {status}"

    attempts.append(guess)
    input_el.value = ""

    if guess == target:
        finish_word(won=True)
    elif len(attempts) >= MAX_ATTEMPTS:
        finish_word(won=False)
    else:
        remaining = MAX_ATTEMPTS - len(attempts)
        el("message").innerText = f"Incorrect. {remaining} attempts left."


def finish_word(won):
    """Punto único de salida: victoria o derrota. Nunca mezcla mensajes."""
    input_el = el("guess-input")
    input_el.disabled = True
    el("guess-btn").disabled = True

    target = WORDS[current_index]["word"]
    is_last = current_index >= len(WORDS) - 1

    if won is True:
        message_el = el("message")
        message_el.innerText = "Correct."
        message_el.className = "message win"

        if is_last:
            show_modal(
                mode="win",
                title="Congratulations",
                body="You have completed all words.",
            )
        else:
            show_modal(
                mode="win",
                title="Correct",
                body="You guessed the word. Ready for the next one?",
            )
    else:
        # ---------- DERROTA ----------
        message_el = el("message")
        message_el.innerText = f"Out of attempts. The word was: {target}"
        message_el.className = "message lose"

        if is_last:
            show_modal(
                mode="lose",
                title="End of game",
                body=f"Out of attempts. The word was: {target}",
            )
        else:
            show_modal(
                mode="lose",
                title="Out of attempts",
                body=f"The word was: {target}",
            )


# Modal
def show_modal(mode, title, body):
    el("modal-title").innerText = title
    el("modal-text").innerText = body

    is_last = current_index >= len(WORDS) - 1
    el("modal-btn").innerText = "Finish" if is_last else "Next word"

    # Buscar el contenedor del modal por id, con fallback a selector de clase
    content = el("modal-content")
    if content is None:
        content = document.querySelector(".modal-content")

    if content is not None:
        content.classList.remove("win")
        content.classList.remove("lose")
        content.classList.add(mode)

    el("modal").classList.remove("hidden")


def hide_modal():
    el("modal").classList.add("hidden")


def on_modal_click(*args, **kwargs):
    global current_index
    hide_modal()

    if current_index < len(WORDS) - 1:
        current_index += 1
        init_game()
    else:
        el("message").innerText = "Game complete. Refresh the page to play again."


# Arranque
init_game()
