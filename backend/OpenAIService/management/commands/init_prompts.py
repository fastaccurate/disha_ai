from django.core.management.base import BaseCommand
from OpenAIService.models import PromptTemplate, LLMConfigName
from OpenAIService.repositories import ValidPromptTemplates


class Command(BaseCommand):
    help = "Initialize all ValidPromptTemplates in the database if not already existing"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing prompt templates before creating new ones",
        )
        parser.add_argument(
            "--clear-llm-configs",
            action="store_true",
            help="Clear existing LLM configs before creating new ones",
        )

    def handle(self, *args, **options):
        # Step 1: Create/ensure default LLM config exists
        self.stdout.write("Checking default LLM configuration...")

        if options.get("clear_llm_configs"):
            self.stdout.write("Clearing existing LLM configs...")
            LLMConfigName.objects.all().delete()
            self.stdout.write(self.style.WARNING("Existing LLM configs cleared!"))

        default_llm_config, llm_created = LLMConfigName.objects.get_or_create(
            name="sample_llm_config"
        )

        if llm_created:
            self.stdout.write(
                self.style.SUCCESS("  ✓ Created default LLM config: sample_llm_config")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("  ✓ Default LLM config already exists: sample_llm_config")
            )

        self.stdout.write("")

        # Step 2: Create prompt templates
        if options["clear"]:
            self.stdout.write("Clearing existing prompt templates...")
            PromptTemplate.objects.all().delete()
            self.stdout.write(self.style.WARNING("Existing prompt templates cleared!"))

        self.stdout.write("Initializing prompt templates...")

        # Get all valid prompt template names from ValidPromptTemplates
        valid_prompts = ValidPromptTemplates.get_all_valid_prompts()

        created_count = 0
        updated_count = 0
        skipped_count = 0

        # Define default prompts for each template
        prompt_configs = {
            ValidPromptTemplates.GRAMMAR_PROCESSOR: {
                "system_prompt": """You are an expert English grammar evaluator. Your task is to analyze the given text and identify grammatical errors.

For each error you find, provide:
1. The incorrect text
2. The correct version
3. The type of grammatical error (e.g., Subject-Verb Agreement, Tense Error, Article Usage, etc.)
4. A brief reason explaining why it's incorrect

Be thorough but fair in your evaluation. Focus on significant errors that affect clarity and correctness.""",
                "user_prompt": """Please analyze the following text for grammatical errors:

Text: {{user_answer}}

Return your analysis as a JSON array of errors.""",
                "required_kwargs": ["user_answer"],
            },
            ValidPromptTemplates.COHERENCE_PROCESSOR: {
                "system_prompt": """You are an expert in evaluating text coherence and logical flow. Your task is to assess how well the answer addresses the question, how complete it is, and how logically structured it is.

Evaluate the following aspects:
1. Completeness: Does the answer fully address all parts of the question? (yes/no)
2. Relevance: How relevant is the answer to the question? (high/medium/low)
3. Logical: How logical and well-structured is the flow of ideas? (high/medium/low)
4. Overall: Overall coherence assessment (high/medium/low)

For each aspect, provide a reason explaining your evaluation.""",
                "user_prompt": """Question: {{question}}

User's Answer: {{user_answer}}

Evaluate the coherence of this answer.""",
                "required_kwargs": ["question", "user_answer"],
            },
        }

        for prompt_name in valid_prompts:
            try:
                # Check if prompt already exists
                prompt, created = PromptTemplate.objects.get_or_create(
                    name=prompt_name,
                    defaults={
                        "system_prompt_template": prompt_configs.get(
                            prompt_name, {}
                        ).get(
                            "system_prompt",
                            f"System prompt for {prompt_name} - Please configure this prompt.",
                        ),
                        "user_prompt_template": prompt_configs.get(prompt_name, {}).get(
                            "user_prompt",
                            f"User prompt for {prompt_name} - Please configure this prompt.",
                        ),
                        "required_kwargs": prompt_configs.get(prompt_name, {}).get(
                            "required_kwargs", []
                        ),
                        "type": "evaluation",
                    },
                )

                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f"  ✓ Created prompt template: {prompt_name}")
                    )
                    created_count += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  ⚠ Prompt template already exists: {prompt_name}"
                        )
                    )
                    skipped_count += 1

                # Link prompt to default LLM config if not already linked
                if default_llm_config not in prompt.llm_config_names.all():
                    prompt.llm_config_names.add(default_llm_config)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"    → Linked to sample_llm_config"
                        )
                    )
                    updated_count += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"  ✗ Error creating prompt template {prompt_name}: {str(e)}"
                    )
                )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Prompt template initialization complete!"
            )
        )
        self.stdout.write(f"  - Created: {created_count}")
        self.stdout.write(f"  - Skipped (already exists): {skipped_count}")
        self.stdout.write(f"  - Linked to LLM config: {updated_count}")
        self.stdout.write("")

        if created_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    "⚠️  Note: Default prompts have been created. You may want to customize them in Django admin or via code."
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ All prompt templates are linked to 'sample_llm_config'"
            )
        )
        self.stdout.write("")
        self.stdout.write(
            self.style.WARNING(
                "⚠️  Important: Configure LLM settings in llm_configs/sample_llm_config.yaml for production use."
            )
        )
