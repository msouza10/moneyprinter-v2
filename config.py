from dotenv import load_dotenv
import os
import logging

logging.basicConfig(level=logging.INFO)

def load_env():
    load_dotenv()
    logging.info("Variáveis de ambiente carregadas.")

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
