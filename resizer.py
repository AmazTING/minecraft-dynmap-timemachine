import pyvips


name = input("Enter the name of the file: ")

wiki = pyvips.Image.thumbnail(name, 8192)
wiki.write_to_file(name.split(".")[0] + "_wiki.jpg")
print("Wiki done!")


small = pyvips.Image.thumbnail(name, 10000)
small.write_to_file(name.split(".")[0] + "_large.png")
print("Large done!")


tiny = pyvips.Image.thumbnail(name, 2000)
tiny.write_to_file(name.split(".")[0] + "_medium.png")
print("Medium done!")

micro = pyvips.Image.thumbnail(name, 500)
micro.write_to_file(name.split(".")[0] + "_small.png")
print("Small done!")