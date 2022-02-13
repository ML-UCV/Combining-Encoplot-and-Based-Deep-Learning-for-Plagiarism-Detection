import math

"""# Validation metrics"""

class ValidationMetrics:
  def __init__(self):
    self.true_positive = 0
    self.false_positive = 0
    self.false_negative = 0

    self.true_positive_list = [] # the segment
    self.false_positive_list = [] # the segment
    self.false_negative_list = [] # just the length

    self.feature_checklist = [] # in order to find the false positive

    self.recall = 0
    self.precision = 0
    self.n_features = 0
    self.n_prec = 0
    self.gran = 0

    self.prev_doc = ""

  def is_overlaping(self, actual_start, actual_end, pred_start, pred_end):
    if actual_start <= pred_end and actual_start >= pred_start or \
        actual_end <= pred_end and actual_end >= pred_start or \
        pred_end <= actual_end and pred_end >= actual_start or \
        pred_start <= actual_end and pred_start >= actual_start:
      return True
    else:
      return False

  def get_recall(self, actual_start, actual_length, source_name, predictions):
    covered = 0
    overlaped = 0

    actual_start = int(actual_start)
    actual_length = int(actual_length)
    actual_end = int(actual_start + actual_length)

    for pred in predictions:
      pred_start = int(pred.this_segment.offset)
      pred_length = int(pred.this_segment.length)
      pred_end = int(pred_start + pred_length)
      
      if self.is_overlaping(actual_start, actual_end, pred_start, pred_end) and \
          pred.source_reference == source_name:

        if actual_start >= pred_start:
          if actual_end >= pred_end:
            covered += pred_length - (actual_start - pred_start)
          else:
            covered += actual_length
        else:
          if actual_end >= pred_end:
            covered += pred_length
          else:
            covered += pred_length - (pred_end - actual_end)
    
    # Check the false negative 
    if covered == 0:
      self.false_negative += 1
      self.false_negative_list.append(actual_length)

    return covered / actual_length

  def get_precision(self, pred_start, pred_length, source_name, features_list):
    covered = 0
    overlaped = 0

    pred_start = int(pred_start)
    pred_length = int(pred_length)
    pred_end = int(pred_start + pred_length)

    positive_found = False

    for feature in features_list:  
      actual_start = int(feature.this_offset)
      actual_length = int(feature.this_length)
      actual_end = int(actual_start + actual_length)
      
      if self.is_overlaping(actual_start, actual_end, pred_start, pred_end) and \
          feature.source_reference == source_name:

        self.true_positive += 1
        positive_found = True # true positive counter  

        if actual_start >= pred_start:
          if actual_end >= pred_end:
            covered += pred_length - (actual_start - pred_start)
          else:
            covered += actual_length
        else:
          if actual_end >= pred_end:
            covered += pred_length
          else:
            covered += pred_length - (pred_end - actual_end)

    if not positive_found:
      self.false_positive += 1
      
    return covered / pred_length

  def get_granularity(self, actual_start, actual_length, source_name, predictions):
    covered = 0
    overlaped = 0

    actual_start = int(actual_start)
    actual_length = int(actual_length)
    actual_end = int(actual_start + actual_length)      

    for pred in predictions:
      pred_start = int(pred.this_segment.offset)
      pred_length = int(pred.this_segment.length)
      pred_end = int(pred_start + pred_length)
      
      if self.is_overlaping(actual_start, actual_end, pred_start, pred_end) and \
          pred.source_reference == source_name:
        covered += 1

    if covered == 0:
      return 1
    else:
      return covered

  def get_f1(self, precision, recall):
    try:
      return 2 * (precision * recall) / (precision + recall)
    except:
      return 0

  def add_to_evaluate(self, predictions_res, features_dict):
    for feature_key in features_dict: # features_key = the doc name
      for feature in features_dict[feature_key].plagiarism_list:
        if feature_key in predictions_res.results:
          self.recall += self.get_recall(feature.this_offset, feature.this_length, feature.source_reference, predictions_res.results[feature_key])
          self.gran += self.get_granularity(feature.this_offset, feature.this_length, feature.source_reference, predictions_res.results[feature_key])
        else:
          self.gran += 1
        
        self.n_features += 1

    for result_key in predictions_res.results: # result_key = the doc name
      for pred in predictions_res.results[result_key]:
        pred_prec = self.precision # for false/true positive
        self.precision += self.get_precision(pred.this_segment.offset, pred.this_segment.length, pred.source_reference, features_dict[result_key].plagiarism_list)
        self.n_prec += 1

        if pred_prec != self.precision:
          self.false_positive_list.append(pred)
        else:
          self.true_positive_list.append(pred)


  def get_overall_score(self):
    if self.n_prec == 0:
      if self.n_features == 0:
        print("No plagiarism")
        return "No plagiarism"

    if self.n_features != 0:
      self.recall /= self.n_features
      print("Recall: ", self.recall)

    if self.n_prec != 0:
      self.precision /= self.n_prec
      print("Precision: ", self.precision)

    if self.n_features != 0:
      self.gran /= self.n_features
      print("Granularity: ", self.gran)
    else:
      self.gran = 1

    if self.precision != 0 and self.recall != 0:
      f1 = self.get_f1(self.precision, self.recall)
    else:
      f1 = 0

    print("F1: ", f1)
    # for feature in doc.features.plagiarism_list:
      # actual_offset = feature.this_offset
      # actual_length = feature.this_offset
      # actual_end = actual_offset + actual_offset

    print("True positive: ", self.true_positive)
    print("False positive: ", self.false_positive)
    print("False negative: ", self.false_negative)

    return f1 / math.log(self.gran + 1, 2)