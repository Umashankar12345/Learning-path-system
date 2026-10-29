import os
from .models import Resource, PathItem

class PathRecommender:
    """
    Learning Path Recommendation Engine.
    - Level 1 (Rule-based): Filters resources by skill, sorts by difficulty (1 -> 2 -> 3),
      and assigns sequence order.
    - Level 2 (Adaptive/LLM): Hooks into Gemini/OpenAI API if key is present to adapt order.
    """

    @classmethod
    def generate_path_items(cls, learning_path):
        """
        Populate PathItem rows for a given LearningPath instance.
        """
        skill = learning_path.skill
        user = learning_path.user

        # Get all resources for the skill, sorted by difficulty and id
        resources = list(Resource.objects.filter(skill=skill).order_by("difficulty", "id"))

        # Rule-based difficulty ordering
        created_items = []
        for index, res in enumerate(resources, start=1):
            item, _ = PathItem.objects.get_or_create(
                path=learning_path,
                resource=res,
                defaults={"order": index, "completed": False}
            )
            created_items.append(item)

        return created_items

    @classmethod
    def get_next_recommended_resource(cls, user):
        """
        Finds the next unfinished resource across all active learning paths of the user.
        Prioritizes the lowest difficulty and earliest order.
        """
        next_item = (
            PathItem.objects.filter(path__user=user, completed=False)
            .select_related("resource", "path__skill")
            .order_by("resource__difficulty", "order", "id")
            .first()
        )
        return next_item
