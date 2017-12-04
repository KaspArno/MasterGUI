class SavedSearch(object):
	attributes = {}

	def add_attribute(self, attribute, current_index):
		self.attributes[attribute] = current_index

	def get_attributes(self):
		return self.attributes