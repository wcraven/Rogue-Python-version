import random
import curses
import time

# Constants
DUNGEON_WIDTH = 20
DUNGEON_HEIGHT = 10
ROOM_MIN_SIZE = 5
ROOM_MAX_SIZE = 10
HALLWAY_WIDTH = 5
PLAYER_HEALTH = 100
PLAYER_ATTACK = 10
PLAYER_DEFENSE = 5
MONSTER_TYPES = {
    'Goblin': {'health': 20, 'attack': 5, 'defense': 2},
    'Kestral': {'health': 40, 'attack': 15, 'defense': 5},
    'Snake': {'health': 60, 'attack': 20, 'defense': 10},
    'Dragon': {'health': 100, 'attack': 30, 'defense': 20},
    'Blob': {'health': 25, 'attack': 8, 'defense': 3}
}
ITEM_TYPES = ['potion_heal', 'weapon_sword', 'armor_shield', 'scroll_identity', 'food_ration', 'magic_ring', 'gold_coin']
POTION_TYPES = ['potion_heal', 'potion_attack', 'potion_defense']
SCROLL_TYPES = ['scroll_heal', 'scroll_attack', 'scroll_defense']
MAX_INVENTORY = 10
LEVEL_UP_EXP = 100  # Experience required to level up

# Player stats
class Player:
    def __init__(self):
        self.x = 2
        self.y = 2
        self.health = PLAYER_HEALTH
        self.attack_damage = PLAYER_ATTACK
        self.defense = PLAYER_DEFENSE
        self.level = 1
        self.exp = 0
        self.inventory = []
        self.max_health = PLAYER_HEALTH

    def pick_up_item(self, item):
        if len(self.inventory) < MAX_INVENTORY:
            self.inventory.append(item)
            return True
        return False

    def gain_exp(self, amount):
        self.exp += amount
        if self.exp >= LEVEL_UP_EXP:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.exp = 0
        self.max_health += 20  # Increase health on level-up
        self.health = self.max_health
        self.attack_damage += 5  # Increase attack damage on level-up
        self.defense += 2  # Increase defense on level-up

    def use_item(self, index, stdscr):
        item = self.inventory[index]
        if item.name.startswith("potion"):
            if item.name == 'potion_heal':
                self.health += 20
                stdscr.addstr(DUNGEON_HEIGHT + 2, 0, "You used a healing potion! Health restored.")
            elif item.name == 'potion_attack':
                self.attack_damage += 5
                stdscr.addstr(DUNGEON_HEIGHT + 2, 0, "You used an attack potion! Attack increased.")
            elif item.name == 'potion_defense':
                self.defense += 5
                stdscr.addstr(DUNGEON_HEIGHT + 2, 0, "You used a defense potion! Defense increased.")
        elif item.name.startswith("scroll"):
            if item.name == 'scroll_heal':
                self.health += 30
                stdscr.addstr(DUNGEON_HEIGHT + 2, 0, "You used a healing scroll! Health restored.")
            elif item.name == 'scroll_attack':
                self.attack_damage += 10
                stdscr.addstr(DUNGEON_HEIGHT + 2, 0, "You used an attack scroll! Attack increased.")
            elif item.name == 'scroll_defense':
                self.defense += 10
                stdscr.addstr(DUNGEON_HEIGHT + 2, 0, "You used a defense scroll! Defense increased.")
        # Remove the item after use
        self.inventory.remove(item)

    def open_inventory(self, stdscr):
        while True:
            stdscr.clear()
            stdscr.addstr(0, 0, "Inventory:")
            if not self.inventory:
                stdscr.addstr(1, 0, "Your inventory is empty.")
            else:
                for index, item in enumerate(self.inventory, start=1):
                    stdscr.addstr(index, 0, f"{index}. {item.name}")
            stdscr.addstr(len(self.inventory) + 2, 0, "Press the number of an item to select it, or 'i' to close...")
            stdscr.refresh()
            key = stdscr.getch()
            if key == ord('i'):
                break
            elif key in range(ord('1'), ord('1') + len(self.inventory)):
                selected_index = key - ord('1')
                self.use_item(selected_index, stdscr)

# Monster class
class Monster:
    def __init__(self, monster_type, x, y):
        self.type = monster_type
        self.health = MONSTER_TYPES[monster_type]['health']
        self.attack = MONSTER_TYPES[monster_type]['attack']
        self.defense = MONSTER_TYPES[monster_type]['defense']
        self.x = x
        self.y = y

    def attack_player(self, player):
        damage = max(0, self.attack - player.defense)
        player.health -= damage

# Item class
class Item:
    def __init__(self, item_type, x, y):
        self.type = item_type
        self.name = item_type
        self.x = x
        self.y = y

# Room class
class Room:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def center(self):
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        return (center_x, center_y)

