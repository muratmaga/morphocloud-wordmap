#!/usr/bin/env python3
"""
Generate a word map/cloud from GitHub issues descriptions.
Extracts keywords from the Description field of issues.
"""

import json
import re
from collections import Counter, defaultdict
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Simple stemming function
def simple_stem(word):
    """Simple stemming to group related words."""
    # Common suffixes to remove
    suffixes = ['ing', 'ed', 'es', 's', 'tion', 'ation', 'ly', 'ment', 'ness', 'er', 'or', 'ist', 'ity', 'al']
    
    word = word.lower()
    for suffix in suffixes:
        if word.endswith(suffix) and len(word) > len(suffix) + 2:
            return word[:-len(suffix)]
    return word

# Common stop words to exclude
STOP_WORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he',
    'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was', 'will',
    'with', 'i', 'am', 'my', 'we', 'this', 'have', 'been', 'would', 'using',
    'use', 'also', 'can', 'may', 'or', 'but', 'if', 'so', 'than', 'do', 'does',
    'did', 'which', 'these', 'those', 'such', 'into', 'through', 'during',
    'before', 'after', 'above', 'below', 'between', 'under', 'over', 'both',
    'each', 'few', 'more', 'most', 'other', 'some', 'there', 'their', 'them',
    'then', 'when', 'where', 'who', 'why', 'how', 'all', 'any', 'been', 'being',
    'could', 'having', 'her', 'here', 'him', 'his', 'me', 'not', 'now', 'only',
    'our', 'out', 'own', 'same', 'should', 'their', 'theirs', 'them', 'themselves',
    'then', 'there', 'they', 'up', 'very', 'what', 'which', 'while', 'who', 'whom',
    'your', 'yours', 'yourself', 'yourselves', 'about', 'via', 'via', 'via', 'want',
    'like', 'need', 'get', 'work', 'working', 'used', 'try', 'trying', 'test', 
    'testing', 'currently', 'able', 'plan', 'planning', 'etc', 'just', 'really',
    'please', 'thanks', 'thank', 'hi', 'hello', 'hey', 'one', 'two', 'three',
    # Banned words as requested
    'morphocloud', 'university', 'instance', 'create', 'created', 'creating',
    'participant', 'workshop', 'github', 'issue', 'well', 'attending', 'orcid',
    # Geographic locations
    'usa', 'america', 'american', 'states', 'united', 'california', 'texas', 'florida',
    'new', 'york', 'washington', 'oregon', 'colorado', 'arizona', 'utah', 'nevada',
    'illinois', 'ohio', 'michigan', 'pennsylvania', 'massachusetts', 'virginia',
    'georgia', 'north', 'carolina', 'south', 'tennessee', 'kentucky', 'alabama',
    'louisiana', 'mississippi', 'arkansas', 'oklahoma', 'kansas', 'nebraska',
    'iowa', 'missouri', 'wisconsin', 'minnesota', 'indiana', 'maryland', 'delaware',
    'connecticut', 'rhode', 'island', 'vermont', 'hampshire', 'maine', 'west',
    'seattle', 'portland', 'denver', 'phoenix', 'chicago', 'boston', 'atlanta',
    'houston', 'dallas', 'austin', 'miami', 'philadelphia', 'detroit', 'baltimore',
    'japan', 'japanese', 'tokyo', 'kyoto', 'osaka', 'china', 'chinese', 'beijing',
    'shanghai', 'canada', 'canadian', 'toronto', 'vancouver', 'montreal', 'ottawa',
    'england', 'london', 'britain', 'british', 'uk', 'scotland', 'wales', 'ireland',
    'france', 'french', 'paris', 'germany', 'german', 'berlin', 'spain', 'spanish',
    'madrid', 'italy', 'italian', 'rome', 'netherlands', 'dutch', 'amsterdam',
    'belgium', 'brussels', 'switzerland', 'swiss', 'sweden', 'stockholm', 'norway',
    'denmark', 'finland', 'austria', 'poland', 'portugal', 'greece', 'russia',
    'australia', 'australian', 'sydney', 'melbourne', 'zealand', 'auckland',
    'india', 'indian', 'delhi', 'mumbai', 'brazil', 'brazilian', 'mexico', 'mexican',
    'argentina', 'chile', 'peru', 'colombia', 'africa', 'african', 'kenya', 'egypt',
    'europe', 'european', 'asia', 'asian', 'kyushu', 'louisville'
}

