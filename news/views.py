from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.conf import settings
from .forms import CustomAuthenticationForm, RegisterForm, APISettingsForm
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import FileResponse, Http404
from .models import APISettings
from scripts.scraping_hltv import main as scrape_hltv_news, get_news_content, user_interaction
from scripts.scraping_dust2 import main as scrape_dust2_news
from scripts.script_generation import generate_script
from scripts.upload_to_notion import create_and_update_script
from scripts.database_helper import mark_news_as_sent, is_news_sent, add_used_game_id, get_used_game_ids
from scripts.twitch_clips import fetch_cs2_clips, search_games, download_clip_from_site, fetch_clip_download_url
from datetime import datetime, timedelta
import logging
import os
import asyncio
import aiofiles
import aiohttp

news_cache = []
clips_cache = []

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                messages.error(request, 'Usuário ou senha incorretos.')
        else:
            messages.error(request, 'Informações inválidas.')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'news/login.html', {'form': form})

@login_required
def home(request):
    return redirect('index')

@login_required
def index(request):
    return render(request, 'news/index.html')

@login_required
def fetch_news(request):
    global news_cache
    if request.method == 'POST':
        source = request.POST.get('source')
        if source not in ['hltv', 'dust2']:
            messages.error(request, 'Fonte inválida! Por favor, selecione HLTV ou Dust2.')
            return redirect('index')

        if source == 'hltv':
            news_cache = scrape_hltv_news()
        else:
            news_cache = scrape_dust2_news()

        messages.success(request, 'Notícias capturadas com sucesso! Selecione as notícias para processar.')
        return redirect('list_news')
    else:
        return redirect('index')

@login_required
def list_news(request):
    return render(request, 'news/list_news.html', {'news': news_cache})

@login_required
def process_news(request):
    global news_cache
    if request.method == 'POST':
        selected_news_ids = request.POST.getlist('selected_news')
        selected_news = [news for news in news_cache if news['guid'] in selected_news_ids]

        settings = APISettings.objects.first()
        token = settings.notion_token
        database_id = settings.notion_database_id

        for news in selected_news:
            if is_news_sent(news['guid']):
                continue

            news['content'] = get_news_content(news['link'])
            script = generate_script(news['content'])
            create_and_update_script(token, database_id, script)
            mark_news_as_sent(news['guid'])

        messages.success(request, 'Notícias processadas e enviadas para o Notion com sucesso!')
        news_cache = [news for news in news_cache if news['guid'] not in selected_news_ids]  # Remove processed news from cache
        return redirect('list_news')
    else:
        return redirect('index')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_view(request):
    return render(request, 'news/admin.html')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário cadastrado com sucesso! Você já pode fazer login.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'news/register.html', {'form': form})

@login_required
def settings(request):
    if request.method == 'POST':
        form = APISettingsForm(request.POST, instance=APISettings.objects.first())
        if form.is_valid():
            form.save()
            messages.success(request, 'Configurações salvas com sucesso!')
            return redirect('settings')
    else:
        settings = APISettings.objects.first()
        form = APISettingsForm(instance=settings)
    
    return render(request, 'news/settings.html', {'form': form})

@login_required
def custom_page_not_found_view(request, exception):
    return redirect(settings.LOGIN_URL)

@login_required
@login_required
def fetch_clips(request):
    global clips_cache
    if request.method == 'POST':
        game_id = request.POST.get('game_id')
        period = request.POST.get('period')
        min_duration = int(request.POST.get('min_duration', 40))
        max_duration = int(request.POST.get('max_duration', 90))
        
        settings = APISettings.objects.first()
        client_id = settings.twitch_client_id
        client_secret = settings.twitch_client_secret

        if not client_id or not client_secret:
            messages.error(request, 'As configurações da API da Twitch não estão definidas. Por favor, configure-as nas configurações.')
            return redirect('settings')

        # Calculate the started_at parameter based on the period
        started_at = None
        if period != 'all':
            now = datetime.utcnow()
            if period == 'day':
                started_at = now - timedelta(days=1)
            elif period == 'week':
                started_at = now - timedelta(weeks=1)
            elif period == 'month':
                started_at = now - timedelta(days=30)
            elif period == 'year':
                started_at = now - timedelta(days=365)
            started_at = started_at.isoformat() + 'Z'

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        clips_cache = loop.run_until_complete(fetch_cs2_clips(client_id, client_secret, game_id, period=period, num_clips=10, min_duration=min_duration, max_duration=max_duration, started_at=started_at))
        
        # Add the URL for embedding each clip
        for clip in clips_cache:
            clip['embed_url'] = f"https://clips.twitch.tv/embed?clip={clip['id']}&parent=localhost"
        
        # Store clips_cache in session
        request.session['clips_cache'] = clips_cache

        messages.success(request, 'Clipes capturados com sucesso!')
        return redirect('list_clips')
    return redirect('index')

@login_required
def list_clips(request):
    clips_cache = request.session.get('clips_cache', [])
    return render(request, 'news/list_clips.html', {'clips': clips_cache})

@login_required
def list_clips(request):
    return render(request, 'news/list_clips.html', {'clips': clips_cache})

@login_required
def list_game_ids(request):
    used_game_ids = get_used_game_ids()
    return render(request, 'news/list_game_ids.html', {'game_ids': used_game_ids})

@login_required
def search_game_ids(request):
    if request.method == 'POST':
        game_name = request.POST.get('game_name')
        settings = APISettings.objects.first()
        client_id = settings.twitch_client_id
        client_secret = settings.twitch_client_secret
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        games = loop.run_until_complete(search_games(client_id, client_secret, game_name))
        
        return render(request, 'news/search_game_ids.html', {'games': games, 'searched': True})
    return render(request, 'news/search_game_ids.html', {'searched': False})

@login_required
def select_clips(request):
    return render(request, 'news/select_clips.html')

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

@login_required
def download_clip_view(request, clip_id):
    # Fetch Twitch credentials
    settings_instance = APISettings.objects.first()
    client_id = settings_instance.twitch_client_id
    client_secret = settings_instance.twitch_client_secret

    if not client_id or not client_secret:
        raise Http404("Credenciais da Twitch não encontradas nas configurações.")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Fetching clip details from the session cache
    clips_cache = request.session.get('clips_cache', [])
    clip = next((clip for clip in clips_cache if clip['id'] == clip_id), None)

    if not clip:
        raise Http404("Clip não encontrado")

    file_path = loop.run_until_complete(download_clip_from_site(clip_id, clip['title'], client_id, client_secret))

    if file_path and os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
        return response
    else:
        raise Http404("Clip não encontrado")