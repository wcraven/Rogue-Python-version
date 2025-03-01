import random
import os
import time
import curses  # Importing curses to handle terminal input better

# Constants for the dungeon dimensions
DUNGEON_WIDTH = 20
DUNGEON_HEIGHT = 10

# Symbols for the grid
WALL = '#'
EMPTY = '.'
PLAYER = '@'
MONSTER = 'M'
ITEM = '*'
STAIRS_UP = '<'
STAIRS_DOWN = '>'

# Player and monster stats
PLAYER_HEALTH = 100
MONSTER_HEALTH = 30
MONSTER_ATTACK = 10
MONSTER_DEFENSE = 5

# Direction map for player movement (h/j/k/l for movement)
DIRECTION_MAP = {
    'h': (-1, 0),  # left
    'j': (0, 1),   # down
    'k': (0, -1),  # up
    'l': (1, 0),   # right
}

# Item types
POTION_HEAL = 'potion_heal'
WEAPON_SWORD = 'weapon_sword'
ARMOR_SHIELD = 'armor_shield'
SCROLL_IDENTITY = 'scroll_identity'
FOOD_RATION = 'food_ration'

# Player inventory size
MAX_INVENTORY = 10

class Monster:
    """Monster class to represent a monster in the dungeon."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = MONSTER_HEALTH
        self.attack_damage = MONSTER_ATTACK
        self.defense = MONSTER_DEFENSE

    def take_damage(self, damage):
        """Monster takes damage and checks if it's still alive."""
        self.health -= damage
        if self.health <= 0:
            print(f"The monster at ({self.x}, {self.y}) has been slain!")

    def attack(self, player):
        """Monster attacks the player."""
        damage = max(0, self.attack_damage - player.defense)
        player.take_damage(damage)
        print(f"The monster attacks you for {damage} damage!")

class Item:
    def __init__(self, x, y, item_type, name, effect=None):
        self.x = x
        self.y = y
        self.item_type = item_type
        self.name = name
        self.effect = effect  # Effect will be a function for using the item

    def use(self, player):
        """Use the item on the player."""
        if self.effect:
            self.effect(player)
            print(f"You use the {self.name}.")

def heal_player(player):
    """Function to heal the player."""
    player.health = min(player.health + 20, PLAYER_HEALTH)  # Heal player but not exceed max health
    print(f"You have been healed! Your current health is {player.health}.")

def use_sword(player):
    """Equip the sword for the player."""
    print("You equip the sword!")

def use_shield(player):
    """Equip the shield for the player."""
    print("You equip the shield!")

def scroll_identify(player):
    """Use a scroll of identity (for now, we'll just print a message)."""
    print("The scroll identifies something...")

def eat_ration(player):
    """Eat a food ration to restore health."""
    player.health = min(player.health + 10, PLAYER_HEALTH)
    print(f"You eat the food ration! Your current health is {player.health}.")

