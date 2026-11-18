import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.contrib.auth.models import User
from learning.models import Skill, Resource, LearningPath, PathItem, PlacementQuestion
from learning.admin import setup_instructor_group
from learning.recommender import PathRecommender


PLACEMENT_QUESTION_BANKS = {
    "Data Science & Machine Learning": [
        ("Which Python library is commonly used for tabular data?", ["Pandas", "Django", "Flask", "Pillow"], 0, 1),
        ("Which statistic is least affected by a few extreme values?", ["Mean", "Median", "Range", "Variance"], 1, 1),
        ("What does a missing-value check help identify?", ["Null entries", "Duplicate imports", "File extensions", "Model weights"], 0, 1),
        ("Why split data into training and test sets?", ["Measure generalization on unseen data", "Increase row count", "Remove all outliers", "Guarantee perfect accuracy"], 0, 2),
        ("Which pandas method gives common summary statistics?", [".describe()", ".compile()", ".render()", ".migrate()"], 0, 2),
        ("What is a common way to encode a nominal category?", ["One-hot encoding", "Min-max scaling", "Gradient descent", "Interpolation"], 0, 2),
        ("What does overfitting usually mean?", ["The model memorizes training patterns and generalizes poorly", "The model has no parameters", "The data has no labels", "The test set is larger"], 0, 2),
        ("Why use cross-validation?", ["Estimate performance across multiple data splits", "Replace feature engineering", "Increase target leakage", "Avoid a validation metric"], 0, 3),
        ("When is precision especially important?", ["When false positives are costly", "When every class is equally common", "When the model has no predictions", "When the data is unlabelled"], 0, 3),
        ("What is data leakage?", ["Training uses information unavailable at prediction time", "A dataset is stored as CSV", "A model is exported", "A feature has a long name"], 0, 3),
    ],
    "Full-Stack Web Development": [
        ("What does HTML primarily define?", ["Page structure", "Database indexes", "Server memory", "Network routes"], 0, 1),
        ("Which JavaScript declaration is block-scoped and reassignable?", ["let", "const", "static", "final"], 0, 1),
        ("What is the main purpose of CSS?", ["Style and layout web content", "Execute SQL", "Compile Python", "Manage DNS"], 0, 1),
        ("What does a React component return to describe UI?", ["JSX", "A database row", "A TCP packet", "A migration"], 0, 2),
        ("Which HTTP method is conventionally used to retrieve a resource?", ["GET", "POST", "PATCH", "DELETE"], 0, 2),
        ("Why use a database transaction?", ["Keep a set of related writes atomic", "Compress images", "Render CSS", "Cache browser history"], 0, 2),
        ("What does an API response status 404 indicate?", ["The requested resource was not found", "The request succeeded", "Authentication succeeded", "The server restarted"], 0, 2),
        ("Why should a password be hashed on the server?", ["Avoid storing the original password", "Make the password reversible", "Send it in a URL", "Reduce database normalization"], 0, 3),
        ("What does an index commonly improve?", ["Lookup performance for selected queries", "Password strength", "CSS specificity", "Image resolution"], 0, 3),
        ("What is a key benefit of separating frontend and backend APIs?", ["Independent interfaces communicate through a defined contract", "The database can be removed", "The browser can access server secrets", "Testing becomes impossible"], 0, 3),
    ],
    "Python Web Development with Django": [
        ("Which Django file commonly maps URL patterns to views?", ["urls.py", "models.py", "admin.py", "apps.py"], 0, 1),
        ("What does a Django model usually represent?", ["Database structure and behavior", "A browser stylesheet", "A network socket", "A test report"], 0, 1),
        ("Which command applies existing migrations?", ["python manage.py migrate", "python manage.py collectstatic", "python manage.py shell", "python manage.py startapp"], 0, 1),
        ("What is a Django QuerySet?", ["A lazy database query interface", "A template file", "A user session cookie", "A CSS selector"], 0, 2),
        ("What does a ForeignKey represent?", ["A many-to-one relationship", "A static file path", "A URL redirect", "A password hash"], 0, 2),
        ("What is a serializer commonly used for in DRF?", ["Validate and transform API data", "Compile templates", "Create database indexes", "Serve JavaScript bundles"], 0, 2),
        ("What does IsAuthenticated enforce?", ["The request must have an authenticated user", "The request must use HTTPS", "The response must be JSON", "The user must be a superuser"], 0, 2),
        ("Why should a migration be reviewed before production?", ["It changes the database schema or data", "It updates browser bookmarks", "It changes a Git branch", "It minifies JavaScript"], 0, 3),
        ("How can an API endpoint scope records to their owner?", ["Filter by request.user in the queryset", "Trust a user_id from the request body", "Disable authentication", "Return every record and hide it in React"], 0, 3),
        ("What is the purpose of select_related for a ForeignKey?", ["Fetch related rows in the same SQL query", "Delete related rows", "Create a new migration", "Serialize passwords"], 0, 3),
    ],
}

