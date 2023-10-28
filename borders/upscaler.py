import pyvips

imagename = "borders.png"

image = pyvips.Image.new_from_file(imagename, access='sequential')

print(image.width, image.height)

target_height = 86016
target_width = 86016*2

height_factor = target_height / image.height
width_factor = target_width / image.width

image = image.affine([width_factor, 0, 0, height_factor])

image.write_to_file(imagename.split(".")[0] + "_resized.tif", compression="deflate", tile=True, bigtiff=True)