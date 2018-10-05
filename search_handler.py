#
# Parse a string entered by the user into keywords
#


def parse_user_query(user_query):

    # Generate the list of words in the user's search query
    keywords = user_query.split()

    # Remove special characters from the words
    alphabetical_keywords = list()
    for word in keywords:
        alnum_word = ''.join(character for character in word.lower()
                             if ('a' <= character <= 'z'
                                 or character == '\''
                                 or '0' <= character <= '9'))
        if alnum_word.isalnum():
            alphabetical_keywords.append(alnum_word)

    # Find the unique keywords & count the number of times they appear
    unique_keywords = dict()  # Dictionary with key = unique keyword, value = # of appearances

    for word in alphabetical_keywords:

        # If this word has not yet been parsed, add it as a new unique keyword
        if unique_keywords.get(word) is None:
            unique_keywords[word] = 1
        # Otherwise increment the # of appearances of this word
        else:
            unique_keywords[word] += 1

    return unique_keywords


#
# Store the 20 most searched keywords in one server session
#


def most_searched_keywords(new_unique_keywords, existing_historic_keywords):

    top_20_keywords = dict()  # This function will return the top 20 most searched words (empty for now)

    # First add each new word to the list of all words historically searched
    for new_word in new_unique_keywords:

        # If keyword is already in table then just update number of occurrences
        if existing_historic_keywords.get(new_word) is not None:
            existing_historic_keywords[new_word] += new_unique_keywords.get(new_word)

        # Otherwise add it as a new word
        else:
            existing_historic_keywords[new_word] = new_unique_keywords.get(new_word)

    # Now figure out the new top 20 most searched keywords

    # If the number of keywords that have historically been searched is less than 20, just display all of the words
    if len(existing_historic_keywords) < 20:
        # Order the top 20 from highest to lowest frequency
        sorted_historic_keywords = sorted(existing_historic_keywords, key=existing_historic_keywords.get, reverse=True)
        for word in sorted_historic_keywords:
            top_20_keywords[word] = existing_historic_keywords.get(word)
        return top_20_keywords
    # Otherwise figure out which words are the new top 20
    else:
        for existing_word in existing_historic_keywords:
            # Fill up the top 20 with the first 20 words encountered
            if len(top_20_keywords) < 20:
                top_20_keywords[existing_word] = existing_historic_keywords.get(existing_word)
            # Then replace words in the top 20 as needed
            else:
                min_count_word = min(top_20_keywords, key=top_20_keywords.get)
                min_count = top_20_keywords.get(min_count_word)
                if existing_historic_keywords.get(existing_word) > min_count:
                    top_20_keywords.pop(min_count_word)
                    top_20_keywords[existing_word] = existing_historic_keywords.get(existing_word)

    # Order the top 20 from highest to lowest frequency
    sorted_top_20_keywords = sorted(top_20_keywords, key=top_20_keywords.get, reverse=True)
    for word in sorted_top_20_keywords:
        top_20_keywords[word] = existing_historic_keywords.get(word)

    return top_20_keywords
