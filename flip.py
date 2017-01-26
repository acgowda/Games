import random

coin = ["heads", "tails"]

def flip():
	ui = raw_input("Heads or Tails? ").lower()
	side = random.choice(coin)

	if ui == side:
		print "You Win!"
	else:
		print "You Lose!"


flip()