import discord
from discord.ext import commands
from discord.utils import get
from yt_dlp import YoutubeDL
import os
import shutil
from youtubesearchpython import VideosSearch
import asyncio
import typing

TOKEN=''


ydl_op = {
        'format' : 'bestaudio/best',
    }
FFMPEG_OPTIONS = {'options': '-vn'}
ydl = YoutubeDL(ydl_op)
lista=[]

intents = discord.Intents.all()
bot=commands.Bot(command_prefix='.',intents=intents)


def search_yt(item):
    if item.startswith("https://"):
        cancion = ydl.extract_info(item, download=False)
        title=cancion["title"]
        url=cancion["url"]
        return{'URL':url, 'titulo':title}
    search = VideosSearch(item, limit=1)
    link=search.result()["result"][0]["link"]
    print(link)
    cancion=ydl.extract_info(link,download=False)
    title=cancion["title"]
    url=cancion["url"]
    return{'URL':url, 'titulo':title}   

@bot.event
async def on_ready():
    await bot.change_presence(activity = discord.Game(name=''))
    print('esta vivo')


@bot.command(pass_context = True)
async def conectar(ctx):
    if ctx.author.voice is None:
        await ctx.send("¡Debes estar en un canal de voz para que pueda unirme!")
        return
    canal = ctx.author.voice.channel

    voz= get(bot.voice_clients,guild=ctx.guild)
    if voz and voz.is_connected():
        await voz.move_to(canal)
        await ctx.send(f"¡Conectado al canal de voz {canal}!")
    else:
        await canal.connect()
        await ctx.send(f"¡Conectado al canal de voz {canal}!")

@bot.command(pass_context = True)
async def desconectar(ctx):
    if ctx.voice_client is None:
        await ctx.send("¡No estoy en un canal de voz!")
        return
    await ctx.voice_client.disconnect()
    await ctx.send("¡Desconectado del canal de voz!")

#pasar cancion
def revisar_lista(ctx):
    voice = get(bot.voice_clients,guild = ctx.guild)
    global lista
    if len(lista)==0:
        return
    lista.pop(0)
    if len(lista) > 0:
        song=lista[0]
        cancion=song['URL']
        voice.play(discord.FFmpegPCMAudio(cancion,executable='ffmpeg',**FFMPEG_OPTIONS),after=lambda e: revisar_lista(ctx))





@bot.command(pass_context = True)
async def play(ctx, *args):
    
    global lista

    query= " ".join(args)
    if query.find("&list=")!=-1:
        query=query[0:query.find("&list=")]
    song = search_yt(query)
    #CONECTAR CANAL
    if ctx.author.voice is None:
        await ctx.send("¡Debes estar en un canal de voz para que pueda unirme!")
        return
    canal = ctx.author.voice.channel

    voz= get(bot.voice_clients,guild=ctx.guild)
    if voz and voz.is_connected():
        await voz.move_to(canal)
    else:
        await canal.connect()
   
    if len(lista)>0:
        lista.append(song)

        await ctx.send("Añadida la cancion "+str(song['titulo'])+" a la lista de reproduccion")\
        
        print("cancion añadida")
        return
    #
    
    lista.append(song)
    voice = get(bot.voice_clients,guild = ctx.guild)
    
    cancion=song['URL']
    voice.play(discord.FFmpegPCMAudio(cancion,executable='ffmpeg',**FFMPEG_OPTIONS),after=lambda e: revisar_lista(ctx))

    await ctx.send(f"reproduciendo: {song['titulo']}")
    print("Reproduciendo \n")

            
                    



@bot.command(pass_context = True)
async def pausa(ctx):
    voz= get(bot.voice_clients,guild=ctx.guild)
    if voz and voz.is_playing():
        print("musica pausada")
        voz.pause()
        await ctx.send("musica pausada")
    else:
        print("No se esta reproduciendo, pausa erronea")
        await ctx.send("No se esta reproduciendo, pausa erronea")

@bot.command(pass_context = True)
async def resume(ctx):
    voz= get(bot.voice_clients,guild=ctx.guild)
    if voz and voz.is_paused():
        print("Reproduciendo nuevamente")
        voz.resume()
        await ctx.send("Reproduciendo nuevamente")
    else:
        print()
        await ctx.send("No se encuentra pausada, no se puede continuar")

@bot.command(pass_context = True)
async def stop(ctx):
    voz= get(bot.voice_clients,guild=ctx.guild)
    if voz and voz.is_playing():
        print("musica detenida")
        voz.stop()
        await ctx.send("Musica detenida")
    else:
        print("No se esta reproduciendo, no se puede detener")
        await ctx.send("No se esta reproduciendo")

@bot.command(pass_context = True)
async def skip(ctx):
    global lista
    voice = get(bot.voice_clients,guild=ctx.guild)
    if voice and voice.is_playing():
        if len(lista) > 1:
            voice.stop()
            lista.pop(0)
            if len(lista) > 0:
                song=lista[0]
                cancion=song['URL']
                voice.play(discord.FFmpegPCMAudio(cancion,executable='ffmpeg'),after=lambda e: revisar_lista(ctx))
        else:
            await ctx.send("No mas canciones en la lista")

@bot.command(pass_context = True)
async def cola(ctx):
    q=""
    global lista
    num=0
    for cancion in lista:
        if num==0:
            num+=1
            q += f"Sonando : {cancion['titulo']} \n"
        else:
            q += f"{num} : {cancion['titulo']} \n"
            num+=1
    await ctx.send(q)

@bot.command(pass_context=True,name="remove", help="Remueve ultima cancion")
async def re(ctx,num : typing.Optional[int] = None):
    global lista
    if num is None:
        if len(lista)>1:
            lista.pop()
            await ctx.send("Ultima cancion eliminada")
        else:
            await ctx.send("Lista vacia")
    else:
        if len(lista)>1:
            if num >0 and num<len(lista):
                lista.pop()
                await ctx.send("Cancion eliminada")
        else:
            await ctx.send("Lista vacia")
@bot.event
async def on_voice_state_update(member, before, after):
    global lista
    if after.channel is None and member==bot.user:
        voice = get(bot.voice_clients)
        voice.stop()
        lista=[]

@bot.command(pass_context=True)
async def clear(ctx):
    global lista
    if len(lista)>0:
        cancion=lista[0]
        lista=[]
        lista.append(cancion)
        await ctx.send("Lista limpia")
    else:
        await ctx.send("Lista ya se encuentraba vacia")



bot.run(TOKEN)