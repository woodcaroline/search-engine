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
                                 or character == "\'"
                                 or '0' <= character <= '9'))
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
# Store the most recently searched keywords for each user who logs in
#
def retrieve_search_history(new_keywords, user_email, existing_search_history):

    # If user has logged in before
    if user_email in existing_search_history:
        # Retrieve user's search history and update as needed
        list_of_search_history = existing_search_history[user_email]

        for word in new_keywords:
            # Add words if we haven't saved 10 most recent yet
            if len(list_of_search_history) < 10:
                list_of_search_history.insert(0, word)

            # Otherwise if we already have 10 most recent saved, replace oldest word searched
            else:
                # Delete oldest word (at 10th/last position)
                del list_of_search_history[9]
                # Insert newest word at front of list
                list_of_search_history.insert(0, word)

    # Otherwise if this is a new user
    else:
        # Create a new empty list that will be filled as the user searches
        existing_search_history[user_email] = list()

    return existing_search_history[user_email]