PLACEMENT_QUESTION_BANKS.update({
    "Python Programming": [
        ("How does Python mark the start of an indented code block?", ["Indentation", "Curly braces", "A begin keyword", "A semicolon"], 0, 1),
        ("Which built-in collection is mutable?", ["tuple", "list", "str", "frozenset"], 1, 1),
        ("What does a dictionary store?", ["Ordered statements", "Only numeric values", "Key-value pairs", "Functions only"], 2, 1),
        ("What does range(2, 6) produce?", ["2 through 6 inclusive", "2, 3, 4, 5", "1 through 6", "Only 2 and 6"], 1, 2),
        ("What is the purpose of a function parameter?", ["To pass input into a function", "To import a module", "To catch exceptions", "To create a package"], 0, 2),
        ("When is a class __init__ method normally called?", ["When a module is imported", "When an instance is created", "When a loop ends", "When an exception is raised"], 1, 2),
        ("Which construct handles an expected runtime exception?", ["if/else", "for/in", "try/except", "with/as"], 2, 2),
        ("Why are mutable default arguments risky?", ["They are converted to strings", "The same object can be reused across calls", "They cannot be passed by keyword", "They disable type checking"], 1, 3),
        ("What does yield do in a generator function?", ["Returns every value at once", "Creates a class", "Raises StopIteration immediately", "Produces values lazily"], 3, 3),
        ("What is a key benefit of a context manager for a file?", ["It sorts file contents", "It handles cleanup when the block exits", "It encrypts the file", "It converts text to JSON"], 1, 3),
    ],
    "Data Structures & Algorithms": [
        ("Which structure follows last-in, first-out order?", ["Queue", "Heap", "Stack", "Graph"], 2, 1),
        ("Which structure follows first-in, first-out order?", ["Queue", "Stack", "Tree", "Set"], 0, 1),
        ("What precondition does standard binary search require?", ["The values are unique", "The data is sorted", "The data is a linked list", "The array length is even"], 1, 1),
        ("Why track visited vertices during graph traversal?", ["To sort vertices alphabetically", "To increase recursion depth", "To create weighted edges", "To avoid processing vertices repeatedly"], 3, 2),
        ("What is the time complexity of accessing the k-th node in a singly linked list?", ["O(n)", "O(1)", "O(log n)", "O(n log n)"], 0, 2),
        ("What is the typical search complexity in a balanced binary search tree?", ["O(n^2)", "O(log n)", "O(1) worst case", "O(2^n)"], 1, 2),
        ("Dynamic programming is especially useful when a problem has what properties?", ["Sorted input and constant memory", "Only one possible solution", "Overlapping subproblems and optimal substructure", "No repeated computation"], 2, 2),
        ("Which traversal finds a shortest path in an unweighted graph?", ["Breadth-first search", "Depth-first search", "In-order traversal", "Heap sort"], 0, 3),
        ("What is the average lookup time for a well-distributed hash table?", ["O(n log n)", "O(log n)", "O(n)", "O(1)"], 3, 3),
        ("Which condition is required for Dijkstra's standard shortest-path algorithm?", ["All edge weights are nonnegative", "The graph is a tree", "Every vertex has degree two", "The graph is unweighted"], 0, 3),
    ],
    "JavaScript Essentials": [
        ("Which declaration is block-scoped and can be reassigned?", ["var", "let", "const", "static"], 1, 1),
        ("What does const prevent?", ["Changing properties of an object", "Reassigning the variable binding", "Reading the variable", "Using the value in a function"], 1, 1),
        ("What does === compare without doing?", ["Checking object identity", "Comparing strings", "Type coercion", "Comparing numbers"], 2, 1),
        ("What does Array.prototype.map return?", ["A new array of mapped values", "The original array only", "A boolean", "A generator"], 0, 2),
        ("What is a closure?", ["A way to stop a browser tab", "A function retaining access to its lexical scope", "A promise that rejects", "A class without methods"], 1, 2),
        ("Where are promise callbacks typically queued relative to timer callbacks?", ["In the microtask queue", "In the CSS queue", "In the network stack only", "In the call stack permanently"], 0, 2),
        ("What does Promise.all do when one input rejects?", ["Silently removes that input", "Resolves with undefined", "Rejects with that failure", "Retries every promise"], 2, 2),
        ("What does an async function always return?", ["A DOM element", "A Promise", "A generator", "A callback"], 1, 3),
        ("What does the nullish coalescing operator ?? test?", ["Whether a value is null or undefined", "Whether a value is any falsy value", "Whether two objects are identical", "Whether a promise is settled"], 0, 3),
        ("What does a browser's same-origin policy restrict by default?", ["HTML element nesting", "CSS class naming", "Cross-origin script access to data", "Local variable declarations"], 2, 3),
    ],
    "Frontend with React": [
        ("What does a React component return to describe the UI?", ["JSX or React elements", "A SQL query", "A CSS file", "An HTTP status"], 0, 1),
        ("How should a component receive parent-provided data?", ["Through props", "Through DOM globals", "Through CSS variables only", "Through an SQL join"], 0, 1),
        ("Why should list elements have stable keys?", ["To encrypt their content", "To help React identify items between renders", "To force every item to remount", "To sort the list"], 1, 1),
        ("Which hook stores local component state?", ["useMemo", "useState", "useId", "useDebugValue"], 1, 2),
        ("What should an effect cleanup function do?", ["Return JSX", "Undo subscriptions or other external work", "Change props", "Run before every browser paint unconditionally"], 1, 2),
        ("What is a controlled input in React?", ["An input whose value is driven by React state", "An input hidden from the browser", "An input that cannot be edited", "An input rendered only on the server"], 0, 2),
        ("What does lifting state up usually mean?", ["Moving shared state to a common parent", "Moving CSS into a child", "Putting all state in local storage", "Replacing props with direct DOM access"], 0, 2),
        ("When do state updates based on previous state benefit from an updater function?", ["When they depend on the previous state value", "Only when the value is a string", "Only during initial render", "When the component has no props"], 0, 3),
        ("Which is a rule of hooks?", ["Call hooks conditionally inside loops", "Call hooks at the top level of React components or custom hooks", "Call hooks from event handlers only", "Call hooks after returning JSX"], 1, 3),
        ("Why should an effect's reactive dependencies be complete?", ["To ensure the effect uses current values and reruns when they change", "To make the component render only once", "To stop state updates", "To reduce the bundle by removing imports"], 0, 3),
    ],
    "HTML & CSS": [
        ("What does semantic HTML primarily improve?", ["Meaning and structure for browsers and assistive technology", "Database consistency", "JavaScript execution speed", "Image compression"], 0, 1),
        ("Which element is intended for a page's primary navigation links?", ["<nav>", "<span>", "<b>", "<br>"], 0, 1),
        ("What does the CSS box model describe?", ["Content, padding, border, and margin", "HTML headings and lists", "Network request headers", "Font file formats"], 0, 1),
        ("What is Flexbox especially useful for?", ["One-dimensional layout and alignment", "Database transactions", "Image encoding", "Server-side routing"], 0, 2),
        ("What does CSS Grid provide?", ["Two-dimensional row and column layout", "A JavaScript event queue", "An HTML form validator", "A color palette generator"], 0, 2),
        ("What does a media query commonly enable?", ["Conditional styling for viewport or device features", "Database filtering", "JavaScript module loading", "Server-side rendering"], 0, 2),
        ("Why should an image have meaningful alternative text?", ["To communicate its relevant content to users who cannot see it", "To increase its resolution", "To load it from a CDN", "To set its CSS width"], 0, 2),
        ("Which CSS unit is relative to the root element's font size?", ["px", "rem", "vh", "pt"], 1, 3),
        ("Why use a mobile-first responsive strategy?", ["Start with small-screen constraints, then enhance for larger screens", "Disable media queries", "Force every element to a fixed width", "Avoid semantic markup"], 0, 3),
        ("What is a benefit of using CSS custom properties?", ["Reusable values that can be changed and scoped", "Automatic HTML validation", "Server-side data storage", "Replacing all selectors"], 0, 3),
    ],
    "SQL & Databases": [
        ("Which SQL statement retrieves rows from a table?", ["SELECT", "INSERT", "ALTER", "DROP"], 0, 1),
        ("What does a primary key guarantee?", ["A row can be uniquely identified", "A table has no indexes", "Every value is encrypted", "Rows are always sorted"], 0, 1),
        ("Which clause filters rows before grouping?", ["WHERE", "HAVING", "ORDER BY", "LIMIT"], 0, 1),
        ("What does an INNER JOIN return?", ["Rows with matching join values in both sources", "Every possible row pair", "Only unmatched rows", "A table's schema"], 0, 2),
        ("What is the purpose of GROUP BY?", ["Group rows for aggregate calculations", "Rename a database", "Delete duplicate tables", "Lock a transaction"], 0, 2),
        ("What does a foreign key represent?", ["A relationship referencing a key in another table", "A password for the database", "A query execution plan", "A database backup"], 0, 2),
        ("Which property does a transaction's atomicity provide?", ["All operations succeed together or roll back together", "Queries always run in parallel", "Indexes are automatically removed", "Rows are always returned in order"], 0, 2),
        ("What is a common tradeoff of adding an index?", ["Faster reads for some queries but extra storage and write cost", "All writes become free", "The database stops using constraints", "Every query becomes constant time"], 0, 3),
        ("Why normalize relational data?", ["Reduce unwanted duplication and update anomalies", "Make every table contain one row", "Avoid all joins", "Remove primary keys"], 0, 3),
        ("What should be considered before adding a composite index?", ["Query predicates and column ordering", "The UI theme color", "The database username length", "Whether the table has a title"], 0, 3),
    ],
    "Git & GitHub": [
        ("What does git status show?", ["The working tree and staging state", "The remote server's CPU use", "Only deleted branches", "The repository license"], 0, 1),
        ("What does git commit create?", ["A recorded snapshot in repository history", "A remote pull request automatically", "A new database", "A deleted working tree"], 0, 1),
        ("What does the staging area allow you to do?", ["Choose which changes enter the next commit", "Encrypt the entire repository", "Install dependencies", "Change the remote URL"], 0, 1),
        ("What is a branch commonly used for?", ["Developing a line of work separately", "Compressing all commits", "Changing file permissions globally", "Replacing a remote"], 0, 2),
        ("What does git fetch do?", ["Downloads remote references and objects without merging them", "Deletes all local commits", "Creates a commit", "Publishes a release"], 0, 2),
        ("What is a merge conflict?", ["Git cannot automatically reconcile overlapping changes", "A branch has no name", "A commit has no message", "A remote is unreachable forever"], 0, 2),
        ("What is the purpose of a pull request?", ["Propose and review changes before integrating them", "Replace version control", "Store passwords", "Run a database migration"], 0, 2),
        ("Why avoid committing secrets to a public repository?", ["They can be copied and abused even after removal from the latest version", "Git automatically changes the secret", "Secrets increase image size", "GitHub requires public credentials"], 0, 3),
        ("What is a useful CI workflow trigger?", ["A push or pull request event", "A CSS selector", "A database primary key", "A browser bookmark"], 0, 3),
        ("When is reverting a commit safer than rewriting shared history?", ["When the commit is already shared with collaborators", "When no commit exists", "Only on a new empty repository", "When changing a local variable"], 0, 3),
    ],
    "Docker & Deployment": [
        ("What is a container image?", ["A packaged filesystem and metadata used to create containers", "A running process only", "A virtual network cable", "A database row"], 0, 1),
        ("What is a container?", ["An isolated running instance created from an image", "A Dockerfile comment", "A registry account", "A YAML list"], 0, 1),
        ("What is a Dockerfile used for?", ["Defining steps to build an image", "Listing running processes", "Declaring database tables", "Creating a Git branch"], 0, 1),
        ("Why pass configuration through environment variables?", ["Keep environment-specific settings out of the image", "Bake secrets permanently into source code", "Replace container networking", "Make all files executable"], 0, 2),
        ("What does a Docker volume provide?", ["Persistent storage managed separately from a container's writable layer", "A CPU limit", "A source-code linter", "A public DNS record"], 0, 2),
        ("What is Docker Compose for?", ["Defining and running multi-container applications", "Building React components", "Editing Git commits", "Generating SQL indexes"], 0, 2),
        ("Why use a multi-stage Docker build?", ["Separate build dependencies from the final runtime image", "Run one container per source line", "Disable image layers", "Avoid setting a base image"], 0, 2),
        ("Why should production images avoid unnecessary packages?", ["Reduce image size and attack surface", "Increase startup dependencies", "Store runtime secrets in layers", "Force a public registry"], 0, 3),
        ("What should a health check indicate?", ["Whether a service is ready to handle its intended work", "The developer's GitHub rank", "The size of an image tag", "Whether a Dockerfile has comments"], 0, 3),
        ("What is a safe approach to container secrets?", ["Inject secrets at runtime from a protected secret store", "Commit them into the image", "Put them in a public label", "Print them in build logs"], 0, 3),
    ],
    "Generative AI & LLMs": [
        ("What does a language model generate?", ["A probability-based sequence of tokens", "A relational schema automatically", "A guaranteed factual answer", "A network connection"], 0, 1),
        ("What is a prompt?", ["Input instructions or context supplied to a model", "A database index", "A model's source code", "A tokenization library only"], 0, 1),
        ("What does tokenization do?", ["Splits text into model-processing units", "Encrypts a prompt", "Stores text in a vector database", "Measures network latency"], 0, 1),
        ("What is an embedding?", ["A numeric vector representing semantic features of data", "A CSS layout rule", "A model password", "A database transaction"], 0, 2),
        ("What is retrieval-augmented generation intended to do?", ["Provide retrieved context to ground a model response", "Guarantee zero hallucinations", "Train a model from scratch", "Replace authentication"], 0, 2),
        ("Why chunk documents before retrieval?", ["Fit useful passages into retrieval and context limits", "Make every chunk identical", "Remove metadata permanently", "Convert vectors back to text"], 0, 2),
        ("What does temperature generally influence in text generation?", ["Randomness or diversity of sampled outputs", "The model's training dataset size", "The API key's expiration", "The vector database schema"], 0, 2),
        ("Why evaluate an LLM system on representative examples?", ["Measure quality and regressions against intended use", "Prove every response is correct", "Avoid logging any failures", "Remove the need for human review"], 0, 3),
        ("What is a risk of sending private data to an external model API?", ["Data may leave the application's trust boundary", "Embeddings stop being numeric", "The API can no longer return JSON", "The model becomes deterministic"], 0, 3),
        ("What should an agent workflow do before a high-impact external action?", ["Validate the proposed action and apply authorization or human review", "Assume model text is trusted code", "Disable audit logging", "Skip tool input validation"], 0, 3),
    ],
    "Web Security Basics": [
        ("What is the main risk of cross-site scripting?", ["Untrusted script runs in a user's browser context", "A database table is normalized", "A request is compressed", "A CSS file is cached"], 0, 1),
        ("What is a common defense against SQL injection?", ["Parameterized queries", "String concatenation", "Putting SQL in a URL", "Hiding errors in the browser"], 0, 1),
        ("What does authentication establish?", ["The identity of a user or client", "The user's permissions for every action", "The database's table order", "The source of a CSS rule"], 0, 1),
        ("What does authorization determine?", ["Whether an identified user may perform an action", "How a password is hashed", "Whether a page uses HTML", "Which DNS server is closest"], 0, 2),
        ("Why use CSRF protection for cookie-authenticated state changes?", ["Browsers may attach cookies to forged cross-site requests", "Cookies are always public", "It prevents every XSS attack", "It replaces server-side permission checks"], 0, 2),
        ("Why store passwords using a dedicated password hash?", ["To make recovery of the original password computationally difficult", "To decrypt passwords faster", "To avoid using unique salts", "To reuse the password as a session token"], 0, 2),
        ("What is the principle of least privilege?", ["Grant only the access needed for a task", "Give every user administrator rights", "Keep all data publicly readable", "Disable audit logs"], 0, 2),
        ("Why validate authorization on the server for every protected object?", ["Client-side checks can be bypassed", "The browser cannot send IDs", "HTTPS hides all request data", "CSS controls database permissions"], 0, 3),
        ("What should an application do with untrusted output in HTML?", ["Use context-appropriate escaping or safe rendering", "Insert it as raw script", "Trust it if it came from a database", "Encode it only in CSS"], 0, 3),
        ("What is a security benefit of HTTPS?", ["It protects data in transit against eavesdropping and tampering", "It prevents all application bugs", "It encrypts data at rest automatically", "It replaces authentication"], 0, 3),
    ],
})

