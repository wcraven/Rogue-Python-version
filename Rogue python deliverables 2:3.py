import random
import sys

# Constants for the dungeon size
DUNGEON_WIDTH = 30
DUNGEON_HEIGHT = 15

# Player and monster stats
PLAYER_HEALTH = 100
MONSTER_HEALTH = 30

# Direction mappings for easier movement and player understanding
DIRECTION_MAP = {
    'w': (-1, 0),  # left
    's': (1, 0),   # right
    'a': (0, -1),  # up
    'd': (0, 1)    # down
}

# Cell types
EMPTY = '.'
WALL = '#'
PLAYER = '@'
MONSTER = 'M'
STAIRS_UP = '<'
STAIRS_DOWN = '>'

class Dungeon:
    def __init__(self):
        self.grid = [[WALL for _ in range(DUNGEON_WIDTH)] for _ in range(DUNGEON_HEIGHT)]
        self.rooms = []
        self.generate_dungeon()

    def generate_dungeon(self):
        """Randomly generate rooms, hallways, and stairs."""
        num_rooms = random.randint(5, 7)
        for _ in range(num_rooms):
            room_width = random.randint(4, 6)
            room_height = random.randint(4, 6)
            room_x = random.randint(1, DUNGEON_WIDTH - room_width - 1)
            room_y = random.randint(1, DUNGEON_HEIGHT - room_height - 1)
            self.add_room(room_x, room_y, room_width, room_height)

        # Add hallways between rooms
        for i in range(1, len(self.rooms)):
            self.add_hallway(self.rooms[i-1], self.rooms[i])

        # Add stairs (up and down)
        self.add_stairs()

    def add_room(self, x, y, width, height):
        """Add a rectangular room to the grid."""
        for i in range(x, x + width):
            for j in range(y, y + height):
                self.grid[j][i] = EMPTY
        self.rooms.append((x, y, width, height))

    def add_hallway(self, room1, room2):
        """Connect two rooms with a more complex hallway."""
        x1, y1, _, _ = room1
        x2, y2, _, _ = room2

        # Create a hallway connecting rooms by moving horizontally first
        if x1 < x2:
            for i in range(x1, x2 + 1):
                self.grid[y1][i] = EMPTY
        elif x1 > x2:
            for i in range(x2, x1 + 1):
                self.grid[y1][i] = EMPTY

        # Then, create a vertical hallway to connect rooms
        if y1 < y2:
            for j in range(y1, y2 + 1):
                self.grid[j][x2] = EMPTY
        elif y1 > y2:
            for j in range(y2, y1 + 1):
                self.grid[j][x1] = EMPTY

    def add_stairs(self):
        """Add stairs up and down to the dungeon."""
        stairs_up_placed = False
        stairs_down_placed = False
        for _ in range(50):  # Try placing stairs going up to 50 times
            x = random.randint(1, DUNGEON_WIDTH - 2)
            y = random.randint(1, DUNGEON_HEIGHT - 2)
            if self.grid[y][x] == EMPTY and not stairs_up_placed:
                self.grid[y][x] = STAIRS_UP
                stairs_up_placed = True
                break

        for _ in range(50):  # Try placing stairs going down up to 50 times
            x = random.randint(1, DUNGEON_WIDTH - 2)
            y = random.randint(1, DUNGEON_HEIGHT - 2)
            if self.grid[y][x] == EMPTY and not stairs_down_placed:
                self.grid[y][x] = STAIRS_DOWN
                stairs_down_placed = True
                break

    def print_dungeon(self, player_x, player_y, monsters):
        """Print the dungeon grid with player and monsters."""
        for y in range(DUNGEON_HEIGHT):
            for x in range(DUNGEON_WIDTH):
                if (x, y) == (player_x, player_y):
                    print(PLAYER, end='')
                elif any((monster.x, monster.y) == (x, y) for monster in monsters):
                    print(MONSTER, end='')
                else:
                    print(self.grid[y][x], end='')
            print()


class Player:
    def __init__(self):
        self.x = 1
        self.y = 1
        self.health = PLAYER_HEALTH

    def move(self, direction):
        dx, dy = DIRECTION_MAP.get(direction, (0, 0))
        self.x += dx
        self.y += dy

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            print("You have died!")
            sys.exit()

    def attack(self, monster):
        """Attack a monster."""
        print(f"You attack the monster at ({monster.x}, {monster.y})!")
        monster.take_damage(15)  # Player attacks monster for 15 damage


class Monster:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = MONSTER_HEALTH

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            print(f"A monster at ({self.x}, {self.y}) has been slain!")
            self.health = 0  # Mark as slain


class Game:
    def __init__(self):
        self.dungeon = Dungeon()
        self.player = Player()
        self.monsters = []
        self.spawn_monsters()

    def spawn_monsters(self):
        """Spawn random monsters in the dungeon."""
        for _ in range(random.randint(3, 5)):
            x = random.randint(1, DUNGEON_WIDTH - 2)
            y = random.randint(1, DUNGEON_HEIGHT - 2)
            if self.dungeon.grid[y][x] == EMPTY:
                self.monsters.append(Monster(x, y))

    def handle_combat(self):
        """Handle combat between the player and any monsters."""
        for monster in self.monsters:
            if (self.player.x, self.player.y) == (monster.x, monster.y):
                print("A monster has attacked you!")
                self.player.take_damage(10)  # Simple combat rule: take 10 damage
                monster.take_damage(15)      # Player attacks monster for 15 damage
                self.player.attack(monster)
                # Prompt for basic attack
                action = input("Do you wish to attack the monster? (y/n): ").lower()
                if action == "y":
                    self.player.attack(monster)
                    self.monsters = [m for m in self.monsters if m.health > 0]

    def check_for_stairs(self):
        """Check if the player is on the stairs."""
        for y in range(DUNGEON_HEIGHT):
            for x in range(DUNGEON_WIDTH):
                if self.dungeon.grid[y][x] == STAIRS_UP and (x, y) == (self.player.x, self.player.y):
                    print("You found the stairs up!")
                    self.dungeon = Dungeon()  # Generate a new dungeon
                    self.player.x, self.player.y = 1, 1  # Reset player position
                    self.spawn_monsters()  # Spawn new monsters
                    return True
                elif self.dungeon.grid[y][x] == STAIRS_DOWN and (x, y) == (self.player.x, self.player.y):
                    print("You found the stairs down!")
                    self.dungeon = Dungeon()  # Generate a new dungeon
                    self.player.x, self.player.y = 1, 1  # Reset player position
                    self.spawn_monsters()  # Spawn new monsters
                    return True
        return False

    def play_turn(self):
        """Play one turn of the game."""
        self.dungeon.print_dungeon(self.player.x, self.player.y, self.monsters)
        direction = input("Move (w/a/s/d): ").lower()

        # Move player
        self.player.move(direction)

        # Check if player is on stairs
        if self.check_for_stairs():
            return  # Skip the rest of the turn if the player is on stairs

        # Handle combat if player moves to a monster
        self.handle_combat()


def main():
    game = Game()

    while True:
        game.play_turn()


if __name__ == "__main__":
    main()

