import wikipediaapi
import curses
import random
import math
import sys

wiki_wiki = wikipediaapi.Wikipedia('en')
next_link = 'Python_(programming_language)'

KEY_ESC = 27
KEY_BACKSP = 263

C_RED = 1
C_YELLOW = 2

def getString():
    global next_link
    page_py = wiki_wiki.page(next_link)
    next_link, v = random.choice(list(page_py.links.items()))

    text = page_py.title + "\n\n" + page_py.summary

    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")

    while "  " in text:
        text = text.replace("  ", " ")

    #text = text.replace(".", ". ")

    return text

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

# start
stdscr = curses.initscr()

height, width = stdscr.getmaxyx()
textWidth = min(50, width)
leftMargin = math.floor((width - textWidth) / 2)
topMargin = math.floor(leftMargin / 6)

# print("width=%d height=%d textWidth=%d leftMargin=%d topMargin=%d" % (width, height, textWidth, leftMargin, topMargin))

curses.start_color()
curses.init_pair(C_RED, curses.COLOR_BLACK, curses.COLOR_RED)
curses.init_pair(C_YELLOW, curses.COLOR_BLACK, curses.COLOR_YELLOW)

# terminal settings
curses.noecho()
curses.cbreak()
stdscr.keypad(True)
stdscr.clear()

# Prepare string
text = getString()
lines, meta = splitIntoLines(text, textWidth)

# print string
for i in range(0, min(height - topMargin, len(lines))):
    stdscr.addstr(i + topMargin, leftMargin, lines[i])

def advanceCursor(y, x):
    global stdscr, curses, leftMargin, topMargin, lines, meta

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
    global stdscr, curses, leftMargin, topMargin, lines, meta

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

advanceCursor(0, 0)

# input loop
x = 0
y = 0
currentChar = lines[0][0]
c = chr(80)

mistakes = 0
correct = 0
charsTyped = 0

while True:
    # TODO: accuracy and wpm
    stdscr.addstr(height - 1, leftMargin, "Typed: " + str(charsTyped) + " Mistakes: " + str(mistakes) + " Last: " + str(c) + " Current: " + currentChar)

    c = stdscr.getch()
    if c == KEY_ESC:
        break

    elif c == KEY_BACKSP:
        x = x - 1

        if x < 0 and y > 0:
            y -= 1
            while len(lines[y]) == 0: # Skip empty lines
                y -= 1
            x = len(lines[y]) - 1

        if x < 0 and y == 0:
            x = 0

        if meta[y][x] == 'o':
            meta[y][x] = ' ' # Undo the Okay

        currentChar = setbackCursor(y, x)
        continue

    elif chr(c) == currentChar:
        correct += 1
        if meta[y][x] == 'e' or meta[y][x] == 'c':
            meta[y][x] = 'c'  # Corrected
        else:
            meta[y][x] = 'o'  # Okay

    elif chr(c) != currentChar:
        mistakes += 1
        meta[y][x] = 'e' # Mistake

    charsTyped += 1

    # TODO: Refactor, nextCord, prevCord methods
    x += 1
    if x >= len(lines[y]):
        x = 0
        y += 1
        while len(lines[y]) == 0: # Skip empty lines
            y += 1

    currentChar = advanceCursor(y, x)

    #stdscr.refresh()
    # TODO: End of text > next text
    # TODO: Shortcut to go to next article
    # TODO: Shortcut to search for article
    # TODO: Choose links?

# end
curses.nocbreak()
stdscr.keypad(0)
curses.echo()
curses.endwin()

# print(c)

#print("Page - Title: %s" % page_py.title)
#print("Page - Summary: %s" % page_py.summary)
#for l in page_py.links:
#    print(l)

# Full text
#wiki_wiki = wikipediaapi.Wikipedia(language='en',
#    extract_format=wikipediaapi.ExtractFormat.WIKI)
#
#p_wiki = wiki_wiki.page("Test 1")
#print(p_wiki.text)

