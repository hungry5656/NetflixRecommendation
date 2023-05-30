from flask import Flask, request, render_template
import pickle

app = Flask(__name__)
model = pickle.load(open('model.pkl', 'rb'))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend',methods=['POST'])
def recommend():
    """Grabs the input values and uses them to make recommendation"""
    user_id = int(request.form["userID"])
    recommendations = model.predict(user_id)  
    
    return render_template('index.html', recommendation_text=f'Recommendations for user {user_id}: {recommendations}')

if __name__ == "__main__":
    app.run()
