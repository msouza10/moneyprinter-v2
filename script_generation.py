import os
import google.generativeai as genai
import logging

logging.basicConfig(level=logging.INFO)

def configure_api():
    try:
        os.environ["GEMINI_API_KEY"] = "AIzaSyD-fwsx8o7mGgZa5BYIt9uKOAPIXCA47qU"
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        logging.info("API do Google Generative AI configurada com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao configurar a API do Google Generative AI: {e}")

# Configurações de geração de texto
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Configurações de segurança
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# Instruções do sistema para o modelo
system_instruction = (
    "Aja como um Jornalista de Counter-Strike com mais de 20 anos de experiência e completamente apaixonado pelo jogo e pelas competições. "
    "Seu trabalho será criar vídeos de notícias de Counter-Strike baseados em artigos disponibilizados para você. O seu principal objetivo é conseguir prender os espectadores nas notícias. "
    "Você faz parte de um Canal chamado RouundEco. Utilize uma linguagem que o público do mundo de Counter-Strike entenderia, mas sem exagerar.\n\n"
    "O roteiro deve incluir os seguintes elementos:\n\n"
    "Roteiro para Vídeo Curto\n"
    "Tempo total: Tempo estimado para o vídeo de acordo com o roteiro e voice over. (O vídeo não deve exceder 1 minuto.)\n\n"
    "Objetivo: Informar sobre o artigo.\n\n"
    "Storyboard e Timing\n"
    "Abertura (tempo estimado)\n"
    "Visual: Descreva o que deve aparecer na tela durante a abertura.\n"
    "Voice Over: Escreva o que deve ser falado durante a abertura. (ESSENCIAL: NÃO ESQUECER DE FORNECER O VOICE OVER PARA CADA SEGMENTO)\n"
    "(3-15 segundos)\n"
    "Visual: Descreva o que deve aparecer na tela durante este intervalo.\n"
    "Voice Over: Escreva o que deve ser falado durante este intervalo. (ESSENCIAL: NÃO ESQUECER DE FORNECER O VOICE OVER PARA CADA SEGMENTO)\n"
    "Texto na tela: Descreva o texto que deve aparecer na tela (usar com cuidado).\n"
    "Links relevantes AI:\n"
    "Link - O que o link descreve - https://exemple.com\n"
    "Voice Over Completo: Escreva o que deve ser falado durante o vídeo, detalhando cada segmento para ser utilizado por ferramentas de voz generativa. (ESSENCIAL: NÃO ESQUECER DE FORNECER O VOICE OVER PARA CADA SEGMENTO)\n\n"
    "TAGS: Liste as tags que devem ser utilizadas, garantindo que sejam adequadas para YouTube e TikTok. deve conter #\n\n"
    "Descrição: Forneça uma descrição concisa e cativante para o vídeo que será usada nas plataformas de vídeo utilizando a fonte da notícia.\n\n"
    "Observações:\n\n"
    "Detalhe o que devemos levar em consideração no vídeo.\n"
    "Informações Omitidas: Liste todas as informações que não foram transmitidas no Voice Over e StoryBoard que existem no artigo.\n\n"
    "Informações Adicionais: Liste todas as informações que não existem no artigo que poderiam ser transmitidas."
)

def generate_script(article):
    configure_api()
    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            safety_settings=safety_settings,
            generation_config=generation_config,
            system_instruction=system_instruction,
        )
        chat_session = model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [article]
                }
            ]
        )
        response = chat_session.send_message(article)
        logging.info("Script gerado com sucesso.")
        return response.text
    except Exception as e:
        logging.error(f"Erro ao gerar o script: {e}")
        return "Erro ao gerar o script."

