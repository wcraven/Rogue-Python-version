Rogue By Will Craven README

Dungeon Crawler Game
This Python-based Dungeon Crawler game is inspired by the Rogue 5.4.4 and Rogue DOS versions. The game includes dynamic interactions between characters, monsters, items, and dungeon environments. Players explore dungeon rooms, battle monsters, collect loot, and enhance their abilities as they level up.
Features
•	Player Character: Players can pick up items, use them, and gain experience by defeating monsters.

•	Monsters: Various monsters with unique abilities, drop rates, and behaviors (e.g., rusting armor, stealing gold).

•	Items: Weapons, armor, potions, scrolls, and gold, each with unique attributes (e.g., durability, enchantments, effects).

•	Dungeon Generation: Procedurally generated dungeons with connected rooms, traps, and item/monster placement.

•	Status Effects: Players and monsters can be affected by various status effects like poison, confusion, sleep, etc.






Game Structure
Classes
GameObject
•	The base class for all objects in the game.

•	Attributes: name (str), description (str)
Character (inherits from GameObject)
•	Represents both the player and monsters.

•	Attributes:
o	HP (int)
o	attack (int)
o	defense (int)
o	speed (int)
o	position (tuple of coordinates)
o	status_effects (list of effects like 'poisoned', 'confused', etc.)
Player (inherits from Character)
•	The main player-controlled character.

•	Attributes:
o	level (int)
o	inventory (list of items)
o	gold (int)
o	experience (int)
o	strength (int)
o	armor_class (int)
o	food_level (int)



•	Methods:
o	pick_item(): Adds an item to the inventory.
o	use_item(): Uses an item from the inventory.
o	gain_experience(): Increases experience and levels up.
o	eat_food(): Increases food level and restores HP.
Monster (inherits from Character)
•	Represents enemy monsters in the dungeon.

•	Attributes:
o	AI_behavior (str): Defines how the monster behaves (e.g., random movement, aggressive).
o	hostility (bool): Whether the monster is hostile or passive.
o	unique_abilities (str): Special abilities like "rusts armor," "confuse player."
o	drop_rate (str): Loot drop rate (e.g., "gold," "weapons").

•	Methods:
o	attack(): Defines the monster's attack behavior.
o	move(): Defines how the monster moves.
o	drop_loot(): Drops loot when the monster is defeated.
Item (base class for items)
•	Represents all items in the game.

•	Attributes:
o	weight (int): The weight of the item.
o	rarity (str): The rarity level of the item.
o	cursed_status (bool): Whether the item is cursed.
o	value (int): The value in gold or trade.





Weapon (inherits from Item)
•	Represents weapons in the game.

•	Attributes:
o	damage (int): The damage dealt by the weapon.
o	durability (int): How many times the weapon can be used before it breaks.
o	enchantment_level (int): The level of magical enhancement.
o	material (str): The material the weapon is made from (e.g., "steel," "iron").
o	weight (int): The weight of the weapon.

•	Methods:
o	equip(): Equip the weapon to the player or monster.
o	use(): Use the weapon to attack.
Armor (inherits from Item)
•	Represents armor in the game.

•	Attributes:
o	defense_bonus (int): The defense bonus provided by the armor.
o	rust_resistance (bool): Whether the armor resists rust.
o	weight (int): The weight of the armor.





•	Methods:
o	equip(): Equip the armor to the player or monster.
Potion (inherits from Item)
•	Represents potions in the game.

•	Attributes:
o	effect (str): The effect of the potion (e.g., "restore 10 HP").
o	color (str): The potion's color.
o	known (bool): Whether the player knows the effect of the potion.
o	uses_left (int): How many uses the potion has.

•	Methods:
o	use(): Consume the potion and apply its effect.
Scroll (inherits from Item)
•	Represents scrolls in the game.

•	Attributes:
o	magic_effect (str): The magical effect of the scroll (e.g., "identify items").
o	paper_type (str): The material of the scroll.
o	known (bool): Whether the scroll's effect is known to the player.

•	Methods:
o	use(): Use the scroll to invoke its effect.

Gold (inherits from Item)
•	Represents gold items in the game.

•	Attributes:
o	amount (int): The amount of gold.
o	weight (int): The weight of gold (usually 1).

•	Methods:
o	use(): Add the gold to the player's inventory.
Dungeon
•	The main class representing the dungeon.

•	Attributes:
o	rooms (list): A list of rooms in the dungeon.
o	floor_number (int): The current floor the player is on.
o	stairs_location (tuple of x, y): The location of the stairs to the next floor.
o	difficulty_level (int): The difficulty level of the dungeon.

•	Methods:
o	enter_room(): Enter a room in the dungeon.
o	move_player(): Move the player around the dungeon.
o	generate_monsters(): Generate monsters in the rooms.
o	spawn_items(): Place items in the dungeon rooms.
Room
•	Represents individual rooms in the dungeon.

•	Attributes:
o	tiles (list): A list of tiles in the room.
o	has_monster (bool): Whether the room contains a monster.
o	has_item (bool): Whether the room contains an item.
o	connected_rooms (list): A list of connected rooms.
Tile
•	Represents tiles in the room.

•	Attributes:
o	type (str): The type of tile (e.g., "floor," "wall").
o	is_walkable (bool): Whether the tile is walkable.
o	traps (list): A list of traps on the tile.
o	visibility (bool): Whether the tile is visible to the player.

Development Notes

•	Random Generation: The dungeon is generated randomly each time the game is started, creating unique layouts for each playthrough.

•	Combat: The combat mechanics are turn-based, where both the player and monsters attack each other until one is defeated.

•	Item Effects: Items have specific effects, such as healing the player, equipping weapons, or consuming food to restore health.

•	Future Enhancements: The game could be extended with additional features such as more item types, advanced monster AI, multiple player classes, and more complex combat mechanics.


How to Play
1.	Start the Game: When you start the game, the dungeon will be procedurally generated. You will enter the first room and can explore the dungeon.

2.	Explore: Move through rooms, interact with tiles, fight monsters, and loot items.

3.	Battle Monsters: When encountering monsters, you will engage in combat where you can attack, use items, or try to escape.

4.	Use Items: Use potions, scrolls, and weapons to improve your stats or aid in battles.

5.	Level Up: Defeat monsters to gain experience points. Level up to increase your strength, defense, and other attributes.

6.	Loot Items: Pick up gold, armor, weapons, and potions to enhance your character's abilities.

7.	Survive: Keep an eye on your health and food level. Manage your inventory wisely to survive the challenges ahead.

![image](https://github.com/user-attachments/assets/08579055-715f-4962-87f4-ac9c26a506ab)
