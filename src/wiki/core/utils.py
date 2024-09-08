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
    
    metaCitationEndPattern = r"\[\]\(wiki:\/[^\s()]+?\/(?:book\b|tv\b)(?=\s|\))\)"
    citationEndPattern = r"\[\*\]\(wiki:(?:.*?)\/(?:book\/book\d+(?:\/chapter\d+)?|tv\/season\d+(?:\/episode\d+)?)\)"
    citationEndPatternEnd = r"\[\*\]\(wiki:(?:.*?)\/(?:book\/book\d+(?:\/chapter\d+)?|tv\/season\d+(?:\/episode\d+)?)(?:\~(?:book\d+(?:\/chapter\d+)?|season\d+(?:\/episode\d+)?))\)"
    section_content = re.sub(metaCitationEndPattern, r"\g<0>\n", section_content)
    section_content = re.sub(citationEndPattern, r"\g<0>\n", section_content)
    section_content = re.sub(citationEndPatternEnd, r"\g<0>\n", section_content)
    
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
        
        
    endPointCitationPattern = r">>.*?\[\*\]\(wiki:(?:.*?)\/(?:book\/book\d+(?:\/chapter\d+)?|tv\/season\d+(?:\/episode\d+)?)(?:\~(?:book\d+(?:\/chapter\d+)?|season\d+(?:\/episode\d+)?))\)"
    endPointCitationRegex = re.compile(endPointCitationPattern)
    sumMatchCharsEndPoint = 0
    allmatchesEndPoint = endPointCitationRegex.findall(section_content)
    for match in allmatchesEndPoint:
        sumMatchCharsEndPoint += len(match)
        
    section_content = section_content.replace("\n","") # Remove lines for math
    
    # If all matches cover the entire section content, return True
    return (sumMatchChars + sumMatchCharsMeta + sumMatchCharsEndPoint) == len(section_content)

def extractLocationNumbers(text):
    """Extract book/season number and chapter/episode number from the text."""
    match = re.search(r'wiki:(?:.*?)/(?:book|season)(\d+)(?:/(?:chapter(\d+)|episode(\d+)))?', text)
    if match:
        outer_number = int(match.group(1) or 0) # Extract the outer number (book or season)
        inner_number = int(match.group(2) or match.group(3) or 0) # Extract the inner number (chapter or episode)
        return outer_number, inner_number
    return None, None

def extractLocationNumbersEndpoint(text):
    """Extract book/season number and chapter/episode number for both parts of the citation."""
    match = re.search(r'wiki:(?:.*?)/(?:book/book(\d+)(?:/chapter(\d+))?|tv/season(\d+)(?:/episode(\d+))?)'
                      r'(?:~(?:book(\d+)(?:/chapter(\d+))?|season(\d+)(?:/episode(\d+))?))', text)
    if match:
        # Extract first part (book/season and chapter/episode)
        first_outer_number = int(match.group(1) or match.group(3) or 0)  # First book or season number
        first_inner_number = int(match.group(2) or match.group(4) or 0)  # First chapter or episode number
        
        # Extract second part (book/season and chapter/episode)
        second_outer_number = int(match.group(5) or match.group(7) or 0)  # Second book or season number
        second_inner_number = int(match.group(6) or match.group(8) or 0)  # Second chapter or episode number
        
        return first_outer_number, first_inner_number, second_outer_number, second_inner_number
    return None, None, None, None

def removeSpoilerContent(section_content, currentProgress):
    citationPattern = r">>.*?\[\*\]\(wiki:(?:.*?)\/(?:book\/book\d+(?:\/chapter\d+)?|tv\/season\d+(?:\/episode\d+)?)\)"
    citationRegex = re.compile(citationPattern)
    # Filter based on citations without an endpoint
    new_text = section_content
    matches = citationRegex.findall(section_content)
    currentProgressOuter, currentProgressInner = extractLocationNumbers(currentProgress)
    for match in matches:
        matchOuter, matchInner = extractLocationNumbers(match) 
        if (currentProgressOuter < matchOuter) or (matchOuter == currentProgressOuter and currentProgressInner < matchInner):
            start_index = new_text.find(match)
            if start_index != -1:
                end_index = start_index + len(match)
                new_text = new_text[:start_index] + new_text[end_index:]
                
    # Remove citations with an endpoint
    endPointCitationPattern = r">>.*?\[\*\]\(wiki:(?:.*?)\/(?:book\/book\d+(?:\/chapter\d+)?|tv\/season\d+(?:\/episode\d+)?)(?:\~(?:book\d+(?:\/chapter\d+)?|season\d+(?:\/episode\d+)?))\)"
    endPointCitationRegex = re.compile(endPointCitationPattern)
    endpointMatches = endPointCitationRegex.findall(section_content)
    
    for match in endpointMatches:
        matchOuterStart, matchInnerStart, matchOuterEnd, matchInnerEnd = extractLocationNumbersEndpoint(match)
        # Remove match if not in the current section
        if (currentProgressOuter < matchOuterStart) or (currentProgressOuter > matchOuterEnd) or (matchOuterStart == currentProgressOuter and currentProgressInner < matchInnerStart) or (matchOuterEnd == currentProgressOuter and currentProgressInner > matchInnerEnd):
            start_index = new_text.find(match)
            if start_index != -1:
                end_index = start_index + len(match)
                new_text = new_text[:start_index] + new_text[end_index:]    
        #Remove section after tilde
        else:
            start_index = new_text.find(match)
            tilde_index = new_text.find("~", start_index)
            end_index = new_text.find(")", tilde_index)  # Find the closing parenthesis after the tilde
            if tilde_index != -1 and end_index != -1:
                # Keep the part before the tilde and the closing parenthesis
                new_text = new_text[:tilde_index] + new_text[end_index:]
    return new_text
