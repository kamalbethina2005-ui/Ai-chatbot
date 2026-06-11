from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# Absolute path for the database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'medical_chatbot.db')

# ─────────────────────────────────────────────────────────────
# PREDEFINED RESPONSES FOR COMMON HEALTH CONDITIONS
# ─────────────────────────────────────────────────────────────
HEALTH_RESPONSES = {
    "diabetes": {
        "description": "Diabetes is a chronic condition where the body cannot properly process blood sugar (glucose). Type 1 is autoimmune; Type 2 is often lifestyle-related.",
        "symptoms": ["Frequent urination", "Excessive thirst", "Unexplained weight loss", "Blurred vision", "Fatigue", "Slow-healing wounds"],
        "foods_good": ["Leafy greens (spinach, kale)", "Whole grains (oats, brown rice)", "Fatty fish (salmon, mackerel)", "Nuts and seeds", "Berries (blueberries, strawberries)", "Beans and lentils", "Sweet potatoes", "Greek yogurt"],
        "foods_avoid": ["Sugary drinks & sodas", "White bread & refined carbs", "Fried foods", "Candy & sweets", "Fruit juices with added sugar"],
        "tips": "Monitor blood sugar regularly. Exercise at least 30 minutes daily. Stay hydrated with water. Eat meals at consistent times."
    },
    "hypertension": {
        "description": "Hypertension (high blood pressure) is when blood pressure is consistently too high, increasing the risk of heart disease and stroke.",
        "symptoms": ["Headaches", "Shortness of breath", "Nosebleeds", "Dizziness", "Chest pain", "Visual changes"],
        "foods_good": ["Bananas (rich in potassium)", "Spinach & leafy greens", "Oats & whole grains", "Garlic", "Berries", "Beets", "Low-fat dairy (yogurt, milk)", "Fatty fish (salmon)"],
        "foods_avoid": ["Excess salt & salty snacks", "Processed & canned foods", "Red meat in excess", "Alcohol", "Caffeine in excess"],
        "tips": "Reduce sodium intake to less than 2,300 mg/day. Exercise regularly. Manage stress through meditation or yoga. Monitor BP at home."
    },
    "asthma": {
        "description": "Asthma is a chronic respiratory condition where airways become inflamed and narrowed, causing difficulty breathing.",
        "symptoms": ["Wheezing", "Shortness of breath", "Chest tightness", "Coughing (especially at night)", "Difficulty sleeping due to breathing"],
        "foods_good": ["Fruits rich in Vitamin C (oranges, strawberries)", "Ginger", "Turmeric", "Tomatoes", "Leafy greens", "Apples", "Honey (in moderation)"],
        "foods_avoid": ["Sulfite-containing foods (wine, dried fruits)", "Processed foods with preservatives", "Dairy (if it triggers symptoms)", "Fried & greasy foods"],
        "tips": "Always carry your inhaler. Avoid known triggers (dust, pollen, smoke). Keep your living space clean. Practice breathing exercises."
    },
    "cold": {
        "description": "The common cold is a viral infection of the upper respiratory tract. It is usually harmless and resolves within 7-10 days.",
        "symptoms": ["Runny or stuffy nose", "Sore throat", "Sneezing", "Mild body aches", "Low-grade fever", "Cough"],
        "foods_good": ["Chicken soup", "Warm water with honey & lemon", "Ginger tea", "Citrus fruits (oranges, lemons)", "Garlic", "Turmeric milk", "Hot herbal teas"],
        "foods_avoid": ["Dairy products (may increase mucus)", "Sugary foods", "Fried foods", "Alcohol", "Cold beverages"],
        "tips": "Rest well. Drink plenty of warm fluids. Gargle with salt water for sore throat. Use steam inhalation for congestion."
    },
    "fever": {
        "description": "Fever is a temporary rise in body temperature, usually caused by an infection. A temperature above 100.4°F (38°C) is considered a fever.",
        "symptoms": ["Elevated body temperature", "Sweating", "Chills and shivering", "Headache", "Muscle aches", "Loss of appetite", "Dehydration"],
        "foods_good": ["Light soups and broths", "Coconut water", "Fresh fruit juices", "Rice porridge (congee)", "Bananas", "Boiled vegetables", "Toast or crackers"],
        "foods_avoid": ["Spicy foods", "Heavy or greasy meals", "Caffeine", "Alcohol", "Sugary snacks"],
        "tips": "Stay hydrated. Rest as much as possible. Use a cool compress on your forehead. Take paracetamol if needed. See a doctor if fever persists beyond 3 days."
    },
    "headache": {
        "description": "Headaches can range from mild tension-type to severe migraines. They may be caused by stress, dehydration, poor sleep, or underlying conditions.",
        "symptoms": ["Throbbing or constant pain", "Pressure around forehead or temples", "Sensitivity to light or sound", "Nausea (for migraines)", "Neck stiffness"],
        "foods_good": ["Water (dehydration is a top cause)", "Magnesium-rich foods (almonds, spinach)", "Ginger tea", "Watermelon", "Bananas", "Dark chocolate (in moderation)", "Coffee (small amounts)"],
        "foods_avoid": ["Aged cheeses", "Processed meats", "Alcohol (especially red wine)", "Artificial sweeteners", "MSG-containing foods"],
        "tips": "Stay hydrated. Take breaks from screens. Get adequate sleep (7-8 hours). Practice relaxation techniques. Try a cold or warm compress."
    },
    "stomach ache": {
        "description": "Stomach aches can result from indigestion, gas, food intolerance, infections, or stress. Most cases are not serious and resolve on their own.",
        "symptoms": ["Abdominal pain or cramping", "Bloating", "Nausea", "Gas", "Diarrhea or constipation", "Loss of appetite"],
        "foods_good": ["Plain rice", "Bananas", "Toast", "Applesauce", "Ginger tea", "Yogurt with probiotics", "Chamomile tea", "Boiled potatoes"],
        "foods_avoid": ["Spicy foods", "Fried or fatty foods", "Dairy (if lactose intolerant)", "Carbonated drinks", "Acidic foods (tomatoes, citrus)"],
        "tips": "Eat small, frequent meals. Avoid eating too fast. Stay upright after meals. Try a warm compress on your abdomen. See a doctor if pain is severe or persistent."
    },
    "acidity": {
        "description": "Acidity (acid reflux) occurs when stomach acid flows back into the esophagus, causing a burning sensation in the chest (heartburn).",
        "symptoms": ["Heartburn (burning in chest)", "Sour taste in mouth", "Bloating", "Burping", "Nausea", "Difficulty swallowing"],
        "foods_good": ["Bananas", "Oatmeal", "Green vegetables (broccoli, beans)", "Ginger", "Melon", "Rice", "Almonds", "Cold milk"],
        "foods_avoid": ["Spicy foods", "Citrus fruits", "Tomatoes", "Coffee & tea", "Chocolate", "Carbonated drinks", "Onions & garlic", "Fried foods"],
        "tips": "Don't lie down right after eating. Eat dinner at least 2-3 hours before bed. Elevate your head while sleeping. Eat smaller portions."
    },
    "anxiety": {
        "description": "Anxiety is a feeling of worry, nervousness, or unease. While occasional anxiety is normal, persistent anxiety may indicate an anxiety disorder.",
        "symptoms": ["Restlessness", "Rapid heartbeat", "Difficulty concentrating", "Excessive worry", "Sleep problems", "Muscle tension", "Irritability"],
        "foods_good": ["Dark chocolate", "Chamomile tea", "Fatty fish (omega-3s)", "Turmeric", "Yogurt (probiotics)", "Green tea", "Almonds & walnuts", "Bananas"],
        "foods_avoid": ["Caffeine (coffee, energy drinks)", "Alcohol", "Sugary foods", "Processed foods", "Excess sodium"],
        "tips": "Practice deep breathing exercises. Try meditation or yoga. Exercise regularly. Maintain a consistent sleep schedule. Talk to someone you trust or a professional."
    },
    "back pain": {
        "description": "Back pain is one of the most common health complaints. It can result from poor posture, muscle strain, injury, or underlying spinal conditions.",
        "symptoms": ["Dull aching pain in the back", "Stiffness", "Sharp or shooting pain", "Pain radiating down the leg (sciatica)", "Difficulty standing straight"],
        "foods_good": ["Anti-inflammatory foods (turmeric, ginger)", "Fatty fish (salmon, sardines)", "Leafy greens", "Berries", "Olive oil", "Nuts", "Calcium-rich foods (milk, yogurt)"],
        "foods_avoid": ["Sugary foods (increase inflammation)", "Processed foods", "Excess red meat", "Alcohol", "Fried foods"],
        "tips": "Maintain good posture. Use ergonomic furniture. Stretch regularly. Apply heat or ice to the affected area. Strengthen your core muscles."
    },
    "cough": {
        "description": "A cough is a reflex to clear the airways. It can be dry or productive (with mucus) and may result from colds, allergies, or infections.",
        "symptoms": ["Persistent coughing", "Sore throat", "Chest discomfort", "Phlegm or mucus", "Wheezing", "Runny nose"],
        "foods_good": ["Warm honey water", "Ginger tea", "Turmeric milk (golden milk)", "Chicken soup", "Pineapple (contains bromelain)", "Warm lemon water", "Thyme tea"],
        "foods_avoid": ["Cold drinks", "Ice cream", "Fried foods", "Dairy (if increasing mucus)", "Histamine-rich foods"],
        "tips": "Stay hydrated with warm fluids. Use a humidifier. Gargle with warm salt water. Honey is excellent for soothing coughs. See a doctor if cough persists over 2 weeks."
    },
    "flu": {
        "description": "Influenza (flu) is a contagious respiratory illness caused by influenza viruses. It is more severe than the common cold.",
        "symptoms": ["High fever", "Body aches", "Fatigue", "Chills", "Headache", "Sore throat", "Dry cough", "Congestion"],
        "foods_good": ["Chicken soup", "Warm broths", "Citrus fruits", "Garlic", "Ginger tea", "Yogurt", "Oatmeal", "Coconut water"],
        "foods_avoid": ["Processed foods", "Sugary drinks", "Fried foods", "Alcohol", "Heavy meals"],
        "tips": "Rest is crucial. Drink lots of warm fluids. Take fever-reducing medication if needed. Wash hands frequently. Get a flu vaccine annually."
    },
    "migraine": {
        "description": "Migraines are intense, throbbing headaches often accompanied by nausea, vomiting, and extreme sensitivity to light and sound.",
        "symptoms": ["Severe throbbing headache (often one-sided)", "Nausea and vomiting", "Light sensitivity", "Sound sensitivity", "Visual disturbances (aura)", "Dizziness"],
        "foods_good": ["Magnesium-rich foods (spinach, pumpkin seeds)", "Riboflavin foods (eggs, nuts)", "Ginger", "Water (stay hydrated)", "Whole grains", "Leafy greens"],
        "foods_avoid": ["Aged cheese", "Red wine", "Chocolate", "Processed meats (nitrates)", "MSG", "Artificial sweeteners", "Strong coffee"],
        "tips": "Identify and avoid your triggers. Keep a headache diary. Rest in a dark, quiet room during episodes. Apply cold compress to forehead. Stay on a regular sleep schedule."
    },
    "constipation": {
        "description": "Constipation is a condition where bowel movements are infrequent or difficult. It is usually caused by low fiber intake, dehydration, or lack of exercise.",
        "symptoms": ["Fewer than 3 bowel movements per week", "Hard or lumpy stools", "Straining", "Feeling of incomplete evacuation", "Bloating", "Abdominal discomfort"],
        "foods_good": ["High-fiber foods (whole grains, bran)", "Prunes and dried fruits", "Leafy greens", "Apples and pears", "Beans and lentils", "Flaxseeds", "Plenty of water"],
        "foods_avoid": ["Processed foods", "White bread & refined flour", "Dairy in excess", "Red meat", "Fried foods", "Unripe bananas"],
        "tips": "Drink at least 8 glasses of water daily. Exercise regularly. Don't ignore the urge to go. Eat meals at regular times. Consider a fiber supplement if needed."
    },
    "allergy": {
        "description": "Allergies occur when the immune system reacts to a harmless substance (allergen) like pollen, dust, certain foods, or pet dander.",
        "symptoms": ["Sneezing", "Runny or itchy nose", "Watery eyes", "Skin rash or hives", "Swelling", "Itching", "Coughing"],
        "foods_good": ["Local honey (may help with pollen)", "Vitamin C-rich fruits", "Turmeric", "Ginger", "Garlic", "Green tea", "Probiotic-rich yogurt"],
        "foods_avoid": ["Known allergen foods", "Processed foods with additives", "Alcohol (may worsen symptoms)", "Histamine-rich foods (aged cheese, fermented foods)"],
        "tips": "Identify and avoid your specific allergens. Keep windows closed during high pollen days. Shower after being outdoors. Use air purifiers. Take antihistamines as needed."
    },
    "skin rash": {
        "description": "Skin rashes can be caused by allergies, infections, heat, or skin conditions like eczema or dermatitis. Most are not serious but can be uncomfortable.",
        "symptoms": ["Redness", "Itching", "Bumps or blisters", "Dry or scaly skin", "Swelling", "Burning sensation"],
        "foods_good": ["Omega-3 rich fish", "Fruits & vegetables (antioxidants)", "Turmeric", "Green tea", "Probiotic yogurt", "Avocados", "Sweet potatoes"],
        "foods_avoid": ["Processed foods", "Excess dairy", "Gluten (if sensitive)", "Spicy foods", "Artificial additives", "Excess sugar"],
        "tips": "Keep the affected area clean and dry. Avoid scratching. Use gentle, fragrance-free soap. Apply aloe vera or calamine lotion. See a dermatologist if it persists."
    },
    "insomnia": {
        "description": "Insomnia is difficulty falling asleep, staying asleep, or getting quality sleep. It can be caused by stress, poor habits, or medical conditions.",
        "symptoms": ["Difficulty falling asleep", "Waking up during the night", "Waking up too early", "Daytime fatigue", "Irritability", "Difficulty concentrating"],
        "foods_good": ["Warm milk", "Chamomile tea", "Almonds & walnuts", "Kiwi", "Tart cherries", "Bananas", "Oatmeal", "Fatty fish"],
        "foods_avoid": ["Caffeine (after 2 PM)", "Alcohol", "Heavy meals before bed", "Spicy foods at night", "Sugary snacks", "Excess water before bed"],
        "tips": "Maintain a consistent sleep schedule. Create a dark, cool sleep environment. Avoid screens 1 hour before bed. Practice relaxation techniques. Limit naps to 20 minutes."
    },
    "dehydration": {
        "description": "Dehydration occurs when the body loses more fluids than it takes in. It can range from mild to severe and requires prompt attention.",
        "symptoms": ["Extreme thirst", "Dark yellow urine", "Dry mouth and lips", "Fatigue", "Dizziness", "Headache", "Reduced urination"],
        "foods_good": ["Water (obviously!)", "Coconut water", "Watermelon", "Cucumber", "Oranges", "ORS (Oral Rehydration Solution)", "Buttermilk", "Soups"],
        "foods_avoid": ["Caffeine", "Alcohol", "Very salty foods", "Sugary drinks", "Protein-heavy meals (require more water to digest)"],
        "tips": "Drink water regularly, don't wait until you're thirsty. Carry a water bottle. Eat water-rich fruits. In hot weather, increase fluid intake. Seek medical help for severe dehydration."
    },
    "obesity": {
        "description": "Obesity is a condition involving excessive body fat that increases health risks. It is typically caused by a combination of overeating, sedentary lifestyle, and genetics.",
        "symptoms": ["BMI over 30", "Excess body fat", "Shortness of breath", "Joint pain", "Fatigue", "Excessive sweating", "Snoring or sleep apnea"],
        "foods_good": ["Vegetables (broccoli, spinach, carrots)", "Lean proteins (chicken, fish, tofu)", "Whole grains", "Fruits in moderation", "Nuts (small portions)", "Beans & lentils", "Green tea"],
        "foods_avoid": ["Sugary drinks & sodas", "Fast food", "Processed snacks", "White bread & pasta", "Fried foods", "Excess desserts", "Large portion sizes"],
        "tips": "Focus on portion control. Exercise at least 150 minutes per week. Eat slowly and mindfully. Keep a food journal. Get adequate sleep. Consult a nutritionist."
    },
    "sore throat": {
        "description": "A sore throat is pain, scratchiness, or irritation of the throat, often caused by viral infections, bacterial infections, or dry air.",
        "symptoms": ["Pain or scratchiness in the throat", "Difficulty swallowing", "Swollen glands", "Hoarse voice", "Red or swollen tonsils"],
        "foods_good": ["Warm honey water", "Ginger tea", "Chicken soup", "Ice chips or popsicles", "Soft foods (mashed potatoes, yogurt)", "Warm lemon water", "Chamomile tea"],
        "foods_avoid": ["Spicy foods", "Acidic foods (citrus, tomatoes)", "Crunchy or hard foods", "Very hot beverages", "Alcohol"],
        "tips": "Gargle with warm salt water. Stay hydrated. Use throat lozenges. Rest your voice. Use a humidifier. See a doctor if it lasts more than a week."
    }
}

