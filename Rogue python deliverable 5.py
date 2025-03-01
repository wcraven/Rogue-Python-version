import random
import os
import time
import curses

# Constants for the dungeon dimensions
DUNGEON_WIDTH = 40
DUNGEON_HEIGHT = 20
ROOM_MIN_SIZE = 5  # Minimum room size
ROOM_MAX_SIZE = 10  # Maximum room size
HALLWAY_WIDTH = 5  # Width of the hallway

# Symbols for the grid
WALL = '|'
EMPTY = '.'
PLAYER = '@'
MONSTER = 'M'
ITEM = '*'
DOOR_CLOSED = '+'  # Closed door symbol
DOOR_OPEN = '/'  # Open door symbol
TRAP = 'T'
POTION_HEAL = 'H'
POTION_ATTACK = 'A'
POTION_DEFENSE = 'D'
SCROLL_HEAL = 'S'
SCROLL_ATTACK = 'F'
SCROLL_DEFENSE = 'G'
STAIRS_UP = '>'  # Upward stairs
STAIRS_DOWN = '<'  # Downward stairs

# Player stats
PLAYER_HEALTH = 100
PLAYER_ATTACK = 10
PLAYER_DEFENSE = 5

# Monster types with attributes
MONSTER_TYPES = {
    'Goblin': {'health': 20, 'attack': 5, 'defense': 2},
    'Orc': {'health': 40, 'attack': 15, 'defense': 5},
    'Troll': {'health': 60, 'attack': 20, 'defense': 10},
    'Dragon': {'health': 100, 'attack': 30, 'defense': 20},
    'Skeleton': {'health': 25, 'attack': 8, 'defense': 3}
}

# Direction map for player movement (arrows and h/j/k/l)
DIRECTION_MAP = {
    'h': (-1, 0),  # Left
    'j': (0, 1),   # Down
    'k': (0, -1),  # Up
    'l': (1, 0),   # Right
    curses.KEY_LEFT: (-1, 0),  # Left arrow
    curses.KEY_DOWN: (0, 1),  # Down arrow
    curses.KEY_UP: (0, -1),    # Up arrow
    curses.KEY_RIGHT: (1, 0),  # Right arrow
}

# Item types
ITEM_TYPES = ['potion_heal', 'weapon_sword', 'armor_shield', 'scroll_identity', 'food_ration', 'magic_ring', 'gold_coin']

# Potions and Scrolls
POTION_TYPES = ['potion_heal', 'potion_attack', 'potion_defense']
SCROLL_TYPES = ['scroll_heal', 'scroll_attack', 'scroll_defense']

# Player inventory size
MAX_INVENTORY = 10

class Item:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y
        if name == 'potion_heal':
            self.symbol = POTION_HEAL
        elif name == 'potion_attack':
            self.symbol = POTION_ATTACK
        elif name == 'potion_defense':
            self.symbol = POTION_DEFENSE
        elif name == 'scroll_heal':
            self.symbol = SCROLL_HEAL
        elif name == 'scroll_attack':
            self.symbol = SCROLL_ATTACK
        elif name == 'scroll_defense':
            self.symbol = SCROLL_DEFENSE
        else:
            self.symbol = ITEM

class Monster:
    def __init__(self, monster_type, x, y):
        self.type = monster_type
        self.health = MONSTER_TYPES[monster_type]['health']
        self.attack = MONSTER_TYPES[monster_type]['attack']
        self.defense = MONSTER_TYPES[monster_type]['defense']
        self.x = x
        self.y = y

    def move_randomly(self):
        dx, dy = random.choice(list(DIRECTION_MAP.values()))
        self.x = max(1, min(DUNGEON_WIDTH - 2, self.x + dx))
        self.y = max(1, min(DUNGEON_HEIGHT - 2, self.y + dy))

    def attack_player(self, player):
        damage = max(0, self.attack - player.defense)
        player.health -= damage

class Player:
    def __init__(self):
        self.x = 2
        self.y = 2
        self.health = PLAYER_HEALTH
        self.attack_damage = PLAYER_ATTACK
        self.defense = PLAYER_DEFENSE
        self.inventory = []

    def pick_up_item(self, item):
        if len(self.inventory) < MAX_INVENTORY:
            self.inventory.append(item)
            return True
        return False

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
                break

