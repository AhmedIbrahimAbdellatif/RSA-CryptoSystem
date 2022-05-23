# RSA Cryptographic System

> This is the project of the Computer Systems Security (CPMN426) course at Communication and Computer Engineering major, Credit-Hour System, faculty of Engineering, Cairo University.
>
> The project is focused on implementing [RSA](https://en.wikipedia.org/wiki/RSA_(cryptosystem)) and its possible attacks

***

**Used Language:**

<img align="left" alt="Python" src="https://img.shields.io/badge/python-%2314354C.svg?style=for-the-badge&logo=python&logoColor=white"/> <br/>

***

## How to Run

> *****
>
> **DISCLAIMER:**
>
> - I run my scripts from the powershell terminal in VSCode, please use the same terminal to replicate my results as the CLI library (called "inquirer") that I used might have some glitches with other terminals
> - When entering messages in the sender terminal please don't press other buttons other than the `letters` buttons, the `backspace` button and the `enter` button because the library gives an exception if another letter is pressed
>
> 

***

1. Install the required packages using the following command: `pip install -r .\requirements.txt`

2. Inside `src\scripts` directory, you have 4 scripts that you can run

   - Interactive demo:

     > A demo of the normal usage of RSA where there are 2 parties using an encrypted communication, where one party acts as the sender (sending messages encrypted with the public key "e") and the other party acts as the receiver (decrypting received messages with the private key "d")

     1. Inside `src` directory there is a `configurations.yaml` file where you can configure the key length (i.e. length of n) and the min length of the prime factors (to ensure a certain level of security). There are other configurations in this file that will change how the algorithm operates but you can leave them with the default values.

        - *Make sure that the min prime length is a value less that half the key length you specified*

     2. Inside `src\scripts` and run the command: `python .\interactive_demo.py -h` This will show you how to run the script to act as "receiver" or as a "sender". Run each one of them in a different terminal.

        - *Please run the "receiver" first as it is the party that generates the RSA key-pair and sends the public one to the "sender" to start the encrypted communication, so it uses the socket that needs to be created first so that the sender socket can connect to it*

     3. In the receiver terminal, you will be prompted by a question to choose if you want to choose `p` and `q` (RSA prime factors) manually from a list of generated valid options, or let the code generate them automatically for you in a randomized way.

        - This is how the prompt looks

          <img src=".\docs\prompt.png"/>

        - This is how the selection from the list of options looks

          <img src=".\docs\p_values.png"/>

     4. After RSA prime factors are chosen/randomly generated, the algorithm has already generated the public value `n` and is ready to choose the public value of the encryption key `e`. So you will be prompted by a question if you want to choose it manually or randomly just like what happened with `p` and `q`

     5. The receiver will share the public key values (`e` and `n`) with the sender and you can start sending messages from the sender terminal, they will be encrypted and sent to the receiver socket where they will be decrypted and displayed on the receiver terminal

        - This is how it looks like at the sender

          <img src=".\docs\sender.png"/>

        - This is how it looks like at the receiver

          <img src=".\docs\receiver.png"/>

     6. To end the communication, send an empty message from the sender terminal (just press Enter)

   - Performance statistics:
     - This script is not interactive and you don't need to do any configurations since the script tries different key lengths to show meaningful statistics for the speed of key generation and encryption.
     - You only need to run the command `python .\performance_stats.py`
     - The output will be graphs showing statistics and they will be saved in `src\stats\rsa_stats` directory

   - Chosen ciphertext attack demo:

     - This demo is not interactive so all you need to do is do the key length and min prime length in the `configurations.yaml` file just like what is explained in the interactive demo and then run the command `python .\chosen_cipher_text_attack_demo.py`

       1. Two sockets will be opened (each one opened by a different thread), one for the legitimate user "Bob", and one for the attacker "Eve" and the attack will be simulated where the attacker manages to use a chosen ciphertext attack to crack a randomly generated message sent by the legitimate user.

       2. The output in the terminal will be the original message printed from the thread simulating legitimate user behavior and the cracked message printed from the thread simulating the attacker behavior. Both messages are expected to match since this script is simulating a successful CCA attack on RSA.

          <img src=".\docs\CCA.png"/>

   - Brute force attack demo and statistics:

     - This demo is not interactive and you don't need to do any configurations since the script tries different key lengths to show meaningful statistics for the speed of bruteforce attack (factorizing `n` using bruteforce over the value of `p`).
     - You only need to run the command `python .\bruteforce_demo.py`
     - The output will be graphs showing statistics and they will be saved in `src\stats\bruteforce_stats` directory

***

## RSA Implementation

### Key Generation

- Configurable parameters (all in `src\configurations.yaml` ):

  - key length (`n`) in bits
  - min prime length in bits (lower limit for `p` and `q`)
  - `e` max length in bits
  - `e` max options count (to choose from in manual choice mode for `e` value in interactive demo)
  - first/second/third sample size (to choose from in manual choice mode for `p` and `q` prime values in interactive demo)

- Generating prime numbers

  - First trial

    - I first tried a method called [Sieve of Eratosthenes](https://en.wikipedia.org/wiki/Sieve_of_Eratosthenes)
    - This method is used to generate all primes up to a certain number, it is a deterministic method but it's an O(n log(log n)) algorithm and the best complexity it can reach is O(n) with some modifications of the classical algorithm which is still not desirable for large values as in our case

  - Second trial (the currently used one)

    - I tried a randomized method inspired by Monte-Carlo. Which is to randomly choose a number of values from a certain range

    - I adapted it to be suitable for generating our `p` and `q`, so instead of just choosing a number of values from a certain range, I made sure that the chosen values are primes as follows

      - To speed up the process I stored the prime values between 2-349 so if the range I want overlaps with these values I directly add these values to my prime set to avoid unnecessary computations

      - Then I start to randomly choose values within the required range and for each value I run 2 checks before I accept it as a prime and add it to my set. The 2 checks are

        - A simple check: *make sure that this candidate is not divisible by any of the set of the primes between 2-349*

        - A Miller-Rabin check: *make sure that there is no factor (< this candidate) where the following formula holds:*

          <img src="https://latex.codecogs.com/svg.image?base^{\&space;factor\&space;*\&space;2^i}=-1\&space;mod\&space;prime\&space;candidate">

          *`i` takes values between 0 and the number of factorization trials which is determined by the number of required shifts to make the prime candidate an even number, and `base` is a random number between 2 and the prime candidate*

    - Then I choose a value for the `p` and a value for `q` where the length their product is within the key length

  * Differences between modes
    * In random generation mode, I generate my prime candidates from the range with length around the half the max key length to ensure that `p` and `q` will be large yet will differ in length by only a few number of bits to make it difficult to bruteforce
    * In manual choice mode, I generate prime candidates from the whole range, but I sample a number of prime numbers from each range with the upper limit configured for each range in the `src\configurations.yaml` file. And I provide the user with these sampled prime candidates as a list of valid options to choose from

- `n` (public key) is calculated as the product of `p` and `q` as instructed by the RSA algorithm

- `phi` is calculated as the product of `p-1` and `q-1` as instructed by the RSA algorithm

- Choosing `e` (public key)

  - To get valid values for `e` I generate random values (modified approach inspired by Monte-Carlo) between 2 and phi (or the upper limit for `e` determined from the max length of `e` configured in the `src\configurations.yaml` file), then I run the Euclidean algorithm on each candidate value to ensure that it is coprime with `phi`
  - Difference between modes
    - In random generation mode, I generate one valid value for `e` and accept it as my public key value for `e`
    - In manual choice mode, I generate different candidates for `e` until I reach the number of choices configured by the user for `e` in the `src\configurations.yaml` file

- `d` is calculated as the inverse of `e` mod `phi`, this is calculated using the extended Euclidean algorithm

### Encrypted Communication

1. The receiver generates the key-pair and sends the public key (`e` and `n`) to the sender
2. The sender divides the message into blocks < size of key
3. The sender encrypts each block by raising the numeric value representing the plaintext block to the power of `e` mod `n`
4. The sender concatenates the encrypted block with its size and sends over socket communication
5. The receiver does the decryption by raising the numeric value representing the encrypted block to the power of `d` mod `n`
6. This operation is done until all blocks are encrypted and sent by the sender party and all are received, decrypted and put again in the original form at the receiver

### Test Cases

> My implementation allows sending any alphanumeric (not only numbers) text of any size over an RSA-encrypted socket communication

To test my implementation of RSA:

1. Run the interactive demo as instructed [above](#How-to-Run) with any key length of your choice
2. Send messages with the following criteria from the sender terminal and ensure that they are received and decrypted correctly at the receiver and the original messages are displayed at the receiver terminal
   - A message consisting of numbers only: `2352022`
   - A message consisting of letters only: `Ahmed Ibrahim`
   - A message consisting of numbers and letters but starts with a letter: `CMPN426`
   - A message consisting of numbers and letters but starts with a number: `23 of May`
   - A message consisting of a single letter: `a`
   - A message consisting of a single number: `0`
   - An empty message to close the communication successfully

***

