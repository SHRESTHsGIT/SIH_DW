from deepface import DeepFace

# Path to the images
img1_path = "/Volumes/T7_Shield/Projects/SIH_11_NEW/data/branches/CSA/2023/faces/BT23CSA013.jpg"
img2_path = "/Users/shresthshankhdhar/Downloads/12.jpg"

# Verify if the faces are the same
result = DeepFace.verify(img1_path, img2_path)

print(result)
