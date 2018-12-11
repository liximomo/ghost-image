import sys
import math
from PIL import Image, ImageDraw, ImageFont


def scale_pixel(pixel, range):
    begin, end = range
    return int(begin + pixel / 255.0 * (end - begin))


def save_image(image, path):
    image.save(path, 'png')


def create_image(i, j):
    image = Image.new("RGBA", (i, j))
    return image


def get_pixel(image, i, j):
    # Inside image bounds?
    width, height = image.size
    if i > width or j > height:
        return None

    # Get Pixel
    pixel = image.getpixel((i, j))
    return pixel


def make_semi_transparent(image, begin_with_transparent, meltToBlack):
    width, height = image.size
    new = create_image(width, height)
    pixels = new.load()

    # Transform to primary
    for col in range(width):
        transparent_index = 0 if begin_with_transparent else 1
        for row in range(height):
            # Get Pixel
            pixel = get_pixel(image, col, row)

            # Get R, G, B values (This are int from 0 to 255)
            red = pixel[0]
            green = pixel[1]
            blue = pixel[2]

            gray = int((red * 0.299) + (green * 0.587) + (blue * 0.114))

            if row % 2 == transparent_index:
                pixels[col, row] = (0, 0, 0, 0)
            else:
                # todo 求补色, 然后再通过与补色的距离求透明度
                # 距离越近, 透明度越低, 使其显示出本来的颜色
                # 距离越远, 透明度越高, 使其显示出背景的颜色
                if (meltToBlack):
                    pixels[col, row] = (
                        0,
                        0,
                        0,
                        scale_pixel(gray, [255, 0])
                    )
                else:
                    pixels[col, row] = (
                        243,
                        243,
                        243,
                        scale_pixel(gray, [0, 255])
                    )

        begin_with_transparent = not begin_with_transparent

    return new


def watermark(img, text):
    drawing = ImageDraw.Draw(img)
    font = ImageFont.truetype("./resouces/Georgia.ttf", 36)
    drawing.text([10, 10], text, fill=(236, 236, 236), font=font)


def resize(target, limit):
    max_width, max_height = limit
    target_width, target_height = target.size
    scale_x = target_width / target_height > max_width / max_height

    resize_target = None
    if (scale_x):
        new_target_height = math.ceil(
            target_height * (max_width / target_width))
        resize_target = target.resize((max_width, new_target_height))
    else:
        new_target_width = math.ceil(
            target_width * (max_height / target_height))
        resize_target = target.resize((new_target_width, max_height))

    return resize_target


def paste(ori, target):
    ori_width, ori_height = ori.size
    target_width, target_height = target.size
    paste_x = math.ceil((ori_width - target_width) / 2)
    paste_y = math.ceil((ori_height - target_height) / 2)
    if paste_x % 2 != 0:
        # make target interlaced with ori
        paste_x = paste_x + 1
    if paste_y % 2 != 0:
        # make target interlaced with ori
        paste_y = paste_y + 1

    ori.paste(target, (paste_x, paste_y), target)
    return ori


# Main
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('请提供两张图片作为素材')
        exit(1)

    shadowPath = sys.argv[1]
    mainPath = sys.argv[2]

    ori_bg = Image.open(shadowPath)
    ori_main = Image.open(mainPath)
    main = resize(ori_main, ori_bg.size)

    bg = make_semi_transparent(ori_bg, False, True)
    semi_main = make_semi_transparent(main, True, False)

    out = paste(bg, semi_main)

    watermark(out, '@liximomo')
    save_image(out, 'out.png')
