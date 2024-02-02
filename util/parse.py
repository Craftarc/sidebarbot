import urllib.parse

def get_query_parameters(string):
    """
    Get query parameters from a raw URL string
    @param: string: raw URL string
    @return: dict: query string parameters
    """
    query_string = urllib.parse.urlparse(string).query
    query_dict = urllib.parse.parse_qs(query_string)

    return query_dict