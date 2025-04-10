import mysql.connector
from mysql.connector import Error

class BlogManager:
    def __init__(self):
        try:
            self.connection = mysql.connector.connect(
                host='localhost',
                user='root', 
                password='', 
                database='blog_management'
            )
            if self.connection.is_connected():
                print("Successfully connected to the database")
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            exit(1)

    def __del__(self):
        if hasattr(self, 'connection') and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection is closed")

    def create_post(self):
        title = input("Enter post title: ")
        content = input("Enter post content: ")
        tags_input = input("Enter comma-separated tags (e.g., python,web,development): ")
        tags = [tag.strip().lower() for tag in tags_input.split(',') if tag.strip()]

        try:
            cursor = self.connection.cursor()
            
            cursor.execute("INSERT INTO posts (title, content) VALUES (%s, %s)", (title, content))
            post_id = cursor.lastrowid
            
            for tag_name in tags:
                cursor.execute("SELECT id FROM tags WHERE name = %s", (tag_name,))
                tag = cursor.fetchone()
                
                if not tag:
                    cursor.execute("INSERT INTO tags (name) VALUES (%s)", (tag_name,))
                    tag_id = cursor.lastrowid
                else:
                    tag_id = tag[0]
                
                cursor.execute("INSERT INTO post_tags (post_id, tag_id) VALUES (%s, %s)", (post_id, tag_id))
            
            self.connection.commit()
            print(f"Post '{title}' created successfully with tags: {', '.join(tags)}")
        except Error as e:
            self.connection.rollback()
            print(f"Error creating post: {e}")

    def view_all_posts(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT id, title FROM posts ORDER BY created_at DESC")
            posts = cursor.fetchall()
            
            if not posts:
                print("No posts found.")
                return
            
            print("\nAll Posts:")
            for post in posts:
                print(f"{post[0]}. {post[1]}")
            print()
        except Error as e:
            print(f"Error fetching posts: {e}")

    def view_post(self):
        title = input("Enter post title to view: ")
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM posts WHERE title = %s", (title,))
            post = cursor.fetchone()
            
            if not post:
                print(f"Post '{title}' not found.")
                return
            
            cursor.execute("""
                SELECT t.name FROM tags t
                JOIN post_tags pt ON t.id = pt.tag_id
                WHERE pt.post_id = %s
            """, (post['id'],))
            tags = [tag['name'] for tag in cursor.fetchall()]
            
            print(f"\nTitle: {post['title']}")
            print(f"Date: {post['created_at']}")
            print(f"Tags: {', '.join(tags) if tags else 'No tags'}")
            print(f"\nContent:\n{post['content']}\n")
        except Error as e:
            print(f"Error viewing post: {e}")

    def search_by_tag(self):
        tag = input("Enter tag to search for: ").lower()
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT p.id, p.title, p.created_at FROM posts p
                JOIN post_tags pt ON p.id = pt.post_id
                JOIN tags t ON pt.tag_id = t.id
                WHERE t.name = %s
                ORDER BY p.created_at DESC
            """, (tag,))
            posts = cursor.fetchall()
            
            if not posts:
                print(f"No posts found with tag '{tag}'.")
                return
            
            print(f"\nPosts tagged with '{tag}':")
            for post in posts:
                print(f"{post['id']}. {post['title']} ({post['created_at']})")
            print()
        except Error as e:
            print(f"Error searching by tag: {e}")

    def run(self):
        while True:
            print("\nBlog Post Manager")
            print("1. Create a new post")
            print("2. View all post titles")
            print("3. View specific post content")
            print("4. Search posts by tag")
            print("5. Exit")
            
            choice = input("Enter your choice (1-5): ")
            
            if choice == '1':
                self.create_post()
            elif choice == '2':
                self.view_all_posts()
            elif choice == '3':
                self.view_post()
            elif choice == '4':
                self.search_by_tag()
            elif choice == '5':
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 5.")

if __name__ == "__main__":
    manager = BlogManager()
    manager.run()