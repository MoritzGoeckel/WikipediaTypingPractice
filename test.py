import wikipediaapi
import curses
import random
import math
import sys

wikiAPI = wikipediaapi.Wikipedia('en')

# Keys
KEY_ESC = 27
KEY_BACKSP = 263
KEY_F5 = 269
KEY_F1 = 265

# Colors
C_RED = 1
C_YELLOW = 2

# Signals
GO_TO_LINK_SELECTION = 0
GO_TO_LINK_ENTRY = 1
GO_TO_EXIT = 2
GO_TO_HELP = 3
GO_TO_STATISTICS = 4

def getString(link):
    global wikiAPI
    page_py = wikiAPI.page(link)
    links = page_py.links.items()

    text = page_py.title + "\n\n" + page_py.summary

    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")

    while "  " in text:
        text = text.replace("  ", " ")

    # links is tuple, we only need first
    return text, [link[0] for link in links]

def splitIntoLines(text, textWidth):
    lines = []
    linesMeta = []
    line = ""
    lineMeta = []
    for c in text:
        if c != '\n':
            line += c
            lineMeta.append(' ')
        if len(line) > textWidth or (len(line) > textWidth * 0.90 and c == ' ') or c == '\n':
            lines.append(line)
            linesMeta.append(lineMeta)
            line = ""
            lineMeta = []

    return lines, linesMeta

