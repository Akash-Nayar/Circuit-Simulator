from PIL import Image, ImageDraw


blockSize = 20
circuit_width = 50
circuit_height = 30


img = Image.new(
    "RGBA", (circuit_width * blockSize, circuit_height * blockSize), (255, 0, 0, 0)
)


draw = ImageDraw.Draw(img)
for i in range(circuit_width):
    draw.line(
        (i * blockSize - 1, 0, i * blockSize - 1, blockSize * circuit_height),
        fill=(128, 128, 128, 128),
        width=2,
    )
for j in range(circuit_height):
    draw.line(
        (0, blockSize * j - 1, circuit_width * blockSize, blockSize * j - 1),
        fill=(128, 128, 128, 128),
        width=2,
    )
# draw.ellipse((25, 25, 75, 75), fill=(255, 0, 0))

print(img.size)

img.save("images/lines.png", "png")
