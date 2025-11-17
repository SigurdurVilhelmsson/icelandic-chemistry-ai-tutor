# Contributing to Icelandic Chemistry AI Tutor

Thank you for your interest in contributing to the Icelandic Chemistry AI Tutor! This document provides guidelines for contributing to the project.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)
- [Documentation](#documentation)
- [Translation Guidelines](#translation-guidelines)
- [Community](#community)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of:
- Age, body size, disability, ethnicity, gender identity and expression
- Level of experience, nationality, personal appearance, race, religion
- Sexual identity and orientation

### Our Standards

**Positive behavior includes:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards others

**Unacceptable behavior includes:**
- Harassment, trolling, or derogatory comments
- Personal or political attacks
- Publishing others' private information without permission
- Other conduct which could be considered inappropriate

### Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be reported by contacting the project team at **sigurdurev@kvenno.is**. All complaints will be reviewed and investigated.

---

## How Can I Contribute?

### 1. Report Bugs

Found a bug? Please create an issue with:

**Title:** Short, descriptive summary
**Description:**
- What you expected to happen
- What actually happened
- Steps to reproduce
- Environment (browser, OS, etc.)
- Screenshots (if applicable)

**Example:**
```
Title: Chat input not accepting Icelandic characters

Description:
Expected: Icelandic characters (á, ð, é, etc.) should work in chat
Actual: Characters are replaced with question marks

Steps to reproduce:
1. Open chat interface
2. Type "Hvað er atóm?"
3. Notice á is replaced with ?

Environment: Firefox 120, Windows 11
```

### 2. Suggest Enhancements

Have an idea for improvement? Create an issue with:
- Clear description of the enhancement
- Why it would be useful
- Possible implementation approach (optional)

### 3. Translate Content

We need help translating:
- **Chemistry chapters** (English → Icelandic)
- **UI text** (English → Icelandic)
- **Documentation** (English → Icelandic)

See [Translation Guidelines](#translation-guidelines) below.

### 4. Improve Documentation

Documentation is crucial! You can:
- Fix typos or unclear explanations
- Add examples
- Translate to Icelandic
- Create tutorials

### 5. Write Code

Contribute code for:
- Bug fixes
- New features
- Performance improvements
- Tests

See [Development Workflow](#development-workflow) below.

---

## Getting Started

### Prerequisites

- Git
- Python 3.11+
- Node.js 18+
- Code editor (VS Code recommended)

### Fork and Clone

1. **Fork the repository** on GitHub

2. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/icelandic-chemistry-ai-tutor.git
   cd icelandic-chemistry-ai-tutor
   ```

3. **Add upstream remote:**
   ```bash
   git remote add upstream https://github.com/SigurdurVilhelmsson/icelandic-chemistry-ai-tutor.git
   ```

4. **Create a branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Set Up Development Environment

Follow the [Development Guide](DEVELOPMENT.md) to set up your local environment.

---

## Development Workflow

### 1. Pick an Issue

- Check [open issues](https://github.com/SigurdurVilhelmsson/icelandic-chemistry-ai-tutor/issues)
- Look for "good first issue" or "help wanted" labels
- Comment on the issue to let others know you're working on it

### 2. Create a Branch

**Branch naming convention:**
- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation changes
- `refactor/description` - Code refactoring
- `test/description` - Adding tests

**Examples:**
```bash
git checkout -b feature/add-latex-support
git checkout -b fix/chat-input-encoding
git checkout -b docs/update-api-reference
```

### 3. Make Changes

- Write clean, readable code
- Follow [Coding Standards](#coding-standards)
- Add tests for new functionality
- Update documentation

### 4. Test Your Changes

**Backend:**
```bash
cd backend
pytest tests/
```

**Frontend:**
```bash
cd frontend
npm test
```

**Manual testing:**
- Test in multiple browsers
- Test with Icelandic characters
- Test edge cases

### 5. Commit Your Changes

Follow [Commit Guidelines](#commit-guidelines):

```bash
git add .
git commit -m "feat: Add LaTeX rendering support for chemical formulas"
```

### 6. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 7. Create a Pull Request

See [Pull Request Process](#pull-request-process) below.

---

## Coding Standards

### Python (Backend)

**Style Guide:** PEP 8

**Formatting:**
```bash
# Install tools
pip install black flake8 mypy

# Format code
black src/ tests/

# Check style
flake8 src/ tests/

# Type checking
mypy src/
```

**Code Example:**
```python
from typing import List, Optional
from pydantic import BaseModel


class QuestionRequest(BaseModel):
    """Request model for chemistry questions."""

    question: str
    conversation_id: Optional[str] = None
    max_results: int = 3


async def process_question(
    request: QuestionRequest
) -> dict:
    """
    Process a chemistry question using RAG pipeline.

    Args:
        request: Question request with parameters

    Returns:
        Dictionary containing answer and citations

    Raises:
        ValueError: If question is invalid
    """
    if not request.question.strip():
        raise ValueError("Question cannot be empty")

    # Implementation
    return {"answer": "...", "citations": []}
```

**Best Practices:**
- Use type hints
- Write docstrings (Google style)
- Keep functions small and focused
- Use descriptive variable names
- Handle errors gracefully

### TypeScript (Frontend)

**Style Guide:** Airbnb JavaScript Style Guide

**Formatting:**
```bash
# Install tools
npm install --save-dev eslint prettier

# Format code
npm run format

# Check style
npm run lint
```

**Code Example:**
```typescript
interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  citations?: Citation[];
}

interface Citation {
  chapter: number;
  section: string;
  page: number;
}

/**
 * Format a chat message for display
 */
export const formatMessage = (
  message: ChatMessage
): string => {
  const time = message.timestamp.toLocaleTimeString('is-IS');
  return `[${time}] ${message.role}: ${message.content}`;
};

/**
 * React component for displaying a message
 */
export const MessageBubble: React.FC<{
  message: ChatMessage;
}> = ({ message }) => {
  const formattedTime = message.timestamp.toLocaleTimeString('is-IS');

  return (
    <div className={`message ${message.role}`}>
      <div className="message-content">{message.content}</div>
      <div className="message-time">{formattedTime}</div>
      {message.citations && (
        <CitationList citations={message.citations} />
      )}
    </div>
  );
};
```

**Best Practices:**
- Use TypeScript (no `any` types)
- Use functional components with hooks
- Keep components small and focused
- Use meaningful prop names
- Write accessible HTML (ARIA labels)

### General Practices

**File Naming:**
- Python: `snake_case.py`
- TypeScript: `PascalCase.tsx` (components), `camelCase.ts` (utilities)
- Tests: `test_*.py`, `*.test.tsx`

**Comments:**
- Use comments to explain *why*, not *what*
- Update comments when code changes
- Remove commented-out code

**Error Handling:**
```python
# Good
try:
    result = process_question(request)
except ValueError as e:
    logger.error(f"Invalid question: {e}")
    raise HTTPException(status_code=400, detail=str(e))

# Bad
try:
    result = process_question(request)
except:  # Too broad
    pass  # Silent failure
```

---

## Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Formatting, missing semicolons, etc.
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance tasks

### Examples

**Good:**
```
feat(rag): Add support for LaTeX formulas in responses

- Parse LaTeX expressions from chemistry content
- Render using KaTeX library
- Add tests for formula rendering

Closes #123
```

**Good (simple):**
```
fix(chat): Handle Icelandic characters in input
```

**Bad:**
```
fixed stuff
```

**Bad:**
```
Updated files
```

### Rules

1. Use imperative mood ("Add feature" not "Added feature")
2. First line max 72 characters
3. Capitalize first letter
4. No period at the end
5. Reference issues when applicable

---

## Pull Request Process

### Before Submitting

**Checklist:**
- ✅ Code follows style guidelines
- ✅ All tests pass
- ✅ New tests added for new functionality
- ✅ Documentation updated
- ✅ Commit messages follow guidelines
- ✅ No merge conflicts with main branch

### Update Your Branch

```bash
# Fetch latest changes
git fetch upstream

# Rebase on main
git rebase upstream/main

# Resolve conflicts if any
# Then push (may need --force-with-lease)
git push origin feature/your-feature --force-with-lease
```

### Create Pull Request

1. **Go to GitHub** and create a pull request

2. **Fill out the template:**
   ```markdown
   ## Description
   Brief description of what this PR does

   ## Related Issue
   Fixes #123

   ## Changes
   - Added LaTeX rendering
   - Updated documentation
   - Added tests

   ## Testing
   - [ ] Backend tests pass
   - [ ] Frontend tests pass
   - [ ] Manual testing completed

   ## Screenshots (if applicable)
   [Add screenshots for UI changes]
   ```

3. **Wait for review**

### Review Process

**What to expect:**
- Maintainers will review within 3-5 days
- They may request changes
- Be responsive to feedback
- Don't take criticism personally

**After approval:**
- PR will be merged by maintainer
- Your branch will be deleted
- Celebrate! 🎉

---

## Testing

### Backend Tests

**Write tests for:**
- API endpoints
- RAG pipeline logic
- Vector store operations
- Error handling

**Example:**
```python
# tests/test_rag_pipeline.py

import pytest
from src.rag_pipeline import RAGPipeline

@pytest.fixture
def rag_pipeline():
    return RAGPipeline()

def test_answer_simple_question(rag_pipeline):
    result = rag_pipeline.answer("Hvað er atóm?")

    assert "atóm" in result["answer"].lower()
    assert len(result["citations"]) > 0
    assert result["citations"][0]["chapter"] is not None

def test_handle_empty_question(rag_pipeline):
    with pytest.raises(ValueError, match="empty"):
        rag_pipeline.answer("")
```

**Run tests:**
```bash
cd backend
pytest tests/ -v
pytest tests/test_rag_pipeline.py::test_answer_simple_question
```

### Frontend Tests

**Write tests for:**
- Component rendering
- User interactions
- API calls
- Error states

**Example:**
```typescript
// src/components/ChatInput.test.tsx

import { render, screen, fireEvent } from '@testing-library/react';
import { ChatInput } from './ChatInput';

describe('ChatInput', () => {
  it('renders input field', () => {
    render(<ChatInput onSubmit={jest.fn()} />);
    expect(screen.getByPlaceholderText(/Spurðu/i)).toBeInTheDocument();
  });

  it('calls onSubmit with question', () => {
    const onSubmit = jest.fn();
    render(<ChatInput onSubmit={onSubmit} />);

    const input = screen.getByPlaceholderText(/Spurðu/i);
    fireEvent.change(input, { target: { value: 'Hvað er atóm?' } });
    fireEvent.submit(input.closest('form')!);

    expect(onSubmit).toHaveBeenCalledWith('Hvað er atóm?');
  });

  it('handles Icelandic characters', () => {
    const onSubmit = jest.fn();
    render(<ChatInput onSubmit={onSubmit} />);

    const input = screen.getByPlaceholderText(/Spurðu/i);
    fireEvent.change(input, { target: { value: 'Hvað er sýra?' } });

    expect(input).toHaveValue('Hvað er sýra?');
  });
});
```

**Run tests:**
```bash
cd frontend
npm test
npm test -- --coverage
```

---

## Documentation

### What to Document

**Code:**
- Public functions and classes
- Complex algorithms
- Non-obvious behavior
- API endpoints

**User-facing:**
- How to use features
- Common workflows
- Troubleshooting

**Developer-facing:**
- Setup instructions
- Architecture decisions
- Deployment process

### Documentation Style

**Clear and concise:**
```markdown
# Good
## Installing Dependencies

Install Python dependencies:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

# Bad
## Dependencies

You need to install the dependencies that are listed in the
requirements.txt file by using pip, which is the Python package
manager...
```

**Use examples:**
```markdown
# Good
### Asking a Question

\`\`\`python
client = ChemistryAIClient("https://api.example.com")
result = client.ask("Hvað er atóm?")
print(result["answer"])
\`\`\`

# Bad
### Asking a Question

Use the client to ask questions.
```

---

## Translation Guidelines

### Translation Workflow

1. **Find content to translate**
   - Check `backend/data/chapters/` for chemistry content
   - Look for `TODO: Translate` comments in code

2. **Translate**
   - Keep scientific accuracy
   - Use proper Icelandic terminology
   - Maintain formatting (Markdown, LaTeX)

3. **Review**
   - Have another Icelandic speaker review
   - Check scientific terms in Icelandic dictionaries

4. **Submit**
   - Create PR with translations
   - Note source of scientific terms

### Chemistry Terminology

**Resources:**
- [Íslensk efnafræðiheiti](http://efnaheiti.arnastofnun.is/)
- Icelandic chemistry textbooks
- [Hugtakasafn](https://hugtakasafn.arnastofnun.is/)

**Common terms:**
| English | Icelandic |
|---------|-----------|
| Atom | Atóm |
| Molecule | Sameind |
| Ion | Jón |
| Acid | Sýra |
| Base | Basi |
| Electron | Rafeind |
| Proton | Róteind |
| Neutron | Nifteind |
| Element | Frumefni |
| Compound | Efnasamband |

### Translation Quality

**Do:**
- ✅ Use correct Icelandic scientific terminology
- ✅ Maintain technical accuracy
- ✅ Keep consistent terminology
- ✅ Preserve formatting

**Don't:**
- ❌ Use Google Translate without review
- ❌ Mix English and Icelandic terms
- ❌ Translate LaTeX formulas
- ❌ Change scientific meaning

---

## Community

### Communication Channels

**GitHub:**
- [Issues](https://github.com/SigurdurVilhelmsson/icelandic-chemistry-ai-tutor/issues) - Bug reports, feature requests
- [Pull Requests](https://github.com/SigurdurVilhelmsson/icelandic-chemistry-ai-tutor/pulls) - Code contributions
- [Discussions](https://github.com/SigurdurVilhelmsson/icelandic-chemistry-ai-tutor/discussions) - General discussion

**Email:**
- sigurdurev@kvenno.is - Project lead

### Recognition

**Contributors are recognized:**
- In README.md
- In release notes
- On GitHub contributors page

**Significant contributors may:**
- Be listed as co-authors on research papers
- Be invited to present at conferences
- Receive acknowledgment in publications

### Getting Help

**Stuck on something?**

1. Check [DEVELOPMENT.md](DEVELOPMENT.md)
2. Search existing issues
3. Ask in GitHub Discussions
4. Email the maintainer

**Be specific:**
- What are you trying to do?
- What have you tried?
- What error are you getting?
- Include code snippets, logs, screenshots

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

## Questions?

If you have questions about contributing, please:

1. Check this document
2. Search [existing issues](https://github.com/SigurdurVilhelmsson/icelandic-chemistry-ai-tutor/issues)
3. Create a new issue with the "question" label
4. Email sigurdurev@kvenno.is

---

## Thank You!

Thank you for taking the time to contribute! Every contribution, no matter how small, helps make this project better for Icelandic students.

**Happy contributing! 🎉**

---

**Last Updated:** November 17, 2025
