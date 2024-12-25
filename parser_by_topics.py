"""
Update the Script with Your Credentials:
    - Replace the placeholders in the script with your actual api_id, api_hash, and phone number:
        api_id = YOUR_API_ID
        api_hash = "YOUR_API_HASH"
        phone = "YOUR_PHONE_NUMBER"


If you choose to select the group interactively, you will be shown its GROUP_ID and ACCESS_HASH
(Optional) If you want to hardcode them:
    - Update the 
    GROUP_ID
    and 
    ACCESS_HASH
    with the appropriate values for the Telegram group you want to fetch messages from.

"""

from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest, GetHistoryRequest
from telethon.tl.types import InputPeerEmpty, InputChannel
from telethon.tl.functions.channels import GetForumTopicsRequest

import csv
import datetime
import json

api_id = 456546456 # Replace with your id
api_hash = "4565bbbbcc64564556cc5646" # Replace with your hash
phone = "+76456456546" #Replace with your phone

GROUP_ID = 2438102676
ACCESS_HASH = -5124988726764050746
TOPIC_ID = 311

client = TelegramClient(phone, api_id, api_hash)
client.start()

def get_messages(group_id, access_hash, topic_id=None):
    """
    Fetches messages from a specified Telegram group.

    Args:
        group_id (int): The ID of the Telegram group.
        access_hash (int): The access hash for the Telegram group.
        topic_id (int, optional): The ID of the topic to fetch messages from. Defaults to None. Doesn't work now.

    Returns:
        tuple: A tuple containing two lists:
            - all_messages (list): A list of dictionaries with message details.
            - raw_messages (list): A list of raw message objects.
    """
    try:
        offset_id = 0
        limit = 100
        all_messages = []
        raw_messages = []

        while True:
            history = client(GetHistoryRequest(
                peer=InputChannel(group_id, access_hash),
                offset_id=offset_id,
                offset_date=None,
                add_offset=0,
                limit=limit,
                max_id=0,
                min_id=0,
                hash=0
            ))
            if not history.messages:
                break

            messages = history.messages
            
            raw_messages.extend(messages)  # Store raw messages
            for message in messages:
                    if topic_id is None or (message.reply_to and message.reply_to.reply_to_top_id == None and message.reply_to.reply_to_msg_id == topic_id) or (message.reply_to and message.reply_to.reply_to_top_id == topic_id):
                        if message.reply_to:
                            all_messages.append({
                            "id": message.id,
                            "date": message.date,
                            "sender_id": message.sender_id,
                            "text": message.message,
                            "reply_to_top_id": message.reply_to.reply_to_top_id,
                            "reply_to_message_id": message.reply_to.reply_to_msg_id,
                            "media": message.media,
                            "views": message.views,
                            "forwards": message.forwards,
                            "replies": message.replies.replies if message.replies else 0,
                            "pinned": message.pinned,
                            "edit_date": message.edit_date,
                            "post_author": message.post_author,
                            "grouped_id": message.grouped_id,
                            })
                        else:      
                            all_messages.append({
                            "id": message.id,
                            "date": message.date,
                            "sender_id": message.sender_id,
                            "text": message.message,
                            "reply_to_top_id": None,
                            "reply_to_message_id": None,
                            "media": message.media,
                            "views": message.views,
                            "forwards": message.forwards,
                            "replies": message.replies.replies if message.replies else 0,
                            "pinned": message.pinned,
                            "edit_date": message.edit_date,
                            "post_author": message.post_author,
                            "grouped_id": message.grouped_id,
                            }) 

                    offset_id = messages[-1].id
    except Exception as e:
        print(f"Error fetching messages: {type(e).__name__}: {e}")
        return [], []

    return all_messages, raw_messages

def save_messages_to_file(messages, raw_messages, filename):
    """
    Saves messages to a CSV file and a raw JSON file.

    Args:
        messages (list): A list of messages to save.
        raw_messages (list): A list of raw message objects.
        filename (str): The name of the file to save the messages to.

    Returns:
        None
    """

        # Save raw messages - Option 1
    raw_filename = filename.replace('.csv', '_raw.json')
    with open(raw_filename, "w", encoding="UTF-8") as raw_file:
        json.dump([msg.to_dict() for msg in raw_messages], raw_file, default=str, ensure_ascii=False, indent=4)
    print(f"Raw messages saved to {raw_filename}")

    # Save raw messages - Option 2
    #with open(filename.replace('.csv', '_raw.json'), "w", encoding="UTF-8") as raw_file:
    #    import json
    #    json.dump(messages, raw_file, default=str, ensure_ascii=False, indent=4)
    #print(f"Raw messages saved to raw_messages.json")


    with open(filename, "w", encoding="UTF-8") as f:
        writer = csv.writer(f, delimiter=",", lineterminator="\n")
        writer.writerow(["Message ID", "Date", "Sender ID", "Message", "Reply To Top", "Reply To", "Media", "Views", "Forwards", "Replies", "Pinned", "Edit Date", "Post Author", "Grouped ID"])
        
        for msg in messages:
            writer.writerow([
                msg["id"],
                msg["date"],
                msg["sender_id"],
                msg["text"],
                msg["reply_to_top_id"],
                msg["reply_to_message_id"],
                msg["media"],
                msg["views"],
                msg["forwards"],
                msg["replies"],
                msg["pinned"],
                msg["edit_date"],
                msg["post_author"],
                msg["grouped_id"]
            ])
    print(f"Messages saved to {filename}")

