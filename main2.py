import discord
from discord.ext import commands
from discord.utils import get
from yt_dlp import YoutubeDL
import os
import shutil
from youtubesearchpython import VideosSearch
import asyncio
import typing
import spotipy
import spotipy.oauth2 as oauth2
from googleapiclient.discovery import build
from re import search,match
import random

api_youtube=''


client_id=''
client_secret=''
auth_manager = oauth2.SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
spotify = spotipy.Spotify(auth_manager=auth_manager)




voice=None






TOKEN=''


ydl_op = {
        'format' : 'bestaudio/best',
    }
FFMPEG_OPTIONS = {'options': '-vn'}
ydl = YoutubeDL(ydl_op)
lista=[]
sonando=False

intents = discord.Intents.all()
bot=commands.Bot(command_prefix='.',intents=intents)


def get_video_title(video_url):
    global lista
    # Extraer el ID del video de la URL
    video_id_match = search(r'(?:https?://)?(?:www\.)?youtu\.?be(?:\.com)?/(?:embed/|watch\?v=|v/|.+\?v=)?([^&=\n%\?]{11})', video_url)
    if video_id_match:
        video_id = video_id_match.group(1)
    else:
        busqueda = VideosSearch(video_url, limit=1)
        video_url=busqueda.result()["result"][0]["link"]
        video_id_match = search(r'(?:https?://)?(?:www\.)?youtu\.?be(?:\.com)?/(?:embed/|watch\?v=|v/|.+\?v=)?([^&=\n%\?]{11})', video_url)
        video_id = video_id_match.group(1)
    # Inicializar la API de YouTube
    youtube = build('youtube', 'v3', developerKey=api_youtube)

    # Obtener el título del video utilizando la API de YouTube
    request = youtube.videos().list(
        part='snippet',
        id=video_id
    )
    response = request.execute()

    # Extraer el título del video de la respuesta
    if 'items' in response and len(response['items']) > 0:
        title = response['items'][0]['snippet']['title']
        lista.append({"URL":video_url,"titulo": title})
        return {"URL":video_url,"titulo": title}
    else:
        print("No se pudo encontrar el video con el ID proporcionado.")
        return "No se pudo encontrar el video con el ID proporcionado."

def get_playlist_titles_and_urls(playlist_url):
    # Extraer el ID de la lista de reproducción de la URL
    playlist_id_match = search(r'(?:https?://)?(?:www\.)?youtube\.com/.+\?list=([^&\n%\?]+)', playlist_url)
    print(playlist_id_match)
    if playlist_id_match:
        playlist_id = playlist_id_match.group(1)
    else:
        print("No se pudo encontrar el ID de la lista de reproducción en la URL proporcionada.")
        return "No se pudo encontrar el ID de la lista de reproducción en la URL proporcionada."

    # Inicializar la API de YouTube
    youtube = build('youtube', 'v3', developerKey=api_youtube)

    # Obtener los títulos y las URLs de las canciones de la lista de reproducción utilizando la API de YouTube
    request = youtube.playlistItems().list(
        part='snippet',
        playlistId=playlist_id,
        maxResults=50  # Máximo de resultados por página
    )
    response = request.execute()

    # Extraer los títulos y las URLs de las canciones de la respuesta
    global lista
    for item in response['items']:
        title = item['snippet']['title']
        video_id = item['snippet']['resourceId']['videoId']
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        lista.append({"URL":video_url,"titulo": title})

def nonesul(item):
    busqueda = VideosSearch(item, limit=1)
    video_url=busqueda.result()["result"][0]["link"]
    cancion = ydl.extract_info(video_url, download=False)
    url=cancion["url"]
    return url

def search_yt(item):
    cancion = ydl.extract_info(item, download=False)
    url=cancion["url"]
    return url

