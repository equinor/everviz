import os
import sys

import dash
import pluggy
import pytest
from PIL import ImageChops, ImageFilter
from selenium.webdriver.common.by import By

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
        diff = sum((pixel_1 - pixel_2) ** 2 for pixel_1, pixel_2 in pixel_pairs)

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


class HelperFunctions:
    """Class containing helper functions used in tests"""

    @staticmethod
    def select_first(dash_duo, selector):
        element = dash_duo.find_element(selector)
        option = element.find_element(By.CSS_SELECTOR, "option")
        option_text = option.text
        option.click()
        return option_text

    @staticmethod
    def clear_dropdown(dash_duo, selector):
        element = dash_duo.find_element(selector)
        element.find_element(By.CSS_SELECTOR, "span.Select-clear").click()


@pytest.fixture
def helpers():
    return HelperFunctions
