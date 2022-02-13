from segment import Segment

class PredictedSegment():
  def __init__(self, this_segment, source_reference, source_segment):
    self.this_segment = this_segment
    self.source_reference = source_reference
    self.source_segment = source_segment

  def __str__(self):
    result = "source_ref: " + self.source_reference + " this_segment: " + str(self.this_segment) + " source_segment: " + str(self.source_segment) +  " similarity_value: " + str(self.similarity_value) 
    return result

  def __repr__(self):
    result = "source_ref: " + self.source_reference + "this_segment: " + str(self.this_segment) + " source_segment: " + str(self.source_segment) +  " similarity_value: " + str(self.similarity_value) 
    return result

  def __eq__(self, other): 
    if self.this_segment == other.this_segment and self.source_segment == other.source_segment:
      return True
    else:
      return False

  def check_same_plagiarism_segment(self, other):
    if self.this_segment == other.this_segment:
      return True
    else:
      return False