from django.http.response import JsonResponse
import re

def object_to_json_response(obj, status=200):
    """
    Given an object, returns an HttpResponse object with a JSON serialized
    version of that object
    """
    return JsonResponse(
        data=obj,
        status=status,
        safe=False,
        json_dumps_params={"ensure_ascii": False},
    )
    
def allTextHasCitations(section):
    """
    Returns true if all of the text of the section excluding header has a citation, false if not
    """
    section_content = section + "\r\n"
    
    # Remove pipe seperators for section content. In effect, this makes table headers deciphered as regular headers (and thus ignored) 
    # Additionally, it makes the contents of a table still require citations.
    section_content = section_content.replace(" | ","") 
    
    # Remove big subheadings for section_content.
    subHeaderLinePattern = r".*?\r\n[=-]+\r\n"
    section_content = re.sub(subHeaderLinePattern, '', section_content)
    
    # Remove small subheadings for section_content
    smallHeaderLinePattern = r"#{3,6}.*?\r\n"
    section_content = re.sub(smallHeaderLinePattern, '', section_content)
    
    # Remove automatic sub-articles list from citation requirement.
    articleListPattern = r'\[article_list depth:\d+\]'
    section_content = re.sub(articleListPattern, '', section_content)
    
    # Remove automatic Table of Contents from citation requirement.
    TOCPattern = r'\[TOC(?:\s+(?:title|baselevel|separator|anchorlink|anchorlink_class|permalink|permalink_class|permalink_title|toc_depth):(?:\S+|"[^"]*"))*\]'
    section_content = re.sub(TOCPattern, '', section_content)
    
    section_content = section_content.replace("\r","") # Remove lines for easier deciphering
    section_content = section_content.replace("\n","") # Remove lines for easier deciphering
    section_content = section_content.replace(" ","") # Remove spaces for easier deciphering
    
    # Add newline between each citation section to seperate
    eitherCitationPattern = r">>.*?\(wiki(.*?)\)"
    section_content = re.sub(eitherCitationPattern, r"\g<0>\n", section_content)
    
    # Define the regex pattern of citations, and count
    citationPattern = r">>.*?\[\*\]\(wiki:(?:.*?)\/(?:book\/book\d+(?:\/chapter\d+)?|tv\/season\d+(?:\/episode\d+)?)\)"
    citationRegex = re.compile(citationPattern)

    allmatches = citationRegex.findall(section_content)
    sumMatchChars = 0
    # Iterate over all matches and sum the characters
    for match in allmatches:
        sumMatchChars += len(match)
        
    metaCitationPattern = r">>.*?\[\]\(wiki:\/[^\s()]+?\/(?:book\b|tv\b)(?=\s|\))\)"
    metaCitationRegex = re.compile(metaCitationPattern)
    sumMatchCharsMeta = 0
    allmatchesMeta = metaCitationRegex.findall(section_content)
    for match in allmatchesMeta:
        sumMatchCharsMeta += len(match)
        
    section_content = section_content.replace("\n","") # Remove lines for math
    
    # If all matches cover the entire section content, return True
    return (sumMatchChars + sumMatchCharsMeta) == len(section_content)