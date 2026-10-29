import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.contrib.auth.models import User
from learning.models import Skill, Resource, LearningPath, PathItem
from learning.admin import setup_instructor_group
from learning.recommender import PathRecommender

def seed():
    print("Seeding database with skills and resources...")

    # 1. Setup instructor group
    setup_instructor_group()
    print("[OK] Instructor group configured.")

    # 2. Create demo users if not present
    demo_user, created = User.objects.get_or_create(
        username="learner_demo",
        defaults={
            "email": "learner@example.com",
            "first_name": "Alex",
            "last_name": "Learner",
        }
    )
    if created:
        demo_user.set_password("LearnerPass123!")
        demo_user.save()
        print(f"[OK] Created demo user: {demo_user.username}")

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

    # 6. Generate an initial learning path for the demo user
    demo_path, _ = LearningPath.objects.get_or_create(user=demo_user, skill=ds_skill)
    items = PathRecommender.generate_path_items(demo_path)

    # Mark the first 2 items completed to give realistic DB data
    if len(items) >= 2:
        items[0].mark_complete()
        items[0].rating = 5
        items[0].save()
        items[1].mark_complete()
        items[1].rating = 4
        items[1].save()

    print(f"[OK] Seeded skills, resources, and demo learning path with {len(items)} items.")

if __name__ == "__main__":
    seed()
