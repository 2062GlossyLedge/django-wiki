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
    # Remove big subheadings for section_content.
    subHeaderLinePattern = r".*?\r\n[=-]+\r\n"
    
    section_content = re.sub(subHeaderLinePattern, '', section_content)
    
    smallHeaderLinePattern = r"#{3,6}.*?\r\n"

    
    section_content = re.sub(smallHeaderLinePattern, '', section_content)
    section_content = section_content.replace("\r","") # Remove lines for easier deciphering
    section_content = section_content.replace("\n","") # Remove lines for easier deciphering
    section_content = section_content.replace(" ","") # Remove spaces for easier deciphering
    
    # Define the regex pattern
    linePattern = r">>.*?\[\*\]\(wiki:[^\)]+\)"
    citationRegex = re.compile(linePattern)

    # Search for the first match
    allmatches = citationRegex.findall(section_content)
    sumMatchChars = 0
    # Iterate over all matches and sum the characters
    for match in allmatches:
        sumMatchChars += len(match)
    
    # If all matches cover the entire section content, return True
    return sumMatchChars == len(section_content)