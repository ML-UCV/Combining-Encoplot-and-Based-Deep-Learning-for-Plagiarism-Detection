import xml.etree.ElementTree as ET
from plagiarism import Plagiarism

"""# FeatureList class - used for document known features

Members:
  - plagiarism_list
"""

class FeaturesList():
  def __init__(self, path):
    self.plagiarism_list = []

    document = ET.parse(path)
    root = document.getroot()

    for child in root:

      # Check language
      if child.attrib['name'] == "language":
        lan = child.attrib['value']

        if lan == "en":
          self.language = "english"
        elif lan == "de":
          self.language = "german"
        elif lan == "es":
          self.language = "spanish"
        else:
          self.language = "english"

      # check plagiarism list (if it is the case)
      if child.attrib['name'] == "artificial-plagiarism":
        this_offset = child.attrib['this_offset']
        this_length = child.attrib['this_length']
        source_reference = child.attrib['source_reference']
        source_offset = child.attrib['source_offset']
        source_length = child.attrib['source_length']
        
        self.plagiarism_list.append(Plagiarism(this_offset, this_length, source_reference, source_offset, source_length))