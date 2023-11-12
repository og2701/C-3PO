from PIL import Image, ImageChops

def center_of_pixels(im, top=True):
    left, right = im.width, 0
    rows = range(15) if top else range(im.height - 5, im.height)
    for y in rows:
        for x in range(im.width):
            pixel = im.getpixel((x, y))
            if pixel[3] > 0:
                left = min(left, x)
                right = max(right, x)
    center = (left + right) // 2 if left < right else im.width // 2
    return center

def trim(im, top=True):
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox), center_of_pixels(im.crop(bbox), top)
    return im, im.width // 2

def merge(files, resultfile):
    parts = ['Emitter', 'Switch', 'Sleeve', 'Hilt']
    images = [Image.open(f'resources/lightsaber_parts/{part}/{files[i]}.png') for i, part in enumerate(parts)]

    trimmed_images = [trim(images[i], top=(parts[i] != 'Emitter')) for i in range(len(parts))]
    heights = [i[0].size[1] for i in trimmed_images]

    max_left_width = max_right_width = 0
    for img, center in trimmed_images:
        width = img.width
        left_width = center
        right_width = width - center
        max_left_width = max(max_left_width, left_width)
        max_right_width = max(max_right_width, right_width)

    result_width = max_left_width + max_right_width
    result_height = sum(heights) - 180

    result = Image.new('RGBA', (result_width, result_height), (0, 0, 0, 0))

    current_height = 10
    for img, center in trimmed_images:
        width, height = img.size
        x_position = max_left_width - center
        result.paste(im=img, box=(x_position, current_height))
        current_height += height - 50

    result.save(f'resources/{resultfile}.png')
