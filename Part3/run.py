from inverted_index import InvertedIndex
from output_gui import OutputGUI

inverted_index = InvertedIndex()
gui = OutputGUI()
query = gui.get_query()
results = inverted_index.vector_query(query)
print(results)
gui.set_results(results)
query = gui.get_query()
