class JointProbabilityTable:
	def __init__(self, columns, data):
		self._columns = columns
		self._probability_index = len(columns)
		self._data = self._normalize(data)
	def _normalize(self, data):
		probability_sum = 0
		for row in data:
			probability_sum += row[-1]
		for row in data:
			row[-1] = row[-1]/probability_sum
		return data
	def given(self, event_name, event_happened_value):
		contextual_columns = [entry for entry in self._columns if entry != event_name]
		contextual_data = []
		event_column_index = self._columns.index(event_name)
		probability_sum = 0
		for row in self._data:
			if row[event_column_index] == event_happened_value:
				new_row = [entry for i, entry in enumerate(row) if i != event_column_index]
				probability_sum += new_row[-1]
				contextual_data.append(new_row)

		for row in contextual_data:
			row[-1] = row[-1]/probability_sum

		return JointProbabilityTable(contextual_columns, contextual_data)

	def _add_to_current_beliefs(self, current_beliefs, event_value, probability):
		if not event_value in current_beliefs:
			current_beliefs[event_value] = 0
		current_beliefs[event_value] += probability
	def _get_matching_probability(self, new_beliefs, event_value):
		for new_belief in new_beliefs:
			if new_belief[0] == event_value:
				return new_belief[1]
	def _clone_data(self):
		return [list(row) for row in self._data]
	def update_belief(self, event_name, new_beliefs):
		current_beliefs = {}
		belief_shifts = {}
		event_column_index = self._columns.index(event_name)
		for row in self._data:
			self._add_to_current_beliefs(current_beliefs, row[event_column_index], row[self._probability_index])
		for event_value in new_beliefs:
			updated_probability = new_beliefs[event_value]
			current_probability = current_beliefs[event_value]
			probability_shift = updated_probability / current_probability
			belief_shifts[event_value] = probability_shift
		new_table = self._clone_data()
		for row in new_table:
			row[-1] = row[-1] * belief_shifts[row[event_column_index]]
		return JointProbabilityTable(self._columns, new_table)
	def probability(self, event_name):
		beliefs = {}
		event_column_index = self._columns.index(event_name)
		for row in self._data:
			event_value = row[event_column_index]
			if not (event_value in beliefs):
				beliefs[event_value] = 0
			beliefs[event_value] += row[-1]
		return beliefs
	def __str__(self):
		return str([self._columns, self._data])

class BayesianNode:
	def __init__(self, joint_probability_table):
		self._original_joint_probability_table = joint_probability_table
		self._joint_probability_table = joint_probability_table
		self._affects_nodes = []
		self._affected_by = []
	def affected_by(self, other_node):
		self._affected_by.append(other_node)
	def affects(self, node):
		self._affects_nodes.append(node)
		node.affected_by(self)

diner_order_probability = JointProbabilityTable(
	columns=['order', 'diner loyalty'],
	data = [
		[True,  'return',  .87],
		[True,  'new',     .13],
		[False, 'return',  .1],
		[False, 'new',     .9],

	])

channel_order_probability = JointProbabilityTable(
	columns=['channel', 'diner loyalty'],
	data = [
		['seo',      'return',  .2],
		['seo',      'new',     .8],
		['direct',   'return',  .9],
		['direct',   'new',     .1],
		['facebook', 'return',  .35],
		['facebook', 'new',     .65],
	])

print diner_order_probability.given('order', False)
adjusted_table = diner_order_probability.update_belief('diner loyalty', {'return': .3, 'new': .7})
print adjusted_table.update_belief('diner loyalty', {'return': .5, 'new': .5})

print "~~~~ Example Scenario ~~~~~~"
loyalty_probability_given_ordered = diner_order_probability.given('order', True)
loyalty_beliefs = loyalty_probability_given_ordered.probability('diner loyalty')
print "Given that an order was placed their loyalty probabilities are:"
print loyalty_beliefs
updated_channel_order_probability = channel_order_probability.update_belief('diner loyalty', loyalty_beliefs)
print "Given that an order was placed their channel probabilities are:"
print updated_channel_order_probability.probability('channel')
print "Given that the diner was new their channel probabilities are:"
print updated_channel_order_probability.given('diner loyalty', 'new')
#channel_order_probability

#print "P(order) = " + str(diner_order_probability.probability('order'))
#loyalty_given_channel = channel_order_probability.given('channel', 'seo')
#new_beliefs = loyalty_given_channel.probability('diner loyalty')
#print new_beliefs
#conversion_by_loyalty_given_channel = diner_order_probability.update_belief('diner loyalty', new_beliefs)
#print conversion_by_loyalty_given_channel
#print conversion_by_loyalty_given_channel.probability('order')