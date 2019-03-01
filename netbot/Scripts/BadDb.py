badDb = {
    "and", "or", "also", "please", "maybe",
    "will", "a", "an", "be", "to", "of", "can",
    "in", "that", "have", "i", "it", "for", "is"
    "as", "at", "by", "so", "than", " ", "", "it"
}

#words irrelevant to searches, though commonly used
badsearchDb = {
    "and", "or", "also", "please", "maybe", "the", "can", "yes", "why",
    "will", "a", "an", "be", "to", "of", "internet", "tell", "are",
    "in", "that", "have", "i", "it", "for", "is", "you", "ok", "no",
    "as", "at", "by", "so", "than", "it", "search", "me", "please",
    "do", "know", "who", "?", "what", "your", "opinion", "about", "tell",
}

#limited - common words, commonly repeated but usually aren't relevant to subject, therefore limited by weight - significance
limited = {"?":5, "and":5, "or":5,"or":5,"who":5,"are":5,"what":5,"whats":5,"where":5,"you":5}