## Moneyprinter-v2: Automatizando a Criação de Scripts de Vídeo para CS:GO

O Moneyprinter-v2 é uma ferramenta poderosa que automatiza o processo de transformar notícias de CS:GO em scripts de vídeo otimizados para YouTube e TikTok. Com foco em eficiência e qualidade, o Moneyprinter-v2 oferece um fluxo de trabalho simplificado, permitindo que criadores de conteúdo se concentrem na produção de vídeos de alta qualidade.

**Recursos:**

* **Coleta de Notícias Inteligente:** O Moneyprinter-v2 monitora continuamente os sites HLTV e Dust2, coletando as notícias mais recentes do mundo do CS:GO.
* **Geração de Scripts Atraentes:** Através do Google Generative AI, o Moneyprinter-v2 transforma essas notícias em scripts de vídeo detalhados, incluindo:
    * **Storyboard e Tempo:** Elementos visuais e narração para cada segmento do vídeo.
    * **Narração Completa:** Script completo, pronto para ser usado por ferramentas de geração de voz.
    * **Tags Relevantes:** Hashtags otimizadas para YouTube e TikTok.
    * **Descrição Envolvente:** Descrição concisa e cativante para o seu vídeo.
    * **Observações:** Informações extras para te ajudar a criar o vídeo de forma mais eficaz.
* **Integração Seamless com o Notion:** O script gerado é enviado diretamente para o seu banco de dados do Notion, pronto para ser editado e organizado. 
* **Controle Total sobre o Processo:** Você escolhe quais notícias deseja processar e gerencia os scripts enviados com total autonomia.

**Como Usar:**

**1. Instalação:**

1. **Requisitos:** Certifique-se de ter o Python 3.8 ou superior instalado.
2. **Ambiente Virtual:** Crie um ambiente virtual: `python -m venv env`
3. **Ativação:** Ative o ambiente: `env\Scripts\activate`
4. **Instalação de Pacotes:** Instale os pacotes necessários: `pip install -r requirements.txt`
5. **Configuração do Ambiente:** Crie um arquivo `.env` na raiz do projeto e adicione as seguintes variáveis:
    * `NOTION_TOKEN`: Seu token de integração do Notion.
    * `NOTION_DATABASE_ID`: O ID do seu banco de dados do Notion.
    * `GEMINI_API_KEY`: Sua chave API do Google Generative AI.

**2. Execução:**

**a) Interface Web:**

1. **Migrações do Banco de Dados:** Execute `python manage.py migrate` para aplicar as migrações.
2. **Servidor Django:** Inicie o servidor de desenvolvimento Django: `python manage.py runserver`
3. **Acesso à Interface:** Acesse a interface web em `http://127.0.0.1:8000/`.
4. **Configurações:** Forneça suas chaves API do Notion e do Google Generative AI na seção "Configurações".
5. **Coleta de Notícias:** Selecione HLTV, Dust2 ou "Tudo" para capturar as notícias.
6. **Seleção de Notícias:** Escolha as notícias que deseja transformar em scripts.
7. **Processamento:** Clique em "Processar Notícias" para gerar os scripts e enviá-los para o seu Notion.

**b) Console:**

1. **Argumentos:** Utilize os seguintes argumentos de linha de comando:
    * `--source`: A fonte das notícias (hltv, dust2, all).
    * `--process`: Processar todas as notícias automaticamente (all).
2. **Exemplo:** `python main.py --source hltv --process all` para coletar e processar todas as notícias do HLTV.

**Estrutura do Projeto:**

```
ProfitPortal/
├── news/
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── templates/
│   │   ├── news/
│   │   │   ├── index.html
│   │   │   ├── list_news.html
│   │   │   └── settings.html
│   └── static/
│       ├── scripts.js
│       └── styles.css
├── ProfitPortal/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── scripts/
    ├── config.py
    ├── database_helper.py
    ├── scraping_dust2.py
    ├── scraping_hltv.py
    ├── script_generation.py
    └── upload_to_notion.py
```

**Vantagens:**

* **Eficiência:** Automatiza o processo de criação de scripts, liberando seu tempo para outras tarefas.
* **Qualidade:** Scripts de vídeo bem escritos e otimizados para o público do YouTube e TikTok.
* **Facilidade de Uso:** Interface amigável e intuitiva, tanto para iniciantes quanto para usuários experientes.
* **Integração com Ferramentas Essenciais:** Integração com Notion e Google Generative AI para um fluxo de trabalho otimizado.

**Comece a usar o Moneyprinter-v2 hoje mesmo e aumente a qualidade e a quantidade de seus vídeos de CS:GO!**

**Contribuindo:**

Se você deseja contribuir com o Moneyprinter-v2, siga estas etapas:

1. **Fork:** Faça um fork do repositório.
2. **Crie um Branch:** Crie um novo branch para suas alterações.
3. **Faça suas Alterações:** Faça suas alterações no código.
4. **Teste:** Execute os testes para garantir que suas alterações não quebrem o projeto.
5. **Envie um Pull Request:** Envie um pull request para o repositório original.

**Licença:**

Este projeto é licenciado sob a Licença MIT.


