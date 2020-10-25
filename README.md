# Music-Sorting-Telegram-Bot
Telegram Bot for sorting music


## Well, i made this project for my self, that's why i dont use async database and doing many strange things, because i just wanted to learn what i need.
It's my first serious and ended project. I understand that I have many mistakes, so feel free write to me and show something new. 

## This project is Telegram Bot based on aiogram. 
Bot allows user sort music by Artist, Album and Playlist. I did not found bot like this, so i created my own.
In this bot i use aiogram as API for telegram and sqlite3 to store all data.
There are commands for this bot:
- "create artist Jimi Hendrix" - create artist command allows you to create list where you can store other lists and music. You able to put any artist or band name instead of Jimi Hendrix

- "create album Are You Experienced" - create album, here you can collect only music. You able to put any album name instead of Are You Experienced

- "create playlist FavoritOfHendrix" - same as album, but playlist command.  You able to put any playlist name instead of FavoritOfHendrix

- "delete FavoritOfHendrix" - delete list no matter what types they are - artist, album or playlist

- "get all lists" - you will get all your lists and their types

- "add list to Are You Experienced>Jimi Hendrix" - add playlist or album to artist. After list name put ">" symbol and artist name after it, whithout space. artist and list could not have ">" in their's name

- "remove list from Are You Experienced>Jimi Hendrix" - work same as previos command, but remove list

- "get lists from artist Jimi Hendrix" - get all lists from artist that you added

- "songs to Are You Experienced" - write this command and after it send to me music, that you want me to store in selected list

- "remove songs from Are You Experienced" - work like previos command, but remove songs from selected artist

- "get list Jimi Hendrix" - send all songs from selected list. If you select artist it will also send all added lists with music in it

## As I wrote, I did not found something similar to this bot
I will not give you my bot, but feel free to use my code as you want to, let me know if you made it better and created own telegram bot
I'll be happy to use it) 

### Well, i think it's all. Bot is simple and I commented out all steps, so i don't think that i have to explain it here

Thanks, here is my ig https://www.instagram.com/lower_house/ I will use it to post my future projects
