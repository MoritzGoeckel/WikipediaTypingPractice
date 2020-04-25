# Practice typing on Wikipedia

This is a simple typing game where you improve your accuracy and typing speed by typing wikipedia articles. After you are done with a page, you get some related articles suggested, so you can choose which one to write next. The idea is to practice typing while learning something about the world.

## Features

- [x] Type articles from wikipedia
- [x] Correct mistakes by using backspace
- [x] Displays accuracy
- [x] Displays word per minute
- [x] Choose related article as next exercise
- [x] Press F5 to choose next article
- [x] Press F1 for help
- [x] Press ESC to exit
- [ ] Store historical statistics in file
- [ ] Search unrelated article

## Tech

The program is 100% terminal based and written in `python3`. The only dependency is the `wikipedia-api` library which can be installed using `pip3`.

## Show it!

![Screenshot](/typing_screenshot.PNG)

This is a screenshot of the typing screen. Characters that you got wrong are marked as red, characters which you corrected will stay marked as yellow. The inverted bar is your cursor. At the bottom some statistics about speed and accuracy are displayed.
