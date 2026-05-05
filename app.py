import os
import io
import datetime
from flask import Flask, request, jsonify, render_template, send_file
import sqlite3
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

# Ensure the generated_ids folder exists
os.makedirs('static/generated_ids', exist_ok=True)

# Database Connection
def get_db_connection():
    conn = sqlite3.connect('noid_db.sqlite')
    conn.row_factory = sqlite3.Row
    return conn

def generate_id_image(user_data):
    # user_data: (pid, name, department, year, program, dob)
    pid, name, department, year, program, dob = user_data
    
    # Create a blank white horizontal ID card (CR80 standard ratio)
    width, height = 1000, 630
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Try to load fonts
    try:
        font_header = ImageFont.truetype("arialbd.ttf", 40)
        font_sub = ImageFont.truetype("arial.ttf", 25)
        font_label = ImageFont.truetype("arialbd.ttf", 22)
        font_value = ImageFont.truetype("arial.ttf", 26)
        font_name = ImageFont.truetype("arialbd.ttf", 45)
    except IOError:
        font_header = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_label = ImageFont.load_default()
        font_value = ImageFont.load_default()
        font_name = ImageFont.load_default()

    # Draw Header (Navy Blue)
    draw.rectangle([(0, 0), (width, 120)], fill=(30, 58, 138))
    draw.text((30, 30), "GLOBAL TECH UNIVERSITY", fill=(255, 255, 255), font=font_header)
    draw.text((30, 80), "OFFICIAL STUDENT IDENTIFICATION", fill=(200, 215, 255), font=font_sub)
    
    # Draw Profile Picture Placeholder
    photo_x, photo_y = 50, 160
    photo_w, photo_h = 240, 300
    draw.rectangle([(photo_x, photo_y), (photo_x + photo_w, photo_y + photo_h)], fill=(226, 232, 240), outline=(148, 163, 184), width=3)
    
    # Draw a generic avatar icon inside photo placeholder
    draw.ellipse([(photo_x + 60, photo_y + 50), (photo_x + 180, photo_y + 170)], fill=(148, 163, 184))
    draw.ellipse([(photo_x + 20, photo_y + 190), (photo_x + 220, photo_y + 350)], fill=(148, 163, 184))

    # Details Area
    text_x = 340
    start_y = 160
    
    # Name is prominent
    draw.text((text_x, start_y), str(name).upper(), fill=(15, 23, 42), font=font_name)
    
    # Info Grid
    fields = [
        ("STUDENT ID", pid),
        ("DEPARTMENT", department),
        ("PROGRAM", program),
        ("YEAR", year),
        ("DATE OF BIRTH", str(dob))
    ]
    
    y_offset = start_y + 80
    for label, val in fields:
        draw.text((text_x, y_offset), f"{label}", fill=(100, 116, 139), font=font_label)
        draw.text((text_x, y_offset + 28), str(val), fill=(15, 23, 42), font=font_value)
        y_offset += 75
        
    # Draw fake barcode at the bottom
    barcode_y = 530
    draw.rectangle([(0, 500), (width, height)], fill=(241, 245, 249))
    draw.line([(0, 500), (width, 500)], fill=(203, 213, 225), width=2)
    
    for i in range(50, 950, 6):
        # random line thickness for barcode effect
        bw = (i * 17 % 5) + 1
        if i % 13 != 0: # create gaps
            draw.rectangle([(i, barcode_y), (i + bw, barcode_y + 60)], fill=(15, 23, 42))

    output_path = f'static/generated_ids/{pid}.png'
    img.save(output_path)
    return output_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/api/generate_id', methods=['POST'])
def generate_id():
    data = request.json
    pid = data.get('pid')
    
    if not pid:
        return jsonify({'error': 'PID is required'}), 400
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT * FROM users WHERE pid = ?", (pid,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'error': 'Invalid User'}), 404
            
        now = datetime.datetime.now()
        current_week = now.isocalendar()[1]
        
        # Check access log
        cursor.execute("SELECT * FROM access_log WHERE pid = ?", (pid,))
        log = cursor.fetchone()
        
        if log:
            # SQLite stores datetime as string, we need to parse it
            last_generated_str = log['last_generated_time']
            access_count = log['access_count']
            log_week = log['week_number']
            
            if last_generated_str:
                last_generated = datetime.datetime.fromisoformat(last_generated_str)
                time_diff = now - last_generated
                
                # Check 8-hour validity
                if time_diff.total_seconds() < 8 * 3600:
                    remaining_seconds = int((8 * 3600) - time_diff.total_seconds())
                    return jsonify({
                        'error': 'ID already valid, try after expiry',
                        'remaining_seconds': remaining_seconds,
                        'image_url': f'/static/generated_ids/{pid}.png' 
                    }), 403
            
            # Check weekly limit
            if log_week == current_week:
                if access_count >= 2:
                    return jsonify({'error': 'Limit reached, please pay fee'}), 403
                new_count = access_count + 1
            else:
                new_count = 1
                
            cursor.execute("""
                UPDATE access_log 
                SET access_count = ?, last_generated_time = ?, week_number = ?
                WHERE pid = ?
            """, (new_count, now.isoformat(), current_week, pid))
            
        else:
            # First time generating
            cursor.execute("""
                INSERT INTO access_log (pid, access_count, last_generated_time, week_number)
                VALUES (?, ?, ?, ?)
            """, (pid, 1, now.isoformat(), current_week))
            
        conn.commit()
        
        # Generate Image
        user_tuple = (user['pid'], user['name'], user['department'], user['year'], user['program'], user['dob'])
        image_path = generate_id_image(user_tuple)
        
        return jsonify({
            'message': 'ID Generated Successfully',
            'image_url': f'/{image_path}?t={int(now.timestamp())}'
        })
        
    except Exception as e:
        print(e)
        return jsonify({'error': 'An internal error occurred.'}), 500
    finally:
        conn.close()

@app.route('/api/add_user', methods=['POST'])
def add_user():
    data = request.json
    required_fields = ['pid', 'name', 'department', 'year', 'program', 'dob']
    
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
            
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO users (pid, name, department, year, program, dob)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (data['pid'], data['name'], data['department'], data['year'], data['program'], data['dob']))
        
        conn.commit()
        return jsonify({'message': 'User added successfully'})
    except sqlite3.IntegrityError:
        return jsonify({'error': 'PID already exists'}), 400
    except Exception as e:
        print(e)
        return jsonify({'error': 'Failed to add user'}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
