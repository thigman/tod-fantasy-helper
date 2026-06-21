def menu(title, items):
    print(f"\n{title}")

    for i, item in enumerate(items, 1):
        print(f"{i}. {item}")

    while True:

        try:
            value = int(input("> "))

            if 1 <= value <= len(items):
                return value - 1

        except:
            pass

        print("Invalid selection")