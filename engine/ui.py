def menu(title, items):
    print(f"\n{title}")

    for i, item in enumerate(items, 1):
        print(f"{i}. {item}")

    while True:

        try:
            choice = int(input("> "))

            if 1 <= choice <= len(items):
                return choice - 1

        except:
            pass

        print("Invalid selection")