# Canonical forms for specific word groups
CANONICAL_FORMS = {
    'segment': 'segmentation',
    'segments': 'segmentation',
    'segmenting': 'segmentation',
    'segmentation': 'segmentation',
    'morphometric': 'morphometrics',
    'morphometrics': 'morphometrics',
}

# Common first names to filter out
COMMON_NAMES = {
    'john', 'mary', 'michael', 'sarah', 'david', 'james', 'robert', 'jennifer',
    'william', 'linda', 'richard', 'patricia', 'charles', 'barbara', 'joseph',
    'elizabeth', 'thomas', 'susan', 'christopher', 'jessica', 'daniel', 'karen',
    'matthew', 'nancy', 'anthony', 'lisa', 'mark', 'betty', 'donald', 'margaret',
    'steven', 'sandra', 'paul', 'ashley', 'andrew', 'kimberly', 'joshua', 'emily',
    'kenneth', 'donna', 'kevin', 'michelle', 'brian', 'carol', 'george', 'amanda',
    'edward', 'melissa', 'ronald', 'deborah', 'timothy', 'stephanie', 'jason',
    'rebecca', 'jeffrey', 'sharon', 'ryan', 'laura', 'jacob', 'cynthia', 'gary',
    'kathleen', 'nicholas', 'amy', 'eric', 'shirley', 'jonathan', 'angela',
    'stephen', 'helen', 'larry', 'anna', 'justin', 'brenda', 'scott', 'pamela',
    'brandon', 'nicole', 'benjamin', 'emma', 'samuel', 'samantha', 'raymond',
    'katherine', 'patrick', 'christine', 'alexander', 'debra', 'jack', 'rachel',
    'dennis', 'catherine', 'jerry', 'carolyn', 'tyler', 'janet', 'aaron', 'ruth',
    'jose', 'maria', 'adam', 'heather', 'henry', 'diane', 'nathan', 'virginia',
    'douglas', 'julie', 'zachary', 'joyce', 'peter', 'victoria', 'kyle', 'olivia',
    'walter', 'kelly', 'ethan', 'christina', 'jeremy', 'lauren', 'harold', 'joan',
    'keith', 'evelyn', 'christian', 'judith', 'roger', 'megan', 'noah', 'cheryl',
    'gerald', 'andrea', 'carl', 'hannah', 'terry', 'jacqueline', 'sean', 'martha',
    'austin', 'gloria', 'arthur', 'teresa', 'lawrence', 'ann', 'jesse', 'sara',
    'dylan', 'madison', 'bryan', 'frances', 'joe', 'kathryn', 'jordan', 'janice',
    'billy', 'jean', 'bruce', 'abigail', 'albert', 'sophia', 'willie', 'isabella',
    'gabriel', 'charlotte', 'logan', 'amelia', 'alan', 'mia', 'juan', 'harper',
    'wayne', 'evelyn', 'roy', 'ella', 'ralph', 'scarlett', 'randy', 'grace',
    'eugene', 'chloe', 'vincent', 'lily', 'russell', 'ellie', 'elijah', 'lucy',
    'louis', 'addison', 'bobby', 'natalie', 'philip', 'lillian', 'johnny', 'leah',
    'karly', 'cohen', 'murat', 'maga', 'luke', 'rose', 'yuto', 'sano', 'anthony',
    'lee', 'annika', 'dawley', 'participant'
}

