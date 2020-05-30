import textwrap
import wikipediaapi
import curses
import random
import math
import sys
from datetime import datetime
import argparse

wikiAPI = wikipediaapi.Wikipedia(language='en', extract_format=wikipediaapi.ExtractFormat.WIKI)
parser = argparse.ArgumentParser(description='Practice typing while reading Wikipedia articles')
parser.add_argument('--article',
                    type=str,
                    action='store',
                    metavar='name',
                    default="Python_(programming_language)",
                    help='Article to start with (optional)')

args = vars(parser.parse_args())

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

    text = page_py.title + "\n\n" + page_py.text # summary

    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")

    while "  " in text:
        text = text.replace("  ", " ")

    # links is tuple, we only need first
    return text, [link[0] for link in links]

def splitIntoLines(text, textWidth, lineOffset = 0):
    lines = []
    linesMeta = []

    line_breaker = textwrap.TextWrapper(width=textWidth)

    paragraphs = text.split('\n')

    for paragraph in paragraphs:
        if len(paragraph) == 0:
            lines.append("")
            linesMeta.append("")
        else:
            plines = line_breaker.wrap(paragraph)
            for line in plines:
                if len(line) > 0 and line[-1] != '-':
                    line += ' '
                lines.append(line)
                linesMeta.append([' '] * len(line))

    if len(lines) <= lineOffset:
        return [], []
    else:
        return lines[lineOffset:], linesMeta[lineOffset:]

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
        while len(lines[y]) == 0:
            # Skip empty lines
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

def handleTypingScreen(link, lineOffset):
    global stdscr, height, width, leftMargin, topMargin, lines, meta, C_YELLOW

    text, links = getString(link)
    lines, meta = splitIntoLines(text, textWidth, lineOffset)

    if len(lines) == 0:
        return links, GO_TO_LINK_SELECTION

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

    starting_time = datetime.now()

    while True:
        # Debug
        # stdscr.addstr(height - 1, leftMargin, "Typed: " + str(correct) + " Mistakes: " + str(mistakes) + " Last: " + str(c) + " Current: " + currentChar + "              ")

        infoBarY = lineCount + topMargin + 2

        time_on_page = datetime.now() - starting_time
        written_words = correct / 5.0
        wpm = (written_words / time_on_page.total_seconds()) * 60.0

        infoStr = "Correct: " + str(correct).ljust(4)
        infoStr += " Mistakes: " + str(mistakes).ljust(3)
        infoStr += " Accuracy: " + (str(round((correct / max(1, correct + mistakes)) * 100.0, 2)) + "% ").ljust(7)
        infoStr += " WPM: " + str(round(wpm, 2)).ljust(3)

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
                while len(lines[y]) == 0:
                    # Skip empty lines
                    y -= 1
                x = len(lines[y]) - 1

            if x < 0 and y == 0:
                x = 0

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
            while y < len(lines) and len(lines[y]) == 0:
                # Skip empty lines
                y += 1
            if y >= lineCount:
                # Go to next page
                return handleTypingScreen(link, lineOffset + lineCount)

        currentChar = advanceCursor(y, x)
        #stdscr.refresh()

def handleLinkSelectionScreen(links):
    stdscr.clear()
    stdscr.addstr(topMargin, leftMargin, "Select next:")

    rand_links = random.sample(links, min(10, len(links)))
    i = 0
    while i < min(10, len(rand_links)):
        stdscr.addstr(topMargin + 2 + i, leftMargin, "[" + str(i) + "] " + rand_links[i])
        i += 1

    if len(links) > 10:
        stdscr.addstr(topMargin + 3 + i, leftMargin, "[x] Reroll")

    while True:
        c = stdscr.getch()
        if c == KEY_ESC:
            shutdown()
        elif chr(c) >= '0' and chr(c) <= '9':
            return rand_links[int(chr(c))]
        elif chr(c) == 'x' and len(links) > 10:
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
textWidth = min(57, width)
leftMargin = math.floor((width - textWidth) / 2)
topMargin = min(4, math.floor(leftMargin / 6))
link = args['article']

startup()

while True:
    links, signal = handleTypingScreen(link, 0)
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
# TODO: Record WPM (total, last 10 sec, last 30 sec)
# TODO: Start on certain page of article
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

