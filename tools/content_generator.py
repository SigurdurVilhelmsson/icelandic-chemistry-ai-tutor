#!/usr/bin/env python3
"""
Icelandic Chemistry Content Generator
Generates realistic chemistry content in Icelandic for testing the RAG system.
"""

import os
import sys
import argparse
import random
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

# Comprehensive Icelandic Chemistry Terminology
CHEMISTRY_TERMS = {
    # Basic concepts
    "atom": "atóm",
    "molecule": "sameind",
    "element": "frumefni",
    "compound": "efnasamband",
    "substance": "efni",
    "matter": "efni",
    "mass": "massi",
    "energy": "orka",
    "temperature": "hitastig",
    "pressure": "þrýstingur",

    # Atomic structure
    "electron": "rafeind",
    "proton": "róteind",
    "neutron": "nifteind",
    "nucleus": "kjarninn",
    "atomic number": "sætistala",
    "mass number": "massatala",
    "isotope": "samsæta",
    "electron shell": "rafeindaskel",
    "orbital": "sporbraut",
    "valence electron": "gildisrafeind",

    # Periodic table
    "periodic table": "lotukerfið",
    "period": "lota",
    "group": "flokkur",
    "metal": "málmur",
    "nonmetal": "málmlaus efni",
    "metalloid": "hálfmálmur",
    "noble gas": "göfugt loft",
    "halogen": "halógen",
    "alkali metal": "alkalímálmur",
    "alkaline earth metal": "jarðalkalímálmur",

    # Chemical bonding
    "bond": "tengi",
    "covalent bond": "samgildt tengi",
    "ionic bond": "jónatengi",
    "metallic bond": "málmtengi",
    "hydrogen bond": "vetnistengi",
    "polar": "skaut-",
    "nonpolar": "óskauta",
    "electronegativity": "rafsækni",
    "Lewis structure": "Lewis-bygging",
    "molecular geometry": "sameindarform",

    # States of matter
    "solid": "fast efni",
    "liquid": "vökvi",
    "gas": "loft",
    "plasma": "plasma",
    "phase": "ástand",
    "melting": "bræðsla",
    "freezing": "frysing",
    "boiling": "seyðing",
    "condensation": "þétting",
    "sublimation": "gufuhlaupsrót",
    "evaporation": "uppgufun",

    # Chemical reactions
    "reaction": "efnahvörf",
    "reactant": "hvarfefni",
    "product": "afurð",
    "catalyst": "hvati",
    "activation energy": "virkjunarorka",
    "endothermic": "varmadrægur",
    "exothermic": "varmamyndandi",
    "equilibrium": "jafnvægi",
    "rate": "hraði",

    # Reaction types
    "combustion": "brennsla",
    "synthesis": "myndun",
    "decomposition": "niðurbrot",
    "single replacement": "einföld útskipting",
    "double replacement": "tvöföld útskipting",
    "oxidation": "oxun",
    "reduction": "afoxun",
    "redox": "redox",

    # Stoichiometry
    "stoichiometry": "efnajöfnuður",
    "mole": "mól",
    "Avogadro's number": "tala Avogadros",
    "molar mass": "mólmassi",
    "limiting reactant": "takmarkandi hvarfefni",
    "excess reactant": "umframhvarfefni",
    "percent yield": "prósentuafkoma",
    "theoretical yield": "fræðileg afkoma",
    "actual yield": "raunveruleg afkoma",

    # Solutions
    "solution": "lausn",
    "solvent": "leysir",
    "solute": "leyst efni",
    "concentration": "styrkur",
    "molarity": "mólarleiki",
    "dilution": "þynning",
    "saturated": "mettaður",
    "solubility": "leysni",

    # Acids and bases
    "acid": "sýra",
    "base": "basi",
    "pH": "pH-gildi",
    "indicator": "vísir",
    "neutralization": "hlutleysingarefni",
    "salt": "salt",
    "buffer": "stuðpúði",

    # Thermochemistry
    "enthalpy": "varmainnihald",
    "entropy": "óreiða",
    "Gibbs free energy": "frjáls orka Gibbs",
    "heat": "varmi",
    "calorimetry": "varmareiknifræði",
    "specific heat": "eðlisvarmi",

    # Common elements
    "hydrogen": "vetni",
    "oxygen": "súrefni",
    "carbon": "kolefni",
    "nitrogen": "köfnunarefni",
    "chlorine": "klór",
    "sodium": "natríum",
    "calcium": "kalsíum",
    "iron": "járn",
    "copper": "kopar",
    "gold": "gull",
    "silver": "silfur",

    # Measurements
    "measurement": "mæling",
    "unit": "eining",
    "volume": "rúmmál",
    "density": "þéttleiki",
    "significant figures": "marktækir tölustafir",
    "precision": "nákvæmni",
    "accuracy": "áreiðanleiki",
}

