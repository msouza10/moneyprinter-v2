import aiohttp
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

async def fetch_cs2_clips(client_id, client_secret, game_id, period='week', num_clips=10, min_duration=40, max_duration=90):
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
        'started_at': (datetime.utcnow() - timedelta(days=7)).isoformat() + 'Z' if period == 'week' else None
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(clips_url, headers=headers, params=params) as response:
            data = await response.json()
            clips = []
            for clip in data['data']:
                duration = clip.get('duration')
                if min_duration <= duration <= max_duration:
                    clips.append({
                        'title': clip['title'],
                        'url': clip['url'],
                        'duration': duration
                    })
            return clips
