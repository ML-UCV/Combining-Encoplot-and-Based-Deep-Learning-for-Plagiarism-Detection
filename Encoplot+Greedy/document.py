from featuresList import FeaturesList
from nltk.corpus import stopwords
from segment import Segment
import re

"""# Document class - containing document features, segments, and embeddings

Members:
  - text
  - features
  - doc_name
  - segments
"""

class Document():
  def __init__(self, path, doc_name):
    try:
      file = open(path + doc_name + ".txt", "r")
      self.text = file.read() 
      file.close()

      self.features = FeaturesList(path + doc_name + ".xml")
      self.doc_name = doc_name + ".txt"
      self.offset_list = []
      self.segments = []
    except:
      self.text = ""
      self.doc_name = ""
      self.offset_list = []
      self.segments = []
      print("Files not found")
