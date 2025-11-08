import argparse
from PIL import Image

def grid_four_images(img_paths, output_path):
    imgs = [Image.open(p) for p in img_paths]
    # Resize to smallest dimensions among input images
    w = min(img.size[0] for img in imgs)
    h = min(img.size[1] for img in imgs)
    imgs = [img.resize((w, h), Image.ANTIALIAS) for img in imgs]
    grid_img = Image.new('RGB', (w * 2, h * 2))
    grid_img.paste(imgs[0], (0, 0))
    grid_img.paste(imgs[1], (w, 0))
    grid_img.paste(imgs[2], (0, h))
    grid_img.paste(imgs[3], (w, h))
    grid_img.save(output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a 2x2 grid of images.")
    parser.add_argument('img_list', metavar='IMG', nargs=4, help='Four image paths')
    parser.add_argument('-o', '--output', default='grid_output.jpg', help='Output filename')
    args = parser.parse_args()

    grid_four_images(args.img_list, args.output)

