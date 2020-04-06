import pytest
import dash
from PIL import ImageFilter, ImageChops


@pytest.fixture()
def assert_equal_images():
    def func(image_1, image_2, threshold=0.1):
        """
        In this function we check if two images are almost identical
         by blurring and calculating MSE between the images.
        """

        image_1, image_2 = [image.convert("L") for image in [image_1, image_2]]
        image_1, image_2 = [
            image.filter(ImageFilter.GaussianBlur(radius=4))
            for image in [image_1, image_2]
        ]

        pixel_pairs = zip(list(image_1.getdata()), list(image_2.getdata()))
        diff = sum([(pixel_1 - pixel_2) ** 2 for pixel_1, pixel_2 in pixel_pairs])

        error = diff / (image_1.size[0] * image_1.size[1])

        assert error < threshold, "Bounding box: {}".format(
            ImageChops.subtract(image_1, image_2).getbbox()
        )

    return func


@pytest.fixture()
def app():
    dash_app = dash.Dash(__name__)
    dash_app.config.suppress_callback_exceptions = True
    yield dash_app