# Topic structure for OpenStax Chemistry Chapters 1-5
CHAPTER_TOPICS = {
    1: {
        "title": "Lykilhugtök efnafræðinnar",
        "sections": [
            {"num": "1.1", "title": "Efnafræði í samtímanum", "topics": ["chemistry applications", "scientific method"]},
            {"num": "1.2", "title": "Ástand efnis", "topics": ["solid", "liquid", "gas", "phase transitions"]},
            {"num": "1.3", "title": "Eiginleikar efnis", "topics": ["physical properties", "chemical properties"]},
            {"num": "1.4", "title": "Mælingar", "topics": ["SI units", "measurement", "precision", "accuracy"]},
            {"num": "1.5", "title": "Stærðfræðileg úrvinnsla", "topics": ["significant figures", "scientific notation"]},
        ]
    },
    2: {
        "title": "Atóm, sameindir og jónir",
        "sections": [
            {"num": "2.1", "title": "Atómkenning efnanna", "topics": ["atomic theory", "Dalton"]},
            {"num": "2.2", "title": "Atómbygging", "topics": ["proton", "neutron", "electron", "nucleus"]},
            {"num": "2.3", "title": "Atómtákn og samsætur", "topics": ["isotope", "atomic number", "mass number"]},
            {"num": "2.4", "title": "Lotukerfið", "topics": ["periodic table", "periods", "groups"]},
            {"num": "2.5", "title": "Eiginleikar frumefna", "topics": ["metals", "nonmetals", "metalloids"]},
        ]
    },
    3: {
        "title": "Efnasamsetning",
        "sections": [
            {"num": "3.1", "title": "Jónatengi", "topics": ["ionic bond", "cation", "anion"]},
            {"num": "3.2", "title": "Samgild tengi", "topics": ["covalent bond", "molecular compounds"]},
            {"num": "3.3", "title": "Lewis-byggingarformúlur", "topics": ["Lewis structure", "valence electrons"]},
            {"num": "3.4", "title": "Formleg hleðsla og ómun", "topics": ["formal charge", "resonance"]},
            {"num": "3.5", "title": "Sameindarform", "topics": ["VSEPR", "molecular geometry", "polarity"]},
        ]
    },
    4: {
        "title": "Efnahvörf og efnajöfnuður",
        "sections": [
            {"num": "4.1", "title": "Efnahvörf", "topics": ["chemical equations", "balancing"]},
            {"num": "4.2", "title": "Gerðir efnahvarfa", "topics": ["synthesis", "decomposition", "combustion"]},
            {"num": "4.3", "title": "Efnajöfnuður", "topics": ["stoichiometry", "mole ratios"]},
            {"num": "4.4", "title": "Mól og massareikningar", "topics": ["mole", "molar mass", "Avogadro"]},
            {"num": "4.5", "title": "Takmarkandi hvarfefni", "topics": ["limiting reactant", "percent yield"]},
        ]
    },
    5: {
        "title": "Ítarlegri efnafræði",
        "sections": [
            {"num": "5.1", "title": "Varmaefnafræði", "topics": ["enthalpy", "heat", "calorimetry"]},
            {"num": "5.2", "title": "Lausnir", "topics": ["solutions", "concentration", "molarity"]},
            {"num": "5.3", "title": "Sýrur og basar", "topics": ["acid", "base", "pH"]},
            {"num": "5.4", "title": "Oxunar- og afoxunarkvörf", "topics": ["redox", "oxidation", "reduction"]},
        ]
    }
}

# Document type templates
DOCUMENT_TYPES = {
    "explanation": {
        "weight": 0.40,
        "min_words": 400,
        "max_words": 700,
        "prompt_style": "detailed conceptual explanation"
    },
    "example": {
        "weight": 0.30,
        "min_words": 300,
        "max_words": 600,
        "prompt_style": "worked example with step-by-step solution"
    },
    "problem": {
        "weight": 0.20,
        "min_words": 200,
        "max_words": 400,
        "prompt_style": "practice problem with hints"
    },
    "summary": {
        "weight": 0.10,
        "min_words": 300,
        "max_words": 500,
        "prompt_style": "concise summary and review"
    }
}

