## services/qr_service.py

import qrcode
import os
from pyzbar import pyzbar
from PIL import Image
import cv2
import numpy as np

class QRService:
    def __init__(self):
        pass
    
    def generate_qr_code(self, roll_no: str, branch_code: str, year: str) -> bool:
        """Generate QR code for student"""
        try:
            # Create QR code directory path
            qr_dir = os.path.join("data", "branches", branch_code, year, "qrcodes")
            os.makedirs(qr_dir, exist_ok=True)
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(roll_no)
            qr.make(fit=True)
            
            # Create QR code image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Save QR code
            qr_path = os.path.join(qr_dir, f"{roll_no}.png")
            img.save(qr_path)
            
            return True
            
        except Exception as e:
            print(f"Error generating QR code: {e}")
            return False
    
    def decode_qr_code(self, image_bytes: bytes) -> str:
        """Decode QR code from image bytes"""
        try:
            # Convert bytes to image
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return None
            
            # Convert to PIL Image for pyzbar
            img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            
            # Decode QR codes
            decoded_objects = pyzbar.decode(img_pil)
            
            if decoded_objects:
                # Return the first QR code data
                return decoded_objects[0].data.decode('utf-8')
            
            return None
            
        except Exception as e:
            print(f"Error decoding QR code: {e}")
            return None
    
    def get_qr_code_path(self, roll_no: str, branch_code: str, year: str) -> str:
        """Get QR code file path for a student"""
        return os.path.join("data", "branches", branch_code, year, "qrcodes", f"{roll_no}.png")
