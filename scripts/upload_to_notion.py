from notion_client import Client
import logging

logging.basicConfig(level=logging.INFO)

def split_text(text, max_length):
    """Divide o texto em partes de no máximo max_length caracteres, mantendo quebras de linha."""
    paragraphs = text.split('\n')
    parts = []
    current_part = ""

    for paragraph in paragraphs:
        if len(current_part) + len(paragraph) + 1 > max_length:
            parts.append(current_part)
            current_part = paragraph
        else:
            if current_part:
                current_part += '\n'
            current_part += paragraph

    if current_part:
        parts.append(current_part)
    
    return parts

def create_and_update_script(token, database_id, script):
    notion = Client(auth=token)

    # Dividir o script em partes de 1500 caracteres
    script_parts = split_text(script, 1500)

    # Extrair a primeira linha do script para o título
    title = script.split('\n')[0] if script else "Sem Título"

    # Criar a página
    try:
        response = notion.pages.create(
            parent={"database_id": database_id},
            properties={
                "title": {
                    "title": [
                        {
                            "type": "text",
                            "text": {
                                "content": title
                            }
                        }
                    ]
                }
            },
            children=[
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": script_parts[0]
                                }
                            }
                        ]
                    }
                }
            ]
        )
        page_id = response['id']
        logging.info(f"Página do script '{title}' criada com sucesso: {response}")
    except Exception as e:
        logging.error(f"Ocorreu um erro ao criar a página: {e}")
        return

    # Atualizar a página com as partes restantes
    for part in script_parts[1:]:
        try:
            response = notion.blocks.children.append(
                block_id=page_id,
                children=[
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": part
                                    }
                                }
                            ]
                        }
                    }
                ]
            )
            logging.info(f"Parte do script adicionada com sucesso: {response}")
        except Exception as e:
            logging.error(f"Ocorreu um erro ao atualizar a página: {e}")

