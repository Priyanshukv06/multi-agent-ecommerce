import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "products.db")

books = [
    {
        "title": "Hands-On Machine Learning with Scikit-Learn, Keras & TensorFlow",
        "author": "Aurélien Géron",
        "price": 899.0,
        "rating": 4.9,
        "category": "machine learning",
        "description": "Practical ML book covering full pipeline from data prep to deployment using Python, Scikit-Learn, and TensorFlow. Best for hands-on learners.",
        "reviews": [
            "Best ML book I have ever read. Covers everything from basics to neural networks with actual code.",
            "Very hands-on approach. Each chapter has exercises. Perfect for someone who learns by doing.",
            "Slightly advanced for absolute beginners but if you know basic Python it is perfect.",
            "The TensorFlow and Keras sections alone are worth the price. Highly recommended.",
            "After reading this book I could build real ML models. No fluff, pure practical knowledge."
        ]
    },
    {
        "title": "Python Machine Learning",
        "author": "Sebastian Raschka",
        "price": 750.0,
        "rating": 4.7,
        "category": "machine learning",
        "description": "Comprehensive guide to ML with Python. Covers algorithms from scratch and with libraries. Strong on theory with practical implementation.",
        "reviews": [
            "Great balance between theory and code. Explains math behind algorithms clearly.",
            "Sebastian explains complex concepts in simple language. Loved the deep learning chapters.",
            "Good book but some chapters feel dense. Better for intermediate learners.",
            "The NLP chapter is excellent. Covers sentiment analysis with real examples.",
            "Bought this after doing basic Python. It stretched my thinking. Worth every rupee."
        ]
    },
    {
        "title": "The Hundred-Page Machine Learning Book",
        "author": "Andriy Burkov",
        "price": 499.0,
        "rating": 4.6,
        "category": "machine learning",
        "description": "Concise ML book that covers all major concepts in 100 pages. Perfect quick reference or fast introduction to the field.",
        "reviews": [
            "Incredible value. So much knowledge packed into a small book.",
            "Read this in 2 days. Great refresher for ML interviews.",
            "Not for absolute beginners but if you have some background this is gold.",
            "Best under ₹500 ML book available. No fluff, just concepts.",
            "The SVM and ensemble methods explanation is the clearest I have seen anywhere."
        ]
    },
    {
        "title": "Introduction to Machine Learning with Python",
        "author": "Andreas Müller & Sarah Guido",
        "price": 649.0,
        "rating": 4.5,
        "category": "machine learning",
        "description": "Beginner-friendly ML book focused on Scikit-Learn. Minimal math, maximum intuition. Best first ML book for Python developers.",
        "reviews": [
            "Perfect for beginners. No scary math just clean code and intuition.",
            "I started ML with this book and it gave me a solid foundation.",
            "Scikit-Learn coverage is top notch. Real world datasets used throughout.",
            "Does not go very deep but it gets you started quickly and correctly.",
            "Finished this in a week. Then moved to Aurélien Géron book. Great progression."
        ]
    },
    {
        "title": "Deep Learning",
        "author": "Ian Goodfellow, Yoshua Bengio, Aaron Courville",
        "price": 1199.0,
        "rating": 4.8,
        "category": "deep learning",
        "description": "The definitive textbook on deep learning. Covers theory rigorously. Written by pioneers of the field. Best for academic deep understanding.",
        "reviews": [
            "The bible of deep learning. Every concept explained from first principles.",
            "Very mathematical. Not for beginners. But if you want to understand DL deeply this is it.",
            "I use this as a reference book. Not cover to cover reading.",
            "Goodfellow explains backpropagation better than any YouTube video.",
            "Heavy content but worth it. Changed how I think about neural networks."
        ]
    },
    {
        "title": "Deep Learning with Python",
        "author": "François Chollet",
        "price": 799.0,
        "rating": 4.8,
        "category": "deep learning",
        "description": "Written by the creator of Keras. Practical deep learning using Python and Keras. Best book for learning neural networks through code.",
        "reviews": [
            "Chollet writes with so much clarity. This is the best DL practical book.",
            "Every code example actually works. No outdated APIs.",
            "Loved the computer vision and NLP chapters. Very practical.",
            "If you want to DO deep learning not just read about it, this is the book.",
            "The second edition has transformer coverage too. Very up to date."
        ]
    },
    {
        "title": "Pattern Recognition and Machine Learning",
        "author": "Christopher Bishop",
        "price": 1299.0,
        "rating": 4.7,
        "category": "machine learning",
        "description": "Graduate-level ML textbook with rigorous mathematical treatment. Covers probabilistic graphical models, Bayesian methods. For researchers.",
        "reviews": [
            "Very mathematical. This is a university textbook not casual reading.",
            "Essential reading if you are pursuing ML research.",
            "Bayesian ML coverage is unmatched anywhere else.",
            "Tough to get through but incredibly rewarding.",
            "Not for beginners. If you are doing a Masters or PhD this is mandatory."
        ]
    },
    {
        "title": "Machine Learning Yearning",
        "author": "Andrew Ng",
        "price": 299.0,
        "rating": 4.5,
        "category": "machine learning",
        "description": "Andrew Ng's practical guide to structuring ML projects. Focuses on how to make strategic decisions when building ML systems.",
        "reviews": [
            "Short and practical. Andrew Ng shares lessons from real projects at Google and Baidu.",
            "Read this in one sitting. Every ML practitioner should read this.",
            "Not about algorithms. About how to think and plan ML projects. Unique.",
            "Changed how I approach error analysis and model improvement.",
            "Free online but worth buying physical copy. Great quick read."
        ]
    },
    {
        "title": "Fluent Python",
        "author": "Luciano Ramalho",
        "price": 849.0,
        "rating": 4.8,
        "category": "python",
        "description": "Master Python's advanced features including generators, decorators, metaclasses and more. For intermediate to advanced Python developers.",
        "reviews": [
            "This book made me a real Python programmer not just a scripter.",
            "Dense but every chapter is worth it. Decorators and generators explained beautifully.",
            "Not for beginners. But once you know basic Python this is the next step.",
            "Best Python book ever written. Period.",
            "Read it twice and still learning new things. Python has so much depth."
        ]
    },
    {
        "title": "Python Crash Course",
        "author": "Eric Matthes",
        "price": 549.0,
        "rating": 4.6,
        "category": "python",
        "description": "Best-selling beginner Python book. Covers fundamentals with 3 real projects: game, data visualization, and web app.",
        "reviews": [
            "My first programming book and it was perfect. Very clear and encouraging.",
            "The project-based approach kept me motivated throughout.",
            "Finished all three projects. Felt so accomplished.",
            "Best beginner Python book available under ₹600.",
            "Explains concepts slowly and clearly. No jargon."
        ]
    },
    {
        "title": "Natural Language Processing with Python",
        "author": "Bird, Klein & Loper",
        "price": 699.0,
        "rating": 4.4,
        "category": "nlp",
        "description": "Classic NLP book using Python's NLTK library. Covers tokenization, POS tagging, parsing, and text classification. Good foundation for NLP.",
        "reviews": [
            "Classic NLP book. A bit dated now but concepts are timeless.",
            "NLTK is old school but understanding it makes modern NLP tools easier.",
            "Good theoretical foundation. Used this in my university course.",
            "Some chapters feel outdated. Pair it with modern transformer tutorials.",
            "Good starting point for NLP. Covers fundamentals thoroughly."
        ]
    },
    {
        "title": "Speech and Language Processing",
        "author": "Dan Jurafsky & James Martin",
        "price": 999.0,
        "rating": 4.7,
        "category": "nlp",
        "description": "The standard NLP textbook covering everything from regular expressions to neural language models and transformers. Used in top universities.",
        "reviews": [
            "The standard NLP textbook. Used in Stanford NLP course.",
            "Third edition covers transformers and BERT. Very up to date.",
            "Academic but very readable. Dan Jurafsky writes with clarity.",
            "Covers breadth and depth of NLP. From regex to GPT concepts.",
            "Essential if you are serious about NLP as a career."
        ]
    },
    {
        "title": "Reinforcement Learning: An Introduction",
        "author": "Sutton & Barto",
        "price": 899.0,
        "rating": 4.8,
        "category": "reinforcement learning",
        "description": "The definitive RL textbook. Covers Markov Decision Processes, Q-Learning, Policy Gradient methods. Written by the founders of RL.",
        "reviews": [
            "If you want to learn RL properly start here. No shortcuts.",
            "Very theoretical but necessary. Every serious RL practitioner needs this.",
            "Second edition covers deep RL too. Timeless material.",
            "The examples using Gridworld and Atari make abstract concepts concrete.",
            "Mathematical but approachable. Takes time but worth every minute."
        ]
    },
    {
        "title": "Hands-On Reinforcement Learning with Python",
        "author": "Sudharsan Ravichandiran",
        "price": 649.0,
        "rating": 4.3,
        "category": "reinforcement learning",
        "description": "Practical RL book using OpenAI Gym and Python. Covers Q-Learning, DQN, PPO with code. Best for learning RL by implementation.",
        "reviews": [
            "Very practical. Every algorithm comes with working Python code.",
            "Good companion to Sutton and Barto. Theory there, practice here.",
            "Some code examples are slightly outdated with newer Gym versions.",
            "Covers enough to build your first RL project.",
            "Nice for beginners to RL who want to code immediately."
        ]
    },
    {
        "title": "Data Science from Scratch",
        "author": "Joel Grus",
        "price": 599.0,
        "rating": 4.4,
        "category": "data science",
        "description": "Builds ML algorithms from scratch using pure Python. Excellent for understanding internals without hiding behind library abstractions.",
        "reviews": [
            "Forces you to actually understand what libraries do under the hood.",
            "Implementing gradient descent from scratch changed my understanding completely.",
            "Good complement to library-based books. Read both for full picture.",
            "Some chapters are a bit dry but the knowledge is invaluable.",
            "Second edition is much better than first. Very updated."
        ]
    },
    {
        "title": "Practical Statistics for Data Scientists",
        "author": "Peter Bruce & Andrew Bruce",
        "price": 699.0,
        "rating": 4.5,
        "category": "data science",
        "description": "Covers statistical concepts specifically for data science applications. No heavy math, intuition-first approach. R and Python examples.",
        "reviews": [
            "Finally a stats book that does not make me want to sleep.",
            "Explains p-values and confidence intervals in a way that actually makes sense.",
            "Both R and Python code provided. Good for switching audiences.",
            "Essential stats foundation for any data scientist.",
            "Short and dense. Very high information density per page."
        ]
    },
    {
        "title": "Machine Learning Design Patterns",
        "author": "Lakshmanan, Robinson & Munn",
        "price": 849.0,
        "rating": 4.5,
        "category": "machine learning",
        "description": "30+ ML design patterns for solving common ML engineering problems. Covers data representation, problem transformation, model training patterns.",
        "reviews": [
            "Changed how I think about ML system design.",
            "Real patterns from Google engineers. Very practical and applicable.",
            "Not for beginners. Best if you have built at least one ML project.",
            "The feature store and model versioning patterns alone justified the price.",
            "Great interview prep for ML engineering roles."
        ]
    },
    {
        "title": "Building Machine Learning Powered Applications",
        "author": "Emmanuel Ameisen",
        "price": 749.0,
        "rating": 4.4,
        "category": "machine learning",
        "description": "Covers the full ML product lifecycle from idea to deployment. Focuses on building usable AI applications, not just models.",
        "reviews": [
            "Fills the gap between academic ML and production ML perfectly.",
            "Covers error analysis, debugging, and deployment. Very practical.",
            "Every ML developer should read this. It teaches you what courses do not.",
            "The failure mode analysis chapter is excellent.",
            "Helped me think about ML products end to end."
        ]
    },
    {
        "title": "Designing Machine Learning Systems",
        "author": "Chip Huyen",
        "price": 899.0,
        "rating": 4.9,
        "category": "machine learning",
        "description": "Comprehensive guide to designing production ML systems. Covers data engineering, feature stores, model deployment, monitoring and more.",
        "reviews": [
            "Best book on ML systems I have ever read. Chip Huyen is exceptional.",
            "Every chapter is pure gold. This is what real ML engineering looks like.",
            "More relevant than most university ML courses.",
            "Covers MLOps concepts clearly. Highly recommended for ML engineers.",
            "This book got me a senior ML engineer job. Enough said."
        ]
    },
    {
        "title": "Mathematics for Machine Learning",
        "author": "Deisenroth, Faisal & Ong",
        "price": 799.0,
        "rating": 4.6,
        "category": "mathematics",
        "description": "Covers the mathematical foundations of ML including linear algebra, calculus, probability, and optimization. Free online, available in print.",
        "reviews": [
            "Finally a math book written for ML practitioners not mathematicians.",
            "Linear algebra and probability chapters are extremely clear.",
            "Read this before any ML book. It makes everything else easier.",
            "Free PDF available online but printed version is nicer to read.",
            "The optimization chapter explains gradient descent mathematically. Eye opening."
        ]
    },
    {
        "title": "An Introduction to Statistical Learning",
        "author": "James, Witten, Hastie & Tibshirani",
        "price": 749.0,
        "rating": 4.7,
        "category": "machine learning",
        "description": "Accessible introduction to statistical learning methods. Covers regression, classification, trees, SVM and unsupervised methods. R and Python labs.",
        "reviews": [
            "The ISLR book is a classic. Very accessible for non-mathematicians.",
            "Python edition recently released. Now more relevant than ever.",
            "Great for understanding theory behind common ML algorithms.",
            "Used in hundreds of universities worldwide. Trusted content.",
            "Best gateway into ML theory without requiring heavy math background."
        ]
    },
    {
        "title": "Grokking Machine Learning",
        "author": "Luis Serrano",
        "price": 649.0,
        "rating": 4.5,
        "category": "machine learning",
        "description": "Visual and intuitive approach to ML. Heavy use of illustrations and minimal math. Best for visual learners who struggle with abstract concepts.",
        "reviews": [
            "If you are a visual learner this is the book for you.",
            "The diagrams make complex concepts click instantly.",
            "Finally understood neural networks properly thanks to this book.",
            "More intuitive than any other ML book I tried.",
            "Perfect for beginners who are scared of math."
        ]
    },
    {
        "title": "Transformers for Natural Language Processing",
        "author": "Denis Rothman",
        "price": 849.0,
        "rating": 4.4,
        "category": "nlp",
        "description": "Practical guide to transformer models including BERT, GPT, T5 using Hugging Face. Covers fine-tuning and deployment of modern NLP models.",
        "reviews": [
            "Very up to date. Covers all modern transformer architectures.",
            "Hugging Face code works out of the box. Very practical.",
            "Some chapters feel rushed but overall very informative.",
            "Best practical transformer book available right now.",
            "Helped me fine-tune BERT for my company project."
        ]
    },
    {
        "title": "Machine Learning with PyTorch and Scikit-Learn",
        "author": "Sebastian Raschka",
        "price": 899.0,
        "rating": 4.7,
        "category": "deep learning",
        "description": "Updated classic covering ML with modern PyTorch. Includes chapters on transformers and graph neural networks. Very comprehensive.",
        "reviews": [
            "Best updated Raschka book. PyTorch makes it very modern.",
            "Transformer chapter is excellent. Very clearly explained.",
            "Covers from logistic regression to graph neural networks. Incredible range.",
            "The graph neural network chapter is rare to find in books.",
            "Perfect if you want one book that covers classical ML and deep learning."
        ]
    },
    {
        "title": "Automate the Boring Stuff with Python",
        "author": "Al Sweigart",
        "price": 449.0,
        "rating": 4.7,
        "category": "python",
        "description": "Teaches Python by automating real tasks: Excel, PDFs, web scraping, scheduling. Free online. Best for learning by solving real problems.",
        "reviews": [
            "This book changed my daily work life. Automated so many tasks.",
            "Completely free online. But worth buying for offline reading.",
            "Best beginner book if you want immediate practical results.",
            "Web scraping chapter is excellent. Built my first scraper from this.",
            "Perfect for non-programmers who want to use Python practically."
        ]
    },
    {
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "price": 699.0,
        "rating": 4.5,
        "category": "software engineering",
        "description": "Principles and best practices for writing clean, maintainable code. Language-agnostic concepts applicable to any programmer.",
        "reviews": [
            "Every programmer should read this. Transformed my code quality.",
            "Some examples feel Java-heavy but principles are universal.",
            "After this book my code reviews became much smoother.",
            "The naming conventions and function design chapters alone are worth it.",
            "A timeless classic. Read it early in your career."
        ]
    },
    {
        "title": "Hands-On Large Language Models",
        "author": "Jay Alammar & Maarten Grootendorst",
        "price": 949.0,
        "rating": 4.8,
        "category": "nlp",
        "description": "Practical guide to using and building with LLMs. Covers prompt engineering, fine-tuning, RAG and embeddings with full code examples.",
        "reviews": [
            "Most practical LLM book I have found. Works with real APIs.",
            "Jay Alammar is the best visual explainer in AI. This book shows that.",
            "RAG and embeddings chapters are outstanding.",
            "Very up to date with GPT-4, Llama and other modern models.",
            "This book is what every AI developer needs right now in 2025."
        ]
    },
    {
        "title": "AI Engineering",
        "author": "Chip Huyen",
        "price": 999.0,
        "rating": 4.9,
        "category": "machine learning",
        "description": "Covers building production AI applications with foundation models, RAG, agents and evals. The most modern ML engineering book available.",
        "reviews": [
            "Chip Huyen does it again. This is the definitive guide to AI engineering.",
            "Covers agents and RAG better than any online course.",
            "Every chapter has practical advice you can apply immediately.",
            "Required reading for any serious AI developer in 2025.",
            "Evaluation framework chapter changed how I measure my AI systems."
        ]
    },
    {
        "title": "Python for Data Analysis",
        "author": "Wes McKinney",
        "price": 799.0,
        "rating": 4.6,
        "category": "data science",
        "description": "Written by the creator of pandas. The definitive guide to data manipulation in Python using NumPy, pandas and Jupyter.",
        "reviews": [
            "Written by the pandas creator himself. The authority on the subject.",
            "Every data analyst needs this. Pandas explained from the inside.",
            "Third edition is fully updated for modern pandas. Very relevant.",
            "The groupby and time series chapters are the best available.",
            "My daily reference for pandas operations."
        ]
    },
    {
        "title": "Feature Engineering for Machine Learning",
        "author": "Alice Zheng & Amanda Casari",
        "price": 699.0,
        "rating": 4.4,
        "category": "machine learning",
        "description": "Focused entirely on feature engineering techniques. Covers numeric, text, categorical and interaction features. Often the most impactful ML skill.",
        "reviews": [
            "The most underrated ML skill finally has its own book.",
            "Feature crosses and interaction terms chapter is incredible.",
            "Very focused. Does one thing and does it brilliantly.",
            "Improved my Kaggle scores more than any other book.",
            "Short but dense. Every page has actionable techniques."
        ]
    }
]


