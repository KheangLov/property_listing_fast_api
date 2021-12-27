
import base64
import datetime
import shutil


class Base64ToFile:
    def __init__(self, data):
        self.data = data
        self.base64_img_bytes = self.data.encode('utf-8')
        self.__convert()

    def __convert(self):
        self.file_name = self.__generate_name()
        with open(f"{self.file_name}.jpg", 'wb') as file_to_save:
            decoded_image_data = base64.decodebytes(self.base64_img_bytes)
            file_to_save.write(decoded_image_data)
            shutil.move(f"{self.file_name}.jpg", f'images/{self.file_name}.jpg')
            file_to_save.close()

    @property
    def filename(self):
        return f"{self.file_name}.jpg"

    @classmethod
    def __generate_name(cls):
        return int(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
