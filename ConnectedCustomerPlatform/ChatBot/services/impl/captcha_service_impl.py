import inspect
import os
import secrets
import string
import base64
from PIL import Image, ImageDraw, ImageFont
import io
import logging
from ChatBot.services.interface.captcha_service_interface import ICaptchaService
from ConnectedCustomerPlatform.exceptions import CustomException

logger = logging.getLogger(__name__)

class CaptchaServiceImpl(ICaptchaService):
    def generate_captcha_image(self, width, height, length):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        """
        Generates a CAPTCHA image and corresponding text.
        
        Args:
            width (int): Width of the CAPTCHA image.
            height (int): Height of the CAPTCHA image.
            length (int): Length of the CAPTCHA text.
        
        Returns:
            tuple: Base64 encoded CAPTCHA image and the raw CAPTCHA text.
        """
        try:
            # Create a blank image with a light grey background
            image = Image.new('RGB', (width, height), '#e0e0e0')
            draw = ImageDraw.Draw(image)
            characters = string.ascii_letters + string.digits
            raw_text = ''.join(secrets.choice(characters) for _ in range(length))

            # Load font and draw the CAPTCHA text on the image
            font = ImageFont.truetype("LiberationSans-Regular.ttf", size=height - 10)

            self.draw_captcha_text_with_spaces(draw, font, image, raw_text, width, height)
            self.add_noise(draw, width, height)

            # Convert the final image to Base64
            img_base64 = self.image_to_base64(image)
            # Return the Base64 image and the raw CAPTCHA text

            encoded_text = base64.b64encode(raw_text.encode()).decode()
            return img_base64, encoded_text
        except Exception as e:
            logger.error(f"Error generating CAPTCHA image: {e}")
            return None, None


    def draw_captcha_text_with_spaces(self, draw, font, image, raw_text, width, height):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
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
        try:
            extra_spacing = 20  # Increased spacing between characters (adjust this as needed)

            # Estimate the average character width for the text
            avg_char_width = sum(draw.textbbox((0, 0), char, font=font)[2] for char in raw_text) / len(raw_text)

            # Estimate how many spaces will be added
            num_spaces = sum(1 for _ in raw_text[:-1] if secrets.choice([True, False]))
            estimated_total_width = len(raw_text) * avg_char_width + num_spaces * extra_spacing

            # Center the text horizontally by calculating the starting x position
            current_x = (width - estimated_total_width) / 2

            # Draw each character with rotation, spacing, and displacement
            for i, char in enumerate(raw_text):
                # Randomly add spaces between characters
                if i < len(raw_text) - 1 and secrets.choice([True, False]):
                    current_x += extra_spacing  # Add space before the next character

                # Randomly rotate and position each character
                angle = secrets.randbelow(61) - 30  # Random angle between -30 and +30 degrees
                displacement = secrets.randbelow(5) - 2  # Random vertical displacement

                # Get the size of the character
                char_width, char_height = draw.textbbox((0, 0), char, font=font)[2:4]
                y = (height - char_height) / 2 + displacement  # Vertical positioning

                # Create a separate image for the character and apply rotation
                char_image = Image.new('RGBA', (char_width, char_height), (0, 0, 0, 0))
                char_draw = ImageDraw.Draw(char_image)
                char_draw.text((0, 0), char, font=font, fill='black')
                char_image = char_image.rotate(angle, expand=1)

                # Paste the rotated character onto the main image
                image.paste(char_image, (int(current_x), int(y)), char_image)

                # Move to the next position
                current_x += char_width  # Move to the next character's starting position

        except Exception as e:
            logger.error(f"Error drawing CAPTCHA text with spaces: {e}")
            raise CustomException("Error drawing CAPTCHA text with spaces.")


    def add_noise(self, draw, width, height):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        """
        Adds noise (points and shapes) to the CAPTCHA image to make it harder for bots to read.
        Args:
            draw (ImageDraw): The drawing object for adding noise.
            width (int): Width of the CAPTCHA image.
            height (int): Height of the CAPTCHA image.
        """
        # Add random points to the image
        try:
            # Add random points to the image
            for _ in range(width * height // 20):
                x, y = secrets.randbelow(width), secrets.randbelow(height)
                draw.point((x, y), fill='black')

            # Add random ellipses (ovals) to the image
            for _ in range(2):
                x1, y1 = secrets.randbelow(width), secrets.randbelow(height)
                x2, y2 = secrets.randbelow(width - x1) + x1, secrets.randbelow(height - y1) + y1
                draw.ellipse([x1, y1, x2, y2], outline='black', width=1)
        except Exception as e:
            logger.error(f"Error adding noise to CAPTCHA image: {e}")


    def image_to_base64(self, image):
        logger.info(f"{self.__class__.__name__} :: {inspect.currentframe().f_code.co_name}")
        """
        Converts the image to a Base64 encoded string.
        Args:
            image (Image): The PIL Image object to encode.
        Returns:
            str: Base64 encoded string of the image.
        """
        # Convert image to binary and encode it in Base64
        try:
            # Convert image to binary and encode it in Base64
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_binary = buffered.getvalue()
            return base64.b64encode(img_binary).decode('utf-8')
        except Exception as e:
            logger.error(f"Error converting image to Base64: {e}")
            return None