@dataclass
class GenerationConfig:
    """Configuration for content generation"""
    chapter: int
    section_num: str
    section_title: str
    topics: List[str]
    doc_type: str
    difficulty: str
    target_words: int

class ContentGenerator:
    """Generate realistic Icelandic chemistry content"""

    def __init__(self, api_key: Optional[str] = None, use_api: bool = True):
        """Initialize generator with optional API key"""
        self.use_api = use_api
        if use_api:
            try:
                import anthropic
                self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
                if not self.api_key:
                    raise ValueError("ANTHROPIC_API_KEY not found in environment")
                self.client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError("anthropic package not found. Install with: pip install anthropic")

        self.stats = {
            "generated": 0,
            "total_words": 0,
            "by_chapter": {},
            "by_type": {}
        }

    def generate_content(self, config: GenerationConfig) -> Dict:
        """Generate a single piece of content"""

        if self.use_api:
            content = self._generate_with_api(config)
        else:
            content = self._generate_template_content(config)

        # Create metadata
        metadata = self._create_metadata(config, content)

        # Update stats
        self._update_stats(config, metadata)

        return {
            "metadata": metadata,
            "content": content
        }

    def _generate_with_api(self, config: GenerationConfig) -> str:
        """Generate content using Claude API"""
        import anthropic

        # Build comprehensive prompt
        prompt = self._build_generation_prompt(config)

        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=0.8,  # Higher temperature for more variety
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            return message.content[0].text

        except Exception as e:
            print(f"API Error: {e}")
            return self._generate_template_content(config)

    def _build_generation_prompt(self, config: GenerationConfig) -> str:
        """Build detailed prompt for Claude API"""

        topics_str = ", ".join(config.topics)
        doc_type_info = DOCUMENT_TYPES[config.doc_type]

        # Get relevant terminology
        relevant_terms = self._get_relevant_terms(config.topics)
        terms_str = "\n".join([f"- {eng}: {ice}" for eng, ice in relevant_terms.items()])

        prompt = f"""Þú ert íslenskur efnafræðikennari. Búðu til efnafræðiefni á íslensku fyrir nemendur.

KAFLI: {config.chapter} - {CHAPTER_TOPICS[config.chapter]['title']}
HLUTI: {config.section_num} - {config.section_title}
EFNI: {topics_str}
TEGUND: {config.doc_type} ({doc_type_info['prompt_style']})
ERFIÐLEIKASTIG: {config.difficulty}
LENGD: {doc_type_info['min_words']}-{doc_type_info['max_words']} orð

ÍSLENSK HUGTÖK (notaðu rétt orðaforða):
{terms_str}

LEIÐBEININGAR:
1. Skrifaðu á réttu íslensku með réttum efnafræðihugtökum
2. Byrjaðu með: # Kafli {config.chapter}: {CHAPTER_TOPICS[config.chapter]['title']}
3. Síðan: ## {config.section_num} {config.section_title}
4. Notaðu undirfyrirsagnir (###) til að skipuleggja efnið
5. Láttu efnið vera fræðandi og nákvæmt
6. Bættu við dæmum þar sem við á
7. Notaðu punkta eða númeraða lista fyrir upptalningar
8. Ef um útreikninga er að ræða, sýndu skref fyrir skref
9. Vertu fjölbreyttur í málfari og nálgun
10. Láttu efnið vera raunhæft og gagnlegt fyrir nemendur

MIKILVÆGT:
- Notaðu BARA íslensk hugtök úr listanum hér að ofan
- Vertu nákvæm/ur með íslenskt mál
- Gerðu efnið læsilegt og skýrt
- Bættu við raun­heimsdæmum þar sem við á

Skrifaðu efnið BEINT - ekki neina innleiðingu eða útskýringu á því hvað þú ert að gera."""

        return prompt

    def _get_relevant_terms(self, topics: List[str]) -> Dict[str, str]:
        """Get relevant terminology for topics"""
        relevant = {}

        # Keywords to search for in topics
        keywords = []
        for topic in topics:
            keywords.extend(topic.lower().split())

        # Find matching terms
        for eng, ice in CHEMISTRY_TERMS.items():
            eng_words = eng.lower().split()
            if any(kw in eng_words or kw in eng.lower() for kw in keywords):
                relevant[eng] = ice

        # Always include some basic terms
        basics = ["atom", "molecule", "element", "compound", "reaction", "energy"]
        for term in basics:
            if term in CHEMISTRY_TERMS:
                relevant[term] = CHEMISTRY_TERMS[term]

        return relevant

    def _generate_template_content(self, config: GenerationConfig) -> str:
        """Generate template-based content (fallback when API unavailable)"""

        chapter_title = CHAPTER_TOPICS[config.chapter]['title']

        content = f"""# Kafli {config.chapter}: {chapter_title}

## {config.section_num} {config.section_title}

### Inngangur

Í þessum hluta munum við kanna {config.section_title.lower()}. Þetta er mikilvægt efni í efnafræðinni sem tengist {', '.join(config.topics)}.

### Lykilhugtök

"""

        # Add some key concepts
        for i, topic in enumerate(config.topics[:3], 1):
            content += f"**{topic.capitalize()}**: Grunnhugtak sem lýsir mikilvægum eiginleikum efnis.\n\n"

        content += """### Skýringar

Efni samanstendur af atómum og sameindum. Atóm eru minnstu einingar frumefnis sem halda eiginleikum þess. Sameindir myndast þegar tvö eða fleiri atóm tengjast saman með efnatengjum.

### Dæmi

Vatn (H₂O) er gott dæmi um sameind. Hún samanstendur af tveimur vetnisatómum og einu súrefnisatómi sem tengjast með samgildum tengjum.

### Samantekt

Í þessum hluta fórum við yfir helstu þætti """

        content += config.section_title.lower() + "."

        return content

    def _create_metadata(self, config: GenerationConfig, content: str) -> Dict:
        """Create metadata for generated content"""

        word_count = len(content.split())

        return {
            "chapter": config.chapter,
            "section": config.section_num,
            "chapter_title": CHAPTER_TOPICS[config.chapter]['title'],
            "section_title": config.section_title,
            "language": "is",
            "word_count": word_count,
            "generated": True,
            "difficulty": config.difficulty,
            "topics": config.topics,
            "doc_type": config.doc_type,
            "generated_at": datetime.now().isoformat()
        }

    def _update_stats(self, config: GenerationConfig, metadata: Dict):
        """Update generation statistics"""
        self.stats["generated"] += 1
        self.stats["total_words"] += metadata["word_count"]

        # By chapter
        ch = config.chapter
        if ch not in self.stats["by_chapter"]:
            self.stats["by_chapter"][ch] = 0
        self.stats["by_chapter"][ch] += 1

        # By type
        dt = config.doc_type
        if dt not in self.stats["by_type"]:
            self.stats["by_type"][dt] = 0
        self.stats["by_type"][dt] += 1

    def get_stats(self) -> Dict:
        """Get generation statistics"""
        return self.stats

