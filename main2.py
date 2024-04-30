import discord
from discord.ext import commands
from discord.utils import get
from yt_dlp import YoutubeDL
import os
import shutil
from youtubesearchpython import VideosSearch
import asyncio




intents = discord.Intents.all()
bot=commands.Bot(command_prefix='.',intents=intents)
global Lista_num
Lista_num=0

def search_yt(item):
    if item.startswith("https://"):
        return item
    search = VideosSearch(item, limit=1)
    
    return search.result()["result"][0]["link"]

@bot.event
async def on_ready():
    await bot.change_presence(activity = discord.Game(name=''))
    LR_en_archivo = os.path.isdir("./Lista")
    LR_carpeta = "./Lista"
    if LR_en_archivo is True:
        print("Removida la carpeta antigua")
        shutil.rmtree(LR_carpeta)
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

@bot.command(pass_context = True)
async def play(ctx, *args):

    

    global Lista_num
    query= " ".join(args)
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


    #FUNCION PASAR CANCION


    def revisar_lista():
        LR_en_archivo = os.path.isdir("./Lista")
        if LR_en_archivo is True:
            DIR = os.path.abspath(os.path.realpath("Lista"))
            tamaño = len(os.listdir(DIR))
            c_activa = tamaño - 1
            try:
                c_primera = os.listdir(DIR)[0]
            except:
                print("No hay canciones\n")
                listar.clear()
                return
            localizacion_principal = os.path.dirname(os.path.realpath(__file__))
            c_localizacion = os.path.abspath(os.path.realpath("Lista") + "\\" + c_primera)
            if tamaño != 0:
                print("Cancion lista, se reproducira en breve")
                print(f"Canciones en la lista: {c_activa}")
                c_encontrada = os.path.isfile("cancion.mp3")
                if c_encontrada:
                    os.remove("cancion.mp3")
                    shutil.move(c_localizacion,localizacion_principal)
                    for file in os.listdir("./"):
                        if file.endswith(".mp3"):
                            os.rename(file,'cancion.mp3')
                    voice.play(discord.FFmpegPCMAudio("cancion.mp3"),after = lambda e:revisar_lista())
                else:
                    listar.clear()
                    return
            else:
                listar.clear()
                print("No se agrego a la lista")
    
    c_encontrada = os.path.isfile("cancion.mp3")
    try:#reproducir cancion
        if c_encontrada:
            os.remove("cancion.mp3")
            listar.clear()
            print("removido archivo antiguo")
    except PermissionError:#agregar a la lista
        Cancion_lista = os.path.isdir("./Lista")
        if Cancion_lista is False:
            os.mkdir("Lista")
        DIR = os.path.abspath(os.path.realpath("Lista"))
        #Lista_num = len(os.listdir(DIR)) no funciona sobrescribe canciones cambiado por variable global
        
        Lista_num+=1
        agregar_lista = True
        while agregar_lista:
            if Lista_num is listar:
                Lista_num+=1
            else:
                agregar_lista = False
                listar[Lista_num] = Lista_num
        Lista_path = os.path.abspath(os.path.realpath("Lista") + f"\cancion{Lista_num}.%(ext)s")
        ydl_op = {
            'format':'bestaudio/best',
            'quiet' : True,
            'outtmpl' : Lista_path,
            'ffmpeg_location':os.path.realpath('C:\\ffmpeg\\bin\\ffmpeg.exe'),
            'postprocessors' : [{
                'key' : 'FFmpegExtractAudio',
                'preferredcodec' : 'mp3',
                'preferredquality' : '192',
            }],
        }


        with YoutubeDL(ydl_op) as ydl:
            print("Descargar Cancion")
            ydl.download([song])

        await ctx.send("Añadida la cancion "+str(Lista_num)+" a la lista de reproduccion")\
        
        print("cancion añadida")
        return
    #
    LR_en_archivo = os.path.isdir("./Lista")
    try:
        LR_carpeta = "./Lista"
        if LR_en_archivo is True:
            print("Removida la carpeta antigua")
            shutil.rmtree(LR_carpeta)
    except:
        print("no hay carpeta antigua")
    
    await ctx.send("Todo lsito")

    voice = get(bot.voice_clients,guild = ctx.guild)

    ydl_op = {
        'format' : 'bestaudio/best',
        'ffmpeg_location':os.path.realpath('C:\\ffmpeg\\bin\\ffmpeg.exe'),
    }

    #with YoutubeDL(ydl_op) as ydl:
        #print("descargando cancion\n")
       # ydl.download([song])
    FFMPEG_OPTIONS = {'options': '-vn'}
    with YoutubeDL(ydl_op) as ydl:
        
        data=  ydl.extract_info(song, download=False)
        cancion=data['url']
    voice.play(discord.FFmpegPCMAudio(cancion,executable='ffmpeg.exe',**FFMPEG_OPTIONS),after=lambda e: revisar_lista())

    #await ctx.send(f"reproduciendo: {nombre[0]}")
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


listar = {}

@bot.command(pass_context = True)
async def lista(ctx,url:str):
    Cancion_lista = os.path.isdir("./Lista")
    if Cancion_lista is False:
        os.mkdir("Lista")
    DIR = os.path.abspath(os.path.realpath("Lista"))
    Lista_num = len(os.listdir(DIR))
    Lista_num+=1
    agregar_lista = True
    while agregar_lista:
        if Lista_num is listar:
            Lista_num+=1
        else:
            agregar_lista = False
            listar[Lista_num] = Lista_num
    Lista_path = os.path.abspath(os.path.realpath("Lista") + f"\cancion{Lista_num}.%(ext)s")
    ydl_op = {
        'format':'bestaudio/best',
        'quiet' : True,
        'outtmpl' : Lista_path,
        'ffmpeg_location':os.path.realpath('C:\\ffmpeg\\bin\\ffmpeg.exe'),
        'postprocessors' : [{
            'key' : 'FFmpegExtractAudio',
            'preferredcodec' : 'mp3',
            'preferredquality' : '192',
        }],
    }
    with YoutubeDL(ydl_op) as ydl:
        print("Descargar Cancion")
        ydl.download([url])

    await ctx.send("Añadida la cancion "+str(Lista_num)+" a la lista de reproduccion")\
    
    print("cancion añadida")

bot.run(TOKEN)