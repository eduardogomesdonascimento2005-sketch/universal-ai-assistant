from universal_ai import UniversalAgent


def main():
    agent = UniversalAgent()
    print("\n=== IA Universal ===")
    print("Digite 'sair' para encerrar.\n")

    while True:
        user_input = input("Você: ")
        if user_input.strip().lower() in {"sair", "exit", "quit"}:
            print("Até logo!")
            break

        response = agent.run(user_input)
        print(f"\nIA: {response}\n")


if __name__ == "__main__":
    main()
