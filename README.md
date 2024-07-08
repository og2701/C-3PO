# C-3PO Bot

Welcome to the C-3PO Bot repository! This bot offers various Star Wars-related commands for a fun and interactive experience on Discord.

## File Structure

Here's an overview of the project structure:

```plaintext
├── funcs
│   ├── archive.py
│   ├── duel.py
│   ├── lightsaber.py
│   ├── quote.py
│   ├── sabacc.py
│   └── translate.py
├── lib
│   ├── classes.py
│   ├── commands.py
│   ├── sabacc_stats.py
│   ├── settings.py
│   └── utils.py
├── main.py
├── requirements.txt
├── resources
│   ├── Aurebesh.otf
│   ├── Neonmachine.ttf
│   ├── duel
│   │   ├── both.png
│   │   ├── left.png
│   │   ├── none.png
│   │   └── right.png
│   ├── lightsaber_parts
│   │   ├── Emitter
│   │   │   ├── 1.png
│   │   │   ├── ...
│   │   │   └── 6.png
│   │   ├── Hilt
│   │   │   ├── 1.png
│   │   │   ├── ...
│   │   │   └── 6.png
│   │   ├── Sleeve
│   │   │   ├── 1.png
│   │   │   ├── ...
│   │   │   └── 6.png
│   │   └── Switch
│   │   │   ├── 1.png
│   │   │   ├── ...
│   │   │   └── 6.png
│   └── quotes.txt
├── start.sh
```

## Using C-3PO in Discord

### Commands List

#### /archive
**Description:** Searches the Star Wars wiki for the specified query.

**Usage:** `/archive <query>`

**Example:** `/archive Luke Skywalker`

**Details:** This command retrieves information from the Star Wars wiki about the specified query and presents it in an embedded message format, including an image and a brief description.

---

#### /duel
**Description:** Initiates a duel between two users.

**Usage:** `/duel <@user>`

**Example:** `/duel @DarthVader`

**Details:** This command creates a duel image between the command user and the mentioned user. It randomly selects a winner and marks the winning position on the image.

---

#### /lightsaber
**Description:** Creates a custom lightsaber image.

**Usage:** `/lightsaber`

**Example:** `/lightsaber`

**Details:** Users can select different parts of a lightsaber (Emitter, Switch, Sleeve, Hilt) to create a custom lightsaber image. The selections are made through interactive buttons.

---

#### /quote
**Description:** Retrieves a random quote from the Star Wars films.

**Usage:** `/quote`

**Example:** `/quote`

**Details:** This command provides a random quote from the Star Wars movies and displays it in an embedded message format.

---

#### /sabacc
**Description:** Starts a game of Sabacc.

**Usage:** `/sabacc`

**Example:** `/sabacc`

**Details:** This command initiates a game of Sabacc with C-3PO. Users can draw cards or stand to play the game, and C-3PO manages the game state.

---

#### /translate
**Description:** Translates a given message to Aurebesh.

**Usage:** `/translate <message>`

**Example:** `/translate Hello there!`

**Details:** This command translates the input message to Aurebesh, the written language of the Star Wars universe, and presents it as an image.

---

## Notes
**Interactivity:** Some commands provide interactive buttons (e.g., `/lightsaber`, `/sabacc`). Ensure to follow the prompts and click the buttons to proceed with your choices.

**Embeds and Images:** C-3PO uses embedded messages and images to display results in a visually appealing manner.

**Game Management:** For the `/sabacc` command, C-3PO manages the game state and ensures a smooth gameplay experience.
