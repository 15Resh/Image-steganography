from PIL import Image

def encode_message(image_path, message, output_path):
    img = Image.open(image_path)
    img = img.convert("RGB")
    
    pixels = img.load()
    message += "###"  # End delimiter
    binary_message = ''.join(format(ord(i), '08b') for i in message)
    
    if len(binary_message) > img.width * img.height:
        raise ValueError("Message too large for image.")

    data_index = 0
    for y in range(img.height):
        for x in range(img.width):
            r, g, b = pixels[x, y]
            if data_index < len(binary_message):
                r = (r & ~1) | int(binary_message[data_index])
                data_index += 1
            pixels[x, y] = (r, g, b)

    img.save(output_path)

def decode_message(image_path):
    img = Image.open(image_path)
    img = img.convert("RGB")

    binary_message = ""
    for y in range(img.height):
        for x in range(img.width):
            r, _, _ = img.getpixel((x, y))
            binary_message += str(r & 1)

    message = "".join(chr(int(binary_message[i:i+8], 2)) for i in range(0, len(binary_message), 8))
    return message.split("###")[0]
