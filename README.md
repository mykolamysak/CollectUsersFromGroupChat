# Telegram Chat User Extractor

This project in Python uses the Telethon library to collect information about users from Telegram channels and groups. The program checks for the existence of a chat, retrieves participant information, and saves this data in JSON and text files.

## Features

- **Chat Existence Check**: The program verifies whether the specified channel or group exists and whether it is private.
- **Participant Information Retrieval**: Gathers user data, including first names, last names, and usernames (if available).
- **Data Saving**: Participant information is saved in a `chatUsers` folder in the following formats:
  - `members.json`: All participants with names and surnames.
  - `male.txt`, `female.txt`, `unknown.txt`: Users sorted by gender based on names.
- **Reporting**: Outputs statistics about participants, including total counts, number of male and female users, and users without usernames.

## Requirements

- Python 3.7+
- Libraries:
  - `Telethon`
  - `configparser`
  - `json`
  - `os`