def buscar_youtube(ctx,query):
    global lista
    global voice
    global sonando
    # Verificar si la entrada es una URL de Spotify de una canción o de una playlist
    if match(r'^https://open\.spotify\.com/track/(\w+)', query):
        # Si es una URL de Spotify de una canción, obtener el nombre de la canción y del artista
        track_id = search(r'^https://open\.spotify\.com/track/(\w+)', query).group(1)
        print(track_id)
        track_info = spotify.track(track_id)
        nombre_cancion = track_info['name']
        nombre_artista = track_info['artists'][0]['name']
        titulo= f"{nombre_cancion} - {nombre_artista}"
        lista.append({'URL':None,'titulo':titulo})

    elif match(r'^https://open\.spotify\.com/playlist/(\w+)\?si=\w+', query):
        # Si es una URL de Spotify de una playlist, obtener las canciones de la playlist
        playlist_id = search(r'^https://open\.spotify\.com/playlist/(\w+)', query).group(1)
        # Obtener los nombres de las canciones y artistas de la playlist
        results = spotify.playlist(playlist_id)
        tracks = results['tracks']
    
        while True:
            for item in tracks['items']:
                if 'track' in item:
                    track = item['track']
                else:
                    track = item
                try:
                    track_name = track['name']
                    track_artist = track['artists'][0]['name']
                    song=f"{track_name} - {track_artist}"
                    lista.append({"URL":None,"titulo": song})

                except UnicodeEncodeError:  # Most likely caused by non-English song names
                            print("Track named {} failed due to an encoding error. This is \
                                    most likely due to this song having a non-English name.".format(track_name))
            if tracks['next']:
                tracks = spotify.next(tracks)
            else:
                break

        # Realizar la búsqueda en YouTube para la primera canción de la playlist
        
    else:
        # Si no es una URL de Spotify, utilizar el texto proporcionado como nombre de la canción
        return
    
    # Realizar la búsqueda en YouTube
    if ctx.author.voice is None:
        return
    canal = ctx.author.voice.channel


    






@bot.event
async def on_ready():
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
    global sonando
    global voice
    global lista
    if len(lista)==0:
        return
    lista.pop(0)
    if len(lista) > 0:
        song=lista[0]
        if song['URL']!=None:
            cancion=search_yt(song['URL'])
            voice.play(discord.FFmpegPCMAudio(cancion,executable='ffmpeg',**FFMPEG_OPTIONS),after=lambda e: revisar_lista(ctx))
            return
        else:
            cancion=nonesul(lista[0]['titulo'])
            voice.play(discord.FFmpegPCMAudio(cancion,executable='ffmpeg',**FFMPEG_OPTIONS),after=lambda e: revisar_lista(ctx))
            return
    sonando=False





