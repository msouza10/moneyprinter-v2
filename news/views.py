from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from .forms import CustomAuthenticationForm, RegisterForm, APISettingsForm
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .models import APISettings
from scripts.scraping_hltv import main as scrape_hltv_news, get_news_content, user_interaction
from scripts.scraping_dust2 import main as scrape_dust2_news
from scripts.script_generation import generate_script
from scripts.upload_to_notion import create_and_update_script
from scripts.database_helper import mark_news_as_sent, is_news_sent

news_cache = []

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
        form = APISettingsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configurações salvas com sucesso!')
            return redirect('settings')
    else:
        settings = APISettings.objects.first()
        form = APISettingsForm(instance=settings)
    
    return render(request, 'news/settings.html', {'form': form})

def custom_page_not_found_view(request, exception):
    return redirect(settings.LOGIN_URL)