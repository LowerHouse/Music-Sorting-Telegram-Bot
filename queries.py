import sqlite3

#creating unic table for new user and inserting his id into users table
async def new_user(id):
    #check if user already registered
    users = get_all_users()
    id = f'user{id}'
    if id not in users:
        #creating new, unic table for user
        conn = sqlite3.Connection('UnicTable.db')
        c = conn.cursor()
        c.execute(f"""
            CREATE TABLE {id} (
            	name TEXT NOT NULL,
            	type TEXT NOT NULL,
            	songs TEXT,
                unic_song_id TEXT,
                list_id TEXT,
                PRIMARY KEY(name)
                ); """)

        #Insert user into users table
        c.execute("""
        INSERT INTO users VALUES (?, ?, ?, ?);
        """, (id, '', '', '') )
        conn.commit()
        conn.close()

#get all users id whithout 'user' in one list
def get_all_users():
    users_list = []
    conn = sqlite3.Connection('UnicTable.db')
    c = conn.cursor()
    c.execute("""

    SELECT user_id FROM users

    """)
    items = c.fetchall()
    for item in items:
        id = ''.join(item)
        users_list += [id[4:]]

    conn.close()
    return users_list

#adding new list into user table
def add_new_list(id, list_name, type):
    id = f'user{id}'
    conn = sqlite3.Connection('UnicTable.db')
    c = conn.cursor()

    if list_name not in lists_names(id[4:]):

        #creating unic list id

        c.execute(f"""
        INSERT INTO {id} VALUES (?, ?, ?, ?, ?)
        """, (list_name, type, '', '', ''))

        conn.commit()
        conn.close()

# Count of all lists that user have
def list_count(id):
    conn = sqlite3.Connection('UnicTable.db')
    c = conn.cursor()
    c.execute(f"""
    SELECT COUNT(name) FROM user{id}
    """)
    return c.fetchone()[0]

#deleting user UnicTable and user id from users
def delete_user(id):
    id = f'user{id}'
    conn = sqlite3.Connection('UnicTable.db')
    c = conn.cursor()

    c.execute(f"""
    DROP TABLE IF EXISTS {id}
    """)


    c.execute(f"DELETE FROM users WHERE user_id = '{id}'")

    conn.commit()
    conn.close()

#finding all lists by label(name) and collecting labels in list
def lists_names(id):

        label_list = []
        id = f'user{id}'
        conn = sqlite3.Connection('UnicTable.db')
        c = conn.cursor()

        c.execute(f"""
        SELECT name FROM {id}
        """)
        items = c.fetchall()
        for item in items:
            label_list += [item[0]]

        conn.commit()
        conn.close()

        return label_list

#this func is for users, it shows to them all lists they have
def list_names_types(id):
    name_list = []
    type_list = []
    id = f'user{id}'
    conn = sqlite3.Connection('UnicTable.db')
    c = conn.cursor()

    c.execute(f"""
        SELECT name, type FROM {id} ORDER BY type
    """)
    items = c.fetchall()
    #collecting names and type to two lists
    for key, value in items:
        name_list += [key]
        type_list += [value]

    conn.close()

    return dict(zip(name_list, type_list))


#delete list from user tabel by name
def delete_list(id, list_name):
    id = f'user{id}'
    conn = sqlite3.Connection('UnicTable.db')
    c = conn.cursor()
    c.execute(f"SELECT rowid from {id} WHERE name = '{list_name}'")
    list_rowid = f'{c.fetchone()[0]}'
    new_list = ''
    # We need flag to chek that we added smth in new_list
    Flag = 0
    for artist, type in list_names_types(id[4:]).items():
        if type == 'artist':
            if is_list_in(id[4:], list_name, artist):
                #Flag is 1 if we passed all "if" requirments, so we will know that we have to set new list
                Flag = 1

                previos_list = artist_lists(id[4:], artist)[0]
                previos_list = previos_list.split('|')
                previos_list.remove(list_rowid)
                for unic_id in previos_list[1:]:
                    new_list += f'|{unic_id}'
    #we can update data if something changed
    if Flag == 1 :
        c.execute(f"""
            UPDATE {id} SET list_id = '{new_list}' WHERE name = '{artist}'
        """)




    c.execute(f" DELETE FROM {id} WHERE name = '{list_name}'")
    conn.commit()
    conn.close()

#add list by list_id to artist
def list_to_artist(id, list_name, artist_name):

    check = list_names_types(id).get(list_name)
    id = f'user{id}'
    if check != 'artist':
        conn = sqlite3.Connection('UnicTable.db')
        c = conn.cursor()


        c.execute(f"""
        SELECT rowid FROM {id} WHERE name = '{list_name}'
        """)
        list_rowid = int(c.fetchone()[0])

        c.execute(f"""
        SELECT list_id FROM {id} WHERE name = '{artist_name}'
        """)

        previos_lists = str(c.fetchone()[0])

        all_lists = f'{previos_lists}|{list_rowid}'
        c.execute(f"UPDATE {id} SET list_id = '{all_lists}' WHERE name = '{artist_name}'")

        conn.commit()
        conn.close()
    else:
        return 'you can not add artist to artist'

#get list of lists added to artist (just row id)
def artist_lists(id, artist_name):
    added = []
    id = f'user{id}'
    conn = sqlite3.Connection('UnicTable.db')
    c = conn.cursor()

    c.execute(f"""
        SELECT list_id FROM {id} WHERE name = '{artist_name}'
    """)
    items = c.fetchall()
    for item in items:
        added += item

    conn.close()
    return added

