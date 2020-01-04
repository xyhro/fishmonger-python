import discord
import re
import time
import numpy as np
from firebase_admin import firestore
import firebase_admin
from firebase_admin import credentials
cred = credentials.Certificate('./fishmonger-49d2e-firebase-adminsdk-ho0me-9248a41c5f.json')
firebase_admin.initialize_app(cred)

db = firestore.client()
users =  db.collection('players')
players = users.stream()

client = discord.Client()
token = 'NDk5NzAyNzc0NTU3MzEwOTg3.XgjAzA.V3wdrBVcbXK7VZbLghm3X9KdxZg' #shenanigans
#token = 'NTgzMTA4Njk0NDM1Mjk5MzMw.XO3ocA.kKTy60g0CQwRzNfh292NbbrTBgI' #chakbot

class Players:

    max_stamina = 20
    def __init__(self,userid,health,stamina,kills,deaths,gold,updatetime):
        self.userid = userid
        self.health = health
        self.stamina = stamina
        self.kills = kills
        self.deaths = deaths
        self.gold = gold
        self.updatetime = time.time()


'''populate teh game for testing purposes; that is all'''
def populate_game(count):
    x= 0
    while x != count:
        newplayer = Players(np.random.randint(100000,10000000),20,20,0,0,0,time.time())
        db.collection('players').document(str(newplayer.userid)).set(newplayer.__dict__)
        x+=1


def exists1(hitter):
    if db.collection('players').document(str(hitter)).get().exists == True:
        print('hitter exists')
    else:
        newplayer = Players(hitter,20,20,0,0,0,time.time())
        db.collection('players').document(str(hitter)).set(newplayer.__dict__)
        print('hitter does not exist and has been made')

def exists2(target):
    if db.collection('players').document(str(target)).get().exists == True:
        print('target exists')
    else:
        newplayer = Players(target,20,20,0,0,0,time.time())
        db.collection('players').document(str(target)).set(newplayer.__dict__)
        print('target does not exist and has been made')
''' check existance, update stamina stats based on time, slap'''
def exists(hitter,target):
    exists1(hitter)
    exists2(target)


def slap(hitter,target,damage):
    exists(hitter,target)
    the_rekt = db.collection('players').document(str(target)).get().to_dict()
    the_hit = db.collection('players').document(str(hitter)).get().to_dict()
    thresholdtime = int((time.time() - the_hit['updatetime']) / 300)
    if thresholdtime > 0:
        the_hit['stamina'] += thresholdtime
        db.collection('players').document(str(hitter)).update({'updatetime': time.time()})

    if the_hit['stamina'] > 20:
        the_hit['stamina'] = 20
    if the_hit['stamina'] == 0:
        return 1
    else:
        the_rekt['health'] -= damage
        the_hit['stamina'] -= 1
        print('stamina decreased')
        if the_rekt['health']< 1:
            the_rekt['deaths']+=1
            the_hit['kills'] +=1
            db.collection('players').document(str(target)).update({'health': 20, 'deaths':the_rekt['deaths']})
            db.collection('players').document(str(hitter)).update({'stamina': the_hit['stamina'], 'kills':the_hit['kills']})
            return 2
        else:
            db.collection('players').document(str(target)).update({'health': the_rekt['health']})
            db.collection('players').document(str(hitter)).update({'stamina': the_hit['stamina']})
            return 3


@client.event
async def on_ready():
    print('logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.content.find ('/slap <@') != -1:
        hitter = message.author.id
        target = re.search('\d{18}>$',message.content).group().split('>')[0]
        if str(hitter) == str(target):
            await message.channel.send(" don't slap yourself idiot")
            return
        else:
            damage = np.random.randint(1, 3)
            result = slap(hitter,target,damage)
            if result == 1:
                await message.channel.send ('you are literally too tired to slap')
            if result == 3:
                newhealth=db.collection('players').document(str(target)).get().to_dict()
                embed = discord.Embed(title = message.author.display_name , description = '<@!{}> slaps <@!{}> around with a bit with a large rubber trout'.format(message.author.id,target),color=0x00ff00)
                embed.add_field(name='Damage',value = damage,inline= True)
                embed.add_field (name ='{} new hp'.format(client.get_user(int(target)).display_name), value = newhealth['health'] , inline=True)
                await message.channel.send(embed=embed)
            if result == 2:
                newhealth=db.collection('players').document(str(target)).get().to_dict()
                embed = discord.Embed(title = message.author.display_name , description = '<@!{}> slaps <@!{}> around with a bit with a large rubber trout \n \n  **{} has died**'.format(message.author.id,target,client.get_user(int(target)).display_name),color=0x00ff00)
                embed.add_field(name='Damage',value = damage,inline= True)
                embed.add_field (name ='{} new hp'.format(client.get_user(int(target)).display_name), value = 0 , inline=True)
                await message.channel.send(embed=embed)


    if message.content.find ('/stats') !=-1:
        author = message.author.id
        timeupdate = db.collection('players').document(str(author)).get().to_dict()
        thresholdtime = int((time.time() - timeupdate['updatetime']) / 300)
        if thresholdtime > 0:
            timeupdate['stamina'] += thresholdtime
            db.collection('players').document(str(author)).update({'updatetime': time.time()})
        if timeupdate['stamina'] > 20:
            timeupdate['stamina'] = 20
        db.collection('players').document(str(author)).update({'stamina': timeupdate['stamina']})
        stats = db.collection('players').document(str(author)).get().to_dict()
        embed = discord.Embed(title = message.author.display_name, description="{}'s current stats".format(message.author.display_name))
        embed.add_field(name='Health', value = stats['health'], inline=True)
        embed.add_field(name='Stamina', value = stats['stamina'],inline = True)
        embed.add_field(name= 'Kills', value = stats['kills'],inline = True)
        embed.add_field(name= 'Deaths',value = stats['deaths'],inline = True)
        await message.channel.send(embed=embed)




    print(message.author.id) #message author name#0000
    print(message.content)  # message content


    if message.author == client.user:
        return



client.run(token)