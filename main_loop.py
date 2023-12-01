from custom_functions import *

def handle_input(verb,target,current_game_state):

    current_room=current_game_state.current_room


    if verb=="move":
        new_room=move(current_room,rooms_list,target[0].upper())

        if current_room!=new_room:
            current_game_state.change_room(new_room)


    if verb == "scan":
        print(current_room.get_scan_description())

    if verb == "give":
        new_item=find_item(target,items_list)
        give_check=new_item.give_item(current_game_state)

        if give_check:

            for item in current_game_state.inventory:
                if item.lower()==target.lower():
                    discard_item=item
            
            current_game_state.remove_item(discard_item)


    if verb=="take":


        for item in current_room.inventory:
            if item.lower()==target.lower():
                new_item=item
                item_object = find_item(new_item, items_list)
                print(item_object.description)
                print("Took " + item)
        
        current_game_state.add_item(new_item)
        current_room.remove_item(new_item)


    if verb=="discard":
        
        for item in current_game_state.inventory:
            if item.lower()==target.lower():
                new_item=item
                print("Discarded " + item)
        
        current_room.add_item(new_item)
        current_game_state.remove_item(new_item)

    if verb=="inventory":
        print(current_game_state.inventory)

    if verb=="use":
        new_item=find_item(target,items_list)
        new_item.use_item(current_game_state)

    if verb=="say":
        

        if target.lower()=="all your base are belong to us." or target.lower()=='all your base are belong to us':

            print('All doors are now unlocked.')
            unlock_all_doors(rooms_list)

        else:
            print('You look around you and scream: '+target+'\nNo one seems to care.')

    if verb == "hint":
        print(current_room.get_hint())

    if not current_game_state.npcs_list==None:
        
        for npc in current_game_state.npcs_list:

            npc.roam(current_game_state)
            #print(npc.current_room)
    

    

    current_game_state.add_ending_counter()
        

    print('-'*10)

    return








room_filename= "room.json"
door_filename= "doors.json"
item_filename= "items.json"
npc_filename= "npcs.json"
game_json = "gameMsg.json"


items_list=import_items(item_filename)
rooms_list,starting_room=import_rooms(room_filename,items_list)
puzzles_list=import_doors(door_filename,rooms_list)
npcs_list=import_npcs(npc_filename,rooms_list,items_list)
intro,ending = import_gameMsg(game_json)


current_game_state=GameState(starting_room,rooms_list,items_list,npcs_list)




current_room=starting_room
previous_room=current_room


end=False



print(intro)
print('-'*10)
print(starting_room.description)
while current_game_state.loop_condition:

    verb=""
    target=""

    print('-'*10)
    text_input=input("Enter what you wanna do (exit to quit): ")
    if text_input.lower()=="exit":
        break




    verb,target=parse_input(text_input,current_game_state)

    if verb=="invalid" or target=="invalid":
        continue

    handle_input(verb,target,current_game_state)



if current_game_state.loop_condition==False:
    end=True



if end==True:

    if current_game_state.ending==0:
        print("The station rumbles around you for a moment, until everything around you is engulfed in a fiery explosion all at once. It seems you didn't escape in time.")

    else:
        print("You succesfully escape the DS-3 Orbital battle station, just as the bomb you planted detonates in the reactor room, causing a cataclysmic explosion. The station is destroyed, and a success is a success, but don't you think you could have done better?")

else:
    print("Exiting game.")





#for i in rooms_list:
    #print(i.name)
    #print(i.get_connected_rooms())
    #print(i.get_connected_doors())
    #print(i.get_door_puzzles())
    
    #print(i.inventory)
    #print()
