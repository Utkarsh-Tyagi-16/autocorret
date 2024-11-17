from flask import Flask, request, jsonify,render_template
import numpy as np
from autocorrect_package.autocorrection import Autocorrection

app = Flask(__name__)

# Initialize the Autocorrection object
checker = Autocorrection("autocorrect_package/corpus.txt")

def autocorrect_word(word):
    corrections = checker.correct_spelling(word.lower())
    if corrections:
        probs = np.array([c[1] for c in corrections])
        best_ix = np.argmax(probs)
        return corrections[best_ix][0]
    return word  # Return the original word if no corrections are found

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/autocorrect", methods=["POST"])
def autocorrect():
    data = request.get_json()
    word = data.get("word", "")
    corrected_word = autocorrect_word(word)
    return jsonify({"corrected": corrected_word})

if __name__ == "__main__":
    app.run(debug=True)