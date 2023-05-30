from PIL import Image, ImageFont, ImageChops

def trim(im):
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)


def merge(files, resultfile):
    image1 = Image.open(f'resources/lightsaber_parts/Emitter/{files[0]}.png')
    image2 = Image.open(f'resources/lightsaber_parts/Switch/{files[1]}.png')
    image3 = Image.open(f'resources/lightsaber_parts/Sleeve/{files[2]}.png')
    image4 = Image.open(f'resources/lightsaber_parts/Hilt/{files[3]}.png')

    (width1, height1) = image1.size
    (width2, height2) = image2.size
    (width3, height3) = image3.size
    (width4, height4) = image4.size

    result_width = max(width1, width2, width3, height4)
    result_height = height1 + height2 + height3 + height4 - 180

    result = Image.new('RGBA', (result_width, result_height),(0,0,0,0))
    result.paste(im=trim(image1), box=(round((result_width-width1)/2), 10))
    result.paste(im=trim(image2), box=(round((result_width-width2)/2), height1-50))
    result.paste(im=trim(image3), box=(round((result_width-width3)/2), height1+height2-110))
    result.paste(im=trim(image4), box=(round((result_width-width4)/2), height1+height2+height3-170))

    result.save(f'resources/{resultfile}.png')