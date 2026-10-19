
import random
# Word bank

WORDS = [
    "python", "hangman", "programming", "challenge", "developer",
    "function", "variable", "algorithm", "syntax", "debugging","performance", "optimization", "inheritance", "polymorphism", "encapsulation","abstraction", "recursion", "iteration", "exception", "module", "package", "library", "framework", "database", "query", "index", "transaction", "commit", "rollback", "concurrency", "parallelism"
]
def play_hangman():
    word = random.choice(WORDS)
    guessed_letters = set()
    wrong_guesses = 0
    max_attempts = 6

    print("=" * 35)
    print("       WELCOME TO HANGMAN!")
    print("=" * 35)
    print("Guess the hidden word one letter at a time.")
    print(f"You have {max_attempts} incorrect guesses available.\n")

    while wrong_guesses < max_attempts:
        # Display the word with hidden letters
        display_word = " ".join(
            letter if letter in guessed_letters else "_"
            for letter in word
        )
        print("Word:", display_word)

        # Display guessed letters and remaining attempts
        print("Guessed letters:",
              " ".join(sorted(guessed_letters)) or "None")
        print("Attempts remaining:", max_attempts - wrong_guesses)

        # Get and validate user input
        guess = input("\nEnter a letter: ").strip().lower()

        if len(guess) != 1 or not guess.isalpha():
            print("Invalid input! Enter a single letter (A-Z).\n")
            continue

        if guess in guessed_letters:
            print(f"You already guessed '{guess}'. Try another letter.\n")
            continue

        guessed_letters.add(guess)

        if guess in word:
            print(f"Correct! '{guess}' is in the word.\n")
        else:
            wrong_guesses += 1
            print(f"Incorrect! '{guess}' is not in the word.\n")

        # Check for a win
        if all(letter in guessed_letters for letter in word):
            print("Word:", " ".join(word))
            print("\nCongratulations! You guessed the word!")
            print(f"You used {wrong_guesses} incorrect guesses.")
            return

    # Game over
    print("Word:", " ".join(word))
    print("\nGAME OVER! You ran out of attempts.")
    print(f"The correct word was: {word}")


if __name__ == "__main__":
    while True:
        play_hangman()

        play_again = input("\nWould you like to play again? (y/n): ")
        if play_again.strip().lower() != "y":
            print("Thanks for playing Hangman!")
            break
        print()
