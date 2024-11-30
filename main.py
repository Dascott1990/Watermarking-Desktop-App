import base64
from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

app = Flask(__name__)

# Route to display the form
@app.route('/')
def home():
    return render_template('index.html')

# Route to upload image and apply watermark
@app.route('/upload', methods=['POST'])
def upload():
    # Get the file and watermark text from the form
    file = request.files.get('image')
    watermark_text = request.form.get('watermark')
    position = request.form.get('position')

    if file and watermark_text:
        # Open the image
        image = Image.open(file)

        # Create watermark
        image_editable = ImageDraw.Draw(image)
        font = ImageFont.load_default()

        # Get the bounding box for the watermark text
        bbox = image_editable.textbbox((0, 0), watermark_text, font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Default position if user doesn't select one
        if position == 'top-left':
            watermark_position = (10, 10)
        elif position == 'top-right':
            watermark_position = (image.width - text_width - 10, 10)
        elif position == 'bottom-left':
            watermark_position = (10, image.height - text_height - 10)
        elif position == 'bottom-right':
            watermark_position = (image.width - text_width - 10, image.height - text_height - 10)
        elif position == 'custom':
            # If user selects 'custom', let them specify coordinates
            x = int(request.form.get('x', 0))
            y = int(request.form.get('y', 0))
            watermark_position = (x, y)
        else:
            watermark_position = (image.width - text_width - 10, image.height - text_height - 10)  # default to bottom-right

        # Adding the watermark
        image_editable.text(watermark_position, watermark_text, font=font, fill=(255, 255, 255, 128))

        # Save the image to a BytesIO object to send as a response
        img_io = BytesIO()
        image.save(img_io, 'PNG')
        img_io.seek(0)

        # Store the image in memory for previewing and provide the download link
        img_url = 'data:image/png;base64,' + base64.b64encode(img_io.getvalue()).decode('utf-8')

        return render_template('preview.html', img_url=img_url, watermark_text=watermark_text)
    else:
        return redirect(url_for('home'))

# Route to download the image
@app.route('/download', methods=['POST'])
def download():
    # Get the image data (base64) from the form
    img_data = request.form.get('image_data')
    img_data = base64.b64decode(img_data.split(',')[1])

    # Save the image to a BytesIO object
    img_io = BytesIO(img_data)
    img_io.seek(0)

    # Send the image as a response to the browser
    return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='watermarked_image.png')

# Route to delete the image (You can implement actual delete functionality as needed)
@app.route('/delete', methods=['POST'])
def delete():
    # Implement deletion if you're saving images on the server
    return jsonify({'message': 'Image deleted successfully'})


if __name__ == '__main__':
    app.run(debug=True)
