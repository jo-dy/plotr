import models
import string
import random

def generate_unique_id():	
	ID_STRING_LEN = 5
	new_id = generate_id(ID_STRING_LEN)
	while models.Dataset.objects.filter(data_id = new_id).count() > 0:
		new_id = generate_id(ID_STRING_LEN)
	return new_id

def generate_id(n):	
	return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(n))