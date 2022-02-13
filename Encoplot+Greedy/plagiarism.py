"""# Plagiarism Class - for document known plagiarism list - used for later evaluation

Members:
  - this_offset
  - this_length
  - source_offset
  - source_length
"""

class Plagiarism():
  def __init__(self, this_offset, this_length, source_reference, source_offset, source_length):
    self.this_offset = this_offset 
    self.this_length = this_length 
    self.source_reference = source_reference
    self.source_offset = source_offset
    self.source_length = source_length