class Floor:
    def __init__(self):
        self.grid = [[EMPTY for _ in range(DUNGEON_WIDTH)] for _ in range(DUNGEON_HEIGHT)]
        self.rooms = []
        self.items = []
        self.monsters = []
        self.stairs_up = None
        self.stairs_down = None

    # Generate the floor layout (rooms, corridors, monsters, etc.)
    def generate(self):
        self.generate_rooms_and_corridors()
        self.place_stairs()
        self.place_items()
        self.place_monsters()

    def place_stairs(self):
        """Place stairs up and down on the floor."""
        # Place stairs up
        while True:
            x = random.randint(1, DUNGEON_WIDTH - 2)
            y = random.randint(1, DUNGEON_HEIGHT - 2)
            if self.grid[y][x] == EMPTY:
                self.stairs_up = (x, y)
                self.grid[y][x] = STAIRS_UP
                break

        # Place stairs down
        while True:
            x = random.randint(1, DUNGEON_WIDTH - 2)
            y = random.randint(1, DUNGEON_HEIGHT - 2)
            if self.grid[y][x] == EMPTY:
                self.stairs_down = (x, y)
                self.grid[y][x] = STAIRS_DOWN
                break

    def get_spawn_point(self):
        """Return a random empty square (.) on the floor to spawn the player."""
        while True:
            x = random.randint(1, DUNGEON_WIDTH - 2)
            y = random.randint(1, DUNGEON_HEIGHT - 2)
            if self.grid[y][x] == EMPTY:  # Ensure the square is empty
                return x, y

    def print_floor(self, player, stdscr):
        """Print the current floor layout including rooms, items, monsters, etc."""
        for y in range(DUNGEON_HEIGHT):
            for x in range(DUNGEON_WIDTH):
                if (x, y) == (player.x, player.y):
                    stdscr.addstr(y, x * 2, PLAYER)
                elif (x, y) == self.stairs_up:
                    stdscr.addstr(y, x * 2, STAIRS_UP)
                elif (x, y) == self.stairs_down:
                    stdscr.addstr(y, x * 2, STAIRS_DOWN)
                elif any((monster.x, monster.y) == (x, y) for monster in self.monsters):
                    stdscr.addstr(y, x * 2, MONSTER)
                elif any((item.x, item.y) == (x, y) for item in self.items):
                    stdscr.addstr(y, x * 2, ITEM)  # Mark the item location with '*'
                else:
                    stdscr.addstr(y, x * 2, self.grid[y][x])
        stdscr.refresh()

    def generate_rooms_and_corridors(self):
        """Randomly generate rooms and corridors (simplified version)."""
        for _ in range(4):  # Add 4 rooms instead of 3 for more open space
            room_width = random.randint(4, 7)
            room_height = random.randint(4, 7)
            x = random.randint(1, DUNGEON_WIDTH - room_width - 1)
            y = random.randint(1, DUNGEON_HEIGHT - room_height - 1)

            # Fill the room with empty space
            for i in range(x, x + room_width):
                for j in range(y, y + room_height):
                    self.grid[j][i] = EMPTY

            # Mark the room border with walls
            for i in range(x, x + room_width):
                self.grid[y][i] = WALL
                self.grid[y + room_height - 1][i] = WALL
            for j in range(y, y + room_height):
                self.grid[j][x] = WALL
                self.grid[j][x + room_width - 1] = WALL

    def place_items(self):
        """Place random items in the dungeon."""
        item_list = [
            (POTION_HEAL, "Healing Potion", heal_player),
            (WEAPON_SWORD, "Sword", use_sword),
            (ARMOR_SHIELD, "Shield", use_shield),
            (SCROLL_IDENTITY, "Scroll of Identity", scroll_identify),
            (FOOD_RATION, "Food Ration", eat_ration),
        ]

        for item_type, name, effect in item_list:
            x = random.randint(1, DUNGEON_WIDTH - 2)
            y = random.randint(1, DUNGEON_HEIGHT - 2)
            if self.grid[y][x] == EMPTY:  # Only place items in empty spaces
                self.items.append(Item(x, y, item_type, name, effect))
                self.grid[y][x] = ITEM

    def place_monsters(self):
        """Place random monsters in the dungeon."""
        for _ in range(2):  # Add 2 monsters instead of 3
            x = random.randint(1, DUNGEON_WIDTH - 2)
            y = random.randint(1, DUNGEON_HEIGHT - 2)
            if self.grid[y][x] == EMPTY:  # Only place monsters in empty spaces
                self.monsters.append(Monster(x, y))

class Dungeon:
    def __init__(self, num_floors=3):
        self.floors = [Floor() for _ in range(num_floors)]  # Create multiple floors
        self.current_floor = 0
        self.create_floor(self.current_floor)

    def create_floor(self, floor_index):
        """Generate a floor with rooms, corridors, items, and monsters."""
        self.floors[floor_index].generate()

    def update(self, player):
        """Update the dungeon: move monsters, check for combat, handle other updates."""
        floor = self.floors[self.current_floor]

        # Update monster movements and check for combat
        for monster in floor.monsters:
            # Example: Monsters could move towards the player or randomly
            self.move_monster(monster)
            if (monster.x, monster.y) == (player.x, player.y):
                self.handle_combat(player, monster)

        # Check if player steps on stairs up or down
        if (player.x, player.y) == floor.stairs_up:
            self.move_player_up(player)
        elif (player.x, player.y) == floor.stairs_down:
            self.move_player_down(player)

    def handle_combat(self, player, monster):
        """Handle combat between the player and a monster."""
        while player.health > 0 and monster.health > 0:
            # Player attacks
            if self.attack_successful(player.attack_damage, monster):
                damage = max(0, player.attack_damage - monster.defense)
                monster.health -= damage
                print(f"You hit the monster for {damage} damage! Monster health: {monster.health}")
            else:
                print("Your attack misses the monster.")

            # Monster attacks if still alive
            if monster.health > 0:
                if self.attack_successful(monster.attack_damage, player):
                    damage = max(0, monster.attack_damage - player.defense)
                    player.health -= damage
                    print(f"The monster hits you for {damage} damage! Your health: {player.health}")
                else:
                    print("The monster's attack misses you.")

            # Pause for the next round of combat
            time.sleep(1)

        if player.health <= 0:
            print("You have been defeated by the monster!")
        elif monster.health <= 0:
            print("You have defeated the monster!")

    def attack_successful(self, attack, target):
        """Determine if an attack is successful."""
        return random.random() < 0.8  # 80% chance to hit for simplicity

    def print_dungeon(self, player, stdscr):
        """Print the current floor with the player, monsters, and items."""
        self.floors[self.current_floor].print_floor(player, stdscr)

    def move_monster(self, monster):
        """Move the monster in a random direction."""
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # right, down, left, up
        direction = random.choice(directions)
        new_x = monster.x + direction[0]
        new_y = monster.y + direction[1]

        if 1 <= new_x < DUNGEON_WIDTH - 1 and 1 <= new_y < DUNGEON_HEIGHT - 1:
            monster.x = new_x
            monster.y = new_y