ADDITIONAL_SKILL_CATALOG = {
    "Python Programming": {
        "category": "Programming",
        "description": "Build a strong Python foundation, from syntax and functions to object-oriented programming and practical projects.",
        "resources": [
            ("Python Syntax and Your First Programs", "https://docs.python.org/3/tutorial/introduction.html", 1, 35, "Learn expressions, variables, strings, and the interactive interpreter."),
            ("Control Flow and Functions", "https://docs.python.org/3/tutorial/controlflow.html", 1, 45, "Practice conditions, loops, function definitions, and parameters."),
            ("Lists, Tuples, Sets, and Dictionaries", "https://docs.python.org/3/tutorial/datastructures.html", 1, 45, "Choose and use Python's built-in collection types."),
            ("Modules, Packages, and Imports", "https://docs.python.org/3/tutorial/modules.html", 2, 35, "Organize reusable code into modules and packages."),
            ("Classes and Object-Oriented Python", "https://docs.python.org/3/tutorial/classes.html", 2, 55, "Use classes, inheritance, and instance methods."),
            ("Exceptions, Files, and a CLI Project", "https://docs.python.org/3/tutorial/errors.html", 3, 60, "Handle errors and apply Python fundamentals in a small command-line program."),
        ],
    },
    "Data Structures & Algorithms": {
        "category": "DSA & Interviews",
        "description": "Practice core data structures, algorithmic thinking, complexity analysis, and interview-style problem solving.",
        "resources": [
            ("Algorithm Analysis and Big-O", "https://www.geeksforgeeks.org/analysis-of-algorithms-set-1-asymptotic-analysis/", 1, 40, "Compare time and space growth using asymptotic notation."),
            ("Arrays and Strings", "https://www.geeksforgeeks.org/array-data-structure-guide/", 1, 45, "Solve traversal, two-pointer, and sliding-window problems."),
            ("Linked Lists", "https://www.geeksforgeeks.org/linked-list-data-structure/", 1, 45, "Understand nodes, links, traversal, and common list operations."),
            ("Stacks and Queues", "https://www.geeksforgeeks.org/stack-data-structure/", 2, 45, "Apply LIFO and FIFO structures to parsing and scheduling problems."),
            ("Sorting and Binary Search", "https://www.geeksforgeeks.org/sorting-algorithms/", 2, 55, "Compare sorting strategies and use binary search on ordered data."),
            ("Trees and Binary Search Trees", "https://www.geeksforgeeks.org/binary-tree-data-structure/", 2, 60, "Traverse trees and reason about search-tree operations."),
            ("Graph Traversal", "https://www.geeksforgeeks.org/graph-data-structure-and-algorithms/", 3, 60, "Model relationships with graphs and implement BFS and DFS."),
            ("Dynamic Programming Patterns", "https://www.geeksforgeeks.org/dynamic-programming/", 3, 70, "Recognize overlapping subproblems and build memoized solutions."),
        ],
    },
    "JavaScript Essentials": {
        "category": "Programming",
        "description": "Learn modern JavaScript syntax, functions, objects, asynchronous code, and browser APIs.",
        "resources": [
            ("JavaScript Language Introduction", "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Introduction", 1, 30, "Understand the language, runtimes, and how JavaScript is used on the web."),
            ("Grammar, Types, and Variables", "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Grammar_and_types", 1, 45, "Work with values, operators, declarations, and type conversion."),
            ("Control Flow and Loops", "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Control_flow_and_error_handling", 1, 45, "Use conditionals, loops, and structured exception handling."),
            ("Functions and Scope", "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Functions", 2, 50, "Build reusable functions and understand closures and scope."),
            ("Objects and Classes", "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Working_with_objects", 2, 50, "Model application data with objects and prototypes."),
            ("Promises and Async Programming", "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Using_promises", 3, 55, "Coordinate asynchronous work using promises and async patterns."),
        ],
    },
    "Frontend with React": {
        "category": "Web Development",
        "description": "Create component-based user interfaces with React, state, routing concepts, and reliable API integration.",
        "resources": [
            ("React Quick Start", "https://react.dev/learn", 1, 45, "Build a first component and learn the core React mental model."),
            ("Your First Component", "https://react.dev/learn/your-first-component", 1, 35, "Compose a user interface from reusable components."),
            ("Passing Data with Props", "https://react.dev/learn/passing-props-to-a-component", 1, 35, "Pass and render data through component props."),
            ("State and Event Handling", "https://react.dev/learn/state-a-components-memory", 2, 45, "Make interfaces interactive with state and event handlers."),
            ("Managing State", "https://react.dev/learn/managing-state", 2, 55, "Choose where state belongs and share it between components."),
            ("Synchronizing with Effects and APIs", "https://react.dev/learn/synchronizing-with-effects", 3, 55, "Load and synchronize external data while handling effect cleanup."),
        ],
    },
    "HTML & CSS": {
        "category": "Web Development",
        "description": "Build accessible, responsive pages with semantic HTML, modern CSS layout, and browser-tested design.",
        "resources": [
            ("Structuring Content with HTML", "https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Structuring_content", 1, 40, "Use semantic elements to create well-structured web pages."),
            ("HTML Forms and User Input", "https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Forms", 1, 45, "Build forms with appropriate controls and native validation."),
            ("CSS Styling Basics", "https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Styling_basics", 1, 45, "Apply selectors, the cascade, color, typography, and box-model rules."),
            ("CSS Flexbox Layout", "https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/CSS_layout/Flexbox", 2, 45, "Arrange responsive one-dimensional layouts with Flexbox."),
            ("CSS Grid Layout", "https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/CSS_layout/Grids", 2, 50, "Create two-dimensional layouts using CSS Grid."),
            ("Responsive Design and Accessibility", "https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/CSS_layout/Responsive_Design", 3, 55, "Adapt interfaces to screen sizes and accessibility needs."),
        ],
    },
    "SQL & Databases": {
        "category": "Databases",
        "description": "Design relational schemas and write efficient SQL with joins, constraints, indexes, and transactions.",
        "resources": [
            ("Relational Tables and Basic SQL", "https://www.postgresql.org/docs/current/tutorial-sql.html", 1, 40, "Create and query relational data with core SQL statements."),
            ("Filtering, Sorting, and Aggregation", "https://www.postgresql.org/docs/current/tutorial-agg.html", 1, 45, "Summarize records using aggregate functions and grouping."),
            ("Joining Related Tables", "https://www.postgresql.org/docs/current/tutorial-join.html", 2, 45, "Combine related records with inner and outer joins."),
            ("Constraints and Data Integrity", "https://www.postgresql.org/docs/current/ddl-constraints.html", 2, 50, "Use primary keys, foreign keys, and checks to protect valid data."),
            ("Indexes and Query Performance", "https://www.postgresql.org/docs/current/indexes.html", 3, 55, "Understand indexes and their effect on query workloads."),
            ("Transactions and Concurrency", "https://www.postgresql.org/docs/current/tutorial-transactions.html", 3, 45, "Use transactions to keep related database operations consistent."),
        ],
    },
    "Git & GitHub": {
        "category": "Tools",
        "description": "Manage source history, branches, collaboration, and review workflows with Git and GitHub.",
        "resources": [
            ("Version Control Fundamentals", "https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control", 1, 30, "Learn why version control matters and how Git records changes."),
            ("Recording Changes and Commits", "https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository", 1, 40, "Stage files, inspect diffs, and create clear commits."),
            ("Branches and Merging", "https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell", 2, 45, "Create branches and integrate work safely."),
            ("Working with Remote Repositories", "https://git-scm.com/book/en/v2/Git-Basics-Working-with-Remotes", 2, 40, "Connect local repositories to remote collaboration workflows."),
            ("GitHub Pull Requests", "https://docs.github.com/en/pull-requests/collaborating-with-pull-requests", 3, 45, "Open, review, and merge pull requests with useful feedback."),
            ("GitHub Actions Fundamentals", "https://docs.github.com/en/actions/about-github-actions/understanding-github-actions", 3, 50, "Understand workflows, jobs, and automated repository checks."),
        ],
    },
    "Docker & Deployment": {
        "category": "DevOps & Cloud",
        "description": "Package applications in containers, configure multi-service environments, and prepare deployments.",
        "resources": [
            ("Docker Concepts and First Steps", "https://docs.docker.com/get-started/introduction/", 1, 35, "Understand images, containers, and the Docker workflow."),
            ("Build an Image from a Dockerfile", "https://docs.docker.com/get-started/docker-concepts/building-images/", 1, 45, "Package an application into a reproducible container image."),
            ("Run and Manage Containers", "https://docs.docker.com/engine/containers/run/", 1, 40, "Start containers and configure ports, environment, and lifecycle."),
            ("Persist Data with Volumes", "https://docs.docker.com/engine/storage/volumes/", 2, 40, "Keep application data beyond a container's lifecycle."),
            ("Multi-Service Apps with Compose", "https://docs.docker.com/compose/", 2, 55, "Define and run an application stack with Docker Compose."),
            ("Publish Images and Deployment Workflow", "https://docs.docker.com/reference/cli/docker/image/push/", 3, 50, "Tag and publish images as part of a deployment workflow."),
        ],
    },
    "Generative AI & LLMs": {
        "category": "Generative AI",
        "description": "Explore language-model fundamentals, prompting, embeddings, retrieval-augmented generation, and evaluation.",
        "resources": [
            ("LLM Course: Transformer Models", "https://huggingface.co/learn/llm-course/chapter1/1", 1, 45, "Learn the core ideas behind transformer language models."),
            ("Using Transformers", "https://huggingface.co/learn/llm-course/chapter2/1", 1, 50, "Load and use pretrained models through the Transformers ecosystem."),
            ("Prompting and Text Generation", "https://huggingface.co/docs/transformers/main_classes/text_generation", 2, 45, "Configure generation and reason about prompt inputs and outputs."),
            ("Text Embeddings", "https://platform.openai.com/docs/guides/embeddings", 2, 45, "Represent text as vectors for semantic similarity and retrieval."),
            ("Retrieval-Augmented Generation", "https://developers.openai.com/api/docs/guides/retrieval", 3, 60, "Retrieve relevant sources and ground generated answers in context."),
            ("Evaluate and Improve LLM Applications", "https://huggingface.co/learn/cookbook/llm_judge", 3, 55, "Use repeatable evaluation to inspect model application quality."),
        ],
    },
    "Web Security Basics": {
        "category": "Security",
        "description": "Recognize common web vulnerabilities and apply secure defaults for authentication, input, and data access.",
        "resources": [
            ("OWASP Top 10 Overview", "https://owasp.org/www-project-top-ten/", 1, 35, "Survey the most important categories of web application risk."),
            ("Django Security Guidance", "https://docs.djangoproject.com/en/stable/topics/security/", 1, 45, "Apply Django guidance for hosts, HTTPS, cookies, and user input."),
            ("Cross-Site Scripting Prevention", "https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html", 2, 45, "Understand output encoding and safe handling of untrusted content."),
            ("SQL Injection Prevention", "https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html", 2, 40, "Use parameterized queries and avoid unsafe query construction."),
            ("Authentication and Session Security", "https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html", 3, 45, "Protect account flows, credentials, and session lifecycle."),
            ("Web Security Testing Guide", "https://owasp.org/www-project-web-security-testing-guide/", 3, 60, "Plan a responsible checklist for testing a web application you own."),
        ],
    },
}


