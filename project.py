import datetime
from collections import Counter
import random

# ------------------- Data Models -------------------

class Book:
    def __init__(self, isbn, title, author, genre, copies, book_type):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.genre = genre
        self.copies = copies
        self.book_type = book_type
        self.waitlist = []  # member ID queue
        self.total_copies = copies  # for bulk acquisition tracking

class Member:
    def __init__(self, member_id, name, contact, membership_type):
        self.member_id = member_id
        self.name = name
        self.contact = contact
        self.membership_type = membership_type
        self.membership_expiry = datetime.date.today() + datetime.timedelta(days=365)
        self.borrowed_books = {}
        self.history = []
        self.reading_times = []
        self.fines = 0
        self.challenge_progress = 0
        self.privacy_consent = True  # GDPR compliance opt-in

class Branch:
    def __init__(self, branch_id, location, operating_hours):
        self.branch_id = branch_id
        self.location = location
        self.operating_hours = operating_hours
        self.books = {}

# ------------------- Main System -------------------

class LibrarySystem:
    def __init__(self):
        self.branches = {}
        self.books = {}
        self.members = {}
        self.system_status = "online"  # simulate downtime

    def add_library_branch(self, branch_id, location, operating_hours):
        self.branches[branch_id] = Branch(branch_id, location, operating_hours)

    def add_book(self, isbn, title, author, genre, copies, book_type):
        if isbn not in self.books:
            self.books[isbn] = Book(isbn, title, author, genre, copies, book_type)
        else:
            self.books[isbn].copies += copies
            self.books[isbn].total_copies += copies

    def register_member(self, member_id, name, contact, membership_type):
        self.members[member_id] = Member(member_id, name, contact, membership_type)

    def issue_book(self, member_id, isbn, branch_id):
        if self.system_status != "online":
            print("System is currently down. Please try again later.")
            return

        member = self.members[member_id]
        book = self.books.get(isbn)

        if not member.privacy_consent:
            print("Cannot proceed. Member has not consented to data use.")
            return

        if datetime.date.today() > member.membership_expiry:
            print("Membership expired. Please renew to borrow books.")
            return

        if any(due < datetime.date.today() for due in member.borrowed_books.values()):
            print("You have overdue books. Return them before borrowing more.")
            return

        if len(member.borrowed_books) >= 5:
            print("You have reached the limit of 5 active books.")
            return

        if book.copies == 0:
            print(f"No copies of '{book.title}' available. Adding to waitlist.")
            self.add_to_waitlist(member_id, isbn)
            return

        if member_id in book.waitlist and book.waitlist[0] != member_id:
            print("You must wait your turn in the reservation queue.")
            return

        book.copies -= 1
        due_date = datetime.date.today() + datetime.timedelta(days=14)
        member.borrowed_books[isbn] = due_date
        print(f"Book '{book.title}' issued to {member.name}. Due: {due_date}")

    def return_book(self, member_id, isbn, return_date, condition):
        member = self.members[member_id]
        book = self.books[isbn]
        due_date = member.borrowed_books.pop(isbn, None)

        if due_date:
            borrow_date = due_date - datetime.timedelta(days=14)
            reading_time = (return_date - borrow_date).days
            member.reading_times.append(reading_time)
            member.history.append(book)
            member.challenge_progress += 1

            if return_date > due_date:
                late_days = (return_date - due_date).days
                member.fines += late_days * 5

            if condition == "damaged":
                member.fines += 100
                print("Book returned damaged. ₹100 fine applied.")
            elif condition == "lost":
                member.fines += 500
                print("Book marked as lost. ₹500 fine applied.")
            else:
                book.copies += 1

            self.handle_waitlist(book, isbn)
            print(f"Book '{book.title}' returned successfully by {member.name}.")

    def handle_waitlist(self, book, isbn):
        while book.waitlist and book.copies > 0:
            next_member = book.waitlist.pop(0)
            print(f"Book '{book.title}' now available for member {next_member}. Auto-issuing...")
            self.issue_book(next_member, isbn, "auto")

    def calculate_fine(self, member_id, return_date, due_date):
        delta = (return_date - due_date).days
        return max(0, delta * 5)

    def add_to_waitlist(self, member_id, isbn):
        if member_id not in self.books[isbn].waitlist:
            self.books[isbn].waitlist.append(member_id)

    def generate_recommendations(self, member_id, recommendation_count):
        member = self.members[member_id]
        genre_count = Counter(book.genre for book in member.history)
        top_genres = [genre for genre, _ in genre_count.most_common(2)]

        recommendations = []
        for book in self.books.values():
            if book.genre in top_genres and book not in member.history:
                recommendations.append(book)
                if len(recommendations) >= recommendation_count:
                    break
        return recommendations

    def analyze_reading_patterns(self, member_id):
        member = self.members[member_id]
        genre_count = Counter(book.genre for book in member.history)
        total = sum(genre_count.values())
        genre_percent = {genre: round((count / total) * 100) for genre, count in genre_count.items()} if total else {}
        avg_time = round(sum(member.reading_times) / len(member.reading_times), 1) if member.reading_times else 0
        return genre_percent, avg_time

    def generate_popular_books_report(self, time_period, genre):
        genre_books = [book for book in self.books.values() if book.genre == genre]
        return random.sample(genre_books, min(3, len(genre_books)))

    def track_reading_challenge(self, member_id, challenge_type):
        return self.members[member_id].challenge_progress

    def display_member_profile(self, member_id):
        member = self.members[member_id]
        genre_percent, avg_time = self.analyze_reading_patterns(member_id)
        recommendations = self.generate_recommendations(member_id, 3)

        print("\n=== MEMBER READING PROFILE ===")
        print(f"Member: {member.name} (ID: {member.member_id})")
        print(f"Membership: {member.membership_type}")
        print(f"Books Borrowed This Year: {len(member.history)}")
        print("Favorite Genres:", ', '.join(f"{g} ({p}%)" for g, p in genre_percent.items()) if genre_percent else "N/A")
        print(f"Average Reading Time: {avg_time} days per book\n")

        print("Current Status:")
        print(f"- Books Issued: {len(member.borrowed_books)}/5")
        overdue = sum(1 for d in member.borrowed_books.values() if d < datetime.date.today())
        print(f"- Overdue Books: {overdue}")
        print(f"- Pending Fines: ₹{member.fines}\n")

        progress = member.challenge_progress
        print("Reading Challenge Progress:")
        print(f"\"50 Books Challenge 2025\": {progress}/50 ({int(progress / 50 * 100)}% complete)\n")

        print("=== RECOMMENDATIONS FOR YOU ===")
        for i, book in enumerate(recommendations, 1):
            print(f"{i}. \"{book.title}\" by {book.author} ({book.genre})")

        print("\nTrending in your preferred genres:")
        if genre_percent:
            trending = self.generate_popular_books_report("monthly", list(genre_percent.keys())[0])
            for i, book in enumerate(trending, 1):
                print(f"{i}. \"{book.title}\" - {random.randint(70, 95)}% match")
        else:
            print("Not enough data yet.")

