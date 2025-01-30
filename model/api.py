from flask import Flask, request, jsonify
from PIL import Image
import numpy as np
import tensorflow as tf  
from io import BytesIO

app = Flask(__name__)

model_size = tf.keras.models.load_model('model/size_model.h5') 
model_brand = tf.keras.models.load_model('model/brand_model.h5')  

size_classes = ['bottle_1250ml', 'bottle_2000ml', 'bottle_330ml', 'bottle_345ml', 'bottle_350ml', 
                'bottle_380ml', 'bottle_450ml', 'bottle_500ml', 'bottle_590ml', 'can'] 
brand_classes = ['7-11', 'aura', 'coke', 'fanta', 'gatorade', 'mirinda', 'oishi']  


CONFIDENCE_THRESHOLD = 0.8

def preprocess_image(image_bytes):
    image = Image.open(BytesIO(image_bytes))
    image = image.resize((224, 224))  
    image = np.array(image) / 255.0  
    image = np.expand_dims(image, axis=0)  
    return image

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        image_bytes = file.read()
        processed_image = preprocess_image(image_bytes)

        size_prediction = model_size.predict(processed_image)
        size_index = np.argmax(size_prediction)  
        size_confidence = np.max(size_prediction) 

        brand_prediction = model_brand.predict(processed_image)
        brand_index = np.argmax(brand_prediction)  
        brand_confidence = np.max(brand_prediction)  

        size_name = size_classes[size_index] if size_confidence >= CONFIDENCE_THRESHOLD else "unknown"
        brand_name = brand_classes[brand_index] if brand_confidence >= CONFIDENCE_THRESHOLD else "unknown"

        return jsonify({
            "size": size_name,  
            "brand": brand_name  
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