def create_database():
    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ── Products table ──────────────────────────────────────────────────────
    cursor.execute("DROP TABLE IF EXISTS products")
    cursor.execute("""
        CREATE TABLE products (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            author      TEXT NOT NULL,
            price       REAL NOT NULL,
            rating      REAL NOT NULL,
            category    TEXT NOT NULL,
            description TEXT NOT NULL,
            reviews     TEXT NOT NULL
        )
    """)

    # ── Orders table ────────────────────────────────────────────────────────
    cursor.execute("DROP TABLE IF EXISTS orders")
    cursor.execute("""
        CREATE TABLE orders (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id    TEXT UNIQUE NOT NULL,
            product_id  INTEGER NOT NULL,
            user_id     TEXT NOT NULL DEFAULT 'default_user',
            status      TEXT NOT NULL DEFAULT 'confirmed',
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    # ── Returns table ───────────────────────────────────────────────────────
    cursor.execute("DROP TABLE IF EXISTS returns")
    cursor.execute("""
        CREATE TABLE returns (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            return_id    TEXT UNIQUE NOT NULL,
            order_id     TEXT NOT NULL,
            user_id      TEXT NOT NULL DEFAULT 'default_user',
            reason       TEXT,
            status       TEXT NOT NULL DEFAULT 'initiated',
            created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY  (order_id) REFERENCES orders(order_id)
        )
    """)

    # ── Seed books ──────────────────────────────────────────────────────────
    import json
    for book in books:
        cursor.execute("""
            INSERT INTO products (title, author, price, rating, category, description, reviews)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            book["title"], book["author"], book["price"],
            book["rating"], book["category"], book["description"],
            json.dumps(book["reviews"])
        ))

    conn.commit()
    conn.close()
    print(f"✅ Database created at: {DB_PATH}")
    print(f"✅ {len(books)} books seeded successfully")
    print(f"✅ orders + returns tables created")


if __name__ == "__main__":
    create_database()