# Keywords mapping to conditions (for flexible matching)
KEYWORD_MAP = {
    "sugar": "diabetes", "blood sugar": "diabetes", "diabetic": "diabetes", "type 1": "diabetes", "type 2": "diabetes", "insulin": "diabetes",
    "bp": "hypertension", "blood pressure": "hypertension", "high bp": "hypertension", "high blood pressure": "hypertension",
    "breathing": "asthma", "asthmatic": "asthma", "inhaler": "asthma", "wheeze": "asthma",
    "cold": "cold", "runny nose": "cold", "stuffy nose": "cold", "sneezing": "cold",
    "fever": "fever", "temperature": "fever", "chills": "fever",
    "headache": "headache", "head pain": "headache", "head ache": "headache",
    "stomach": "stomach ache", "stomach ache": "stomach ache", "stomach pain": "stomach ache", "tummy": "stomach ache", "abdominal pain": "stomach ache", "belly pain": "stomach ache",
    "acidity": "acidity", "acid reflux": "acidity", "heartburn": "acidity", "gas": "acidity", "bloating": "acidity",
    "anxiety": "anxiety", "anxious": "anxiety", "worry": "anxiety", "nervous": "anxiety", "panic": "anxiety", "stress": "anxiety",
    "back pain": "back pain", "backache": "back pain", "back ache": "back pain", "spine": "back pain", "sciatica": "back pain",
    "cough": "cough", "coughing": "cough", "dry cough": "cough", "wet cough": "cough",
    "flu": "flu", "influenza": "flu",
    "migraine": "migraine",
    "constipation": "constipation", "constipated": "constipation",
    "allergy": "allergy", "allergic": "allergy", "allergies": "allergy", "pollen": "allergy", "hives": "allergy",
    "rash": "skin rash", "skin rash": "skin rash", "eczema": "skin rash", "dermatitis": "skin rash", "itching": "skin rash", "itchy skin": "skin rash",
    "insomnia": "insomnia", "sleep": "insomnia", "can't sleep": "insomnia", "sleepless": "insomnia",
    "dehydration": "dehydration", "dehydrated": "dehydration", "thirsty": "dehydration",
    "obesity": "obesity", "overweight": "obesity", "weight loss": "obesity", "fat": "obesity",
    "sore throat": "sore throat", "throat pain": "sore throat", "throat": "sore throat",
}


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_doctors_by_disease(disease):
    conn = get_db_connection()
    cur = conn.cursor()
    query = """
        SELECT name, specialty, contact 
        FROM doctors 
        WHERE LOWER(disease_tag) LIKE ?
    """
    cur.execute(query, ('%' + disease.lower() + '%',))
    doctors = cur.fetchall()
    conn.close()
    return doctors


