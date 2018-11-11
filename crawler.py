
# Copyright (C) 2011 by Peter Goodman
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import urllib2
import urlparse
from bs4 import BeautifulSoup
from bs4 import Tag
from collections import defaultdict
from sets import Set
import re

# CSC326 Lab 3 - BEGIN
from pagerank import *
import sqlite3
import os
from operator import itemgetter
# CSC326 Lab 3 - END

def attr(elem, attr):
    """An html attribute from an html element. E.g. <a href="">, then
    attr(elem, "href") will get the href or an empty string."""
    try:
        return elem[attr]
    except:
        return ""

WORD_SEPARATORS = re.compile(r'\s|\n|\r|\t|[^a-zA-Z0-9\-_]')

class crawler(object):
    """Represents 'Googlebot'. Populates a database by crawling and indexing
    a subset of the Internet.

    This crawler keeps track of font sizes and makes it simpler to manage word
    ids and document ids."""

    def __init__(self, db_conn, url_file):
        """Initialize the crawler with a connection to the database to populate
        and with the file containing the list of seed URLs to begin indexing."""
        self._url_queue = [ ]
        self._doc_id_cache = { }
        self._word_id_cache = { }

        # CSC326 Lab 1 - BEGIN
        # declare data structures
        self._revert_doc_id = { } # stores the url that corresponds to a doc_id
        self._revert_word_id = { } # stores the word that corresponds to a word_id

        self._doc_index = defaultdict(set) # stores the word_id's that correspond to a doc_id
        self._inverted_index = defaultdict(set) # stores doc_id's that correspond to a word_id
        self._resolved_inverted_index = defaultdict(set) # stores url's that correspond to a word

        self._page_title = { } # stores the title of each web page
        self._page_description = { } # stores the first line of each web page
        # CSC326 Lab 1 - END

        # CSC326 Lab 3 - BEGIN
        self._links = [ ]
        self._url_ranks = [ ]
        self._inverted_index_db = [ ]
        # CSC326 Lab 3 - END

        # functions to call when entering and exiting specific tags
        self._enter = defaultdict(lambda *a, **ka: self._visit_ignore)
        self._exit = defaultdict(lambda *a, **ka: self._visit_ignore)

        # add a link to our graph, and indexing info to the related page
        self._enter['a'] = self._visit_a

        # record the currently indexed document's title an increase
        # the font size
        def visit_title(*args, **kargs):
            self._visit_title(*args, **kargs)
            self._increase_font_factor(7)(*args, **kargs)

        # increase the font size when we enter these tags
        self._enter['b'] = self._increase_font_factor(2)
        self._enter['strong'] = self._increase_font_factor(2)
        self._enter['i'] = self._increase_font_factor(1)
        self._enter['em'] = self._increase_font_factor(1)
        self._enter['h1'] = self._increase_font_factor(7)
        self._enter['h2'] = self._increase_font_factor(6)
        self._enter['h3'] = self._increase_font_factor(5)
        self._enter['h4'] = self._increase_font_factor(4)
        self._enter['h5'] = self._increase_font_factor(3)
        self._enter['title'] = visit_title

        # decrease the font size when we exit these tags
        self._exit['b'] = self._increase_font_factor(-2)
        self._exit['strong'] = self._increase_font_factor(-2)
        self._exit['i'] = self._increase_font_factor(-1)
        self._exit['em'] = self._increase_font_factor(-1)
        self._exit['h1'] = self._increase_font_factor(-7)
        self._exit['h2'] = self._increase_font_factor(-6)
        self._exit['h3'] = self._increase_font_factor(-5)
        self._exit['h4'] = self._increase_font_factor(-4)
        self._exit['h5'] = self._increase_font_factor(-3)
        self._exit['title'] = self._increase_font_factor(-7)

        # never go in and parse these tags
        self._ignored_tags = set([
            'meta', 'script', 'link', 'meta', 'embed', 'iframe', 'frame',
            'noscript', 'object', 'svg', 'canvas', 'applet', 'frameset',
            'textarea', 'style', 'area', 'map', 'base', 'basefont', 'param',
        ])

        # set of words to ignore
        self._ignored_words = set([
            '', 'the', 'of', 'at', 'on', 'in', 'is', 'it',
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
            'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
            'u', 'v', 'w', 'x', 'y', 'z', 'and', 'or',
        ])

        # TODO remove me in real version
        self._mock_next_doc_id = 1
        self._mock_next_word_id = 1

        # keep track of some info about the page we are currently parsing
        self._curr_depth = 0
        self._curr_url = ""
        self._curr_doc_id = 0
        self._font_size = 0
        self._curr_words = None

        # get all urls into the queue
        try:
            with open(url_file, 'r') as f:
                for line in f:
                    self._url_queue.append((self._fix_url(line.strip(), ""), 0))
        except IOError:
            pass

    # TODO remove me in real version
    def _mock_insert_document(self, url):
        """A function that pretends to insert a url into a document db table
        and then returns that newly inserted document's id."""
        ret_id = self._mock_next_doc_id
        self._mock_next_doc_id += 1
        return ret_id

    # TODO remove me in real version
    def _mock_insert_word(self, word):
        """A function that pretends to inster a word into the lexicon db table
        and then returns that newly inserted word's id."""
        ret_id = self._mock_next_word_id
        self._mock_next_word_id += 1
        return ret_id

    def word_id(self, word):
        """Get the word id of some specific word."""
        if word in self._word_id_cache:
            return self._word_id_cache[word]

        # TODO: 1) add the word to the lexicon, if that fails, then the
        #          word is in the lexicon
        #       2) query the lexicon for the id assigned to this word,
        #          store it in the word id cache, and return the id.

        word_id = self._mock_insert_word(word)
        self._word_id_cache[word] = word_id

        # CSC326 Lab 1 - BEGIN
        self._revert_word_id[word_id] = word
        # CSC326 Lab 1 - END

        return word_id

    def document_id(self, url):
        """Get the document id for some url."""
        if url in self._doc_id_cache:
            return self._doc_id_cache[url]

        # TODO: just like word id cache, but for documents. if the document
        #       doesn't exist in the db then only insert the url and leave
        #       the rest to their defaults.

        doc_id = self._mock_insert_document(url)
        self._doc_id_cache[url] = doc_id

        # CSC326 Lab 1 - BEGIN
        self._revert_doc_id[doc_id] = url
        # CSC326 Lab 1 - END

        return doc_id

    def _fix_url(self, curr_url, rel):
        """Given a url and either something relative to that url or another url,
        get a properly parsed url."""

        rel_l = rel.lower()
        if rel_l.startswith("http://") or rel_l.startswith("https://"):
            curr_url, rel = rel, ""

        # compute the new url based on import
        curr_url = urlparse.urldefrag(curr_url)[0]
        parsed_url = urlparse.urlparse(curr_url)
        return urlparse.urljoin(parsed_url.geturl(), rel)

    def add_link(self, from_doc_id, to_doc_id):
        """Add a link into the database, or increase the number of links between
        two pages in the database."""
        # TODO

        # CSC326 Lab 3 - BEGIN
        self._links.append((from_doc_id, to_doc_id))
        # CSC326 Lab 3 - END

    def _visit_title(self, elem):
        """Called when visiting the <title> tag."""
        title_text = self._text_of(elem).strip()
        #print "document title="+ repr(title_text)      #CSC326 Lab 1

        # TODO update document title for document id self._curr_doc_id

        # CSC326 Lab 1 - BEGIN
        self._page_title[self._curr_doc_id] = title_text
        # CSC326 Lab 1 - END

    def _visit_a(self, elem):
        """Called when visiting <a> tags."""

        dest_url = self._fix_url(self._curr_url, attr(elem,"href"))

        #print "href="+repr(dest_url), \
        #      "title="+repr(attr(elem,"title")), \
        #      "alt="+repr(attr(elem,"alt")), \
        #      "text="+repr(self._text_of(elem))

        # add the just found URL to the url queue
        self._url_queue.append((dest_url, self._curr_depth))

        # add a link entry into the database from the current document to the
        # other document
        self.add_link(self._curr_doc_id, self.document_id(dest_url))

        # TODO add title/alt/text to index for destination url

    def _add_words_to_document(self):
        # TODO: knowing self._curr_doc_id and the list of all words and their
        #       font sizes (in self._curr_words), add all the words into the
        #       database for this document

        # CSC326 Lab 1 - BEGIN
        for word in self._curr_words:
            _curr_word_id = word[0] # get the word_id
            _curr_word = self._revert_word_id[_curr_word_id] # get the word that corresponds to the word_id

            self._doc_index[self._curr_doc_id].add(_curr_word_id)
            self._inverted_index[_curr_word_id].add(self._curr_doc_id)
            self._resolved_inverted_index[_curr_word].add(self._curr_url)
        # CSC326 Lab 1 - END

        # CSC326 Lab 3 - BEGIN
            self._inverted_index_db.append((_curr_word_id, self._curr_doc_id))
        # CSC326 Lab 3 - END

        #print "    num words="+ str(len(self._curr_words))     # CSC326 Lab 1

    def _increase_font_factor(self, factor):
        """Increade/decrease the current font size."""
        def increase_it(elem):
            self._font_size += factor
        return increase_it

    def _visit_ignore(self, elem):
        """Ignore visiting this type of tag"""
        pass

    def _add_text(self, elem):
        """Add some text to the document. This records word ids and word font sizes
        into the self._curr_words list for later processing."""
        words = WORD_SEPARATORS.split(elem.string.lower())
        for word in words:
            word = word.strip()
            if word in self._ignored_words:
                continue
            self._curr_words.append((self.word_id(word), self._font_size))

    def _text_of(self, elem):
        """Get the text inside some element without any tags."""
        if isinstance(elem, Tag):
            text = [ ]
            for sub_elem in elem:
                text.append(self._text_of(sub_elem))

            return " ".join(text)
        else:
            return elem.string

    def _index_document(self, soup):
        """Traverse the document in depth-first order and call functions when entering
        and leaving tags. When we come accross some text, add it into the index. This
        handles ignoring tags that we have no business looking at."""
        class DummyTag(object):
            next = False
            name = ''

        class NextTag(object):
            def __init__(self, obj):
                self.next = obj

        tag = soup.html
        stack = [DummyTag(), soup.html]

        # CSC326 Lab 3 - BEGIN
        top_of_page = 10 # just landed on the web page
        page_description = ""
        # CSC326 Lab 3 - END

        while tag and tag.next:
            tag = tag.next

            # html tag
            if isinstance(tag, Tag):

                if tag.parent != stack[-1]:
                    self._exit[stack[-1].name.lower()](stack[-1])
                    stack.pop()

                tag_name = tag.name.lower()

                # ignore this tag and everything in it
                if tag_name in self._ignored_tags:
                    if tag.nextSibling:
                        tag = NextTag(tag.nextSibling)
                    else:
                        self._exit[stack[-1].name.lower()](stack[-1])
                        stack.pop()
                        tag = NextTag(tag.parent.nextSibling)

                    continue

                # enter the tag
                self._enter[tag_name](tag)
                stack.append(tag)

            # text (text, cdata, comments, etc.)
            else:
                self._add_text(tag)

                # CSC326 Lab 3 - BEGIN
                page_text = self._text_of(tag).strip()
                if page_text is None or page_text == "":
                    continue

                if top_of_page > 0:
                    page_description += page_text
                    page_description += "... "
                    top_of_page -= 1
                # CSC326 Lab 3 - END

        # Remove the character '\u2013' and '\ from each page description
        #page_description.replace("\u2013", " ")
        #page_description.replace("\xe8", "")

        # page_description = str(page_description)

        print(page_description)
        self._page_description[self._curr_doc_id] = str(page_description)

    def crawl(self, depth=2, timeout=3):
        """Crawl the web!"""
        seen = set()

        while len(self._url_queue):

            url, depth_ = self._url_queue.pop()

            # skip this url; it's too deep
            if depth_ > depth:
                continue

            doc_id = self.document_id(url)

            # we've already seen this document
            if doc_id in seen:
                continue

            seen.add(doc_id) # mark this document as haven't been visited

            socket = None
            try:
                socket = urllib2.urlopen(url, timeout=timeout)
                soup = BeautifulSoup(socket.read(), features="html.parser")

                self._curr_depth = depth_ + 1
                self._curr_url = url
                self._curr_doc_id = doc_id
                self._font_size = 0
                self._curr_words = [ ]
                self._index_document(soup)
                self._add_words_to_document()
                #print "    url="+repr(self._curr_url)          #CSC326 Lab 1

            except Exception as e:
                #print e                                        #CSC326 Lab 1
                pass
            finally:
                if socket:
                    socket.close()

        # CSC326 Lab 3 - BEGIN

        # Remove duplicate tuples
        self._links = set(self._links)
        self._links = list(self._links)

        # Run PageRank algorithm
        self._url_ranks = page_rank(self._links)

        # Remove dbFile.db if it's in the current directory
        try:
            os.remove('dbFile.db')
        except:
            pass

        con = sqlite3.connect('dbFile.db')
        cur = con.cursor()

        # Store lexicon to persistent storage
        cur.execute("CREATE TABLE lexicon (word text, word_id integer)")
        cur.executemany("INSERT INTO lexicon VALUES (?, ?)", self._word_id_cache.items())

        # Store inverted index to persistent storage
        cur.execute("CREATE TABLE inverted_index (word_id integer, doc_id integer)")
        cur.executemany("INSERT INTO inverted_index VALUES (?, ?)", self._inverted_index_db)

        # Store PageRank to persistent storage
        cur.execute("CREATE TABLE PageRank (doc_id integer, PageRank real)")
        cur.executemany("INSERT INTO PageRank VALUES (?, ?)", self._url_ranks.items())

        # Store document index to persistent storage
        cur.execute("CREATE TABLE document_index (doc_id integer, url text)")
        cur.executemany("INSERT INTO document_index VALUES (?, ?)", self._revert_doc_id.items())

        # Store page title to persistent storage
        cur.execute("CREATE TABLE page_title (doc_id integer, title text)")
        cur.executemany("INSERT INTO page_title VALUES (?, ?)", self._page_title.items())

        # Store page description to persistent storage
        cur.execute("CREATE TABLE page_description (doc_id integer, description text)")
        cur.executemany("INSERT INTO page_description VALUES (?, ?)", self._page_description.items())

        con.commit()
        con.close()

        # CSC326 Lab 3 - END

    # CSC326 Lab 1 - BEGIN
    def get_doc_index(self):
        return dict(self._doc_index)

    def get_inverted_index(self):
        return dict(self._inverted_index)

    def get_resolved_inverted_index(self):
        return dict(self._resolved_inverted_index)

    def get_page_title(self, doc_id):
        page_title = self._page_title[doc_id]
        return page_title

    def get_page_description(self, doc_id):
        page_description = self._page_description[doc_id]
        return page_description
    # CSC326 Lab 1 - END

    # CSC326 Lab 3 - BEGIN

    # Test functions
    def get_links(self):
        links = self._links
        return links

    def get_unsorted_pagerank(self):
        pagerank = self._url_ranks.items()
        return pagerank

    def get_sorted_pagerank(self):
        pagerank = self._url_ranks.items()
        sorted_pagerank = [ ]

        # Sort by decreasing PageRank score
        for tuple in sorted(pagerank, key=itemgetter(1)):
            sorted_pagerank.append(tuple)

        sorted_pagerank.reverse()
        return sorted_pagerank

    def get_unsorted_pagerank_url(self):
        pagerank = self._url_ranks.items()
        unsorted_pagerank = [ ]

        for item in pagerank:
            temp = list(item)
            url = self._revert_doc_id[temp[0]]
            unsorted_pagerank.append((url, temp[1]))

        return unsorted_pagerank

    def get_sorted_pagerank_url(self):
        pagerank = self._url_ranks.items()
        sorted_pagerank = [ ]

        # Sort by decreasing PageRank score
        for item in sorted(pagerank, key=itemgetter(1)):
            temp = list(item)
            url = self._revert_doc_id[temp[0]]
            sorted_pagerank.append((url, temp[1]))

        sorted_pagerank.reverse()
        return sorted_pagerank

    # Helper functions

    # word --> word_id
    def get_word_id(self, word):
        if word is None or word not in self._word_id_cache:
            return None

        word_id = self._word_id_cache[word]
        return word_id

    # word_id --> doc_id
    def get_doc_id(self, word_id):
        doc_id = [ ]

        if word_id is None:
            return doc_id

        doc_id = self._inverted_index[word_id]
        return doc_id

    # doc_id --> url_ranks
    def get_url_ranks(self, doc_id):
        url_ranks = [ ]

        if doc_id is None:
            return url_ranks

        urls = set(doc_id).intersection(self._url_ranks)
        url_ranks = {i:self._url_ranks[i] for i in urls}
        url_ranks = url_ranks.items()

        return url_ranks

    # url_ranks --> sorted_doc_ids
    def get_sorted_doc_ids(self, url_ranks):
        sorted_doc_ids = [ ]

        if url_ranks is None:
            return sorted_doc_ids

        # Sort by decreasing PageRank score
        for doc_id in sorted(url_ranks, key=itemgetter(1)):
            sorted_doc_ids.append(doc_id[0])

        sorted_doc_ids.reverse()
        return sorted_doc_ids

    # sorted_doc_ids --> sorted_urls
    def get_sorted_urls(self, sorted_doc_ids):
        sorted_urls = [ ]

        if sorted_doc_ids is None:
            return sorted_urls

        for doc_id in sorted_doc_ids:
            url = self._revert_doc_id[doc_id]

            if doc_id in self._page_title:
                title = self._page_title[doc_id]
            else:
                title = ""

            if doc_id in self._page_description:
                description = self._page_description[doc_id]
            else:
                description = ""

            sorted_urls.append((url, title, description))

        return sorted_urls

    # Main functions
    # Combining all helper functions into one

    def get_results(self, word):
        sorted_urls = [ ]

        if word is None or word not in self._word_id_cache:
            return sorted_urls

        # word --> word_id
        word_id = self._word_id_cache[word]

        # word_id --> doc_id
        doc_id = self._inverted_index[word_id]

        # doc_id --> url_ranks
        urls = set(doc_id).intersection(self._url_ranks)
        url_ranks = {i:self._url_ranks[i] for i in urls}
        url_ranks = url_ranks.items()

        # url_ranks --> sorted_doc_ids
        sorted_doc_ids = [ ]
        for doc_id in sorted(url_ranks, key=itemgetter(1)):
            sorted_doc_ids.append(doc_id[0])

        sorted_doc_ids.reverse()

        # sorted_doc_ids --> sorted_urls
        for doc_id in sorted_doc_ids:
            url = self._revert_doc_id[doc_id]

            if doc_id in self._page_title:
                title = self._page_title[doc_id]
            else:
                title = ""

            if doc_id in self._page_description:
                description = self._page_description[doc_id]
            else:
                description = ""

            sorted_urls.append((url, title, description))

        return sorted_urls

    # End of class definition for crawler

    # CSC326 Lab 3 - END