#chek if list is already in artist
def is_list_in(id, list_name, artist_name):
    id = f'user{id}'
    conn = sqlite3.Connection('UnicTable.db')
    c = conn.cursor()
    c.execute(f"""
        SELECT rowid FROM {id} WHERE name = '{list_name}'
    """)
    list_id = c.fetchone()[0]
    conn.close()
    lists_in = artist_lists(id[4:], artist_name)[0]
    lists_in = lists_in.split('|')
    if f'{list_id}' in lists_in:
        return True
    else:
        return False

#get all names of added lists
def names_of_added_lists(id, artist_name):
    name_list = []
    parsed_id_list = []
    artists_lists = str(artist_lists(id, artist_name))
    artists_lists = artists_lists.replace('[', '')
    artists_lists = artists_lists.replace(']', '')
    artists_lists = artists_lists.replace('\'', '')
    artists_lists = artists_lists.split('|')

    id = f'user{id}'
    for list_id in artists_lists:
        parsed_id_list += list_id
    conn = sqlite3.Connection('UnicTable.db')
    c = conn.cursor()

    for ids in artists_lists[1:]:

        c.execute(f"""
        SELECT name FROM {id} WHERE rowid = '{ids}'
        """)
        single_id = c.fetchone()
        if single_id is not None:

            name_list += single_id

    conn.close()
    return name_list

#delete list from artists list_id column
def del_list_from_artist(id,list_name, artist_name):
    id = f'user{id}'
    conn = sqlite3.Connection('UnicTable.db')
    c = conn.cursor()
    c.execute(f"SELECT rowid from {id} WHERE name = '{list_name}'")
    list_rowid = f'{c.fetchone()[0]}'
    new_list = None

    if is_list_in(id[4:], list_name, artist_name):
        new_list = ''
        #collect all lists from artist
        previos_list = artist_lists(id[4:], artist_name)[0]
        previos_list = previos_list.split('|')
        #remove from previos list selected list
        previos_list.remove(list_rowid)
        for unic_id in previos_list[1:]:
            #creating new list of lists without removed list XD
            new_list += f'|{unic_id}'
    if new_list != None:
        c.execute(f"""
            UPDATE {id} SET list_id = '{new_list}' WHERE name = '{artist_name}'
        """)
    conn.commit()
    conn.close()

#add song file id and file unique id.
#we need both because file id differend for each message, but we can send music as audio with it
# file unique id will be same, so we can remove song by it from Database
def add_song(id, song_id, song_unic_id, list_name):
    id = f'user{id}'
    conn = sqlite3.Connection('UnicTable.db')
    c = conn.cursor()

    #collecting previos lists fist
    c.execute(f"""
    SELECT unic_song_id FROM {id} WHERE name = '{list_name}'
    """)

    previos_unic_list = str(c.fetchone()[0])

    new__unic_list = f'{previos_unic_list}|{song_unic_id}'
    c.execute(f"""
    SELECT songs FROM {id} WHERE name = '{list_name}'
    """)

    previos_list = str(c.fetchone()[0])

    #update with new list
    new_list = f'{previos_list}|{song_id}'
    c.execute(f"""
        UPDATE {id} SET songs = '{new_list}' WHERE name = '{list_name}'
    """)

    c.execute(f"""
        UPDATE {id} SET unic_song_id = '{new__unic_list}' WHERE name = '{list_name}'
    """)


    conn.commit()
    conn.close()

#return file id of songs in list
def get_songs(id, list_name):
    songs = []
    id = f'user{id}'
    conn = sqlite3.Connection('UnicTable.db')
    c = conn.cursor()

    c.execute(f"""
        SELECT songs FROM {id} WHERE name = '{list_name}'
    """)
    added = c.fetchone()[0]
    added = added.split('|')
    conn.close()
    return added[1:]

#set current name to users table, explained why in "bot.py"
def set_current_name(id, list_name):
    id = f'user{id}'
    conn = sqlite3.Connection('UnicTable.db')
    c = conn.cursor()

    c.execute(f"""
        UPDATE users SET current_name = '{list_name}' WHERE user_id = '{id}'
    """)

    conn.commit()
    conn.close()

#get name of current list to add it in functions in "bot.py"
def get_current_name(id):
    id = f'user{id}'
    conn = sqlite3.Connection('UnicTable.db')
    c = conn.cursor()

    c.execute(f"""
        SELECT current_name FROM users WHERE user_id = '{id}'
    """)
    current_name = c.fetchone()[0]

    conn.close()

    return current_name

#dict that collect songs file id and file unique id from list
def get_songs_dict(id, list_name):
    song_dict = {}
    id = f'user{id}'
    conn = sqlite3.Connection('UnicTable.db')
    c = conn.cursor()

    c.execute(f"""
        SELECT unic_song_id FROM {id} WHERE name = '{list_name}'
    """)

    unic_added = c.fetchone()[0]
    unic_added = unic_added.split('|')


    c.execute(f"""
        SELECT songs FROM {id} WHERE name = '{list_name}'
    """)

    added = c.fetchone()[0]
    added = added.split('|')
    song_dict = dict(zip(unic_added[1:], added[1:]))

    conn.close()

    return song_dict

# remove song from list by file unique id
def delete_song_from(id, list_name, song_unic_id):
    id = f'user{id}'

    conn = sqlite3.Connection('UnicTable.db')
    c = conn.cursor()

    new_dict = get_songs_dict(id[4:], list_name)
    new_dict.pop(song_unic_id)
    songs_list = ''
    unic_id_list = ''
    for key, value in new_dict.items():
        songs_list += f'|{value}'
        unic_id_list += f'|{key}'

    c.execute(f"""
        UPDATE {id} SET songs = '{songs_list}' WHERE name = '{list_name}'
    """)

    c.execute(f"""
        UPDATE {id} SET unic_song_id = '{unic_id_list}' WHERE name = '{list_name}'
    """)


    conn.commit()
    conn.close()
