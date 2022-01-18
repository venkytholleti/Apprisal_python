from passlib.context import CryptContext
import random
import string

pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")
lower = string.ascii_lowercase
upper = string.ascii_uppercase
num = string.digits
# symbols = string.punctuation
all = lower + upper + num

def hash(password:str):
	return pwd_context.hash(password)

def verify(plain_password,hashed_password):
	return pwd_context.verify(plain_password,hashed_password)


def generate_password(length):
	password = random.sample(all,length)
	password = ''.join(password)
	return password