import aiohttp
import aiofiles
import logging
import os
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)

async def search_games(client_id, client_secret, game_name):
    """Busca jogos na Twitch pelo nome."""
    auth_url = 'https://id.twitch.tv/oauth2/token'
    auth_params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(auth_url, params=auth_params) as response:
            auth_data = await response.json()
            access_token = auth_data['access_token']
    
    search_url = 'https://api.twitch.tv/helix/games'
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'name': game_name
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(search_url, headers=headers, params=params) as response:
            data = await response.json()
            return data['data']

async def fetch_cs2_clips(client_id, client_secret, game_id, period='week', num_clips=10, min_duration=40, max_duration=90, started_at=None):
    """Busca os clipes mais populares de um jogo na Twitch."""
    auth_url = 'https://id.twitch.tv/oauth2/token'
    auth_params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(auth_url, params=auth_params) as response:
            auth_data = await response.json()
            access_token = auth_data['access_token']
    
    clips_url = 'https://api.twitch.tv/helix/clips'
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'game_id': game_id,
        'first': num_clips,
        'started_at': started_at
    }

    logging.info(f"Fetching clips with params: {params}")

    async with aiohttp.ClientSession() as session:
        async with session.get(clips_url, headers=headers, params=params) as response:
            data = await response.json()
            logging.info(f"Response from Twitch API: {data}")
            clips = []
            for clip in data.get('data', []):
                duration = float(clip.get('duration'))
                if min_duration <= duration <= max_duration:
                    clips.append({
                        'id': clip['id'],
                        'title': clip['title'],
                        'url': clip['url'],
                        'thumbnail_url': clip['thumbnail_url'],
                        'duration': duration,
                        'view_count': clip['view_count'],
                        'download_url': clip['url']  # URL para download do clipe
                    })
            return clips

async def fetch_clip_download_url(clip_id, client_id, client_secret):
    """Obtém a URL de download de um clipe da Twitch."""
    auth_url = 'https://id.twitch.tv/oauth2/token'
    auth_params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(auth_url, params=auth_params) as response:
            auth_data = await response.json()
            access_token = auth_data['access_token']

    clip_url = f'https://api.twitch.tv/helix/clips?id={clip_id}'
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {access_token}'
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(clip_url, headers=headers) as response:
            data = await response.json()
            clip_data = data.get('data', [])
            if clip_data:
                return clip_data[0]['thumbnail_url'].split('-preview-')[0] + '.mp4'
            else:
                return None

async def download_clip(clip_id, clip_title, client_id, client_secret):
    """Baixa um clipe da Twitch usando o ID do clipe."""
    download_url = await fetch_clip_download_url(clip_id, client_id, client_secret)
    if not download_url:
        logging.error("URL de download não encontrada.")
        return

    clips_dir = 'clips'
    os.makedirs(clips_dir, exist_ok=True)
    file_path = os.path.join(clips_dir, f"{clip_title}.mp4")

    async with aiohttp.ClientSession() as session:
        async with session.get(download_url) as response:
            if response.status == 200:
                async with aiofiles.open(file_path, "wb") as file:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        await file.write(chunk)
                logging.info(f"Clip '{clip_title}' baixado com sucesso em '{file_path}'.")
            else:
                logging.error(f"Erro ao baixar o clipe: Status {response.status}")

async def fetch_and_download_top_clip(client_id, client_secret, game_id, period='week', min_duration=40, max_duration=90):
    """Busca e baixa o clipe mais famoso."""
    # Primeiro, buscar o clipe mais famoso independentemente da duração
    auth_url = 'https://id.twitch.tv/oauth2/token'
    auth_params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(auth_url, params=auth_params) as response:
            auth_data = await response.json()
            access_token = auth_data['access_token']
    
    clips_url = 'https://api.twitch.tv/helix/clips'
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'game_id': game_id,
        'first': 1,
        'started_at': (datetime.utcnow() - timedelta(days=7)).isoformat() + 'Z' if period == 'week' else None
    }

    logging.info(f"Fetching top clip with params: {params}")

    async with aiohttp.ClientSession() as session:
        async with session.get(clips_url, headers=headers, params=params) as response:
            data = await response.json()
            logging.info(f"Response from Twitch API: {data}")
            clips = data.get('data', [])
            if clips:
                top_clip = clips[0]
                await download_clip(top_clip['id'], top_clip['title'], client_id, client_secret)
                logging.info(f"Top clip '{top_clip['title']}' com duração de {top_clip['duration']} segundos baixado.")
            else:
                logging.info("Nenhum clipe encontrado com os critérios especificados.")

async def download_clip_async(clip_id, clip_title, client_id, client_secret):
    """Baixa um clipe da Twitch usando o ID do clipe."""
    download_url = await fetch_clip_download_url(clip_id, client_id, client_secret)
    if not download_url:
        logging.error("URL de download não encontrada.")
        return None

    clips_dir = 'clips'
    os.makedirs(clips_dir, exist_ok=True)
    file_path = os.path.join(clips_dir, f"{clip_title}.mp4")

    async with aiohttp.ClientSession() as session:
        async with session.get(download_url) as response:
            if response.status == 200:
                async with aiofiles.open(file_path, "wb") as file:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        await file.write(chunk)
                logging.info(f"Clip '{clip_title}' baixado com sucesso em '{file_path}'.")
                return file_path
            else:
                logging.error(f"Erro ao baixar o clipe: Status {response.status}")
                return None
            
async def download_clip_from_site(clip_id, clip_title, client_id, client_secret):
    """Baixa um clipe da Twitch usando o ID do clipe (para uso via site)."""
    download_url = await fetch_clip_download_url(clip_id, client_id, client_secret)
    if not download_url:
        logging.error("URL de download não encontrada.")
        return None

    clips_dir = 'clips'
    os.makedirs(clips_dir, exist_ok=True)
    file_path = os.path.join(clips_dir, f"{clip_title}.mp4")

    async with aiohttp.ClientSession() as session:
        async with session.get(download_url) as response:
            if response.status == 200:
                async with aiofiles.open(file_path, "wb") as file:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        await file.write(chunk)
                logging.info(f"Clip '{clip_title}' baixado com sucesso em '{file_path}'.")
                return file_path
            else:
                logging.error(f"Erro ao baixar o clipe: Status {response.status}")
                return None