# WhatsApp IA - Assistente Inteligente via WhatsApp

Esta é a versão final da sua IA integrada com WhatsApp Business.

## Recursos

- ✅ Chat automático com IA
- ✅ Memória de conversa por usuário
- ✅ Histórico de mensagens
- ✅ Respostas automáticas
- ✅ Integração com OpenAI
- ✅ Banco de dados SQLite
- ✅ Webhook seguro

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn python-dotenv openai requests sqlalchemy
```

## Configuração

1. Crie o arquivo `.env`

```env
OPENAI_API_KEY=sua_chave_aqui
MODEL_NAME=gpt-4o-mini
WHATSAPP_TOKEN=seu_token_do_whatsapp
WHATSAPP_PHONE_NUMBER_ID=seu_phone_number_id
WHATSAPP_VERIFY_TOKEN=seu_verify_token
```

2. Configure o webhook no Meta

- URL: `https://seu-dominio.com/webhook`
- Verify token: o mesmo do `.env`
- Validar tokens e eventos

3. Rode o servidor

```bash
uvicorn whatsapp_ai:app --reload
```

4. Teste

- Mande uma mensagem para o número do WhatsApp
- A IA vai responder automaticamente

## Fluxo

1. Usuário manda mensagem no WhatsApp
2. Meta envia evento para `/webhook`
3. IA processa a mensagem
4. Salva no banco de dados
5. Envia resposta automática
6. Mantém histórico da conversa

## Endpoints

- `GET /` - status da aplicação
- `GET /health` - saúde do servidor
- `GET /webhook` - verificação de webhook
- `POST /webhook` - recebimento de mensagens

## Próximos passos (opcionais)

- Upload de arquivos no WhatsApp
- Leitura de documentos
- Processamento de imagens
- Integração com banco de dados em produção
- Painel de gerenciamento
- Múltiplos números de WhatsApp

## Suporte

Se houver erros:
- Verifique o token do WhatsApp
- Confirme o phone number ID
- Valide o verify token
- Verifique a chave da OpenAI
