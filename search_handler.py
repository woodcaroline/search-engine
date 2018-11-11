#
# Parse a string entered by the user into keywords
# (Modified for Lab 3)
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

    # Return the first keyword to search against it
    return alphabetical_keywords[0]


#
# Store the most recently searched keywords for each user who logs in
#
def retrieve_search_history(new_search, user_email, existing_search_history):

    # if new_search is None:
    #     return existing_search_history[user_email]

    # If user has logged in before
    if user_email in existing_search_history:
        # Retrieve user's search history and update as needed
        list_of_search_history = existing_search_history[user_email]

        # Add query if we haven't saved 10 most recent yet
        if len(list_of_search_history) < 10:
            list_of_search_history.insert(0, new_search)

        # Otherwise if we already have 10 most recent saved, replace oldest query searched
        else:
            # Delete oldest word (at 10th/last position)
            del list_of_search_history[9]
            # Insert newest word at front of list
            list_of_search_history.insert(0, new_search)

    # Otherwise if this is a new user
    else:
        # Create a new empty list that will be filled as the user searches
        existing_search_history[user_email] = list()

    return existing_search_history[user_email]