class Player:
    def __init__(self):
        self.x = 1
        self.y = 1
        self.health = PLAYER_HEALTH
        self.attack_damage = 10
        self.defense = 5
        self.inventory = []

    def take_damage(self, damage):
        """Reduce player's health by damage amount."""
        self.health -= damage
        print(f"You take {damage} damage! Current health: {self.health}")
    
    def attack(self, monster):
        """Player attacks a monster, causing damage."""
        damage = self.attack_damage
        monster.take_damage(damage)
        print(f"You attack the monster for {damage} damage.")

    def is_move_valid(self, dx, dy, floor):
        """Check if the player's move is valid (i.e., not hitting walls)."""
        new_x = self.x + dx
        new_y = self.y + dy
        if 0 <= new_x < DUNGEON_WIDTH and 0 <= new_y < DUNGEON_HEIGHT:
            if floor.grid[new_y][new_x] == WALL:
                return False
            return True
        return False

    def pick_up_item(self, item):
        """Pick up an item and add it to the player's inventory."""
        if len(self.inventory) < MAX_INVENTORY:
            self.inventory.append(item)
            print(f"You pick up the {item.name}.")
        else:
            print("Your inventory is full!")

    def use_item(self, item_name):
        """Use an item from the inventory."""
        item = next((i for i in self.inventory if i.name.lower() == item_name.lower()), None)
        if item:
            item.use(self)
            self.inventory.remove(item)

def main(stdscr):
    # Initialize the screen and game objects
    curses.curs_set(0)  # Hide the cursor
    stdscr.nodelay(1)  # Non-blocking input
    stdscr.timeout(100)  # Refresh every 100ms

    player = Player()
    dungeon = Dungeon()

    while player.health > 0:
        # Print the current dungeon state
        stdscr.clear()
        dungeon.print_dungeon(player, stdscr)
        stdscr.addstr(DUNGEON_HEIGHT, 0, f"Health: {player.health}  Inventory: {len(player.inventory)} items")
        stdscr.refresh()

        # Get user input
        key = stdscr.getch()

        if key == ord('q'):
            break  # Quit the game
        elif key == ord('h'):
            move = 'h'
        elif key == ord('j'):
            move = 'j'
        elif key == ord('k'):
            move = 'k'
        elif key == ord('l'):
            move = 'l'
        else:
            move = None

        if move:
            dx, dy = DIRECTION_MAP.get(move, (0, 0))
            if player.is_move_valid(dx, dy, dungeon.floors[dungeon.current_floor]):
                player.x += dx
                player.y += dy
            else:
                stdscr.addstr(DUNGEON_HEIGHT + 1, 0, "You can't move in that direction.")
                stdscr.refresh()

        # Allow player to interact with items and monsters
        if (player.x, player.y) in [(item.x, item.y) for item in dungeon.floors[dungeon.current_floor].items]:
            stdscr.addstr(DUNGEON_HEIGHT + 1, 0, "You find an item. Do you want to pick it up? (y/n) ")
            stdscr.refresh()
            pick_up_choice = stdscr.getch()
            if chr(pick_up_choice).lower() == 'y':
                item = next(i for i in dungeon.floors[dungeon.current_floor].items if (i.x, i.y) == (player.x, player.y))
                player.pick_up_item(item)
                dungeon.floors[dungeon.current_floor].items.remove(item)

        # Update dungeon (monster movements, combat, etc.)
        dungeon.update(player)
        
    stdscr.addstr(DUNGEON_HEIGHT + 2, 0, "Game Over!")
    stdscr.refresh()
    stdscr.getch()

curses.wrapper(main)
