import subprocess
import glob
import re
from document import Document
from predictions import Predictions
from validationMetrics import ValidationMetrics
from featuresList import FeaturesList 

PATH_SOURCE_PART = "documents/source-documents/part"
PATH_SUSPICIOUS_PART = "documents/suspicious-documents/part"
PATH_SOURCE = "documents/source-documents/"
PATH_SUSPICIOUS = "documents/suspicious-documents/"
SUSPICIOUS_DOCUMENT_PREFIX = "suspicious-document"
SOURCE_DOCUMENT_PREFIX = "source-document"

ENCOPLOT_MAX_STEP_DIF = 10
ENCOPLOT_MIN_FOUND_CONSECUTIVE = 30

SOURCE_NO = 14429
SUSPICIOUS_NO = 14428

def check_part_folder(doc_name):
  doc_number = int(doc_name[-5 :])
  return doc_number // 2000 + 1

def extract_sample(samples_sus_number, samples_sources_number):
  sources_list = []
  suspicious_list = []

  for i in range(1, samples_sus_number + 1):
    index = str(i)

    while len(index) < 5:
      index = '0' + index
      
    sus_doc_name =  SUSPICIOUS_DOCUMENT_PREFIX + index
    part_folder = str(check_part_folder(sus_doc_name))
    full_path = PATH_SUSPICIOUS_PART + part_folder + "/" + sus_doc_name + ".txt"

    suspicious_list.append(full_path)

  for i in range(1, samples_sources_number + 1):
    index = str(i)

    while len(index) < 5:
      index = '0' + index
      
    source_doc_name =  SOURCE_DOCUMENT_PREFIX + index
    part_folder = str(check_part_folder(source_doc_name))
    full_path = PATH_SOURCE_PART + part_folder + "/" + source_doc_name + ".txt"

    sources_list.append(full_path)

  return suspicious_list, sources_list

def get_docs(path):
  result = []
  result += glob.glob(path + "*.txt")

  if glob.glob(path + "*/"):
    for dir in glob.glob(path + "*/"):
      result += glob.glob(dir + "*.txt")
  
  return result

class Encoplot:
  def __init__(self, suspicious_doc, source_doc):
    self.current_score = 0
    self.suspicious_posible_offsets = []
    self.source_posible_offsets = []
    
    self.suspicious_doc = suspicious_doc
    self.source_doc = source_doc

    # get the encoplot results
    encoplot_raw_result = str(subprocess.check_output(["./a.out", suspicious_doc, source_doc]))

    # process the results -> a list sorted by the suspicious offset
    encoplot_raw_result = encoplot_raw_result.replace(",'", "")
    encoplot_raw_result = encoplot_raw_result.replace("'", "")
    encoplot_raw_result = encoplot_raw_result.replace("b", "")

    if(len(encoplot_raw_result) == 0):
      return 
      
    encoplot_list = encoplot_raw_result.split(",")

    for it in range(0, len(encoplot_list)):
      encoplot_list[it] = encoplot_list[it].split("-")
      encoplot_list[it][0] = int(encoplot_list[it][0])
      encoplot_list[it][1] = int(encoplot_list[it][1])

    # sort the pairs
    sorting_key = lambda a : a[0]
    encoplot_list.sort(key=sorting_key)

    Succesfullsteps = 0
    lastStep = [0, 0]

    # check the "score" based on the consecutive pairs
    for it in encoplot_list:
      if abs(it[0] - lastStep[0] - it[1] + lastStep[1]) < ENCOPLOT_MAX_STEP_DIF:
        Succesfullsteps += 1
      else:
        Succesfullsteps = 0

      if Succesfullsteps == ENCOPLOT_MIN_FOUND_CONSECUTIVE:
        self.current_score += 1

      lastStep = it

    # it the score is better than 0, save the segments as well
    if self.current_score > 0:
      for it in encoplot_list:
        self.suspicious_posible_offsets.append(it[0])
        self.source_posible_offsets.append(it[1])

def extract_path_and_doc_name(path):
  match = re.compile(r'(\w+.txt|\w+-\w+.txt)')
  
  match_result = match.findall(path)[0]
  path_result = path.replace(match_result, "")
  doc_result = match_result.replace(".txt", "")
  
  return [path_result, doc_result]