def startup():
    global stdscr, C_RED, C_YELLOW
    curses.start_color()
    curses.init_pair(C_RED, curses.COLOR_BLACK, curses.COLOR_RED)
    curses.init_pair(C_YELLOW, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    stdscr.clear()

def writeTextLines(number):
    global stdscr, height, topMargin, leftMargin
    for i in range(0, number):
        stdscr.addstr(i + topMargin, leftMargin, lines[i])

def advanceCursor(y, x):
    global stdscr, leftMargin, topMargin, lines, meta, C_RED, C_YELLOW

    # skip empty lines
    while len(lines[y]) == 0:
        y += 1

    c = lines[y][x]
    stdscr.addstr(y + topMargin, leftMargin + x, lines[y][x], curses.A_REVERSE)

    # Redraw one char before
    x -= 1
    if x < 0:
        y -= 1
        while len(lines[y]) == 0: # Skip empty lines
            y -= 1

        x = len(lines[y]) - 1
        if y < 0:
            return c # Do nothing, start of file

    if meta[y][x] == 'o' or meta[y][x] == ' ': # No meta info
        stdscr.addstr(topMargin + y, leftMargin + x, lines[y][x])
    elif meta[y][x] == 'e': # Mistake
        stdscr.addstr(topMargin + y, leftMargin + x, lines[y][x], curses.color_pair(C_RED))
    elif meta[y][x] == 'c': # Corrected
        stdscr.addstr(topMargin + y, leftMargin + x, lines[y][x], curses.color_pair(C_YELLOW))

    return c

def setbackCursor(y, x):
    global stdscr, leftMargin, topMargin, lines, meta, C_YELLOW

    c = lines[y][x]
    stdscr.addstr(topMargin + y, leftMargin + x, lines[y][x], curses.A_REVERSE)

    # Redraw one char after
    x += 1
    if x > len(lines[y]) - 1:
        x = 0
        y += 1
        while len(lines[y]) == 0: # Skip empty lines
            y += 1
        if y >= len(lines):
            return c # Do nothing, end of file

    if meta[y][x] == 'c' or meta[y][x] == 'e': # Corrected
        stdscr.addstr(topMargin + y, leftMargin + x, lines[y][x], curses.color_pair(C_YELLOW))
    else:
        stdscr.addstr(topMargin + y, leftMargin + x, lines[y][x])

    return c

def shutdown():
    global stdscr
    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()
    sys.exit(0)

def handleTypingScreen(link):
    global stdscr, height, width, leftMargin, topMargin, lines, meta, C_YELLOW

    text, links = getString(link)
    lines, meta = splitIntoLines(text, textWidth)

    lineCount = min(height - topMargin * 3, len(lines))

    stdscr.clear()
    writeTextLines(lineCount)
    advanceCursor(0, 0)

    x = 0
    y = 0
    currentChar = lines[0][0]
    c = chr(80)

    mistakes = 0
    correct = 0

    while True:
        # Debug
        # stdscr.addstr(height - 1, leftMargin, "Typed: " + str(correct) + " Mistakes: " + str(mistakes) + " Last: " + str(c) + " Current: " + currentChar + "              ")

        infoBarY = lineCount + topMargin + 2

        infoStr = "Correct: " + str(correct).ljust(4)
        infoStr += " Mistakes: " + str(mistakes).ljust(3)
        infoStr += " Accuracy: " + (str(round((correct / max(1, correct + mistakes)) * 100.0, 2)) + "% ").ljust(7)
        infoStr += " WPM: " + "XXX".ljust(3)

        stdscr.addstr(infoBarY, leftMargin, infoStr)

        c = stdscr.getch()
        if c == KEY_ESC:
            return 0, GO_TO_EXIT

        if c == KEY_F5:
            return links, GO_TO_LINK_SELECTION

        if c == KEY_F1:
            return links, GO_TO_HELP

        elif c == KEY_BACKSP:
            x = x - 1

            if x < 0 and y > 0:
                y -= 1
                while len(lines[y]) == 0: # Skip empty lines
                    y -= 1
                x = len(lines[y]) - 1

            if x < 0 and y == 0:
                x = 0

            #if meta[y][x] == 'o':
            #    meta[y][x] = ' ' # Undo the Okay

            currentChar = setbackCursor(y, x)
            continue

        elif chr(c) == currentChar:
            if meta[y][x] == ' ':
                correct += 1
                # We only count the ones that
                # got typed correct the first time

            if meta[y][x] == 'e' or meta[y][x] == 'c':
                meta[y][x] = 'c'  # Corrected
            else:
                meta[y][x] = 'o'  # Okay

        elif chr(c) != currentChar:
            mistakes += 1
            meta[y][x] = 'e' # Mistake

        # TODO: Refactor, nextCord, prevCord methods
        x += 1
        if x >= len(lines[y]):
            x = 0
            y += 1
            while y < len(lines) and len(lines[y]) == 0: # Skip empty lines
                y += 1
            if y >= lineCount:
                return links, GO_TO_LINK_SELECTION

        currentChar = advanceCursor(y, x)
        #stdscr.refresh()

def handleLinkSelectionScreen(links):
    stdscr.clear()
    stdscr.addstr(topMargin, leftMargin, "Select next:")

    rand_links = random.sample(links, 10)
    i = 0
    while i < min(10, len(rand_links)):
        stdscr.addstr(topMargin + 2 + i, leftMargin, "[" + str(i) + "] " + rand_links[i])
        i += 1
    stdscr.addstr(topMargin + 3 + i, leftMargin, "[x] Reroll")

    while True:
        c = stdscr.getch()
        if c == KEY_ESC:
            shutdown()
        elif chr(c) >= '0' and chr(c) <= '9':
            return rand_links[int(chr(c))]
        elif chr(c) == 'x':
            return handleLinkSelectionScreen(links)


# Not implemented yet, is also never called
def handleLinkEntryScreen():
    stdscr.clear()
    return "Python_(programming_language)"

def handleHelpScreen():
    stdscr.clear()
    stdscr.addstr(topMargin, leftMargin,     "Commands:")
    stdscr.addstr(topMargin + 2, leftMargin, "F1    Help")
    stdscr.addstr(topMargin + 3, leftMargin, "F5    Next page")
    stdscr.addstr(topMargin + 4, leftMargin, "ESC   Exit")
    stdscr.addstr(topMargin + 6, leftMargin, "Press any key to continue...")
    stdscr.getch()
    return

# Main starts here
stdscr = curses.initscr()

height, width = stdscr.getmaxyx()
textWidth = min(50, width)
leftMargin = math.floor((width - textWidth) / 2)
topMargin = min(4, math.floor(leftMargin / 6))
link = "Python_(programming_language)"
startup()

while True:
    links, signal = handleTypingScreen(link)
    if signal == GO_TO_LINK_SELECTION:
        link = handleLinkSelectionScreen(links)
    elif signal == GO_TO_LINK_ENTRY:
        link = handleLinkEntryScreen(links)
    elif signal == GO_TO_HELP:
        handleHelpScreen()
    elif signal == GO_TO_EXIT:
        break

shutdown()

# TODO: Shortcut to search for article
# TODO: Stop text with last period (.)
# TODO: Properly break lines at word end
# TODO: Let continue with article (second page)
# TODO: Record WPM (total, last 10 sec, last 30 sec)
# TODO: Save stats in file (also total time practiced)

# print(c)

#print("Page - Title: %s" % page_py.title)
#print("Page - Summary: %s" % page_py.summary)
#for l in page_py.links:
#    print(l)

# Full text
#wikiAPI = wikipediaapi.Wikipedia(language='en',
#    extract_format=wikipediaapi.ExtractFormat.WIKI)
#
#p_wiki = wikiAPI.page("Test 1")
#print(p_wiki.text)