# CSC326 Lab 3 - BEGIN

# word --> word_id
def get_word_id_db(word):
    if word is None:
        return None

    con = sqlite3.connect('dbFile.db')
    cur = con.cursor()

    printcur = cur.execute("SELECT * FROM lexicon WHERE word = '%s'" % word)
    word_id = printcur.fetchone()
    if word_id is None:
        return None
    word_id = word_id[1]

    return word_id

# word_id --> doc_id
def get_doc_id_db(word_id):
    doc_id = [ ]

    if word_id is None:
        return doc_id

    con = sqlite3.connect('dbFile.db')
    cur = con.cursor()

    printcur = cur.execute("SELECT * FROM inverted_index WHERE word_id = '%d'" % word_id)
    doc_id_list = printcur.fetchall()

    doc_id = [ ]
    for key, value in doc_id_list:
        doc_id.append(value)
        # Each tuple in doc_id_list has its key = word_id

    # Remove duplicate tuples
    doc_id = set(doc_id)
    doc_id = list(doc_id)

    return doc_id

# doc_id --> url_ranks
def get_url_ranks_db(doc_id):
    url_ranks = [ ]

    if doc_id is None:
        return url_ranks

    con = sqlite3.connect('dbFile.db')
    cur = con.cursor()

    for doc in doc_id:
        printcur = cur.execute("SELECT * FROM PageRank WHERE doc_id = '%d'" % doc)
        pair = printcur.fetchone()
        if pair is not None:
            url_ranks.append(pair)

    return url_ranks

