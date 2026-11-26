"""tools/mechanics.py — tests of this game's mechanics (copy, then rewrite MECHANICS for the game).
npm script: "mechanics": "python3 tools/mechanics.py" · run: npm run mechanics -- --only clean_room"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))
from mechanics import run

# Example for a "run a motel" style game. Every field reads window.__game; adapt names to the game.
MECHANICS = [
    dict(name='clean_room',                                       # main action changes the world
         setup="const g = window.__game; g.reset(); g.teleport('room1_door');",
         act=[('hold', 'KeyE', 1500)],
         expect="window.__game.rooms[0].dirt === 0", timeout=6),
    dict(name='furnish_unlocks_after_clean',                      # reward of the action is visible
         expect="window.__game.ui.shopOpen || window.__game.rooms[0].canFurnish", timeout=3),
    dict(name='guest_pays',                                       # loop closes: result -> money
         setup="window.__game.rooms[0].placeBed();",
         act=[('wait', 1)],
         expect="window.__game.econ.cash > 0", timeout=20),
    dict(name='next_goal_visible',                                # the next goal is shown by the world
         expect="window.__game.funnel && window.__game.funnel.has('next_goal_seen')", timeout=10),
]

if __name__ == '__main__':
    run(MECHANICS)
