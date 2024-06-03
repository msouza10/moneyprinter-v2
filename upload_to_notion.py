from notion_client import Client

def split_text(text, max_length):
    """Divide o texto em partes de no máximo max_length caracteres."""
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]

def create_and_update_script(token, database_id, script):
    notion = Client(auth=token)
    
    # Dividir o script em partes de 1500 caracteres
    script_parts = split_text(script, 1500)
    
    # Extrair a primeira linha do script para o título
    title = "*" + script.split('\n')[0]

    # Criar a página
    try:
        response = notion.pages.create(
            parent={"database_id": database_id},
            properties={
                "title": [
                    {
                        "type": "text",
                        "text": {
                            "content": title
                        }
                    }
                ]
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
        print(f"Página do script '{title}' criada com sucesso: {response}")
    except Exception as e:
        print(f"Ocorreu um erro ao criar a página: {e}")
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
            print(f"Parte do script adicionada com sucesso: {response}")
        except Exception as e:
            print(f"Ocorreu um erro ao atualizar a página: {e}")
