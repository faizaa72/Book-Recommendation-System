from flask import Flask, render_template,request
import pickle
import numpy as np
app = Flask(__name__)

popular_df = pickle.load(open('popular.pkl', 'rb'))
books=pickle.load(open('books.pkl', 'rb'))
pt=pickle.load(open('pt.pkl', 'rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl', 'rb'))

@app.route('/')
def index():
    book_name = list(popular_df['Book-Title'].values)
    author = list(popular_df['Book-Author'].values)
    image = list(popular_df['Image-URL-M'].values)
    votes = [f"{float(v):.1f}" for v in popular_df['num_rating'].values]
    rating = [f"{float(r):.1f}" for r in popular_df['avg_rating'].values]

    return render_template(
        'index.html',
        book_name=book_name,
        author=author,
        image=image,
        votes=votes,
        rating=rating
    )
@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')


@app.route('/recommend_books', methods=['GET','POST'])
def recommend():
    user_input = request.form.get('user_input').strip()

    # 🔍 Case-insensitive + partial matching
    matches = [book for book in pt.index if user_input.lower() in book.lower()]

    if len(matches) == 0:
        return render_template('recommend.html', error="Book not found. Try another name.")

    # Take best match
    matched_book = matches[0]

    index = np.where(pt.index == matched_book)[0][0]
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:6]

    data = []

    for i in similar_items:
        item = []

        temp_df = books[books['Book-Title'] == pt.index[i[0]]]

        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))

        data.append(item)

    return render_template('recommend.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)