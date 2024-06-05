from django.shortcuts import render, redirect
from django.contrib import messages
from .models import APISettings
from .forms import APISettingsForm
from scripts.scraping_hltv import main as scrape_hltv_news, get_news_content, user_interaction
from scripts.scraping_dust2 import main as scrape_dust2_news
from scripts.script_generation import generate_script
from scripts.upload_to_notion import create_and_update_script
from scripts.config import get_env_variable
from scripts.database_helper import create_database, mark_news_as_sent, is_news_sent
import os
from dotenv import load_dotenv
import logging

load_dotenv()
create_database()

news_cache = []

def index(request):
    return render(request, 'news/index.html')

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

        logging.info(f"Notícias coletadas: {len(news_cache)} itens")
        messages.success(request, 'Notícias capturadas com sucesso! Selecione as notícias para processar.')
        return redirect('list_news')
    else:
        return redirect('index')

def list_news(request):
    return render(request, 'news/list_news.html', {'news': news_cache})

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
                logging.info(f"Notícia '{news['title']}' já foi enviada para o Notion.")
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

def settings(request):
    if request.method == 'POST':
        form = APISettingsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configurações salvas com sucesso!')
            return redirect('settings')
    else:
        settings = APISettings.objects.first()
        form = APISettingsForm(instance=settings)
    
    return render(request, 'news/settings.html', {'form': form})