def seed_placement_questions():
    for skill_name, questions in PLACEMENT_QUESTION_BANKS.items():
        skill = Skill.objects.filter(name=skill_name).first()
        if not skill:
            continue
        for index, (question_text, options, correct_option, difficulty) in enumerate(questions):
            if len(options) != 4:
                raise ValueError(f"{skill_name} placement question must have four options.")
            rotation = index % len(options)
            rotated_options = options[rotation:] + options[:rotation]
            PlacementQuestion.objects.update_or_create(
                skill=skill,
                question_text=question_text,
                defaults={
                    "options": rotated_options,
                    "correct_option": (correct_option - rotation) % len(options),
                    "difficulty": difficulty,
                    "is_active": True,
                },
            )


def seed_additional_skills():
    for skill_name, details in ADDITIONAL_SKILL_CATALOG.items():
        skill, _ = Skill.objects.update_or_create(
            name=skill_name,
            defaults={
                "category": details["category"],
                "description": details["description"],
            },
        )
        for title, url, difficulty, duration, description in details["resources"]:
            Resource.objects.update_or_create(
                title=title,
                skill=skill,
                defaults={
                    "url": url,
                    "resource_type": "article",
                    "difficulty": difficulty,
                    "duration_minutes": duration,
                    "description": description,
                },
            )