def list_groups():
    result = client(GetDialogsRequest(
        offset_date=None,
        offset_id=0,
        offset_peer=InputPeerEmpty(),
        limit=200,
        hash=0
    ))
    groups = [chat for chat in result.chats if getattr(chat, 'megagroup', False)]
    print("Available groups:")
    for i, group in enumerate(groups):
        print(f"{i} - {group.title}")
    return groups

def list_topics(group_id, access_hash):
    group = InputChannel(group_id, access_hash)
    try:
        result = client(GetForumTopicsRequest(
            channel=group,
            offset_date=None,
            offset_id=0,
            offset_topic=0,
            limit=100
        ))
        if not result.topics:
            print("No topics found in this group.")
            return []
        print("\nAvailable topics:")
        print("\n-1 - all topics")
        for i, topic in enumerate(result.topics):
            print(f"{i} - {topic.title} (ID: {topic.id})")
        return result.topics
    except Exception as e:
        print(f"Error fetching topics: {type(e).__name__}: {e}")
        return []

def get_group_name(group_id, access_hash):
    """Fetch the group name using group ID and access hash."""
    try:
        result = client(GetDialogsRequest(
            offset_date=None,
            offset_id=0,
            offset_peer=InputPeerEmpty(),
            limit=200,
            hash=0
        ))
        for chat in result.chats:
            if chat.id == group_id and chat.access_hash == access_hash:
                return chat.title
        return "Unknown_Group"
    except Exception as e:
        print(f"Error fetching group name: {type(e).__name__}: {e}")
        return "Unknown_Group"

def get_topic_name(group_id, access_hash, topic_id):
    """Fetch the topic name using group ID, access hash, and topic ID."""
    try:
        group = InputChannel(group_id, access_hash)
        result = client(GetForumTopicsRequest(
            channel=group,
            offset_date=None,
            offset_id=0,
            offset_topic=0,
            limit=100
        ))
        for topic in result.topics:
            if topic.id == topic_id:
                return topic.title
        return "Unknown_Topic"
    except Exception as e:
        print(f"Error fetching topic name: {type(e).__name__}: {e}")
        return "Unknown_Topic"

def main():
    print("Choose an option:")
    print("1 - Use hardcoded group and topic details")
    print("2 - Select group and topic interactively")
    choice = int(input("Enter your choice: "))

    if choice == 1:
        # Hardcoded values
        group_id = GROUP_ID
        access_hash = ACCESS_HASH
        topic_id = TOPIC_ID
        group_name = get_group_name(group_id, access_hash)
        topic_name = get_topic_name(group_id, access_hash, topic_id) if topic_id else "all"
    elif choice == 2:
        # Interactive selection
        groups = list_groups()
        group_index = int(input("\nEnter the number of the group: "))
        selected_group = groups[group_index]
        group_id = selected_group.id
        access_hash = selected_group.access_hash
        group_name = selected_group.title
        print(f"\nSelected Group: {group_name}")


        topics = list_topics(group_id, access_hash)
        if not topics:
            print("This group has no topics. Fetching all group messages.")
            topic_id = None
            topic_name = "all"
        else:
            topic_index = int(input("\nEnter the number of the topic: "))
            if topic_index == -1:
                topic_id = None
                topic_name = "all"
            else:
                selected_topic = topics[topic_index]
                topic_id = selected_topic.id
                topic_name = selected_topic.title
            print(f"\nSelected Topic: {topic_name}")

    else:
        print("Invalid choice.")
        return

    # Fetch messages
    print(f"\nGroup ID: {group_id}")
    print(f"Group Access Hash: {access_hash}")
    print(f"Group Name: {group_name}")
    if topic_id:
        print(f"Topic ID: {topic_id}")
        print(f"Topic Name: {topic_name}")

    messages, raw_mesages = get_messages(group_id, access_hash, topic_id)
    print(f"\nFetched {len(messages)} messages.")
    if messages:
        save_messages_to_file(messages, raw_mesages, f"messages_{group_name.replace(' ', '_')}_topic_{topic_name.replace(' ', '_')}.csv")
    else:
        print("No messages found.")

if __name__ == "__main__":
    main()