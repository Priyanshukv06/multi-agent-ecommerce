import sqlite3
import json
import os
import bcrypt

DB_PATH = os.path.join(os.path.dirname(__file__), "products.db")

books = [

    # ── 1. MACHINE LEARNING (8 books) ─────────────────────────────────────────
    {
        "title": "Hands-On Machine Learning with Scikit-Learn, Keras & TensorFlow",
        "author": "Aurélien Géron", "price": 899.0, "rating": 4.9,
        "category": "machine learning", "stock": 50,
        "description": "The most practical ML book available. Covers everything from linear regression to deep neural networks with real projects and clean code.",
        "reviews": ["Best ML book I have ever read. Very practical.", "Covers everything from basics to neural networks.", "Perfect for hands-on learners.", "The gold standard for ML books."]
    },
    {
        "title": "Python Machine Learning",
        "author": "Sebastian Raschka", "price": 750.0, "rating": 4.7,
        "category": "machine learning", "stock": 40,
        "description": "Comprehensive guide to ML with Python covering algorithms, evaluation, pipelines and best practices using scikit-learn and TensorFlow.",
        "reviews": ["Great balance of theory and code.", "Sebastian explains concepts clearly.", "Good for intermediate learners.", "Very thorough coverage of scikit-learn."]
    },
    {
        "title": "Introduction to Machine Learning with Python",
        "author": "Andreas Müller", "price": 649.0, "rating": 4.5,
        "category": "machine learning", "stock": 55,
        "description": "Beginner-friendly ML book focused entirely on Scikit-Learn. No heavy math required — just clean, working code.",
        "reviews": ["Perfect for beginners.", "No scary math, clean code examples.", "Great first ML book.", "Very well structured for newcomers."]
    },
    {
        "title": "Machine Learning with PyTorch and Scikit-Learn",
        "author": "Sebastian Raschka", "price": 899.0, "rating": 4.7,
        "category": "machine learning", "stock": 35,
        "description": "Modern ML combining classical algorithms with deep learning using PyTorch. Covers transformers and large-scale training.",
        "reviews": ["Best book combining classical ML and deep learning.", "PyTorch coverage is excellent.", "Great progression from basics to advanced.", "Updated for modern ML workflows."]
    },
    {
        "title": "The Hundred-Page Machine Learning Book",
        "author": "Andriy Burkov", "price": 499.0, "rating": 4.6,
        "category": "machine learning", "stock": 60,
        "description": "Concise ML overview covering all key algorithms and concepts in 100 pages. Best quick reference for practitioners.",
        "reviews": ["Best ML overview book.", "Dense with information.", "Great quick reference.", "Burkov distills ML perfectly."]
    },
    {
        "title": "Feature Engineering for Machine Learning",
        "author": "Alice Zheng", "price": 699.0, "rating": 4.5,
        "category": "machine learning", "stock": 35,
        "description": "Practical guide to feature engineering covering text, images and structured data. The missing link in most ML curricula.",
        "reviews": ["Essential practical ML skill book.", "Feature engineering is underrated.", "Great real-world examples.", "Must read for ML practitioners."]
    },
    {
        "title": "Approaching Almost Any Machine Learning Problem",
        "author": "Abhishek Thakur", "price": 549.0, "rating": 4.8,
        "category": "machine learning", "stock": 45,
        "description": "World's first Kaggle Grandmaster shares a systematic framework for solving any ML problem end to end.",
        "reviews": ["Game changing for competition ML.", "Abhishek is the real deal.", "Best practical ML framework book.", "Covers everything competition ML needs."]
    },
    {
        "title": "Machine Learning Design Patterns",
        "author": "Valliappa Lakshmanan", "price": 799.0, "rating": 4.5,
        "category": "machine learning", "stock": 30,
        "description": "Solutions to common ML problems presented as reusable design patterns. Covers data representation, training and deployment.",
        "reviews": ["Unique approach to ML problems.", "Design patterns concept works well for ML.", "Very practical and production-focused.", "Good for senior ML engineers."]
    },

    # ── 2. DEEP LEARNING (8 books) ────────────────────────────────────────────
    {
        "title": "Deep Learning",
        "author": "Ian Goodfellow", "price": 1199.0, "rating": 4.8,
        "category": "deep learning", "stock": 30,
        "description": "The definitive textbook on deep learning by the creator of GANs. Rigorous mathematical treatment of neural networks.",
        "reviews": ["The bible of deep learning.", "Essential for anyone serious about AI.", "Dense but incredibly rewarding.", "Best theoretical deep learning resource."]
    },
    {
        "title": "Deep Learning with Python",
        "author": "François Chollet", "price": 799.0, "rating": 4.8,
        "category": "deep learning", "stock": 45,
        "description": "Keras creator's guide to deep learning. Practical code-first approach using Python and Keras with real-world projects.",
        "reviews": ["Perfect balance of theory and practice.", "Chollet explains concepts brilliantly.", "Best introduction to Keras and deep learning.", "The most accessible DL book available."]
    },
    {
        "title": "Neural Networks and Deep Learning",
        "author": "Michael Nielsen", "price": 549.0, "rating": 4.6,
        "category": "deep learning", "stock": 50,
        "description": "Free online book that explains neural networks intuitively from first principles. Best beginner DL resource available.",
        "reviews": ["Best free DL learning resource.", "Nielsen explains backprop perfectly.", "Intuitive without losing rigor.", "Where everyone should start with DL."]
    },
    {
        "title": "Generative Deep Learning",
        "author": "David Foster", "price": 849.0, "rating": 4.7,
        "category": "deep learning", "stock": 30,
        "description": "Covers GANs, VAEs, diffusion models and LLMs with hands-on Keras code. Updated with latest generative AI advances.",
        "reviews": ["Best generative AI book.", "Foster explains GANs brilliantly.", "Code examples are excellent.", "Updated with diffusion models."]
    },
    {
        "title": "Graph Neural Networks in Action",
        "author": "Keita Broadwater", "price": 849.0, "rating": 4.5,
        "category": "deep learning", "stock": 25,
        "description": "Practical guide to GNNs covering graph data, message passing architectures and real-world applications.",
        "reviews": ["Best practical GNN book.", "Fills a big gap in the literature.", "Great code examples.", "Essential for graph ML work."]
    },
    {
        "title": "Programming PyTorch for Deep Learning",
        "author": "Ian Pointer", "price": 699.0, "rating": 4.5,
        "category": "deep learning", "stock": 40,
        "description": "Practical introduction to building deep learning models with PyTorch covering CNNs, RNNs and transfer learning.",
        "reviews": ["Best introductory PyTorch book.", "Very hands-on approach.", "Good progression from basics.", "Clean code examples throughout."]
    },
    {
        "title": "Dive into Deep Learning",
        "author": "Aston Zhang", "price": 999.0, "rating": 4.7,
        "category": "deep learning", "stock": 25,
        "description": "Interactive deep learning textbook with math, code and discussion. Covers modern architectures including transformers.",
        "reviews": ["Best comprehensive DL textbook.", "Interactive format is great.", "Math and code together is perfect.", "Essential modern DL resource."]
    },
    {
        "title": "Natural Language Processing with Transformers",
        "author": "Lewis Tunstall", "price": 899.0, "rating": 4.8,
        "category": "deep learning", "stock": 35,
        "description": "Hands-on guide to building NLP applications with Hugging Face Transformers including BERT, GPT and T5.",
        "reviews": ["Best practical transformer book.", "Hugging Face team knows their stuff.", "Real-world NLP applications covered.", "Essential for modern NLP work."]
    },

    # ── 3. PYTHON (7 books) ───────────────────────────────────────────────────
    {
        "title": "Python Crash Course",
        "author": "Eric Matthes", "price": 499.0, "rating": 4.8,
        "category": "python", "stock": 80,
        "description": "Fast-paced introduction to Python. Best book for absolute beginners featuring 3 real projects — game, data viz and web app.",
        "reviews": ["Best Python book for beginners.", "Very clear and well structured.", "Loved the project-based approach.", "Perfect first programming book."]
    },
    {
        "title": "Fluent Python",
        "author": "Luciano Ramalho", "price": 950.0, "rating": 4.9,
        "category": "python", "stock": 25,
        "description": "Deep dive into Python features and idioms. Essential reading for intermediate to advanced Python developers.",
        "reviews": ["Best advanced Python book.", "Changed how I write Python code.", "Essential reading for Python developers.", "Ramalho's explanations are superb."]
    },
    {
        "title": "Automate the Boring Stuff with Python",
        "author": "Al Sweigart", "price": 399.0, "rating": 4.7,
        "category": "python", "stock": 90,
        "description": "Practical Python for real-world automation. Covers file handling, web scraping, Excel and PDF automation.",
        "reviews": ["Life-changing for productivity.", "Made Python fun and practical.", "Perfect for non-programmers.", "Free online and still worth buying."]
    },
    {
        "title": "Effective Python",
        "author": "Brett Slatkin", "price": 749.0, "rating": 4.7,
        "category": "python", "stock": 40,
        "description": "90 specific ways to write better Python. Covers Pythonic patterns, concurrency, testing and performance.",
        "reviews": ["Best book for writing idiomatic Python.", "Each item is actionable.", "Slatkin knows Python deeply.", "Essential for professional Python developers."]
    },
    {
        "title": "Python Tricks: The Book",
        "author": "Dan Bader", "price": 449.0, "rating": 4.6,
        "category": "python", "stock": 50,
        "description": "Practical Python patterns and tricks to write cleaner code. Great for intermediate developers wanting to level up.",
        "reviews": ["Great collection of Python tips.", "Every trick is genuinely useful.", "Bader presents things clearly.", "Perfect companion to Fluent Python."]
    },
    {
        "title": "Learning Python",
        "author": "Mark Lutz", "price": 849.0, "rating": 4.4,
        "category": "python", "stock": 35,
        "description": "The most comprehensive Python reference available. Covers the language in exhaustive detail.",
        "reviews": ["Most thorough Python book.", "Great reference to have nearby.", "Lutz covers everything.", "Good if you want complete coverage."]
    },
    {
        "title": "Python Cookbook",
        "author": "David Beazley", "price": 799.0, "rating": 4.7,
        "category": "python", "stock": 30,
        "description": "Recipes for Python 3 covering data structures, algorithms, networking and system administration.",
        "reviews": ["Best Python recipes book.", "Beazley is a Python expert.", "Covers advanced topics well.", "Great reference for working developers."]
    },

    # ── 4. DATA SCIENCE (7 books) ─────────────────────────────────────────────
    {
        "title": "Python for Data Analysis",
        "author": "Wes McKinney", "price": 849.0, "rating": 4.6,
        "category": "data science", "stock": 40,
        "description": "The definitive guide to pandas by its creator. Covers data wrangling, aggregation and time series analysis.",
        "reviews": ["Essential for data scientists.", "Best pandas reference available.", "McKinney knows pandas inside out.", "Comprehensive and practical."]
    },
    {
        "title": "Data Science from Scratch",
        "author": "Joel Grus", "price": 699.0, "rating": 4.5,
        "category": "data science", "stock": 45,
        "description": "Build data science tools from scratch in Python. Great for understanding the fundamentals behind libraries.",
        "reviews": ["Great for understanding foundations.", "Building from scratch really helps.", "Grus has a great teaching style.", "Perfect complement to library-heavy books."]
    },
    {
        "title": "The Data Science Handbook",
        "author": "Field Cady", "price": 749.0, "rating": 4.4,
        "category": "data science", "stock": 30,
        "description": "Comprehensive guide covering the full data science workflow from data collection to production deployment.",
        "reviews": ["Great overview of the full DS workflow.", "Practical and comprehensive.", "Good reference for working data scientists.", "Covers topics other books miss."]
    },
    {
        "title": "Storytelling with Data",
        "author": "Cole Nussbaumer Knaflic", "price": 649.0, "rating": 4.8,
        "category": "data science", "stock": 50,
        "description": "How to create compelling data visualisations that communicate effectively. Essential for every data analyst.",
        "reviews": ["Changed how I present data.", "Best data viz communication book.", "Practical and beautifully written.", "Every data analyst needs this."]
    },
    {
        "title": "Practical Statistics for Data Scientists",
        "author": "Peter Bruce", "price": 749.0, "rating": 4.6,
        "category": "data science", "stock": 40,
        "description": "Statistics fundamentals applied to data science problems with R and Python code examples.",
        "reviews": ["Best stats book for data scientists.", "Makes statistics practical.", "Great R and Python examples.", "Essential stats foundation."]
    },
    {
        "title": "Data Science for Business",
        "author": "Foster Provost", "price": 699.0, "rating": 4.5,
        "category": "data science", "stock": 35,
        "description": "Data science concepts for business professionals. Covers decision making, prediction and model evaluation.",
        "reviews": ["Best DS book for business context.", "Provost bridges business and data science.", "Great for non-technical stakeholders.", "Essential for DS product managers."]
    },
    {
        "title": "Hands-On Data Analysis with Pandas",
        "author": "Stefanie Molin", "price": 799.0, "rating": 4.6,
        "category": "data science", "stock": 35,
        "description": "Practical data analysis with pandas covering data wrangling, visualisation and anomaly detection with real datasets.",
        "reviews": ["Best hands-on pandas book.", "Real datasets make it practical.", "Molin explains pandas clearly.", "Great project-based learning."]
    },

    # ── 5. NLP (7 books) ──────────────────────────────────────────────────────
    {
        "title": "Natural Language Processing with Python",
        "author": "Steven Bird", "price": 699.0, "rating": 4.5,
        "category": "nlp", "stock": 35,
        "description": "Classic NLP book using NLTK. Covers text processing, classification, parsing and semantic analysis.",
        "reviews": ["The classic NLP textbook.", "NLTK coverage is comprehensive.", "Good foundation for NLP work.", "Essential starting point for NLP."]
    },
    {
        "title": "Speech and Language Processing",
        "author": "Dan Jurafsky", "price": 999.0, "rating": 4.8,
        "category": "nlp", "stock": 20,
        "description": "Comprehensive NLP and computational linguistics textbook. The industry and academic gold standard.",
        "reviews": ["The gold standard NLP textbook.", "Jurafsky is a legend in the field.", "Covers everything in NLP.", "Essential for serious NLP work."]
    },
    {
        "title": "Transformers for Natural Language Processing",
        "author": "Denis Rothman", "price": 849.0, "rating": 4.6,
        "category": "nlp", "stock": 30,
        "description": "Practical guide to transformer models including BERT, GPT and T5 using the Hugging Face ecosystem.",
        "reviews": ["Best practical transformer book.", "Hugging Face coverage is excellent.", "Perfect for modern NLP work.", "Great code examples throughout."]
    },
    {
        "title": "Applied Text Analysis with Python",
        "author": "Benjamin Bengfort", "price": 749.0, "rating": 4.4,
        "category": "nlp", "stock": 30,
        "description": "End-to-end NLP pipeline building with Python covering feature extraction, classification and topic modelling.",
        "reviews": ["Very practical NLP book.", "Good pipeline-focused approach.", "Real-world text analysis coverage.", "Good complement to Jurafsky."]
    },
    {
        "title": "Text Analytics with Python",
        "author": "Dipanjan Sarkar", "price": 799.0, "rating": 4.5,
        "category": "nlp", "stock": 25,
        "description": "Practical NLP covering sentiment analysis, topic modelling, text classification and named entity recognition.",
        "reviews": ["Comprehensive NLP with Python.", "Good breadth of topics.", "Sarkar covers practical applications well.", "Great for applied NLP projects."]
    },
    {
        "title": "Practical Natural Language Processing",
        "author": "Sowmya Vajjala", "price": 849.0, "rating": 4.6,
        "category": "nlp", "stock": 30,
        "description": "End-to-end NLP for building real-world applications covering data collection, modelling and deployment.",
        "reviews": ["Best production NLP book.", "Great end-to-end coverage.", "Real application focus is refreshing.", "Essential for NLP engineers."]
    },
    {
        "title": "Mastering spaCy",
        "author": "Duygu Altinok", "price": 699.0, "rating": 4.4,
        "category": "nlp", "stock": 25,
        "description": "In-depth guide to spaCy for industrial-strength NLP covering pipelines, custom components and deployment.",
        "reviews": ["Best spaCy book available.", "Altinok knows spaCy inside out.", "Very practical pipeline approach.", "Great for production NLP."]
    },

    # ── 6. MATHEMATICS (7 books) ──────────────────────────────────────────────
    {
        "title": "Mathematics for Machine Learning",
        "author": "Marc Deisenroth", "price": 799.0, "rating": 4.7,
        "category": "mathematics", "stock": 35,
        "description": "Covers linear algebra, calculus, probability and statistics with ML applications. Free PDF available online.",
        "reviews": ["Best ML math foundation book.", "Makes the math accessible.", "Essential before tackling advanced ML.", "Very well explained concepts."]
    },
    {
        "title": "The Elements of Statistical Learning",
        "author": "Trevor Hastie", "price": 1099.0, "rating": 4.8,
        "category": "mathematics", "stock": 20,
        "description": "Comprehensive statistical learning theory graduate textbook. Used worldwide in top ML programmes.",
        "reviews": ["The statistician ML bible.", "Dense but incredibly thorough.", "Essential for ML researchers.", "Free PDF available too."]
    },
    {
        "title": "Pattern Recognition and Machine Learning",
        "author": "Christopher Bishop", "price": 1299.0, "rating": 4.8,
        "category": "mathematics", "stock": 15,
        "description": "Bishop's classic probabilistic ML textbook covering Bayesian methods, graphical models and neural networks.",
        "reviews": ["Bishop's masterpiece.", "The probabilistic ML standard.", "Essential for ML researchers.", "Very mathematical but worth it."]
    },
    {
        "title": "Linear Algebra Done Right",
        "author": "Sheldon Axler", "price": 749.0, "rating": 4.7,
        "category": "mathematics", "stock": 35,
        "description": "Clean determinant-free approach to linear algebra. Best book for understanding the subject deeply.",
        "reviews": ["Best linear algebra textbook.", "Axler's approach is brilliant.", "Makes linear algebra crystal clear.", "Essential for ML foundations."]
    },
    {
        "title": "Probability Theory: The Logic of Science",
        "author": "E.T. Jaynes", "price": 899.0, "rating": 4.7,
        "category": "mathematics", "stock": 25,
        "description": "Definitive Bayesian probability textbook. Covers probability as an extension of logic with ML applications.",
        "reviews": ["The Bayesian bible.", "Jaynes changed my view of probability.", "Dense but transformative.", "Essential for Bayesian ML."]
    },
    {
        "title": "All of Statistics",
        "author": "Larry Wasserman", "price": 849.0, "rating": 4.6,
        "category": "mathematics", "stock": 30,
        "description": "Concise overview of statistical theory covering estimation, hypothesis testing and Bayesian inference.",
        "reviews": ["Best concise statistics book.", "Wasserman is very clear.", "Great overview of all stats.", "Perfect for ML students."]
    },
    {
        "title": "Statistical Inference",
        "author": "George Casella", "price": 999.0, "rating": 4.6,
        "category": "mathematics", "stock": 20,
        "description": "Classic graduate statistics textbook covering probability, distributions, estimation and hypothesis testing rigorously.",
        "reviews": ["The classic stats inference book.", "Rigorous and thorough.", "Casella and Berger is the gold standard.", "Hard but essential."]
    },

    # ── 7. ALGORITHMS (8 books) ───────────────────────────────────────────────
    {
        "title": "Introduction to Algorithms (CLRS)",
        "author": "Thomas Cormen", "price": 1299.0, "rating": 4.8,
        "category": "algorithms", "stock": 40,
        "description": "The definitive algorithms textbook. Covers every major algorithm with mathematical proofs and pseudocode.",
        "reviews": ["The algorithm bible.", "Every CS student must own this.", "Comprehensive and rigorous.", "The standard reference for algorithms."]
    },
    {
        "title": "Algorithms",
        "author": "Robert Sedgewick", "price": 999.0, "rating": 4.7,
        "category": "algorithms", "stock": 35,
        "description": "Practical algorithms and data structures with Java implementations. Beautifully illustrated and clearly explained.",
        "reviews": ["Best practical algorithms book.", "Sedgewick explains visually.", "Java examples are clean.", "Great companion to CLRS."]
    },
    {
        "title": "The Algorithm Design Manual",
        "author": "Steven Skiena", "price": 899.0, "rating": 4.8,
        "category": "algorithms", "stock": 30,
        "description": "Practical algorithm design with real-world applications and a comprehensive catalog of algorithm techniques.",
        "reviews": ["Best algorithm design book.", "Skiena war stories are gold.", "Algorithm catalog is incredibly useful.", "Must-read for competitive programmers."]
    },
    {
        "title": "Grokking Algorithms",
        "author": "Aditya Bhargava", "price": 549.0, "rating": 4.8,
        "category": "algorithms", "stock": 70,
        "description": "Visual beginner-friendly introduction to algorithms with illustrations. Makes complex algorithms approachable.",
        "reviews": ["Best beginner algorithms book.", "Illustrations make everything clear.", "Bhargava explains beautifully.", "Perfect first algorithms book."]
    },
    {
        "title": "Competitive Programming 3",
        "author": "Steven Halim", "price": 799.0, "rating": 4.7,
        "category": "algorithms", "stock": 30,
        "description": "Complete guide to competitive programming covering all algorithm types with ICPC-style problems.",
        "reviews": ["Best competitive programming book.", "Comprehensive problem coverage.", "Essential for ICPC prep.", "Halim knows CP inside out."]
    },
    {
        "title": "Data Structures and Algorithms in Python",
        "author": "Michael Goodrich", "price": 899.0, "rating": 4.6,
        "category": "algorithms", "stock": 45,
        "description": "Complete DSA textbook using Python. Covers arrays, linked lists, trees, graphs and all sorting algorithms.",
        "reviews": ["Best Python DSA book.", "Clean Python implementations.", "Goodrich explains clearly.", "Great for Python developers."]
    },
    {
        "title": "Cracking the Coding Interview",
        "author": "Gayle Laakmann McDowell", "price": 849.0, "rating": 4.7,
        "category": "algorithms", "stock": 60,
        "description": "189 programming questions and solutions. The go-to interview prep book for software engineering roles.",
        "reviews": ["Essential for coding interviews.", "McDowell knows what interviewers want.", "Coverage is comprehensive.", "Got me my dream job."]
    },
    {
        "title": "Elements of Programming Interviews in Python",
        "author": "Adnan Aziz", "price": 799.0, "rating": 4.6,
        "category": "algorithms", "stock": 40,
        "description": "300+ interview problems with Python solutions covering all major DSA topics for top tech companies.",
        "reviews": ["Great Python interview prep.", "Problems are well chosen.", "Solutions are clean and explained.", "Perfect for FAANG prep."]
    },

    # ── 8. SYSTEM DESIGN (7 books) ────────────────────────────────────────────
    {
        "title": "Designing Data-Intensive Applications",
        "author": "Martin Kleppmann", "price": 999.0, "rating": 4.9,
        "category": "system design", "stock": 40,
        "description": "The definitive guide to building scalable, reliable and maintainable systems. Covers databases, streams and distributed systems.",
        "reviews": ["The best tech book I have ever read.", "Kleppmann explains distributed systems perfectly.", "Essential for every backend engineer.", "Changed how I think about systems."]
    },
    {
        "title": "System Design Interview",
        "author": "Alex Xu", "price": 799.0, "rating": 4.7,
        "category": "system design", "stock": 55,
        "description": "Step-by-step framework for cracking system design interviews. Covers URL shorteners, Twitter, YouTube and more.",
        "reviews": ["Best system design interview prep.", "Alex Xu examples are perfect.", "Framework is very usable.", "Got me through my system design rounds."]
    },
    {
        "title": "System Design Interview Volume 2",
        "author": "Alex Xu", "price": 849.0, "rating": 4.7,
        "category": "system design", "stock": 45,
        "description": "Advanced system design problems covering proximity services, distributed message queues and real-time gaming leaderboards.",
        "reviews": ["Great follow-up to volume 1.", "Harder problems than vol 1.", "Great depth on each system.", "Essential for senior engineering interviews."]
    },
    {
        "title": "Clean Architecture",
        "author": "Robert C. Martin", "price": 799.0, "rating": 4.6,
        "category": "system design", "stock": 45,
        "description": "Uncle Bob's guide to building software systems with clean maintainable architecture and SOLID principles.",
        "reviews": ["Uncle Bob is always worth reading.", "Changed how I structure code.", "SOLID principles explained brilliantly.", "Essential for software architects."]
    },
    {
        "title": "Software Architecture Patterns",
        "author": "Mark Richards", "price": 649.0, "rating": 4.5,
        "category": "system design", "stock": 40,
        "description": "Covers five key architecture patterns: layered, event-driven, microkernel, microservices and space-based.",
        "reviews": ["Great concise overview of patterns.", "Richards explains tradeoffs well.", "Good starting point for architects.", "Very practical focus."]
    },
    {
        "title": "Building Microservices",
        "author": "Sam Newman", "price": 949.0, "rating": 4.7,
        "category": "system design", "stock": 35,
        "description": "The definitive guide to designing, building and deploying microservices in production environments.",
        "reviews": ["The microservices bible.", "Newman explains everything clearly.", "Very practical and opinionated.", "Essential for distributed system design."]
    },
    {
        "title": "The Art of Scalability",
        "author": "Martin Abbott", "price": 899.0, "rating": 4.5,
        "category": "system design", "stock": 25,
        "description": "Framework for scaling people, process and technology. The scale cube model is widely used in industry.",
        "reviews": ["Great scalability framework.", "Beyond just technical scaling.", "Scale cube is a great mental model.", "Good for engineering managers too."]
    },

    # ── 9. DATABASES (7 books) ────────────────────────────────────────────────
    {
        "title": "Database Internals",
        "author": "Alex Petrov", "price": 899.0, "rating": 4.7,
        "category": "databases", "stock": 30,
        "description": "Deep dive into how databases work internally covering storage engines, indexing and distributed protocols.",
        "reviews": ["Best database internals book.", "Petrov explains low-level details brilliantly.", "Essential for database engineers.", "Changed how I use databases."]
    },
    {
        "title": "Learning SQL",
        "author": "Alan Beaulieu", "price": 549.0, "rating": 4.6,
        "category": "databases", "stock": 55,
        "description": "Clear introduction to SQL covering queries, joins, subqueries and transactions. Best SQL beginner book.",
        "reviews": ["Best SQL book for beginners.", "Beaulieu explains SQL very clearly.", "Great progression of topics.", "Perfect first SQL book."]
    },
    {
        "title": "SQL Performance Explained",
        "author": "Markus Winand", "price": 699.0, "rating": 4.7,
        "category": "databases", "stock": 35,
        "description": "How indexes work under the hood and how to use them to write fast SQL queries across all major databases.",
        "reviews": ["Best SQL performance book.", "Winand explains indexes perfectly.", "Immediately applicable.", "Made my queries 10x faster."]
    },
    {
        "title": "NoSQL Distilled",
        "author": "Pramod Sadalage", "price": 649.0, "rating": 4.5,
        "category": "databases", "stock": 35,
        "description": "Concise guide to NoSQL databases covering key-value, document, column-family and graph stores with tradeoffs.",
        "reviews": ["Best NoSQL overview.", "Covers all NoSQL types concisely.", "Great for choosing the right DB.", "Fowler and Sadalage are great."]
    },
    {
        "title": "MongoDB: The Definitive Guide",
        "author": "Kristina Chodorow", "price": 799.0, "rating": 4.5,
        "category": "databases", "stock": 30,
        "description": "Complete guide to MongoDB covering CRUD, indexing, aggregation, replication and sharding.",
        "reviews": ["Best MongoDB book.", "Chodorow knows MongoDB deeply.", "Comprehensive coverage.", "Great reference for MongoDB developers."]
    },
    {
        "title": "Redis in Action",
        "author": "Josiah Carlson", "price": 749.0, "rating": 4.6,
        "category": "databases", "stock": 30,
        "description": "Practical Redis covering data structures and patterns for caching, queuing, real-time analytics and search.",
        "reviews": ["Best Redis book.", "Carlson shows creative Redis uses.", "Very practical approach.", "Essential for Redis practitioners."]
    },
    {
        "title": "PostgreSQL: Up and Running",
        "author": "Regina Obe", "price": 699.0, "rating": 4.5,
        "category": "databases", "stock": 35,
        "description": "Practical guide to PostgreSQL covering installation, queries, extensions and performance tuning.",
        "reviews": ["Best introductory PostgreSQL book.", "Gets you productive quickly.", "Good coverage of extensions.", "Great reference for PostgreSQL users."]
    },

    # ── 10. OPERATING SYSTEMS (6 books) ──────────────────────────────────────
    {
        "title": "Operating System Concepts (Dinosaur Book)",
        "author": "Abraham Silberschatz", "price": 1199.0, "rating": 4.7,
        "category": "operating systems", "stock": 30,
        "description": "The standard OS textbook covering processes, memory, storage and protection. Used in universities worldwide.",
        "reviews": ["The standard OS textbook.", "Silberschatz explains OS clearly.", "Comprehensive coverage of all OS topics.", "Essential for CS students."]
    },
    {
        "title": "Modern Operating Systems",
        "author": "Andrew Tanenbaum", "price": 1099.0, "rating": 4.7,
        "category": "operating systems", "stock": 25,
        "description": "Tanenbaum's classic OS textbook with real-world examples from Unix, Windows and Android.",
        "reviews": ["Tanenbaum is the OS master.", "Better examples than Silberschatz.", "Very readable for a textbook.", "Essential for deep OS understanding."]
    },
    {
        "title": "The Linux Command Line",
        "author": "William Shotts", "price": 549.0, "rating": 4.8,
        "category": "operating systems", "stock": 60,
        "description": "Complete guide to the Linux command line covering shell scripting, file management and system administration.",
        "reviews": ["Best Linux command line book.", "Shotts explains everything clearly.", "Free online too.", "Made me productive in Linux fast."]
    },
    {
        "title": "Linux Kernel Development",
        "author": "Robert Love", "price": 899.0, "rating": 4.7,
        "category": "operating systems", "stock": 20,
        "description": "Comprehensive guide to Linux kernel internals covering processes, scheduling, memory management and device drivers.",
        "reviews": ["The Linux kernel book.", "Love explains kernel clearly.", "Essential for systems programmers.", "Great depth without being impenetrable."]
    },
    {
        "title": "Systems Performance",
        "author": "Brendan Gregg", "price": 1099.0, "rating": 4.8,
        "category": "operating systems", "stock": 20,
        "description": "Comprehensive systems performance analysis covering OS internals, CPU, memory, file systems and networking.",
        "reviews": ["Brendan Gregg is the performance master.", "No other book comes close.", "Essential for SREs and systems engineers.", "Changed how I debug performance issues."]
    },
    {
        "title": "How Linux Works",
        "author": "Brian Ward", "price": 649.0, "rating": 4.6,
        "category": "operating systems", "stock": 40,
        "description": "What every Linux user should know about how the OS works under the hood. Practical and demystifying.",
        "reviews": ["Best practical Linux internals book.", "Ward explains without jargon.", "Perfect for developers new to Linux.", "Makes Linux much less mysterious."]
    },

    # ── 11. COMPUTER NETWORKS (6 books) ──────────────────────────────────────
    {
        "title": "Computer Networking: A Top-Down Approach",
        "author": "James Kurose", "price": 1099.0, "rating": 4.7,
        "category": "computer networks", "stock": 30,
        "description": "The standard networking textbook using a top-down approach from applications to physical layer.",
        "reviews": ["Best networking textbook.", "Top-down approach makes sense.", "Kurose explains networks clearly.", "Essential for CS students."]
    },
    {
        "title": "Computer Networks",
        "author": "Andrew Tanenbaum", "price": 999.0, "rating": 4.6,
        "category": "computer networks", "stock": 25,
        "description": "Classic networking textbook covering protocols, architecture and implementation from physical to application layer.",
        "reviews": ["Tanenbaum is always excellent.", "Bottom-up approach is thorough.", "Great complement to Kurose.", "Essential networking reference."]
    },
    {
        "title": "High Performance Browser Networking",
        "author": "Ilya Grigorik", "price": 799.0, "rating": 4.7,
        "category": "computer networks", "stock": 30,
        "description": "Deep dive into networking protocols for web performance including TCP, UDP, HTTP/2 and WebSockets.",
        "reviews": ["Best web networking book.", "Grigorik is a Google expert.", "Made my web apps significantly faster.", "Free online too."]
    },
    {
        "title": "TCP/IP Illustrated Volume 1",
        "author": "Kevin Fall", "price": 1099.0, "rating": 4.7,
        "category": "computer networks", "stock": 20,
        "description": "Definitive TCP/IP reference with detailed protocol analysis using packet captures and real-world examples.",
        "reviews": ["The TCP/IP reference.", "Stevens original is a classic.", "Essential for network engineers.", "Most thorough protocol coverage available."]
    },
    {
        "title": "Network Programming with Go",
        "author": "Adam Woodbeck", "price": 799.0, "rating": 4.5,
        "category": "computer networks", "stock": 30,
        "description": "Practical network programming using Go covering sockets, REST, gRPC and secure communications.",
        "reviews": ["Best network programming with Go.", "Very practical approach.", "Good coverage of modern protocols.", "Great for Go backend developers."]
    },
    {
        "title": "DNS and BIND",
        "author": "Cricket Liu", "price": 849.0, "rating": 4.4,
        "category": "computer networks", "stock": 20,
        "description": "Comprehensive guide to DNS and BIND covering configuration, security and troubleshooting.",
        "reviews": ["The DNS reference book.", "Essential for sysadmins.", "Liu covers DNS completely.", "Great troubleshooting guide."]
    },

    # ── 12. DISTRIBUTED SYSTEMS (7 books) ─────────────────────────────────────
    {
        "title": "Designing Distributed Systems",
        "author": "Brendan Burns", "price": 749.0, "rating": 4.5,
        "category": "distributed systems", "stock": 35,
        "description": "Patterns for distributed system design by the co-creator of Kubernetes. Covers sidecars, ambassadors and adapters.",
        "reviews": ["Burns is the distributed systems expert.", "Patterns are practical.", "Great Kubernetes context.", "Essential for cloud engineers."]
    },
    {
        "title": "Understanding Distributed Systems",
        "author": "Roberto Vitillo", "price": 699.0, "rating": 4.6,
        "category": "distributed systems", "stock": 40,
        "description": "Accessible introduction to distributed systems covering communication, coordination and scalability.",
        "reviews": ["Best intro to distributed systems.", "Vitillo is very clear.", "Makes complex topics accessible.", "Perfect starting point."]
    },
    {
        "title": "Distributed Systems: Principles and Paradigms",
        "author": "Andrew Tanenbaum", "price": 999.0, "rating": 4.6,
        "category": "distributed systems", "stock": 25,
        "description": "Classic distributed systems textbook covering communication, naming, synchronisation, consistency and replication.",
        "reviews": ["Classic Tanenbaum quality.", "Comprehensive distributed systems coverage.", "Great theoretical foundation.", "Essential textbook."]
    },
    {
        "title": "Kafka: The Definitive Guide",
        "author": "Neha Narkhede", "price": 899.0, "rating": 4.6,
        "category": "distributed systems", "stock": 30,
        "description": "Complete guide to Apache Kafka covering producers, consumers, streams and large-scale operations.",
        "reviews": ["The Kafka bible.", "Narkhede co-created Kafka.", "Comprehensive and practical.", "Essential for event-driven systems."]
    },
    {
        "title": "Designing Event-Driven Systems",
        "author": "Ben Stopford", "price": 749.0, "rating": 4.5,
        "category": "distributed systems", "stock": 30,
        "description": "Guide to building event-driven microservices with Kafka covering event sourcing and CQRS patterns.",
        "reviews": ["Best event-driven systems book.", "Stopford explains event sourcing clearly.", "CQRS coverage is excellent.", "Essential for event-driven architects."]
    },
    {
        "title": "Cloud Native Patterns",
        "author": "Cornelia Davis", "price": 849.0, "rating": 4.5,
        "category": "distributed systems", "stock": 30,
        "description": "Patterns for building cloud-native applications covering microservices, containers and dynamic routing.",
        "reviews": ["Great cloud native patterns.", "Davis explains patterns clearly.", "Very practical approach.", "Good for cloud architects."]
    },
    {
        "title": "Site Reliability Engineering",
        "author": "Niall Richard Murphy", "price": 999.0, "rating": 4.8,
        "category": "distributed systems", "stock": 35,
        "description": "How Google runs production systems. Covers SLOs, error budgets, toil reduction and incident management.",
        "reviews": ["The SRE bible.", "Google production wisdom.", "Essential for SREs and DevOps.", "Changed how I think about reliability."]
    },

    # ── 13. REINFORCEMENT LEARNING (5 books) ──────────────────────────────────
    {
        "title": "Reinforcement Learning: An Introduction",
        "author": "Richard Sutton", "price": 999.0, "rating": 4.9,
        "category": "reinforcement learning", "stock": 25,
        "description": "The definitive RL textbook by Sutton and Barto. Covers all fundamental RL algorithms from bandits to deep RL.",
        "reviews": ["The RL bible. Period.", "Sutton and Barto are legends.", "Essential for anyone in RL.", "Free online and still worth buying."]
    },
    {
        "title": "Grokking Deep Reinforcement Learning",
        "author": "Miguel Morales", "price": 849.0, "rating": 4.6,
        "category": "reinforcement learning", "stock": 30,
        "description": "Practical deep RL with Python code. Bridges theory and implementation with clean examples.",
        "reviews": ["Best practical RL book.", "Great code examples.", "Makes RL approachable.", "Perfect complement to Sutton."]
    },
    {
        "title": "Deep Reinforcement Learning Hands-On",
        "author": "Maxim Lapan", "price": 899.0, "rating": 4.6,
        "category": "reinforcement learning", "stock": 25,
        "description": "Practical deep RL using PyTorch covering DQN, policy gradients, DDPG and AlphaGo-style methods.",
        "reviews": ["Best hands-on RL book.", "PyTorch code is clean.", "Lapan covers advanced topics well.", "Great for RL practitioners."]
    },
    {
        "title": "Algorithms for Reinforcement Learning",
        "author": "Csaba Szepesvári", "price": 649.0, "rating": 4.5,
        "category": "reinforcement learning", "stock": 20,
        "description": "Concise mathematical treatment of RL algorithms covering TD learning, Q-learning and policy gradient methods.",
        "reviews": ["Best concise RL algorithms book.", "Mathematical rigor is appreciated.", "Good supplement to Sutton.", "Dense but valuable."]
    },
    {
        "title": "Foundations of Deep Reinforcement Learning",
        "author": "Laura Graesser", "price": 799.0, "rating": 4.5,
        "category": "reinforcement learning", "stock": 25,
        "description": "Theory and practice of deep RL covering policy gradients, actor-critic and model-based methods.",
        "reviews": ["Great theory plus practice balance.", "Graesser explains foundations clearly.", "Good code examples.", "Essential modern RL book."]
    },

    # ── 14. MLOPS (6 books) ───────────────────────────────────────────────────
    {
        "title": "Designing Machine Learning Systems",
        "author": "Chip Huyen", "price": 849.0, "rating": 4.8,
        "category": "mlops", "stock": 40,
        "description": "End-to-end ML system design covering data, training, deployment and monitoring in production.",
        "reviews": ["Best MLOps book available.", "Chip Huyen is a brilliant teacher.", "Real-world ML engineering insights.", "Essential for ML engineers."]
    },
    {
        "title": "Practical MLOps",
        "author": "Noah Gift", "price": 749.0, "rating": 4.5,
        "category": "mlops", "stock": 35,
        "description": "Hands-on MLOps covering CI/CD pipelines, model deployment, monitoring and cloud platform integrations.",
        "reviews": ["Practical and hands-on.", "Good CI/CD coverage for ML.", "Cloud platform examples are helpful.", "Great for ML engineers."]
    },
    {
        "title": "Building Machine Learning Powered Applications",
        "author": "Emmanuel Ameisen", "price": 699.0, "rating": 4.6,
        "category": "mlops", "stock": 30,
        "description": "End-to-end guide to building ML products from idea to production with iterative development.",
        "reviews": ["Best product-focused ML book.", "Ameisen bridges research and engineering.", "Real product building insights.", "Essential for ML product builders."]
    },
    {
        "title": "Machine Learning Engineering",
        "author": "Andriy Burkov", "price": 749.0, "rating": 4.6,
        "category": "mlops", "stock": 35,
        "description": "Comprehensive guide to ML engineering covering data collection, model training, deployment and monitoring.",
        "reviews": ["Best ML engineering overview.", "Burkov is consistently excellent.", "Practical and comprehensive.", "Great complement to his 100-page book."]
    },
    {
        "title": "Introducing MLOps",
        "author": "Mark Treveil", "price": 649.0, "rating": 4.4,
        "category": "mlops", "stock": 30,
        "description": "Introduction to MLOps principles covering model lifecycle, governance, monitoring and team workflows.",
        "reviews": ["Good intro to MLOps concepts.", "Business and technical balance.", "Covers governance well.", "Good starting point for MLOps."]
    },
    {
        "title": "ML Engineering with Python",
        "author": "Andrew McMahon", "price": 799.0, "rating": 4.5,
        "category": "mlops", "stock": 30,
        "description": "Hands-on ML engineering using Python covering pipelines, testing, deployment and monitoring with real projects.",
        "reviews": ["Very hands-on approach.", "Python code is clean.", "McMahon covers real engineering.", "Great for practising ML engineers."]
    },

    # ── 15. COMPUTER VISION (7 books) ─────────────────────────────────────────
    {
        "title": "Computer Vision: Algorithms and Applications",
        "author": "Richard Szeliski", "price": 1199.0, "rating": 4.7,
        "category": "computer vision", "stock": 20,
        "description": "Comprehensive CV textbook covering classical and deep learning approaches. Free second edition available online.",
        "reviews": ["The CV textbook.", "Comprehensive coverage of CV.", "Free online too.", "Essential for CV researchers."]
    },
    {
        "title": "Programming Computer Vision with Python",
        "author": "Jan Erik Solem", "price": 599.0, "rating": 4.4,
        "category": "computer vision", "stock": 40,
        "description": "Practical computer vision with Python covering image processing, recognition, 3D reconstruction and AR.",
        "reviews": ["Great practical CV book.", "Python examples are clear.", "Good starting point for CV.", "Accessible and hands-on."]
    },
    {
        "title": "Learning OpenCV 4",
        "author": "Adrian Kaehler", "price": 849.0, "rating": 4.6,
        "category": "computer vision", "stock": 30,
        "description": "Comprehensive OpenCV guide covering image processing, camera calibration, object detection and deep learning.",
        "reviews": ["Best OpenCV book.", "Kaehler knows OpenCV deeply.", "Comprehensive and practical.", "Essential for OpenCV developers."]
    },
    {
        "title": "Deep Learning for Vision Systems",
        "author": "Mohamed Elgendy", "price": 799.0, "rating": 4.6,
        "category": "computer vision", "stock": 30,
        "description": "Deep learning applied to CV covering CNNs, object detection, segmentation and generative models.",
        "reviews": ["Best deep learning for CV book.", "Elgendy explains CNNs brilliantly.", "Great code examples.", "Perfect bridge between DL and CV."]
    },
    {
        "title": "Multiple View Geometry in Computer Vision",
        "author": "Richard Hartley", "price": 1099.0, "rating": 4.7,
        "category": "computer vision", "stock": 15,
        "description": "Mathematical foundation for 3D computer vision covering epipolar geometry, camera models and reconstruction.",
        "reviews": ["The 3D vision bible.", "Hartley and Zisserman is the gold standard.", "Dense but essential for 3D vision.", "Essential for robotics and AR."]
    },
    {
        "title": "Practical Deep Learning for Cloud and Mobile",
        "author": "Anirudh Koul", "price": 849.0, "rating": 4.5,
        "category": "computer vision", "stock": 25,
        "description": "Deploying CV models to cloud, mobile and edge devices covering TensorFlow Lite and CoreML.",
        "reviews": ["Best deployment-focused CV book.", "Covers mobile deployment well.", "Koul has great industry experience.", "Essential for CV deployment."]
    },
    {
        "title": "Hands-On Image Processing with Python",
        "author": "Sandipan Dey", "price": 749.0, "rating": 4.4,
        "category": "computer vision", "stock": 30,
        "description": "Practical image processing with Python covering filtering, segmentation, feature extraction and deep learning.",
        "reviews": ["Comprehensive image processing book.", "Dey covers breadth of topics.", "Python code is clear.", "Good reference for image processing."]
    },
]


