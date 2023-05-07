from PIL import Image


class ImageConverter:
    def convert_image(self, file, to):
        image = Image.open(file)
        image.save(file, format=to)
