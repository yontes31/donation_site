from django.core.management.base import BaseCommand
from locations.models import DonationCategory

class Command(BaseCommand):
    help = 'Adds initial donation categories'

    def handle(self, *args, **options):
        categories = [
            {
                'name_hebrew': 'ביגוד',
                'name_english': 'clothing',
                'keywords': 'בגדים יד שניה, חנות בגדים משומשים, תרומות בגדים'
            },
            {
                'name_hebrew': 'מזון',
                'name_english': 'food',
                'keywords': 'בנק מזון, תרומות מזון, חבילות מזון'
            },
            {
                'name_hebrew': 'ריהוט',
                'name_english': 'furniture',
                'keywords': 'רהיטים יד שניה, תרומות רהיטים, מחסן רהיטים'
            },
            {
                'name_hebrew': 'צעצועים',
                'name_english': 'toys',
                'keywords': 'צעצועים יד שניה, תרומות צעצועים, משחקים'
            },
            {
                'name_hebrew': 'ספרים',
                'name_english': 'books',
                'keywords': 'ספרים יד שניה, תרומות ספרים, ספריה'
            }
        ]

        for category_data in categories:
            category, created = DonationCategory.objects.get_or_create(
                name_hebrew=category_data['name_hebrew'],
                defaults={
                    'name_english': category_data['name_english'],
                    'keywords': category_data['keywords']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name_hebrew}'))
            else:
                self.stdout.write(f'Category already exists: {category.name_hebrew}')