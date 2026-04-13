from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.models import get_issues_for_board


def find_similar_issues(new_title, new_description, board_id, threshold=0.3):
    existing_issues = get_issues_for_board(board_id)

    if not existing_issues:
        return []

    # Combine title and description for each existing issue
    existing_texts = []
    for issue in existing_issues:
        text = issue['title']
        if issue['description']:
            text += ' ' + issue['description']
        existing_texts.append(text)

    # Combine title and description for the new issue
    new_text = new_title
    if new_description:
        new_text += ' ' + new_description

    # All texts: existing issues + the new issue (last one)
    all_texts = existing_texts + [new_text]

    # Vectorize using TF-IDF
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(all_texts)

    # Compare the new issue (last vector) against all existing ones
    new_vector = tfidf_matrix[-1]
    existing_vectors = tfidf_matrix[:-1]
    similarities = cosine_similarity(new_vector, existing_vectors)[0]

    # Return issues above the threshold, sorted by similarity
    similar = []
    for i, score in enumerate(similarities):
        if score >= threshold:
            similar.append({
                'id': existing_issues[i]['id'],
                'title': existing_issues[i]['title'],
                'description': existing_issues[i]['description'],
                'member_count': existing_issues[i]['member_count'],
                'score': round(score * 100, 1)
            })

    similar.sort(key=lambda x: x['score'], reverse=True)
    return similar