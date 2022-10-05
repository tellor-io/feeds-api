

def generate_docs_msg(query_type_string):
    """Generate a message for the docs"""
    msg = f"""
    Reference {query_type_string}.md at https://github.com/tellor-io/dataSpecs/tree/main/types/
    for the Solidity reponse type and more info.
    """
    return msg
