# messaging/management/__init__.py
# Empty file to make this a Python package

# messaging/management/commands/__init__.py
# Empty file to make this a Python package

# messaging/management/commands/setup_test_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from messaging.models import Message, Notification


class Command(BaseCommand):
    help = 'Creates test data for the messaging app'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=3,
            help='Number of test users to create',
        )
        parser.add_argument(
            '--messages',
            type=int,
            default=10,
            help='Number of test messages to create',
        )

    def handle(self, *args, **options):
        # Create test users
        users = []
        for i in range(options['users']):
            username = f'testuser{i+1}'
            email = f'test{i+1}@example.com'
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': f'Test{i+1}',
                    'last_name': 'User'
                }
            )
            
            if created:
                user.set_password('testpass123')
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Created user: {username}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'User already exists: {username}')
                )
            
            users.append(user)

        # Create test messages
        import random
        from django.utils import timezone
        from datetime import timedelta

        test_messages = [
            "Hello! How are you doing today?",
            "Did you see the latest news about Django?",
            "Let's meet up for coffee sometime!",
            "Thanks for your help with the project.",
            "What do you think about the new features?",
            "I'm working on something interesting.",
            "Hope you're having a great day!",
            "Can you review this code for me?",
            "The weather is really nice today.",
            "Let's catch up soon!",
        ]

        for i in range(options['messages']):
            sender = random.choice(users)
            receiver = random.choice([u for u in users if u != sender])
            content = random.choice(test_messages)
            
            # Create some messages in the past
            timestamp = timezone.now() - timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            message = Message.objects.create(
                sender=sender,
                receiver=receiver,
                content=content,
                timestamp=timestamp,
                read=random.choice([True, False])
            )
            
            # Create some replies (30% chance)
            if random.random() < 0.3:
                reply_content = random.choice([
                    "Thanks for the message!",
                    "I agree with you.",
                    "That's interesting!",
                    "Let me think about it.",
                    "Sounds good to me."
                ])
                
                Message.objects.create(
                    sender=receiver,
                    receiver=sender,
                    content=reply_content,
                    parent_message=message,
                    timestamp=timestamp + timedelta(minutes=random.randint(5, 60))
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {options["messages"]} test messages'
            )
        )
        
        # Display statistics
        total_users = User.objects.count()
        total_messages = Message.objects.count()
        total_notifications = Notification.objects.count()
        unread_messages = Message.objects.filter(read=False).count()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nDatabase Statistics:\n'
                f'- Total Users: {total_users}\n'
                f'- Total Messages: {total_messages}\n'
                f'- Total Notifications: {total_notifications}\n'
                f'- Unread Messages: {unread_messages}'
            )
        )