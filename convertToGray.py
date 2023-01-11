from PIL import Image
file = input("Enter path to file: ")
img_rgb = Image.open(file).convert('L')
img_rgb.save("gray.jpg")
