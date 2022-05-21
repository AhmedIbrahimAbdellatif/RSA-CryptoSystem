from rsa import encrypt
import yaml
import math
import socket
import sys
from dataclasses import dataclass
from algorithm.utils import RSAUtils, UserInterfaceUtils

@dataclass
class Params:
    p: int
    q: int
    n: int
    e: int
    d: int

class RSA:
    def __init__(self):
        with open("src\configurations.yaml", "r") as f:
            config = yaml.safe_load(f)
        self.key_length = math.floor(config["KEY_GENERATION"]["KEY_LENGTH"])
        self.prime_min_length = math.floor(config["KEY_GENERATION"]["PRIME_MIN_LENGTH"])
        assert self.prime_min_length >= 2, "prime min length must be greater than or equal 2" 
        assert self.key_length > self.prime_min_length, "key length must be > prime min length" 
        self.prime_max_length = self.key_length - self.prime_min_length
        assert self.prime_max_length > self.prime_min_length, "min length must be less than half the key length"
        self.first_sample_max_size = math.floor(config["KEY_GENERATION"]["FIRST_SAMPLE_MAX_SIZE"])
        self.middle_sample_max_size = math.floor(config["KEY_GENERATION"]["MIDDLE_SAMPLE_MAX_SIZE"])
        self.third_sample_max_size = math.floor(config["KEY_GENERATION"]["THIRD_SAMPLE_MAX_SIZE"])
        self.e_max_length = math.floor(config["KEY_GENERATION"]["E_MAX_LENGTH"])
        self.e_options_max_count = math.floor(config["KEY_GENERATION"]["E_OPTIONS_MAX_COUNT"])
        self.params = None
        UserInterfaceUtils.display_starting_message(self.key_length)
    
    def generate_key(self, isInteractive: bool):
        smallest_prime = 2 ** (self.prime_min_length - 1)
        p_max = (2 ** self.prime_max_length) - 1
        method = "Randomly" if not isInteractive else UserInterfaceUtils.get_selection_mode("p & q")
        if method == "Randomly":
            p, q = RSAUtils.get_random_p_q(self.key_length)
        else:
            prime_candidates = RSAUtils.get_prime_candidates(self.key_length, smallest_prime, p_max, self.first_sample_max_size, self.middle_sample_max_size, self.third_sample_max_size)
            p, q = RSAUtils.get_p_q_from_user(self.key_length, smallest_prime, prime_candidates, self.first_sample_max_size, self.middle_sample_max_size, self.third_sample_max_size)
        assert(p != q)
        n = p * q
        phi = (p - 1) * (q - 1)
        UserInterfaceUtils.display_horizontal_line()
        method = "Randomly" if not isInteractive else UserInterfaceUtils.get_selection_mode("e")
        if method == "Randomly":
            e = RSAUtils.get_random_e(self.e_max_length, phi)
        else:    
            e = RSAUtils.get_e_from_user(self.e_max_length, phi, self.e_options_max_count)
        assert(math.gcd(phi, e) == 1)
        d = RSAUtils.get_inverse(e, phi)
        assert((d != None) and ((d*e) % phi == 1))
        self.params = Params(p, q, n, e, d)
        UserInterfaceUtils.display_generated_parameters(p,q,n,e,d)
    
    def encrypt_block(block:int, e: int, n: int):
        return pow(block, e, n)

    def send_encrypted_message_blocks(connection: socket, message: str, e, n, key_length, is_communication_mode):
        block = 0
        block_size = 0
        for index in range(len(message)+1):
            if block_size + 8 >= key_length or index >= len(message):
                encrypted_block = RSA.encrypt_block(block, e, n)
                if is_communication_mode: connection.send((str(encrypted_block) + "\t" + str(block_size) + "\n").encode("utf8"))
                block = 0
                block_size = 0
            
            if index < len(message):
                character = message[index]
                block = (block << 8) + ord(character)
                block_size += 8
    
    def decrypt_block(block: int, d: int, n: int):
        return pow(block, d, n)

    def decrypt_message_block(block:int, block_size:int, d, n):
        num_finished_chars = 0
        original_block = ""
        decrypted_characters = RSA.decrypt_block(block, d, n)
        while num_finished_chars < block_size:
            character = chr(decrypted_characters & 0xFF)
            original_block = character + original_block
            decrypted_characters = decrypted_characters >> 8
            num_finished_chars += 8
        return original_block