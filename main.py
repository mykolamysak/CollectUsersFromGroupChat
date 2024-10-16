import os
import json
import configparser
from telethon.sync import TelegramClient
from telethon.errors import (
    SessionPasswordNeededError, FloodWaitError, ChannelInvalidError, ChannelPrivateError,
    UserNotMutualContactError
)
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import User, Channel

config = configparser.ConfigParser()
config.read('config.ini')

api_id = config['pyrogram']['api_id']
api_hash = config['pyrogram']['api_hash']
session_name = 'my_session'

# Connect to telegram
client = TelegramClient(session_name, api_id, api_hash)

async def chat_exists(channel_name):
    """Checks if chat exists"""
    try:
        await client.start()  # Connect to client
        entity = await client.get_entity(channel_name)
        return isinstance(entity, (Channel, User))  # Type check
    except ChannelInvalidError:
        print(f"Error: Channel '{channel_name}' is invalid.")
    except ChannelPrivateError:
        print(f"Error: Channel '{channel_name}' is private and cannot be accessed.")
    except FloodWaitError as e:
        print(f"Error: Rate limit exceeded. Please wait {e.seconds} seconds.")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return False

async def get_members_info(channel_name):
    try:
        async with client:
            # Connect to channel
            channel_entity = await client.get_entity(channel_name)

            # Get channel info
            channel_full_info = await client(GetFullChannelRequest(channel=channel_entity))

            # Get channel participants
            participants = await client.get_participants(channel_entity)
            members_info = {}

            for participant in participants:
                if isinstance(participant, User):
                    username = participant.username if participant.username else "no_username"
                    members_info[username] = {
                        "name": participant.first_name,
                        "last_name": participant.last_name if participant.last_name else None
                    }

            # Create folder for all chats
            main_folder = "chatUsers"
            os.makedirs(main_folder, exist_ok=True)  # Check if exists

            # Create subfolder for specific chat
            chat_folder = os.path.join(main_folder, f"{channel_name}_users")

            # Check if subfolder already exists
            if os.path.exists(chat_folder):
                print(f"Folder '{chat_folder}' already exists. Data has been updated in '{chat_folder}'.\n")
            else:
                os.makedirs(chat_folder, exist_ok=True)  # if doesn't exist

            # Save to JSON
            with open(os.path.join(chat_folder, 'members.json'), 'w', encoding='utf-8') as json_file:
                json.dump(members_info, json_file, ensure_ascii=False, indent=4)

            total_count = channel_full_info.full_chat.participants_count
            print(f"Total participants: {total_count}")

            return members_info, total_count
    except ChannelInvalidError:
        print(f"Error: Unable to access channel '{channel_name}'. It might be invalid or deleted.")
    except ChannelPrivateError:
        print(f"Error: Unable to access private channel '{channel_name}'.")
    except FloodWaitError as e:
        print(f"Error: Rate limit exceeded. Please wait {e.seconds} seconds.")
    except UserNotMutualContactError:
        print("Error: Unable to access user information. This user is not a mutual contact.")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return {}, 0  # Return empty members_info and 0 total_count in case of an error

def load_names(filename):
    """Uploads names from file and returns them in lowercase"""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return {line.strip().lower() for line in file}
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return set()

def filter_gender(members_info, total_count, chat_folder):
    # Get names from DB
    male_names = load_names('genderDB/names_male.txt')
    female_names = load_names('genderDB/names_female.txt')

    male_usernames = []
    female_usernames = []
    unknown_usernames = []  # Users without username

    for username, info in members_info.items():
        first_name = info["name"]
        if first_name and first_name.lower() in male_names:
            male_usernames.append(username)
        elif first_name and first_name.lower() in female_names:
            female_usernames.append(username)
        else:
            unknown_usernames.append(username)  # No username

    # Save to .txt
    try:
        with open(os.path.join(chat_folder, 'male.txt'), 'w', encoding='utf-8') as male_file:
            for username in male_usernames:
                male_file.write(username + '\n')

        with open(os.path.join(chat_folder, 'female.txt'), 'w', encoding='utf-8') as female_file:
            for username in female_usernames:
                female_file.write(username + '\n')

        with open(os.path.join(chat_folder, 'unknown.txt'), 'w', encoding='utf-8') as unknown_file:
            for username in unknown_usernames:
                unknown_file.write(username + '\n')
    except Exception as e:
        print(f"Error while saving gender data: {e}")

    # Calculations and output
    total_users = len(members_info)
    male_count = len(male_usernames)
    female_count = len(female_usernames)
    unknown_count = len(unknown_usernames)
    users_without_username = total_count - total_users

    print(f"Total users: {total_users}")
    print(f"Male users: {male_count}")
    print(f"Female users: {female_count}")
    print(f"Unknown users: {unknown_count}")
    print(f"Users without username: {users_without_username}")

async def main():
    channel_name = input("Enter the channel or group name: ")

    # Check if chat exists
    if not await chat_exists(channel_name):
        print("Chat not found. Please check the name and try again.")
        return

    # Get participants info
    members_info, total_users = await get_members_info(channel_name)

    # Filter and save
    if members_info:
        main_folder = "chatUsers"  # Main folder for chats
        chat_folder = os.path.join(main_folder, f"{channel_name}_users")  # Subfolder for specific chat
        filter_gender(members_info, total_users, chat_folder)

# Run async method
client.loop.run_until_complete(main())
