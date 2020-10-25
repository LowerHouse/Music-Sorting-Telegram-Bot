from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import ContentType
from aiogram.utils import executor
from aiogram.utils.markdown import text, bold, italic, code, pre
from aiogram.types import ParseMode, Audio


from config import TOKEN
import queries

import sqlite3

#creating main table, that store all users
conn = sqlite3.Connection('UnicTable.db')
c = conn.cursor()

c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT NOT NULL,
        user_status INTEGER,
        list_sum INTEGER,
        current_name TEXT,

        PRIMARY KEY(user_id)
        );
""")

conn.commit()
conn.close()


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

#handle all audio input to bot
@dp.message_handler(content_types = ContentType.AUDIO )
async def audio_saver(message: types.Message):
    id = message.chat.id
    #getting all usefull stuf that we will need to save audio into Database
    file_unique_id = message.audio.file_unique_id
    file_id = message.audio.file_id
    #getting name of list where user wanna save music
    current_name = queries.get_current_name(id)

#checking what user wanna do, delete or add music
    if current_name != '' and not current_name.startswith('DELETE1DELETE2DELETE3DELETE4DELETE5') and current_name in queries.lists_names(id):

        #add song to current list
        queries.add_song(id, file_id,file_unique_id, current_name)
        await message.reply(f'song added to {current_name}', parse_mode=ParseMode.MARKDOWN)

    elif current_name.startswith('DELETE1DELETE2DELETE3DELETE4DELETE5') and current_name[36:] in queries.lists_names(id) :
        #delete song from current list
        if file_unique_id in queries.get_songs_dict(id, current_name[36:]):
            queries.delete_song_from(id, current_name[36:], file_unique_id)
            await message.reply(f'song deleted from {current_name[36:]}', parse_mode=ParseMode.MARKDOWN)
    #if there is no current list, we need to say it to user
    else:
        await message.reply('use first comand "songs to" to select list where songs have to be\n or comand "remove songs from" to remove song from list', parse_mode=ParseMode.MARKDOWN)

#handle start command
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    id = message.chat.id
    await message.reply('Use \'/help\', to find out what i can.')
    #creating new user table
    await queries.new_user(id)


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    msg = '''
"create artist Jimi Hendrix" - create artist command allows you to create list where you can store other lists and music. You able to put any artist or band name instead of Jimi Hendrix
------------------------------
"create album Are You Experienced" - create album, here you can collect only music. You able to put any album name instead of Are You Experienced
------------------------------
"create playlist FavoritOfHendrix" - same as album, but playlist command.  You able to put any playlist name instead of FavoritOfHendrix
------------------------------
"delete FavoritOfHendrix" - delete list no matter what types they are - artist, album or playlist
------------------------------
"get all lists" - you will get all your lists and their types
------------------------------
"add list to Are You Experienced>Jimi Hendrix" - add playlist or album to artist. After list name put ">" symbol and artist name after it, whithout space. artist and list could not have ">" in their's name
------------------------------
"remove list from Are You Experienced>Jimi Hendrix" - work same as previos command, but remove list
------------------------------
"get lists from artist Jimi Hendrix" - get all lists from artist that you added
------------------------------
"songs to Are You Experienced" - write this command and after it send to me music, that you want me to store in selected list
------------------------------
"remove songs from Are You Experienced" - work like previos command, but remove songs from selected artist
------------------------------
"get list Jimi Hendrix" - send all songs from selected list. If you select artist it will also send all added lists with music in it
    '''
    await message.reply(msg)


#handle all commands
@dp.message_handler()
async def doing_job(message: types.Message):
    #saving chat id, we will need it in all commands to get information from current user
    id = message.chat.id

    #all explained in "queries.py" here i just get input from user, nothing serious
    if message.text.lower().startswith('create artist'):
        artist_name = message.text[14:]
        type = 'artist'
        queries.add_new_list (id, artist_name, type)
        msg = text(bold(f'Artist list \'{artist_name}\' created'))
        await message.reply(msg, parse_mode=ParseMode.MARKDOWN)


    elif message.text.lower().startswith('create album'):
        album_name = message.text[13:]
        type = 'album'
        queries.add_new_list (id, album_name, type)
        msg = text(bold(f'Album list \'{album_name}\' created'))
        await message.reply(msg, parse_mode=ParseMode.MARKDOWN)

    elif message.text.lower().startswith('create playlist'):
        playlist_name = message.text[16:]
        type = 'playlist'
        queries.add_new_list (id, playlist_name, type)
        msg = text(bold(f'Playlist \'{playlist_name}\' created'))
        await message.reply(msg, parse_mode=ParseMode.MARKDOWN)

#deleting list
    elif message.text.lower().startswith('delete'):
        list_name = message.text[7:]
        #checking is this list exists
        if list_name in queries.lists_names(id):
            queries.delete_list(id, list_name)
            msg = text(bold(f'\'{list_name}\' is deleted'))
            await message.reply(msg, parse_mode=ParseMode.MARKDOWN)
        else:
            msg = text(bold(f'list named \'{list_name}\' is not exists\nremember, "music list" and "Music list" are two differend lists'))
            await message.reply(msg, parse_mode=ParseMode.MARKDOWN)

    elif message.text.lower().startswith('get all lists'):
        #look stupid, I know
        get_lists = str(queries.list_names_types(id))
        get_lists = get_lists.replace('{', '')
        get_lists = get_lists.replace('}', '')
        get_lists = get_lists.replace(', ', '\n')
        get_lists = get_lists.replace('\'', '')
        await message.reply(get_lists, parse_mode=ParseMode.MARKDOWN)

    elif message.text.lower().startswith('add list to'):
        name = message.text[12: ]
        #split by ">" and collect list artist names
        name = name.split('>')
        list_name = name[0]
        artist_name = name[1]
        #chek and add if all fine
        if list_name in queries.lists_names(id) and artist_name in queries.lists_names(id):
            if queries.is_list_in(id, list_name, artist_name) is False:
                queries.list_to_artist(id, list_name, artist_name)
                await message.reply('successfully added', parse_mode=ParseMode.MARKDOWN)
            else:
                await message.reply('already added', parse_mode=ParseMode.MARKDOWN)
        else:
            await message.reply('list not exists', parse_mode=ParseMode.MARKDOWN)

#this one will send to user all lists from artist
    elif message.text.lower().startswith('get lists from artist'):
        artist_name = message.text[22: ]

        #creating stroke that bot will send to user
        all_names = f'Here is your lists in \'{artist_name}\'\n'

        if  artist_name in queries.list_names_types(id):

            list_of_lists = queries.names_of_added_lists(id, artist_name)

            #add to stroke all lists that are in artist list
            for list in list_of_lists:
                all_names += f'{list}\n'

            await message.reply(all_names, parse_mode=ParseMode.MARKDOWN)
        else:
            await message.reply('Artist not exists', parse_mode=ParseMode.MARKDOWN)

#removing list from artist
    elif message.text.lower().startswith('remove list from'):
        name = message.text[17: ]

        name = name.split('>')
        #pretty same as "add list to" command
        list_name = name[0]
        artist_name = name[1]
        if list_name in queries.lists_names(id) and artist_name in queries.lists_names(id):
            if queries.is_list_in(id, list_name, artist_name):
                queries.del_list_from_artist(id, list_name, artist_name)
                await message.reply('successfully removed', parse_mode=ParseMode.MARKDOWN)
            else:
                await message.reply('list was not in', parse_mode=ParseMode.MARKDOWN)
        else:
            await message.reply('list not exists', parse_mode=ParseMode.MARKDOWN)

#after this one all sended by user songs will be added to selected list
    elif message.text.lower().startswith('songs to'):
        if message.text[9:] in queries.lists_names(id):
            current_name = message.text[9:]
            #set curent name in users table, so bot will know where have to be songs that user will send
            queries.set_current_name(id, current_name)
            await message.reply(f'songs will be added to {current_name}', parse_mode=ParseMode.MARKDOWN)
        else:
            await message.reply('list not exists', parse_mode=ParseMode.MARKDOWN)

#after this, all sended by user songs will be removed from selected list
    elif message.text.lower().startswith('remove songs from'):
        if message.text[18:] in queries.lists_names(id):
            # XD look stupid, to know that we wanna remove songs from list i add secret words in current name
            current_name = f'DELETE1DELETE2DELETE3DELETE4DELETE5 {message.text[18:]}'
            queries.set_current_name(id, current_name)
            await message.reply(f'send to me songs that you wanna delete from {message.text[18:]}', parse_mode=ParseMode.MARKDOWN)
        else:
            await message.reply(f'list {current_name} not exists', parse_mode=ParseMode.MARKDOWN)


#after this one, bot will send all music that list collect
    elif message.text.lower().startswith('get list'):
        list_name = message.text[9:]
        if list_name in queries.lists_names(id):
            #we have to chek what type of list  user sended
            if queries.list_names_types(id).get(list_name) == 'artist':
                #if it's artist we have to get all lists added in, to send music from them too
                lists = queries.names_of_added_lists(id, list_name)

                #sending lists, types of lists and  music from them
                for list in lists:
                    type = queries.list_names_types(id).get(list)
                    await bot.send_message(id, f'{list} : {type}')
                    song_list = queries.get_songs(id, list)
                    for song in song_list:
                        await Bot.send_audio(bot, id, song)

                #send music that added to artist
                song_list = queries.get_songs(id, list_name)
                for song in song_list:
                    await Bot.send_audio(bot, id, song)

            #if sended list is not artist we just send all music from list
            else:
                song_list = queries.get_songs(id, list_name)
                for song in song_list:
                    await Bot.send_audio(bot, id, song)

        else:
            await message.reply(f'list {list_name} not exists', parse_mode=ParseMode.MARKDOWN)



    #if user wrote smth else bot will tell that user has to chek commands
    else:
        await message.reply(bold('Please check commands by /help command, something is wrong!'), parse_mode=ParseMode.MARKDOWN)

#handle other types to say that this bot does not work with them
@dp.message_handler(content_types = ContentType.ANY)
async def any_type(message: types.Message):
    await message.reply('Bot accept only audio type, no voice or any else', parse_mode=ParseMode.MARKDOWN)

if __name__ == '__main__':
    executor.start_polling(dp)
