import os
from datetime import datetime

import img2pdf
from PIL import Image


def superimpose(file1, file2, new_file):
    background = Image.open(file1).convert('RGBA')
    img = Image.open(file2).convert('RGBA')

    background.paste(img, (0, 0), img)
    background.save(new_file, 'PNG')


def get_concat_h(im1, im2):
    dst = Image.new('RGB', (im1.width + im2.width, im1.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    return dst


def get_concat_v(im1, im2):
    dst = Image.new('RGB', (im1.width, im1.height + im2.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (0, im1.height))
    return dst


def merge(OUT_DIR):
    images = []
    for i in range(1, 4):
        for j in range(1, 3):
            images.append(Image.open(os.path.join(OUT_DIR, f'{j}x{i}.jpg')))

    fi1 = get_concat_h(images[0], images[1])
    fi2 = get_concat_h(images[2], images[3])
    fi3 = get_concat_h(images[4], images[5])

    fi4 = get_concat_v(fi1, fi2)
    get_concat_v(fi4, fi3).save(os.path.join(OUT_DIR, 'page.jpg'))


def build_pdf(OUT_DIR, total_pages):
    print('Creating PDF file')
    today = datetime.today().strftime('%d-%m-%Y')
    image_list = [os.path.join(OUT_DIR, f'page-{pn}', 'page.jpg') for pn in range(1, total_pages + 1)]
    with open(os.path.join(OUT_DIR, f'Tarun-Bharat-Goa-{today}.pdf'), "wb") as out_file:
        out_file.write(img2pdf.convert(image_list))
