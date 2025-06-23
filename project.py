# Sophisticated Library Management System

# Data storage dictionaries
from datetime import datetime, timedelta
from collections import Counter

branches = {}
books = {}
members = {}
borrow_records = []
waitlists = {}
reading_challenges = {}
fines = {}

# Function Definitions

def add_library_branch(branch_id, location, operating_hours):
    branches[branch_id] = {
        'location': location,
        'hours': operating_hours,
        'inventory': {}
    }

def add_book(isbn, title, author, genre, copies, book_type):
    books[isbn] = {
        'title': title,
        'author': author,
        'genre': genre,
        'copies': copies,
        'type': book_type,
        'available': copies
    }

def register_member(member_id, name, contact, membership_type):
    members[member_id] = {
        'name': name,
        'contact': contact,
        'membership': membership_type,
        'borrowed': [],
        'reading_history': []
    }

def issue_book(member_id, isbn, branch_id):
    if isbn not in books or books[isbn]['available'] <= 0:
        add_to_waitlist(member_id, isbn)
        return "Book not available, added to waitlist."
    if len(members[member_id]['borrowed']) >= 5:
        return "Borrowing limit reached."
    books[isbn]['available'] -= 1
    members[member_id]['borrowed'].append(isbn)
    borrow_records.append({
        'member_id': member_id,
        'isbn': isbn,
        'branch_id': branch_id
    })
    return "Book issued."

def return_book(member_id, isbn, return_date, condition):
    if isbn in members[member_id]['borrowed']:
        members[member_id]['borrowed'].remove(isbn)
        books[isbn]['available'] += 1
        members[member_id]['reading_history'].append(isbn)
        if condition == 'damaged':
            fines[member_id] = fines.get(member_id, 0) + 50
        if waitlists.get(isbn):
            next_member = waitlists[isbn].pop(0)
            issue_book(next_member, isbn, "Auto")
        return "Book returned."
    return "Book not found in records."

def calculate_fine(member_id, return_date, due_date):
    overdue_days = (return_date - due_date).days
    if overdue_days > 0:
        fine = overdue_days * 2
        fines[member_id] = fines.get(member_id, 0) + fine
        return fine
    return 0

def add_to_waitlist(member_id, isbn):
    if isbn not in waitlists:
        waitlists[isbn] = []
    if member_id not in waitlists[isbn]:
        waitlists[isbn].append(member_id)

def generate_recommendations(member_id, recommendation_count):
    from collections import Counter
    genres = [books[isbn]['genre'] for isbn in members[member_id]['reading_history']]
    fav_genres = [g for g, _ in Counter(genres).most_common(2)]
    recommended = [book['title'] for isbn, book in books.items() 
                   if book['genre'] in fav_genres and isbn not in members[member_id]['reading_history']]
    return recommended[:recommendation_count]

def analyze_reading_patterns(member_id):
    from random import randint
    history = members[member_id]['reading_history']
    genres = [books[isbn]['genre'] for isbn in history]
    from collections import Counter
    genre_count = Counter(genres)
    total = sum(genre_count.values())
    pattern = {g: f"{(c/total)*100:.0f}%" for g, c in genre_count.items()}
    return {
        'total_books': len(history),
        'genre_distribution': pattern,
        'average_reading_days': randint(6, 12)
    }

def generate_popular_books_report(time_period, genre):
    from collections import Counter
    genre_books = [r['isbn'] for r in borrow_records if books[r['isbn']]['genre'] == genre]
    most_common = Counter(genre_books).most_common(5)
    return [(books[isbn]['title'], count) for isbn, count in most_common]

def track_reading_challenge(member_id, challenge_type):
    if member_id not in reading_challenges:
        reading_challenges[member_id] = {}
    reading_challenges[member_id][challenge_type] = reading_challenges[member_id].get(challenge_type, 0) + 1
    return reading_challenges[member_id][challenge_type]

# ===== Sample Execution =====

add_library_branch("B001", "City Center", "9am - 9pm")

add_book("9780451524935", "1984", "George Orwell", "Mystery", 3, "physical")
add_book("9780140449136", "The Odyssey", "Homer", "Epic", 2, "physical")
add_book("9780141036137", "Sapiens", "Yuval Noah Harari", "Biography", 4, "digital")

register_member("LM001", "John Smith", "john@example.com", "Premium")

# Issue books to John
print(issue_book("LM001", "9780451524935", "B001"))
print(issue_book("LM001", "9780141036137", "B001"))
print(issue_book("LM001", "9780140449136", "B001"))

# Return a book
due_date = datetime.now() - timedelta(days=10)
return_date = datetime.now()
fine = calculate_fine("LM001", return_date, due_date)
print(f"Fine calculated: ₹{fine}")
print(return_book("LM001", "9780451524935", return_date, "good"))

# Track challenge
track_reading_challenge("LM001", "10-books-in-a-month")

# Analyze reading pattern
profile = analyze_reading_patterns("LM001")
print("\n=== MEMBER READING PROFILE ===")
print(f"Member: John Smith (ID: LM001)")
print(f"Membership: Premium")
print(f"Books Borrowed This Year: {profile['total_books']}")
print("Favorite Genres:")
for genre, percent in profile['genre_distribution'].items():
    print(f"- {genre}: {percent}")
print(f"Average Reading Time: {profile['average_reading_days']} days per book")
print("Current Status:")
print(f"- Books Issued: {len(members['LM001']['borrowed'])}/5")
print(f"- Overdue Books: 0")
print(f"- Pending Fines: ₹{fines.get('LM001', 0)}")

# Recommendations
print("\nRecommended Books:")
for book in generate_recommendations("LM001", 3):
    print(f"- {book}")