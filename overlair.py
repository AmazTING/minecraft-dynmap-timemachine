import pyvips

# Load the two images
image1 = pyvips.Image.new_from_file('places.png')
image2 = pyvips.Image.new_from_file("final.tif")

images = [image1, image2]

image = images[1].composite(images[0], "over")

image.write_to_file('final_better.tif', compression="deflate", tile=True, bigtiff=True)