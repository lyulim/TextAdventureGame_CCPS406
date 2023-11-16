import json

class Puzzle:
    def __init__(self, solvedState=False, keyItem="", keyVerb=""):
        self.solvedState = solvedState
        self.keyItem = keyItem
        self.keyVerb = keyVerb

    def getKeyItem(self):
        return self.keyItem

    def getKeyVerb(self):
        return self.keyVerb

    def getState(self):
        return self.solvedState

    def setState(self, solvedState):
        self.solvedState = solvedState

# Load JSON data for puzzles
json_data = """
{
    "compoundPuzzle1": {
        // Define puzzle 1 data
    },
    "compoundPuzzle2": {
        // Define puzzle 2 data
    },
    "compoundPuzzle3": {
        // Define puzzle 3 data
    },
    "compoundPuzzle4": {
        // Define puzzle 4 data
    }
}
"""

puzzles_data = json.loads(json_data)

# Create instances of the Puzzle class for each puzzle
puzzle_instances = {}
for puzzle_id, puzzle_data in puzzles_data.items():
    puzzle_instances[puzzle_id] = Puzzle(solvedState=puzzle_data["initialState"] == "solved", keyItem=puzzle_data["key"], keyVerb=puzzle_data["keyVerb"])

# Example usage in a text-based game
if __name__ == "__main__":
    # Initialize the game state
    current_room = "Starting Room"

    # Main game loop
    while True:
        print(f"You are in the {current_room}.")

        # Check if there is a puzzle associated with the current room
        if current_room in puzzles_data:
            puzzle = puzzle_instances[current_room]
            print(f"Puzzle Name: {puzzles_data[current_room]['name']}")
            print(f"Puzzle Description: {puzzles_data[current_room]['stateDescriptions'][puzzle.getState().lower()]}")
            print(f"Key Item: {puzzle.getKeyItem()}")

            user_action = input("What do you want to do? ").strip().upper()

            # Logic to interact with the puzzle
            if user_action == puzzle.getKeyVerb():
                if not puzzle.getState():
                    # Handle solving the puzzle
                    user_answer = input(f"What is the answer to the {puzzles_data[current_room]['subPuzzles'][0]['name']}? ").strip().lower()
                    if user_answer == puzzles_data[current_room]['subPuzzles'][0]['answer']:
                        puzzle.setState(True)
                        print("You've solved the puzzle!")
                    else:
                        print("That's not the correct answer.")
                else:
                    print("The puzzle is already solved.")
            elif user_action == "LOOK AT":
                # Describe the room or puzzle
                print(puzzles_data[current_room]['stateDescriptions'][puzzle.getState().lower()])
            elif user_action == "MOVE":
                destination = input("Where do you want to go? ").strip()
                if destination in rooms_data.get(current_room, []):
                    current_room = destination
                else:
                    print("You can't go there from here.")
            elif user_action == "QUIT":
                print("Thanks for playing!")
                break
            else:
                print("You can't do that here.")

        # Game progression logic (e.g., moving to other rooms) goes here
        else:
            print("There's nothing to do here.")


        # Access and manipulate the puzzle instances
    puzzle1 = puzzle_instances["compoundPuzzle1"]
    puzzle2 = puzzle_instances["compoundPuzzle2"]
    puzzle3 = puzzle_instances["compoundPuzzle3"]
    puzzle4 = puzzle_instances["compoundPuzzle4"]

    print("Puzzle 1 Name:", puzzles_data["compoundPuzzle1"]["name"])
    print("Puzzle 1 Key Item:", puzzle1.getKeyItem())
    print("Puzzle 1 Key Verb:", puzzle1.getKeyVerb())
    print("Puzzle 1 Solved State:", puzzle1.getState())

    print("\nPuzzle 2 Name:", puzzles_data["compoundPuzzle2"]["name"])
        # Access and print attributes for puzzle 2, 3, and 4 similarly.
    print("\nPuzzle 2 Name:", puzzles_data["compoundPuzzle2"]["name"])
    print("Puzzle 2 Key Item:", puzzle2.getKeyItem())
    print("Puzzle 2 Key Verb:", puzzle2.getKeyVerb())
    print("Puzzle 2 Solved State:", puzzle2.getState())

    print("\nPuzzle 3 Name:", puzzles_data["compoundPuzzle3"]["name"])
    print("Puzzle 3 Key Item:", puzzle3.getKeyItem())
    print("Puzzle 3 Key Verb:", puzzle3.getKeyVerb())
    print("Puzzle 3 Solved State:", puzzle3.getState())

    print("\nPuzzle 4 Name:", puzzles_data["compoundPuzzle4"]["name"])
    print("Puzzle 4 Key Item:", puzzle4.getKeyItem())
    print("Puzzle 4 Key Verb:", puzzle4.getKeyVerb())
    print("Puzzle 4 Solved State:", puzzle4.getState())
 