def create_generation_plan(count: int, chapters: List[int], difficulty: str) -> List[GenerationConfig]:
    """Create a plan for generating content"""

    configs = []

    # Calculate how many docs per chapter
    docs_per_chapter = count // len(chapters)
    remainder = count % len(chapters)

    for chapter in chapters:
        chapter_count = docs_per_chapter + (1 if remainder > 0 else 0)
        remainder -= 1

        sections = CHAPTER_TOPICS[chapter]["sections"]

        # Distribute documents across sections
        for i in range(chapter_count):
            section = sections[i % len(sections)]

            # Choose document type based on weights
            doc_type = random.choices(
                list(DOCUMENT_TYPES.keys()),
                weights=[DOCUMENT_TYPES[t]["weight"] for t in DOCUMENT_TYPES.keys()]
            )[0]

            # Calculate target word count
            min_words = DOCUMENT_TYPES[doc_type]["min_words"]
            max_words = DOCUMENT_TYPES[doc_type]["max_words"]
            target_words = random.randint(min_words, max_words)

            config = GenerationConfig(
                chapter=chapter,
                section_num=section["num"],
                section_title=section["title"],
                topics=section["topics"],
                doc_type=doc_type,
                difficulty=difficulty,
                target_words=target_words
            )

            configs.append(config)

    # Shuffle to mix chapters and types
    random.shuffle(configs)

    return configs