def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def create_database():
    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ── Drop all tables ───────────────────────────────────────────────────────
    for table in ["returns", "order_items", "orders",
                  "stock", "users", "products", "conversation_memory"]:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")

    # ── Users ─────────────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role          TEXT NOT NULL DEFAULT 'user',
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── Products ──────────────────────────────────────────────────────────────
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

    # ── Stock ─────────────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE stock (
            product_id INTEGER PRIMARY KEY,
            quantity   INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    # ── Orders ────────────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE orders (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id   TEXT UNIQUE NOT NULL,
            user_id    INTEGER NOT NULL,
            status     TEXT NOT NULL DEFAULT 'confirmed',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # ── Order Items ───────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE order_items (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id   TEXT UNIQUE NOT NULL,
            product_id INTEGER NOT NULL,
            quantity   INTEGER NOT NULL DEFAULT 1,
            price      REAL NOT NULL,
            FOREIGN KEY (order_id)   REFERENCES orders(order_id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    # ── Returns ───────────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE returns (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            return_id  TEXT UNIQUE NOT NULL,
            order_id   TEXT NOT NULL,
            user_id    INTEGER NOT NULL,
            reason     TEXT,
            status     TEXT NOT NULL DEFAULT 'initiated',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (user_id)  REFERENCES users(id)
        )
    """)

    # ── Conversation Memory ───────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE conversation_memory (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            user_id    INTEGER,
            role       TEXT NOT NULL,
            content    TEXT NOT NULL,
            intent     TEXT,
            category   TEXT,
            budget     REAL,
            product_id INTEGER,
            order_id   TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── Seed users ────────────────────────────────────────────────────────────
    default_users = [
        ("admin", hash_password("admin123"), "admin"),
        ("user1", hash_password("user123"),  "user"),
        ("user2", hash_password("user123"),  "user"),
        ("user3", hash_password("user123"),  "user"),
    ]
    cursor.executemany(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        default_users
    )

    # ── Seed products + stock ─────────────────────────────────────────────────
    for book in books:
        cursor.execute("""
            INSERT INTO products
            (title, author, price, rating, category, description, reviews)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            book["title"], book["author"], book["price"],
            book["rating"], book["category"],
            book["description"], json.dumps(book["reviews"])
        ))
        pid = cursor.lastrowid
        cursor.execute(
            "INSERT INTO stock (product_id, quantity) VALUES (?, ?)",
            (pid, book["stock"])
        )

    conn.commit()
    conn.close()

    # ── Print summary ─────────────────────────────────────────────────────────
    cats = {}
    for b in books:
        cats[b["category"]] = cats.get(b["category"], 0) + 1

    print(f"\n✅ Database created at: {DB_PATH}")
    print(f"✅ {len(books)} books seeded across {len(cats)} categories")
    print(f"✅ {len(default_users)} users seeded\n")
    print("📚 Books per category:")
    for cat, count in sorted(cats.items()):
        print(f"   {cat:<28} {count} books")
    print("\n👤 Default accounts:")
    print("   admin  / admin123  → role: admin")
    print("   user1  / user123   → role: user")
    print("   user2  / user123   → role: user")
    print("   user3  / user123   → role: user")


if __name__ == "__main__":
    create_database()