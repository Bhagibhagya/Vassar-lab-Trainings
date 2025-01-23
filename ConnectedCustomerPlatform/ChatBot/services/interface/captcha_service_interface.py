from abc import ABC, abstractmethod
class ICaptchaService(ABC):
    @abstractmethod
    def generate_captcha_image(self, width, height, length):
        """
        Generates a CAPTCHA image and text.
        Args:
            width (int): Width of the CAPTCHA image.
            height (int): Height of the CAPTCHA image.
            length (int): Length of the CAPTCHA text.
        Returns:
            tuple: Base64 encoded CAPTCHA image and CAPTCHA text.
        """


    @abstractmethod
    def draw_captcha_text_with_spaces(self, draw, font, image, raw_text, width, height):
        """
        Draws the CAPTCHA text with random spaces, random rotation, and positioning for each character.
        Args:
            draw (ImageDraw): The drawing object for adding text to the image.
            font (ImageFont): The font used for drawing the text.
            image (Image): The CAPTCHA image.
            raw_text (str): The original CAPTCHA text without spaces.
            width (int): Width of the CAPTCHA image.
            height (int): Height of the CAPTCHA image.
        """

    @abstractmethod
    def add_noise(self, draw, width, height):
        """
        Adds noise like points and ellipses to the CAPTCHA image for obfuscation.
        Args:
            draw (ImageDraw): The drawing object for adding noise to the image.
            width (int): Width of the CAPTCHA image.
            height (int): Height of the CAPTCHA image.
        """

    @abstractmethod
    def image_to_base64(self, image):
        """
        Converts an image to a Base64 encoded string.
        Args:
            image (Image): The image to convert.
        Returns:
            str: Base64 encoded image.
        """
