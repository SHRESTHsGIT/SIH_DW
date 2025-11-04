## services/face_service.py

import cv2
import os
import numpy as np
from deepface import DeepFace
import tempfile
from typing import Optional, Tuple

class FaceService:
    def __init__(self):
        self.confidence_threshold = 0.6
    
    def save_face_image(self, image_bytes: bytes, roll_no: str, branch_code: str, year: str) -> bool:
        """Save face image for a student"""
        try:
            # Create face directory path
            face_dir = os.path.join("data", "branches", branch_code, year, "faces")
            os.makedirs(face_dir, exist_ok=True)
            
            # Save image
            face_path = os.path.join(face_dir, f"{roll_no}.jpg")
            
            # Convert bytes to image
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return False
            
            # Save image
            success = cv2.imwrite(face_path, img)
            return success
            
        except Exception as e:
            print(f"Error saving face image: {e}")
            return False
    
    def recognize_face(self, input_image_bytes: bytes, branch_code: str, year: str) -> Optional[str]:
        """Recognize face and return roll number of best match"""
        try:
            print(f"🔍 Starting face recognition for {branch_code}/{year}")
            
            # Save input image temporarily
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                tmp_file.write(input_image_bytes)
                input_image_path = tmp_file.name
            print(f"📁 Input image saved to: {input_image_path}")
            
            # Get all face images from the faces directory
            faces_dir = os.path.join("data", "branches", branch_code, year, "faces")
            print(f"📂 Looking for faces in: {faces_dir}")
            
            if not os.path.exists(faces_dir):
                print(f"❌ Faces directory not found: {faces_dir}")
                os.unlink(input_image_path)
                return None
            
            face_files = [f for f in os.listdir(faces_dir) if f.endswith('.jpg')]
            print(f"📊 Found {len(face_files)} face images to compare")
            
            if not face_files:
                print("❌ No face images found in database")
                os.unlink(input_image_path)
                return None
            
            best_match = None
            lowest_distance = float('inf')
            all_results = []
            
            # Compare with all stored faces and find best match
            for face_file in face_files:
                roll_no = face_file.replace('.jpg', '')
                stored_face_path = os.path.join(faces_dir, face_file)
                
                try:
                    print(f"🔄 Comparing with {roll_no}...")
                    
                    # Use DeepFace to verify faces
                    result = DeepFace.verify(
                        img1_path=input_image_path,
                        img2_path=stored_face_path,
                        model_name='VGG-Face',
                        enforce_detection=False
                    )
                    
                    distance = result['distance']
                    verified = result['verified']
                    
                    print(f"   📈 {roll_no}: distance={distance:.4f}, verified={verified}")
                    
                    # Store result for logging
                    all_results.append({
                        'roll_no': roll_no,
                        'distance': distance,
                        'verified': verified
                    })
                    
                    # Check if this is the best match so far
                    if verified and distance < lowest_distance:
                        lowest_distance = distance
                        best_match = roll_no
                        print(f"   ✅ New best match: {roll_no} with distance {distance:.4f}")
                        
                except Exception as e:
                    print(f"❌ Error comparing with {roll_no}: {str(e)}")
                    continue
            
            # Clean up temporary file
            os.unlink(input_image_path)
            
            # Log all comparison results
            print(f"📊 All comparison results:")
            for result in sorted(all_results, key=lambda x: x['distance']):
                status = "✅ VERIFIED" if result['verified'] else "❌ NOT VERIFIED"
                print(f"   {result['roll_no']}: {result['distance']:.4f} - {status}")
            
            if best_match:
                print(f"🎯 BEST MATCH FOUND: {best_match} with distance {lowest_distance:.4f}")
                return best_match
            else:
                print("❌ No verified matches found")
                return None
            
        except Exception as e:
            print(f"❌ Critical error in face recognition: {str(e)}")
            # Clean up temporary file if it exists
            try:
                if 'input_image_path' in locals():
                    os.unlink(input_image_path)
            except:
                pass
            return None
    
    def extract_face_from_camera(self, image_bytes: bytes) -> Optional[bytes]:
        """Extract and crop face from camera image"""
        try:
            # Convert bytes to image
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return None
            
            # Use OpenCV's face detection to crop face
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) > 0:
                # Take the largest face
                largest_face = max(faces, key=lambda x: x[2] * x[3])
                x, y, w, h = largest_face
                
                # Add some padding around the face
                padding = int(0.2 * min(w, h))
                x = max(0, x - padding)
                y = max(0, y - padding)
                w = min(img.shape[1] - x, w + 2 * padding)
                h = min(img.shape[0] - y, h + 2 * padding)
                
                # Crop face
                face_img = img[y:y+h, x:x+w]
                
                # Encode back to bytes
                _, buffer = cv2.imencode('.jpg', face_img)
                return buffer.tobytes()
            
            # If no face detected, return original image
            _, buffer = cv2.imencode('.jpg', img)
            return buffer.tobytes()
            
        except Exception as e:
            print(f"Error extracting face: {e}")
            return None