from scraping_hltv import main as scrape_hltv_news, user_interaction, get_news_content
from scraping_dust2 import main as scrape_dust2_news
from script_generation import generate_script
from upload_to_notion import create_and_update_script
import os
from dotenv import load_dotenv

def get_env_variable(var_name, prompt):
    current_value = os.getenv(var_name)
    if current_value:
        print(f"Valor atual de {var_name}: {current_value}")
        change = input(f"Deseja mudar {var_name}? (sim/nao): ").strip().lower()
        if change == 'sim':
            new_value = input(prompt).strip()
            os.environ[var_name] = new_value
            return new_value
        else:
            return current_value
    else:
        new_value = input(prompt).strip()
        os.environ[var_name] = new_value
        return new_value

def format_uuid(uuid):
    return uuid

def main():
    load_dotenv()

    token = get_env_variable("NOTION_TOKEN", "Digite seu token de integração do Notion: ")
    database_id = format_uuid(get_env_variable("NOTION_DATABASE_ID", "Digite o ID da base de dados do Notion: "))

    choice = input("Você quer pegar notícias da HLTV ou Dust2? (Digite 'hltv' ou 'dust2'): ").strip().lower()
    
    if choice == 'hltv':
        news_data = scrape_hltv_news()
    elif choice == 'dust2':
        news_data = scrape_dust2_news()
    else:
        print("Escolha inválida. Por favor, digite 'hltv' ou 'dust2'.")
        return
    
    print(f"Notícias coletadas: {len(news_data)} itens")
    
    selected_news = user_interaction(news_data)

    for news in selected_news:
        news['content'] = get_news_content(news['link'])  # Preenchendo o conteúdo da notícia
        script = generate_script(news['content'])
        print(script)
        print("="*50)
        
        create_and_update_script(token, database_id, script)

if __name__ == "__main__":
    main()
