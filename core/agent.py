from .tools import ToolRegistry, parse_tool_request

__all__ = ["ProfessionalAgent"]


class ProfessionalAgent:
    def __init__(self):
        self.tools = ToolRegistry()

    def respond(self, username: str, user_prompt: str) -> str:
        prompt = (user_prompt or "").strip()
        if not prompt:
            return "Digite uma tarefa válida."

        tool_request = parse_tool_request(prompt)
        if tool_request:
            result = self.execute_tool(tool_request)
            return self.format_tool_result(prompt, result)

        return self.ask_llm(prompt, username)

    def format_tool_result(self, prompt: str, result):
        if isinstance(result, dict):
            result_text = str(result)
        elif isinstance(result, list):
            result_text = "\n".join(str(item) for item in result)
        else:
            result_text = str(result)

        summary = (
            "A ação foi executada com sucesso. "
            "Aqui está o resultado: \n\n"
            f"Pedido: {prompt}\n\nResultado:\n{result_text}"
        )
        return summary

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

    def ask_llm(self, prompt: str, username: str) -> str:
        from openai import OpenAI
        import os

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        if not os.getenv("OPENAI_API_KEY"):
            return "Chave da OpenAI não configurada. Adicione OPENAI_API_KEY no .env."

        completion = client.chat.completions.create(
            model=os.getenv("MODEL_NAME", "gpt-4o-mini"),
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é uma IA profissional e muito útil. "
                        "Responda de forma clara, objetiva e útil. "
                        "Se precisar, proponha passos concretos e organize a resposta."
                    ),
                },
                {"role": "user", "content": f"Usuário: {username}\n\nPedido: {prompt}"},
            ],
            temperature=0.7,
            max_tokens=1500,
        )

        return completion.choices[0].message.content.strip()
