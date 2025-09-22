def simple_test():
    numbers = []
    numbers.append(42)
    numbers.append(24)

    total = 0
    for num in numbers:
        total += num

    return total

def main():
    result = simple_test()
    print(f"Result: {result}")
    return 0

if __name__ == "__main__":
    main()