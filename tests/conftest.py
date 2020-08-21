import os
import sys
import pluggy
import pytest
import dash

from PIL import ImageFilter, ImageChops

# Allow everviz to be installed and have tests run without installing everest
module = type(sys)("everest.plugins")
module.hookimpl = pluggy.HookimplMarker("test")
sys.modules["everest.plugins"] = module


@pytest.fixture()
def assert_equal_images(tmpdir):
    def func(image_1, image_2, threshold=0.1):
        """
        In this function we check if two images are almost identical
         by blurring and calculating MSE between the images.
        """
        filename1 = (
            os.path.join(tmpdir, image_1.filename)
            if not os.path.isabs(image_1.filename)
            else image_1.filename
        )
        filename2 = (
            os.path.join(tmpdir, image_2.filename)
            if not os.path.isabs(image_2.filename)
            else image_2.filename
        )

        image_1, image_2 = [image.convert("L") for image in [image_1, image_2]]
        image_1, image_2 = [
            image.filter(ImageFilter.GaussianBlur(radius=5))
            for image in [image_1, image_2]
        ]

        pixel_pairs = zip(list(image_1.getdata()), list(image_2.getdata()))
        diff = sum([(pixel_1 - pixel_2) ** 2 for pixel_1, pixel_2 in pixel_pairs])

        error = diff / (image_1.size[0] * image_1.size[1])

        assert (
            error < threshold
        ), "Bounding box: {}\nImage 1 path: {}\nImage 2 path: {}\n".format(
            ImageChops.subtract(image_1, image_2).getbbox(), filename1, filename2
        )

    return func


@pytest.fixture()
def app():
    dash_app = dash.Dash(__name__)
    dash_app.config.suppress_callback_exceptions = True
    yield dash_app