def extract_description(body_text):
    """Extract the Description field content from issue body."""
    if not body_text:
        return ""
    
    # Look for the ### Description section
    # Extract content between ### Description and the next ### section
    description_match = re.search(
        r'### Description\s*\n\n(.*?)(?=\n### |\Z)', 
        body_text, 
        re.DOTALL | re.IGNORECASE
    )
    
    if description_match:
        return description_match.group(1).strip()
    return ""

def is_likely_name(word):
    """Check if a word is likely a person's name."""
    if not word or len(word) == 0:
        return False
    
    # Check if word is in common names list
    if word.lower() in COMMON_NAMES:
        return True
    
    # Check if word looks like a proper name (has uppercase)
    # but exclude common acronyms and technical terms
    if word[0].isupper() and len(word) > 2:
        # Allow certain uppercase patterns that are technical
        if word.isupper():  # All caps (like CT, MRI) - keep these
            return False
        # Mixed case likely indicates a proper name
        return True
    
    return False

def extract_keywords(text):
    """Extract meaningful keywords from text."""
    if not text:
        return []
    
    # Store original case for name detection
    original_text = text
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove common phrases and patterns
    text = re.sub(r'\d+[a-z]*', '', text)  # Remove numbers
    text = re.sub(r'[^\w\s-]', ' ', text)  # Keep only words and hyphens
    
    # Get original words with case preserved for name detection
    original_words = original_text.split()
    
    # Split into words
    words = text.split()
    
    # Filter words: remove stop words, short words, names, and keep meaningful terms
    keywords = []
    for i, word in enumerate(words):
        word = word.strip('-')
        
        # Get the original case version for name checking
        orig_word = original_words[i].strip('-.,!?;:') if i < len(original_words) else word
        
        if (len(word) >= 3 and 
            word not in STOP_WORDS and 
            not word.isdigit() and
            not is_likely_name(orig_word)):
            
            # Apply canonical form if it exists
            if word in CANONICAL_FORMS:
                keywords.append(CANONICAL_FORMS[word])
            else:
                keywords.append(word)
    
    return keywords

def main():
    # Load the issues
    with open('/Users/amaga/all_issues.json', 'r') as f:
        issues = json.load(f)
    
    print(f"Loaded {len(issues)} issues")
    
    # Extract descriptions and collect keywords
    # Now we apply canonical forms before stemming
    keyword_counts = Counter()
    processed_count = 0
    
    for issue in issues:
        body = issue.get('body', '')
        description = extract_description(body)
        
        if description:
            keywords = extract_keywords(description)
            keyword_counts.update(keywords)
            processed_count += 1
    
    print(f"Processed {processed_count} issues with descriptions")
    print(f"Total unique keywords: {len(keyword_counts)}")
    
    if not keyword_counts:
        print("No keywords found!")
        return
    
    # Print top 50 keywords
    print("\nTop 50 Keywords:")
    print("-" * 60)
    for i, (word, count) in enumerate(sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:50], 1):
        print(f"{i:2d}. {word:30s} ({count:3d})")
    
    # Generate word cloud
    wordcloud = WordCloud(
        width=1600,
        height=900,
        background_color='white',
        colormap='twilight_shifted',
        relative_scaling=0.5,
        min_font_size=10,
        max_words=200
    ).generate_from_frequencies(keyword_counts)
    
    # Create and save visualization
    plt.figure(figsize=(20, 11))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('MorphoCloud Issues - Keyword Word Map', fontsize=24, pad=20)
    plt.tight_layout(pad=0)
    
    # Save to file
    output_file = '/Users/amaga/wordmap.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\nWord map saved to: {output_file}")
    
    # Also save keyword frequencies to CSV
    csv_file = '/Users/amaga/keyword_frequencies.csv'
    with open(csv_file, 'w') as f:
        f.write("Keyword,Frequency\n")
        for word, count in sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True):
            f.write(f'"{word}",{count}\n')
    print(f"Keyword frequencies saved to: {csv_file}")

if __name__ == "__main__":
    main()
