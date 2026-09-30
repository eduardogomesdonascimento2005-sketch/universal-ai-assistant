import os
import re

from openai import OpenAI

from universal_ai.config import MODEL_NAME, OPENAI_API_KEY
from universal_ai.memory import MemoryStore
from universal_ai.tools import ToolRegistry, parse_tool_request


class UniversalAgent:
    def __init__(self):
        self.memory = MemoryStore()
        self.tools = ToolRegistry()
        self.client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

    def run(self, user_message: str) -> str:
        self.memory.append("user", user_message)

        if not user_message or not user_message.strip():
            return "Desculpe, não recebi uma mensagem válida."

        tool_request = parse_tool_request(user_message)
        if tool_request:
            result = self.execute_tool(tool_request)
            self.memory.append("tool", str(result))
            if self.client:
                prompt = self._build_tool_response_prompt(user_message, result)
                final_text = self.call_model(prompt)
                return final_text
            return self.format_tool_result(result)

        if self.client:
            response = self.call_model(self._build_chat_prompt(user_message))
            self.memory.append("assistant", response)
            return response

        return (
            "Você ainda não configurou a chave da API OpenAI.\n"
            "Crie um arquivo .env com OPENAI_API_KEY=sua_chave.\n"
            "Depois rode novamente o programa."
        )

    def execute_tool(self, tool_request):
        tool_name = tool_request["tool"]
        args = tool_request["args"]

        if tool_name == "list_dir":
            return self.tools.list_dir(args.get("path", "."))
        if tool_name == "read_file":
            return self.tools.read_file(args.get("path", "."))
        if tool_name == "write_file":
            return self.tools.write_file(args.get("path", ""), args.get("content", ""))
        if tool_name == "run_command":
            return self.tools.run_command(args.get("command", ""))
        if tool_name == "search_web":
            return self.tools.search_web(args.get("query", ""))
        return {"status": "erro", "mensagem": "Ferramenta desconhecida"}

    def format_tool_result(self, result):
        if isinstance(result, dict):
            return str(result)
        if isinstance(result, list):
            return "\n".join(f"- {item}" for item in result)
        return str(result)

    def call_model(self, prompt: str) -> str:
        completion = self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "Você é uma IA universal, útil, objetiva e inteligente."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=1500,
        )
        return completion.choices[0].message.content.strip()

    def _build_chat_prompt(self, user_message):
        history = self.memory.recent(8)
        history_text = "\n".join(f"{item['role']}: {item['content']}" for item in history)
        return (
            "Você é um assistente universal. Responda de forma útil e direta.\n\n"
            f"Histórico:\n{history_text}\n\nPergunta atual:\n{user_message}"
        )

    def _build_tool_response_prompt(self, user_message, result):
        return (
            "Você recebeu uma solicitação de usuário que foi executada com uma ferramenta. "
            "Agora responda ao usuário de forma clara, resumindo o resultado e explicando o que foi feito.\n\n"
            f"Pedido do usuário: {user_message}\n\nResultado da ferramenta:\n{result}"
        )
