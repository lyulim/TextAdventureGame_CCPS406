from gameLoader import GameLoader
from modelClasses import Room, Puzzle, SOLVED
import random

FILE_NAME_LIST = [
    "JSON/npcs.json",
    "JSON/room.json",
    "JSON/items.json",
    "JSON/puzzles.json",
    "JSON/gameMsg.json",
    "JSON/commands.json",
]

SIDEQUEST_NPC = [("npc_K", "coin")]

# for roaming
SEED = 10  # for the roam random generator
DIRECTION_DUMMY = "X"


class GameState:
    def __init__(self):
        # load the json objects into dictionaries of each object type
        self.models = GameLoader(FILE_NAME_LIST)
        (
            self.npc_dict,
            self.room_dict,
            self.item_dict,
            self.puzzle_dict,
            self.msg_dict,
            self.command_dict,
        ) = self.models.loadGame()

        random.seed(SEED)  # seed it for roam

        self.roamers_limited = []
        self.getRoamers()
        self.roamers_free = []

        self.sidequest = False

        # print(self.npc_dict["npc_player"].inventory)

    # ========================== COMMAND/VERB RELATED METHODS ============================

    # moves an OBJECT from one CONTAINER to another.
    # this method assumes that the given args are the actual objs
    def moveObject(self, obj, source, target):
        # remove from source and add to target AKA move
        source.removeObject(obj)
        target.addToInv(obj)

    def moveNPC(self, npc_obj, target_room):  # target_room is the actual room object
        # get the NPC's current room object
        current_room = self.room_dict[npc_obj.getLocation()]

        self.moveObject(npc_obj, current_room, target_room)

        new_location = self.findRoom(target_room.getName())
        npc_obj.setLocation(new_location)

    def findRoom(self, name):
        for room_key in self.room_dict:
            if self.room_dict[room_key].getName() == name:
                return room_key
        return None

    # ==== ROAM ====  will cause all self roaming NPCs to move about

    def getRoamers(self):
        for npc_key in self.npc_dict:
            if self.npc_dict[npc_key].getRoamState():
                self.roamers_limited.append(npc_key)

    # this one will roam but be unable to go through locked door
    def roamLimited(self):
        # print(">>> LOGGING : roam activated")
        for npc_name in self.roamers_limited:
            npc = self.npc_dict[npc_name]  # get the npc object
            room = self.room_dict[npc.getLocation()]  # get their room

            # check if they can move, if yes then move them
            direction = random.choice(Room.DIRECTIONS + [DIRECTION_DUMMY])
            can_move = self.canMove(room, direction)
            if can_move[0]:
                self.moveNPC(npc, can_move[1])
                # print(">>> LOGGING : ", npc_name, " has moved!")
            else:
                # if the direction isnt valid bc locked door / not exist,
                # they stay AKA do nothing
                # print(">>> LOGGING : ", npc_name, " STAYED!")
                pass

    # returns a list of 2 objects:
    # 1st boolean tells you if you can move - if true, 2nd give new_room
    # 2nd booleans tells if there is a door
    def canMove(self, room, direction):
        door = room.getAssociatedDoor(direction)
        new_room = room.getConnectedRoom(direction)

        if new_room is None:
            return [False, False]
        elif door is None:  # is a room, no blocking door
            return [True, new_room]
        elif door.getCurrentState() == SOLVED:
            return [True, new_room]
        else:  # door is still locked
            return [False, True]

    # this one is for grunts/enemies, who are not limited by locked doors
    # storywise, they all have a masterkey and lock the door behind them if it was already locked
    def roamAnywhere(self):
        for npc_name in self.roamers_free:
            npc = self.npc_dict[npc_name]  # get the npc object
            room = self.room_dict[npc.getLocation()]  # get their room

            # check if they can move, if yes then move them
            direction = random.choice(Room.DIRECTIONS)
            new_room = room.getConnectedRoom(direction)

            if new_room is not None:
                self.moveNPC(npc, new_room)

    # =====================================================================================
    # all side quests require the target NPC to have a certain item in their inv
    # coin with K, datadrive with Lia, beamsaber + jaydai with player
    # BUT the final boss one also requires the player to be in the room
    # BUT talk with jaydai WITH beamsaber is a requirement for them to join
    def sideQuests(self):
        # list of NPCs with their special item
        # check each time this method is called whether they have it
        # if true, ensure each relative NPC acts as if the sidequest is solved
        for npc_key, item_name in SIDEQUEST_NPC:
            npc = self.npc_dict[npc_key]
            #print(npc.name, item_name)
            #print(npc.inventory)

            # currently just k, so this is ok
            if item_name in npc.inventory.keys() and self.sidequest is False:
                self.unlockAllDoors()
                self.sidequest = True
                #print("cheat code: doors are all unlocked")

            # admittedly this is super rough

            # to improve? subclass NPC to create QuestNPCs
            # will add variable to list their quest Item + if its present in their inv
            # might also have them hold a veriable to their own unique method
            # ala self.method(), like the verb dict in gameEngine's executeCommand()

    def unlockAllDoors(self):
        for room in self.room_dict.values():
            connections = room.associated_door

            for door in connections.values():
                if door is None:
                    continue
                else:
                    door.solved()

    # =====================================================================================

    # This method converts the inventories of all NPCs + Rooms into dictionaries
    # that points to the actual item/puzzle/npc object
    # Also converts puzzle's key into the actual object
    def populateWorld(self):
        # fill puzzle keys
        self.keyToObject()

        pool = {**self.item_dict, **self.puzzle_dict}  # merge the dictionaries
        # print(pool)

        # 1) fill NPC inventories with items + puzzles
        self.fillInv(self.npc_dict, pool)
        # print(self.npc_dict["npc_lia"].inventory)
        # print(">>> npc filled")

        # 2) fill room inventories with NPCs, items, + puzzles (doors + others)
        pool.update(self.npc_dict)
        self.fillInv(self.room_dict, pool)
        self.fillRooms(self.room_dict, pool)

        # return updated room dictionary
        return self.room_dict

    # converts the inventory from a list of strings(keys) to dictionary of objects
    def fillInv(self, beingFilled, pool):
        # print("-" * 20)
        # get individual npc/room/etc whose inv needs to be filled
        for model in beingFilled.values():
            # print(model.name)
            tmp = {}

            for thing_name in model.inventory:
                if thing_name is None:
                    break

                true_obj = pool[thing_name]
                # print(true_obj.name)
                tmp[true_obj.getName()] = true_obj

            model.inventory = tmp
            # print(model.inventory)

    # specifically handles the room's doors and connecting rooms
    def fillRooms(self, room_dict, pool):
        for room in room_dict.values():
            # print(">>>> ", room.name)
            for direction in room.connected_to:
                # fill out connected to
                connected_room_name = room.connected_to[direction]
                if connected_room_name is not None:
                    true_room = room_dict[connected_room_name]
                else:
                    true_room = None
                room.connected_to[direction] = true_room

                # fill out doors
                door_name = room.associated_door[direction]
                if door_name is not None:
                    true_door = pool[door_name]
                else:
                    true_door = None
                room.associated_door[direction] = true_door

            # print(room.connected_to)
            # print(room.associated_door)

    # specifically handles converting a puzzle's key from a string to an object
    def keyToObject(self):
        for puzzle in self.puzzle_dict.values():
            item = self.item_dict[puzzle.getKey()]
            puzzle.setKey(item)
            # print(puzzle.getKey())

    # ================================END POPULATE WORLD METHODS ========================================

    def getNPC(self, npc_name):
        # Check if the NPC exists in the dictionary before returning
        if npc_name in self.npc_dict:
            return self.npc_dict[npc_name]
        else:
            # NPC doesn't exist, handle this situation (print an error message or return None)
            print(f"NPC '{npc_name}' does not exist in the game.")
            return None  # Or handle the situation according to your game's logicw

    def getCommands(self):
        return self.command_dict

    def getMsgs(self):
        return self.msg_dict

    def save(self):
        pass
        # call gameSaver to save data


# test = GameState()
# rooms = test.populateWorld()
# print(rooms)
# print(rooms.get("room_Hangar").associated_door['S'])
# print(rooms["room_security"].inventory)
# print(rooms["room_armory"].describeRoom())
# print(rooms.get("room_Hangar").associated_door)