def seed():
    print("Seeding database with skills and resources...")

    # 1. Setup instructor group
    setup_instructor_group()
    print("[OK] Instructor group configured.")

    # 2. Create superuser if not present
    admin_user, admin_created = User.objects.get_or_create(
        username="admin",
        defaults={
            "email": "admin@example.com",
            "is_staff": True,
            "is_superuser": True,
        }
    )
    if admin_created:
        admin_user.set_password("AdminPass123!")
        admin_user.save()
        print("[OK] Created superuser: admin / AdminPass123!")

    # 3. Data Science & Machine Learning Skill
    ds_skill, _ = Skill.objects.get_or_create(
        name="Data Science & Machine Learning",
        defaults={
            "description": "Comprehensive journey from Python basics, EDA, to Machine Learning pipelines and real-world projects.",
            "category": "Data Science",
        }
    )

    ds_resources = [
        # Beginner (difficulty=1)
        {
            "title": "Python for Data Science Foundations",
            "url": "https://www.coursera.org/learn/python-for-applied-data-science-ai",
            "resource_type": "course",
            "difficulty": 1,
            "duration_minutes": 60,
            "description": "Variables, loops, data structures, and fundamental Python logic for data workflows.",
        },
        {
            "title": "Data Handling & Cleaning with Pandas and NumPy",
            "url": "https://realpython.com/pandas-dataframe/",
            "resource_type": "article",
            "difficulty": 1,
            "duration_minutes": 45,
            "description": "Clean missing data, reshape dataframes, and transform columns for statistical modeling.",
        },
        {
            "title": "Exploratory Data Analysis (EDA) Techniques",
            "url": "https://www.youtube.com/watch?v=-o3AxdVcUtQ",
            "resource_type": "video",
            "difficulty": 1,
            "duration_minutes": 50,
            "description": "Univariate, bivariate analysis, outlier detection, and statistical summarization.",
        },
        # Intermediate (difficulty=2)
        {
            "title": "Data Visualization with Matplotlib, Seaborn & Plotly",
            "url": "https://realpython.com/python-matplotlib-guide/",
            "resource_type": "article",
            "difficulty": 2,
            "duration_minutes": 40,
            "description": "Craft publication-grade visual storytelling with heatmaps, pairplots, and interactive charts.",
        },
        {
            "title": "Supervised Machine Learning: Regression & Classification",
            "url": "https://www.coursera.org/specializations/machine-learning-introduction",
            "resource_type": "course",
            "difficulty": 2,
            "duration_minutes": 90,
            "description": "Linear regression, Logistic regression, Decision Trees, and Random Forests with Scikit-learn.",
        },
        {
            "title": "Crop Yield Predictor - Real-World ML Project",
            "url": "https://github.com/Infant-Joshva",
            "resource_type": "project",
            "difficulty": 2,
            "duration_minutes": 120,
            "description": "Hands-on project predicting crop yields from agricultural features and historical climate datasets.",
        },
        # Advanced (difficulty=3)
        {
            "title": "Deep Learning: Neural Networks with TensorFlow & Keras",
            "url": "https://www.coursera.org/specializations/deep-learning",
            "resource_type": "course",
            "difficulty": 3,
            "duration_minutes": 120,
            "description": "Build multi-layer perceptrons, tune activation functions, and evaluate loss metrics.",
        },
        {
            "title": "Employee Attrition ML Pipeline & Web Deployment",
            "url": "https://github.com/Infant-Joshva",
            "resource_type": "project",
            "difficulty": 3,
            "duration_minutes": 150,
            "description": "End-to-end production pipeline with feature engineering, model selection, and Streamlit dashboard.",
        },
    ]

    for item in ds_resources:
        Resource.objects.update_or_create(
            title=item["title"],
            skill=ds_skill,
            defaults=item,
        )

    # 4. Full-Stack Web Development Skill
    fs_skill, _ = Skill.objects.get_or_create(
        name="Full-Stack Web Development",
        defaults={
            "description": "Master modern full-stack development with TypeScript, React, RESTful architectures, and database modeling.",
            "category": "Web Development",
        }
    )

    fs_resources = [
        # Beginner (difficulty=1)
        {
            "title": "TypeScript Fundamentals & Modern JavaScript (ES6+)",
            "url": "https://www.typescriptlang.org/docs/handbook/intro.html",
            "resource_type": "article",
            "difficulty": 1,
            "duration_minutes": 45,
            "description": "Type annotations, interfaces, generics, async/await, and TypeScript compiler basics.",
        },
        {
            "title": "React Architecture & Component Hierarchy with Vite",
            "url": "https://react.dev/learn",
            "resource_type": "course",
            "difficulty": 1,
            "duration_minutes": 60,
            "description": "Component lifecycles, JSX syntax, props, modular CSS, and fast developer environments.",
        },
        # Intermediate (difficulty=2)
        {
            "title": "Advanced React: Hooks, Context & State Management",
            "url": "https://www.youtube.com/watch?v=LlvBzyy-558",
            "resource_type": "video",
            "difficulty": 2,
            "duration_minutes": 55,
            "description": "Custom hooks, useReducer, context providers, and performance optimizations.",
        },
        {
            "title": "REST API Architecture, Axios Interceptors & JWT Authentication",
            "url": "https://www.freecodecamp.org/news/how-to-build-a-rest-api/",
            "resource_type": "article",
            "difficulty": 2,
            "duration_minutes": 60,
            "description": "Design clean HTTP REST endpoints, handle token authorization headers, and manage sessions.",
        },
        # Advanced (difficulty=3)
        {
            "title": "Relational Data Modeling with Foreign Keys & Migration Strategies",
            "url": "https://docs.djangoproject.com/en/stable/topics/db/models/",
            "resource_type": "course",
            "difficulty": 3,
            "duration_minutes": 80,
            "description": "Design normalized schema relationships, execute zero-downtime migrations, and optimize queries.",
        },
        {
            "title": "End-to-End Full-Stack Capstone Application",
            "url": "https://github.com/",
            "resource_type": "project",
            "difficulty": 3,
            "duration_minutes": 180,
            "description": "Build, test, containerize, and deploy a full-stack dashboard with real-time analytics.",
        },
    ]

    for item in fs_resources:
        Resource.objects.update_or_create(
            title=item["title"],
            skill=fs_skill,
            defaults=item,
        )

    # 5. Python Web Development with Django
    django_skill, _ = Skill.objects.get_or_create(
        name="Python Web Development with Django",
        defaults={
            "description": "From Django basics to REST APIs, relational models, sessions, cookies, and production dashboards.",
            "category": "Backend Engineering",
        }
    )

    django_resources = [
        {
            "title": "Django Setup, Architecture & Project Configuration (Unit I)",
            "url": "https://docs.djangoproject.com/en/stable/intro/tutorial01/",
            "resource_type": "article",
            "difficulty": 1,
            "duration_minutes": 35,
            "description": "Virtual environments, startproject, startapp, and settings.py configuration.",
        },
        {
            "title": "Django URL Routing, Views & Template Inheritance (Units II, III)",
            "url": "https://www.youtube.com/watch?v=F5mRW0jo-U4",
            "resource_type": "video",
            "difficulty": 1,
            "duration_minutes": 50,
            "description": "Function and class-based views, URL routing, base.html template inheritance and context data.",
        },
        {
            "title": "Django Forms, CSRF Protection & Input Validation (Unit IV)",
            "url": "https://docs.djangoproject.com/en/stable/topics/forms/",
            "resource_type": "article",
            "difficulty": 2,
            "duration_minutes": 45,
            "description": "Form classes, CSRF token security, clean methods, and dynamic error messages.",
        },
        {
            "title": "Relational Models, Foreign Keys & Django Admin (Unit V)",
            "url": "https://docs.djangoproject.com/en/stable/topics/db/models/",
            "resource_type": "course",
            "difficulty": 2,
            "duration_minutes": 60,
            "description": "ForeignKey relationships, reverse lookups, ModelAdmin customization, and Instructor group permissions.",
        },
        {
            "title": "Django Authentication, Sessions & Cookies (Unit VI)",
            "url": "https://docs.djangoproject.com/en/stable/topics/auth/",
            "resource_type": "course",
            "difficulty": 2,
            "duration_minutes": 55,
            "description": "UserCreationForm, login_required decorator, session management, and persistent cookies.",
        },
        {
            "title": "Django REST Framework (DRF) & JWT Authentication",
            "url": "https://www.django-rest-framework.org/",
            "resource_type": "course",
            "difficulty": 3,
            "duration_minutes": 90,
            "description": "Build high-performance REST APIs with ModelSerializers, Token authentication, and permissions.",
        },
    ]

    for item in django_resources:
        Resource.objects.update_or_create(
            title=item["title"],
            skill=django_skill,
            defaults=item,
        )

    seed_additional_skills()
    seed_placement_questions()
    print("[OK] Seeded skills, resources, and placement diagnostics successfully.")

if __name__ == "__main__":
    seed()
