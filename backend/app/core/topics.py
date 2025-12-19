from typing import Dict, List

# Predefined conversation topics by proficiency level
TOPICS_BY_LEVEL: Dict[str, List[str]] = {
    "A1": [
        "Self introduction and basic personal information",
        "Spelling names and giving phone numbers",
        "Description of family members and household",
        "Description of a home, room, or apartment",
        "Discussion of daily routines",
        "Telling the time and discussing schedules",
        "Discussion of food and drink preferences",
        "Ordering food and drinks in a café",
        "Description of current and weekly weather",
        "Description of clothes worn today",
        "Identification of common places in a town",
        "Asking for and giving simple directions",
        "Discussion of hobbies and free-time activities",
        "Description of pets and favorite animals",
        "Discussion of favorite music or singers",
        "Basic description of pictures using adjectives",
        "Discussion of weekend activities",
        "Simple shopping interactions",
        "Discussion of transportation methods",
        "Description of activities done at home"
    ],

    "A2": [
        "Planning a weekend or short trip",
        "Discussion of jobs or fields of study",
        "Description of daily life at work or school",
        "Shopping for clothes and describing needs",
        "Description of a past holiday or trip",
        "Description of a city or neighborhood",
        "Discussion of childhood memories",
        "Discussion of recently watched movies or TV shows",
        "Discussion of sports and physical activities",
        "Planning meals or eating at a restaurant",
        "Discussion of health, exercise, and habits",
        "Description of a typical day in a country",
        "Discussion of future plans",
        "Comparison of life in the past and present",
        "Discussion of problems and advice",
        "Description of people’s appearance and personality",
        "Discussion of celebrations and birthdays",
        "Explanation of rules for a simple game",
        "Discussion of transportation and travel problems",
        "Discussion of likes and preferences in detail"
    ],

    "B1": [
        "Description of significant personal experiences",
        "Discussion of challenges and problem-solving experiences",
        "Discussion of advantages and disadvantages of social media",
        "Discussion of cultural differences between countries",
        "Discussion of environmental problems and solutions",
        "Discussion of books, films, or series",
        "Discussion of opinions on education",
        "Discussion of work-life balance and stress",
        "Discussion of technology in everyday life",
        "Description of ideal holidays or lifestyles",
        "Discussion of traditions and festivals",
        "Discussion of language learning experiences",
        "Expression of agreement and disagreement",
        "Discussion of healthy and unhealthy lifestyles",
        "Discussion of volunteering and helping others",
        "Discussion of career goals",
        "Discussion of current news topics",
        "Comparison of urban and rural lifestyles",
        "Discussion of money and happiness",
        "Discussion of friendships and relationships"
    ],

    "B2": [
        "Debate on the influence of social media on society",
        "Analysis of the impact of technology on work and communication",
        "Discussion of environmental policies and responsibility",
        "Discussion of globalization and cultural identity",
        "Discussion of ethical issues in science or medicine",
        "Analysis of advantages and disadvantages of remote work",
        "Discussion of education systems and reforms",
        "Expression and defense of complex opinions",
        "Debate on freedom of speech and its limits",
        "Discussion of artificial intelligence and automation",
        "Analysis of media bias and misinformation",
        "Discussion of consumerism and sustainability",
        "Discussion of gender roles and equality",
        "Analysis of causes and effects of social problems",
        "Debate on the role of government in society",
        "Discussion of mental health awareness",
        "Discussion of success and personal fulfillment",
        "Analysis of cultural stereotypes",
        "Discussion of immigration and multicultural societies",
        "Evaluation of long-term technological consequences"
    ],

    "C1": [
        "In-depth analysis of social and political issues",
        "Discussion of abstract concepts such as identity and freedom",
        "Debate on ethical dilemmas in emerging technologies",
        "Literary analysis of texts and narrative techniques",
        "Discussion of geopolitical conflicts and power dynamics",
        "Evaluation of economic systems and inequality",
        "Analysis of historical events and modern parallels",
        "Discussion of human psychology and behavior",
        "Debate on the limits of scientific progress",
        "Analysis of media discourse and framing",
        "Discussion of leadership styles and decision-making",
        "Evaluation of educational philosophies",
        "Discussion of cultural globalization and localization",
        "Analysis of the relationship between language and thought",
        "Debate on global and local climate responsibility",
        "Discussion of innovation and ethical responsibility",
        "Analysis of social movements and societal impact",
        "Debate on privacy in the digital age",
        "Discussion of philosophical perspectives on happiness and meaning",
        "Evaluation of long-term societal trends"
    ],

    "C2": [
        "Advanced academic and theoretical discourse",
        "Analysis of abstract philosophical frameworks",
        "Debate on complex moral and ethical systems",
        "Advanced literary criticism and theory",
        "Analysis of epistemology and the nature of knowledge",
        "Discussion of interdisciplinary research synthesis",
        "Debate on postmodern and contemporary philosophies",
        "Analysis of discourse, ideology, and power structures",
        "Discussion of the future of human civilization",
        "Analysis of consciousness and human cognition",
        "Debate on determinism, free will, and agency",
        "Discussion of meta-ethics and moral philosophy",
        "Analysis of cultural narratives and collective memory",
        "Debate on transhumanism and human enhancement",
        "Discussion of the limits of language and representation",
        "Analysis of systems thinking and complexity",
        "Debate on global governance and world order",
        "Discussion of the philosophy of science",
        "Analysis of the nature of reality and existence",
        "Spontaneous, nuanced argumentation"
    ]
}

def get_topic_for_level(level: str) -> str:
    """Get a random topic appropriate for the specified proficiency level."""
    import random
    topics = TOPICS_BY_LEVEL.get(level, TOPICS_BY_LEVEL["B1"])
    return random.choice(topics)