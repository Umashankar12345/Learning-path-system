import logging
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

def send_welcome_email(user):
    """
    Sends a warm welcome email upon signup.
    """
    subject = "Welcome to LearningPath.ai! 🚀"
    message = f"""Hi {user.first_name or user.username},

Welcome to LearningPath.ai! Your account has been created successfully.

Here is how to get the most out of your dashboard:
1. Explore our curated skill tracks (Data Science, Full-Stack Development, Django).
2. Enroll in your goal to get a difficulty-ranked curriculum (Beginner -> Intermediate -> Advanced).
3. Mark milestones complete to track your weekly learning hours and daily streaks!

Log in anytime at: http://localhost:5173/dashboard

Happy learning,
The LearningPath.ai Team
"""
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email] if user.email else ["learner@learningpath.ai"],
            fail_silently=True,
        )
        logger.info(f"Welcome email queued for user {user.username}")
    except Exception as e:
        logger.warning(f"Failed to send welcome email: {e}")


def send_streak_email(user, streak_days):
    """
    Celebrates milestone daily streaks (e.g., 3 days, 5 days, 7 days).
    """
    if streak_days not in (3, 5, 7, 14, 30):
        return

    subject = f"🔥 You're on a {streak_days}-day learning streak!"
    message = f"""Hey {user.first_name or user.username},

Incredible dedication! You have maintained an active study streak for {streak_days} consecutive days.

Keep the momentum going:
http://localhost:5173/dashboard

Best,
LearningPath.ai
"""
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email] if user.email else ["learner@learningpath.ai"],
            fail_silently=True,
        )
    except Exception as e:
        logger.warning(f"Failed to send streak email: {e}")


def send_completion_email(user, learning_path):
    """
    Congratulates learner on 100% path completion and provides certificate link.
    """
    subject = f"🎓 Congratulations! You completed '{learning_path.skill.name}'"
    message = f"""Outstanding work, {user.first_name or user.username}!

You have completed 100% of the milestones in the '{learning_path.skill.name}' curriculum.

Your official PDF Certificate of Completion is now ready to download from your dashboard:
http://localhost:5173/paths/{learning_path.id}

Keep advancing,
LearningPath.ai
"""
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email] if user.email else ["learner@learningpath.ai"],
            fail_silently=True,
        )
    except Exception as e:
        logger.warning(f"Failed to send path completion email: {e}")