def extract_promissing_documents(suspicious_path, source_samples):
  results = []

  for source in source_samples:
    enc = Encoplot(suspicious_path, source)

    if enc.current_score > 0:
      results.append(enc)
  
  results.sort(key=lambda x:x.current_score, reverse=True)

  return results[:10]

def compute_by_extracting():
  sus_sample = get_docs(PATH_SUSPICIOUS)
  source_sample = get_docs(PATH_SOURCE)

  print("suspicios sample: " + str(len(sus_sample)))
  print("sources sample: " + str(len(source_sample)))

  pred_result = Predictions()
  features_list_dic = {}

  metrics = ValidationMetrics()

  debug_count = 1

  for sus in sus_sample:

    encoplot_results = extract_promissing_documents(sus, source_sample)
    doc_path, doc_name = extract_path_and_doc_name(sus)
    sus_doc = Document(doc_path, doc_name)
    features_list_dic[doc_name + ".txt"] = sus_doc.features

    for encoplot in encoplot_results:
      source = encoplot.source_doc

      doc_path, doc_name = extract_path_and_doc_name(source)
      source_doc = Document(doc_path, doc_name)

      sus_doc.offset_list = encoplot.suspicious_posible_offsets
      source_doc.offset_list = encoplot.source_posible_offsets

      current_pred = Predictions()
      current_pred.add_prediction(sus_doc, source_doc)
      pred_result += current_pred

    print(str(debug_count))
    debug_count += 1   

    if debug_count == 100:
      break

  metrics = ValidationMetrics()

  metrics.add_to_evaluate(pred_result, features_list_dic)
  print("Overall score ", metrics.get_overall_score())

def compute_from_file(file):
  f_encoplot = open(file, "r+")

  suspicious_doc = None
  suspicious_doc_path = ""
  suspicious_doc_name = ""

  source_doc = None
  source_doc_path = ""
  source_doc_name = ""

  check_sources = False
  check_sus = False

  metrics = ValidationMetrics()

  pred_result = Predictions()
  features_list_dic = {}

  candidates = []

  cur_line = f_encoplot.readline()

  try:
    while cur_line != "":
      arg = cur_line.split(" ")

      if check_sources == True and check_sus == True:
        check_sources = False
        check_sus = False

        for candidate in candidates:
          full_path = candidate[0]
          suspicious_posible_offsets = candidate[1]
          source_posible_offsets = candidate[2]

          source_doc_path, source_doc_name = extract_path_and_doc_name(full_path)
          source_doc = Document(source_doc_path, source_doc_name)

          suspicious_doc.offset_list = suspicious_posible_offsets
          source_doc.offset_list = source_posible_offsets

          current_pred = Predictions()

          current_pred.add_prediction(suspicious_doc, source_doc)
          pred_result += current_pred

      elif arg[0] == "fsus":
        if check_sus == True and check_sources == False:
          current_pred.add_prediction(suspicious_doc, Document("", ""))
          pred_result += current_pred

        check_sus = True

        full_path = arg[1][:-1]

        suspicious_doc_path, suspicious_doc_name = extract_path_and_doc_name(full_path)
        suspicious_doc = suspicious_doc = Document(suspicious_doc_path, suspicious_doc_name)

        features_list_dic[suspicious_doc_name + ".txt"] = suspicious_doc.features

        print(full_path)
        cur_line = str(f_encoplot.readline())

      elif arg[0] == "fsour":
        candidates = []

        while arg[0] == "fsour":
          full_path = arg[1][:-1]

          suspicious_posible_offsets = []
          source_posible_offsets = []

          cur_line = str(f_encoplot.readline())

          while cur_line[0] == "r":
            arg = cur_line.split(" ")
            suspicious_posible_offsets.append(int(arg[1]))
            source_posible_offsets.append(int(arg[2]))

            cur_line = str(f_encoplot.readline())

          candidates.append([full_path, suspicious_posible_offsets, source_posible_offsets])
          arg = cur_line.split(" ")

        candidates.sort(key=lambda x: len(x[1]), reverse=True)
        candidates = candidates[:10]

        check_sources = True
  
    if check_sus == True and check_sources == False:
      check_sus = False
      current_pred.add_prediction(suspicious_doc, Document("", ""))
      pred_result += current_pred
  except:
    print("Exception was found")

  f_encoplot.close()

  metrics.add_to_evaluate(pred_result, features_list_dic)

  print("Overall score: ", metrics.get_overall_score())

def main():
  compute_from_file("encoplot.txt")


if __name__ == "__main__":
  main()