def save_document(doc: Dict, output_dir: Path, index: int):
    """Save generated document to file"""

    metadata = doc["metadata"]
    content = doc["content"]

    # Create filename
    chapter = metadata["chapter"]
    section = metadata["section"].replace(".", "_")
    doc_type = metadata["doc_type"]
    filename = f"ch{chapter}_sec{section}_{doc_type}_{index:03d}.md"

    filepath = output_dir / filename

    # Create YAML frontmatter
    frontmatter = "---\n"
    for key, value in metadata.items():
        if isinstance(value, list):
            frontmatter += f"{key}:\n"
            for item in value:
                frontmatter += f"  - {item}\n"
        elif isinstance(value, str):
            frontmatter += f'{key}: "{value}"\n'
        else:
            frontmatter += f"{key}: {value}\n"
    frontmatter += "---\n\n"

    # Write file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(frontmatter + content)

    return filepath

def main():
    parser = argparse.ArgumentParser(
        description="Generate Icelandic chemistry content for testing"
    )
    parser.add_argument(
        "--count", "-c",
        type=int,
        default=50,
        help="Number of documents to generate (default: 50)"
    )
    parser.add_argument(
        "--chapters",
        type=str,
        default="1,2,3,4,5",
        help="Comma-separated chapter numbers (default: 1,2,3,4,5)"
    )
    parser.add_argument(
        "--difficulty",
        choices=["basic", "intermediate", "advanced"],
        default="intermediate",
        help="Difficulty level (default: intermediate)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="tools/generated",
        help="Output directory (default: tools/generated)"
    )
    parser.add_argument(
        "--no-api",
        action="store_true",
        help="Use templates only, skip Claude API"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="Anthropic API key (or set ANTHROPIC_API_KEY env var)"
    )

    args = parser.parse_args()

    # Parse chapters
    chapters = [int(ch.strip()) for ch in args.chapters.split(",")]

    # Validate chapters
    for ch in chapters:
        if ch not in CHAPTER_TOPICS:
            print(f"Error: Invalid chapter {ch}. Must be 1-5.")
            return 1

    # Setup output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize generator
    print(f"\n{'='*60}")
    print("Icelandic Chemistry Content Generator")
    print(f"{'='*60}\n")

    use_api = not args.no_api
    if use_api:
        print("🤖 Using Claude API for content generation")
    else:
        print("📝 Using template-based generation (no API)")

    try:
        generator = ContentGenerator(api_key=args.api_key, use_api=use_api)
    except ValueError as e:
        print(f"❌ {e}")
        return 1

    # Create generation plan
    print(f"\n📋 Planning generation of {args.count} documents...")
    print(f"📚 Chapters: {', '.join(map(str, chapters))}")
    print(f"🎯 Difficulty: {args.difficulty}")
    print(f"💾 Output: {output_dir.absolute()}\n")

    configs = create_generation_plan(args.count, chapters, args.difficulty)

    # Generate documents
    print(f"{'='*60}")
    print("Generating content...")
    print(f"{'='*60}\n")

    for i, config in enumerate(configs, 1):
        print(f"[{i}/{len(configs)}] Kafli {config.chapter}.{config.section_num}: {config.section_title} ({config.doc_type})...", end=" ")

        try:
            doc = generator.generate_content(config)
            filepath = save_document(doc, output_dir, i)
            print(f"✅ ({doc['metadata']['word_count']} orð)")

        except Exception as e:
            print(f"❌ Error: {e}")
            continue

    # Print statistics
    stats = generator.get_stats()

    print(f"\n{'='*60}")
    print("Generation Complete!")
    print(f"{'='*60}\n")

    print(f"✅ Generated: {stats['generated']} documents")
    print(f"📊 Total words: {stats['total_words']:,}")
    print(f"📈 Average words/doc: {stats['total_words'] // stats['generated'] if stats['generated'] > 0 else 0}")

    print(f"\n📚 By chapter:")
    for ch in sorted(stats['by_chapter'].keys()):
        print(f"   Kafli {ch}: {stats['by_chapter'][ch]} docs")

    print(f"\n📝 By type:")
    for dt in sorted(stats['by_type'].keys()):
        print(f"   {dt.capitalize()}: {stats['by_type'][dt]} docs")

    print(f"\n💾 Saved to: {output_dir.absolute()}")
    print(f"\n🚀 Next steps:")
    print(f"   1. Review generated content in {output_dir}")
    print(f"   2. Run ingestion: cd backend && python src/ingest.py --input ../{output_dir}")
    print(f"   3. Test RAG system with Icelandic queries\n")

    return 0

if __name__ == "__main__":
    sys.exit(main())
