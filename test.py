import wikipediaapi
import curses
import random

wiki_wiki = wikipediaapi.Wikipedia('en')
next_link = 'Python_(programming_language)'

KEY_ESC = 27

def getString():
    global next_link
    page_py = wiki_wiki.page(next_link)
    next_link, v = random.choice(list(page_py.links.items()))
    return page_py.title + " " + page_py.summary

# start
stdscr = curses.initscr()
height, width = stdscr.getmaxyx()
tw = min(70, width)
leftMargin = 4

# terminal settings
curses.noecho()
curses.cbreak()
stdscr.keypad(True)
stdscr.clear()

# Prepare string
text = getString()
# TODO: Remove double spaces, add space after .
text = text.replace('\n', " ")
lines = []
line = ""
for c in text:
    line += c
    if len(line) > tw or (len(line) > tw * 0.90 and c == ' '):
        lines.append(line)
        line = ""

# print string
for i in range(0, min(height, len(lines))):
    stdscr.addstr(i, leftMargin, lines[i])

def setCursor(y, x):
    global stdscr, curses, leftMargin, lines
    c = lines[y][x]
    stdscr.addstr(y, leftMargin + x, lines[y][x], curses.A_REVERSE)
    x -= 1
    if x < 0 and y > 0:
        y -= 1
        x = len(lines[y]) - 1

    if y >= 0:
        stdscr.addstr(y, leftMargin + x, lines[y][x])
    return c

setCursor(0, 0)

# input loop
x = 0
y = 0
currentChar = lines[0][0]

mistakes = 0
charsTyped = 0
while True:
    # TODO: accuracy and wpm
    stdscr.addstr(height - 1, 0, "Chars: " + str(charsTyped) + " Mistakes: " + str(mistakes))

    c = stdscr.getch()
    if c == KEY_ESC:
        break

    if chr(c) != currentChar:
        mistakes += 1
        # TODO: Add error mode: Still offset cursor, but
        # draw red and expect backspaces
        continue

    x = x + 1
    if x >= len(lines[y]):
        x = 0
        y += 1

    currentChar = setCursor(y, x)
    charsTyped += 1
    # TODO: End of text > next text
    # TODO: Shortcut to go to next article

# end
curses.nocbreak()
stdscr.keypad(0)
curses.echo()
curses.endwin()

print(c)

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

