"""# predictions class

"""

from predictedSegment import PredictedSegment
from segment import Segment
import copy


MAX_STEP_DIF = 10
MIN_FOUND_CONSECUTIVE = 30
MAX_ACCEPTED_FAULTS = 4
MAX_FAULTS_DIF = 200

class Predictions():
  # plagiarism_predicted = []
  # predicted_segments = []
  # _extracted_predicted_segments = []
  # doc_name = ""

  def __init__(self):
    self.plagiarism_predicted = []
    self.current_suspicious_doc = ""
    self.results = {}

  def add_prediction(self, suspicious_doc, source_doc):
    self.current_suspicious_doc = suspicious_doc.doc_name

    self._compute_predictions(suspicious_doc, source_doc)

    if self.current_suspicious_doc not in self.results:
      self.results[self.current_suspicious_doc] = []

    for prediction in self.plagiarism_predicted:
      conflicts = False

      # if prediction.this_segment.length < 
      
      for result in self.results[self.current_suspicious_doc]:
        if prediction.check_same_plagiarism_segment(result):
          conflicts = True
          break

      if not conflicts: # and prediction.similarity_value > TH_COSIN_VALUE:
        # print(prediction)
        self.results[self.current_suspicious_doc].append(prediction)

    self.plagiarism_predicted = []

    return self.results[self.current_suspicious_doc]

  def _compute_predictions(self, suspicious_doc, source_doc):
    cur_sus_segment = Segment("", 0, 0)
    cur_source_segment = Segment("", 0, 0)

    last_sus_offset = -9999
    last_source_offset = -9999

    Succesfullsteps = 0
    current_faults = 0

    new_segment_req = True


    for sus_offset, source_offset in zip(suspicious_doc.offset_list, source_doc.offset_list):
        if new_segment_req:
            new_segment_req = False

            if Succesfullsteps > MIN_FOUND_CONSECUTIVE:
                cur_sus_segment.text = suspicious_doc.text[cur_sus_segment.offset : cur_sus_segment.offset + cur_sus_segment.length]
                cur_source_segment.text = source_doc.text[cur_source_segment.offset : cur_source_segment.offset + cur_source_segment.length]

                self.plagiarism_predicted.append(PredictedSegment(cur_sus_segment, source_doc.doc_name, cur_source_segment))
                # print(cur_sus_segment)
            
            cur_sus_segment = Segment("", sus_offset, 0)
            cur_source_segment = Segment("", source_offset, 0)

            Succesfullsteps = 0
            current_faults = 0

        if abs(sus_offset - last_sus_offset - source_offset + last_source_offset) < MAX_STEP_DIF:
            Succesfullsteps += 1
        else:
            if abs(sus_offset - last_sus_offset - source_offset + last_source_offset) < MAX_FAULTS_DIF:
                current_faults += 1

                if current_faults > MAX_ACCEPTED_FAULTS:
                    new_segment_req = True
            else:
                new_segment_req = True


        cur_sus_segment.length = sus_offset - cur_sus_segment.offset
        cur_source_segment.length = source_offset - cur_source_segment.offset
        
        last_sus_offset = sus_offset
        last_source_offset = source_offset

  def __add__(self, other_pred):
    add_result = copy.deepcopy(self)

    for doc_name in other_pred.results:
      add_result.current_suspicious_doc = doc_name   

      if doc_name not in add_result.results:
        add_result.results[add_result.current_suspicious_doc] = []

      for prediction in other_pred.results[doc_name]:
        conflicts = False
        
        for result in add_result.results[doc_name]:
          if prediction.check_same_plagiarism_segment(result):
            conflicts = True
            break

        if not conflicts: # and prediction.similarity_value > TH_COSIN_VALUE:
          add_result.results[add_result.current_suspicious_doc].append(prediction)

    return add_result