@bot.command(pass_context = True,name="play", aliases=["p","playing"])
async def play(ctx, *args):
    global sonando
    global lista
    global voice
    query= " ".join(args)
    
    #CONECTAR CANAL
    if ctx.author.voice is None:
        await ctx.send("¡Debes estar en un canal de voz para que pueda unirme!")
        return
    canal = ctx.author.voice.channel

    voice= get(bot.voice_clients,guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(canal)
    else:
        await canal.connect()

    if match(r'^https://open\.spotify\.com/track/(\w+)', query) or match(r'^https://open\.spotify\.com/playlist/(\w+)\?si=\w+', query):
        buscar_youtube(ctx,query)
        await ctx.send("añadido a la lista")
        if sonando==False:
            sonando=True
            if voice==None:
                voice = get(bot.voice_clients,guild = ctx.guild)
            
            cancion=nonesul(lista[0]['titulo'])
            await ctx.send(f"reproduciendo: {lista[0]['titulo']}")
            voice.play(discord.FFmpegPCMAudio(cancion,executable='ffmpeg',**FFMPEG_OPTIONS),after=lambda e: revisar_lista(ctx))
        return
    if len(lista)>0 and sonando==True:
        if query.find("list=")!=-1:
            get_playlist_titles_and_urls(query)
            await ctx.send("playlist agregada a la cola")
        else:
            song=get_video_title(query)
            await ctx.send("Añadida la cancion "+str(song['titulo'])+" a la lista de reproduccion")\
        
        print("cancion añadida")
        return
    else:
        if query.find("list=")!=-1:
            get_playlist_titles_and_urls(query)
        else:
            get_video_title(query)
        song = lista[0]
        sonando=True
        voice = get(bot.voice_clients,guild = ctx.guild)
        cancion=search_yt(song['URL'])
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
    global lista
    voz= get(bot.voice_clients,guild=ctx.guild)
    if voz and voz.is_playing():
        print("musica detenida")
        lista=[]
        voz.stop()
        await ctx.send("Musica detenida")
    else:
        print("No se esta reproduciendo, no se puede detener")
        await ctx.send("No se esta reproduciendo")

@bot.command(pass_context = True)
async def skip(ctx):
    global lista
    global voice
    if voice and voice.is_playing():
        if len(lista) > 1:
            song=lista[1]
            await ctx.send(f"reproduciendo{song['titulo']}")
            voice.stop()

        else:
            await ctx.send("No mas canciones en la lista")



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
    global voice
    if after.channel is None and member==bot.user:
        voice.stop()
        lista=[]
        voice=None

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


# Función para dividir la lista de canciones en páginas
def paginate_list(lst, page_number, page_size):
    start_index = (page_number - 1) * page_size
    end_index = min(start_index + page_size, len(lst))
    return lst[start_index:end_index]
# Comando para mostrar las canciones paginadas
@bot.command()
async def cola(ctx, page_number: int = 1):
    global lista
    canciones=[]
    for i in lista:
        canciones.append(i['titulo'])
    

# Verifica que el número de página sea válido
    if page_number < 1:
        await ctx.send("Número de página inválido.")
        return

    # Divide la lista de canciones en páginas
    page_size = 5  # Cambia 5 al número de canciones que quieras mostrar por página
    start_index = (page_number - 1) * page_size
    end_index = min(start_index + page_size, len(canciones))
    pages_count = -(-len(canciones) // page_size)  # Calcula el número de páginas
    if page_number > pages_count:
        await ctx.send("Esta página no tiene contenido.")
        return
    page = [f"{start_index + i + 1}. {cancion}" for i, cancion in enumerate(canciones[start_index:end_index])]
    #page = paginate_list(canciones, page_number, page_size)
    
    # Construye el mensaje con las canciones de la página actual
    embed = discord.Embed(title=f"Página {page_number}/{pages_count}", description="\n".join(page))
    message = await ctx.send(embed=embed)

    # Agrega emojis de reacción para la paginación
    if pages_count > 1:
        await message.add_reaction("◀️")  # Flecha izquierda
        await message.add_reaction("▶️")  # Flecha derecha

    # Función para manejar la paginación
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]

    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=60, check=check)
            await message.remove_reaction(reaction, user)
            
            if str(reaction.emoji) == "◀️" and page_number > 1:
                page_number -= 1
            elif str(reaction.emoji) == "▶️" and page_number < pages_count:
                page_number += 1
            start_index = (page_number - 1) * page_size
            end_index = min(start_index + page_size, len(canciones))
            page = [f"{start_index + i + 1}. {cancion}" for i, cancion in enumerate(canciones[start_index:end_index])]
            embed = discord.Embed(title=f"Página {page_number}/{pages_count}", description="\n".join(page))
            await message.edit(embed=embed)
        except asyncio.TimeoutError:
            break

@bot.command(pass_context=True,name="discord")
async def lista_discord(ctx):
    global lista
    global sonando
    global voice
    birdy_uri = '4ikCL8ztmEMH4jr2Akj78y'
    results = spotify.playlist(birdy_uri)
    tracks = results['tracks']
    await ctx.send("cargando playlist espere por favor")
    while True:
        for item in tracks['items']:
            if 'track' in item:
                track = item['track']
            else:
                track = item
            try:
                track_name = track['name']
                track_artist = track['artists'][0]['name']
                song=f"{track_name} - {track_artist}"
                lista.append({"URL":None,"titulo": song})

            except UnicodeEncodeError:  # Most likely caused by non-English song names
                        print("Track named {} failed due to an encoding error. This is \
                                most likely due to this song having a non-English name.".format(track_name))
        if tracks['next']:
            tracks = spotify.next(tracks)
        else:
            break
    if ctx.author.voice is None:
        await ctx.send("¡Debes estar en un canal de voz para que pueda unirme!")
        return
    canal = ctx.author.voice.channel

    voice= get(bot.voice_clients,guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(canal)
    else:
        await canal.connect()

    if sonando==False:
        sonando=True
        if voice==None:
            voice = get(bot.voice_clients,guild = ctx.guild)
        cancion=nonesul(lista[0]['titulo'])
        voice.play(discord.FFmpegPCMAudio(cancion,executable='ffmpeg',**FFMPEG_OPTIONS),after=lambda e: revisar_lista(ctx))


@bot.command(pass_context=True,name="shuffle",aliases=["revolver","mezclar"])
async def revolver(ctx):
    global lista
    global sonando
    if sonando:  # Si hay una canción sonando, mantenla en su lugar
        primera_cancion = lista.pop(0)
        random.shuffle(lista)
        lista.insert(0, primera_cancion)
    else:
        random.shuffle(lista)
    await ctx.send("¡La lista de reproducción ha sido revuelta!")





bot.run(TOKEN)