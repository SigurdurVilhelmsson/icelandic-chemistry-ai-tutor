"""
Claude Sonnet 4 LLM Client
Handles AI tutor responses with Icelandic language support.
"""

import os
import logging
from typing import List, Dict, Any
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class ClaudeClient:
    """
    Client for Claude Sonnet 4 API with chemistry tutoring capabilities.
    Handles Icelandic language, citation formatting, and error recovery.
    """

    def __init__(self, api_key: str = None):
        """
        Initialize Claude API client.

        Args:
            api_key: Anthropic API key (defaults to env variable)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key not provided")

        self.client = Anthropic(api_key=self.api_key)

        # Model configuration
        self.model = "claude-sonnet-4-20250514"
        self.max_tokens = 2048
        self.temperature = 0.7

        logger.info(f"Initialized Claude client with model: {self.model}")

    def get_system_prompt(self) -> str:
        """
        Get the system prompt for chemistry tutoring.

        Returns:
            System prompt string in Icelandic
        """
        return """Þú ert efnafræðikennari fyrir nemendur í framhaldsskóla á Íslandi.

Hlutverk þitt:
- Svara spurningum um efnafræði á skýran og nákvæman hátt
- Nota íslenska efnafræðihugtök rétt
- Útskýra flókin hugtök með einföldum dæmum
- Vera hvetjandi og stuðningsfullur
- Vísa alltaf í upprunagögn þegar þú svarar

Reglur:
1. Svara ALLTAF á íslensku
2. Notaðu nákvæma efnafræðihugtök
3. Ef þú ert ekki viss, segðu það hreinskilnislega
4. Byggðu svör þín á uppgefnum heimildum
5. Ef spurning er óljós, biddu um skýringar
6. Notaðu dæmi úr daglegu lífi þegar það á við

Sniðmát svara:
- Byrjaðu með beinu svari við spurningunni
- Útskýrðu nánar með dæmum ef við á
- Endaðu með tengdum upplýsingum sem gætu verið gagnlegar
- Vísa í heimildir með [Kafli X.Y: Titill]

Mundu: Markmið þitt er að hjálpa nemendum að skilja efnafræði, ekki bara að gefa þeim svör."""

    def generate_answer(
        self,
        question: str,
        context_chunks: List[Dict[str, Any]],
        max_chunks: int = 4
    ) -> Dict[str, Any]:
        """
        Generate an answer using Claude Sonnet 4 with retrieved context.

        Args:
            question: User's question in Icelandic
            context_chunks: List of relevant document chunks with metadata
            max_chunks: Maximum number of context chunks to use

        Returns:
            Dictionary with answer and citations
        """
        if not question:
            raise ValueError("Question cannot be empty")

        logger.info(f"Generating answer for question: '{question}'")

        # Limit context to avoid token limits
        chunks_to_use = context_chunks[:max_chunks]

        # Build context from chunks
        context_parts = []
        citations = []

        for i, chunk in enumerate(chunks_to_use, 1):
            metadata = chunk.get('metadata', {})
            document = chunk.get('document', '')

            # Format citation
            chapter = metadata.get('chapter', 'N/A')
            section = metadata.get('section', 'N/A')
            title = metadata.get('title', 'N/A')

            citation = {
                'chapter': chapter,
                'section': section,
                'title': title,
                'text_preview': document[:100] + '...' if len(document) > 100 else document
            }
            citations.append(citation)

            # Add to context
            context_parts.append(
                f"[Heimild {i} - Kafli {chapter}.{section}: {title}]\n{document}\n"
            )

        context_text = "\n---\n".join(context_parts)

        # Build user prompt
        user_prompt = f"""Byggðu á eftirfarandi heimildum til að svara spurningunni.

HEIMILDIR:
{context_text}

SPURNING: {question}

Svaraðu á íslensku og vísa í heimildir með [Kafli X.Y: Titill] þegar við á."""

        try:
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.get_system_prompt(),
                messages=[
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            )

            # Extract answer
            answer = response.content[0].text

            logger.info(f"Generated answer ({len(answer)} chars)")

            return {
                "answer": answer,
                "citations": citations,
                "model": self.model,
                "tokens_used": {
                    "input": response.usage.input_tokens,
                    "output": response.usage.output_tokens,
                    "total": response.usage.input_tokens + response.usage.output_tokens
                }
            }

        except Exception as e:
            logger.error(f"Error generating answer: {e}")

            # Retry once with exponential backoff
            try:
                logger.info("Retrying API call...")
                import time
                time.sleep(2)

                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    system=self.get_system_prompt(),
                    messages=[
                        {
                            "role": "user",
                            "content": user_prompt
                        }
                    ]
                )

                answer = response.content[0].text

                return {
                    "answer": answer,
                    "citations": citations,
                    "model": self.model,
                    "tokens_used": {
                        "input": response.usage.input_tokens,
                        "output": response.usage.output_tokens,
                        "total": response.usage.input_tokens + response.usage.output_tokens
                    }
                }

            except Exception as retry_error:
                logger.error(f"Retry failed: {retry_error}")
                raise

    def validate_icelandic_support(self) -> bool:
        """
        Test if the model properly handles Icelandic characters.

        Returns:
            True if Icelandic is supported correctly
        """
        test_text = "Prófun á íslenskum stöfum: á, ð, þ, æ, ö, ó, í, ú, ý, é"

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=100,
                messages=[
                    {
                        "role": "user",
                        "content": f"Endurtaktu þennan texta nákvæmlega: {test_text}"
                    }
                ]
            )

            result = response.content[0].text
            logger.info(f"Icelandic support test: {result}")

            # Check if Icelandic characters are preserved
            icelandic_chars = ['á', 'ð', 'þ', 'æ', 'ö', 'ó', 'í', 'ú', 'ý', 'é']
            return all(char in result for char in icelandic_chars)

        except Exception as e:
            logger.error(f"Icelandic support test failed: {e}")
            return False