class Floor:
    def __init__(self, floor_number=0):
        self.grid = [[EMPTY for _ in range(DUNGEON_WIDTH)] for _ in range(DUNGEON_HEIGHT)]
        self.monsters = [Monster(random.choice(list(MONSTER_TYPES.keys())), random.randint(1, DUNGEON_WIDTH-2), random.randint(1, DUNGEON_HEIGHT-2)) for _ in range(5)]
        self.items = [Item(random.choice(ITEM_TYPES), random.randint(1, DUNGEON_WIDTH-2), random.randint(1, DUNGEON_HEIGHT-2)) for _ in range(5)]
        self.traps = [Item('trap', random.randint(1, DUNGEON_WIDTH-2), random.randint(1, DUNGEON_HEIGHT-2)) for _ in range(3)]
        self.potions = [Item(random.choice(POTION_TYPES), random.randint(1, DUNGEON_WIDTH-2), random.randint(1, DUNGEON_HEIGHT-2)) for _ in range(2)]
        self.scrolls = [Item(random.choice(SCROLL_TYPES), random.randint(1, DUNGEON_WIDTH-2), random.randint(1, DUNGEON_HEIGHT-2)) for _ in range(2)]
        self.stairs_up = None
        self.stairs_down = None
        self.door = None
        self.hallway = None  # Track if the player is in the hallway
        self.floor_number = floor_number
        self.room_doors = []  # Track the doors
        
        # Create rooms and hallways
        self.create_rooms_and_hallways()

    def create_rooms_and_hallways(self):
        # Randomize room positions and sizes
        num_rooms = 4
        rooms = []
        for _ in range(num_rooms):
            room_width = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
            room_height = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
            x1 = random.randint(1, DUNGEON_WIDTH - room_width - 1)
            y1 = random.randint(1, DUNGEON_HEIGHT - room_height - 1)
            x2 = x1 + room_width
            y2 = y1 + room_height
            rooms.append((x1, y1, x2, y2))

            # Fill room with empty spaces and walls
            for y in range(y1, y2):
                for x in range(x1, x2):
                    self.grid[y][x] = EMPTY
            for y in range(y1, y2):
                self.grid[y][x1] = WALL
                self.grid[y][x2-1] = WALL
            for x in range(x1, x2):
                self.grid[y1][x] = WALL
                self.grid[y2-1][x] = WALL

            # Add door to a random wall
            self.add_random_door(x1, y1, x2, y2)

        # Create hallways between rooms
        self.create_hallways_between_rooms(rooms)

    def add_random_door(self, x1, y1, x2, y2):
        # Pick a random wall and place a door
        wall_choice = random.choice(['top', 'bottom', 'left', 'right'])
        if wall_choice == 'top':
            x = random.randint(x1 + 1, x2 - 2)
            self.grid[y1][x] = DOOR_CLOSED
        elif wall_choice == 'bottom':
            x = random.randint(x1 + 1, x2 - 2)
            self.grid[y2-1][x] = DOOR_CLOSED
        elif wall_choice == 'left':
            y = random.randint(y1 + 1, y2 - 2)
            self.grid[y][x1] = DOOR_CLOSED
        elif wall_choice == 'right':
            y = random.randint(y1 + 1, y2 - 2)
            self.grid[y][x2-1] = DOOR_CLOSED

    def create_hallways_between_rooms(self, rooms):
        for i in range(len(rooms) - 1):
            # Get the door locations of two rooms
            x1, y1, x2, y2 = rooms[i]
            x3, y3, x4, y4 = rooms[i + 1]

            # For simplicity, create a hallway between the center of each room
            hallway_x1, hallway_y1 = (x1 + x2) // 2, (y1 + y2) // 2
            hallway_x2, hallway_y2 = (x3 + x4) // 2, (y3 + y4) // 2

            # Create vertical and horizontal corridors between rooms
            self.create_hallway(hallway_x1, hallway_y1, hallway_x2, hallway_y2)

    def create_hallway(self, x1, y1, x2, y2):
        # Create a hallway between two points
        if x1 == x2:
            for y in range(min(y1, y2), max(y1, y2) + 1):
                self.grid[y][x1] = EMPTY
        elif y1 == y2:
            for x in range(min(x1, x2), max(x1, x2) + 1):
                self.grid[y1][x] = EMPTY

    def update(self, player):
        for monster in self.monsters:
            monster.move_randomly()
            if (monster.x, monster.y) == (player.x, player.y):
                monster.attack_player(player)

    def place_stairs(self):
        if self.rooms:
            up_room = random.choice(self.rooms)
            down_room = random.choice(self.rooms)
            self.stairs_up = (random.randint(up_room[0] + 1, up_room[2] - 2), random.randint(up_room[1] + 1, up_room[3] - 2))
            self.stairs_down = (random.randint(down_room[0] + 1, down_room[2] - 2), random.randint(down_room[1] + 1, down_room[3] - 2))
            self.grid[self.stairs_up[1]][self.stairs_up[0]] = STAIRS_UP
            self.grid[self.stairs_down[1]][self.stairs_down[0]] = STAIRS_DOWN

    def print_dungeon(self, player, stdscr):
        for y in range(DUNGEON_HEIGHT):
            line = ''
            for x in range(DUNGEON_WIDTH):
                if (x, y) == (player.x, player.y):
                    line += PLAYER
                elif any((monster.x, monster.y) == (x, y) for monster in self.monsters):
                    line += MONSTER
                elif any((item.x, item.y) == (x, y) for item in self.items):
                    line += ITEM
                elif any((item.x, item.y) == (x, y) for item in self.potions):
                    line += POTION_HEAL
                elif any((item.x, item.y) == (x, y) for item in self.scrolls):
                    line += SCROLL_HEAL
                elif self.grid[y][x] == DOOR_CLOSED:
                    line += DOOR_CLOSED
                elif self.grid[y][x] == DOOR_OPEN:
                    line += DOOR_OPEN
                elif self.grid[y][x] == STAIRS_UP:
                    line += STAIRS_UP
                elif self.grid[y][x] == STAIRS_DOWN:
                    line += STAIRS_DOWN
                elif self.grid[y][x] == TRAP:
                    line += TRAP
                else:
                    line += self.grid[y][x]
            stdscr.addstr(y, 0, line)

    def enter_hallway(self, player):
        self.hallway = True  # Track hallway state
        player.x = DUNGEON_WIDTH // 2
        player.y = DUNGEON_HEIGHT // 2

