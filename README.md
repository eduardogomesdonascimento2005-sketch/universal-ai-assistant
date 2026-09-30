# IA Universal

Um agente de IA completo para executar tarefas gerais com:
- memória de conversa
- execução de comandos do terminal
- leitura e escrita de arquivos
- busca na web
- respostas com ajuda de modelo OpenAI

## Estrutura do projeto

- `main.py` — ponto de entrada da aplicação
- `universal_ai/` — código principal
- `.env.example` — variáveis de ambiente
- `requirements.txt` — dependências
- `README.md` — documentação

## Requisitos

- Python 3.10+
- Conta OpenAI com chave da API

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edite o arquivo `.env` e insira sua chave:

```env
OPENAI_API_KEY=sua_chave_aqui
MODEL_NAME=gpt-4o-mini
```

## Como usar

```bash
python main.py
```

Exemplos de pedidos:

- "Crie uma landing page em HTML para uma loja de roupas"
- "Liste os arquivos da pasta atual"
- "Leia o arquivo README.md e me explique"
- "Pesquise sobre inteligência artificial e me resuma"
- "Crie um script em Python para organizar arquivos de uma pasta"

## Observações

Este é um agente generalista e útil, mas para uso profissional é recomendado:
- definir limites de segurança
- separar permissões por ambiente
- usar banco de dados para memória
- controlar execução de comandos sensíveis

## Licença

MIT
