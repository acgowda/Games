inp = raw_input("Enter Command: ")
array = inp.split(" ")
if array[0] == "add":
  sumed = int(array[1]) + int(array[2])
  print str(sumed) + "\n"
else:
  diff = int(array[1]) - int(array[2])
  print str(diff) + "\n"