def match_condition(user_input):
    """Match user input to a known health condition using keyword mapping."""
    text = user_input.lower().strip()

    # Direct match first
    if text in HEALTH_RESPONSES:
        return text

    # Try keyword mapping (longest match first to avoid partial matches)
    sorted_keywords = sorted(KEYWORD_MAP.keys(), key=len, reverse=True)
    for keyword in sorted_keywords:
        if keyword in text:
            return KEYWORD_MAP[keyword]

    return None


def build_response(condition_key, user_input):
    """Build a formatted HTML response for the matched condition."""
    data = HEALTH_RESPONSES[condition_key]

    symptoms_list = "".join(f"<li>{s}</li>" for s in data["symptoms"])
    good_foods = "".join(f"<li>✅ {f}</li>" for f in data["foods_good"])
    avoid_foods = "".join(f"<li>❌ {f}</li>" for f in data["foods_avoid"])

    html = f"""
    <p><strong>🔍 {condition_key.title()}</strong></p>
    <p>{data['description']}</p>
    <p><strong>📋 Common Symptoms:</strong></p>
    <ul>{symptoms_list}</ul>
    <p><strong>🥗 Recommended Foods:</strong></p>
    <ul>{good_foods}</ul>
    <p><strong>🚫 Foods to Avoid:</strong></p>
    <ul>{avoid_foods}</ul>
    <p><strong>💡 Tips:</strong> {data['tips']}</p>
    """
    return html.strip()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.form.get('message', '').strip()
    if not user_input:
        return jsonify({'response': '<p>Please enter a message.</p>'})

    # Greetings
    greetings = ["hi", "hello", "hey", "good morning", "good evening", "good afternoon"]
    if user_input.lower() in greetings:
        return jsonify({'response': '<p>Hello! 👋 I\'m your Medical Assistant. Tell me your health concern (e.g., <em>diabetes</em>, <em>headache</em>, <em>cold</em>) and I\'ll provide helpful information including food suggestions and tips!</p>'})

    # Help / list conditions
    if user_input.lower() in ["help", "list", "what can you do", "conditions", "diseases"]:
        conditions = sorted(HEALTH_RESPONSES.keys())
        items = "".join(f"<li>{c.title()}</li>" for c in conditions)
        return jsonify({'response': f'<p><strong>I can help with these conditions:</strong></p><ul>{items}</ul><p>Just type the name of a condition!</p>'})

    # Match condition
    condition = match_condition(user_input)

    if condition:
        response_html = build_response(condition, user_input)

        # Check for doctors in DB
        doctors = get_doctors_by_disease(condition)
        if doctors:
            doc_html = "<br><strong>👨‍⚕️ Recommended Specialists:</strong><ul>"
            for doc in doctors:
                doc_html += f"<li><strong>{doc['name']}</strong> ({doc['specialty']}) — Contact: {doc['contact']}</li>"
            doc_html += "</ul>"
            response_html += doc_html

        # Log to database
        try:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO conversations (user_id, user_message, bot_response) VALUES (?, ?, ?)",
                (1, user_input, response_html)
            )
            conn.commit()
            conn.close()
        except Exception:
            pass

        return jsonify({'response': response_html})
    else:
        return jsonify({'response': '<p>I\'m sorry, I didn\'t recognize that condition. 😕</p><p>Try typing a common health issue like <strong>diabetes</strong>, <strong>headache</strong>, <strong>cold</strong>, <strong>fever</strong>, <strong>acidity</strong>, or type <strong>help</strong> to see all conditions I can assist with.</p>'})


@app.route('/doctors')
def doctors():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT name, specialty, contact FROM doctors")
    doctors = cur.fetchall()
    conn.close()

    doctors_list = [dict(doc) for doc in doctors]
    return jsonify({'doctors': doctors_list})


if __name__ == '__main__':
    app.run(debug=True)