# Dungeon class
class Dungeon:
    def __init__(self):
        self.grid = [['#' for _ in range(DUNGEON_WIDTH)] for _ in range(DUNGEON_HEIGHT)]  # Set walls initially
        self.rooms = []
        self.monsters = []
        self.items = []
        self.generate_dungeon()

    def generate_dungeon(self):
        for _ in range(4):  # Four rooms
            while True:
                w = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
                h = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)

                # Ensure the room size fits within the dungeon grid.
                max_x = DUNGEON_WIDTH - w - 1
                max_y = DUNGEON_HEIGHT - h - 1

                if max_x > 0 and max_y > 0:
                    x = random.randint(1, max_x)
                    y = random.randint(1, max_y)
                    new_room = Room(x, y, w, h)

                    if self.is_valid_room(new_room):
                        self.create_room(new_room)
                        if self.rooms:
                            prev_center = self.rooms[-1].center()
                            new_center = new_room.center()
                            self.create_hallway(prev_center, new_center)
                        self.rooms.append(new_room)
                        break
                        
        self.spawn_monsters()
        self.spawn_items()

    def is_valid_room(self, room):
        """Ensure that rooms don't overlap and walls are respected."""
        for y in range(room.y, room.y + room.height):
            for x in range(room.x, room.x + room.width):
                if self.grid[y][x] == '#':  # Check if wall exists where room should be
                    return False
        return True

    def spawn_monsters(self):
        for _ in range(5):
            monster_type = random.choice(list(MONSTER_TYPES.keys()))
            while True:
                mx, my = random.randint(1, DUNGEON_WIDTH - 2), random.randint(1, DUNGEON_HEIGHT - 2)
                if self.grid[my][mx] == '#':  # Check only open spaces (hallways)
                    self.monsters.append(Monster(monster_type, mx, my))
                    break

    def spawn_items(self):
        for _ in range(5):  # Let's spawn 5 items
            item_type = random.choice(ITEM_TYPES)
            while True:
                ix, iy = random.randint(1, DUNGEON_WIDTH - 2), random.randint(1, DUNGEON_HEIGHT - 2)
                if self.grid[iy][ix] == '#':  # Check only open spaces (hallways)
                    self.items.append(Item(item_type, ix, iy))
                    break

    def create_room(self, room):
        for y in range(room.y, room.y + room.height):
            for x in range(room.x, room.x + room.width):
                self.grid[y][x] = '.'  # Empty floor for room

    def create_hallway(self, start, end):
        x1, y1 = start
        x2, y2 = end
        if random.choice([True, False]):
            self.create_horiz_hallway(x1, x2, y1)
            self.create_vert_hallway(y1, y2, x2)
        else:
            self.create_vert_hallway(y1, y2, x1)
            self.create_horiz_hallway(x1, x2, y2)

    def create_horiz_hallway(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.grid[y][x] = '#'  # Hallway floor

    def create_vert_hallway(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.grid[y][x] = '#'  # Hallway floor

    def render(self, stdscr, player):
        stdscr.clear()
        for y in range(DUNGEON_HEIGHT):
            line = ''
            for x in range(DUNGEON_WIDTH):
                if (x, y) == (player.x, player.y):
                    line += '@'
                else:
                    if self.grid[y][x] == '#':  # Hallway floor
                        line += '#'
                    elif self.grid[y][x] == '.':  # Empty space (open floor)
                        line += '.'
                    elif self.grid[y][x] == '+':  # Doors
                        line += '+'
                    elif self.grid[y][x] == '|':  # Walls
                        line += '|'
            stdscr.addstr(y, 0, line)
        stdscr.addstr(DUNGEON_HEIGHT, 0, f"Level: {player.level} Health: {player.health} Attack: {player.attack_damage} Defense: {player.defense} EXP: {player.exp}/{LEVEL_UP_EXP}")
        stdscr.refresh()

    def handle_combat(self, player):
        for monster in self.monsters:
            if (player.x, player.y) == (monster.x, monster.y):
                monster.attack_player(player)
                player.gain_exp(20)
                if player.health <= 0:
                    return False
        return True

# Help menu
def show_help(stdscr):
    stdscr.clear()
    stdscr.addstr(0, 0, "Game Instructions:")
    stdscr.addstr(1, 0, "Move with arrow keys")
    stdscr.addstr(2, 0, "Press 'i' to open your inventory")
    stdscr.addstr(3, 0, "Press 'q' to quit")
    stdscr.addstr(4, 0, "Press 'r' to use a healing potion in your inventory")
    stdscr.addstr(5, 0, "Press 'f' to fight monsters")
    stdscr.refresh()
    stdscr.getch()

def main(stdscr):
    player = Player()
    dungeon = Dungeon()

    while True:
        dungeon.render(stdscr, player)
        key = stdscr.getch()

        if key == ord('q'):
            break
        elif key == ord('i'):
            player.open_inventory(stdscr)
        elif key == ord('h'):
            show_help(stdscr)

        # Handle movement (WASD or Arrow keys)
        if key == curses.KEY_UP and player.y > 0:
            player.y -= 1
        elif key == curses.KEY_DOWN and player.y < DUNGEON_HEIGHT - 1:
            player.y += 1
        elif key == curses.KEY_LEFT and player.x > 0:
            player.x -= 1
        elif key == curses.KEY_RIGHT and player.x < DUNGEON_WIDTH - 1:
            player.x += 1

        # Handle combat
        if not dungeon.handle_combat(player):
            stdscr.addstr(DUNGEON_HEIGHT + 2, 0, "You have been defeated!")
            stdscr.refresh()
            time.sleep(2)
            break

curses.wrapper(main)
