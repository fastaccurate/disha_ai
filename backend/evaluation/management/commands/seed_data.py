from django.core.management.base import BaseCommand
from evaluation.models import Question, AssessmentGenerationConfig
import datetime


class Command(BaseCommand):
    help = "Seeds the database with sample questions and assessment configurations"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing data before seeding",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("Clearing existing data...")
            Question.objects.all().delete()
            AssessmentGenerationConfig.objects.all().delete()
            self.stdout.write(self.style.WARNING("Existing data cleared!"))

        self.stdout.write("Creating sample questions...")
        self.create_questions()

        self.stdout.write("Creating assessment configurations...")
        self.create_assessment_configs()

        self.stdout.write(self.style.SUCCESS("✅ Database seeded successfully!"))

    def create_questions(self):
        """Create sample MCQ, MMCQ, and Subjective questions"""

        # MCQ Questions (Single Choice)
        mcq_questions = [
            {
                "question_data": {
                    "question": "What is the time complexity of binary search?",
                    "options": ["O(n)", "O(log n)", "O(n²)", "O(1)"],
                    "answer": 1,
                    "hint": "Think about how the search space is divided",
                },
                "answer_type": 0,
                "level": 1,
                "tags": ["algorithms", "binary-search", "complexity"],
            },
            {
                "question_data": {
                    "question": "Which data structure uses LIFO (Last In First Out) principle?",
                    "options": ["Queue", "Stack", "Array", "Tree"],
                    "answer": 1,
                },
                "answer_type": 0,
                "level": 1,
                "tags": ["data-structures", "stack"],
            },
            {
                "question_data": {
                    "question": "What does API stand for?",
                    "options": [
                        "Application Programming Interface",
                        "Advanced Programming Interface",
                        "Application Process Integration",
                        "Automated Programming Interface",
                    ],
                    "answer": 0,
                },
                "answer_type": 0,
                "level": 1,
                "tags": ["general", "api"],
            },
            {
                "question_data": {
                    "question": "Which of the following is NOT a Python data type?",
                    "options": ["List", "Dictionary", "Array", "Tuple"],
                    "answer": 2,
                    "hint": "Think about Python's built-in types",
                },
                "answer_type": 0,
                "level": 2,
                "tags": ["python", "data-types"],
            },
            {
                "question_data": {
                    "question": "What is the output of: print(2 ** 3)?",
                    "options": ["5", "6", "8", "9"],
                    "answer": 2,
                },
                "answer_type": 0,
                "level": 1,
                "tags": ["python", "operators"],
            },
        ]

        # MMCQ Questions (Multiple Choice - Multiple Answers)
        mmcq_questions = [
            {
                "question_data": {
                    "paragraph": "Consider the following programming paradigms:",
                    "questions": [
                        {
                            "question": "Which are object-oriented programming languages?",
                            "options": ["Java", "C", "Python", "Assembly"],
                            "answer": [0, 2],
                        },
                        {
                            "question": "Which languages support functional programming?",
                            "options": ["JavaScript", "Python", "C", "Haskell"],
                            "answer": [0, 1, 3],
                        },
                        {
                            "question": "Which are compiled languages?",
                            "options": ["Python", "Java", "C", "JavaScript"],
                            "answer": [1, 2],
                        },
                    ],
                },
                "answer_type": 1,
                "level": 2,
                "tags": ["programming-languages", "paradigms"],
            },
            {
                "question_data": {
                    "paragraph": "Software Development Life Cycle (SDLC) phases:",
                    "questions": [
                        {
                            "question": "Which phases involve customer interaction?",
                            "options": [
                                "Requirements",
                                "Design",
                                "Testing",
                                "Deployment",
                            ],
                            "answer": [0, 2, 3],
                        },
                        {
                            "question": "Which phases involve writing code?",
                            "options": [
                                "Requirements",
                                "Implementation",
                                "Testing",
                                "Maintenance",
                            ],
                            "answer": [1, 2, 3],
                        },
                    ],
                },
                "answer_type": 1,
                "level": 2,
                "tags": ["sdlc", "software-engineering"],
            },
        ]

        # Subjective Questions
        subjective_questions = [
            {
                "question_data": {
                    "question": "Explain the difference between a process and a thread in operating systems. Provide examples of when you would use one over the other.",
                    "hints": [
                        "Consider memory allocation",
                        "Think about communication between them",
                        "Consider creation overhead",
                    ],
                },
                "answer_type": 2,
                "level": 2,
                "tags": ["operating-systems", "concurrency"],
            },
            {
                "question_data": {
                    "question": "Describe what RESTful APIs are and explain the principles that make an API RESTful. Give examples of HTTP methods and their purposes.",
                    "hints": [
                        "Think about statelessness",
                        "Consider HTTP methods",
                        "Think about resource representation",
                    ],
                },
                "answer_type": 2,
                "level": 2,
                "tags": ["api", "rest", "web-development"],
            },
            {
                "question_data": {
                    "question": "What is the difference between SQL and NoSQL databases? When would you choose one over the other?",
                    "hints": [
                        "Consider data structure",
                        "Think about scalability",
                        "Consider ACID properties",
                    ],
                },
                "answer_type": 2,
                "level": 2,
                "tags": ["databases", "sql", "nosql"],
            },
        ]

        # Create all questions
        created_count = 0
        for q_data in mcq_questions + mmcq_questions + subjective_questions:
            question, created = Question.objects.get_or_create(
                question_data=q_data["question_data"],
                defaults={
                    "answer_type": q_data["answer_type"],
                    "level": q_data["level"],
                    "tags": q_data["tags"],
                    "time_required": datetime.timedelta(minutes=2),
                },
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f"  ✓ Created {created_count} questions"))

    def create_assessment_configs(self):
        """Create sample assessment configurations"""

        # Get question IDs by type
        mcq_questions = list(
            Question.objects.filter(answer_type=0).values_list("id", flat=True)
        )
        mmcq_questions = list(
            Question.objects.filter(answer_type=1).values_list("id", flat=True)
        )
        subjective_questions = list(
            Question.objects.filter(answer_type=2).values_list("id", flat=True)
        )

        configs = [
            {
                "assessment_name": "technical_screening_mcq",
                "assessment_display_name": "Technical Screening - MCQ",
                "assessment_generation_class_name": "QuestionIdsBasedAssessment",
                "test_duration": datetime.timedelta(minutes=30),
                "enabled": True,
                "kwargs": {
                    "total_number": len(mcq_questions),
                    "subcategories": [
                        {
                            "section_name": "Technical Knowledge",
                            "question_ids": mcq_questions,
                            "number": len(mcq_questions),
                            "skippable": True,
                        }
                    ],
                },
                "display_data": {
                    "instructions": "This is a technical screening test with multiple choice questions. You have 30 minutes to complete all questions. Each question has only one correct answer."
                },
            },
            {
                "assessment_name": "comprehensive_assessment",
                "assessment_display_name": "Comprehensive Technical Assessment",
                "assessment_generation_class_name": "QuestionIdsBasedAssessment",
                "test_duration": datetime.timedelta(hours=1),
                "enabled": True,
                "kwargs": {
                    "total_number": len(mcq_questions)
                    + len(mmcq_questions)
                    + len(subjective_questions),
                    "subcategories": [
                        {
                            "section_name": "Multiple Choice",
                            "question_ids": mcq_questions,
                            "number": len(mcq_questions),
                            "skippable": True,
                        },
                        {
                            "section_name": "Multiple Select",
                            "question_ids": mmcq_questions,
                            "number": len(mmcq_questions),
                            "skippable": True,
                        },
                        {
                            "section_name": "Written Response",
                            "question_ids": subjective_questions,
                            "number": len(subjective_questions),
                            "skippable": False,
                        },
                    ],
                },
                "display_data": {
                    "instructions": "This comprehensive assessment includes multiple choice, multiple select, and written response questions. You have 1 hour to complete the test. Written responses are mandatory."
                },
            },
            {
                "assessment_name": "quick_aptitude_test",
                "assessment_display_name": "Quick Aptitude Test",
                "assessment_generation_class_name": "QuestionPoolBasedAssessment",
                "test_duration": datetime.timedelta(minutes=15),
                "enabled": True,
                "kwargs": {
                    "total_number": min(3, len(mcq_questions)),
                    "subcategories": [
                        {
                            "section_name": "Aptitude",
                            "question_pool": mcq_questions,
                            "number": min(3, len(mcq_questions)),
                            "skippable": True,
                        }
                    ],
                },
                "display_data": {
                    "instructions": "A quick 15-minute aptitude test with randomly selected questions. Answer as many as you can!"
                },
            },
        ]

        created_count = 0
        for config_data in configs:
            config, created = AssessmentGenerationConfig.objects.get_or_create(
                assessment_name=config_data["assessment_name"],
                defaults={
                    "assessment_display_name": config_data["assessment_display_name"],
                    "assessment_generation_class_name": config_data[
                        "assessment_generation_class_name"
                    ],
                    "test_duration": config_data["test_duration"],
                    "enabled": config_data["enabled"],
                    "kwargs": config_data["kwargs"],
                    "display_data": config_data["display_data"],
                },
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"  ✓ Created {created_count} assessment configurations")
        )
