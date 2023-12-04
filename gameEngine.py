import os
import view, gameState

# from modelClasses import all

# starting game constants : can change as desired, but may softlock players
START_ROOM = "room_Hangar"
USER_NPC = "npc_player"

# input initialization constants
BAD_INPUT = "invalidInput"
PROMPT = "defaultPrompt"

# output msg formatting
NEW_LINE = "\n"
TURN_BORDER = "\n" + "=" * 100


class GameEngine:
    def __init__(self) -> None:
        self.turn_counter = 0  # bomb sabotage for example
        self.playing_now = True

        self.gameState = gameState.GameState()

        self.filled_rooms = self.gameState.populateWorld()
        self.current_room = self.filled_rooms[START_ROOM]
        self.player = self.gameState.getPlayer(USER_NPC)
        self.player_status = True

        cmd_list = [cmds for cmds in self.gameState.command_dict]
        self.commands = self.player.listToGrammarString(cmd_list)

        self.msg_dict = self.gameState.getMsgs()

        self.inH = view.InputHandler(
            cmd_list, self.msg_dict[BAD_INPUT], self.msg_dict[PROMPT]
        )
        self.outH = view.OutputHandler(self.gameState.getCommands(), self.msg_dict)

    # helper for the play() method's main while loop
    # will check every possible flag that means the game needs to end
    def checkPlayStatus(self):
        if self.player_status is False or self.playing_now is False:
            return False
        else:
            return True

    # ====== MAIN LOOP - WILL BE CALLED IN play.py ======
    def intro(self):
        self.outH.appendToBuffer(NEW_LINE)
        self.outH.printGameMessage("introduction")
        self.outH.appendToBuffer(NEW_LINE)
        self.outH.displayOutput()

    def badEnding(self):
        pass

    def play(self):
        self.intro()
        while self.checkPlayStatus():
            self.outH.appendToBuffer(NEW_LINE)
            self.executeCommand()
            self.outH.appendToBuffer(TURN_BORDER)
            self.outH.displayOutput()

    # =====================================================

    def executeCommand(self):
        # MOVE THESE 2 DICTS UPWARD AS GLOBAL CONSTANTS LATER

        # to use method,type COMMANDS_NO_ARGS[key]( parameter )
        COMMANDS_NO_ARGS = {
            "EXIT": self.exit,  # done
            "INVENTORY": self.listInventory,  # done
            "SAVE": self.gameState.save,
            "HELP": self.listCommands,  # done
            "LOCATION": self.location,  # done
            "SCAN": self.scan,  # done
            # "HINT" : self.hint
        }
        # ALL METHODS HERE NEED TO HANDLE WHEN USER DONT GIVE ADDITIONAL ENOUGH EX) MOVE + ""
        COMMANDS_WITH_ARGS = {
            "SAY": self.say,  # done
            "MOVE": self.move,  # done
            "ATTACK": self.attack,
            "USE": self.use,
            "GIVE": self.give,
            "TAKE": self.take,  # done
            "DISCARD": self.discard,  # done
        }
        # some of these will call the method from the appropriate object (container, room, etc)
        # but then get additional paramters when sent to outputHandler

        # get the input from user/player
        self.inH.parseInput()
        verb = self.inH.getVerb()
        keyword1 = self.inH.getFirstKeyword()
        keyword2 = self.inH.getSecondKeyword()  # attack GRUNT with BLASTER

        # print(" >>>> : ", verb, keyword1)

        # check dictionary of commands, seperated on whether it has parameters or not
        if verb.upper() in COMMANDS_NO_ARGS:
            COMMANDS_NO_ARGS[verb.upper()]()

        elif verb.upper() in COMMANDS_WITH_ARGS:
            if keyword2 == "":  # aka only 1 parameter
                COMMANDS_WITH_ARGS[verb.upper()](keyword1)
            else:  # unlikely to occure since game atm is very simple
                COMMANDS_WITH_ARGS[verb.upper()](keyword1, keyword2)

        else:
            self.outH.appendToBuffer("Invalid input, please try again.")

        self.outH.displayOutput()

    def move(self, direction="x"):
        direction = direction.upper()  # to match keys

        # print(self.current_room.name, direction)

        # add the actually north, south, etc if time permits

        # get rid of invalid input
        if direction.upper() not in ["N", "E", "W", "S"]:
            # REPLACE WITH OUT MSG CALL
            self.outH.appendToBuffer("That's not a valid direction.")
            return

        # get the door + room to move to
        door = self.current_room.getAssociatedDoor(direction)
        new_room = self.current_room.getConnectedRooms().get(direction)

        if door is not None:  # there is a room that direction but door locked
            if door.getCurrentState() == "solved":
                self.moveSuccess(new_room)
            elif door.getCurrentState() == "unsolved":
                self.moveFailure("there")
                self.outH.appendToBuffer(
                    door.getStateDescription(door.getCurrentState())
                )
        elif new_room is not None:  # room that direction, unblocked
            self.moveSuccess(new_room)
        else:
            self.moveFailure(self.msg_dict["roomNotThere"])

    # === the following 2 methods are helper methods for move() ===
    def moveFailure(self, targeted_room_name):
        self.outH.failMsg("MOVE", [targeted_room_name])

    def moveSuccess(self, new_room):
        self.current_room = new_room

        self.outH.successMsg("MOVE", [self.current_room.getName()])
        self.outH.appendToBuffer("\n" + self.current_room.describeRoom())

        new_room.hasEntered()  # has to be after description has been printed

    # HELPER for commands/verbs as some are very simple and use same structure
    # so far used in scan(), listInventory(), location(), listCommands()
    def basicOutputCall(self, toBeInserted, verb):
        if toBeInserted is None:
            self.outH.failMsg(verb, [])
        else:
            self.outH.successMsg(verb, [toBeInserted])

    def scan(self):
        objects = self.current_room.scan()  # aka the room's inventory
        self.basicOutputCall(objects, "SCAN")

    def listInventory(self):
        invString = self.player.listInventory()
        self.basicOutputCall(invString, "INVENTORY")

    def location(self):
        self.basicOutputCall(self.current_room.getName(), "LOCATION")

    def listCommands(self):
        self.outH.successMsg("HELP", [self.commands])

    def say(self, speech):
        if speech != "":
            self.outH.successMsg("SAY", [speech])
        else:
            self.outH.failMsg("SAY", [])

    def attack(self):
        pass

    # use can be used on door keys, puzzle keyItems
    # NOT CODED IN: teleporter, revive, other special items -> will need to be sibclassed
    def use(self, item_name):
        used = False
        # retrieve the item, but None if not in inv
        item_obj = self.player.getObject(item_name)

        if item_obj is None:
            self.outH.printGameMessage("dontHave")
            self.outH.failMsg("USE", [item_name])

        elif item_obj.use():  # means the item can only be a puzzle's key
            # ok, try opening door, if failed, then try to find a puzzle
            # if both failed THEN fail msg
            if not self.tryOpeningDoors(item_obj):  # check the doors
                self.tryPuzzle(item_obj)  # check the room for a standalone puzzle

    # helper for use()
    # will look for a door puzzle and see if the item is its key, but already opened doors fail
    def tryOpeningDoors(self, item_obj):
        if self.current_room.tryOpeningDoors(item_obj):
            self.outH.successMsg("USE", [item_obj.getName()])
            # REPLACE WITH OUT MSG CALL
            self.outH.appendToBuffer("\nYou unlocked a door.\n")
            return True
        else:
            return False

    # helper for use()
    # will look in room for a puzzle and try to solve it
    def tryPuzzle(self, keyItem):
        if self.current_room.tryPuzzle(keyItem):
            self.outH.successMsg("USE", [keyItem.getName()])
        else:
            self.outH.failMsg("USE", [keyItem.getName()])

    # due to our current naming in JSON and thus how inputHandler gets the keywords
    # the item_name is case sensitive
    def take(self, item_name):
        # get the item, remove from room if there BUT returns None if not
        item_obj = self.current_room.getObject(item_name)

        if item_name == "" or item_obj is None:
            if item_name == "":
                item_name = "nothing"
            self.outH.failMsg("TAKE", [item_name])
        else:
            # print item description
            self.outH.appendToBuffer(
                item_obj.getStateDescription(item_obj.current_state) + "\n"
            )
            # remove item and add item to player inv
            self.gameState.moveObject(item_obj, self.current_room, self.player)

            # print take msg
            self.outH.successMsg("TAKE", [item_name])

    # like take, item_name is case Sensitive
    def discard(self, item_name):
        # check the player has the item, will also remove from inv if it is there
        item_obj = self.player.getObject(item_name)

        if item_name == "":
            self.outH.failMsg("DISCARD", ["nothing"])
        elif item_obj is None:
            self.outH.printGameMessage("dontHave")
            self.outH.failMsg("DISCARD", [item_name])
        else:  # player has the object
            # remove from player + put item into room inventory
            self.gameState.moveObject(item_obj, self.player, self.current_room,)
            self.outH.successMsg("DISCARD", [item_name])

    def save(self):
        pass

    def give(self, item_name, target_npc):
        # check player has item
        # check if npc in room

        # if both true, then move item
        pass

    def exit(self):
        self.player_status = False
        self.outH.successMsg("EXIT", [])

    # from old demo code.... may not need

    def unlockAllDoors(room_dict):
        for room in room_dict.values():
            connections = room.associated_door

            for door in connections:
                if door is None:
                    continue
                else:
                    door.current_state = "solved"


os.system("cls" if os.name == "nt" else "clear")
test = GameEngine()
test.play()