# url_ranks --> sorted_doc_ids
def get_sorted_doc_ids_db(url_ranks):
    sorted_doc_ids = [ ]

    if url_ranks is None:
        return sorted_doc_ids

    # Sort by descending PageRank score
    for doc_id in sorted(url_ranks, key=itemgetter(1)):
        sorted_doc_ids.append(doc_id)

    sorted_doc_ids.reverse()
    return sorted_doc_ids

# sorted_doc_ids --> sorted_urls
def get_sorted_urls_db(sorted_doc_ids):
    sorted_urls = [ ]

    if sorted_doc_ids is None:
        return sorted_urls

    con = sqlite3.connect('dbFile.db')
    cur = con.cursor()

    sorted_urls = [ ]
    if sorted_doc_ids is None:
        return sorted_urls

    for doc_id in sorted_doc_ids:
        printcur = cur.execute("SELECT * FROM document_index WHERE doc_id = '%d'" % doc_id[0])
        item = printcur.fetchone()
        sorted_urls.append((item[1], item[2], item[3]))
    return sorted_urls

def get_results_db(word):

    con = sqlite3.connect('dbFile.db')
    cur = con.cursor()

    sorted_urls = [ ]

    # word --> word_id
    printcur = cur.execute("SELECT * FROM lexicon WHERE word = '%s'" % word)
    word_id = printcur.fetchone()
    if word_id is None:
        return sorted_urls
    word_id = word_id[1]

    # word_id --> doc_id
    printcur = cur.execute("SELECT * FROM inverted_index WHERE word_id = '%d'" % word_id)
    doc_id_list = printcur.fetchall()

    doc_id = [ ]
    for key, value in doc_id_list:
        doc_id.append(value)

    doc_id = set(doc_id)
    doc_id = list(doc_id)

    # doc_id --> url_ranks
    url_ranks = [ ]
    for doc in doc_id:
        printcur = cur.execute("SELECT * FROM PageRank WHERE doc_id = '%d'" % doc)
        pair = printcur.fetchone()
        if pair is not None:
            url_ranks.append(pair)

    # url_ranks --> sorted_doc_ids
    sorted_doc_ids = [ ]
    for doc_id in sorted(url_ranks, key=itemgetter(1)):
        sorted_doc_ids.append(doc_id)

    sorted_doc_ids.reverse()

    # sorted_doc_ids --> sorted_urls
    for doc_id in sorted_doc_ids:
        printcur = cur.execute("SELECT * FROM document_index WHERE doc_id = '%d'" % doc_id[0])
        url = printcur.fetchone()

        printcur = cur.execute("SELECT * FROM page_title WHERE doc_id = '%d'" % doc_id[0])
        title = printcur.fetchone()

        printcur = cur.execute("SELECT * FROM page_title WHERE doc_id = '%d'" % doc_id[0])
        description = printcur.fetchone()

        url = url[1]

        if title is None:
            title = ""
        else:
            title = title[1]

        if description is None:
            description = ""
        else:
            description = description[1]

        sorted_urls.append((url, title, description))

    return sorted_urls

# CSC326 Lab 3 - END

if __name__ == "__main__":
    bot = crawler(None, "urls.txt")
    bot.crawl(depth=1)                                          #CSC326 Lab 1
