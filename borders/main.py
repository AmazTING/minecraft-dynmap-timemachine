import requests
import json
import PIL.ImageDraw as ImageDraw
import PIL.Image as Image
from PIL import ImageColor
from tqdm import tqdm

r = requests.get('https://map.ccnetmc.com/nationsmap/tiles/_markers_/marker_world.json')
data = r.json()

data = data['sets']['towny.markerset']['areas']
new_dataset = {}
for i in data.keys():
    if ("shop" in i.lower()):
        pass
    else:
        new_dataset[i] = data[i]


#print(json.dumps(new_dataset, indent=4))

coords = []
outcolor = []
colors = []

for i in new_dataset:
    temp_array = []
    temp_color = new_dataset[i]['fillcolor']
    temp_color = ImageColor.getcolor(f"{temp_color}", "RGBA")
    temp_color = (temp_color[0], temp_color[1], temp_color[2], 100)
    outcolor.append(new_dataset[i]['color'])
    colors.append(temp_color)
    for j in range(len(new_dataset[i]['x'])):
        temp_array.append((new_dataset[i]['x'][j] + 21500, new_dataset[i]['z'][j] + 10750))
    coords.append(temp_array)


coords = tuple(coords)

print(coords)

#print(coords)
print(colors)
print(outcolor)
image = Image.new('RGBA', (43000, 21500), (255, 255, 255, 0))
draw = ImageDraw.Draw(image)

# convert colors to rgb tuples


for i in tqdm(range(len(coords)), desc="Processing", unit="poylgons"):
    draw.polygon(coords[i], fill=(colors[i]), outline=outcolor[i], width=1)

image.save("borders.png")