# ------------------- Test Run -------------------

if __name__ == "__main__":
    lib = LibrarySystem()

    # Add a branch
    lib.add_library_branch("BR001", "Mumbai", "9am–9pm")

    # Add books
    lib.add_book("111", "The Silent Patient", "Alex Michaelides", "Mystery", 2, "physical")
    lib.add_book("112", "Project Hail Mary", "Andy Weir", "Science Fiction", 2, "digital")
    lib.add_book("113", "Educated", "Tara Westover", "Biography", 2, "physical")
    lib.add_book("114", "Gone Girl", "Gillian Flynn", "Mystery", 2, "physical")
    lib.add_book("115", "Dune", "Frank Herbert", "Science Fiction", 2, "physical")

    # Register members
    lib.register_member("LM001", "John Smith", "9876543210", "Premium")
    lib.register_member("LM002", "Jennifer Winget", "9246892882", "Standard")

    # Borrow & return books
    lib.issue_book("LM001", "111", "BR001")
    lib.return_book("LM001", "111", datetime.date.today(), "good")

    lib.issue_book("LM001", "112", "BR001")
    lib.return_book("LM001", "112", datetime.date.today(), "damaged")

    lib.issue_book("LM001", "113", "BR001")
    lib.return_book("LM001", "113", datetime.date.today(), "lost")

    lib.issue_book("LM002", "114", "BR001")
    lib.return_book("LM002", "114", datetime.date.today(), "good")

    lib.issue_book("LM002", "113", "BR001")

    # Simulate 1 book overdue
    lib.members["LM001"].borrowed_books["112"] = datetime.date.today() - datetime.timedelta(days=3)

    # Set reading challenge manually
    lib.members["LM001"].challenge_progress = 20
    lib.members["LM002"].challenge_progress = 10

    # Display profiles
    lib.display_member_profile("LM001")
    lib.display_member_profile("LM002")
