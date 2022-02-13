SECTION_POSITION_MAX_DIF = 100

"""# Segment class for generic segments

Members:
  - text
  - offset
  - cleaned_text
  - length (optional, default to 0)
"""

class Segment():
  def __init__(self, text, offset, length = 0):
    self.text = text
    self.offset = offset
    self.length = length

    if length == 0:
      self.length = len(text)
    else:
      self.length = length

  def __str__(self):
    result = "offset: " + str(self.offset) + " length: " + str(self.length)
    return result

  def __repr__(self):
    result = "offset: " + str(self.offset) + " length: " + str(self.length)
    return result

  # equal is it has same offset or length or is overlaped or is at less than SECTION_POSITION_MAX_DIF distance
  def __eq__(self, other): 
    s_start = self.offset
    s_end = self.offset + self.length
    o_start = other.offset
    o_end = other.offset + other.length

    if s_start <= o_end and s_start >= o_start or \
        s_start <= o_end and s_start >= o_start or \
        o_end <= s_start and o_end >= s_start or \
        o_start <= s_start and o_start >= s_start:
      return True
    else:
      return False

    return False