def main(stdscr):
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(1)  # Non-blocking input
    stdscr.timeout(100)  # Update every 100ms

    player = Player()
    dungeon = Floor()

    while True:
        stdscr.clear()
        dungeon.print_dungeon(player, stdscr)
        stdscr.addstr(DUNGEON_HEIGHT, 0, f"Health: {player.health} Attack: {player.attack_damage} Defense: {player.defense} Inventory: {len(player.inventory)}")
        stdscr.addstr(DUNGEON_HEIGHT + 1, 0, "Press 'i' to view inventory, arrow keys to move.")
        stdscr.refresh()

        key = stdscr.getch()

        if key == ord('i'):
            player.open_inventory(stdscr)
        elif key == ord('q'):
            break

        dx, dy = DIRECTION_MAP.get(key, (0, 0))
        new_x = player.x + dx
        new_y = player.y + dy
        if 0 < new_x < DUNGEON_WIDTH-1 and 0 < new_y < DUNGEON_HEIGHT-1:
            if dungeon.grid[new_y][new_x] != WALL:
                player.x = new_x
                player.y = new_y

        # Interact with door (if adjacent)
        if dungeon.grid[player.y][player.x] == DOOR_OPEN:
            dungeon.enter_hallway(player)
            
  # Check for items and pick them up automatically
        for item in dungeon.items[:]:
            if (player.x, player.y) == (item.x, item.y):
                if player.pick_up_item(item):
                    dungeon.items.remove(item)

        # Check for stairs
        if (player.x, player.y) == dungeon.stairs_up:
            dungeon = Floor(floor_number=dungeon.floor_number + 1)  # Transition to the next floor
        elif (player.x, player.y) == dungeon.stairs_down:
            dungeon = Floor(floor_number=dungeon.floor_number - 1)  # Transition to the previous floor

        dungeon.update(player)

curses.wrapper(main)
